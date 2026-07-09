#!/usr/bin/env python3
"""instantiate.py - copy one family member out into a fresh git repo of its own.

The take-just-one-part path: each member folder is self-contained, so instantiation is a copy
plus `git init` plus a first commit. Nothing is filled in here - open the new repo in your agent
runtime and its onboarding gate takes over.

Usage:
    python3 instantiate.py <folder-agent-workspace|shared-context|capability-registry> <destination>

Example:
    python3 instantiate.py folder-agent-workspace ~/my-workspace

The destination must be a folder that does not exist yet (or is empty).
Never used a terminal? Start with START-HERE.md instead.

Deterministic, stdlib only. Refuses a non-empty destination.
"""
from __future__ import print_function

import sys

if sys.version_info < (3, 6):
    sys.stderr.write(
        "instantiate: this script needs Python 3, but you ran it with Python %d.%d.\n"
        "Try again with:  python3 instantiate.py %s\n"
        % (sys.version_info[0], sys.version_info[1], " ".join(sys.argv[1:])))
    sys.exit(1)

import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Assembled-repo folder names first, local build names second.
MEMBERS = {
    "folder-agent-workspace": ["folder-agent-workspace", "Folder-Agent-Workspace-Template"],
    "shared-context": ["shared-context", "Shared-Context-Template"],
    "capability-registry": ["capability-registry", "Capability-Registry-Template"],
}


def fail(msg):
    print("instantiate: " + msg, file=sys.stderr)
    sys.exit(1)


def find_member(name):
    for candidate in MEMBERS[name]:
        for base in (HERE, HERE.parent):
            p = base / candidate
            if (p / "AGENTS.md").is_file():
                return p
    fail("member folder for %r not found beside this script" % name)


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in MEMBERS:
        print(__doc__)
        return 1
    name, dest = sys.argv[1], Path(sys.argv[2]).expanduser()
    if shutil.which("git") is None:
        fail("git is not installed (or not on your PATH). Install it and run this again.\n"
             "  Windows: https://git-scm.com  |  Mac: type `git` in Terminal and accept the "
             "install prompt  |  Linux: `sudo apt install git`")
    src = find_member(name)
    if dest.is_file():
        fail("destination %s already exists and is a file, not a folder.\n"
             "Pick a folder name that does not exist yet, e.g. ~/my-workspace" % dest)
    if dest.is_dir() and any(dest.iterdir()):
        fail("destination %s already exists and is not empty.\n"
             "Pick a folder that does not exist yet (nothing is ever overwritten), "
             "e.g. ~/my-workspace" % dest)
    shutil.copytree(src, dest, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
    subprocess.run(["git", "init", "-q"], cwd=dest, check=True)
    subprocess.run(["git", "add", "-A"], cwd=dest, check=True)
    r = subprocess.run(["git", "commit", "-q", "-m",
                        "chore: instantiate %s from the Agent-Workspace-Templates template" % name],
                       cwd=dest, capture_output=True, text=True)
    if r.returncode != 0:
        print("instantiate: copied, but the first commit needs git identity set - run:\n"
              "  git -C %s commit -m 'chore: instantiate %s'" % (dest, name))
    print("instantiate: %s -> %s" % (name, dest))
    print("Next: open it in your agent runtime; the onboarding gate takes over "
          "(or follow INSTALL.md by hand).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
