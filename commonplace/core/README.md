---
id: core.readme
name: Neutral core - the runtime-agnostic machinery
type: reference
layer: C0
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [core, neutral, runtime, adapters, hooks, onboarding, agent-agnostic]
related:
  - {ref: AGENTS.md, dimension: why, polarity: explains}
  - {ref: core/RUNTIMES.md, dimension: how, polarity: enables}
---

# Neutral core

Every piece of executable machinery in this workspace, in one runtime-agnostic place. Nothing in
this folder knows or cares which agent runtime is driving the workspace - that is the point. The
constitution ([`AGENTS.md`](../AGENTS.md)) holds the judgment; this folder holds the plumbing; thin
per-runtime adapters wire the two into whatever runtime you use.

## What lives here

- [`hooks/`](hooks/README.md) - the reflexes (journal immutability guard, onboarding gate, session
  brief, session digest, memory reaper, registry-drift sensor). Standalone `python3` scripts with a
  documented stdin/stdout/exit-code contract.
- [`onboarding/`](onboarding/ONBOARDING.md) - the instantiation playbook, the token registry
  (`placeholders.yml`), the deterministic substitution engine (`apply.py`), and its tests.
- [`git-hooks/`](git-hooks/) - optional, runtime-independent enforcement. `pre-commit` refuses any
  commit that modifies or deletes an existing journal entry, so the append-only invariant holds
  even for an agent runtime with no hook system at all.
- [`RUNTIMES.md`](RUNTIMES.md) - the adapter contract and the "wire a new runtime in 15 minutes"
  guide. The ONE sanctioned place where runtime/vendor specifics are documented.

## The rule that keeps this honest

Adapters point; the core does. A per-runtime file (a root pointer file, a shim, a settings file)
may translate and wire, but it may not carry policy, playbook content, or logic of its own.
`tools/agnostic-check.py` fails the build if an adapter grows content or if runtime-specific
assumptions leak into the neutral core.

## Related

- [<<WORKSPACE_NAME>>](../AGENTS.md)
- [Runtime adapters - the contract and the 15-minute wiring guide](RUNTIMES.md)
