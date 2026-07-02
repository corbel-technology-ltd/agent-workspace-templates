---
id: <<store_slug>>.operating-rules.readme
name: Operating rules - how agents behave, everywhere
type: reference
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [operating-rules, governance, cross-workspace, discipline]
related:
  - {ref: SHARED.md, dimension: why, polarity: derived_from}
  - {ref: operating-rules/scope-test.md, dimension: what, polarity: enables}
  - {ref: operating-rules/rule-plumbing.md, dimension: how, polarity: enables}
---

# Operating rules

Rules that govern **how agents operate across every workspace** - decision frameworks, discipline
for changing the system itself, coordination protocols. Rules, not knowledge: what agents *know*
lives in their workspaces; how they *behave* lives here once.

## What does not live here

- Identity material (voice, availability) - [`../identity/`](../identity/README.md)
- Preferences that vary by context - [`../calibration-os/`](../calibration-os/README.md)
- Workspace-specific rules - each workspace's own constitution
- Domain knowledge - each workspace's own folders

## Rules

| Rule | Governs |
|---|---|
| [`scope-test.md`](scope-test.md) | What earns a place in this store: the mutual-benefit test every addition must pass. |
| [`rule-plumbing.md`](rule-plumbing.md) | How a new rule is installed properly - location, frontmatter, propagation, discoverability - so rules never scatter or fork. |

Two seed rules ship because they are the store's own operating mechanics. Your rules accrue
through governance: propose with [`_rule-template.md`](_rule-template.md), collect sign-off, land
with a ledger trailer.

## Related

- [<<STORE_NAME>>](../SHARED.md)
- [Scope test - what earns a place in the store](scope-test.md)
- [Rule plumbing - how to install a rule properly](rule-plumbing.md)
