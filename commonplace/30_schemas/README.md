---
id: <<workspace_slug>>.schemas.index
name: Schemas — the shape contracts for structured artefacts
type: reference
layer: C2
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [schemas, contracts, frontmatter, okf, 5w1h, artefacts]
related:
  - {ref: AGENTS.md, dimension: why, polarity: derived_from}
  - {ref: 30_schemas/event.md, dimension: what, polarity: explains}
  - {ref: 30_schemas/memory-card.md, dimension: what, polarity: explains}
  - {ref: 30_schemas/decision-packet.md, dimension: what, polarity: explains}
  - {ref: 40_templates/decision-packet.md, dimension: how, polarity: enables}
  - {ref: 20_memory/README.md, dimension: what, polarity: explains}
---

# Schemas

The **shape contracts** (C2) for every structured artefact the workspace produces: what fields each
artefact type must carry, in what shape, with what rules. A schema is the answer to "what does a
valid X look like?" — the journal event, the memory atom, the decision the founder signs off. The
[routing map](../AGENTS.md#routing-map) sends most tasks through one of these before anything durable
is written.

## What a schema is (and is not)

Each file here is one **contract**, not a generator. It states the frontmatter keys, the body shape,
and the rules that make an instance valid — then leaves the producing to a workflow or a template.
Every durable artefact is Markdown with an **OKF-compatible body** plus the typed-edge + lifecycle
frontmatter extension (`AGENTS.md` rule 6): `type` required, one concept per file, `related[].ref`
edges mirrored as inline body links. The schemas are where those keys are pinned down per artefact.
Many fields map to a future SQL column, so the file store can graduate to a database + vector + graph
as a migration rather than a rewrite.

## How it is used (the contract)

Read the schema **before** you write the artefact, not after. The flow:

1. A [routing-map](../AGENTS.md#routing-map) row names the schema for the task (record something →
   [`event.md`](event.md); a founder decision → [`decision-packet.md`](decision-packet.md); a
   durable fact → [`memory-card.md`](memory-card.md)).
2. Fill the artefact to the schema's frontmatter + field list. Where a
   [template](../40_templates/) exists, fill from it; the schema is the contract, the template is the
   blank.

3. Validation against the schema is part of **Plan → Validate → Execute**: an artefact with a missing
   mandatory field is not ready to surface (a Decision Packet with an empty field is held, not
   shipped). Schemas are C2 reference — do not silently rewrite one; propose a diff (`AGENTS.md`
   rule 4).

## What lives here

- [`event.md`](event.md) — the **journal event**: one immutable Markdown file in
  [`../20_memory/journal/`](../20_memory/), the only source of truth. Everything else folds from it.
- [`memory-card.md`](memory-card.md) — the **memory atom**: the 5W1H footprint + provenance + trust +
  activation/validity fields. The unit the memory model decays, merges, and forgets over (see
  [`../20_memory/README.md`](../20_memory/README.md)).

- [`decision-packet.md`](decision-packet.md) — the **Decision Packet**: the one-page,
  human-in-the-loop surface that encodes the gate. The only way a consequential action reaches the
  founder. Blank: [`../40_templates/decision-packet.md`](../40_templates/decision-packet.md).

- [`action-intent.md`](action-intent.md) — the **action intent**: a proposed consequential action,
  with a reversibility judgement, made explicit so it can be checked against the gate.
- [`opportunity.md`](opportunity.md) — the **opportunity object**: a candidate thing-to-build,
  scored by hand, ending in a recommendation. Complements an intel engine, does not duplicate it.

- [`project.md`](project.md) — the **project**: the folder contract under
  [`../80_projects/`](../80_projects/) — `index.md` (status + links) and `loops.md` (the `## Open` /
  `## Closed` loop tables).

- [`knowledge-gap.md`](knowledge-gap.md) — the **knowledge gap**: one named thing the workspace does
  not yet know but needs to, a row in `20_memory/knowledge-gaps.md`. The hand-run ignorance graph
  that makes **source-or-abstain** legible.

## Instance state

The schemas ship **carried** — the contracts above are part of the operating system and travel with
the template. What is empty is the artefacts they shape: no journal events, no atoms, no packets yet.
Those accrue in `20_memory/`, `90_runs/`, and `80_projects/` as the workspace runs.

## Related

- [<<WORKSPACE_NAME>>](../AGENTS.md)
- [Journal event schema](event.md)
- [Memory card (atom) schema](memory-card.md)
- [Decision Packet schema](decision-packet.md)
- [Decision packet (blank instance)](../40_templates/decision-packet.md)
- [Memory structure — the model](../20_memory/README.md)
