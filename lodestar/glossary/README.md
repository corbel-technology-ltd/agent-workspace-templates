---
id: <<store_slug>>.glossary.readme
name: Glossary - the shared vocabulary
type: reference
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [glossary, vocabulary, naming, terms]
related:
  - {ref: SHARED.md, dimension: why, polarity: derived_from}
  - {ref: glossary/glossary.md, dimension: what, polarity: enables}
---

# Glossary

The shared vocabulary: terms every agent uses identically across workspaces, plus - just as
load-bearing - the **names ruled out**. Vocabulary drift is a real cross-workspace failure mode:
two agents using one word for different things (or different words for one thing) corrupts every
handoff between them.

- [`glossary.md`](glossary.md) - the live table, plus the killed-names register.

One vocabulary rule: a term used in a cross-workspace artefact (dashboard rows, ledger entries,
shared rules) must either be plain English or be in the glossary. Workspace-internal jargon stays
internal.

## Related

- [<<STORE_NAME>>](../SHARED.md)
- [The glossary table](glossary.md)
