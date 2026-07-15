#!/usr/bin/env python3
"""Copy one family member into a new, standalone git repository.

Usage:
    python3 instantiate.py <folder-agent-workspace|shared-context|capability-registry> <destination>

The destination must not exist. Nothing is overwritten and failures leave no partial workspace.
Never used a terminal? Start with START-HERE.md instead.
"""
from __future__ import print_function

import datetime
import hashlib
import importlib.util
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

if sys.version_info < (3, 8):
    sys.stderr.write(
        "instantiate: Python 3.8 or newer is required; you have %d.%d.\n"
        "Install a current Python, then run the same command again.\n"
        % (sys.version_info[0], sys.version_info[1]))
    sys.exit(1)

HERE = Path(__file__).resolve().parent
MEMBERS = {
    "folder-agent-workspace": ["folder-agent-workspace", "Folder-Agent-Workspace-Template"],
    "shared-context": ["shared-context", "Shared-Context-Template"],
    "capability-registry": ["capability-registry", "Capability-Registry-Template"],
}
DEFAULT_REPO_URL = "https://github.com/CORBEL-Technology/agent-workspace-templates.git"


def fail(msg):
    print("instantiate: " + msg, file=sys.stderr)
    raise SystemExit(1)


def find_member(name):
    for candidate in MEMBERS[name]:
        for base in (HERE, HERE.parent):
            path = base / candidate
            if (path / "AGENTS.md").is_file():
                return path
    fail("the %s template folder is missing. Download the repository again, then retry." % name)


def check_git_identity():
    """Prove a brand-new repo can identify its first commit, without touching the destination."""
    with tempfile.TemporaryDirectory(prefix="instantiate-git-check-") as temp:
        result = subprocess.run(
            ["git", "var", "GIT_AUTHOR_IDENT"], cwd=temp,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode:
        fail(
            "git needs your name and email before it can create the first save. Run:\n"
            "  git config --global user.name \"Your Name\"\n"
            "  git config --global user.email \"you@example.com\"\n"
            "Replace the example values, then run the install command again. "
            "No workspace files were created.")


def load_managed_paths():
    """Load the one path policy shipped with the workspace update tool."""
    policy = find_member("folder-agent-workspace") / "tools" / "template_paths.py"
    spec = importlib.util.spec_from_file_location("template_paths", policy)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_identity():
    """Return (repo URL, HEAD), degrading cleanly for an extracted source archive."""
    try:
        top = subprocess.run(
            ["git", "-C", str(HERE), "rev-parse", "--show-toplevel"],
            check=True, capture_output=True, text=True).stdout.strip()
        if Path(top).resolve() != HERE.resolve():
            raise subprocess.CalledProcessError(1, "git rev-parse")
        commit = subprocess.run(
            ["git", "-C", str(HERE), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True).stdout.strip()
        remote = subprocess.run(
            ["git", "-C", str(HERE), "remote", "get-url", "origin"],
            capture_output=True, text=True)
        repo_url = remote.stdout.strip() if remote.returncode == 0 else DEFAULT_REPO_URL
        return repo_url or DEFAULT_REPO_URL, commit
    except (OSError, subprocess.CalledProcessError):
        return DEFAULT_REPO_URL, "unknown"


def write_origin_stamp(stage, member):
    policy = load_managed_paths()
    repo_url, commit = source_identity()
    manifest = {
        rel: hashlib.sha256((stage / rel).read_bytes()).hexdigest()
        for rel in policy.managed_files(stage)
    }
    stamp = {
        "repo_url": repo_url,
        "member": member,
        "commit": commit,
        "instantiated": datetime.date.today().isoformat(),
        "managed_manifest": manifest,
        "accepted_local_manifest": {},
        "values": {},
    }
    target = stage / "00_meta" / "template-origin.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(stamp, indent=2) + "\n", encoding="utf-8")


def main():
    if len(sys.argv) != 3:
        fail("use exactly: python3 instantiate.py <member> <destination>\n"
             "Valid members: " + ", ".join(MEMBERS))
    name = sys.argv[1]
    if name not in MEMBERS:
        fail("%r is not a member name. Valid members: %s. Correct it and run again."
             % (name, ", ".join(MEMBERS)))

    dest = Path(sys.argv[2]).expanduser().absolute()
    if shutil.which("git") is None:
        fail("git is not installed. Mac: run `xcode-select --install`. "
             "Linux/WSL: run `sudo apt install git`. Then run this command again.")
    if dest.exists():
        fail("destination already exists: %s\n"
             "Nothing was overwritten. Choose an unused path and run again, for example:\n"
             "  python3 instantiate.py %s %s-new"
             % (shlex.quote(str(dest)), name, shlex.quote(str(dest))))

    src = find_member(name)
    dest.parent.mkdir(parents=True, exist_ok=True)
    check_git_identity()

    stage = Path(tempfile.mkdtemp(prefix=".%s.installing-" % dest.name,
                                  dir=str(dest.parent)))
    try:
        shutil.copytree(
            src, stage, dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", ".venv"))
        if name == "folder-agent-workspace":
            write_origin_stamp(stage, name)
        subprocess.run(["git", "init", "-q"], cwd=stage, check=True)
        subprocess.run(["git", "add", "-A"], cwd=stage, check=True)
        subprocess.run(
            ["git", "commit", "-q", "-m",
             "chore: instantiate %s from the Agent-Workspace-Templates template" % name],
            cwd=stage, check=True)
        subprocess.run(["git", "branch", "-M", "main"], cwd=stage, check=True)
        os.replace(str(stage), str(dest))
    except (OSError, subprocess.CalledProcessError) as exc:
        shutil.rmtree(stage, ignore_errors=True)
        fail("creation failed (%s). No partial workspace was kept. Fix the error, then run:\n"
             "  python3 instantiate.py %s %s" % (exc, name, shlex.quote(str(dest))))

    print("instantiate: %s -> %s" % (name, dest))
    print("Next: open it in your agent runtime; the onboarding gate takes over.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
