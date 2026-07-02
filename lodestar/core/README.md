---
id: core.readme
name: Neutral core - the runtime-agnostic machinery
type: reference
layer: C0
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [core, neutral, runtime, adapters, hooks, onboarding, link-in, agent-agnostic]
related:
  - {ref: AGENTS.md, dimension: why, polarity: explains}
  - {ref: core/RUNTIMES.md, dimension: how, polarity: enables}
---

# Neutral core

Every piece of executable machinery in this store, in one runtime-agnostic place. Nothing here
knows which agent runtime is visiting - that is the point. The constitution
([`SHARED.md`](../SHARED.md)) holds the doctrine; this folder holds the plumbing; thin per-runtime
adapters wire the two into whatever runtime is used.

## What lives here

- [`hooks/`](hooks/onboarding-gate.py) - the two store reflexes: `onboarding-gate.py` (route a
  fresh agent to onboarding while the sentinel exists) and `store-brief.py` (surface open
  objection windows, open handoffs, and the roster at session start; silent when clean).
- [`onboarding/`](onboarding/ONBOARDING.md) - the instantiation playbook, the token registry
  (`placeholders.yml`, six tokens), and the deterministic substitution engine (`apply.py` -
  byte-identical to its siblings across the family; its tests live upstream with Commonplace).
- [`link-workspace.py`](link-workspace.py) - the executable half of the link-in contract: roster
  registration, the boot rule, the ledger trailer.
- [`derive-scrub.py`](derive-scrub.py) - generates scrub denylists from the boundaries
  never-share list, so the confidentiality line is written once and enforced mechanically.
- [`RUNTIMES.md`](RUNTIMES.md) - the adapter contract and wiring guide; the ONE sanctioned place
  where runtime/vendor specifics are documented.

## The rule that keeps this honest

Adapters point; the core does. A per-runtime file may translate and wire, never carry policy or
logic. `tools/agnostic-check.py` fails the build if an adapter grows content or a vendor name
leaks into the neutral core.

## Related

- [<<STORE_NAME>> store manifest](../AGENTS.md)
- [Runtime adapters - the contract and the wiring guide](RUNTIMES.md)
