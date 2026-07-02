---
id: <<chandlery_slug>>.registry.okf-check
name: okf-check - structural gate (capability)
type: reference
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [capability, okf, check]
related:
  - {ref: registry/README.md, dimension: where, polarity: derived_from}
---

# okf-check (structural gate)

Verifies OKF-compatible frontmatter across the target workspace's tracked Markdown: `type`
present, every `related[].ref` existing and mirrored as an inline body link, `index.md`
reserved. Exit 1 on any violation. Pairs with `gen-related`, which keeps the mirrors green
deterministically.

See `manifest.yml` for the exact files, targets, and checksums.

## Related

- [The stock - what a capability is](../README.md)
