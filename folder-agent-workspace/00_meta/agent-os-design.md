---
id: <<workspace_slug>>.meta.agent-os-design
name: Agent OS design - constitution / reflexes / playbooks / cognition / memory
type: design-spec
layer: C0
status: current
owner: shared
created: <<CREATED_DATE>>
source: design principle (operator) + verified runtime hook reality (per adapter, core/RUNTIMES.md)
tags: [agent-os, hooks, skills, subagents, constitution, instrumentation]
related:
  - {ref: AGENTS.md, dimension: what, polarity: explains}
  - {ref: 10_doctrine/autonomy-and-gates.md, dimension: how, polarity: requires}
  - {ref: 20_memory/README.md, dimension: where, polarity: requires}
---

# Agent OS design

How this workspace becomes intelligent **by instrumenting the environment**, not by lengthening the
prompt. The principle:

> `AGENTS.md` describes **judgment**. Hooks enforce **reflexes**. Skills hold **playbooks**.
> Subagents handle **heavy cognition**. The journal + registers hold **memory/evidence**.

## The mapping

| Principle layer | Lives in | Status |
|---|---|---|
| **Constitution** (judgment) | `AGENTS.md` | exists |
| **Reflexes** (enforce) | `core/hooks/` (logic), wired per runtime by a thin adapter (`core/RUNTIMES.md`) | **installed** (all six: journal-guard, onboarding-gate, session-brief, session-digest, reaper, registry-drift) |
| **Playbooks** | `core/` (e.g. `core/onboarding/`), surfaced per runtime as skills/commands; the `60_workflows/` specs graduate here when invoked often | onboarding shipped; others graduate on use |
| **Heavy cognition** | the runtime's subagent surface (adapter-specific) | deferred (no input/consumer yet) |
| **Memory / evidence** | `20_memory/journal/` (events) + `50_registers/` (observations, decisions, backlog, metrics) | **exists - reuse, do not rebuild** |

The key fit: **hooks are the sensory organs that append to the immutable journal.** The reaper folds
the journal; the subconscious spots trends. There is no parallel `ops/metrics/` tree - that collapses
into reuse of the journal + registers. No new evidence tree.

## Verified hook reality (per runtime)

Hook capability differs per runtime: which lifecycle events exist, which can block, and what the
context cost is. That detail is adapter-specific, so it lives with the adapters - the verified
event list, block semantics, and configuration surface for each wired runtime are documented in
[`core/RUNTIMES.md`](../core/RUNTIMES.md). Two rules travel with every runtime:

- **The neutral contract is fixed.** Core hooks read a documented JSON payload on stdin and signal
  "block" with exit 2 (`core/hooks/README.md`); the adapter maps that onto whatever its runtime
  offers. A runtime with no hooks degrades to the documented manual protocol plus the git-level
  journal guard.
- **Verify before relying.** Hook surfaces drift across runtime versions, and even a verifier can
  hallucinate events - re-check the live binary's event names before wiring anything new.

## Hook discipline (the rule that keeps this from re-bloating)

- **Silent by default.** Write to the journal/registers; return `additionalContext` only when it
  changes the current decision.

- **Block only the unsafe**, with **narrow matchers** (not a blanket BLOCK on whole tool classes -
  that is chatty and obstructive).

- **No write-only dead logs** - wire a consumer in the same step, or don't write.
- **Notify only when a human is needed.**

## Prioritisation (prose hierarchy, not a formula)

Proactivity without prioritisation is noise. Rank by, in order: **blocking** (unblocks the founder or
a commitment) → **strategic** (advances the locked direction) → **opportunistic** (nice-to-have).
Within that, gate each surfaced improvement: **do-now** (clearly high-impact + low-risk + reversible)
· **suggest** (worth a Decision Packet) · **log** (to the backlog) · **ignore**. No multiplicative
score with inputs we don't yet measure - that reads precise and gets hand-waved. Promote to a real
score only when the inputs (confidence, recurrence, cost-to-delay) are actually tracked.

## What stays in `AGENTS.md` vs moves out

- **Stays (judgment):** mission, the one vocabulary, hard invariants, the gate's *intent*, the
  operating loop, the prioritisation hierarchy, the sensor doctrine, the OS map, definition of done.

- **Moves out (enforcement/inventory):** the gate's *enforcement* → a `PreToolUse` hook; long
  playbooks → skills; heavy audits → subagents; events/metrics → the journal + registers.

- **Placement test:** additions to always-loaded text must pass the
  [delta rule](../10_doctrine/context-decomposition.md#always-loaded-delta); explanatory detail
  stays in indexed documentation.

## Load policy

The staged build status and the emergent-intelligence learning-system detail are situational, not
needed every time this design is consulted, so they live in a concept folder rather than forcing
every reader through the full roadmap and the speculative refinements. Map:
[`00-INDEX.md`](agent-os-design/00-INDEX.md).

| File | Contains | Load when |
| --- | --- | --- |
| `agent-os-design/01-staged-plan.md` | what's built (NOW), what awaits an input (AWAIT-NEED), what's deliberately deferred (DEFER) | checking hook build status, or deciding what to build/wire next |
| `agent-os-design/02-emergent-intelligence.md` | observation budget, anti-superstition feedback, nudge limits, the promotion ladder | working on the subconscious/learning system or `homeostasis.yml` |

## Related

- [<<WORKSPACE_NAME>>](../AGENTS.md)
- [Autonomy & gates - the single decision gate](../10_doctrine/autonomy-and-gates.md)
- [Memory structure - the model](../20_memory/README.md)
