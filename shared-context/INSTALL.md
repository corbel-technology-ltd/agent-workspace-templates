---
id: <<store_slug>>.install
name: Install & onboarding
type: doc
layer: C0
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [install, onboarding, setup, requirements, link-in]
related:
  - {ref: SHARED.md, dimension: why, polarity: derived_from}
---

# Install & onboarding

**Shared-Context**: a blank, shareable shared-context store - the constitution that sits above every
workspace a principal runs. This file covers requirements, the first run, and linking workspaces in.

## Requirements

- **Python 3** - the `core/` machinery and the `tools/` gates run on the system `python3` (no
  virtualenv assumed).
- **PyYAML** - `pip install -r requirements.txt`. Used by the onboarding engine (which reads
  `placeholders.yml`).
- **git** - the store is a git repo; onboarding discovers files via `git ls-files`, the gates scan
  the tracked tree, and the append-only ledger leans on git as tamper-evidence.

## Runtime / agent scope

**Neutral core, thin adapters** - same law as the whole family. The constitution, folders, and all
machinery are runtime-neutral; runtimes attach through pinned pointer files plus a config dir
(wiring documented in [`core/RUNTIMES.md`](core/RUNTIMES.md)). A store needs far less wiring than
a workspace: one session-start gate while blank, one session-start brief once live. Any
file-reading agent can consume the store with no wiring at all.

## First run (onboarding)

1. Create your repo from the template, clone it, open it in your agent runtime.
2. The [`.uninitialised`](.uninitialised) sentinel + the session-start gate
   ([`core/hooks/onboarding-gate.py`](core/hooks/onboarding-gate.py)) route the agent to the
   **onboarding** playbook ([`core/onboarding/ONBOARDING.md`](core/onboarding/ONBOARDING.md)).
3. The playbook asks for the store identity (store name, principal name, objection-window hours,
   file cap), then runs [`apply.py`](core/onboarding/apply.py) to fill every `<<TOKEN>>`
   placeholder deterministically (snapshot, validation, `--dry-run` preview available), writes the
   first ledger entry in `CHANGES.md`, and removes the sentinel.
4. You're live - but **blank**. Content arrives two ways, and only two ways:
   - **calibration** - staged interviews and confirmed corrections fill `identity/`,
     `calibration-os/`, `boundaries/`, `glossary/`;
   - **governed edits** - agents propose files through the protocol in
     [`_meta/governance.md`](_meta/governance.md).

## Link a workspace in

```bash
python3 core/link-workspace.py --name Acme --path /home/you/acme-workspace --agent aster
```

Registers the workspace on the roster, offers the ledger line for `CHANGES.md`, and prints the
boot rule to paste into that workspace's constitution. A Folder-Agent-Workspace workspace needs no paste -
its onboarding asks for the shared-context path and its session brief already loads the store.
Full contract: [`SHARED.md`](SHARED.md) §link-in.

## Before distributing your own copy

**A live store is not distributable as-is** - `boundaries/` and its derived denylist both hold your
private terms. Distribute the blank template, or genericise `boundaries/boundaries.md` first. The
scrub gate is the check: a live store *fails* it (via the boundaries file), and green means "safe
to share". The derived `tools/scrub-terms.txt` is gitignored (regenerate it locally with
`python3 core/derive-scrub.py --write`), so the denylist itself never ships.

Run the gates ([`tools/README.md`](tools/README.md)) - all four must exit `0` on a genericised copy:

```bash
python3 tools/scrub-check.py
python3 tools/okf-check.py
python3 tools/agnostic-check.py
python3 tools/shared-lint.py
```

## The family

Shared-Context is the shared-context member of the FAW template family (siblings: **Folder-Agent-Workspace**, the
workspace that links in at onboarding; **Capability-Registry**, the capability registry whose fleet report
cross-checks this store's roster). Composition and take-just-one-part paths: `FAMILY.md` at the
family repo root (`github.com/CORBEL-Technology/Agent-Workspace-Templates`).

## Related

- [<<STORE_NAME>>](SHARED.md)
