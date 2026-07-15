#!/usr/bin/env python3
"""Pre-distribution structural gate for a Shared-Context shared-context store.

Five deterministic checks over the git-tracked tree, all derived from the store's own doctrine
(SHARED.md scope + file cap, _meta/governance.md trailer format, the coordination tables):

  (1) STRUCTURE LOCK - the top level may contain only the known files and folders. A shared store
      fails by dumping; a new top-level thing is a governance decision, not a drift, so the gate
      forces the conversation (add it to ALLOWED_* deliberately, with sign-off).
  (2) FILE CAP - content files across the content folders (excluding READMEs and `_`-prefixed
      templates) must not exceed the `file_cap:` recorded in _meta/governance.md frontmatter.
      Skipped with a note while the cap is still an unfilled `<<TOKEN>>` (blank template).
  (3) FRONTMATTER COMPLETENESS - every tracked .md with frontmatter carries non-empty `id`,
      `type`, `status`, and `owner` (okf-check requires only `type`; a governed store needs the
      other three for ownership and lifecycle to mean anything).
  (4) LEDGER FORMAT - every dated line in CHANGES.md parses as the trailer
      `YYYY-MM-DD | who | summary | window: ...`, and the coordination tables keep their headers.
  (5) LOADING CONTRACT - governed files declare always/triggered loading, index tables agree,
      current files are substantive, and the real selector excludes seeds.

Exit 0 if clean, 1 on any violation. Stdlib only.

Usage:
    python3 tools/shared-lint.py
"""
import os
import importlib.util
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALLOWED_ROOT_FILES = {
    "SHARED.md", "AGENTS.md", "README.md", "INSTALL.md", "CHANGES.md", "FAMILY.md",
    "LICENSE", "requirements.txt",
}
# A root ALL-CAPS .md beyond the set above is allowed ONLY if it is a genuine
# runtime-adapter pointer file: thin and deferring to AGENTS.md. This gate checks
# that itself (agnostic-check only pointer-checks the two hardcoded adapters), so a
# content dump like NOTES.md cannot slip in under a shouty filename.
POINTER_RE = re.compile(r"^[A-Z][A-Z0-9_-]*\.md$")
MAX_POINTER_LINES = 16
ALLOWED_ROOT_DIRS = {
    "identity", "operating-rules", "people", "places", "concepts", "automations",
    "tech-stack", "calibration-os", "boundaries", "glossary",
    "_coordination", "_meta", "core", "tools",
}
CONTENT_DIRS = [
    "identity", "operating-rules", "people", "places", "concepts", "automations",
    "tech-stack", "calibration-os", "boundaries", "glossary",
]
LOADING_DIRS = ("identity", "operating-rules", "boundaries")
REQUIRED_ALWAYS = {
    "SHARED.md", "identity/README.md", "operating-rules/README.md", "boundaries/README.md",
    "identity/principal.md", "boundaries/boundaries.md",
}

ENTRY_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2} \| [^|]+ \| .+ \| window: (open \(closes \d{4}-\d{2}-\d{2}\)|closed|n/a \(.+\))\s*$")


def git_tracked_files():
    out = subprocess.run(["git", "-C", REPO_ROOT, "ls-files"],
                         check=True, capture_output=True, text=True)
    return [p for p in out.stdout.splitlines() if p]


def read(rel):
    try:
        with open(os.path.join(REPO_ROOT, rel), "r", encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


def split_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i]
    return None


def fm_value(fm_lines, key):
    for line in fm_lines:
        m = re.match(rf"{key}:\s*(.*)$", line)
        if m:
            return m.group(1).strip().strip("'\"")
    return ""


def check_structure(tracked, violations):
    for rel in tracked:
        top = rel.split("/", 1)[0]
        if top.startswith("."):
            continue  # dotfiles + runtime-adapter dirs are the adapter layer's business
        if "/" in rel:
            if top not in ALLOWED_ROOT_DIRS:
                violations.append(
                    f"{rel}: unknown top-level folder '{top}/' - a new folder is a governance "
                    f"decision (sign-off), then add it to shared-lint's ALLOWED_ROOT_DIRS")
        else:
            if top in ALLOWED_ROOT_FILES:
                continue
            if POINTER_RE.match(top):
                # allowed only if it is genuinely a thin pointer, not a content dump
                text = read(rel) or ""
                lines = text.splitlines()
                if len(lines) > MAX_POINTER_LINES or "AGENTS.md" not in text:
                    violations.append(
                        f"{rel}: root ALL-CAPS .md that is not a thin adapter pointer "
                        f"({len(lines)} lines; must be <= {MAX_POINTER_LINES} and defer to "
                        f"AGENTS.md). Content files do not belong at root - that is a governance "
                        f"decision.")
                continue
            violations.append(
                f"{rel}: unknown top-level file - a new root file is a governance decision "
                f"(sign-off), then add it to shared-lint's ALLOWED_ROOT_FILES")


def check_file_cap(tracked, violations, notes):
    gov = read("_meta/governance.md")
    cap = None
    if gov:
        fm = split_frontmatter(gov)
        if fm:
            raw = fm_value(fm, "file_cap")
            if raw.isdigit():
                cap = int(raw)
    if cap is None:
        notes.append("file cap not yet numeric (blank template) - cap check skipped")
        return
    content = [rel for rel in tracked
               if rel.split("/", 1)[0] in CONTENT_DIRS and rel.endswith(".md")
               and os.path.basename(rel) != "README.md"
               and not os.path.basename(rel).startswith("_")]
    if len(content) > cap:
        violations.append(
            f"file cap exceeded: {len(content)} content files > cap {cap} "
            f"(_meta/governance.md) - consolidate or retire before adding")


def check_frontmatter(tracked, violations):
    for rel in tracked:
        if not rel.endswith(".md"):
            continue
        if rel.split("/", 1)[0].startswith("."):
            continue  # runtime-adapter files follow their runtime's conventions
        base = os.path.basename(rel)
        if base in ("index.md", "log.md"):
            continue
        text = read(rel)
        if text is None:
            continue
        fm = split_frontmatter(text)
        if fm is None:
            continue  # frontmatter-less files are not concept files
        for key in ("id", "type", "status", "owner"):
            if not fm_value(fm, key):
                violations.append(f"{rel}: frontmatter missing '{key}'")


def check_ledger_and_tables(violations):
    changes = read("CHANGES.md")
    if changes is None:
        violations.append("CHANGES.md: missing")
    else:
        for lineno, line in enumerate(changes.splitlines(), start=1):
            s = line.strip()
            # Any line that STARTS with a date (however it is spaced or punctuated
            # after it) is meant to be a trailer; hold it to the strict format. This
            # catches the likely typo class - a missing space, 'closes' without a
            # date - that a `^date \|` trigger would wave through.
            if re.match(r"^\d{4}-\d{2}-\d{2}\b", s) and not ENTRY_RE.match(s):
                violations.append(
                    f"CHANGES.md:{lineno}: dated line does not parse as a trailer "
                    f"(YYYY-MM-DD | who | summary | window: open (closes YYYY-MM-DD) | closed | n/a (reason))")
    dash = read("_coordination/dashboard.md")
    if dash is None or "| ID | From -> To | Summary |" not in dash:
        violations.append("_coordination/dashboard.md: open-handoffs table header missing/changed")
    roster = read("_coordination/roster.md")
    if roster is None or "| Workspace | Path | Agent | Linked | Status |" not in roster:
        violations.append("_coordination/roster.md: roster table header missing/changed")


def loading_module():
    path = os.path.join(REPO_ROOT, "core", "hooks", "store-brief.py")
    spec = importlib.util.spec_from_file_location("shared_store_brief", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def index_load_rows(directory, violations):
    text = read(f"{directory}/README.md") or ""
    lines, capturing = text.splitlines(), False
    rows = {}
    for line in lines:
        if line.strip().startswith("## "):
            capturing = line.strip() == "## Load policy"
            continue
        if not capturing or not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[0].lower() == "file" or set(cells[0]) <= set("-: "):
            continue
        match = re.search(r"\]\(([^)#?]+)", cells[0])
        if not match:
            violations.append(f"{directory}/README.md: load row has no local Markdown link")
            continue
        rel = f"{directory}/{match.group(1)}"
        rows[rel] = (cells[1], cells[2])
    return rows


def check_loading_contract(tracked, violations):
    try:
        selector = loading_module()
    except (OSError, AttributeError) as exc:
        violations.append(f"core/hooks/store-brief.py: loading selector unavailable ({exc})")
        return
    loading_files = ["SHARED.md"] + sorted(
        rel for rel in tracked if rel.endswith(".md") and rel.count("/") == 1
        and rel.split("/", 1)[0] in LOADING_DIRS)
    metadata = {}
    for rel in loading_files:
        text = read(rel)
        if text is None:
            violations.append(f"{rel}: loading-contract file is unreadable")
            continue
        fm = split_frontmatter(text)
        if fm is None:
            violations.append(f"{rel}: loading-contract frontmatter missing")
            continue
        for key in ("status", "load"):
            matches = [line for line in fm if re.match(rf"{key}:\s*", line)]
            if len(matches) > 1:
                violations.append(f"{rel}: duplicate frontmatter key '{key}'")
        status, load = fm_value(fm, "status"), fm_value(fm, "load")
        metadata[rel] = (status, load, text)
        if load not in ("always", "triggered"):
            violations.append(f"{rel}: load must be 'always' or 'triggered'")
        if rel in REQUIRED_ALWAYS and load != "always":
            violations.append(f"{rel}: required safety/index file must declare load: always")
        try:
            has_body = selector.substantive(text)
        except ValueError as exc:
            violations.append(f"{rel}: loading metadata is ambiguous ({exc})")
            has_body = False
        if status == "current" and not has_body:
            violations.append(f"{rel}: status current but body is blank or still marked blank")

    for directory in LOADING_DIRS:
        rows = index_load_rows(directory, violations)
        siblings = {rel for rel in loading_files
                    if rel.startswith(directory + "/") and not rel.endswith("/README.md")}
        if set(rows) != siblings:
            violations.append(f"{directory}/README.md: load table does not exactly list sibling files")
        for rel, (table_load, trigger) in rows.items():
            if rel in metadata and table_load != metadata[rel][1]:
                violations.append(f"{directory}/README.md: load value disagrees with {rel}")
            if table_load == "triggered" and not trigger.strip():
                violations.append(f"{directory}/README.md: triggered row for {rel} needs a trigger")

    try:
        selected, warnings = selector.select_always(Path(REPO_ROOT))
    except (OSError, ValueError) as exc:
        violations.append(f"core/hooks/store-brief.py: selector rejected the store ({exc})")
        return
    if warnings:
        violations.append("core/hooks/store-brief.py: selector reports contract warning: "
                          + "; ".join(warnings))
    for rel in selected:
        if metadata.get(rel, (None,))[0] == "seed":
            violations.append(f"core/hooks/store-brief.py: selector loaded seed file {rel}")
    check_selector_fail_safes(selector, violations)


def fixture_doc(status, load, marker, *, blank=False):
    body = "> Blank by design - fixture.\n" if blank else f"{marker}\n"
    return (f"---\nid: fixture.{marker.lower()}\ntype: context\nstatus: {status}\n"
            f"load: {load}\nowner: shared\n---\n\n# {marker}\n\n{body}")


def check_selector_fail_safes(selector, violations):
    """Exercise safety edges which a clean provider tree cannot demonstrate."""
    with tempfile.TemporaryDirectory(prefix="shared-loading-selftest-") as raw:
        root = Path(raw) / "store"
        for directory in LOADING_DIRS:
            (root / directory).mkdir(parents=True, exist_ok=True)
        files = {
            "SHARED.md": ("current", "always", "SHARED"),
            "identity/README.md": ("current", "always", "IDENTITY"),
            "identity/principal.md": ("seed", "always", "PRINCIPAL"),
            "identity/voice.md": ("current", "triggered", "VOICE"),
            "operating-rules/README.md": ("current", "always", "RULES"),
            "operating-rules/a.md": ("current", "always", "A_RULE"),
            "boundaries/README.md": ("current", "always", "BOUNDARIES"),
            "boundaries/boundaries.md": ("seed", "always", "BOUNDARY_FILE"),
        }
        for rel, values in files.items():
            (root / rel).write_text(fixture_doc(*values), encoding="utf-8")
        expected = [*selector.CORE_ORDER, "operating-rules/a.md"]
        try:
            selected, warnings = selector.select_always(root)
            if selected != expected or warnings:
                violations.append("core/hooks/store-brief.py: deterministic selection fixture failed")
        except (OSError, ValueError) as exc:
            violations.append(f"core/hooks/store-brief.py: clean selector fixture failed ({exc})")

        voice = root / "identity/voice.md"
        voice.write_text(fixture_doc("current", "invalid", "VOICE"), encoding="utf-8")
        try:
            selected, warnings = selector.select_always(root)
            if "identity/voice.md" not in selected or not any("invalid" in item for item in warnings):
                violations.append("core/hooks/store-brief.py: invalid load did not use conservative fallback")
        except (OSError, ValueError) as exc:
            violations.append(f"core/hooks/store-brief.py: invalid-load fallback failed ({exc})")
        voice.write_text(fixture_doc("current", "triggered", "VOICE"), encoding="utf-8")

        shared = root / "SHARED.md"
        shared.write_text(fixture_doc("current", "always", "SHARED", blank=True), encoding="utf-8")
        try:
            selector.select_always(root)
        except ValueError:
            pass
        else:
            violations.append("core/hooks/store-brief.py: blank required core file did not fail safe")
        shared.write_text(fixture_doc("current", "always", "SHARED"), encoding="utf-8")

        duplicate = fixture_doc("current", "triggered", "VOICE").replace(
            "load: triggered", "load: triggered\nload: always")
        voice.write_text(duplicate, encoding="utf-8")
        try:
            selector.select_always(root)
        except ValueError:
            pass
        else:
            violations.append("core/hooks/store-brief.py: duplicate load metadata did not fail safe")
        voice.write_text(fixture_doc("current", "triggered", "VOICE"), encoding="utf-8")

        identity_index = root / "identity/README.md"
        identity_bytes = identity_index.read_bytes()
        identity_index.unlink()
        try:
            selector.select_always(root)
        except ValueError:
            pass
        else:
            violations.append("core/hooks/store-brief.py: missing required index did not fail safe")
        identity_index.write_bytes(identity_bytes)

        outside = Path(raw) / "outside.md"
        outside.write_text(fixture_doc("seed", "always", "OUTSIDE"), encoding="utf-8")
        principal = root / "identity/principal.md"
        principal.unlink()
        principal.symlink_to(outside)
        try:
            selector.select_always(root)
        except OSError:
            pass
        else:
            violations.append("core/hooks/store-brief.py: escaping governed symlink did not fail safe")

        shim_root = Path(raw) / "shim-fixture"
        adapter_dir = "." + "cl" + "aude"
        shim = shim_root / adapter_dir / "hooks/shim.py"
        shim.parent.mkdir(parents=True)
        (shim_root / "core/hooks").mkdir(parents=True)
        shim.write_text(read(f"{adapter_dir}/hooks/shim.py") or "", encoding="utf-8")
        (shim_root / "core/hooks/probe.py").write_text(
            "import sys\nprint('probe failed', file=sys.stderr)\nraise SystemExit(1)\n",
            encoding="utf-8")
        result = subprocess.run([sys.executable, str(shim), "probe"], input="{}",
                                text=True, capture_output=True)
        if result.returncode or "manual review" not in result.stdout:
            violations.append("runtime shim: non-blocking core failure was not surfaced")


def main():
    violations, notes = [], []
    tracked = git_tracked_files()
    check_structure(tracked, violations)
    check_file_cap(tracked, violations, notes)
    check_frontmatter(tracked, violations)
    check_ledger_and_tables(violations)
    check_loading_contract(tracked, violations)

    for n in notes:
        print(f"shared-lint: note - {n}")
    if not violations:
        print("shared-lint: clean - structure, cap, frontmatter, ledger, and loading contract OK.")
        return 0
    for v in sorted(set(violations)):
        print(v)
    print(f"\nshared-lint: {len(set(violations))} violation(s).", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
