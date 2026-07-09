# Capability-Registry

**The outfitter for your workspace fleet.** A plain-files capability registry plus a parity
ledger: the mechanism by which deterministic tooling (gate scripts, hooks, onboarding engines,
schemas, workflow specs) moves between agent workspaces - and by which drift between siblings
becomes visible instead of silent.

Capability-Registry is the registry member of the **FAW template family** (Filesystem Agent Workspace).
**Folder-Agent-Workspace** is the workspace a fleet is made of; **Shared-Context** is the shared brain those
workspaces steer by; the Capability-Registry is where every vessel fits out with standard, proven gear.

## The problem it exists for

The moment you run two agent workspaces, their machinery forks. A hook gets fixed in one and not
the other; a lint gets ported by hand and drifts; "improvements should flow back upstream" stays
doctrine with no mechanism. Knowledge-level governance does not fix this - it is a *supply*
problem, not a rules problem.

## How it works

A **capability** is a folder: a `manifest.yml` (name, integer version, files with sha256 checksums
and workspace target paths) plus the payload. The engine (`core/chandler.py`, stdlib + PyYAML, no
network) does exactly eight things: `list`, `verify`, `status`, `diff`, `install`, `pack`,
`fleet`, `enrol`.

```bash
python3 core/chandler.py status --workspace ~/acme     # what has drifted?
python3 core/chandler.py diff okf-check --workspace ~/acme
python3 core/chandler.py install okf-check --workspace ~/acme   # adopt (gated by --yes on conflict)
python3 core/chandler.py pack okf-check --from-workspace ~/acme --yes  # flow an improvement back, v+1
python3 core/chandler.py fleet                          # whole-fleet drift report
```

Install is an operator decision (nothing runs unattended, nothing overwrites local difference
without `--yes`); every registry change is a version bump plus an append-only
[`ledger.md`](ledger.md) line. Not a package manager: no dependency resolution, no remote fetch,
no auto-update - copying files and recording checksums, with a human at the gate.

## It ships stocked - and load-bearing

The five seed capabilities are the FAW family's own shared tools (the scrub/OKF/agent-agnostic
gates, the Related-mirror generator, the onboarding engine). They are not demo content: the family
repo's own check verifies every sibling template's vendored copies against **this registry's
checksums**. The registry keeps the family honest before it ever keeps your fleet honest.

## Composes with, never requires

- **Alone:** any folder-shaped tooling can be stocked and synced - agent workspaces, dotfiles-like
  setups, anything.
- **With Folder-Agent-Workspace:** workspaces track installed capabilities in a `.capability-registry.yml` lockfile;
  their component registries stay the per-workspace catalogue while the capability-registry holds the
  cross-workspace stock.
- **With Shared-Context:** point `fleet.yml`'s `shared_context:` at the store and `fleet` cross-checks
  the store's roster - a workspace plugged into the shared brain but missing from the fleet gets
  flagged. Adoption *rules* (what needs sign-off) belong in the store's `operating-rules/`; the
  capability-registry is the mechanism those rules govern.

## What is inside

```text
AGENTS.md        the constitution: scope, the flow, the hard rules
registry/        the stock - one folder per capability (manifest + payload + doc)
core/chandler.py the engine: list · verify · status · diff · install · pack · fleet · enrol
ledger.md        append-only history of the stock
fleet.yml        the workspaces this capability-registry outfits
core/            onboarding + the session-start gate, runtime-neutral
tools/           the family gates (scrub, OKF, agent-agnostic)
```

Plus one thin adapter per wired runtime (`core/RUNTIMES.md`). Start at [`AGENTS.md`](AGENTS.md).

## The family

Capability-Registry is the **registry** member of the FAW template family - three templates that stand alone
and click together (the whole story lives in `FAMILY.md` at the family repo root,
`github.com/CORBEL-Technology/Agent-Workspace-Templates`):

- **Folder-Agent-Workspace** - the workspace an agent runs; the fleet is made of these.
- **Shared-Context** - the shared-context store the fleet steers by; `fleet.yml` can point at it for
  roster cross-checks.
- **Capability-Registry** (this one) - where the fleet fits out.

**Taking just this part is fine.** Nothing here assumes the siblings exist - any folder-shaped
tooling can be stocked, installed, packed, and drift-checked.

## Licence

MIT, © 2026 CORBEL Ltd. See [LICENSE](LICENSE).
