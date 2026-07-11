---
id: <<workspace_slug>>.workflows.index
name: Workflows - the operating playbooks
type: reference
layer: C2
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [workflows, playbooks, procedures, run-by-hand, plan-validate-execute, graduation]
related:
  - {ref: AGENTS.md, dimension: why, polarity: derived_from}
  - {ref: 60_workflows/default.md, dimension: what, polarity: explains}
  - {ref: 30_schemas/decision-packet.md, dimension: what, polarity: requires}
  - {ref: 40_templates/daily-brief.md, dimension: what, polarity: requires}
  - {ref: 70_integrations/README.md, dimension: where, polarity: requires}
---

# Workflows - the operating playbooks

The repeatable, multi-step routines the workspace runs by hand: the named procedures the
[Routing map](../AGENTS.md#routing-map) points at. Each file is **one contract** - what it is for,
when to use it, the ordered steps, the gates it respects, and the artefact it produces. They are C2
contracts (see the [context layers](../AGENTS.md#context-layers)): stable, reviewed, and cited, not
working notes.

## The contract

A workflow is **run by hand** - the agent executes the steps, the founder settles anything gated.
None of them is a cron job or a service; promotion to software is fenced behind the value-gate
(design-spec §9) and only fires once a pass has run by hand long enough to earn it. Until then a
workflow is a written procedure, deterministic-first: an LLM enters only to summarise, draft, or
judge genuine ambiguity, never to decide urgency, approve, or send (**AI-minimisation**;
**signpost, don't advise**). Side-effecting routines follow **Plan → Validate → Execute** and stop
at the safety gate; the [hard invariants](../AGENTS.md#non-negotiable-rules) hold throughout. When
the same pattern repeats often enough, a workflow **graduates** to a playbook in `core/`, surfaced
per runtime as a skill (see [the OS map](../AGENTS.md#the-os-map)); these specs are the source it
graduates from.

## What lives here

- [`default.md`](default.md) - the fallback. The irreducible six-stage skeleton (discover → route →
  load → execute → verify → closeout) for any task no specialised workflow covers. Its expansion
  rule is what tells you when to propose a new workflow rather than extend it inline.
- [`daily-brief.md`](daily-brief.md) - the morning assembly. Gathers open decisions, due loops, and
  parked email drafts into `90_runs/<as-of>-brief.md`; the single thing that competes for the
  founder's attention (**anti-noise batching**).
- [`weekly-review.md`](weekly-review.md) - the once-a-week scan, reconcile, reap, and
  re-prioritise over the week's run folders and the registers; runs the reaper as a step and emits
  `90_runs/YYYY-Www-review.md`.
- [`open-loop-tracking.md`](open-loop-tracking.md) - opens, surfaces, and closes the open
  commitments in each project's `loops.md` (**capture-back** for promises, **anti-noise batching**
  for the chase).
- [`email-triage-approve.md`](email-triage-approve.md) - a thin wrapper over the instance's email
  loop (poller + sender, wired in [`../70_integrations/README.md`](../70_integrations/README.md)).
  Reads, classifies, drafts; every outbound reply routes through a
  [Decision Packet](../30_schemas/decision-packet.md). **Hard
  invariant:** no external send without explicit founder approval.
- [`memory-reaper.md`](memory-reaper.md) - the fast, fully deterministic consolidation pass. Folds
  the journal into the depth-layer projections and keeps activation and membership correct; no LLM.
- [`memory-sleep.md`](memory-sleep.md) - the deep, bounded-LLM synthesis pass (schema abstraction,
  subconscious world-model, trend detection). `awaits-inputs`: the reaper suffices until there is
  real journal volume to synthesise.
- [`template-update.md`](template-update.md) - the non-clobbering check, inspect, apply, merge, and
  accept flow for bringing template-managed spine changes into a live instance.

## How they connect

The [Routing map](../AGENTS.md#routing-map) is the entry point: a task type names the workflow to
load. From there they compose - the daily brief drives the open-loop sweep and reads the parked
email drafts; the weekly review runs the reaper and feeds capture-back into the journal. Each
workflow names its own schema ([`../30_schemas/`](../30_schemas/)) and template
([`../40_templates/`](../40_templates/)) where it needs one, and writes its working output to
[`../90_runs/`](../90_runs/). Read the file before running it; the routing row only points the way.

## Related

- [<<WORKSPACE_NAME>>](../AGENTS.md)
- [Default workflow](default.md)
- [Decision Packet schema](../30_schemas/decision-packet.md)
- [Daily founder brief - fill-in template](../40_templates/daily-brief.md)
- [Integrations - what-runs-where map (instance-specific slots)](../70_integrations/README.md)
