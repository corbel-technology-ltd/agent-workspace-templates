#!/usr/bin/env python3
"""Workspace health gate: context decomposition (concept folders with index maps).

The law it enforces (10_doctrine/context-decomposition.md): large durable context files decompose
into one-concept notes behind an index map so context can be loaded granularly. Every git-tracked
file is in scope by default; exceptions are explicit, per-file, and must carry a reason.

Checks:
  (1) PROSE SIZE   - a .md file outside structural exemptions may not exceed MD_LIMIT lines or
                     MD_CHAR_LIMIT characters, including notes in concept folders, unless excepted.
  (2) CODE SIZE    - a file with a recognised code extension may not exceed CODE_LIMIT lines
                     unless its atomic engine/test-module policy class is cited in an exception.
  (3) EXCEPTION HYGIENE - every row must be unique, reasoned, live, necessary, and non-structural.
  (4) OWNING INDEX - every concept note must link or carry a related-edge ref to its owning
                     00-INDEX.md and have a genuine top-level frontmatter status key. This check
                     runs even in structurally exempt directories and for excepted notes.

Structural exemptions (the doctrine's keep-whole classes, encoded):
  AGENTS.md                            the constitution (single boot file by design)
  50_registers/**                     registers/ledgers (row-granular tables)
  20_memory/**                        journal events + derived memory layers
  90_runs/**                          run artefacts (C4 historical record, sealed evidence)
  30_schemas/**, 40_templates/**      schemas/templates as structural classes
  CHANGELOG.md                        ledger-like
  non-code, non-md files              data/config; not prose context

Runtime adapter pointer files are already capped to a few lines by the adapter-purity gate, so
they can never reach the prose ceiling and need no exemption here.

Recognised code extensions: .py, .js, .sh, .ts, .tsx, .jsx, .mjs, .cjs, .rs, .go, .rb, .java,
.c, .h, .cpp, .hpp, and .bash.

Exit 0 if clean, 1 on any violation. Stdlib only.

Usage:
    python3 tools/decomposition-check.py
"""
import os
import posixpath
import re
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCEPTIONS_FILE = os.path.join(REPO_ROOT, "tools", "decomposition-exceptions.txt")

MD_LIMIT = 150
MD_CHAR_LIMIT = 12_000
CODE_LIMIT = 500

EXEMPT_FILES = {"AGENTS.md", "CHANGELOG.md"}
EXEMPT_PREFIXES = (
    "50_registers/", "20_memory/", "90_runs/", "30_schemas/", "40_templates/",
)
CODE_EXTS = {
    ".py", ".js", ".sh", ".ts", ".tsx", ".jsx", ".mjs", ".cjs", ".rs", ".go",
    ".rb", ".java", ".c", ".h", ".cpp", ".hpp", ".bash",
}
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
RELATED_REF_RE = re.compile(r"\bref:\s*['\"]?([^,}\s'\"]+)")


def git_tracked_files():
    out = subprocess.run(
        ["git", "-C", REPO_ROOT, "ls-files"], check=True, capture_output=True, text=True)
    return [path for path in out.stdout.splitlines() if path]


def structural_exemption(rel):
    ext = os.path.splitext(rel)[1].lower()
    return (os.path.basename(rel) in EXEMPT_FILES or rel.startswith(EXEMPT_PREFIXES)
            or (ext != ".md" and ext not in CODE_EXTS))


def read_text(rel, violations):
    try:
        with open(os.path.join(REPO_ROOT, rel), "r", encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeError) as exc:
        violations.append(f"{rel}: tracked in-scope file is unreadable ({exc})")
        return None


def frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return ""
    for index, line in enumerate(lines[1:], start=1):
        if line == "---":
            return "\n".join(lines[1:index])
    return ""


def in_concept_folder(rel):
    directory = os.path.dirname(rel)
    return bool(directory and os.path.isfile(os.path.join(REPO_ROOT, directory, "00-INDEX.md")))


def normalise_link(rel, target):
    target = target.strip().split()[0].strip("<>").split("#", 1)[0].split("?", 1)[0]
    if not target or "://" in target:
        return ""
    if target.startswith("/"):
        return posixpath.normpath(target.lstrip("/"))
    return posixpath.normpath(posixpath.join(posixpath.dirname(rel), target))


def references_owning_index(rel, text, metadata):
    owner = posixpath.join(posixpath.dirname(rel), "00-INDEX.md")
    for match in MARKDOWN_LINK_RE.finditer(text):
        if normalise_link(rel, match.group(1)) == owner:
            return True
    for match in RELATED_REF_RE.finditer(metadata):
        target = match.group(1).split("#", 1)[0]
        if posixpath.normpath(target.lstrip("/")) == owner:
            return True
    return False


def check_concept_hygiene(rel, text, violations):
    if os.path.basename(rel) == "00-INDEX.md" or not in_concept_folder(rel):
        return
    metadata = frontmatter(text)
    if not re.search(r"^status:[ \t]*\S", metadata, re.MULTILINE):
        violations.append(f"{rel}: concept note has no top-level frontmatter status key of its own")
    if not references_owning_index(rel, text, metadata):
        violations.append(
            f"{rel}: concept note has no markdown link or related-edge ref to its owning "
            f"00-INDEX.md")


def load_exceptions(tracked, violations):
    exceptions = {}
    seen_paths = set()
    if not os.path.exists(EXCEPTIONS_FILE):
        return exceptions
    try:
        with open(EXCEPTIONS_FILE, "r", encoding="utf-8") as fh:
            rows = list(fh)
    except (OSError, UnicodeError) as exc:
        violations.append(f"tools/decomposition-exceptions.txt: unreadable ({exc})")
        return exceptions
    tracked_set = set(tracked)
    for lineno, raw in enumerate(rows, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "#" not in line:
            violations.append(
                f"tools/decomposition-exceptions.txt:{lineno}: entry has no reason "
                f"(format: <path>  # <reasoned keep-intact policy>)")
            continue
        path, reason = (part.strip() for part in line.split("#", 1))
        if not path or not reason:
            violations.append(
                f"tools/decomposition-exceptions.txt:{lineno}: empty path or reason")
            continue
        if path in seen_paths:
            violations.append(
                f"tools/decomposition-exceptions.txt:{lineno}: duplicate entry for {path}")
            continue
        seen_paths.add(path)
        if path not in tracked_set:
            violations.append(
                f"tools/decomposition-exceptions.txt:{lineno}: stale entry - {path} is not a "
                f"tracked file (remove the row)")
            continue
        exceptions[path] = (reason, lineno)
    return exceptions


def exception_hygiene(exceptions, measurements, violations):
    for rel, (_, lineno) in exceptions.items():
        prefix = f"tools/decomposition-exceptions.txt:{lineno}: unnecessary exception - {rel}"
        if structural_exemption(rel):
            violations.append(f"{prefix} is structurally exempt")
            continue
        measured = measurements.get(rel)
        if measured is None:
            continue
        lines, chars, ext = measured
        if ext == ".md" and lines <= MD_LIMIT and chars <= MD_CHAR_LIMIT:
            violations.append(f"{prefix} is under both prose ceilings")
        elif ext in CODE_EXTS and lines <= CODE_LIMIT:
            violations.append(f"{prefix} is under the code ceiling")


def main():
    violations = []
    tracked = git_tracked_files()
    exceptions = load_exceptions(tracked, violations)
    measurements = {}

    for rel in tracked:
        ext = os.path.splitext(rel)[1].lower()
        if ext != ".md" and ext not in CODE_EXTS:
            continue
        text = read_text(rel, violations)
        if text is None:
            continue
        if ext == ".md":
            check_concept_hygiene(rel, text, violations)
        measurements[rel] = (len(text.splitlines()), len(text), ext)

    exception_hygiene(exceptions, measurements, violations)

    for rel, (lines, chars, ext) in measurements.items():
        if structural_exemption(rel) or rel in exceptions:
            continue
        if ext == ".md" and (lines > MD_LIMIT or chars > MD_CHAR_LIMIT):
            excess = []
            if lines > MD_LIMIT:
                excess.append(f"{lines} lines (max {MD_LIMIT})")
            if chars > MD_CHAR_LIMIT:
                excess.append(f"{chars} characters (max {MD_CHAR_LIMIT})")
            violations.append(
                f"{rel}: {', '.join(excess)} for prose - decompose into a concept folder with "
                f"00-INDEX.md (40_templates/concept-folder/), or add a reasoned exception")
        elif ext in CODE_EXTS and lines > CODE_LIMIT:
            violations.append(
                f"{rel}: {lines} lines (max {CODE_LIMIT} for code) - split into modules, or cite "
                f"the atomic code/test-suite keep-intact class in a reasoned exception")

    unique = sorted(set(violations))
    if not unique:
        print("decomposition-check: clean - durable context is concept-scoped; "
              "exceptions all reasoned, live, and necessary.")
        return 0
    for violation in unique:
        print(violation)
    print(f"\ndecomposition-check: {len(unique)} violation(s) - "
          f"see 10_doctrine/context-decomposition.md.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
