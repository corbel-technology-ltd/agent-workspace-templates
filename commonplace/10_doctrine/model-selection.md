---
id: <<workspace_slug>>.doctrine.model-selection
name: Model selection — which model, once you have decided to use one
type: doctrine
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [doctrine, model-selection, cost, routing, ai-minimisation]
related:
  - {ref: 10_doctrine/principles.md, dimension: why, polarity: derived_from}
  - {ref: 10_doctrine/autonomy-and-gates.md, dimension: how, polarity: requires}
---

# Model selection

The second axis under **AI-minimisation**. `principles.md` decides *whether* to reach for an LLM at
all (deterministic plumbing first). This decides *which* model once you have. Defaulting to the
mid-tier is sometimes wasteful; defaulting to the top tier usually is; defaulting to the cheapest
silently degrades quality on tasks that need reasoning. Score the task, then route. Reach for the
cheapest model that clears the bar.

## Four axes (score 1-5 each)

- **Difficulty** — 1 trivial extraction · 2 closed-taxonomy classification · 3 open
  classification/paraphrase under constraint · 4 judgement under partial information · 5 novel
  synthesis under genuine uncertainty.
- **Reasoning depth** — 1 single-step · 2 a few premises · 3 multi-factor weighing · 4 multi-step
  chain · 5 iterative self-critique/revise.
- **Quality required** — 1 mediocre is fine · 3 errors caught downstream · 4 load-bearing, errors
  hurt trust · 5 mistake is catastrophic/irreversible/expensive.
- **Volume (cost sensitivity)** — 1 one-off · 2 weekly · 3 daily · 4 hourly · 5 per-event/bursty.
  Higher volume biases toward cheaper models.

## Routing

`complexity = difficulty + reasoning_depth + quality` (range 3-15). Volume class: LOW (1-3),
MEDIUM (4), HIGH (5). Map to the cheapest / mid / top tier available in the model family you use.

| Complexity | LOW vol | MEDIUM vol | HIGH vol |
|---|---|---|---|
| **3-6** simple | cheap | cheap | cheap |
| **7-9** moderate | mid | mid | cheap |
| **10-12** complex | top | mid | mid |
| **13-15** deep | top | top | mid |

## Two overrides

- **A — irreversible escalation.** If `quality_required = 5` and the action is irreversible (sent
  email, public commit, money, a real calendar invite), bump one tier (cheap → mid → top; top
  stays). This is `autonomy-by-reversibility` applied to model choice.
- **B — cost ceiling.** If `volume = 5` and `complexity ≤ 9`, stay on the cheap tier regardless. If
  you genuinely need the mid tier at that volume, redesign the task (cache, batch, pre-filter) first.

## Worked examples

| Task | D | R | Q | V | Tier |
|---|---|---|---|---|---|
| Voice/format check (regex) | — | — | — | — | **No LLM** (deterministic first) |
| Daily-brief aggregation | 1 | 1 | 2 | 3 | **cheap** |
| Email/signal classification | 2 | 1 | 3 | 5 | **cheap** (override B) |
| Reaper candidate judgement | 3 | 3 | 3 | 3 | **mid** |
| Weekly-review synthesis | 4 | 4 | 4 | 2 | **top** |
| Decision-packet drafting | 4 | 4 | 5 | 1 | **top** |

## Cost ordering (indicative — verify before quoting)

Tiers differ by roughly an order of magnitude on output tokens (cheap ≪ mid ≪ top). Exact figures
drift; treat as ordering, not fact, and check current pricing before any cost claim
(source-or-abstain). On a subscription plan the binding constraint is often quota throughput, not
dollars.

## Revisit when

A task's cost overshoots projection by 50%+ (reclassify volume, drop a tier); outputs are
consistently weaker than expected (reclassify quality, raise a tier); a new task type doesn't fit
(score it, add a row).

## Related

- [Operating principles — the one vocabulary](principles.md)
- [Autonomy & gates — the single decision gate](autonomy-and-gates.md)
