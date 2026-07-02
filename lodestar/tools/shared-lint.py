#!/usr/bin/env python3
"""Pre-distribution structural gate for a Lodestar shared-context store.

Four deterministic checks over the git-tracked tree, all derived from the store's own doctrine
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

Exit 0 if clean, 1 on any violation. Stdlib only.

Usage:
    python3 tools/shared-lint.py
"""
import os
import re
import subprocess
import sys

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
    "identity", "operating-rules", "people", "tech-stack", "calibration-os",
    "boundaries", "glossary", "_coordination", "_meta", "core", "tools",
}
CONTENT_DIRS = [
    "identity", "operating-rules", "people", "tech-stack", "calibration-os",
    "boundaries", "glossary",
]

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


def main():
    violations, notes = [], []
    tracked = git_tracked_files()
    check_structure(tracked, violations)
    check_file_cap(tracked, violations, notes)
    check_frontmatter(tracked, violations)
    check_ledger_and_tables(violations)

    for n in notes:
        print(f"shared-lint: note - {n}")
    if not violations:
        print("shared-lint: clean - structure, cap, frontmatter, and ledger format OK.")
        return 0
    for v in sorted(set(violations)):
        print(v)
    print(f"\nshared-lint: {len(set(violations))} violation(s).", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
