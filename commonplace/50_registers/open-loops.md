---
id: <<workspace_slug>>.register.open-loops
name: Open loops register (moved)
type: register
layer: C1
status: superseded
owner: shared
created: <<CREATED_DATE>>
staging: v1-now
tags: [register, open-loops, waiting-on, moved, redirect]
related:
  - {ref: 80_projects/index.md, dimension: where, polarity: superseded_by}
  - {ref: 60_workflows/open-loop-tracking.md, dimension: how, polarity: explains}
  - {ref: 30_schemas/project.md, dimension: what, polarity: explains}
---

# Open loops — moved to per-project files

Outstanding loops no longer live in a single flat register. Each loop now lives with its project
under [`../80_projects/`](../80_projects/index.md): `80_projects/<slug>/loops.md` (and
`80_projects/_general/loops.md` for loops tied to no project).

- **Where loops live now:** [`../80_projects/index.md`](../80_projects/index.md)
- **The contract:** [`../30_schemas/project.md`](../30_schemas/project.md)
- **How to open / surface / close a loop:** [`../60_workflows/open-loop-tracking.md`](../60_workflows/open-loop-tracking.md)

The doctrine is unchanged: a loop derives from a journal event (source-or-abstain), the journal is
the truth, and the loops file is the rebuildable view. The daily brief and the SessionStart brief
read the per-project `## Open` tables. This stub remains only so existing links resolve — **do not
re-populate it as a live register**: loops live per project, and a second table here would split the
source of truth.

## Related

- [Active projects](../80_projects/index.md)
- [Open-loop tracking workflow](../60_workflows/open-loop-tracking.md)
- [Project schema](../30_schemas/project.md)
