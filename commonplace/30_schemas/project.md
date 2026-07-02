---
id: <<workspace_slug>>.schema.project
name: Project schema
type: schema
layer: C2
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [schema, project, loops, registers, 80_projects]
related:
  - {ref: 80_projects/index.md, dimension: where, polarity: explains}
  - {ref: 30_schemas/event.md, dimension: why, polarity: derived_from}
  - {ref: 50_registers/decision-queue.md, dimension: what, polarity: supports}
---

# Project schema

An **active project** is a folder under `80_projects/<slug>/` holding the project's live working
state: its status and its outstanding loops. It is the C1 live tracker, distinct from durable
knowledge in `15_canon/` and from any gitignored root `projects/` (self-contained apps/binaries with
their own internals). Seed a project only when it has live content (`AGENTS.md` rule 8). The folder
contract is indexed from [`80_projects/index.md`](../80_projects/index.md) and traces back to the
journal via [`30_schemas/event.md`](event.md); a blocked loop graduates to
[`50_registers/decision-queue.md`](../50_registers/decision-queue.md).

A project folder has exactly two files: `index.md` (status + links) and `loops.md` (its outstanding
loops).

## `index.md` (the project)

```yaml
---
id: <<workspace_slug>>.project.<slug>
name: <project name>
type: project
layer: C1
status: active | paused | done
owner: <<agent_slug>>
created: YYYY-MM-DD
tags: [project, ...]
related:
  - {ref: 15_canon/domains/<domain>/README.md, dimension: what, polarity: explains}
  - {ref: 90_runs/<run>.md, dimension: when, polarity: derived_from}
---
```

Body: `## Summary` (one line), `## Status` (one paragraph: current state and the next step), and
`## Links` (relevant runs + canon + a pointer to `loops.md`). A project's next step is a sentence in
`## Status`, not a separate surface; structured waiting-on commitments are loops in `loops.md`.

## `loops.md` (the project's loops)

Carries OKF-compatible frontmatter like any durable file (`AGENTS.md` rule 6): `type: register`,
`id: <<workspace_slug>>.project.<slug>.loops`, layer C1, `status`/`owner`/`created`/`tags`, and
`related:` to the project `index.md` and the loop sources. Body:

```text
## Open

| item | ball | who | since | due | status | source |
|---|---|---|---|---|---|---|
| <one-line commitment> | mine | <owner> | YYYY-MM-DD | YYYY-MM-DD or none | open | [journal](...) |

## Closed

| item | ball | who | opened | closed | outcome | source |
|---|---|---|---|---|---|---|
| (none yet) | | | | | | |
```

- **ball** — who the loop hangs on: `mine` (the owner to act), `theirs` (a counterparty owes),
  `external` (awaiting a dated external event with no single owner to chase). The daily brief
  promotes due `ball: mine` loops to §1 Top founder actions.
- **status** — `open` | `nudged` | `overdue` | `blocked`.
- **source** — the journal entry the loop traces to (source-or-abstain). A loop with no journal
  source is unverified. The journal is the truth; `loops.md` is the rebuildable view.
- `item` is column 0 so the SessionStart brief parser reads it directly.
- One `## Open` table per file (the brief parser handles a single open table per file).
- `## Closed` is per-project, append-only. A re-opened loop is a NEW row in `## Open` with a fresh
  `since`, never an edit of a closed row.
- A `blocked` loop becomes a [`decision-queue.md`](../50_registers/decision-queue.md) row with a
  Decision Packet; do not guess the decision in the loops table.

## Aggregation

The SessionStart brief and the daily brief read the `## Open` table of every
`80_projects/*/loops.md` (direct children only, including `_general/loops.md`), never recursively.
Cross-cutting loops with no project home live in `80_projects/_general/loops.md`.

## Naming note

A workspace whose live tracker is product- or client-centric rather than project-centric may name
this folder and schema to match its domain (for example a `product_loops` framing over the same
`80_projects/<slug>/loops.md` shape). The contract — folder per item, `index.md` + `loops.md`, the
`## Open`/`## Closed` tables, `ball`/`status`/`source` columns, `item` in column 0 — is unchanged;
only the label differs. The brief aggregation globs `80_projects/*/loops.md` regardless of label.

## Related

- [Active projects](../80_projects/index.md)
- [Journal event schema](event.md)
- [Decision queue — open founder decisions](../50_registers/decision-queue.md)
