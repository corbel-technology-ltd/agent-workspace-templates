#!/usr/bin/env python3
"""instantiate.py - copy one family member out into a fresh git repo of its own.

The take-just-one-part path: each member folder is self-contained, so instantiation is a copy
plus `git init` plus a first commit. Nothing is filled in here - open the new repo in your agent
runtime and its onboarding gate takes over.

Usage:
    python3 instantiate.py <commonplace|lodestar|chandlery> <destination>

Deterministic, stdlib only. Refuses a non-empty destination.
"""
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Assembled-repo folder names first, local build names second.
MEMBERS = {
    "commonplace": ["commonplace", "Workspace-Template"],
    "lodestar": ["lodestar", "Shared-Context-Template"],
    "chandlery": ["chandlery", "Chandlery-Template"],
}


def fail(msg):
    print(f"instantiate: {msg}", file=sys.stderr)
    sys.exit(1)


def find_member(name):
    for candidate in MEMBERS[name]:
        for base in (HERE, HERE.parent):
            p = base / candidate
            if (p / "AGENTS.md").is_file():
                return p
    fail(f"member folder for {name!r} not found beside this script")


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in MEMBERS:
        print(__doc__)
        return 1
    name, dest = sys.argv[1], Path(sys.argv[2]).expanduser()
    src = find_member(name)
    if dest.exists() and any(dest.iterdir()):
        fail(f"destination {dest} exists and is not empty")
    shutil.copytree(src, dest, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
    subprocess.run(["git", "init", "-q"], cwd=dest, check=True)
    subprocess.run(["git", "add", "-A"], cwd=dest, check=True)
    r = subprocess.run(["git", "commit", "-q", "-m",
                        f"chore: instantiate {name} from the Harbour template"],
                       cwd=dest, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"instantiate: copied, but the first commit needs git identity set - run:\n"
              f"  git -C {dest} commit -m 'chore: instantiate {name}'")
    print(f"instantiate: {name} -> {dest}")
    print("Next: open it in your agent runtime; the onboarding gate takes over "
          "(or follow INSTALL.md by hand).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
