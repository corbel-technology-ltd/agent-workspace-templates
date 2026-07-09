---
id: <<store_slug>>.coordination.dashboard
name: Dashboard - open cross-workspace handoffs
type: register
layer: C1
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [dashboard, handoffs, coordination, register, mutable]
related:
  - {ref: _coordination/roster.md, dimension: who, polarity: requires}
  - {ref: CHANGES.md, dimension: how, polarity: complements}
---

# Dashboard - open cross-workspace handoffs

What is **currently pending** between workspaces. If you want "what happened", read
[`CHANGES.md`](../CHANGES.md); if you want "what do I owe / what am I owed right now", read this.

## How to use

- **At session boot:** scan for rows whose *To* is your workspace. Act, or update the status.
- **Handing work over:** add a row. ID it `<from-initial><to-initial>-NN` (e.g. `AB-01` for the
  first Acme->Bramble handoff), one-line summary, date, status, and a pointer to the detail
  (usually a ledger entry or a run note in the sending workspace).
- **Completing:** move the row to *Recently closed* with the date and outcome; prune closed rows
  older than ~2 weeks.
- Row-status updates are low-risk (no objection window). Changing this file's structure is a
  normal governed edit.

## Open handoffs

| ID | From -> To | Summary | Raised | Status | Detail |
|---|---|---|---|---|---|
| _none yet_ | | | | | |

## Recently closed

| ID | Summary | Closed | Outcome |
|---|---|---|---|
| _none yet_ | | | |

## Related

- [Workspace roster - who is plugged in](roster.md)
- [Shared profile changelog](../CHANGES.md)
