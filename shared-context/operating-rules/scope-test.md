---
id: <<store_slug>>.operating-rules.scope-test
name: Scope test - what earns a place in the store
type: doctrine
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [scope, anti-dumping, mutual-benefit, file-cap, doctrine]
related:
  - {ref: operating-rules/README.md, dimension: where, polarity: derived_from}
  - {ref: _meta/governance.md, dimension: how, polarity: complements}
---

# The scope test

A shared store fails by **dumping**: content lands here because "shared" sounds safer than
deciding where it belongs, and the store becomes a second attic no agent can load lean. Every
addition passes four questions, all four:

1. **Mutual benefit** - would at least two plugged-in workspaces *independently* need this? Not
   "might be handy"; each would have had to write its own copy otherwise.
2. **Rules or identity, not knowledge** - is this about the principal, the agents' behaviour, or
   the shared estate? Domain and project knowledge stays in its workspace however shared-sounding
   it is.
3. **Durable** - will it still be true next quarter? Live state belongs in `_coordination/` or in
   a workspace register, not in a content file.
4. **Publishable in shape** - could this file's *structure* ship in a template? If the content is
   inseparable from a secret or a never-share boundary item, it belongs behind the boundary, not
   in prose here.

Fail any -> it stays workspace-local (a workspace can always link to another workspace's file for
awareness without promoting it). Pass all four -> propose it through
[`_meta/governance.md`](../_meta/governance.md), inside the file cap.

## Related

- [Operating rules - how agents behave, everywhere](README.md)
- [Governance - the full edit protocol](../_meta/governance.md)
