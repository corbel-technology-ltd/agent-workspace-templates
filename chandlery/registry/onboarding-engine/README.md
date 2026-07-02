---
id: <<chandlery_slug>>.registry.onboarding-engine
name: onboarding-engine - engine (capability)
type: reference
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [capability, onboarding, engine]
related:
  - {ref: registry/README.md, dimension: where, polarity: derived_from}
---

# onboarding-engine (engine)

The deterministic substitution engine behind every family template's onboarding: reads the
workspace's `placeholders.yml` registry + a confirmed `values.json`, validates every value,
snapshots the tracked tree, fills each `<<TOKEN>>` with context-aware escaping (.py / .json /
YAML-frontmatter / prose), validates zero leftovers, and cleans up - atomic, idempotent, with
`--dry-run` preview. Requires PyYAML. Its test suite lives at its upstream home (the
Commonplace template, `core/onboarding/tests/`).

See `manifest.yml` for the exact files, targets, and checksums.

## Related

- [The stock - what a capability is](../README.md)
