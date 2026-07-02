#!/usr/bin/env python3
"""Claude Code adapter shim - the only bridge between Claude Code and the neutral core.

`.claude/settings.json` wires every hook event to `shim.py <hook-name>`. The shim reads Claude
Code's hook payload from stdin, translates it to the neutral contract documented in
core/RUNTIMES.md, invokes the matching `core/hooks/<hook-name>.py`, and passes stdout/stderr and
the exit code straight through (Claude Code treats exit 2 as "block", which is exactly the core
contract's block signal, so no mapping is needed).

Keep this file thin: translation only, no policy. Policy lives in core/hooks/.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "core" / "hooks"

# Claude Code tool name -> neutral op class (core/RUNTIMES.md).
OPS = {
    "Edit": "modify",
    "MultiEdit": "modify",
    "NotebookEdit": "modify",
    "Write": "create-or-overwrite",
    "Bash": "shell",
}


def neutral_payload(hook: str, data: dict) -> str:
    """Translate a Claude Code hook payload into the neutral contract."""
    if hook == "journal-guard":
        tool = data.get("tool_name") or data.get("tool") or ""
        ti = data.get("tool_input") or data.get("toolInput") or {}
        return json.dumps({
            "op": OPS.get(tool, ""),
            "path": ti.get("file_path") or ti.get("notebook_path") or "",
            "command": ti.get("command") or "",
        })
    if hook == "session-digest":
        return json.dumps({
            "reason": data.get("reason") or data.get("source") or "other",
            "session_id": str(data.get("session_id") or ""),
        })
    # session-brief, onboarding-gate, reaper, registry-drift take no payload
    return "{}"


def main():
    if len(sys.argv) != 2:
        sys.stderr.write("usage: shim.py <hook-name>\n")
        sys.exit(1)
    hook = sys.argv[1]
    core_hook = CORE / f"{hook}.py"
    # Fail OPEN if the core hook is missing: a partially-copied or renamed core must not
    # wedge every tool call. Blocking (exit 2) is reserved for a hook that actually ran
    # and decided to block - never for the shim failing to find it.
    if not core_hook.is_file():
        sys.stderr.write(f"[shim] core hook not found: {core_hook} - skipping (fail open)\n")
        sys.exit(0)
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    try:
        r = subprocess.run(
            [sys.executable, str(core_hook)],
            input=neutral_payload(hook, data), text=True, capture_output=True)
    except Exception as e:
        sys.stderr.write(f"[shim] failed to run {core_hook}: {e} - skipping (fail open)\n")
        sys.exit(0)
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    # Pass through the core hook's own signal: 2 = it chose to block; anything else = continue.
    sys.exit(r.returncode if r.returncode == 2 else 0)


if __name__ == "__main__":
    main()
