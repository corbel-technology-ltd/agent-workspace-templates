---
id: <<store_slug>>.manifest
name: <<STORE_NAME>> store manifest
type: identity
layer: C0
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [manifest, shared-context, routing, store]
related:
  - {ref: SHARED.md, dimension: why, polarity: explains}
  - {ref: _meta/governance.md, dimension: how, polarity: requires}
---

# <<STORE_NAME>> - store manifest

You are inside a **shared-context store**, not a workspace. This store has no agent persona and no
task queue of its own; agents visit it from the workspaces on the
[roster](_coordination/roster.md). The constitution is [`SHARED.md`](SHARED.md) - read it first.
Per-runtime pointer files at this root are pinned adapters that defer to this manifest; on any
conflict, `SHARED.md` wins on doctrine and this file wins on routing.

## Route by intent

| You are here to | Do |
|---|---|
| Onboard a blank store (`.uninitialised` present) | Run the onboarding playbook: `core/onboarding/ONBOARDING.md`. Do nothing else first. |
| Consume the shared context for a workspace session | Follow [`SHARED.md`](SHARED.md) §link-in: constitution plus the three index READMEs, their current non-blank `always` set, relevant triggered files, then the dashboard. Read-only; leave. |
| Edit or add shared content | [`_meta/governance.md`](_meta/governance.md) first: scope test, CHANGES trailer, objection window, sign-off rules. |
| Register a new workspace | `python3 core/link-workspace.py --name <ws> --path </abs> --agent <name>` (see [`SHARED.md`](SHARED.md) §link-in). |
| Update handoffs / check what is owed | [`_coordination/dashboard.md`](_coordination/dashboard.md) (row updates are low-risk; structure changes are not). |
| Check the store's health before distributing | `tools/`: scrub-check, okf-check, agnostic-check, skill-surface-check, shared-lint - all must exit 0. |

## Hard rules

1. **No secrets.** Never write a credential, token, or key anywhere in this store.
2. **CHANGES.md is append-only.** New entries go on top, under the marker line. An entry's date,
   author, and summary are immutable; the only permitted edit to a past entry is its `window:`
   field flipping `open` -> `closed` once when the window lapses. A correction or objection is a
   new entry.
3. **The boundaries file is law.** Nothing listed in [`boundaries/`](boundaries/README.md) as
   never-share may appear in any artefact that leaves the principal's machines.
4. **Blank means blank.** Skeleton files earn content through calibration and governance, never
   through invention. Source-or-abstain applies to facts about the principal above all.

## Related

- [<<STORE_NAME>>](SHARED.md)
- [Governance - the full edit protocol](_meta/governance.md)
