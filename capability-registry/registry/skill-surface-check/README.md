---
id: <<capability-registry_slug>>.registry.skill-surface-check
name: skill-surface-check - runtime skill discovery gate
type: reference
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [capability, skill, discovery, pointer, check]
related:
  - {ref: registry/README.md, dimension: where, polarity: derived_from}
---

# skill-surface-check

Discovers tracked `*/skills/*/SKILL.md` files and validates their discovery metadata, adapter-local
name uniqueness, neutral playbook links, and thin-pointer shape. It rejects links into adapter
surfaces and catches procedure-heavy pointers through the family's existing 30-line convention,
second-level-heading ban, and code-fence ban.

The gate is deliberately structural. A human still reviews whether a description is genuinely
discriminative and whether pointer prose semantically duplicates its neutral playbook. Run
`python3 tools/skill-surface-check.py --self-test` for its disposable fixture proof.

See `manifest.yml` for the exact payload, target, and checksum.

## Related

- [The stock - what a capability is](../README.md)
