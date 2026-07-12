---
id: <<workspace_slug>>.reference.scripts-and-hooks
name: Workspace reference — scripts, adapters and hook wiring
type: reference
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [reference, scripts, hooks, adapters, tools]
related:
  - {ref: reference-notes/00-INDEX.md, dimension: where, polarity: part_of}
  - {ref: core/RUNTIMES.md, dimension: where, polarity: requires}
  - {ref: core/hooks/README.md, dimension: what, polarity: explains}
  - {ref: tools/README.md, dimension: how, polarity: enables}
---

# Workspace reference — scripts, adapters and hook wiring

> Decomposed 2026-07-12 under the context-decomposition rule (10_doctrine/context-decomposition.md); wording unchanged.

Folder map: [00-INDEX.md](00-INDEX.md).

## Scripts

### `core/hooks/` - runtime reflexes

| Script | One-line job |
|---|---|
| `journal-guard.py` | Blocks changes to existing journal entries while allowing a new entry. |
| `onboarding-gate.py` | Points a fresh workspace at onboarding; silent after the sentinel is removed. |
| `session-brief.py` | Prints identity, current focus, open decisions, and project loops at session start. |
| `session-digest.py` | Appends a terse journal event when a session ends. |
| `reaper.py` | Validates, tiers, decays, supersedes, and archives memory deterministically. |
| `registry-drift.py` | Reports uncatalogued operational components without blocking work. |
| `sleep-prep.py` | Builds the bounded evidence set for deep memory synthesis. |
| `sleep-apply.py` | Validates proposed memories, writes accepted atoms, then runs the reaper. |

### `tools/` - checks and maintenance

| Script | One-line job |
|---|---|
| `agnostic-check.py` | Proves neutral files are runtime-independent and adapters remain thin. |
| `gen-related.py` | Regenerates body links from typed `related:` edges. |
| `memory-selftest.py` | Proves the complete memory loop in a disposable fixture. |
| `okf-check.py` | Checks required frontmatter, valid links, and mirrored relationships. |
| `recall-tiered.py` | Searches memory from the hottest curated layer down to raw journal truth. |
| `scrub-check.py` | Finds configured private or instance-specific terms before distribution. |
| `template-update.py` | Checks, classifies, and safely applies template changes without clobbering customisations. |
| `update-selftest.py` | Proves the non-clobbering template update flow in disposable repositories. |

Other executable entry points: `core/onboarding/apply.py` performs the one-time atomic placeholder
fill; `core/git-hooks/pre-commit` is the optional runtime-independent journal backstop.

## Runtime adapters and skills

Runtime-specific pointers, config directories, skill surfaces, and hook wiring are catalogued only
in [`core/RUNTIMES.md`](../core/RUNTIMES.md). An adapter translates lifecycle events into the neutral
contracts; it does not own policy, workflows, or business logic. Root pointer files point to
`AGENTS.md`; adapter skill files point to a neutral playbook.

### Add a new agent-agnostic skill

| Step | Change |
|---|---|
| 1. Neutral playbook | Add `60_workflows/<skill-name>.md` with the same frontmatter pattern as its siblings and no runtime-specific language. |
| 2. Thin pointers | In each supported runtime skill/command surface listed in `core/RUNTIMES.md`, add a short pointer that says to follow that playbook. |
| 3. Registry | Add the pointer paths and lifecycle wiring notes to `core/RUNTIMES.md`; keep all vendor detail there. |
| 4. Proof | Run `python3 tools/agnostic-check.py`; it must report that the neutral core is vendor-free and adapters are thin pointers. |

## Hook wiring and proof

| Check | Command or expected result |
|---|---|
| Core start brief | `python3 core/hooks/session-brief.py` prints the workspace brief. |
| Onboarding gate | `python3 core/hooks/onboarding-gate.py` is silent when live; on a blank copy it prints the exact onboarding action. |
| Journal block | Send `{"op":"modify","path":"20_memory/journal/<existing-entry>.md"}` to `python3 core/hooks/journal-guard.py`; exit `2` means blocked. |
| Adapter purity | `python3 tools/agnostic-check.py` exits `0`. |
| Automatic wiring | Start a new runtime session and confirm the session brief appears; use the adapter's wiring and verification entry in `core/RUNTIMES.md` if it does not. |

Hook logic and its payload contract are in [`core/hooks/README.md`](../core/hooks/README.md). Installing
or changing adapter wiring is an operator-approved settings change.

## Related

- [Reference notes index](00-INDEX.md)
- [Runtime adapters](../core/RUNTIMES.md)
- [Reflex hooks](../core/hooks/README.md)
- [Tools](../tools/README.md)
