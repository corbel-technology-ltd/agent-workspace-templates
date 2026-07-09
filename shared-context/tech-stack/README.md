---
id: <<store_slug>>.tech-stack.readme
name: Tech stack - the shared estate
type: reference
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [tech-stack, estate, machines, software, shared]
related:
  - {ref: SHARED.md, dimension: why, polarity: derived_from}
  - {ref: operating-rules/scope-test.md, dimension: how, polarity: requires}
---

# Tech stack

The **shared machine and software estate**: the hosts, services, and tools that more than one
workspace operates on or around. One file per fact-cluster, from
[`_entry-template.md`](_entry-template.md) - a server topology, a service inventory, a "this tool
is available everywhere" note, a runbook both agents may need.

The [scope test](../operating-rules/scope-test.md) is the gate: only what two or more workspaces
independently need. Workspace-specific infrastructure stays in that workspace's
`70_integrations/` (or equivalent). **Never credentials** - an entry says a service exists and
where its runbook lives, never how to authenticate to it; secrets stay in each workspace's
untracked `.env`.

Ships with the template only; entries accrue through governance. Hostnames and internal service
names are exactly the kind of term the [boundaries](../boundaries/README.md) never-share list and
`tools/scrub-terms.txt` exist for.

## Related

- [<<STORE_NAME>>](../SHARED.md)
- [Scope test - what earns a place in the store](../operating-rules/scope-test.md)
