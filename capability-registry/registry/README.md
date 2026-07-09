---
id: <<capability-registry_slug>>.registry.readme
name: The stock - what a capability is
type: reference
layer: C0
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [registry, capabilities, manifest, checksums, stock]
related:
  - {ref: AGENTS.md, dimension: why, polarity: derived_from}
  - {ref: ledger.md, dimension: how, polarity: complements}
---

# The stock

One folder per **capability**. Each holds:

- `manifest.yml` - `name` (matches the folder), integer `version` (only goes up),
  `description`, `provenance` (where it came from / where its tests live), `requires`
  (runtime deps, e.g. PyYAML), and `files:` - each with `src` (path inside this folder),
  `target` (path inside a workspace), and `sha256` (of the payload).
- `files/` - the payload, byte-exact.
- `README.md` - what it does, what it needs, what installing changes.

The contract, enforced by `python3 core/chandler.py verify`: **payloads match their manifests,
always**. Editing a payload in place breaks `verify` on purpose - content only changes through
`pack`, which bumps the version and leaves a [`ledger.md`](../ledger.md) line.

What qualifies as a capability: deterministic plumbing a workspace *runs or fills in* - gate
scripts, hooks, engines, schemas, templates, workflow specs. What never does: knowledge, canon,
preferences, credentials (see the scope rule in [`AGENTS.md`](../AGENTS.md)).

## Seed stock

The FAW family's own shared tools ship stocked: `scrub-check`, `okf-check`, `gen-related`,
`agnostic-check`, `onboarding-engine`. Their upstream home (and tests) is the Folder-Agent-Workspace
workspace template; the family repo verifies every sibling's vendored copies against the
checksums here.

## Related

- [<<CHANDLERY_NAME>>](../AGENTS.md)
- [Registry ledger](../ledger.md)
