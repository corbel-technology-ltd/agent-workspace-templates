---
id: <<chandlery_slug>>.registry.gen-related
name: gen-related - maintenance tool (capability)
type: reference
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [capability, gen, related]
related:
  - {ref: registry/README.md, dimension: where, polarity: derived_from}
---

# gen-related (maintenance tool)

Regenerates each concept file's `## Related` body section from its frontmatter `related:`
edges (title from the target's `name:` or H1). Idempotent; `--check` reports without writing
(exit 1 if anything would change) for CI. The maintenance half of the okf-check contract.

See `manifest.yml` for the exact files, targets, and checksums.

## Related

- [The stock - what a capability is](../README.md)
