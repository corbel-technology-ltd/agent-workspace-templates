---
id: <<workspace_slug>>.registers.model
name: Registers — live ledgers / state (rebuildable views over journal truth)
type: reference
layer: C1
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [registers, live-state, ledgers, projections, gate, capture-back, source-or-abstain]
related:
  - {ref: AGENTS.md, dimension: why, polarity: derived_from}
  - {ref: 20_memory/journal/README.md, dimension: what, polarity: requires}
  - {ref: 60_workflows/daily-brief.md, dimension: how, polarity: enables}
  - {ref: 30_schemas/decision-packet.md, dimension: what, polarity: explains}
---

# Registers

The workspace's **live working state**: the small set of ledgers the founder and the agent read and
write turn-by-turn. Each is a **rebuildable view over journal truth** — the
[`journal/`](../20_memory/journal/README.md) is the only source of truth (append-only, immutable);
a register is a current-state projection folded from it. On any conflict, the journal wins. These are
the C1 surfaces in [`AGENTS.md`](../AGENTS.md)'s context layers — the live face of the control plane,
distinct from the long-term memory model in [`20_memory/`](../20_memory/README.md).

## The contract

- **Sourced, not invented.** Every row traces to a journal event or a named origin (source-or-abstain).
  A row with no source is unverified.
- **Two kinds of ledger.** Most registers are *working sets* — rows live only while active, settled
  rows are pruned, and the durable record moves elsewhere. A few are *append-only* (the decision log)
  and follow the journal's rule: never edit or delete a past row; a reversal is a NEW row that names
  the one it overturns.
- **The gate runs here.** The decision queue and blocked-actions register are the visible face of
  `AGENTS.md`'s safety gate: preparation is automated, **authority is always gated**. The agent may
  draft, evidence, and recommend; it never approves its own packets.
- **Starts empty.** The template ships the register files with their headers, conventions, and an
  empty table (`(none yet)`). Content accrues as the workspace runs.

## How they're used

The daily brief ([`../60_workflows/daily-brief.md`](../60_workflows/daily-brief.md)) and the
SessionStart brief render the open rows so nothing else competes for the founder's attention. The
[Routing map](../AGENTS.md) points here when a decision is needed, a risk surfaces, a document is
filed, or an improvement is sensed. Closing a loop is itself capture-back: settled decisions land in
the append-only log, durable lessons go back to the journal as atoms.

## What lives here

- [`decision-queue.md`](decision-queue.md) — open founder decisions; one row per prepared
  [Decision Packet](../30_schemas/decision-packet.md) awaiting `approve` / `reject` / `snooze` / `ask`.
  The live working face of the gate.
- [`decision-log.md`](decision-log.md) — **append-only** audit trail of decisions *made* (approvals
  and rejections both), each naming the `memory_update` atom it produced (capture-back).
- [`blocked-actions.md`](blocked-actions.md) — audit trail of every action the gate **stopped**, and
  why; proof that autonomy-by-reversibility is enforced, not just stated.
- [`component-registry.md`](component-registry.md) — catalogue of every ops moving part (script,
  automation, alert, API, hook): what it is, what triggers it, what it touches. The splash-zone map.
- [`risk-register.md`](risk-register.md) — material risks to the entity, one row per live risk,
  each traced to a source.
- [`records.md`](records.md) — thin index over stored documents (invoices, contracts, filings); the
  binary lives off-machine, the row is the pointer (evidence plane).
- [`improvement-backlog.md`](improvement-backlog.md) — where sensed proactivity lands so it does not
  become noise; ranked blocking → strategic → opportunistic, gated do-now / suggest / log / ignore.
- [`measurement.md`](measurement.md) — the inward signal: hand-tracked weekly metrics graded on the
  North Star (founder decisions made from prepared packets). No dashboard, no software.
- [`tool-watchlist.md`](tool-watchlist.md) — external tools/repos scouted but not adopted; a parking
  lot, promoted to the component registry only when actually wired in.
- [`open-loops.md`](open-loops.md) — a **redirect stub only**, kept so existing links resolve. Open
  loops moved to per-project files under [`../80_projects/`](../80_projects/index.md); do not
  re-populate this as a live register.

## Related

- [<<WORKSPACE_NAME>>](../AGENTS.md)
- [Journal — the append-only event log](../20_memory/journal/README.md)
- [Daily brief — the run-by-hand morning assembly](../60_workflows/daily-brief.md)
- [Decision Packet schema](../30_schemas/decision-packet.md)
