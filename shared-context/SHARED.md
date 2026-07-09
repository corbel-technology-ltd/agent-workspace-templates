---
id: <<store_slug>>.constitution
name: <<STORE_NAME>>
type: doctrine
layer: C0
status: current
owner: shared
spec_version: 0.1
initialised: false
created: <<CREATED_DATE>>
updated: <<CREATED_DATE>>
tags: [shared-context, constitution, precedence, link-in, governance, shared-context]
related:
  - {ref: _meta/governance.md, dimension: how, polarity: requires}
  - {ref: _coordination/roster.md, dimension: who, polarity: enables}
  - {ref: boundaries/README.md, dimension: what, polarity: requires}
---

# <<STORE_NAME>> - the shared-context constitution

This store is the single, agent-neutral source of truth for **who <<PRINCIPAL_NAME>> is, how their
agents behave, and what environment those agents operate in**. It sits *above* every workspace.
Many agents and workspaces plug into one store; each keeps its own operational content locally and
reads the shared brain from here.

Built from **Shared-Context**, the shared-context member of the FAW template family (a workspace is to
one venture what this store is to the whole of the principal's agent estate).

## Precedence (the doctrine this store exists for)

**Shared outranks local.** When a workspace's local notes about the principal, their preferences,
their people, or their environment disagree with this store, **this store wins**. Highest first:

1. Safety, legality, privacy, and explicit approval rules.
2. The principal's current, direct instruction.
3. **This store** - durable shared identity, rules, calibration, boundaries.
4. The workspace's own constitution and local rules (its operational domain stays its own).
5. Examples and style references - evidence, never law.
6. Agent inference.

Two clarifications that stop precedence being misread:

- Precedence applies to **shared-scope content** (the principal, cross-workspace rules, shared
  people/tech). A workspace's routing, registers, and domain knowledge are out of this store's
  scope, so there is nothing for the store to outrank there.
- A newer local observation about the principal does not silently override the store: it is a
  **correction candidate** - log it (`calibration-os/corrections.md`) and promote it through
  governance, so every sibling workspace inherits the fix instead of one drifting.

## Scope (what belongs here, and the test)

**In scope:** identity-level material and cross-workspace rules that two or more consumers need -
who the principal is, how agents should behave everywhere, shared people, the shared
machine/software estate, living calibration, the confidentiality line, and the shared vocabulary.

**Out of scope:** workspace-specific operational content, project/domain knowledge, run artefacts,
credentials and secrets (never store a secret here - this store is designed to be read widely).

The gate for adding anything: the **scope test** ([`operating-rules/scope-test.md`](operating-rules/scope-test.md))
- would at least two plugged-in workspaces independently need this? If not, it stays local. The
store carries a **file cap** (<<FILE_CAP>> content files; `tools/shared-lint.py` counts) so growth
stays a decision, not a drift.

## The link-in contract

Plugging a workspace into this store is a five-clause contract. Add a workspace later = point it
here, inherit the whole brain.

1. **Register.** From this store's root:
   `python3 core/link-workspace.py --name <workspace> --path </abs/path> --agent <agent-name>`.
   That records the workspace in [`_coordination/roster.md`](_coordination/roster.md), offers the
   CHANGES ledger line, and prints the boot rule below.
2. **Reach.** The workspace records this store's absolute path in its own constitution (a
   Folder-Agent-Workspace workspace fills `SHARED_CONTEXT_PATH` at onboarding; any other layout keeps an
   equivalent pointer). If the workspace symlinks this store into its tree, its search tooling
   must **follow symlinks**, or the shared brain silently vanishes from local search.
3. **Boot reflex.** At session start, the workspace's agent loads `identity/` and
   `operating-rules/` at minimum, then checks [`_coordination/dashboard.md`](_coordination/dashboard.md)
   for anything owed to or by it, and reviews open objection windows in [`CHANGES.md`](CHANGES.md).
   The canonical boot rule (paste into the workspace constitution):

   > **Load the shared context first.** Read `<store-path>/SHARED.md`, then `identity/` and
   > `operating-rules/`. The store outranks this workspace's local notes on the principal. Check
   > `_coordination/dashboard.md` for open handoffs owed to this workspace.

4. **Precedence.** The workspace acknowledges the hierarchy above: the store wins on shared-scope
   conflicts, and corrections flow back through governance rather than forking locally.
5. **Governance.** Any edit made to this store from any workspace follows the protocol in
   [`_meta/governance.md`](_meta/governance.md): CHANGES trailer, <<OBJECTION_WINDOW_HOURS>>-hour
   objection window, sign-off for adding or removing files. The roster is who "everyone" means.

## Governance (summary - full protocol in `_meta/governance.md`)

- **Joint ownership, principal override.** Every roster agent co-owns the store;
  <<PRINCIPAL_NAME>> retains override authority on everything.
- **Every edit gets a ledger entry.** Append a trailer line to [`CHANGES.md`](CHANGES.md) (date,
  workspace, summary, window status). The ledger is append-only.
- **Objection window.** Edits stand open for <<OBJECTION_WINDOW_HOURS>> hours; other roster agents
  review at their next session boot. Low-risk status updates inside `_coordination/` need no
  window; structural changes do.
- **Add/remove a file = sign-off.** New or deleted files need every roster agent's sign-off,
  recorded in each workspace's own decision log.
- **Disagreement.** One round of written agent-to-agent exchange; the principal only if deadlocked.

## The map

| Folder | Holds | Starts |
|---|---|---|
| [`identity/`](identity/README.md) | The principal's canonical profile, voice, availability | blank skeletons |
| [`operating-rules/`](operating-rules/README.md) | Cross-workspace rules - how agents behave, not what they know | seed rules + template |
| [`people/`](people/README.md) | Shared people (only those 2+ workspaces deal with) | template only |
| [`tech-stack/`](tech-stack/README.md) | The shared machine/software estate | template only |
| [`calibration-os/`](calibration-os/README.md) | Living scoped preferences + corrections pipeline | blank by design |
| [`boundaries/`](boundaries/README.md) | The confidentiality line; scrub lists derive from it | skeleton |
| [`glossary/`](glossary/README.md) | The shared vocabulary (incl. names ruled out) | skeleton |
| [`_coordination/`](_coordination/README.md) | Live dashboard of open handoffs + the workspace roster | empty tables |
| [`CHANGES.md`](CHANGES.md) | Append-only ledger of every edit | onboarding writes entry one |
| [`_meta/`](_meta/governance.md) | Governance protocol + the store's own design spec | shipped |
| `core/`, `tools/` | Onboarding + hooks (neutral) and the gates | shipped |

## Operate lean

Load the **minimum** a task needs; the map is a ceiling, not a checklist. Never load blank files -
they cost attention and add nothing. Consolidate before adding: a new file must pass the scope
test and the file cap.

## Related

- [Governance - the full edit protocol](_meta/governance.md)
- [Workspace roster - who is plugged in](_coordination/roster.md)
- [Boundaries - the confidentiality line](boundaries/README.md)
