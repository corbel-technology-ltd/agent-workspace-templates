---
id: <<workspace_slug>>.meta.agent-os-design.staged-plan
name: Agent OS design — staged plan
type: design-spec
layer: C0
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [agent-os, hooks, roadmap, staged-plan]
related:
  - {ref: 00_meta/agent-os-design/00-INDEX.md, dimension: where, polarity: part_of}
---

# Agent OS design — staged plan

One concept: what's built now, what awaits an input, and what's deliberately deferred. Folder map:
[00-INDEX.md](00-INDEX.md).

> Decomposed 2026-07-12 under the context-decomposition rule (10_doctrine/context-decomposition.md); wording unchanged.

## Staged plan

### NOW (built / shipped with the template)

- **`AGENTS.md`** is the full constitution (operating loop, proactivity + prioritisation hierarchy,
  sensor doctrine, the OS map, definition of done). Judgment only.

- **`50_registers/improvement-backlog.md`** - where proactivity output lands, with a prose priority
  tag (do-now / suggest / log / ignore).

- **Reflex hooks**, logic in `core/hooks/`, wired per runtime (installing or changing wiring edits
  runtime settings, so it needs operator approval):
  1. **Journal-immutability guard** (pre-tool-use) - block any modify/overwrite/delete targeting
     `20_memory/journal/*`. Turns the load-bearing append-only invariant into a reflex. Narrow
     matcher; silent unless it blocks. An optional git pre-commit guard (`core/git-hooks/`) backs it
     at commit time for any runtime.
  2. **Onboarding gate** (session start) - while the `.uninitialised` sentinel exists, route the
     agent to the onboarding playbook before any other work.
  3. **Session brief** (session start) - a boot-orientation block (who you are, load shared context,
     read `00_meta/staging.md`, re-verify the newest handover) plus open `decision-queue` items and
     the per-project `## Open` loops aggregated from `80_projects/*/loops.md` (`## Closed` excluded).
     A few lines; situational awareness at near-zero cost.
  4. **Session digest** (session end) - append one journal event (what changed, decisions, files) so
     the session is captured as truth for the reaper. Silent (writes to `journal/`).
  5. **Reaper** (session end) - the deterministic fast memory pass.
  6. **Registry-drift sensor** (session end, advisory) - flag uncatalogued ops components.

### AWAIT-NEED (specced, switch on when the input exists)

- A prompt-submit task-router (deterministic classify) - once prompt volume justifies it.
- Post-tool-use metric/data-stream detection + a `metric-scout` subagent - once the journal has real
  volume for it to scan (a subagent with no journal to read is pointless now).

- A file-changed data-stream scout - once there are real data streams to map.
- Playbooks - graduate a `60_workflows/` spec into `core/` (surfaced as a runtime skill) when it is
  invoked repeatedly.
- A pre-compaction snapshot - useful insurance once sessions carry heavy context.

### DEFER (no data / over-strict)

- Any statistical graduation apparatus (no events logged yet - use plain counts if/when fed).
- A broad `PreToolUse` BLOCK on send/publish/push (over-strict vs the gate's CONFIRM; match narrowly
  on `--force` / protected branches only, and only once such tooling exists here).

- `risk-reviewer` / `simplifier` subagents - reuse a review skill / a doctrine line first.

## Evidence / provenance

Source: the spine, `00_meta/agent-os-design.md`, "Staged plan" section, moved verbatim when this
folder was created under `10_doctrine/context-decomposition.md`. Update this note when a hook or
mechanism actually ships, moves stage, or is dropped; update the spine only if the underlying design
rationale itself changes.
