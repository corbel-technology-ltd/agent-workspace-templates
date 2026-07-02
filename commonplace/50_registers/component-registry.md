---
id: <<workspace_slug>>.register.component-registry
name: Component registry — scripts, automations, alerts, APIs
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

Every durable **ops** moving part — script, automation/timer, alert, API/integration, hook — in one
catalogue, so we know **what it is, where it is, what triggers it, what it's for, and what it
touches**. This is a map over the existing layout (files are NOT moved; paths stay stable); on any
conflict the source file wins.

**Scope: the control plane that runs the workspace, not what the entity builds.** Self-contained
projects and apps are out of scope — they keep their own internal catalogue and are excluded from
this registry and the drift sensor. What belongs here: the ops dirs (`70_integrations/`,
`core/hooks/`, the runtime-adapter shims) and any future ops automation. If a project/app ever
needs cataloguing, it gets its own registry, not a row here.

## How to use it (splash-zone before you change anything)

1. **Changing component X?** Read its row's **touches** to see what your change will hit downstream.
2. **Reverse blast radius?** Grep this file for `X`'s path/name — any row that lists it under
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
| `core/hooks/session-brief.py` | hook | Inject boot orientation (who/focus/handover/stand-by) plus open decisions/loops at session start. | session start | `00_meta/staging.md`, `90_runs/` (newest handover), `80_projects/*/loops.md`, `50_registers/decision-queue.md` | active |
| `core/hooks/session-digest.py` | hook | Append a session-end digest journal entry. | session end | `20_memory/journal/` | active |
| `core/hooks/reaper.py` | hook | Deterministic memory reaper: fold/compress atoms, write the build marker. | session end | `20_memory/journal/`, atoms, `_meta/build.md` | active |
| `core/hooks/onboarding-gate.py` | hook | If `.uninitialised` is present, prompt the agent to run the onboarding playbook before any other work; silent once onboarded. | session start | `.uninitialised` sentinel | active |
| `core/hooks/registry-drift.py` | hook | This registry's drift sensor: flag any component not catalogued here. | session end (wiring optional), manual | this file, repo file tree | active |
| `core/git-hooks/pre-commit` | hook | Optional commit-time backstop for journal immutability (works with any runtime). | git commit, once installed per clone | `20_memory/journal/` staged changes | dormant |

The per-runtime shims (each wired runtime's config dir routes its hook events to `core/hooks/`)
are catalogued with their adapters in `core/RUNTIMES.md`, not here - this registry stays neutral.

<!-- Add a section per component cluster as it is wired (e.g. "## Executor", "## Email pipeline",
     "## Automations — timers & services", "## CRM store"). Row shape as above. -->

## Related

- [Integrations — what-runs-where map (instance-specific slots)](../70_integrations/README.md)
- [<<WORKSPACE_NAME>>](../AGENTS.md)
