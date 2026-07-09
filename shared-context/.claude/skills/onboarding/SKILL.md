---
name: onboarding
description: Onboard a freshly copied blank shared-context store - run when the .uninitialised sentinel is present, before any other work
type: skill
---

# Onboarding (Claude Code adapter)

This skill is a thin runtime adapter. The playbook it wraps is neutral and lives at
[`core/onboarding/ONBOARDING.md`](../../../core/onboarding/ONBOARDING.md).

Read that file and follow it exactly: staged interview, confirm-before-write, then the
deterministic fill via `python3 core/onboarding/apply.py --root .`.

Do not duplicate playbook content here. If the flow needs to change, change
`core/onboarding/ONBOARDING.md` so every runtime inherits the fix.
