#!/usr/bin/env python3
"""Pre-distribution confidentiality gate: zero in-house terms in the template.

Reads tools/scrub-terms.txt (one lowercase term per line; `#` comments and blank
lines ignored) and scans every git-tracked file for any term across THREE
surfaces:
  (a) file CONTENTS  — every line of the file
  (b) frontmatter `id:` value — the `id:` line inside a leading `---` block
  (c) FILENAME / path — the tracked path itself

Matching is case-insensitive on WHOLE WORDS (regex \\b boundaries) so a term like
'cat' never fires on 'category' and 'ace' never fires on 'space'. Some listed
terms may be collision-prone; they still word-boundary match and are reported for
human review (a hit is a prompt to look, not proof of a leak).

The terms file itself and the tools/ check scripts are excluded (they legitimately
contain the term list / the matching logic).

Exit 0 if clean (or no terms configured yet), 1 if any hit.

Usage:
    python3 tools/scrub-check.py
"""

import os
import re
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TERMS_FILE = os.path.join(REPO_ROOT, "tools", "scrub-terms.txt")

# Tracked paths that legitimately contain the terms / matching logic — never scan.
EXCLUDE_PATHS = {
    "tools/scrub-terms.txt",
    "tools/scrub-check.py",
    "tools/okf-check.py",
    # LICENSE legitimately names the copyright holder (an entity name that may
    # match a scrub term); it is the legal attribution, not an in-house leak.
    "LICENSE",
}


def load_terms(path):
    """Return the list of lowercase terms from the terms file."""
    terms = []
    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            terms.append(line.lower())
    return terms


def git_tracked_files():
    """Return git-tracked paths (repo-relative, forward slashes)."""
    out = subprocess.run(
        ["git", "-C", REPO_ROOT, "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [p for p in out.stdout.splitlines() if p]


def compile_patterns(terms):
    """Map each term to a compiled whole-word, case-insensitive regex.

    A term may contain spaces or punctuation (e.g. 'acme corp',
    'owner@example.com'); we anchor with \\b on each side so the match is
    a standalone token. re.escape keeps regex metacharacters literal.
    """
    return {term: re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
            for term in terms}


def frontmatter_id_lines(text):
    """Yield (lineno, id_value) for `id:` lines inside the leading `---` block.

    Only the first frontmatter block (delimited by a leading `---`) is inspected.
    Returns nothing for files without frontmatter.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            break
        m = re.match(r"\s*id:\s*(.+?)\s*$", lines[i])
        if m:
            yield i + 1, m.group(1)


def scan():
    if not os.path.isfile(TERMS_FILE):
        # No denylist configured means nothing to scrub - a clean pass, not an error.
        # (A store that DERIVES its denylist may gitignore it, so it is legitimately
        # absent on a fresh clone; the blank template still passes.)
        print(f"scrub-check: no terms file at {TERMS_FILE} - nothing to scan "
              f"(no denylist configured).")
        return 0

    terms = load_terms(TERMS_FILE)
    if not terms:
        print(f"scrub-check: no in-house terms configured in {TERMS_FILE} yet — "
              f"nothing to scan (expected for a fresh template). Add your instance's "
              f"private terms there before you distribute your own copy.")
        return 0
    patterns = compile_patterns(terms)

    hits = []  # (path, lineno_label, term)

    for rel in git_tracked_files():
        if rel in EXCLUDE_PATHS:
            continue

        # (c) FILENAME / path surface
        for term, pat in patterns.items():
            if pat.search(rel):
                hits.append((rel, "filename", term))

        abspath = os.path.join(REPO_ROOT, rel)
        try:
            with open(abspath, "r", encoding="utf-8") as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError):
            # Binary or unreadable file — path surface already checked; skip body.
            continue

        # (a) CONTENTS surface — per line, so we can report a line number.
        for lineno, line in enumerate(text.splitlines(), start=1):
            for term, pat in patterns.items():
                if pat.search(line):
                    hits.append((rel, str(lineno), term))

        # (b) frontmatter id: surface — reported explicitly (also caught by (a),
        # but flagging the id line makes an id leak unambiguous).
        for lineno, id_value in frontmatter_id_lines(text):
            for term, pat in patterns.items():
                if pat.search(id_value):
                    hits.append((rel, f"id@{lineno}", term))

    if not hits:
        print("scrub-check: clean — no in-house terms found.")
        return 0

    # Stable, de-duplicated output.
    for path, label, term in sorted(set(hits)):
        print(f"{path}:{label}: {term}")
    print(f"\nscrub-check: {len(set(hits))} hit(s) — review before distribution.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(scan())
