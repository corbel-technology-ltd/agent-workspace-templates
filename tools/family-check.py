#!/usr/bin/env python3
"""family-check.py - the family gate: members healthy, shared machinery in sync.

Five checks across the three member templates (found beside this repo root under their
assembled names or their local build names):

  (1) MEMBER GATES - each member's own pre-distribution gates exit 0 (scrub, okf, agnostic;
      plus shared-lint for the shared-context member and `chandler.py verify` for the registry).
  (2) VENDORED PARITY - every capability manifest in the registry member is checked against
      each member's vendored copy: byte-for-byte (sha256) identical. The family runs on its own
      supply chain; this is the check that makes that claim true.
  (3) LICENCE PARITY - every member's LICENSE is byte-identical to the family root's.
  (4) FAMILY THREAD - every member README names the family and points at FAMILY.md.
  (5) CHANGELOG DISCIPLINE - advisory warning when HEAD changes a member without changing the
      family CHANGELOG.md [Unreleased] block.

Exit 0 if all green, 1 otherwise. Stdlib only (the registry manifests are parsed with a minimal
line scanner, so this gate runs even where PyYAML is absent).

Usage:
    python3 tools/family-check.py
"""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MEMBERS = {
    "folder-agent-workspace": ["folder-agent-workspace", "Folder-Agent-Workspace-Template"],
    "shared-context": ["shared-context", "Shared-Context-Template"],
    "capability-registry": ["capability-registry", "Capability-Registry-Template"],
}

GATES = {
    "folder-agent-workspace": ["tools/scrub-check.py", "tools/okf-check.py", "tools/agnostic-check.py",
                 "tools/memory-selftest.py", "tools/update-selftest.py"],
    "shared-context": ["tools/scrub-check.py", "tools/okf-check.py", "tools/agnostic-check.py",
                 "tools/shared-lint.py"],
    "capability-registry": ["tools/scrub-check.py", "tools/okf-check.py", "tools/agnostic-check.py"],
}


def find(name):
    for candidate in MEMBERS[name]:
        for base in (ROOT, ROOT.parent):
            p = base / candidate
            if (p / "AGENTS.md").is_file():
                return p
    return None


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_entries(manifest: Path):
    """(target, sha256) pairs from a manifest.yml, minimal parser (no PyYAML needed)."""
    target = None
    for line in manifest.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*-?\s*target:\s*(\S+)", line)
        if m:
            target = m.group(1)
        m = re.match(r"\s*sha256:\s*([0-9a-f]{64})", line)
        if m and target:
            yield target, m.group(1)
            target = None


def unreleased_block(text):
    match = re.search(r"^## \[Unreleased\]\s*$\n(.*?)(?=^## \[|\Z)",
                      text, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def changelog_warning():
    """Advisory only: a member-changing HEAD should grow the family Unreleased notes."""
    try:
        changed = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
            cwd=ROOT, check=True, capture_output=True, text=True).stdout.splitlines()
        prefixes = tuple(candidate + "/" for candidates in MEMBERS.values()
                         for candidate in candidates)
        if not any(path.startswith(prefixes) for path in changed):
            return ""
        before = subprocess.run(
            ["git", "show", "HEAD^:CHANGELOG.md"], cwd=ROOT,
            capture_output=True, text=True).stdout
        after = subprocess.run(
            ["git", "show", "HEAD:CHANGELOG.md"], cwd=ROOT,
            capture_output=True, text=True).stdout
        if unreleased_block(before) == unreleased_block(after):
            return ("warning: newest commit changed a family member but did not add a "
                    "CHANGELOG.md [Unreleased] entry")
    except (OSError, subprocess.CalledProcessError):
        return ""
    return ""


def main():
    problems = []
    paths = {}
    for name in MEMBERS:
        p = find(name)
        if p is None:
            problems.append(f"member missing: {name} (looked for {MEMBERS[name]})")
        else:
            paths[name] = p

    # (1) member gates
    for name, p in paths.items():
        for gate in GATES[name]:
            r = subprocess.run([sys.executable, str(p / gate)],
                               cwd=p, capture_output=True, text=True)
            if r.returncode != 0:
                problems.append(f"{name}: gate failed: {gate}\n"
                                + "\n".join("    " + ln for ln in
                                            (r.stdout + r.stderr).splitlines()[:6]))
        if name == "capability-registry":
            r = subprocess.run([sys.executable, str(p / "core/chandler.py"), "verify"],
                               cwd=p, capture_output=True, text=True)
            if r.returncode != 0:
                problems.append(f"capability-registry: `chandler.py verify` failed\n"
                                + (r.stdout + r.stderr)[:400])

    # (2) vendored parity via the registry's manifests
    if "capability-registry" in paths:
        registry = paths["capability-registry"] / "registry"
        for manifest in sorted(registry.glob("*/manifest.yml")):
            cap = manifest.parent.name
            for target, want in manifest_entries(manifest):
                for name, p in paths.items():
                    vendored = p / target
                    if not vendored.is_file():
                        problems.append(f"{name}: vendored copy missing: {target} ({cap})")
                    elif sha256(vendored) != want:
                        problems.append(
                            f"{name}: vendored {target} drifted from registry capability "
                            f"'{cap}' - pack or install to reconcile")

    # (3) licence parity
    root_licence = ROOT / "LICENSE"
    if not root_licence.is_file():
        problems.append("family root: LICENSE missing")
    else:
        want = sha256(root_licence)
        for name, p in paths.items():
            lic = p / "LICENSE"
            if not lic.is_file():
                problems.append(f"{name}: LICENSE missing")
            elif sha256(lic) != want:
                problems.append(f"{name}: LICENSE differs from the family root's")

    # (4) family thread
    for name, p in paths.items():
        readme = p / "README.md"
        text = readme.read_text(encoding="utf-8") if readme.is_file() else ""
        if "FAMILY.md" not in text:
            problems.append(f"{name}: README.md does not point at FAMILY.md")

    warning = changelog_warning()
    if warning:
        print(warning)

    if problems:
        for pr in problems:
            print(pr)
        print(f"\nfamily-check: {len(problems)} problem(s).", file=sys.stderr)
        return 1
    print(f"family-check: clean - {len(paths)} members, gates green, vendored tools in sync, "
          f"licences identical, family thread present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
