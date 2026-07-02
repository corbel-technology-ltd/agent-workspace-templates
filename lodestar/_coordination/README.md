---
id: <<store_slug>>.coordination.readme
name: Coordination - the live dashboard and the roster
type: reference
layer: C1
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [coordination, dashboard, roster, handoffs, link-in]
related:
  - {ref: _coordination/dashboard.md, dimension: what, polarity: enables}
  - {ref: _coordination/roster.md, dimension: who, polarity: enables}
  - {ref: CHANGES.md, dimension: how, polarity: complements}
---

# Coordination

The **mutable counterpart to the append-only ledger**. [`CHANGES.md`](../CHANGES.md) answers "what
happened, ever"; this folder answers "what is pending, right now" - and never both in one file.

- [`dashboard.md`](dashboard.md) - open handoffs between workspaces: who owes what to whom, each
  row with an ID, a status, and a pointer to the detail. Rows move to *Recently closed* when done
  and drop off after ~2 weeks. Row-status updates are the low-risk edit class (no objection
  window; see [`_meta/governance.md`](../_meta/governance.md)).
- [`roster.md`](roster.md) - the register of plugged-in workspaces the link-in contract writes to
  (`core/link-workspace.py`). The roster defines who "every agent" means in governance: sign-offs
  and objection windows bind exactly the agents listed here.

At session boot, a visiting agent scans the dashboard for rows addressed to its workspace and the
ledger for open objection windows; `core/hooks/store-brief.py` prints both automatically where a
runtime wires it.

## Related

- [Dashboard - open cross-workspace handoffs](dashboard.md)
- [Workspace roster - who is plugged in](roster.md)
- [Shared profile changelog](../CHANGES.md)
