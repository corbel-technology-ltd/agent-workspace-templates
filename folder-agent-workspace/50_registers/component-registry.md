---
id: <<workspace_slug>>.register.component-registry
name: Component registry - scripts, automations, alerts, APIs
type: register
layer: C1
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [register, components, scripts, automations, alerts, apis, hooks, splash-zone, audit]
related:
  - {ref: 70_integrations/README.md, dimension: where, polarity: complements}
  - {ref: AGENTS.md, dimension: why, polarity: derived_from}
---

# Component registry

Every durable **ops** moving part - script, automation/timer, alert, API/integration, hook - in one
catalogue, so we know **what it is, where it is, what triggers it, what it's for, and what it
touches**. This is a map over the existing layout (files are NOT moved; paths stay stable); on any
conflict the source file wins.

**Scope: the control plane that runs the workspace, not what the entity builds.** Self-contained
projects and apps are out of scope - they keep their own internal catalogue and are excluded from
this registry and the drift sensor. What belongs here: the ops dirs (`70_integrations/`,
`core/hooks/`, the runtime-adapter shims) and any future ops automation. If a project/app ever
needs cataloguing, it gets its own registry, not a row here.

## How to use it (splash-zone before you change anything)

1. **Changing component X?** Read its row's **touches** to see what your change will hit downstream.
2. **Reverse blast radius?** Grep this file for `X`'s path/name - any row that lists it under
   **triggered by** or **touches** depends on it, so it's in the splash zone.
3. **Auditing for improvement?** Scan a section; `dormant`/`deprecated` rows are removal candidates,
   repeated **touches** reveal coupling worth simplifying.

## Keeping it current (a registry that rots is worse than none)

- **Definition-of-done:** adding or changing a component **updates its row here** in the same change.
- **Drift sensor:** [`core/hooks/registry-drift.py`](../core/hooks/registry-drift.py) walks the
  repo for components and flags any path missing from this file (advisory, never blocks). Run by hand
  (`python3 core/hooks/registry-drift.py`) or via a session-end hook.
- Deeper detail for a cluster lives in its own doc (linked in **touches**), not duplicated here.

`kind`: script · automation (timer/cron) · alert · api (integration) · hook · service.
`status`: active · dormant (built, not enabled) · deprecated.

## Agent-OS hooks (`core/hooks/`, wired per runtime)

The reflex hooks that ship with the template. Logic lives in `core/hooks/`; each wired runtime
routes its events through a thin shim in its own config dir (see `core/RUNTIMES.md`). Other
sections (executor, integrations, automations) are added per instance as those components are wired.

| component | kind | purpose (what + why) | triggered by | touches (splash zone) | status |
|---|---|---|---|---|---|
| `core/hooks/journal-guard.py` | hook | Block edits/deletes of journal entries (immutability reflex). | pre-tool-use, via the runtime adapter | `20_memory/journal/` write attempts | active |
| `core/hooks/session-brief.py` | hook | Inject the safely selected Shared always set before local orientation, then focus/handover/stand-by, open decisions/loops, and offline maintenance nudges. | session start | configured Shared `SHARED.md`, identity/operating-rules/boundaries Markdown (read-only, no external execution), `00_meta/staging.md`, `90_runs/`, project loops, decision queue, template-check state | active |
| `core/hooks/session-digest.py` | hook | Append a session-end digest journal entry. | session end | `20_memory/journal/` | active |
| `core/hooks/reaper.py` | hook | Deterministic memory reaper: validity/supersession/quarantine plus ACT-R tiering — hysteresis layer moves, working-set budget, long-term archive clock; writes the build marker. | session end | `20_memory/journal/`, atoms, `_meta/build.md` | active |
| `core/hooks/sleep-prep.py` | tool | Sleep pass stage 1 (deterministic): stage unconsolidated journal entries, entity recurrence + co-occurrence, known-entity universe. | memory-sleep skill, manual | `20_memory/journal/`, `_meta/sleep-candidates.json` | active |
| `core/hooks/sleep-apply.py` | tool | Sleep pass stage 2 (deterministic validator + writer): bind claims to the staged window, reject unsupported/invented claims, merge repeat evidence, write accepted atoms + subconscious outputs, advance the processed set, run the reaper. | memory-sleep skill, manual | depth layers, `subconscious/`, `_meta/sleep-*.{json,md}` | active |
| memory-sleep skill (runtime adapter layer; see `core/RUNTIMES.md`) | skill | Deep bounded synthesis when due or requested; routine work uses the deterministic reaper fast path and validator failure stops before durable writes. | brief nudge, user request | `60_workflows/memory-reaper.md`, `60_workflows/memory-sleep.md`, `_meta/sleep-claims.json` | active |
| `tools/recall-tiered.py` | tool | Depth-ordered memory search: working -> short-term -> long-term -> subconscious (PRIMING) -> archive (EXPIRED) -> journal (raw truth); stops at first answering depth; --follow walks related: edges one hop; --touch feeds retrievals into ACT-R activation and REELS archive hits back to short-term. | manual, any retrieval need | read-only over `20_memory/` (--touch updates touches/retrieval_count) | active |
| `tools/memory-selftest.py` | tool | End-to-end memory-loop proof (synthesis, rejection classes, promotion, hysteresis, expiry, quarantine, idempotency); runs as a family-check gate. | family check, manual | temp dir only | active |
| `tools/template-update.py` | tool | Safely apply repeated updates with canonical manifest keys, pending-review authority, verified fills/candidates, write-all atomic replacement, path containment, and preflighted legacy migration. | template-update playbook, manual | prefix-managed spine, exact-managed doctrine/meta files, `00_meta/template-origin.json`, `20_memory/_meta/template-check.json`, user cache | active |
| `tools/template_paths.py` | tool | Define the managed spine with bounded prefixes plus exact doctrine/meta exceptions. | origin stamping, template update | files eligible for managed propagation | active |
| `tools/update-selftest.py` | tool | Prove repeated cycles, exact-file propagation, update authority and atomicity, plus Shared lifecycle selection, fallback, path containment and non-execution. | family gate, manual | temp git repositories and synthetic Shared store only | active |
| `tools/decomposition-check.py` | tool | Enforce prose/code ceilings, concept-note hygiene and live reasoned exceptions. | family gate, manual | tracked member tree, `tools/decomposition-exceptions.txt` | active |
| `tools/decomposition-selftest.py` | tool | Prove ceilings, structural exemptions, concept ownership and exception hygiene in disposable repositories. | family gate, manual | temp directories only | active |
| `tools/skill-surface-check.py` | tool | Enforce skill discovery metadata, adapter-local name uniqueness, neutral playbook links and thin pointers. | family gate, manual | tracked runtime skill surfaces and linked neutral playbooks | active |
| template-update skill (runtime adapter layer; see `core/RUNTIMES.md`) | skill | Live-instance pointer requiring origin validation; preserves local differences for manual candidate review instead of force-overwriting. | session nudge, user request | `60_workflows/template-update.md`, `00_meta/template-origin.json`, managed spine | active |
| onboarding skill (runtime adapter layer; see `core/RUNTIMES.md`) | skill | Fresh-workspace pointer to the neutral validated onboarding playbook; stops when the sentinel is absent or validation fails. | `.uninitialised` present | `core/onboarding/ONBOARDING.md`, onboarding values and sentinel | active |
| `core/hooks/onboarding-gate.py` | hook | If `.uninitialised` is present, direct the agent through the staged interview, root values file, atomic apply, first state/journal seed, and sentinel-last completion; silent once onboarded. | session start | `.uninitialised` sentinel, `core/onboarding/ONBOARDING.md` | active |
| `core/onboarding/apply.py` | tool | Validate root `values.json`, recover any interrupted snapshot, fill registered tokens atomically, prove zero leftovers, and make a completed rerun a no-op. | onboarding playbook, manual recovery | git-tracked tree, `values.json`, `.onboarding_apply*` transients | active |
| `core/hooks/registry-drift.py` | hook | This registry's drift sensor: flag any component not catalogued here. | session end (wiring optional), manual | this file, repo file tree | active |
| `core/git-hooks/pre-commit` | hook | Optional commit-time backstop for journal immutability (works with any runtime). | git commit, once installed per clone | `20_memory/journal/` staged changes | dormant |

The per-runtime shims (each wired runtime's config dir routes its hook events to `core/hooks/`)
are catalogued with their adapters in `core/RUNTIMES.md`, not here - this registry stays neutral.

<!-- Add a section per component cluster as it is wired (e.g. "## Executor", "## Email pipeline",
     "## Automations - timers & services", "## CRM store"). Row shape as above. -->

## Related

- [Integrations - what-runs-where map (instance-specific slots)](../70_integrations/README.md)
- [<<WORKSPACE_NAME>>](../AGENTS.md)
