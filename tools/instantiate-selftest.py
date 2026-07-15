#!/usr/bin/env python3
"""Prove each family member remains healthy after standalone extraction."""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEMBERS = ("folder-agent-workspace", "shared-context", "capability-registry")
EXTRACTION_SAFE_GATES = {
    "folder-agent-workspace": (
        "tools/scrub-check.py",
        "tools/okf-check.py",
        "tools/agnostic-check.py",
        "tools/skill-surface-check.py",
        "tools/memory-selftest.py",
        "tools/decomposition-check.py",
        "tools/decomposition-selftest.py",
    ),
    "shared-context": (
        "tools/scrub-check.py",
        "tools/okf-check.py",
        "tools/agnostic-check.py",
        "tools/skill-surface-check.py",
        "tools/shared-lint.py",
    ),
    "capability-registry": (
        "tools/scrub-check.py",
        "tools/okf-check.py",
        "tools/agnostic-check.py",
        "tools/skill-surface-check.py",
    ),
}
TOKEN_RE = re.compile(r"<<[A-Za-z_][A-Za-z0-9_]*>>")
SIBLING_REL_RE = re.compile(
    r"\.\./(?:folder-agent-workspace|shared-context|capability-registry)(?:/|\b)", re.I
)


def run(args, *, cwd, env):
    return subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True)


def token_inventory(root):
    inventory = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        try:
            matches = TOKEN_RE.findall(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            continue
        if matches:
            inventory[path.relative_to(root).as_posix()] = matches
    return inventory


def tracked_files(root):
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files"], check=True, capture_output=True, text=True
    )
    return set(result.stdout.splitlines())


def source_files(name):
    """Files instantiate will ship, including non-ignored candidate additions under review."""
    prefix = name + "/"
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "--cached", "--others", "--exclude-standard",
         "--", name],
        check=True,
        capture_output=True,
        text=True,
    )
    return {path[len(prefix):] for path in result.stdout.splitlines() if path.startswith(prefix)}


def sibling_dependencies(root):
    found = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if SIBLING_REL_RE.search(text):
            found.append(path.relative_to(root).as_posix())
    return found


def check_member(name, dest, env):
    problems = []
    source = ROOT / name
    expected_files = source_files(name)
    if name == "folder-agent-workspace":
        expected_files.add("00_meta/template-origin.json")
    delivered_files = tracked_files(dest)
    if delivered_files != expected_files:
        missing = sorted(expected_files - delivered_files)
        extra = sorted(delivered_files - expected_files)
        problems.append(f"tracked layout differs (missing={missing[:3]}, extra={extra[:3]})")
    for rel in sorted(source_files(name) & delivered_files):
        if (source / rel).read_bytes() != (dest / rel).read_bytes():
            problems.append(f"copied bytes changed: {rel}")
    if not (dest / ".uninitialised").is_file():
        problems.append("missing .uninitialised sentinel")
    if token_inventory(dest) != token_inventory(source):
        problems.append("placeholder-token inventory changed during extraction")
    stamp = dest / "00_meta" / "template-origin.json"
    if name == "folder-agent-workspace" and not stamp.is_file():
        problems.append("Folder origin stamp missing")
    elif name == "folder-agent-workspace":
        try:
            origin = json.loads(stamp.read_text(encoding="utf-8"))
            if origin.get("member") != name:
                problems.append("Folder origin stamp has the wrong member")
            if origin.get("accepted_local_manifest") != {} or origin.get("values") != {}:
                problems.append("Folder origin stamp does not start with empty local state")
            manifest = origin.get("managed_manifest")
            if not isinstance(manifest, dict) or not manifest:
                problems.append("Folder origin stamp has no managed manifest")
            else:
                for rel, expected in manifest.items():
                    path = dest / rel
                    actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
                    if actual != expected:
                        problems.append(f"Folder origin manifest mismatch: {rel}")
        except (OSError, ValueError, TypeError) as exc:
            problems.append(f"Folder origin stamp is unreadable: {exc}")
    if name != "folder-agent-workspace" and stamp.exists():
        problems.append("Folder-only origin stamp leaked into this member")
    for rel in sibling_dependencies(dest):
        problems.append(f"sibling-relative dependency: {rel}")

    commands = [[sys.executable, gate] for gate in EXTRACTION_SAFE_GATES[name]]
    if name == "capability-registry":
        commands.append([sys.executable, "core/chandler.py", "verify"])
    for command in commands:
        result = run(command, cwd=dest, env=env)
        if result.returncode:
            detail = (result.stdout + result.stderr).strip().splitlines()
            problems.append(
                f"{' '.join(command[1:])} exited {result.returncode}"
                + (f": {detail[0]}" if detail else "")
            )

    status = run(["git", "status", "--porcelain"], cwd=dest, env=env)
    if status.returncode or status.stdout.strip():
        problems.append("delivered git repository is not clean")
    branch = run(["git", "branch", "--show-current"], cwd=dest, env=env)
    commits = run(["git", "rev-list", "--count", "HEAD"], cwd=dest, env=env)
    if branch.returncode or branch.stdout.strip() != "main":
        problems.append("delivered git repository is not on main")
    if commits.returncode or commits.stdout.strip() != "1":
        problems.append("delivered git repository does not contain exactly one commit")
    return problems


def main():
    parser = argparse.ArgumentParser(
        description="Instantiate every member and run extraction-safe gates."
    )
    parser.add_argument(
        "--work-root",
        type=Path,
        help="parent for the disposable run (defaults to the system temporary directory)",
    )
    args = parser.parse_args()

    if args.work_root:
        args.work_root.mkdir(parents=True, exist_ok=True)
        work = Path(tempfile.mkdtemp(prefix="instantiate-selftest-", dir=args.work_root))
    else:
        work = Path(tempfile.mkdtemp(prefix="instantiate-selftest-"))
    env = dict(
        os.environ,
        HOME=str(work / "home"),
        GIT_CONFIG_GLOBAL=str(work / "gitconfig"),
        GIT_CONFIG_NOSYSTEM="1",
        GIT_AUTHOR_NAME="Template Self-Test",
        GIT_AUTHOR_EMAIL="template-selftest@example.invalid",
        GIT_COMMITTER_NAME="Template Self-Test",
        GIT_COMMITTER_EMAIL="template-selftest@example.invalid",
    )
    (work / "home").mkdir()
    (work / "gitconfig").write_text("", encoding="utf-8")
    problems = []
    try:
        for name in MEMBERS:
            dest = work / (name + "-parent") / name
            result = run(
                [sys.executable, str(ROOT / "instantiate.py"), name, str(dest)],
                cwd=ROOT,
                env=env,
            )
            if result.returncode:
                detail = (result.stdout + result.stderr).strip().splitlines()
                problems.append(
                    f"{name}: instantiate exited {result.returncode}"
                    + (f": {detail[0]}" if detail else "")
                )
                continue
            problems.extend(f"{name}: {problem}" for problem in check_member(name, dest, env))
    finally:
        shutil.rmtree(work, ignore_errors=True)

    if problems:
        for problem in problems:
            print(problem)
        print(f"instantiate-selftest: {len(problems)} problem(s).", file=sys.stderr)
        return 1
    print("instantiate-selftest: clean - 3 standalone members, extraction-safe gates green.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
