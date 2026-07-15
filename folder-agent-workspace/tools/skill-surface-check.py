#!/usr/bin/env python3
"""Validate tracked runtime skill discovery surfaces and thin neutral pointers.

Discovers */skills/*/SKILL.md files. Each must carry scalar name and description
frontmatter, have a name unique within its adapter, stay a thin pointer, and link to
at least one tracked neutral Markdown playbook. Stdlib only.
"""
import argparse
import posixpath
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
MAX_SKILL_LINES = 30
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
BLOCK_SCALAR_RE = re.compile(r"^[|>](?:[+-]?[1-9]?|[1-9]?[+-]?)$")
DISCOVERY_KEYS = {"name", "description"}


def tracked_files(root):
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files"], capture_output=True, text=True)
    if result.returncode:
        raise OSError(result.stderr.strip() or "git ls-files failed")
    return {line for line in result.stdout.splitlines() if line}


def skill_paths(tracked):
    found = []
    for rel in tracked:
        parts = PurePosixPath(rel).parts
        if len(parts) >= 4 and parts[-3] == "skills" and parts[-1] == "SKILL.md":
            found.append(rel)
    return sorted(found)


def discovery_scalar(raw):
    value = raw.strip()
    if not value:
        return "", False
    if value[0] in "'\"":
        if len(value) < 2 or value[-1] != value[0]:
            return value, False
        return value[1:-1], bool(value[1:-1])
    invalid = (value.lower() in {"null", "~"} or value == "-"
               or BLOCK_SCALAR_RE.fullmatch(value) is not None
               or value.startswith(("[", "{", "!", "&", "*")))
    return value, not invalid


def frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return None, None, None, None
    try:
        end = lines.index("---", 1)
    except ValueError:
        return None, None, None, None
    values, valid, issues, active = {}, {}, [], None
    for line in lines[1:end]:
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            key, raw = match.group(1), match.group(2)
            active = key if key in DISCOVERY_KEYS else None
            if key in DISCOVERY_KEYS:
                value, scalar = discovery_scalar(raw)
                if key in values:
                    valid[key] = False
                    issues.append(f"duplicate frontmatter key {key!r}")
                else:
                    valid[key] = scalar
                values[key] = value
            else:
                values[key] = raw.strip()
        elif active and line[:1].isspace() and line.strip() and not line.lstrip().startswith("#"):
            valid[active] = False
            issues.append(f"{active} must stay on one physical frontmatter line")
    return values, lines[end + 1:], valid, issues


def local_target(skill_rel, raw):
    target = raw.strip()
    if target.startswith("<"):
        close = target.find(">")
        target = target[1:close].strip() if close >= 0 else target
    else:
        try:
            parts = shlex.split(target)
        except ValueError:
            parts = [target]
        target = parts[0] if parts else ""
    if not target or target.startswith("#") or target.startswith("/") or SCHEME_RE.match(target):
        return None
    target = unquote(target.split("#", 1)[0].split("?", 1)[0])
    return posixpath.normpath(posixpath.join(posixpath.dirname(skill_rel), target))


def check_root(root):
    root = Path(root)
    tracked = tracked_files(root)
    skills = skill_paths(tracked)
    adapter_roots = sorted({posixpath.dirname(posixpath.dirname(posixpath.dirname(rel)))
                            for rel in skills})
    problems = []
    names = {}
    for rel in skills:
        path = root / rel
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            problems.append(f"{rel}: unreadable SKILL.md ({exc})")
            continue
        lines = text.splitlines()
        meta, body, valid, metadata_issues = frontmatter(text)
        if meta is None:
            problems.append(f"{rel}: missing or unterminated frontmatter")
            continue
        problems.extend(f"{rel}: {issue}" for issue in metadata_issues)
        name = meta.get("name", "").strip()
        description = meta.get("description", "").strip()
        if not valid.get("name"):
            problems.append(f"{rel}: frontmatter needs a non-empty scalar name")
        if not valid.get("description"):
            problems.append(f"{rel}: frontmatter needs a non-empty one-line description")
        adapter = posixpath.dirname(posixpath.dirname(posixpath.dirname(rel)))
        if valid.get("name"):
            key = (adapter, name)
            if key in names:
                problems.append(f"{rel}: duplicate skill name {name!r} in adapter {adapter!r} "
                                f"(also {names[key]})")
            else:
                names[key] = rel
        if len(lines) > MAX_SKILL_LINES:
            problems.append(f"{rel}: {len(lines)} lines (max {MAX_SKILL_LINES}); keep adapter skills thin")
        setext = any(index and re.fullmatch(r"\s*-{3,}\s*", line) and body[index - 1].strip()
                     for index, line in enumerate(body))
        if any(line.lstrip().startswith("##") for line in body) or setext:
            problems.append(f"{rel}: content section in thin skill pointer")
        if any(line.lstrip().startswith(("```", "~~~")) for line in body):
            problems.append(f"{rel}: code fence in thin skill pointer")

        neutral_markdown = 0
        for raw in LINK_RE.findall(text):
            target = local_target(rel, raw)
            if target is None:
                continue
            if target == ".." or target.startswith("../"):
                problems.append(f"{rel}: local link escapes the repository: {raw}")
                continue
            target_parts = PurePosixPath(target).parts
            in_adapter = any(target == adapter_root or target.startswith(adapter_root + "/")
                             for adapter_root in adapter_roots)
            if in_adapter or (target_parts and target_parts[0].startswith(".")):
                problems.append(f"{rel}: local link targets an adapter surface: {raw}")
                continue
            if target not in tracked or not (root / target).is_file():
                problems.append(f"{rel}: local link target is not a tracked file: {raw}")
                continue
            if PurePosixPath(target).suffix.lower() == ".md":
                neutral_markdown += 1
        if neutral_markdown == 0:
            problems.append(f"{rel}: needs a resolvable local Markdown link to a neutral playbook")
    return sorted(set(problems))


def fixture(skill_text=None, *, second=None, extras=None):
    temp = tempfile.TemporaryDirectory(prefix="skill-surface-selftest-")
    root = Path(temp.name)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "playbook.md").write_text("# Neutral playbook\n", encoding="utf-8")
    if skill_text is not None:
        path = root / ".adapter/skills/one/SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text(skill_text, encoding="utf-8")
    if second is not None:
        path = root / ".adapter/skills/two/SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text(second, encoding="utf-8")
    for rel, content in (extras or {}).items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    return temp, root


def sample(*, name="one", description="Use for one exact case", link="../../../playbook.md", extra=""):
    return ("---\n" f"name: {name}\n" f"description: {description}\n" "type: skill\n---\n\n"
            "# One\n\n" f"Follow [the neutral playbook]({link}).\n" f"{extra}")


def self_test():
    cases = []
    cases.append((None, {}, None))
    cases.append((sample(), {}, None))
    cases.append((sample(link='../../../playbook.md "Playbook"'), {}, None))
    cases.append((sample().replace("name: one\n", ""), {}, "non-empty scalar name"))
    cases.append((sample().replace("description: Use for one exact case\n", ""), {},
                  "non-empty one-line description"))
    cases.append((sample(name="|"), {}, "non-empty scalar name"))
    cases.append((sample(name="[one]"), {}, "non-empty scalar name"))
    cases.append((sample(description=""), {}, "non-empty one-line description"))
    cases.append((sample(description="|+"), {}, "non-empty one-line description"))
    cases.append((sample(description="null"), {}, "non-empty one-line description"))
    cases.append((sample().replace("description: Use for one exact case",
                                   "description: Use for one exact case\n  continued"), {}, "physical frontmatter line"))
    cases.append((sample().replace("name: one", "name: one\n  continued"), {},
                  "physical frontmatter line"))
    cases.append((sample().replace("name: one", "name: one\nname: null"), {},
                  "duplicate frontmatter key"))
    cases.append((sample().replace("description: Use for one exact case",
                                   "description: Use for one exact case\ndescription: null"), {}, "duplicate frontmatter key"))
    cases.append((sample(), {"second": sample(name="one")}, "duplicate skill name"))
    cases.append((sample(link="../../../missing.md"), {}, "not a tracked file"))
    cases.append((sample(link="../../../../outside.md"), {}, "escapes the repository"))
    cases.append((sample(link="../../adapter-note.md"),
                  {"extras": {".adapter/adapter-note.md": "# Adapter\n"}}, "targets an adapter surface"))
    cases.append((sample(extra="\n".join(f"line {i}" for i in range(25))), {}, "max 30"))
    cases.append((sample(extra="## Procedure\n"), {}, "content section"))
    cases.append((sample(extra="   ## Procedure\n"), {}, "content section"))
    cases.append((sample(extra="Procedure\n---\n"), {}, "content section"))
    cases.append((sample(extra="```text\ncommand\n```\n"), {}, "code fence"))
    for index, (skill_text, options, expected) in enumerate(cases, start=1):
        temp, root = fixture(skill_text, second=options.get("second"), extras=options.get("extras"))
        try:
            problems = check_root(root)
        finally:
            temp.cleanup()
        if expected is None and problems:
            raise AssertionError(f"case {index} unexpectedly failed: {problems}")
        if expected is not None and not any(expected in problem for problem in problems):
            raise AssertionError(f"case {index} omitted {expected!r}: {problems}")
    print("skill-surface-check self-test: all green - discovery, metadata, links, and thin pointers enforced.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run disposable fixture tests")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    try:
        problems = check_root(ROOT)
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"skill-surface-check: failure - {exc}", file=sys.stderr)
        return 1
    if problems:
        for problem in problems:
            print(problem)
        print(f"\nskill-surface-check: {len(problems)} violation(s).", file=sys.stderr)
        return 1
    print(f"skill-surface-check: clean - {len(skill_paths(tracked_files(ROOT)))} skill pointer(s) checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
