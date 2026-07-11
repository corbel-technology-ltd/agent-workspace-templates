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
  - {ref: core/RUNTIMES.md, dimension: where, polarity: requires}
  - {ref: core/hooks/README.md, dimension: what, polarity: explains}
  - {ref: 20_memory/README.md, dimension: where, polarity: explains}
  - {ref: 60_workflows/README.md, dimension: how, polarity: enables}
  - {ref: tools/README.md, dimension: how, polarity: enables}
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

Other executable entry points: `core/onboarding/apply.py` performs the one-time atomic placeholder
fill; `core/git-hooks/pre-commit` is the optional runtime-independent journal backstop.

## Runtime adapters and skills

Runtime-specific pointers, config directories, skill surfaces, and hook wiring are catalogued only
in [`core/RUNTIMES.md`](core/RUNTIMES.md). An adapter translates lifecycle events into the neutral
contracts; it does not own policy, workflows, or business logic. Root pointer files point to
`AGENTS.md`; adapter skill files point to a neutral playbook.

### Add a new agent-agnostic skill

| Step | Change |
|---|---|
| 1. Neutral playbook | Add `60_workflows/<skill-name>.md` with the same frontmatter pattern as its siblings and no runtime-specific language. |
| 2. Thin pointers | In each supported runtime skill/command surface listed in `core/RUNTIMES.md`, add a short pointer that says to follow that playbook. |
| 3. Registry | Add the pointer paths and lifecycle wiring notes to `core/RUNTIMES.md`; keep all vendor detail there. |
| 4. Proof | Run `python3 tools/agnostic-check.py`; it must report that the neutral core is vendor-free and adapters are thin pointers. |

## Memory map

| Location | Meaning |
|---|---|
| `20_memory/journal/` | Append-only ground truth; corrections and retractions are new events. |
| `20_memory/working/` | Small, hottest set for immediate work. |
| `20_memory/short-term/` | Current useful atoms outside the working budget. |
| `20_memory/long-term/` | Durable, repeatedly supported memory. |
| `20_memory/subconscious/` | Non-assertable associations, priors, trends, and world-model cues. |
| `20_memory/archive/` | Cold, expired, or superseded atoms retained for recall. |
| `20_memory/_quarantine/` | Invalid or unsourced atoms awaiting review. |
| `20_memory/_meta/` | Rebuild markers and sleep state; generated rather than authoritative. |
| `20_memory/homeostasis.yml` | Working-set budgets, decay, hysteresis, promotion, and sleep set-points. |

Search it:

```bash
python3 tools/recall-tiered.py <search words>
```

Add `--all` to search every depth, `--follow` for one-hop links, or `--touch` only when retrieval
should strengthen the matching atom. The full model is in [`20_memory/README.md`](20_memory/README.md).

## Hook wiring and proof

| Check | Command or expected result |
|---|---|
| Core start brief | `python3 core/hooks/session-brief.py` prints the workspace brief. |
| Onboarding gate | `python3 core/hooks/onboarding-gate.py` is silent when live; on a blank copy it prints the exact onboarding action. |
| Journal block | Send `{"op":"modify","path":"20_memory/journal/<existing-entry>.md"}` to `python3 core/hooks/journal-guard.py`; exit `2` means blocked. |
| Adapter purity | `python3 tools/agnostic-check.py` exits `0`. |
| Automatic wiring | Start a new runtime session and confirm the session brief appears; use the adapter's wiring and verification entry in `core/RUNTIMES.md` if it does not. |

Hook logic and its payload contract are in [`core/hooks/README.md`](core/hooks/README.md). Installing
or changing adapter wiring is an operator-approved settings change.

## Updating from the template

| What changed upstream | Safe update path |
|---|---|
| A stocked script or gate | From the capability registry, run `status`, inspect `diff`, then approve `install`; never overwrite a local difference blindly. |
| Doctrine, schemas, workflows, or templates | Instantiate the latest template beside this workspace, compare it, and port only the reviewed neutral changes. Never merge a blank template wholesale over live identity, canon, registers, or memory. |
| A useful local generic improvement | Port it to the template or use the capability registry's `pack` flow; keep instance facts here. |

The neutral workflow catalogue is [`60_workflows/README.md`](60_workflows/README.md), and the gate
catalogue is [`tools/README.md`](tools/README.md).

Capability update one-liners (replace `<registry-root>`):

```bash
python3 <registry-root>/core/chandler.py status --workspace "$PWD"
python3 <registry-root>/core/chandler.py diff <capability> --workspace "$PWD"
python3 <registry-root>/core/chandler.py install <capability> --workspace "$PWD"
```

## Backup and mirror

1. Keep the workspace's off-machine repository private; memory and canon may be sensitive.
2. Commit approved changes, add a private backup remote once, then push the `main` branch:

   ```bash
   git remote add backup <private-repository-url>
   git push -u backup main
   ```

3. Mirror every branch and tag when required: `git push --mirror <private-mirror-url>`.
4. Back up `.env` separately in a secrets manager: it is intentionally ignored by git.

## Uninstall

The workspace installs no service and owns no global database. First push or copy anything to
keep, preserve the untracked `.env` separately, and close the runtime. Then, from its parent folder:

```bash
rm -rf -- '<workspace-folder>'
```

That removes the workspace and its local `.venv`. Delete the separate template download only when
you no longer need it to create or compare workspaces.

## Related

- [Folder-Agent-Workspace](README.md)
- [Runtime adapters](core/RUNTIMES.md)
- [Reflex hooks](core/hooks/README.md)
- [Memory](20_memory/README.md)
- [Workflows](60_workflows/README.md)
- [Tools](tools/README.md)
