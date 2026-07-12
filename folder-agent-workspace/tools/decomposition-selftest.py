#!/usr/bin/env python3
"""Disposable behavioural proof for the context-decomposition gate."""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


MEMBER = Path(__file__).resolve().parents[1]
CHECKER = MEMBER / "tools" / "decomposition-check.py"
CODE_EXTS = (
    ".py", ".js", ".sh", ".ts", ".tsx", ".jsx", ".mjs", ".cjs", ".rs", ".go",
    ".rb", ".java", ".c", ".h", ".cpp", ".hpp", ".bash",
)
INDEX = """---
type: index
status: current
---

# Index
"""
GOOD_NOTE = """---
type: reference
status: current
---

# Note

[Folder map](00-INDEX.md)
"""
RELATED_NOTE = """---
type: reference
status: current
related:
  - {ref: topic/00-INDEX.md, dimension: where, polarity: part_of}
---

# Note
"""
GIT_ENV = dict(
    os.environ,
    GIT_AUTHOR_NAME="Test",
    GIT_AUTHOR_EMAIL="test@example.invalid",
    GIT_COMMITTER_NAME="Test",
    GIT_COMMITTER_EMAIL="test@example.invalid",
)


def run(args, *, cwd, expected=None):
    result = subprocess.run(args, cwd=cwd, env=GIT_ENV, capture_output=True, text=True)
    if expected is not None and result.returncode != expected:
        raise AssertionError(
            f"expected exit {expected}, got {result.returncode}: {' '.join(map(str, args))}\n"
            + result.stdout + result.stderr)
    return result


def write_files(root, files):
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if content is None:
            path.symlink_to("missing-target")
        else:
            path.write_text(content, encoding="utf-8")


def initialise(member, files, exceptions=""):
    (member / "tools").mkdir(parents=True, exist_ok=True)
    shutil.copy2(CHECKER, member / "tools" / CHECKER.name)
    (member / "tools" / "decomposition-exceptions.txt").write_text(exceptions, encoding="utf-8")
    write_files(member, files)
    run(["git", "init", "-q"], cwd=member, expected=0)
    run(["git", "add", "-A"], cwd=member, expected=0)
    run(["git", "commit", "-q", "-m", "fixture"], cwd=member, expected=0)
    return member


def check(member, *, cwd=None):
    return run([sys.executable, str(member / "tools" / CHECKER.name)], cwd=cwd or member)


def clean(result, label):
    if result.returncode != 0:
        raise AssertionError(f"{label}: expected clean\n{result.stdout}{result.stderr}")


def fails(result, needle, label):
    output = result.stdout + result.stderr
    if result.returncode == 0 or needle not in output:
        raise AssertionError(f"{label}: expected failure containing {needle!r}\n{output}")


def main():
    if not CHECKER.is_file():
        print("decomposition-selftest: ERROR - checker missing", file=sys.stderr)
        return 1
    try:
        with tempfile.TemporaryDirectory(prefix="decomposition-selftest-") as raw:
            temp = Path(raw)
            counter = 0

            def fixture(files, exceptions=""):
                nonlocal counter
                counter += 1
                return initialise(temp / f"case-{counter}", files, exceptions)

            result = check(fixture({"too-many-lines.md": "x\n" * 151}))
            fails(result, "151 lines (max 150)", "prose line ceiling")

            result = check(fixture({"too-many-characters.md": "x" * 12_001}))
            fails(result, "12001 characters (max 12000)", "prose character ceiling")

            code_files = {f"engine{ext}": "x\n" * 501 for ext in CODE_EXTS}
            result = check(fixture(code_files))
            for rel in code_files:
                fails(result, rel, f"code extension {Path(rel).suffix}")

            structural = {
                "AGENTS.md": "x\n" * 200,
                "CHANGELOG.md": "x\n" * 200,
                "50_registers/ledger.md": "x\n" * 200,
                "20_memory/journal/event.md": "x\n" * 200,
                "90_runs/run.md": "x\n" * 200,
                "30_schemas/schema.md": "x\n" * 200,
                "40_templates/example.md": "x\n" * 200,
            }
            clean(check(fixture(structural)), "structural exemptions")

            clean(check(fixture({
                "topic/00-INDEX.md": INDEX,
                "topic/linked.md": GOOD_NOTE,
                "topic/related.md": RELATED_NOTE,
            })), "valid concept membership")

            false_status = """---
type: reference
---

# Note

status: current
[Folder map](00-INDEX.md)
"""
            result = check(fixture({"topic/00-INDEX.md": INDEX, "topic/note.md": false_status}))
            fails(result, "no top-level frontmatter status", "frontmatter status parsing")

            bare_index = """---
type: reference
status: current
---

# Note

Owning file: 00-INDEX.md
"""
            result = check(fixture({"topic/00-INDEX.md": INDEX, "topic/note.md": bare_index}))
            fails(result, "no markdown link or related-edge ref", "owning-index reference parsing")

            result = check(fixture({
                "40_templates/topic/00-INDEX.md": INDEX,
                "40_templates/topic/note.md": "# bare note\n",
            }))
            fails(result, "no top-level frontmatter status", "exempt concept hygiene")
            fails(result, "no markdown link or related-edge ref", "exempt owning-index hygiene")

            excepted_note = "# bare note mentioning 00-INDEX.md\n" + "x\n" * 501
            result = check(fixture(
                {"topic/00-INDEX.md": INDEX, "topic/note.md": excepted_note},
                "topic/note.md  # atomic keep-intact fixture\n"))
            fails(result, "no top-level frontmatter status", "excepted concept hygiene")
            fails(result, "no markdown link or related-edge ref", "excepted owning-index hygiene")

            result = check(fixture(
                {"large.md": "x\n" * 151},
                "large.md  # first reason\nlarge.md  # duplicate reason\n"))
            fails(result, "duplicate entry for large.md", "duplicate exception")

            result = check(fixture(
                {"small.md": "small\n"}, "small.md  # no longer required\n"))
            fails(result, "under both prose ceilings", "unnecessary exception")

            result = check(fixture(
                {"20_memory/large.md": "x\n" * 200},
                "20_memory/large.md  # structural class\n"))
            fails(result, "is structurally exempt", "structural exception")

            result = check(fixture({}, "missing.md  # stale row\n"))
            fails(result, "stale entry", "stale exception")

            result = check(fixture({"unreadable.md": None}))
            fails(result, "tracked in-scope file is unreadable", "unreadable file")

            family = temp / "scoped-family"
            member = family / "member"
            (member / "tools").mkdir(parents=True)
            shutil.copy2(CHECKER, member / "tools" / CHECKER.name)
            (member / "tools" / "decomposition-exceptions.txt").write_text("", encoding="utf-8")
            (member / "inside.md").write_text("small\n", encoding="utf-8")
            (family / "outside.md").write_text("x\n" * 151, encoding="utf-8")
            run(["git", "init", "-q"], cwd=family, expected=0)
            run(["git", "add", "-A"], cwd=family, expected=0)
            run(["git", "commit", "-q", "-m", "scoped fixture"], cwd=family, expected=0)
            nested = member / "nested"
            nested.mkdir()
            clean(check(member, cwd=nested), "member-subdirectory git scoping")
    except (AssertionError, OSError) as exc:
        print(f"decomposition-selftest: FAIL - {exc}", file=sys.stderr)
        return 1

    print("decomposition-selftest: clean - ceilings, hygiene, exceptions, reads, and git scope proven.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
