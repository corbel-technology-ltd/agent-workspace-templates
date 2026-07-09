---
id: <<capability-registry_slug>>.registry.agnostic-check
name: agnostic-check - agent-agnostic gate (capability)
type: reference
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [capability, agnostic, check]
related:
  - {ref: registry/README.md, dimension: where, polarity: derived_from}
---

# agnostic-check (agent-agnostic gate)

Enforces the family's Law: no vendor/runtime term outside the adapter layer and its
sanctioned registry, and every adapter pointer file stays a thin pointer (line cap, defers to
the constitution, no content sections). Exit 1 on any violation. What makes "no behaviour
depends on a specific vendor" checkable instead of aspirational.

See `manifest.yml` for the exact files, targets, and checksums.

## Related

- [The stock - what a capability is](../README.md)
