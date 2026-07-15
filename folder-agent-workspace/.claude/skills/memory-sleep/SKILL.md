---
name: memory-sleep
description: Use when the session brief says the deep memory-sleep pass is due or the user asks to consolidate unconsolidated journal evidence
type: skill
---

# Memory sleep (Claude Code adapter)

For routine deterministic consolidation use the fast path,
[`60_workflows/memory-reaper.md`](../../../60_workflows/memory-reaper.md), instead.

For the due or requested deep pass, follow the neutral playbook at
[`60_workflows/memory-sleep.md`](../../../60_workflows/memory-sleep.md).

Follow its validation and bounded-synthesis contract exactly. A validator or tool failure stops
the pass before durable writes.

Keep procedure in the neutral playbook so every runtime inherits the same flow.
