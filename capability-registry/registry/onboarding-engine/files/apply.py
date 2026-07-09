#!/usr/bin/env python3
"""apply.py — deterministic onboarding substitution engine.

Reads `placeholders.yml` (the token registry + validation rules + replacement
order, via PyYAML) and a `values.json` (one value per token), validates EVERY
value against its registry rule, then replaces every `<<TOKEN>>` occurrence
across the GIT-TRACKED files of the workspace tree, with CONTEXT-AWARE ESCAPING
by file type:

  * .py            -> the value is escaped for a double-quoted Python string
                      literal (tokens sit inside "<<...>>" literals).
  * .json          -> the value is escaped for a JSON string (tokens sit inside
                      "<<...>>" JSON string values).
  * .md / .yml /   -> inside YAML frontmatter (the leading `---` block of a .md,
    .yaml             or the whole document for .yml/.yaml): emit a YAML-safe
                      scalar (single-quote-wrap, internal quotes doubled, when a
                      raw scalar would be unsafe). In markdown body / prose: raw.

After substitution, a VALIDATOR asserts no leftover `<<X>>` remains for any
registered token name (the generic `<<TOKEN>>` doc literal is ignored). The run is ATOMIC + IDEMPOTENT: a pre-flight snapshot of the tracked
tree is taken before any write; per-phase checkpoint flags are recorded; a
re-run from a partial state is a no-op; on validation failure the tree is
restored from the snapshot. On success the snapshot, checkpoints, and
values.json are deleted.

stdlib + PyYAML only.
"""
import argparse
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml


# Files whose substitutions never need escaping (charset-constrained tokens) vs.
# files where escaping matters are decided per-occurrence below, not here.
TEXT_EXTS_SKIP = {
    ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".ico", ".woff", ".woff2",
    ".ttf", ".otf", ".zip", ".gz", ".bin",
}

CHECKPOINT_DIRNAME = ".onboarding_apply"
SNAPSHOT_DIRNAME = ".onboarding_apply_snapshot"


# --------------------------------------------------------------------------- #
# errors                                                                       #
# --------------------------------------------------------------------------- #
class AbortError(Exception):
    """Raised on any condition that must abort the run with a clear message."""


# --------------------------------------------------------------------------- #
# registry loading                                                             #
# --------------------------------------------------------------------------- #
def load_registry(placeholders_path: Path) -> dict:
    with placeholders_path.open(encoding="utf-8") as fh:
        reg = yaml.safe_load(fh)
    tokens = reg.get("tokens") or []
    by_name = {}
    for t in tokens:
        name = t["name"]
        v = t.get("validation", {}) or {}
        by_name[name] = {
            "regex": v.get("regex"),
            "rule": v.get("rule", ""),
            "allow_empty": bool(v.get("allow_empty", False)),
        }
    order = reg.get("replacement_order") or list(by_name.keys())
    # keep only declared names, in declared order, then append any missed
    order = [n for n in order if n in by_name] + \
            [n for n in by_name if n not in order]
    validator = reg.get("validator", {}) or {}
    ignore_literals = set(validator.get("ignore_literals") or [])
    return {"tokens": by_name, "order": order, "ignore_literals": ignore_literals}


# --------------------------------------------------------------------------- #
# validation                                                                   #
# --------------------------------------------------------------------------- #
def validate_values(registry: dict, values: dict):
    """Validate EVERY registered token's value. Abort listing all problems."""
    problems = []
    for name, spec in registry["tokens"].items():
        if name not in values:
            problems.append(f"{name}: MISSING (no value supplied)")
            continue
        val = values[name]
        if not isinstance(val, str):
            problems.append(f"{name}: value must be a string, got {type(val).__name__}")
            continue
        if val == "" and spec["allow_empty"]:
            continue
        rx = spec["regex"]
        if rx and not re.match(rx, val):
            problems.append(
                f"{name}: value {val!r} fails rule {spec['rule']!r} "
                f"(regex {rx!r})")
    # Reject a value that itself contains a registered token literal: substitution
    # runs in a fixed order, so `WORKSPACE_NAME = "X <<OWNER>> Y"` would recursively
    # expand and produce a surprising result. A real value never contains <<TOKEN>>.
    reg_tokens = set(registry["tokens"].keys())
    tok_re = re.compile(r"<<([A-Za-z_][A-Za-z0-9_]*)>>")
    for name, val in values.items():
        if not isinstance(val, str):
            continue
        embedded = {m.group(1) for m in tok_re.finditer(val)} & reg_tokens
        if embedded:
            problems.append(
                f"{name}: value {val!r} contains a registered token literal "
                f"({', '.join('<<' + t + '>>' for t in sorted(embedded))}) - "
                f"remove it; values must not embed placeholders")
    # also surface any unknown keys (not fatal on their own, but report)
    unknown = [k for k in values if k not in registry["tokens"]]
    if problems:
        raise AbortError(
            "value validation failed:\n  - " + "\n  - ".join(problems)
            + (f"\n  (unknown keys ignored: {unknown})" if unknown else ""))


# --------------------------------------------------------------------------- #
# context-aware escaping                                                        #
# --------------------------------------------------------------------------- #
def esc_python(value: str) -> str:
    """Escape `value` for placement inside a double-quoted Python string literal.

    The token sits as "<<NAME>>" in source, so we substitute the *inner* text.
    json.dumps produces a double-quoted, fully-escaped literal whose escape set
    (\\\\, \\", \\n, \\t, control chars, \\uXXXX) is a subset valid in Python
    string literals — we strip its surrounding quotes to get the inner text.
    """
    dumped = json.dumps(value, ensure_ascii=False)  # '"...."'
    return dumped[1:-1]


def esc_json(value: str) -> str:
    """Escape `value` for placement inside a JSON string ("<<NAME>>")."""
    dumped = json.dumps(value, ensure_ascii=False)
    return dumped[1:-1]


def _yaml_scalar_is_plain_safe(value: str) -> bool:
    """True if `value` can appear as a raw (plain) YAML scalar with no quoting.

    Conservative: round-trip the candidate as a bare scalar and require it to
    parse back to the identical string with no surprises.
    """
    if value == "":
        return False  # empty plain scalar is null in YAML — must quote
    # leading/trailing whitespace, or any char YAML treats specially -> not plain
    if value != value.strip():
        return False
    # characters / patterns that make a plain scalar unsafe or ambiguous
    unsafe_chars = set(":#{}[],&*!|>'\"%@`")
    if any(c in unsafe_chars for c in value):
        return False
    if value[0] in "-?:,[]{}#&*!|>'\"%@` ":
        return False
    if "\n" in value or "\t" in value:
        return False
    try:
        parsed = yaml.safe_load(value)
    except yaml.YAMLError:
        return False
    return parsed == value


def esc_yaml_scalar(value: str) -> str:
    """Return a YAML-safe representation of `value` for a frontmatter scalar.

    The token sits as a bare scalar (`key: <<NAME>>`). If the value is plain-safe
    we emit it raw; otherwise we single-quote-wrap with internal single quotes
    doubled (the YAML single-quoted escape).
    """
    if _yaml_scalar_is_plain_safe(value):
        return value
    return "'" + value.replace("'", "''") + "'"


# --------------------------------------------------------------------------- #
# per-file substitution                                                         #
# --------------------------------------------------------------------------- #
def _frontmatter_bounds(text: str):
    """Return (start, end) char offsets of the frontmatter body for a .md file,
    or None if there is no leading `---` frontmatter block.

    Frontmatter = a leading `---\\n` ... `\\n---` block at the very top.
    """
    if not text.startswith("---\n"):
        return None
    # find the closing fence: a line that is exactly '---' after the opener
    m = re.search(r"\n---\s*(\n|$)", text[3:])
    if not m:
        return None
    body_start = 4  # len('---\n')
    body_end = 3 + m.start() + 1  # +1 to include the leading '\n' position
    return (body_start, body_end)


def substitute_file(path: Path, order, values, write=True) -> int:
    """Substitute all tokens in one file with context-aware escaping.

    Returns the number of token *occurrences* replaced. Writes only if changed
    (and only when `write` is True - a dry run counts without touching disk).
    """
    ext = path.suffix.lower()
    if ext in TEXT_EXTS_SKIP:
        return 0
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, FileNotFoundError):
        return 0

    if ext == ".py":
        replaced = _sub_uniform(text, order, values, esc_python)
    elif ext == ".json":
        replaced = _sub_uniform(text, order, values, esc_json)
    elif ext in (".yml", ".yaml"):
        replaced = _sub_uniform(text, order, values, esc_yaml_scalar)
    elif ext == ".md":
        replaced = _sub_markdown(text, order, values)
    else:
        # default: treat unknown text files as prose (raw substitution)
        replaced = _sub_uniform(text, order, values, lambda v: v)

    new_text, count = replaced
    if count and new_text != text and write:
        path.write_text(new_text, encoding="utf-8")
    return count


def _sub_uniform(text, order, values, escaper):
    """Apply one escaper across the whole text, in declared order."""
    count = 0
    for name in order:
        token = f"<<{name}>>"
        if token not in text:
            continue
        repl = escaper(values[name])
        occurrences = text.count(token)
        text = text.replace(token, repl)
        count += occurrences
    return text, count


def _sub_markdown(text, order, values):
    """Markdown: frontmatter scalars use YAML escaping; body is raw."""
    bounds = _frontmatter_bounds(text)
    if bounds is None:
        return _sub_uniform(text, order, values, lambda v: v)
    fm_start, fm_end = bounds
    head = text[:fm_start]
    frontmatter = text[fm_start:fm_end]
    body = text[fm_end:]
    fm_new, c1 = _sub_uniform(frontmatter, order, values, esc_yaml_scalar)
    body_new, c2 = _sub_uniform(body, order, values, lambda v: v)
    return head + fm_new + body_new, c1 + c2


# --------------------------------------------------------------------------- #
# leftover validator                                                            #
# --------------------------------------------------------------------------- #
def find_leftovers(root: Path, files, registry):
    """Return {relpath: [names]} for any registered token still present.
    The generic <<TOKEN>> (in ignore_literals) is never flagged."""
    names = set(registry["tokens"].keys())
    pat = re.compile(r"<<([A-Za-z_][A-Za-z0-9_]*)>>")
    leftovers = {}
    for rel in files:
        p = root / rel
        ext = p.suffix.lower()
        if ext in TEXT_EXTS_SKIP:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        hits = []
        for m in pat.finditer(text):
            nm = m.group(1)
            if nm in registry["ignore_literals"]:
                continue
            if nm in names:
                hits.append(nm)
        if hits:
            leftovers[rel] = sorted(set(hits))
    return leftovers


# --------------------------------------------------------------------------- #
# git-tracked file discovery                                                    #
# --------------------------------------------------------------------------- #
def git_tracked_files(root: Path, excludes=()):
    out = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        capture_output=True, text=True, check=True)
    files = [f for f in out.stdout.split("\0") if f]
    # never touch anything under .git, nor this onboarding skill's own dir: the
    # registry, engine, tests and SKILL reference the <<TOKEN>> names verbatim
    # (and the test fixtures use the real token literals), so substituting into
    # them would corrupt the machinery. Self-exclude by this file's own location
    # so a rename of the skill dir still skips it. Callers may add further
    # exclude prefixes (e.g. a capability registry's cargo dirs, which may
    # legitimately carry token literals owned by OTHER templates).
    try:
        ob_rel = Path(__file__).resolve().parent.relative_to(root.resolve()).as_posix()
    except ValueError:
        ob_rel = "core/onboarding"
    skip = (".git/", ob_rel + "/")

    def excluded(f):
        if f.startswith(skip):
            return True
        for e in excludes:
            if any(ch in e for ch in "*?["):
                pat = e + "*" if e.endswith("/") else e
                if fnmatch.fnmatch(f, pat):
                    return True
            elif f.startswith(e.rstrip("/") + "/"):
                return True
        return False

    return [f for f in files if not excluded(f)]


# --------------------------------------------------------------------------- #
# snapshot (atomicity)                                                          #
# --------------------------------------------------------------------------- #
def take_snapshot(root: Path, files):
    """Copy every tracked file to a sibling staging dir for rollback."""
    snap = root / SNAPSHOT_DIRNAME
    if snap.exists():
        shutil.rmtree(snap)
    snap.mkdir()
    for rel in files:
        src = root / rel
        if not src.exists():
            continue
        dst = snap / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return snap


def restore_snapshot(root: Path, snap: Path, files):
    for rel in files:
        src = snap / rel
        dst = root / rel
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def discard_snapshot(snap: Path):
    if snap.exists():
        shutil.rmtree(snap, ignore_errors=True)


# --------------------------------------------------------------------------- #
# checkpoints (idempotency)                                                     #
# --------------------------------------------------------------------------- #
def checkpoint_dir(root: Path) -> Path:
    return root / CHECKPOINT_DIRNAME


def read_checkpoint(root: Path) -> set:
    d = checkpoint_dir(root)
    if not d.exists():
        return set()
    return {p.name for p in d.glob("*.done")}


def write_checkpoint(root: Path, phase: str):
    d = checkpoint_dir(root)
    d.mkdir(exist_ok=True)
    (d / f"{phase}.done").write_text("ok", encoding="utf-8")


def clear_checkpoints(root: Path):
    d = checkpoint_dir(root)
    if d.exists():
        shutil.rmtree(d, ignore_errors=True)


# --------------------------------------------------------------------------- #
# main run                                                                      #
# --------------------------------------------------------------------------- #
def run(root: Path, placeholders_path: Path, values_path: Path,
        dry_run: bool = False, excludes=()) -> int:
    root = root.resolve()

    # --- IDEMPOTENCY: if a prior run already completed (no values.json and the
    # tree has no leftovers), a re-run with no values.json is a clean no-op.
    if not values_path.exists():
        registry = load_registry(placeholders_path)
        files = git_tracked_files(root, excludes)
        leftovers = find_leftovers(root, files, registry)
        if not leftovers:
            print("apply.py: nothing to do — no values.json and no leftover "
                  "tokens (already applied). exit 0.")
            clear_checkpoints(root)
            discard_snapshot(root / SNAPSHOT_DIRNAME)
            return 0
        raise AbortError(
            f"values.json not found at {values_path}, but leftover tokens "
            f"remain in: {sorted(leftovers)}")

    # --- load registry + values
    registry = load_registry(placeholders_path)
    try:
        values = json.loads(values_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise AbortError(f"values.json is not valid JSON: {e}")
    if not isinstance(values, dict):
        raise AbortError("values.json must be a JSON object {token: value}")

    # --- VALIDATE every value BEFORE touching the tree
    validate_values(registry, values)

    # --- discover tracked files
    files = git_tracked_files(root, excludes)

    # --- DRY RUN: validate + report what would change, write nothing
    if dry_run:
        per_file = {}
        for rel in files:
            n = substitute_file(root / rel, registry["order"], values, write=False)
            if n:
                per_file[rel] = n
        print("apply.py: DRY RUN - nothing written. replacements that would be made:")
        for rel in sorted(per_file):
            print(f"  {rel}: {per_file[rel]}")
        print(f"  total files that would change: {len(per_file)}")
        print("apply.py: dry run complete; values.json left in place. exit 0.")
        return 0

    # --- SNAPSHOT before any write
    snap = take_snapshot(root, files)
    done = read_checkpoint(root)

    try:
        # --- PHASE: substitute
        per_file = {}
        if "substitute" not in done:
            for rel in files:
                n = substitute_file(root / rel, registry["order"], values)
                if n:
                    per_file[rel] = n
            write_checkpoint(root, "substitute")
        else:
            # already substituted on a prior partial run; recompute report best-effort
            pass

        # --- PHASE: validate leftovers
        leftovers = find_leftovers(root, files, registry)
        if leftovers:
            raise AbortError(
                "post-substitution validator FAILED — leftover registered "
                f"tokens remain: {json.dumps(leftovers, indent=2)}")
        write_checkpoint(root, "validate")

    except Exception as e:
        # restore the tree to its pre-flight state so it stays recoverable
        restore_snapshot(root, snap, files)
        clear_checkpoints(root)
        discard_snapshot(snap)
        if isinstance(e, AbortError):
            raise
        raise AbortError(f"unexpected error during apply (tree restored): {e}")

    # --- SUCCESS: report, then clean up snapshot + checkpoints + values.json
    print("apply.py: substitution complete. replacements per file:")
    if per_file:
        for rel in sorted(per_file):
            print(f"  {rel}: {per_file[rel]}")
    else:
        print("  (no files contained tokens, or already applied)")
    print(f"  total files touched: {len(per_file)}")

    discard_snapshot(snap)
    clear_checkpoints(root)
    try:
        values_path.unlink()
    except FileNotFoundError:
        pass
    print("apply.py: cleaned snapshot, checkpoints, and values.json. exit 0.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Onboarding substitution engine.")
    ap.add_argument("--root", default=".",
                    help="workspace root (a git repo). default: cwd")
    ap.add_argument("--placeholders", default=None,
                    help="path to placeholders.yml (default: alongside apply.py)")
    ap.add_argument("--values", default=None,
                    help="path to values.json (default: <root>/values.json)")
    ap.add_argument("--dry-run", action="store_true",
                    help="validate values and report per-file replacement counts "
                         "without writing anything (values.json is kept)")
    ap.add_argument("--exclude", action="append", default=[],
                    help="path prefix or glob to leave untouched (repeatable) - "
                         "e.g. 'registry/*/files/' for a capability registry's "
                         "cargo, whose files may carry token literals owned by "
                         "other templates")
    args = ap.parse_args(argv)

    root = Path(args.root)
    here = Path(__file__).resolve().parent
    placeholders = Path(args.placeholders) if args.placeholders \
        else here / "placeholders.yml"
    values = Path(args.values) if args.values else root / "values.json"

    try:
        return run(root, placeholders, values, dry_run=args.dry_run,
                   excludes=args.exclude)
    except AbortError as e:
        print(f"apply.py: ABORT — {e}", file=sys.stderr)
        return 2
    except subprocess.CalledProcessError as e:
        print(f"apply.py: ABORT — git failed: {e.stderr or e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
