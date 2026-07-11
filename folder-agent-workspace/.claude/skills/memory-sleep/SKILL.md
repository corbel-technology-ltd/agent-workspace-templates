---
name: memory-sleep
description: Consolidate unconsolidated journal entries into memory atoms (the sleep pass) - run when the session brief reports a sleep run is due, or when the user asks to consolidate/fold memory
type: skill
---

# Memory sleep (Claude Code adapter)

This skill is a thin runtime adapter. The playbook it wraps is neutral and lives at
[`60_workflows/memory-sleep.md`](../../../60_workflows/memory-sleep.md).

Read that file and follow its "Running the pass" section exactly: `sleep-prep.py`, then
synthesise strict-JSON claims per the contract there, then `sleep-apply.py` (the validator).

Do not duplicate playbook content here. If the flow needs to change, change
`60_workflows/memory-sleep.md` so every runtime inherits the fix.
