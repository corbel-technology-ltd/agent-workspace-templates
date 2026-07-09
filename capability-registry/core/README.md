---
id: core.readme
name: Neutral core - the runtime-agnostic machinery
type: reference
layer: C0
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [core, neutral, runtime, adapters, chandler, onboarding, agent-agnostic]
related:
  - {ref: AGENTS.md, dimension: why, polarity: explains}
  - {ref: core/RUNTIMES.md, dimension: how, polarity: enables}
---

# Neutral core

Every piece of executable machinery in this registry, runtime-agnostic. The constitution
([`AGENTS.md`](../AGENTS.md)) holds the rules; this folder holds the plumbing; thin per-runtime
adapters wire the two into whatever runtime is used.

- [`chandler.py`](chandler.py) - the engine: `list`, `verify`, `status`, `diff`, `install`,
  `pack`, `fleet`, `enrol`. Deterministic, local files only, human at every gate.
- [`onboarding/`](onboarding/ONBOARDING.md) - the instantiation playbook, the token registry
  (four tokens), and the substitution engine (`apply.py` - byte-identical across the family; it
  is also stocked as the `onboarding-engine` capability, and its tests live upstream with
  Folder-Agent-Workspace).
- [`hooks/`](hooks/onboarding-gate.py) - the single reflex a registry needs: the onboarding gate
  while the sentinel exists.
- [`RUNTIMES.md`](RUNTIMES.md) - the adapter contract and wiring guide; the ONE sanctioned place
  where runtime/vendor specifics are documented.

Adapters point; the core does. `tools/agnostic-check.py` fails the build if an adapter grows
content or a vendor name leaks into the neutral core.

## Related

- [<<CHANDLERY_NAME>>](../AGENTS.md)
- [Runtime adapters - the contract and the wiring guide](RUNTIMES.md)
