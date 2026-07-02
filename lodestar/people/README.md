---
id: <<store_slug>>.people.readme
name: People - the shared circle
type: reference
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [people, circle, gatekeepers, shared]
related:
  - {ref: SHARED.md, dimension: why, polarity: derived_from}
  - {ref: operating-rules/scope-test.md, dimension: how, polarity: requires}
---

# People

People in the principal's circle that **two or more workspaces deal with** - a partner who
gatekeeps naming decisions, a collaborator both ventures rely on, a key client shared across
lines. One file per person, from [`_person-template.md`](_person-template.md).

Not a contacts database and not biography: capture only **decision-affecting** material - what
this person gates, prefers, or reacts to, with an audit trail of observed reactions so agents can
predict the next one. A person only one workspace deals with stays in that workspace (the
[scope test](../operating-rules/scope-test.md) applies here with full force).

Ships with the template only. People files are personal data: they pass through the
[boundaries](../boundaries/README.md) lens before any copy of this store leaves the principal's
machines, and `tools/scrub-check.py` should carry every listed person's name.

## Related

- [<<STORE_NAME>>](../SHARED.md)
- [Scope test - what earns a place in the store](../operating-rules/scope-test.md)
