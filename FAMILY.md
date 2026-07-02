# The FAW family

Three templates, one pattern: the **Filesystem Agent Workspace** (FAW) - run your work as plain
Markdown and git that an AI agent operates and a human stays in front of. No app, no database, no
vendor. Each member is independently useful; together they cover the three surfaces every serious
agent estate grows: the workspace, the shared brain, and the supply chain between them.

| Member | Is | One-liner |
|---|---|---|
| **Commonplace** (`commonplace/`) | the workspace | A folder-based agent workspace: constitution, doctrine, append-only journal + decaying memory, registers, workflows, and a safety gate that keeps authority human. |
| **Lodestar** (`lodestar/`) | the shared context | The store above every workspace: who the principal is, how their agents behave, the environment they share - governed by ledger + objection windows, and outranking anything local. |
| **Chandlery** (`chandlery/`) | the capability registry | The outfitter for the fleet: versioned, checksummed capabilities (gates, hooks, engines) that install into workspaces, flow improvements back, and make drift visible. |

## How they compose

One principal, one Lodestar, many Commonplace workspaces, one Chandlery:

```text
                       Lodestar  (the star they steer by)
                      /    |    \        identity · rules · calibration · boundaries
        link-in      /     |     \       CHANGES ledger · objection windows · roster
                    /      |      \
         Commonplace  Commonplace  Commonplace     (the vessels)
                    \      |      /
        install/pack \     |     /       capabilities · versions · checksums
                      \    |    /        fleet drift report · append-only ledger
                       Chandlery  (where they fit out)
```

- A workspace **links into** Lodestar at onboarding (`SHARED_CONTEXT_PATH`); the store's roster
  records it, its session brief loads the shared brain first, and "shared outranks local" keeps
  every sibling calibrated identically.
- A workspace **fits out from** the Chandlery: `install` adopts a capability (operator-gated),
  `pack` flows a local improvement back (version bump + ledger), `fleet` shows who has drifted.
- Lodestar and Chandlery **compose without coupling**: point the Chandlery's `fleet.yml` at the
  store and the fleet report cross-checks the roster; adoption *rules* live in the store's
  `operating-rules/`, the *mechanism* they govern lives in the Chandlery.

## Take just one part

Each member folder is self-contained (own LICENSE, gates, install guide, onboarding). From this
repo: `python3 instantiate.py <commonplace|lodestar|chandlery> <dest>` copies one out and
`git init`s it - or copy the folder by hand and `git init` yourself. Nothing in a member reaches
into a sibling by relative path.

- **Only a workspace?** Take Commonplace. Leave `SHARED_CONTEXT_PATH` blank at onboarding; wire a
  Lodestar later without re-onboarding.
- **Only the shared brain?** Take Lodestar. Its link-in contract speaks plain files; any workspace
  layout can consume it, not just Commonplace.
- **Only the registry?** Take Chandlery. Any folder-shaped tooling can be stocked and synced;
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
- Confidentiality scrub before distribution (`scrub-check`); in Lodestar the denylist derives
  mechanically from `boundaries/`.
- Append-only history with a mutable counterpart: journal + registers (Commonplace), CHANGES +
  dashboard (Lodestar), ledger + fleet report (Chandlery).

The five shared tools are vendored byte-identical into each member, stocked as the Chandlery's
seed capabilities, and `tools/family-check.py` (repo root) fails if any vendored copy drifts from
the registry checksums - the family runs on its own supply chain.

## House rules

British English; no em dashes; one concept per file, linked into a graph; source-or-abstain;
deterministic first, the model only where judgement is genuinely needed; the human at every
consequential gate. MIT, © 2026 CORBEL Ltd.
