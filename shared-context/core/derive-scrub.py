#!/usr/bin/env python3
"""derive-scrub.py - generate the scrub denylist from the boundaries file.

The confidentiality line is written ONCE, in boundaries/boundaries.md; scrub denylists derive
from it mechanically. This reads every backticked term from the `## Never share` section and
prints it (one lowercase term per line), or rewrites tools/scrub-terms.txt with --write. Copy the
same output into any consuming workspace's scrub-terms.txt so every member of the family scrubs
against one line.

Term format in boundaries.md: each bullet begins with the term in backticks -
    - `internal-hostname` - why it is sensitive

Deterministic, idempotent, stdlib only. Exit 0 with a note when the section is empty (a fresh
blank store).

Usage:
    python3 core/derive-scrub.py            # print the derived terms
    python3 core/derive-scrub.py --write    # rewrite tools/scrub-terms.txt
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOUNDARIES = ROOT / "boundaries" / "boundaries.md"
SCRUB = ROOT / "tools" / "scrub-terms.txt"

TERM_RE = re.compile(r"^\s*-\s+`([^`]+)`")

HEADER = """\
# scrub-terms.txt - GENERATED from boundaries/boundaries.md (## Never share).
# Do not edit by hand: edit the boundaries file, then re-run
#   python3 core/derive-scrub.py --write
# Format: one lowercase term per line. scrub-check matches case-insensitive whole words.
"""


def never_share_terms():
    if not BOUNDARIES.exists():
        print("derive-scrub: boundaries/boundaries.md not found.", file=sys.stderr)
        sys.exit(1)
    lines = BOUNDARIES.read_text(encoding="utf-8").splitlines()
    terms, capturing, in_comment = [], False, False
    for line in lines:
        s = line.strip()
        # Skip HTML-comment blocks so the doc's illustrative <!-- `example` --> bullets
        # (which can span lines - only the first carries the '<!--') never leak into the
        # denylist and brick the scrub gate on a virgin store.
        if in_comment:
            if "-->" in s:
                in_comment = False
            continue
        if s.startswith("<!--"):
            if "-->" not in s:
                in_comment = True
            continue
        if s.startswith("## "):
            capturing = s.lower() == "## never share"
            continue
        if capturing:
            m = TERM_RE.match(line)
            if m:
                terms.append(m.group(1).strip().lower())
    # stable order, no duplicates
    seen, out = set(), []
    for t in terms:
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


def main():
    terms = never_share_terms()
    if not terms:
        print("derive-scrub: the Never-share list is empty (expected for a blank store). "
              "Populate boundaries/boundaries.md, then re-run.")
        return 0
    if "--write" in sys.argv:
        SCRUB.write_text(HEADER + "\n" + "\n".join(terms) + "\n", encoding="utf-8")
        print(f"derive-scrub: wrote {len(terms)} term(s) to tools/scrub-terms.txt.")
    else:
        for t in terms:
            print(t)
    return 0


if __name__ == "__main__":
    sys.exit(main())
