---
id: <<workspace_slug>>.meta.readme
name: Meta — how the workspace explains and governs itself
type: reference
layer: C0
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [meta, governance, design-spec, staging, agent-os, self-description]
related:
  - {ref: AGENTS.md, dimension: what, polarity: explains}
  - {ref: 00_meta/design-spec.md, dimension: why, polarity: derived_from}
  - {ref: 00_meta/agent-os-design.md, dimension: how, polarity: explains}
  - {ref: 00_meta/staging.md, dimension: where, polarity: requires}
---

# Meta

The workspace's **self-description and governance**: the founding blueprint, the agent-OS design, the
memory architecture, and the staging/current-state. Where the system explains *why* it is shaped this
way and *how* it governs its own change. C0 reference, alongside the root manifest
[`../AGENTS.md`](../AGENTS.md) — `AGENTS.md` holds the live judgment; this folder holds the design
behind it.

## How it is used (the contract)

These are **C3-style reference** docs (would they still be true tomorrow? yes): the spine is designed
here up front, not accreted by need. Read order at boot is set by `AGENTS.md` — it points sessions at
[`staging.md`](staging.md) (the `Now / In flight` block) before routing. The rest is loaded only when
a decision needs the reasoning behind a structural choice.

Two are **append-only / load-bearing for governance**: [`log.md`](log.md) records every structural
change (newest first), and [`staging.md`](staging.md) is the current-state index. The design specs
(`design-spec`, `agent-os-design`, `memory-architecture`) are **not silently rewritten** — per
`AGENTS.md` rule 4, a change to C0/C3 reference is proposed as a diff, confirmed, then logged here.
Generic OS improvements made in an instance flow **upstream** to the template (the upstreaming rule in
the root manifest and the template `README.md`).

## What lives here

- [`design-spec.md`](design-spec.md) — the **founding blueprint**: what this workspace is (a
  deterministic founder control plane, not an autonomous AI CEO), the locked decisions, the one
  vocabulary, the C0-C4 structure, the staging tiers, the file inventory, and the deferred-software
  value-gate. The authoritative PRD.

- [`agent-os-design.md`](agent-os-design.md) — **how the workspace becomes intelligent by
  instrumenting the environment**, not by lengthening the prompt: judgment in `AGENTS.md`, reflexes in
  `core/hooks/`, playbooks in `core/` (surfaced per runtime), heavy cognition in subagents, evidence
  in the journal + registers. Holds the hook-discipline rules and the staged now/await-need/defer
  plan; the per-runtime verified hook reality lives with the adapters in `core/RUNTIMES.md`.

- [`memory-architecture.md`](memory-architecture.md) — the **canonical, research-backed memory
  design** (C3): one immutable truth (`journal/`) projected into four depth layers that get sharper as
  they get deeper, with ACT-R activation, hysteresis, the reaper + sleep passes, and the deferred
  graduation path. The operator's view is [`../20_memory/README.md`](../20_memory/README.md).

- [`staging.md`](staging.md) — the **concept staging index** + instance status: every concept tagged
  **v1-now** / **awaits-inputs** / **deferred-software**. The boot pointer for current focus.

- [`log.md`](log.md) — the **append-only workspace change log**: one dated section per change set
  (doctrine edits, schema/workflow additions, hook installs, migrations), newest at the top.

- [`always-on-executor-spec.md`](always-on-executor-spec.md) — *placeholder / optional.* The design
  shape and hardening checklist for a headless executor that runs jobs and **raises** prepared
  decisions; wired (when built) through [`../70_integrations/README.md`](../70_integrations/README.md).

- [`migration-map.md`](migration-map.md) — *placeholder.* A slot for an instance's plan to absorb a
  prior workspace as a curated fresh start. A fresh instance can leave it blank or delete it.

A blank template carries `<<TOKEN>>` onboarding placeholders (the nine names - `WORKSPACE_NAME`,
`OWNER`, `AGENT_NAME`, `CREATED_DATE`, and so on - each appearing on disk in angle brackets);
onboarding fills them deterministically via the playbook at `core/onboarding/ONBOARDING.md`
(`apply.py` + `placeholders.yml`). Runtime `{{...}}` tokens like `{{YYYY-MM-DD}}` are filled per
artefact when it is created and stay. The manual fallback: search the tree for `<<` and fill each
token per the table in the template `README.md`.

## Related

- [<<WORKSPACE_NAME>>](../AGENTS.md)
- [Workspace — founding design spec (founder control plane)](design-spec.md)
- [Agent OS design — constitution / reflexes / playbooks / cognition / memory](agent-os-design.md)
- [Concept staging index](staging.md)
