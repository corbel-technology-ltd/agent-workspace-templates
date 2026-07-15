# The FAW family

Three templates, one pattern: the **Filesystem Agent Workspace** (FAW) - run your work as plain
Markdown and git that an AI agent operates and a human stays in front of. No app, no database, no
vendor. Each member is independently useful; together they cover the three surfaces every serious
agent estate grows: the workspace, the shared brain, and the supply chain between them.

| Member | Is | One-liner |
|---|---|---|
| **Folder-Agent-Workspace** (`folder-agent-workspace/`) | the workspace | A folder-based agent workspace: constitution, doctrine, append-only journal + decaying memory, registers, workflows, and a safety gate that keeps authority human. |
| **Shared-Context** (`shared-context/`) | the shared context | The store above every workspace: who the principal is, how their agents behave, the environment they share - governed by ledger + objection windows, and outranking anything local. |
| **Capability-Registry** (`capability-registry/`) | the capability registry | The outfitter for the fleet: versioned, checksummed capabilities (gates, hooks, engines) that install into workspaces, flow improvements back, and make drift visible. |

## How they compose

One principal, one Shared-Context, many Folder-Agent-Workspace workspaces, one Capability-Registry:

```text
                       Shared-Context  (the star they steer by)
                      /    |    \        identity · rules · calibration · boundaries
        link-in      /     |     \       CHANGES ledger · objection windows · roster
                    /      |      \
         Folder-Agent-Workspace  Folder-Agent-Workspace  Folder-Agent-Workspace     (the vessels)
                    \      |      /
        install/pack \     |     /       capabilities · versions · checksums
                      \    |    /        fleet drift report · append-only ledger
                       Capability-Registry  (where they fit out)
```

- A workspace **links into** Shared-Context at onboarding (`SHARED_CONTEXT_PATH`); the store's roster
  records it, its session brief loads the shared brain first, and "shared outranks local" keeps
  every sibling calibrated identically.
- A workspace **fits out from** the Capability-Registry: `install` adopts a capability (operator-gated),
  `pack` flows a local improvement back (version bump + ledger), `fleet` shows who has drifted.
- Shared-Context and Capability-Registry **compose without coupling**: point the Capability-Registry's `fleet.yml` at the
  store and the fleet report cross-checks the roster; adoption *rules* live in the store's
  `operating-rules/`, the *mechanism* they govern lives in the Capability-Registry.

## Take just one part

Each member folder is self-contained (own LICENSE, gates, install guide, onboarding). From this
repo: `python3 instantiate.py <folder-agent-workspace|shared-context|capability-registry> <dest>` copies one out and
`git init`s it - or copy the folder by hand and `git init` yourself. Nothing in a member reaches
into a sibling by relative path.

The family gate proves this after delivery: `tools/instantiate-selftest.py` makes fresh standalone
copies, preserves their blank onboarding state, and runs every extraction-safe member gate. Tests
that intentionally exercise family-root machinery continue to run against the family checkout.

- **Only a workspace?** Take Folder-Agent-Workspace. Leave `SHARED_CONTEXT_PATH` blank at onboarding; wire a
  Shared-Context later without re-onboarding.
- **Only the shared brain?** Take Shared-Context. Its link-in contract speaks plain files; any workspace
  layout can consume it, not just Folder-Agent-Workspace.
- **Only the registry?** Take Capability-Registry. Any folder-shaped tooling can be stocked and synced;
  nothing assumes the siblings exist.

## One law across all three (agent-agnostic, zero lock-in)

`AGENTS.md` is each member's neutral constitution; all logic lives in a neutral `core/`; runtimes
attach through **pinned pointer files plus one thin shim** (each member's `core/RUNTIMES.md` wires
a new runtime in minutes). A gate - `tools/agnostic-check.py`, identical in all three - fails any
build where a vendor name leaks into the neutral core or an adapter grows beyond a pointer.

## Shared mechanics (learn once, use thrice)

- `<<TOKEN>>` onboarding: a `.uninitialised` sentinel + session-start gate route a fresh agent to
  `core/onboarding/ONBOARDING.md`; a confirmed `values.json` is filled deterministically by
  `apply.py` (atomic, idempotent, `--dry-run`). `{{...}}` markers are runtime fill-ins, never
  onboarding's.
- OKF-compatible frontmatter with typed `related:` edges mirrored as body links
  (`okf-check` + `gen-related`).
- Confidentiality scrub before distribution (`scrub-check`); in Shared-Context the denylist derives
  mechanically from `boundaries/`.
- Append-only history with a mutable counterpart: journal + registers (Folder-Agent-Workspace), CHANGES +
  dashboard (Shared-Context), ledger + fleet report (Capability-Registry).

The six shared tools are vendored byte-identical into each member, stocked as the Capability-Registry's
seed capabilities, and `tools/family-check.py` (repo root) fails if any vendored copy drifts from
the registry checksums - the family runs on its own supply chain.

## House rules

British English; no em dashes; one concept per file, linked into a graph; source-or-abstain;
deterministic first, the model only where judgement is genuinely needed; the human at every
consequential gate. MIT, © 2026 CORBEL Ltd.

Always-loaded family context accepts only a stated consequential delta and names the redundant or
displaced text it removes; descriptive material stays in canonical indexed documentation.
