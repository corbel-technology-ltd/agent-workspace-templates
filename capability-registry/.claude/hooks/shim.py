#!/usr/bin/env python3
"""Claude Code adapter shim - the bridge between Claude Code and this registry's neutral core.

`.claude/settings.json` wires the session-start event to `shim.py onboarding-gate`. That hook takes
no payload, so the shim just runs `core/hooks/<name>.py`, passes its stdout/stderr through, and
returns 0 (continue) unless the hook signalled a block with exit 2.

Keep this file thin: wiring only, no policy. Policy lives in core/. See core/RUNTIMES.md.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "core" / "hooks"


def main():
    if len(sys.argv) != 2:
        sys.stderr.write("usage: shim.py <hook-name>\n")
        sys.exit(1)
    core_hook = CORE / f"{sys.argv[1]}.py"
    # Fail OPEN if the core hook is missing: a partial core must never wedge a session.
    if not core_hook.is_file():
        sys.stderr.write(f"[shim] core hook not found: {core_hook} - skipping (fail open)\n")
        sys.exit(0)
    try:
        sys.stdin.read()
    except Exception:
        pass
    try:
        r = subprocess.run([sys.executable, str(core_hook)],
                           input="{}", text=True, capture_output=True)
    except Exception as e:
        sys.stderr.write(f"[shim] failed to run {core_hook}: {e} - skipping (fail open)\n")
        sys.exit(0)
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    sys.exit(r.returncode if r.returncode == 2 else 0)


if __name__ == "__main__":
    main()
