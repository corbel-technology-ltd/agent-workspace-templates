---
id: <<store_slug>>.automations.readme
name: Automations - the shared standing machinery
type: reference
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [automations, cron, monitoring, standing-machinery, shared]
related:
  - {ref: SHARED.md, dimension: why, polarity: derived_from}
  - {ref: tech-stack/README.md, dimension: where, polarity: complements}
  - {ref: operating-rules/scope-test.md, dimension: how, polarity: requires}
---

# Automations

The **shared standing machinery**: every scheduled job, watcher, webhook, or agent-run automation
that keeps running when nobody is looking - and that more than one workspace could collide with.
One file per automation (or per tightly-coupled group), from
[`_automation-template.md`](_automation-template.md).

Why this register earns its place: the classic multi-workspace failure is one agent retiring,
double-scheduling, or silently breaking another agent's automation because nothing recorded that
it existed. An automation catalogued here is discoverable before it is trodden on.

The entry records *that it exists, where it lives, and who owns it* - the runbook detail stays
with the owning workspace or in `tech-stack/`. Changing another workspace's automation goes
through a handoff (ledger entry in `CHANGES.md`), never a direct edit.

## Related

- [<<STORE_NAME>>](../SHARED.md)
- [Tech stack - the shared estate](../tech-stack/README.md)
- [Scope test - what earns a place in the store](../operating-rules/scope-test.md)
