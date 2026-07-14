---
id: <<workspace_slug>>.templates.index
name: Templates - copy-and-complete authoring scaffolds
type: reference
layer: C2
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [templates, scaffolds, fill-in, schemas, runs, c2]
related:
  - {ref: AGENTS.md, dimension: why, polarity: derived_from}
  - {ref: 30_schemas/README.md, dimension: what, polarity: explains}
  - {ref: 90_runs/README.md, dimension: where, polarity: enables}
---

# Templates

**Fill-in authoring starting points** (C2): copy-and-complete scaffolds for the recurring artefacts a
workspace produces - a daily brief, a decision packet, a memory atom, a design system. A template is
the **blank instance** you copy and fill by hand; a schema is the **shape** that instance must
satisfy. Templates carry the prose, headings, and `{{...}}` runtime markers so the founder (or the
agent) fills fields rather than reinventing structure each time. Where each kind of thing lives in the OS:
[`../AGENTS.md`](../AGENTS.md).

## The contract

- **Schema defines, template scaffolds, run is the output.** Most templates are a blank instance of a
  [`../30_schemas/`](../30_schemas/README.md) shape (the `related:` `derived_from` edge names which); completing
  one produces a C4 artefact in [`../90_runs/`](../90_runs/README.md), a register row, or a
  [`../20_memory/`](../20_memory/README.md) atom. The template's own header says where the filled copy
  lands.
- **Copy, don't edit in place.** Copy the file to its destination (e.g. `90_runs/YYYY-MM-DD-brief.md`)
  and fill it there. The template stays blank for the next use.
- **Generic and blank.** Templates hold no instance content. They are part of the reusable OS, so
  improvements flow **upstream** to the master template per the upstreaming rule.

## What lives here

- [`daily-brief.md`](daily-brief.md) - the start-of-day founder brief; renders open loops + the
  decision queue. Pairs with [`../60_workflows/daily-brief.md`](../60_workflows/daily-brief.md).
- [`weekly-review.md`](weekly-review.md) - the weekly fold over registers and run folders; feeds the
  reaper. Pairs with [`../60_workflows/weekly-review.md`](../60_workflows/weekly-review.md).
- [`decision-packet.md`](decision-packet.md) - a blank Decision Packet: options, evidence, a
  recommendation for the founder to decide. Schema: [`../30_schemas/decision-packet.md`](../30_schemas/decision-packet.md).
- [`memory-card.md`](memory-card.md) - a memory atom (5W1H + provenance) to drop into a depth layer.
  Schema: [`../30_schemas/memory-card.md`](../30_schemas/memory-card.md).
- [`opportunity.md`](opportunity.md) - a wedge/validation worksheet. Schema:
  [`../30_schemas/opportunity.md`](../30_schemas/opportunity.md).
- [`research-signal.md`](research-signal.md) - one captured external signal (source-or-abstain),
  feeding atoms and opportunities.
- [`design-system.md`](design-system.md) - a blank **DESIGN.md** (AI-readable design tokens + brand
  rationale), copied into a client/project repo as `DESIGN.md`.
- [`concept-folder/`](concept-folder/README.md) - a fill-in index map plus one-concept note scaffold
  for decomposing large durable context under the
  [`context-decomposition`](../10_doctrine/context-decomposition.md) rule.
- [`knowledge-pack/`](knowledge-pack/README.md) - a stampable **knowledge corpus** for a project
  repo (manifest, type/relation registries, one-concept-per-file `concepts/`), copied into the
  target repo as `knowledge/`. Vocabulary: [`../30_schemas/taxonomy.md`](../30_schemas/taxonomy.md).

Each carries its own frontmatter, `{{...}}` runtime markers, and a destination note. Start from the
[Routing map](../AGENTS.md#routing-map): it points each task at the template to copy.

## Related

- [<<WORKSPACE_NAME>>](../AGENTS.md)
- [Schemas - the shape contracts for structured artefacts](../30_schemas/README.md)
- [Runs](../90_runs/README.md)
