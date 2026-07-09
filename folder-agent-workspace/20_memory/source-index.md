---
id: <<workspace_slug>>.memory.source-index
name: Source index
type: register
layer: C1
status: current
owner: shared
staging: v1-now
created: <<CREATED_DATE>>
tags: [memory, provenance, sources, source-or-abstain]
---

# Source index

The provenance ledger enforcing the source-of-truth rule: **every durable memory preserves a
pointer to where it came from.** Primary sources (statute, standards bodies, official guidance)
are listed here so atoms can cite them and so currency can be re-checked.

| source id | kind | citation / URL | covers | confidence-tier | last_verified |
|---|---|---|---|---|---|
| (none yet) | | | | | |

Tiers: `primary` (verified against the original) · `secondary` (reported) · `[VERIFY]` (believed,
unconfirmed). A legal/statutory atom must cite a `primary` source or be marked `aspirational` /
`[VERIFY]`. Absence of a source is an explicit "I don't know", never a guess.
