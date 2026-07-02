---
id: <<workspace_slug>>.projects.readme
name: 80_projects — how the live project tracker works
type: reference
layer: C1
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [projects, readme, loops, live-state]
related:
  - {ref: 80_projects/index.md, dimension: where, polarity: complements}
  - {ref: 30_schemas/project.md, dimension: what, polarity: explains}
  - {ref: 60_workflows/open-loop-tracking.md, dimension: how, polarity: enables}
---

# 80_projects

The live tracker for this workspace's active projects. One folder per project, each holding the
project's working state. The navigation index is [`index.md`](index.md); the folder contract is
[`30_schemas/project.md`](../30_schemas/project.md); the lifecycle is
[`60_workflows/open-loop-tracking.md`](../60_workflows/open-loop-tracking.md).

## What it is

This is **live working state** (C1). It is distinct from:

- `15_canon/` — durable *knowledge* (facts, gotchas) about the domains a project touches. C3.
- root `projects/` (gitignored, if present) — self-contained *apps/binaries* with their own
  internals, out of the control-plane scope.

A project folder has exactly two files (per the schema):

- `index.md` — the project's frontmatter, a one-line summary, a `## Status` paragraph (current state
  and next step), and `## Links` (relevant runs + canon + its `loops.md`).
- `loops.md` — the project's outstanding loops as a `## Open` / `## Closed` table.

Cross-cutting loops with no project home live in [`_general/loops.md`](_general/loops.md).

## How it is used

- **Add a project:** create `80_projects/<slug>/` with `index.md` and `loops.md` per
  [`30_schemas/project.md`](../30_schemas/project.md), and add a row to [`index.md`](index.md). Seed
  a project only when it has live content (`AGENTS.md` rule 8 — add leaves only when their inputs
  exist).
- **A loop** opens from a journal event (source-or-abstain), lives in the project's `loops.md`
  `## Open` table until it resolves, then moves to that file's `## Closed`. The journal is the truth;
  these tables are the rebuildable view. Lifecycle:
  [`60_workflows/open-loop-tracking.md`](../60_workflows/open-loop-tracking.md).
- **The briefs aggregate it:** the SessionStart brief and the daily brief read the `## Open` table of
  every `80_projects/*/loops.md` (direct children only, including `_general/`), never recursively.
  The daily brief promotes due `ball: mine` loops to its Top founder actions.

## Related

- [Active projects](index.md)
- [Project schema](../30_schemas/project.md)
- [Open-loop tracking workflow](../60_workflows/open-loop-tracking.md)
