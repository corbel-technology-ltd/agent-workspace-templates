---
id: <<workspace_slug>>.reference
name: Workspace user reference - files, scripts, memory, adapters, upkeep
type: reference
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [reference, map, scripts, hooks, memory, adapters, maintenance]
related:
  - {ref: README.md, dimension: why, polarity: explains}
  - {ref: reference-notes/00-INDEX.md, dimension: how, polarity: enables}
---

# Workspace user reference

The after-week-one lookup sheet: where things live, what runs, and the safe maintenance commands.
Start-of-session behaviour and authority still come from `AGENTS.md`.

## Where things live

| Need | Location |
|---|---|
| Identity, routing, authority | `AGENTS.md` |
| Current focus and latest handover | `00_meta/staging.md` |
| Standing judgement | `10_doctrine/` |
| Durable reference | `15_canon/` |
| Events and memory | `20_memory/` |
| Artefact contracts | `30_schemas/` |
| Blank forms | `40_templates/` |
| Live queues and ledgers | `50_registers/` |
| Runtime-neutral playbooks | `60_workflows/` |
| Instance system connections | `70_integrations/` |
| Project state and loops | `80_projects/` |
| Briefs, packets, handovers | `90_runs/` |
| Deterministic runtime logic | `core/` |
| Checks and maintenance commands | `tools/` |

## Scripts, memory and maintenance

The rest of this lookup sheet is situational detail: the script catalogue, the memory map, and the
safe maintenance commands. It is decomposed into concept notes so a session loads only what the
task needs: start at [`reference-notes/00-INDEX.md`](reference-notes/00-INDEX.md) and do not
preload the whole folder.

| Need | Load |
|---|---|
| What a hook or tool script does; adding a new agent-agnostic skill; proving hook wiring after setup or changes | `reference-notes/01-scripts-and-hooks.md` |
| Where memory lives and how to search it | `reference-notes/02-memory-map.md` |
| Updating from the template, backing the workspace up and mirroring it, or uninstalling it | `reference-notes/03-maintenance-operations.md` |

## Related

- [Folder-Agent-Workspace](README.md)
- [Workspace reference notes — index](reference-notes/00-INDEX.md)
