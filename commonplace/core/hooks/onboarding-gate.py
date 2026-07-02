#!/usr/bin/env python3
"""Session-start gate: block work on an uninitialised workspace until onboarding runs.

If the workspace-root `.uninitialised` sentinel is present, this freshly copied template has not
been onboarded yet: print a clear instruction that the agent must run the onboarding playbook
before ANY other work, then exit. If the sentinel is absent, the workspace is already initialised -
exit 0 silently.

This hook runs BEFORE onboarding fills the `<<TOKEN>>` placeholders, so it must carry no fill tokens
and depend on nothing but the standard library. The workspace root is inferred from this file's
location (repo root = two levels up from core/hooks/); the sentinel lives at the root.

Neutral hook contract (see core/RUNTIMES.md): stdlib only; reads (and ignores) any JSON on stdin;
prints the instruction on stdout for the runtime adapter to inject at session start.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SENTINEL = ROOT / ".uninitialised"


def main():
    # Consume the SessionStart payload on stdin; its contents are not needed here.
    try:
        json.load(sys.stdin)
    except Exception:
        pass

    if not SENTINEL.exists():
        # Already onboarded — say nothing.
        sys.exit(0)

    print(
        "[onboarding-gate] This workspace is UNINITIALISED (a .uninitialised sentinel is present "
        "at the workspace root).\n"
        "Before ANY other work, run the onboarding playbook "
        "(core/onboarding/ONBOARDING.md): it gathers the instance values, confirms them, then "
        "fills the <<TOKEN>> placeholders deterministically via apply.py and removes the sentinel.\n"
        "Do not edit placeholders by hand and do not start other tasks until onboarding completes."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
