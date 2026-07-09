---
id: <<capability-registry_slug>>.install
name: Install & onboarding
type: doc
layer: C0
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [install, onboarding, setup, requirements, fleet]
related:
  - {ref: AGENTS.md, dimension: why, polarity: derived_from}
---

# Install & onboarding

**Capability-Registry**: a blank, shareable capability registry for a fleet of agent workspaces. This file
covers requirements, the first run, and stocking.

## Requirements

- **Python 3** - the engine, hooks, and gates run on the system `python3` (no virtualenv assumed).
- **PyYAML** - `pip install -r requirements.txt`. Used by `core/chandler.py` (manifests,
  lockfiles, the fleet file) and the onboarding engine.
- **git** - the registry is a git repo; the gates scan the tracked tree and the append-only
  ledger leans on git as tamper-evidence.

## Runtime / agent scope

**Neutral core, thin adapters** - same law as the whole family. The engine is a CLI any agent (or
human) runs by hand; the only session wiring is the onboarding gate while blank. Adapters and the
wiring guide: [`core/RUNTIMES.md`](core/RUNTIMES.md).

## First run (onboarding)

1. Create your repo from the template, clone it, open it in your agent runtime.
2. The [`.uninitialised`](.uninitialised) sentinel + the session-start gate route the agent to the
   **onboarding** playbook ([`core/onboarding/ONBOARDING.md`](core/onboarding/ONBOARDING.md)):
   four tokens (capability-registry name, owner, slug, date), deterministic fill, first ledger entry.
3. Enrol your workspaces and check the stock:

   ```bash
   python3 core/chandler.py enrol --name Acme --path /home/you/acme-workspace
   python3 core/chandler.py fleet
   python3 core/chandler.py install scrub-check --workspace /home/you/acme-workspace
   ```

## Stocking your own capabilities

A capability is a folder under `registry/<name>/`: payload under `files/`, plus a `manifest.yml`
(`name`, integer `version`, `description`, `provenance`, `requires`, and per-file
`src`/`target`/`sha256`). Copy an existing capability as the pattern, then `verify` until green.
The easiest path: build the thing inside a workspace first, prove it there, then `pack` it in.

## Before distributing your own copy

Populate `tools/scrub-terms.txt` (your fleet's private names do not belong in a shared registry),
then run the gates - all four must exit `0`:

```bash
python3 tools/scrub-check.py
python3 tools/okf-check.py
python3 tools/agnostic-check.py
python3 core/chandler.py verify
```

## The family

Capability-Registry is the registry member of the FAW template family (siblings: **Folder-Agent-Workspace**, the
workspace the fleet is made of; **Shared-Context**, the shared-context store whose roster the fleet
report cross-checks). Composition and take-just-one-part paths: `FAMILY.md` at the family repo
root (`github.com/CORBEL-Technology/Agent-Workspace-Templates`).

## Related

- [<<CHANDLERY_NAME>>](AGENTS.md)
