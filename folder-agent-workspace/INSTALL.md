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

- **Python 3** - the `core/hooks/` reflexes and the onboarding `apply.py` run on the system
  `python3` (no virtualenv assumed).
- **PyYAML** - `pip install -r requirements.txt`. Used by the memory reaper hook and by the onboarding
  engine (which reads `placeholders.yml`).
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

1. On GitHub, click **Use this template** to create your own repository from Folder-Agent-Workspace, then clone it
   and open the folder in your agent runtime (see [`core/RUNTIMES.md`](core/RUNTIMES.md) for the
   wired adapters and for attaching any other).
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

Run the pre-distribution gates ([`tools/README.md`](tools/README.md)) - all three must exit `0`:

```bash
python3 tools/scrub-check.py      # zero in-house terms across contents, ids, filenames
python3 tools/okf-check.py        # OKF-compatible frontmatter + body-link mirroring
python3 tools/agnostic-check.py   # neutral core vendor-free, adapters thin pointers
```

## The family

Folder-Agent-Workspace is the workspace member of the FAW template family (siblings: **Shared-Context**, the
shared-context store `SHARED_CONTEXT_PATH` points at; **Capability-Registry**, the capability registry this
template's tools are stocked in). Composition and take-just-one-part paths: `FAMILY.md` at the
family repo root (`github.com/CORBEL-Technology/Agent-Workspace-Templates`).

## Related

- [<<WORKSPACE_NAME>>](AGENTS.md)
