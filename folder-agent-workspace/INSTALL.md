---
id: <<workspace_slug>>.install
name: Install & onboarding
type: doc
layer: C0
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [install, onboarding, setup, requirements, agent-scope]
related:
  - {ref: AGENTS.md, dimension: why, polarity: derived_from}
---

# Install & onboarding

**Folder-Agent-Workspace**: a blank, client-shareable folder-based agent workspace, a founder control plane you
onboard once and run. This file covers requirements, the first run, and the honest agent scope.

## Requirements

- **Python 3.8+** - the `core/hooks/` reflexes and onboarding engine run with `python3`.
- **PyYAML** - used by the memory reaper and onboarding engine. The family-root installer first
  tries the user package location; if PEP 668 protects system Python, it creates `.venv` inside the
  workspace and prints the activation command. For a direct template clone, run
  `python3 -m venv .venv`, `. .venv/bin/activate`, then `python -m pip install -r requirements.txt`.
- **git** - the workspace is a git repo; onboarding discovers and snapshots files via `git ls-files`,
  and the per-folder loop/journal discipline assumes version control.

## Runtime / agent scope (honest)

**Neutral core, thin adapters.** All the IP - the constitution, doctrine, schemas, templates,
registers, AND every executable (reflex hooks, onboarding engine, gates) - lives in neutral
locations (`AGENTS.md`, the numbered folders, `core/`, `tools/`). A runtime attaches through a
thin adapter: a pinned pointer file at the root plus that runtime's config dir, translation and
wiring only. Two adapters ship (one fully hook-wired, one a pointer); [`core/RUNTIMES.md`](core/RUNTIMES.md)
documents them and wires a new runtime in about 15 minutes. A runtime with no hook system still gets the full
workspace plus a git-level journal guard (`core/git-hooks/pre-commit`); it loses only the automatic
session reflexes, and `core/RUNTIMES.md` says so. The gate `tools/agnostic-check.py` fails the
build if an adapter grows content or a vendor name leaks into the neutral core.

## First run (onboarding)

1. Prefer the family-root `install.sh`. For a direct template copy, create/activate `.venv` as
   above, then open the folder in your agent runtime (see [`core/RUNTIMES.md`](core/RUNTIMES.md) for
   the wired adapters and for attaching any other).
2. The [`.uninitialised`](.uninitialised) sentinel + the session-start gate
   ([`core/hooks/onboarding-gate.py`](core/hooks/onboarding-gate.py)) prompt the agent to run the
   **onboarding** playbook ([`core/onboarding/ONBOARDING.md`](core/onboarding/ONBOARDING.md))
   before anything else.
3. The playbook interviews you for the workspace identity (name, entity, owner, agent name, root-env,
   and the optional shared-context path), then runs
   [`apply.py`](core/onboarding/apply.py) to fill every `<<TOKEN>>` placeholder
   deterministically (with a pre-flight snapshot, validation, and a `--dry-run` preview), seeds the
   registers, writes the first journal entry, and removes the sentinel.
4. You're live. The runtime `{{...}}` markers (e.g. `{{YYYY-MM-DD}}`) are intentional and are filled
   per-artefact as you work - they are not onboarding tokens.

## Before distributing your own copy

Run the canonical extraction-safe distribution checks in
[`tools/README.md`](tools/README.md). Every command in that section must exit `0`; the separately
listed updater maintenance proof requires a template-family checkout.

## The family

Folder-Agent-Workspace is the workspace member of the FAW template family (siblings: **Shared-Context**, the
shared-context store `SHARED_CONTEXT_PATH` points at; **Capability-Registry**, the capability registry this
template's tools are stocked in). Composition and take-just-one-part paths: `FAMILY.md` at the
family repo root (`github.com/corbel-technology-ltd/agent-workspace-templates`).

## Related

- [<<WORKSPACE_NAME>>](AGENTS.md)
