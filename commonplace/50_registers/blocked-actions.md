---
id: <<workspace_slug>>.register.blocked-actions
name: Blocked actions register
type: register
layer: C1
status: current
owner: shared
created: <<CREATED_DATE>>
staging: v1-now
tags: [register, autonomy, gate, safety, audit]
related:
  - {ref: 10_doctrine/autonomy-and-gates.md, dimension: why, polarity: derived_from}
  - {ref: 50_registers/decision-log.md, dimension: what, polarity: supports}
  - {ref: 30_schemas/event.md, dimension: how, polarity: explains}
---

# Blocked actions register

The audit trail of every action the gate **stopped**, and why. It makes the safety rail visible:
proof that **autonomy-by-reversibility** is enforced, not just stated, and a record of where the
agent reached for authority it does not have.

A block is not a failure. It is the gate working. Each row is one moment where the proposed action
crossed a tier in [`autonomy-and-gates.md`](../10_doctrine/autonomy-and-gates.md) that required a
human, hit a hard invariant, or asked for permission the agent cannot grant itself.

## When to add a row

Append a row whenever an intended action is refused at the gate. The blocking cases, in
precedence order:

1. **Hard invariant** (always outranks any soft default):
   - external send / publish / pay / sign without explicit founder approval
   - delete or overwrite a `journal/` entry (immutable; a retraction is a NEW entry)
   - the agent attempting to upgrade its own permissions
   - a statutory/legal/factual claim with no primary source (**source-or-abstain**)
2. **Confirm tier reached but not granted** — editing C3 doctrine/schemas/`AGENTS.md`, running a
   tool from outside the workspace, a git commit or push, where confirmation was withheld or not
   yet given.

3. **Escalated as ambiguous** — the action's reversibility could not be assessed, so it was held
   for the founder (**escalate-with-context**) rather than guessed.

Logging is itself the cheap, reversible side: record the block, do not perform the action.

## How to use this register (v1-now, by hand)

1. The block happens at the gate during **Plan → Validate → Execute** (validate fails).
2. Append one row to the table below. Keep the proposed action factual, not editorialised.
3. Name the exact rule from `autonomy-and-gates.md` in `Gate rule`.
4. Set `Resolution` to `pending` until the founder rules; then update it in place (this is a live
   working register, C1, not the immutable log).

5. If the block produced a durable lesson (a recurring near-miss, a preference the founder states
   when resolving it), record it via [`event.md`](../30_schemas/event.md) into `journal/` so the
   reaper can mint a **normative** atom. The register row stays; the durable truth lives in the
   journal.

## Status vocabulary

- `pending` — awaiting the founder's decision.
- `approved-then-executed` — founder authorised; the action was carried out, with the approval
  recorded.

- `rejected` — founder declined; the action will not be taken.
- `revised` — a safer, more reversible variant was substituted and proceeded.
- `withdrawn` — the agent abandoned the action; no founder decision needed.

## Register

| Date | Proposed action | Gate rule triggered | Resolution |
|---|---|---|---|
| (none yet) | | | |

No blocks recorded yet. The empty table is the expected state on a quiet day; rows accrue as the
gate does its work.

## Notes

- This register is **not** authority. It is evidence that authority stayed with the founder. A row
  here never licenses the action it describes; only an explicit founder approval, recorded against
  that row, does.

- Counterpart records: approved consequential decisions land in
  [`decision-log.md`](decision-log.md); open items awaiting a ruling sit in the decision queue and
  surface in the daily brief.

## Related

- [Autonomy & gates — the single decision gate](../10_doctrine/autonomy-and-gates.md)
- [Decision log (append-only)](decision-log.md)
- [Journal event schema](../30_schemas/event.md)
