---
id: <<store_slug>>.places.readme
name: Places - shared locations and venues
type: reference
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [places, locations, context, shared]
related:
  - {ref: SHARED.md, dimension: why, polarity: derived_from}
  - {ref: operating-rules/scope-test.md, dimension: how, polarity: requires}
---

# Places

The **shared location context**: the physical and logical places more than one workspace needs to
reason about - the home/office and what lives where, recurring venues, storage sites, "the garage
holds X", travel bases. One file per place, from [`_place-template.md`](_place-template.md).

A place earns a file here only when it passes the scope test (two or more workspaces care).
A place only one workspace cares about stays in that workspace's own canon.

Addresses and anything a stranger could misuse belong behind the boundaries line: name the place,
alias the address (`boundaries/boundaries.md` + `tools/scrub-terms.txt`).

## Related

- [<<STORE_NAME>>](../SHARED.md)
- [Scope test - what earns a place in the store](../operating-rules/scope-test.md)
