---
id: <<store_slug>>.operating-rules.rule-plumbing
name: Rule plumbing - how to install a rule properly
type: doctrine
layer: C3
status: current
load: triggered
owner: shared
created: <<CREATED_DATE>>
tags: [rules, plumbing, discipline, propagation, discoverability]
related:
  - {ref: operating-rules/README.md, dimension: where, polarity: derived_from}
  - {ref: CHANGES.md, dimension: how, polarity: requires}
---

# Rule plumbing

A rule that is not plumbed does not exist: it lives in one agent's habits, silently forks across
workspaces, and dies at the next context reset. Installing a rule means all six:

1. **Canonical location** - one file, here, named for the rule. No second copy anywhere;
   workspaces that need to reference it point, never paste.
2. **Complete frontmatter** - `id`, `type`, `status`, `owner`, tags; `status: proposed` until
   sign-off completes, then `current`.
3. **The rule states its trigger** - a "When this applies" section precise enough that two agents
   agree whether a given situation is covered.
4. **Ledger + window** - a `CHANGES.md` trailer, the objection window, and (for a new file) every
   roster agent's sign-off.
5. **Propagation** - each workspace that must *act* on the rule gets a pointer from its own
   constitution or boot path; loading the store's `operating-rules/` at boot covers the default.
6. **Discoverability test** - a fresh agent, given only the store and the question "may I do X?",
   finds the rule without being told it exists. If it cannot, the rule's name or the README table
   needs fixing.

Retiring a rule is the same protocol in reverse: `status: superseded`, a trailer naming what
replaces it, and the row removed from the README table.

## Related

- [Operating rules - how agents behave, everywhere](README.md)
- [Shared profile changelog](../CHANGES.md)
