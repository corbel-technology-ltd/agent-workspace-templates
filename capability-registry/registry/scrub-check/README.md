---
id: <<capability-registry_slug>>.registry.scrub-check
name: scrub-check - confidentiality gate (capability)
type: reference
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [capability, scrub, check]
related:
  - {ref: registry/README.md, dimension: where, polarity: derived_from}
---

# scrub-check (confidentiality gate)

Scans every git-tracked file of the target workspace - contents, frontmatter ids, and
filenames - for the terms in that workspace's `tools/scrub-terms.txt` (case-insensitive,
whole-word). Exit 1 on any hit. The proof that a copy carries no private terms before it is
shared onward.

Installing changes `tools/scrub-check.py` only; the terms file stays the workspace's own
(a Shared-Context store derives it from its boundaries file).

See `manifest.yml` for the exact files, targets, and checksums.

## Related

- [The stock - what a capability is](../README.md)
