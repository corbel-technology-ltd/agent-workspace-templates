---
id: <<capability-registry_slug>>.manifest
name: <<CHANDLERY_NAME>>
type: identity
layer: C0
status: current
owner: shared
spec_version: 0.1
initialised: false
created: <<CREATED_DATE>>
updated: <<CREATED_DATE>>
tags: [capability-registry, registry, capabilities, parity, manifest]
related:
  - {ref: registry/README.md, dimension: what, polarity: enables}
  - {ref: ledger.md, dimension: how, polarity: enables}
---

# <<CHANDLERY_NAME>> - capability registry manifest

You are inside a **capability-registry**: the stocked store a fleet of agent workspaces fits out from, and
the ledger that makes drift between them visible. It holds **capabilities** - deterministic
plumbing (gate scripts, hooks, engines, schemas, workflow specs) packaged as plain files with
versioned, checksummed manifests. It does not hold knowledge, canon, preferences, or secrets;
those belong to workspaces and to the shared-context store.

Built from **Capability-Registry**, the registry member of the FAW template family. Owner: <<OWNER>>.

## The flow (and where the human sits)

`improve (in a workspace) -> pack (version bump + ledger) -> install (into each sibling, gated) ->
status (drift visible again)`

Everything is `python3 core/chandler.py <command>` - deterministic, local files only, no network:

| Intent | Command |
|---|---|
| What is stocked | `list` |
| Registry self-check (the gate) | `verify` |
| Is a workspace in sync | `status --workspace <path>` |
| What exactly differs | `diff <name> --workspace <path>` |
| Adopt registry -> workspace | `install <name> --workspace <path>` (needs `--yes` to overwrite local difference) |
| Flow an improvement back | `pack <name> --from-workspace <path> --yes [--write-ledger]` |
| Whole-fleet drift report | `fleet` |
| Add a workspace to the fleet | `enrol --name <ws> --path </abs>` |

## Hard rules

1. **Install is an operator decision.** The chandler never runs unattended and never overwrites a
   differing workspace file without an explicit `--yes`. Adopting a capability into a workspace is
   that workspace operator's call, made at that workspace's own gate.
2. **A registry payload is never edited in place.** `verify` fails on a checksum mismatch by
   design: the only way content changes is `pack`, which bumps the version and leaves a ledger
   line. History is append-only ([`ledger.md`](ledger.md)); git is the tamper-evidence.
3. **Versions are integers and only go up.** No semver theatre for plain files; "newer" must be
   trivially decidable.
4. **Scope is plumbing, not brain.** A capability is something a workspace *runs or fills in*
   (script, hook, gate, engine, schema, template, workflow spec). Facts about the principal go to
   the shared-context store; workspace content stays home. Never a secret, anywhere.
5. **Drift is a report, not a sin.** A workspace may deliberately diverge; `status` makes the
   divergence visible so it is a decision. The fix for wanted divergence is a fork under a new
   capability name, not a silently drifted copy.

## Onboarding

Blank template, not yet initialised: the `.uninitialised` sentinel routes a fresh agent to
[`core/onboarding/ONBOARDING.md`](core/onboarding/ONBOARDING.md) (four tokens, deterministic
fill). Per-runtime pointer files at this root are pinned adapters that defer to this manifest.

## Related

- [The stock - what a capability is](registry/README.md)
- [Registry ledger](ledger.md)
