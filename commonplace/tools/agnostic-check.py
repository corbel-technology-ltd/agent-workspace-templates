#!/usr/bin/env python3
"""Pre-distribution agent-agnostic gate: neutral core + thin adapters, enforced.

The law it enforces: the constitution (AGENTS.md), doctrine, schemas, and all executable machinery
(core/, tools/) are runtime-neutral; each runtime attaches through a THIN adapter (a pinned pointer
file at the root plus that runtime's config dir). Vendor/runtime names may appear ONLY in the
adapter layer and in the sanctioned registry (core/RUNTIMES.md). Adapters may not grow content.

Two checks over the git-tracked tree:

  (1) ADAPTER PURITY - each pointer file in ADAPTER_POINTERS must exist, stay within
      MAX_POINTER_LINES total lines, name `AGENTS.md` (the pointer contract) at least twice,
      declare that AGENTS.md wins on conflict, and contain no second-level headings (no content
      sections). Every *.md inside an adapter dir must stay within MAX_ADAPTER_DOC_LINES.

  (2) NEUTRAL-CORE PURITY - no file outside the adapter layer + sanctioned registry may contain a
      vendor/runtime term (word-boundary, case-insensitive). This catches both prose lock-in
      ("works in X") and structural lock-in (neutral docs pointing into a runtime config dir).

Exit 0 if clean, 1 on any violation. Stdlib only.

Usage:
    python3 tools/agnostic-check.py
"""
import os
import re
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- the adapter layer ------------------------------------------------------
# Root pointer files, one per runtime. Add yours here when wiring a new runtime
# (step 1 of the core/RUNTIMES.md guide).
ADAPTER_POINTERS = ["CLAUDE.md", "GEMINI.md"]

# Runtime config dirs (everything under them is adapter wiring).
ADAPTER_DIRS = [".claude/", ".gemini/"]

# The one sanctioned place for vendor detail outside the adapters, plus this
# script (it carries the term list itself).
SANCTIONED = {"core/RUNTIMES.md", "tools/agnostic-check.py"}

# Capability payloads in a Chandlery registry are CARGO: they are checked in the
# workspace they get installed into, not in the warehouse that stocks them (the
# stock may legitimately include adapter tooling - or this very script).
CARGO_RE = re.compile(r"^registry/[^/]+/files/")

MAX_POINTER_LINES = 16       # a pointer is ~10 lines; leave headroom, forbid essays
MAX_ADAPTER_DOC_LINES = 30   # adapter READMEs/skill pointers stay thin

# Vendor/runtime terms that must not appear in the neutral core. Word-boundary,
# case-insensitive. Note "claude" also catches neutral docs referencing the
# `.claude/` config dir - that is structural lock-in and exactly what this gate
# is for (point at core/ or core/RUNTIMES.md instead).
VENDOR_TERMS = ["claude", "gemini", "anthropic", "openai", "chatgpt", "copilot"]


def git_tracked_files():
    out = subprocess.run(
        ["git", "-C", REPO_ROOT, "ls-files"],
        check=True, capture_output=True, text=True)
    return [p for p in out.stdout.splitlines() if p]


def read(rel):
    try:
        with open(os.path.join(REPO_ROOT, rel), "r", encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


def in_adapter_layer(rel):
    if rel in ADAPTER_POINTERS:
        return True
    return any(rel.startswith(d) for d in ADAPTER_DIRS)


def check_pointer(rel, violations):
    text = read(rel)
    if text is None:
        violations.append(f"{rel}: adapter pointer file missing or unreadable")
        return
    lines = text.splitlines()
    if len(lines) > MAX_POINTER_LINES:
        violations.append(
            f"{rel}: pointer has {len(lines)} lines (max {MAX_POINTER_LINES}) - "
            f"adapters must stay pointers, content belongs in AGENTS.md")
    if text.count("AGENTS.md") < 2:
        violations.append(f"{rel}: does not point at AGENTS.md as the canonical manifest")
    if "wins" not in text:
        violations.append(f"{rel}: missing the conflict rule ('AGENTS.md wins')")
    for i, line in enumerate(lines, start=1):
        if line.startswith("##"):
            violations.append(f"{rel}:{i}: content section in a pointer file")


def check_adapter_doc(rel, violations):
    text = read(rel)
    if text is None:
        return
    n = len(text.splitlines())
    if n > MAX_ADAPTER_DOC_LINES:
        violations.append(
            f"{rel}: adapter doc has {n} lines (max {MAX_ADAPTER_DOC_LINES}) - "
            f"move content to core/ and point to it")


def check_neutral(rel, patterns, violations):
    text = read(rel)
    if text is None:
        return  # binary or unreadable - path itself carries no vendor term by construction here
    for lineno, line in enumerate(text.splitlines(), start=1):
        for term, pat in patterns.items():
            if pat.search(line):
                violations.append(f"{rel}:{lineno}: vendor term '{term}' in neutral core")


def main():
    patterns = {t: re.compile(r"\b" + re.escape(t) + r"\b", re.IGNORECASE)
                for t in VENDOR_TERMS}
    violations = []
    tracked = git_tracked_files()

    for rel in ADAPTER_POINTERS:
        check_pointer(rel, violations)

    for rel in tracked:
        if rel in SANCTIONED or CARGO_RE.match(rel):
            continue
        if in_adapter_layer(rel):
            if rel.endswith(".md") and rel not in ADAPTER_POINTERS:
                check_adapter_doc(rel, violations)
            continue
        check_neutral(rel, patterns, violations)

    if not violations:
        print("agnostic-check: clean - neutral core is vendor-free, adapters are thin pointers.")
        return 0
    for v in sorted(set(violations)):
        print(v)
    print(f"\nagnostic-check: {len(set(violations))} violation(s) - "
          f"see core/RUNTIMES.md for where runtime specifics belong.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
