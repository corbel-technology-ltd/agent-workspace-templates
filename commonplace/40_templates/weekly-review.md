---
id: <<workspace_slug>>.template.weekly-review
name: Weekly review template
type: template
layer: C2
status: current
owner: shared
created: <<CREATED_DATE>>
staging: v1-now
tags: [template, weekly-review, registers, runs, anti-noise-batching, capture-back]
related:
  - {ref: 60_workflows/weekly-review.md, dimension: how, polarity: explains}
  - {ref: 50_registers/decision-log.md, dimension: what, polarity: derived_from}
  - {ref: 80_projects/index.md, dimension: what, polarity: derived_from}
  - {ref: 50_registers/decision-queue.md, dimension: what, polarity: derived_from}
  - {ref: 60_workflows/memory-reaper.md, dimension: how, polarity: requires}
---

# Weekly review template

Copy this file to `90_runs/YYYY-Www-review.md` and fill it in. Run it by hand over the week's
run folders (`90_runs/`) and the registers (`50_registers/`); the procedure is
[`../60_workflows/weekly-review.md`](../60_workflows/weekly-review.md). This is the
**anti-noise batching** endpoint: the non-urgent that accumulated over the week is reviewed here,
once, instead of interrupting the days. Anything durable that surfaces is written back as a
journal entry so the reaper can capture it (**capture-back**).

Rules for filling this in:

- **source-or-abstain.** Every line points at where it came from: a run file, a register row, or a
  journal entry. If a claim has no source, write "no source" rather than guessing.

- **signpost, don't advise.** Sections surface state and options; decisions belong in the decision
  queue and log, not invented here.

- Leave a section's body empty and write "none this week" rather than padding it.

---
title: Weekly review YYYY-Www
week_of: YYYY-MM-DD            # Monday of the week under review
reviewed_on: YYYY-MM-DD
reviewer: shared
sources_scanned: [90_runs/, 50_registers/decision-log.md, 80_projects/, 50_registers/decision-queue.md, 20_memory/_meta/build.md]
---

## 1. What shipped

What actually moved this week. One line each, with the source.

| What | Where it landed | Source |
|---|---|---|
|  |  | `90_runs/...` |

## 2. Decisions made

Pulled from [`../50_registers/decision-log.md`](../50_registers/decision-log.md) (append-only) for
this week only. Do not re-litigate; record what was decided and the reversibility tier, so the
weekly view stays honest about how much was irreversible.

| Date | Decision | Reversibility | Source |
|---|---|---|---|
| YYYY-MM-DD |  | reversible / one-way | `decision-log.md#...` |

Still open in [`../50_registers/decision-queue.md`](../50_registers/decision-queue.md) (carried, not
decided): list ids only; the queue is the live truth.

## 3. Open loops still open

From the `## Open` table of each [`../80_projects/`](../80_projects/index.md) `loops.md` (incl.
`_general/`). Only loops still open at review time. Flag any that have been open longer than expected.

| Loop | Ball | Opened | Ageing? | Source |
|---|---|---|---|---|
|  | mine / theirs / external | YYYY-MM-DD | yes/no | `80_projects/<slug>/loops.md#...` |

## 4. Drift and staleness flags

Where the workspace and reality have diverged. Sources of drift to scan: atoms past
`last_verified + valid_for`, doctrine or schemas that a week's events have contradicted, registers
that disagree with run folders, and the memory budgets in `_meta/build.md`.

- **Stale atoms** (`status: stale` or expired validity): list refs, or "none".
- **Contradicted reference (C3):** propose a diff for review per the gate; do not silently rewrite.
- **Register / run mismatch:** what disagrees and which is right.

## 5. Memory reaper run note

Did the reaper run this week, and what did it do. Read from `20_memory/_meta/build.md` (regenerated
locally by the reaper, gitignored - absent until the first run; the spec is
[`../60_workflows/memory-reaper.md`](../60_workflows/memory-reaper.md)). If it did not run, say so and
note whether it should next week.

- **Ran:** yes / no (`--as-of` date used: YYYY-MM-DD)
- **Counts:** promoted / merged / demoted / quarantined / archived (from `build.md`)
- **Churn abort?** yes/no. If yes, link the review file it wrote.
- **Capture-back this week:** journal entries minted from this review (refs), or "none".

## 6. Next-week priorities

The signpost into next week. Three to five items, ranked. Each is either an existing open loop, a
queued decision, or a new journal-backed intent; nothing here is a fresh commitment made up in the
review.

1.
2.
3.

## Related

- [Weekly review — the once-a-week scan, reap, and re-prioritise](../60_workflows/weekly-review.md)
- [Decision log (append-only)](../50_registers/decision-log.md)
- [Active projects](../80_projects/index.md)
- [Decision queue — open founder decisions](../50_registers/decision-queue.md)
- [Memory reaper — the fast consolidation pass](../60_workflows/memory-reaper.md)
