---
name: template-update
description: Use when a live instantiated workspace reports an upstream template check or update and local customisations must be preserved
type: skill
---

# Template update (Claude Code adapter)

Use only in a live instantiated workspace with valid origin metadata. Read and follow
[`60_workflows/template-update.md`](../../../60_workflows/template-update.md) exactly.

Run its validation before apply. On provenance or validation failure, stop. Preserve local
differences as `.template-new` for manual review; never force-overwrite them.

Keep procedure in that neutral playbook so every runtime inherits the same safe flow.
