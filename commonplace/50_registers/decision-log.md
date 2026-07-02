---
id: <<workspace_slug>>.register.decision-log
name: Decision log (append-only)
type: register
layer: C1
status: current
owner: shared
created: <<CREATED_DATE>>
staging: v1-now
tags: [register, decisions, audit-trail, autonomy-by-reversibility, capture-back]
related:
  - {ref: 50_registers/decision-queue.md, dimension: what, polarity: derived_from}
  - {ref: 30_schemas/decision-packet.md, dimension: how, polarity: explains}
  - {ref: 60_workflows/daily-brief.md, dimension: how, polarity: enables}
  - {ref: 20_memory/journal/README.md, dimension: why, polarity: requires}
---

# Decision log

The audit trail of founder judgement. Every decision **made** lands here as one row: what was
decided, why, how reversible it was, and which memory atom captured the lesson. This is where the
[`decision-queue`](decision-queue.md) ends up once an item is approved, rejected, or otherwise
resolved.

Both approvals and rejections are recorded. **Rejections are not waste**: a rejected packet is a
preference made explicit, and the `memory_update` it produces sharpens future routing so the same
non-fit is filtered earlier (`capture-back`). A pattern of rejections is itself a signal the
weekly review reads.

## Rules

- **Append-only.** Like the [`journal/`](../20_memory/journal/README.md), rows are never edited or
  deleted. A reversal of a past decision is a NEW row that names the one it overturns in
  `rationale`; the original stays as the record of what was believed at the time. Git history is
  the tamper-evidence.

- **One row per resolved decision.** Most rows come from a [Decision Packet](../30_schemas/decision-packet.md)
  reaching `approve` or `reject` in the queue. Trivial reversible calls made in the normal course
  of work do not need a row; this register is for decisions a founder weighed.

- **`memory_update` is mandatory and load-bearing.** Capture-back is not optional: every row names
  the atom (usually `long-term/` for a preference or rule, a `procedural` tag for a way-of-working)
  that the decision wrote or amended. If a decision produced no durable learning, write `none`
  and say so in `rationale` rather than leaving it blank.

- **`reversibility` drives nothing retroactively but explains everything.** It records the gate
  tier the decision sat at under `autonomy-by-reversibility`: `reversible` (the action could be
  undone cheaply), `costly` (undoable but with real cost or delay), or `irreversible` (an external
  send, payment, signature, or publish). Irreversible decisions should always trace to an explicit
  founder approval.

- **`rationale` is one line.** The full reasoning lives in the source Decision Packet in
  `90_runs/`; link to it. The log is the index, not the essay.

- **`source` cites the packet or journal entry.** `source-or-abstain` applies: a decision resting
  on a factual claim links the evidence; a judgement call says so plainly.

## Columns

| field | meaning |
|---|---|
| `id` | `D-NNNN`, monotonic, never reused |
| `date` | `YYYY-MM-DD` the decision was made |
| `decision` | what was decided, in the founder's terms (approved / rejected / chose X over Y) |
| `rationale` | one line: why; for a reversal, names the row it overturns |
| `reversibility` | `reversible` \| `costly` \| `irreversible` |
| `memory_update` | atom written or amended (e.g. `long-term/<slug>.md`), or `none` |
| `source` | link to the Decision Packet in `90_runs/` or a `journal/` entry |

## Log

<!-- APPEND new rows below this line. Never edit a row above it. -->

| id | date | decision | rationale | reversibility | memory_update | source |
|---|---|---|---|---|---|---|
| (none yet) | | | | | | |

## Related

- [Decision queue — open founder decisions](decision-queue.md)
- [Decision Packet schema](../30_schemas/decision-packet.md)
- [Daily brief — the run-by-hand morning assembly](../60_workflows/daily-brief.md)
- [Journal — the append-only event log](../20_memory/journal/README.md)
