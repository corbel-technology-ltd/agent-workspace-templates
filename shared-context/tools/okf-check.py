#!/usr/bin/env python3
"""Pre-distribution structural gate: OKF-compatible frontmatter + body-link mirror.

Over every git-tracked `*.md` file with YAML frontmatter, verify:

  (a) required key `type` is present and non-empty (concept files only);
  (b) for each `related[].ref`:
        - the target file EXISTS                       -> else DANGLING
        - the ref is mirrored as an inline markdown body link
          (basename OR path match)                     -> else UNMIRRORED;
  (c) reserved files:
        - `index.md` must carry NO frontmatter (it lists `* [Title](rel) - desc`);
        - `log.md` is the change-log file;
      reserved files are exempt from the `type`/`related` requirements, but a
      NON-reserved concept file missing `type` is flagged `missing type`.

Frontmatter is parsed with a minimal hand parser (no PyYAML): split on the leading
`---` block, then line-scan for `type:` and for `ref:` inside the `related:` list.

Prints each violation as:
    path: ref -> DANGLING
    path: ref -> UNMIRRORED
    path: missing type
    path: index.md has frontmatter (reserved file)

Exit 0 if clean, 1 if any violation (or on a usage error).

Usage:
    python3 tools/okf-check.py
"""

import os
import re
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# tools/ scripts are not OKF concept files; they are not *.md so they are skipped
# by the *.md filter anyway, but keep the intent explicit for any future *.md here.
EXCLUDE_PATHS = set()


def git_tracked_md_files():
    """Return git-tracked `*.md` paths (repo-relative, forward slashes)."""
    out = subprocess.run(
        ["git", "-C", REPO_ROOT, "ls-files", "*.md"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [p for p in out.stdout.splitlines() if p and p not in EXCLUDE_PATHS]


def split_frontmatter(text):
    """Split a leading `---` frontmatter block from the body.

    Returns (frontmatter_lines, body_text). If there is no leading `---` block,
    frontmatter_lines is None and body_text is the whole file.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fm = lines[1:i]
            body = "\n".join(lines[i + 1:])
            return fm, body
    # Unterminated frontmatter — treat the whole thing as body, no frontmatter.
    return None, text


def parse_type(fm_lines):
    """Return the `type:` value (stripped) or '' if absent/empty.

    Only top-level (column-0) `type:` keys count, so a nested `type:` inside a
    list item is not mistaken for the document type.
    """
    for line in fm_lines:
        m = re.match(r"type:\s*(.*)$", line)
        if m:
            return m.group(1).strip().strip("'\"")
    return ""


def parse_refs(fm_lines):
    """Return the list of `ref:` values found in the `related:` block.

    Handles the workspace's inline-map list form:
        related:
          - {ref: path/to/file.md, dimension: how, polarity: requires}
    and the plain block form:
        related:
          - ref: path/to/file.md
    by simply scanning every frontmatter line for a `ref:` token.
    """
    refs = []
    for line in fm_lines:
        for m in re.finditer(r"ref:\s*([^,}\s]+)", line):
            refs.append(m.group(1).strip().strip("'\""))
    return refs


def body_link_targets(body):
    """Return the set of link targets from inline markdown links in the body.

    Matches `[text](target)` and strips any `#anchor`. Reference-style and bare
    autolinks are not part of the mirroring convention, so only `](target)` form
    is collected.
    """
    targets = set()
    for m in re.finditer(r"\]\(([^)]+)\)", body):
        target = m.group(1).strip()
        # Drop a fragment/anchor and any surrounding angle brackets or title.
        target = target.split()[0] if target else target
        target = target.split("#", 1)[0]
        target = target.strip("<>")
        if target:
            targets.add(target)
    return targets


def is_mirrored(ref, link_targets):
    """True if `ref` is mirrored by any body link (basename OR path match)."""
    ref_base = os.path.basename(ref)
    for target in link_targets:
        if target == ref:
            return True
        if os.path.basename(target) == ref_base:
            return True
    return False


def check():
    violations = []  # list of formatted strings

    for rel in git_tracked_md_files():
        abspath = os.path.join(REPO_ROOT, rel)
        try:
            with open(abspath, "r", encoding="utf-8") as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError):
            continue

        basename = os.path.basename(rel)
        fm_lines, body = split_frontmatter(text)

        # (c) reserved files -------------------------------------------------
        if basename == "index.md":
            if fm_lines is not None:
                violations.append(
                    f"{rel}: index.md has frontmatter (reserved file)")
            # index.md and log.md are exempt from type/related checks.
            continue
        if basename == "log.md":
            continue

        # Files without frontmatter are not OKF concept files — nothing to check.
        if fm_lines is None:
            continue

        # (a) required type --------------------------------------------------
        if not parse_type(fm_lines):
            violations.append(f"{rel}: missing type")

        # (b) related refs: existence + body-link mirror ---------------------
        refs = parse_refs(fm_lines)
        if refs:
            link_targets = body_link_targets(body)
            for ref in refs:
                target_abs = os.path.join(REPO_ROOT, ref)
                if not os.path.isfile(target_abs):
                    violations.append(f"{rel}: {ref} -> DANGLING")
                elif not is_mirrored(ref, link_targets):
                    violations.append(f"{rel}: {ref} -> UNMIRRORED")

    if not violations:
        print("okf-check: clean — frontmatter and body-link mirroring OK.")
        return 0

    for line in violations:
        print(line)
    print(f"\nokf-check: {len(violations)} violation(s) — fix before distribution.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(check())
