#!/usr/bin/env python3
"""Generate / refresh the '## Related' body section of each OKF content file from its
frontmatter `related:` edges.

OKF consumers read relationships from inline markdown links in the body, not from the typed
frontmatter `related:` extension. This script mirrors every `related[].ref` as a body link in a
uniform '## Related' section so the (untyped) graph is visible to an OKF consumer and `okf-check`
passes. Idempotent: an existing '## Related' section is replaced. Reserved files (index.md, log.md)
and files without frontmatter `related:` edges are skipped.

Usage:  python3 tools/gen-related.py [--check]
        --check : report which files would change, write nothing (exit 1 if any would change).
"""
import os
import re
import sys
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FM_RE = re.compile(r"(?s)^(---\n.*?\n---\n)(.*)$")
REF_RE = re.compile(r"ref:\s*([^\s,}]+)")
NAME_RE = re.compile(r"^name:\s*(.+)$", re.M)
H1_RE = re.compile(r"^#\s+(.+)$", re.M)
RELATED_RE = re.compile(r"(?ms)^##\s+Related\b.*?(?=^##\s|\Z)")


def tracked_md():
    out = subprocess.check_output(["git", "ls-files", "*.md"], cwd=ROOT).decode()
    return [f for f in out.splitlines() if f.strip()]


def _unquote_yaml_scalar(s):
    """Undo the quoting apply.py / a hand author may put on a frontmatter scalar.

    Single-quoted YAML doubles internal quotes ('O''Brien'); double-quoted uses
    backslash escapes. Plain scalars pass through. Keeps gen-related stdlib-only
    while round-tripping names the onboarding engine legitimately produces."""
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] == "'":
        return s[1:-1].replace("''", "'")
    if len(s) >= 2 and s[0] == s[-1] == '"':
        try:
            return s[1:-1].encode("utf-8").decode("unicode_escape")
        except (UnicodeDecodeError, ValueError):
            return s[1:-1]
    return s


def title_for(ref):
    path = os.path.join(ROOT, ref)
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return os.path.basename(ref)
    m = FM_RE.match(text)
    if m:
        nm = NAME_RE.search(m.group(1))
        if nm:
            return _unquote_yaml_scalar(nm.group(1))
    h1 = H1_RE.search(text)
    return h1.group(1).strip() if h1 else os.path.basename(ref)


def related_section(srcfile, refs):
    srcdir = os.path.dirname(srcfile)
    lines = ["## Related", ""]
    for r in refs:
        rel = os.path.relpath(r, srcdir) if srcdir else r
        lines.append(f"- [{title_for(r)}]({rel})")
    return "\n".join(lines) + "\n"


def process(f):
    path = os.path.join(ROOT, f)
    if os.path.basename(f) in ("index.md", "log.md"):
        return False
    text = open(path, encoding="utf-8").read()
    m = FM_RE.match(text)
    if not m:
        return False
    fmblock, body = m.group(1), m.group(2)
    refs = REF_RE.findall(fmblock)
    if not refs:
        return False
    body = RELATED_RE.sub("\n", body).rstrip() + "\n"
    new = fmblock + body + "\n" + related_section(f, refs)
    if new != text:
        if "--check" not in sys.argv:
            open(path, "w", encoding="utf-8").write(new)
        return True
    return False


def main():
    changed = [f for f in tracked_md() if process(f)]
    verb = "would change" if "--check" in sys.argv else "updated"
    for f in changed:
        print(f"  {verb}: {f}")
    print(f"{len(changed)} file(s) {verb}.")
    if "--check" in sys.argv and changed:
        sys.exit(1)


if __name__ == "__main__":
    main()
