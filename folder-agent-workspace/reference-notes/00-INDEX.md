---
id: <<workspace_slug>>.reference.index
name: Workspace reference notes — index
type: index
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [reference, index, concept-folder, scripts, memory, maintenance]
related:
  - {ref: REFERENCE.md, dimension: where, polarity: part_of}
---

# Workspace reference notes — index

## Purpose

The situational half of [`../REFERENCE.md`](../REFERENCE.md): the after-week-one lookup sheet's
script catalogue, memory map, and safe maintenance commands, decomposed so a session loads only
the part a task needs. Not a second source of truth — every note here summarises a source file
that still owns its own facts.

## Load policy

Do not preload this folder. Read [`../REFERENCE.md`](../REFERENCE.md) first (it holds the compact
"Where things live" core); come here only when a task's retrieval cue matches a row below.

| File | Contains | Load when |
| --- | --- | --- |
| `01-scripts-and-hooks.md` | The `core/hooks/` and `tools/` script tables, how to add a new agent-agnostic skill, and the hook-wiring proof checklist | you need to know what a script does, you're adding a skill, or you're proving hooks fire after setup/changes |
| `02-memory-map.md` | Where each memory depth layer lives and the `recall-tiered.py` search command | you need to search memory or explain the memory location model |
| `03-maintenance-operations.md` | Pulling a template update, backing the workspace up and mirroring it, and uninstalling it | you're running a workspace-lifecycle operation (update / backup / uninstall) |

## Load recipes

- **"What does script X do?":** `01-scripts-and-hooks.md` only.
- **Adding a new agent-agnostic skill:** `01-scripts-and-hooks.md` (the "Add a new agent-agnostic
  skill" table).
- **Post-setup or post-change verification that hooks fire:** `01-scripts-and-hooks.md` (the "Hook
  wiring and proof" table).
- **Searching or explaining memory:** `02-memory-map.md` only.
- **Template update, backup, or uninstall:** `03-maintenance-operations.md` only.
- **Full audit of this reference area:** this index, then all three notes in order.

## Authority

Use this precedence when sources conflict:

1. `AGENTS.md` (session boot, routing, and the safety gate) always wins.
2. The native source file a note summarises (`core/RUNTIMES.md`, `core/hooks/README.md`,
   `20_memory/README.md`, `60_workflows/README.md`, `tools/README.md`, and the scripts
   themselves) owns its factual content - per `AGENTS.md` rule 7, the graph/index is a map, not
   the terrain.
3. [`../REFERENCE.md`](../REFERENCE.md) is authoritative only for reference routing and load
   policy, not for facts owned by those native sources.
4. This folder's notes.

The spine and this folder may never override `AGENTS.md` or a native source, invent a maintenance
command that the scripts do not support, or become a second home for content that already lives in
the files they point at.

## Maintenance rule

Update a concept note only when the section it decomposed from changes. Update this index when a
note is added, removed, renamed, or its retrieval cue changes. If `../REFERENCE.md`'s core
changes, check whether a note's summary of a source file has drifted too.

## Related

- [Workspace user reference - files, scripts, memory, adapters, upkeep](../REFERENCE.md)
