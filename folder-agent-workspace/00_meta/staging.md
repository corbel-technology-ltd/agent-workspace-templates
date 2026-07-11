---
id: <<workspace_slug>>.meta.staging
name: Concept staging index
type: state
layer: C1
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [staging, index, roadmap]
---

# Concept staging index

Every concept is one of: **v1-now** (built, runnable by hand today) · **awaits-inputs** (spec
written; activates when its real inputs/customers exist) · **deferred-software** (fenced behind the
value-gate, design-spec §9).

## Instance status

> Set at instantiation. Replace this line with the one-line status of the workspace (what is built,
> what is live, what the current focus is). A mature instance keeps a richer boot pointer here:
> `**Current focus:** ...` and `**Latest handover:** 90_runs/...` lines that the session brief reads.

## v1-now (runnable by hand)

- Doctrine: `principles`, `non-goals`, `autonomy-and-gates`, `memory-homeostasis`, `model-selection`,
  `session-discipline`.
- Memory (v2, four depth layers): `journal/` + `working/` + `short-term/` + `long-term/` +
  `subconscious/`; the fast reaper; `homeostasis.yml` (ACT-R + hysteresis); `memory-architecture.md`;
  `knowledge-gaps`, `source-index`, `memory-index`; the memory-card + event schemas.

- Decision flow: `decision-packet` schema + template, `decision-queue`, `decision-log`.
- Workflows: `daily-brief`, `weekly-review`, `open-loop-tracking`, `email-triage-approve`,
  `memory-reaper`.
- Memory sleep: the bounded prep/synthesis/apply pass and minimal subconscious outputs are current;
  ambitious temporal-KG synthesis remains deferred.

- Registers: `decision-queue`, `decision-log`, `blocked-actions`, `component-registry`,
  `improvement-backlog`, `measurement`. Project loops live per project in `80_projects/`
  (`30_schemas/project.md`); the old `open-loops` register is now a redirect stub.
- Integrations map (`70_integrations/README.md`) - slots to fill per instance.

## awaits-inputs (spec ready; activate on real inputs)

- `evaluation` (memory-sharpness harness) - build the gold set once there is real journal volume.
- `opportunity` schema + worksheet - activates when a real opportunity signal lands.
- `action-intent` template - used when the first genuinely consequential automated action appears.
- `research-signal` template - activates with the first inbound research stream.

## deferred-software (behind the value-gate)

A database 5W1H graph + action_intent/validation tables; an event pipeline + scorer + router; UI
surfaces (brief / decision-queue / memory-search / dashboard); runtime ABAC, dissonance, and
ignorance-graph engines; any service decomposition; the auto-learning loop; full metric
instrumentation; any productisation/multi-user work.

**Value-gate:** promote a workflow to software only after it has run by hand for ≥4 weeks and
consistently costs >20 minutes to assemble, or signal volume crosses a stated threshold. Reuse the
instance's existing infrastructure; one vector store only if ever needed.
