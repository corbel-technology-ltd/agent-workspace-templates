---
id: <<workspace_slug>>.doctrine.model
name: Doctrine - the standing judgment rules
type: reference
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [doctrine, judgment, principles, gates, model-selection, session-discipline]
related:
  - {ref: AGENTS.md, dimension: why, polarity: derived_from}
  - {ref: 10_doctrine/principles.md, dimension: what, polarity: explains}
  - {ref: 10_doctrine/autonomy-and-gates.md, dimension: how, polarity: explains}
  - {ref: 10_doctrine/non-goals.md, dimension: why, polarity: explains}
---

# Doctrine

The agent's **standing doctrine**: the judgment rules that hold across every task and do not change
per job. Reflexes live in hooks, playbooks in skills, heavy cognition in subagents - but *judgment*
lives here, as the long-form text behind the one-paragraph summaries in
[`../AGENTS.md`](../AGENTS.md). This is C3 reference: stable, slow-moving, read for orientation, not
regenerated as the workspace runs.

## How it is used (the contract)

`AGENTS.md` names each rule in a single line and points here for the full statement; this folder is
the **authority** that line defers to. The doctrine is **read, not run**: it shapes how the agent
decides, gates, and routes, but nothing executes it directly. Two hard constraints follow from its
C3 status (see `AGENTS.md` non-negotiable rules 4 and 8): the agent does **not** silently rewrite
doctrine - changes are proposed as diffs for review; and the **spine is designed up front** while
leaves grow on demand, so these files are deliberately complete, not stubs. When principles conflict,
**hard invariants outrank soft defaults** ([`principles.md`](principles.md) precedence rule).

## What lives here

- [`principles.md`](principles.md) - the **one vocabulary**: every canonical principle stated once
  (AI-minimisation/60-20-20, source-or-abstain, signpost-don't-advise, autonomy-by-reversibility,
  verify-live-state, and the rest), plus the task→method table and the hard-vs-soft precedence rule.

- [`autonomy-and-gates.md`](autonomy-and-gates.md) - the **single decision gate**: the autonomy
  default table, the qualitative risk tiers, the always-escalate list, and the two action-preflight
  rules. One gate for "may the agent act unattended, or does it need a yes?".

- [`model-selection.md`](model-selection.md) - *which* model once `principles.md` has decided to use
  one at all: the four scoring axes, the complexity×volume routing table, the two overrides, and
  worked examples. Reach for the cheapest model that clears the bar.

- [`session-discipline.md`](session-discipline.md) - operating long agent sessions: the context
  budget, the degradation symptoms, and the handover/resume contract. `escalate-with-context`
  applied to the agent's own limits.

- [`memory-homeostasis.md`](memory-homeostasis.md) - the ten principles that keep the memory store
  from bloating, the reaper contract, and what is kept deliberately crude. The doctrine behind the
  memory model in [`../20_memory/README.md`](../20_memory/README.md).

- [`non-goals.md`](non-goals.md) - the hard rails: what the system must **not** do (auto-send,
  auto-publish, auto-pay, auto-sign, replace founder judgment, swamp memory). Preparation is
  automated; authority stays gated.

## Where it fits

Doctrine is the **why** behind the gate. The gate's enforcement is partly reflex (hooks in
`core/hooks/`, wired per runtime) and partly self-applied via the schemas - `30_schemas/action-intent.md` and
`30_schemas/decision-packet.md` are the surfaces that put these rules into practice on a real action.
The full OS map and routing live in [`../AGENTS.md`](../AGENTS.md).

## Related

- [<<WORKSPACE_NAME>>](../AGENTS.md)
- [Operating principles - the one vocabulary](principles.md)
- [Autonomy & gates - the single decision gate](autonomy-and-gates.md)
- [Non-goals - the safety rails](non-goals.md)
