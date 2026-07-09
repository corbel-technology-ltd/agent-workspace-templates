---
id: <<store_slug>>.coordination.roster
name: Workspace roster - who is plugged in
type: register
layer: C1
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [roster, link-in, workspaces, register, governance-scope]
related:
  - {ref: SHARED.md, dimension: why, polarity: derived_from}
  - {ref: _coordination/dashboard.md, dimension: what, polarity: complements}
---

# Workspace roster

Every workspace plugged into this store, written by the link-in contract
(`python3 core/link-workspace.py`, see [`SHARED.md`](../SHARED.md) §link-in). This register is
**governance scope**: sign-offs and objection windows bind exactly the agents listed here.

Unlinking a workspace is a governed edit to a `_coordination/` file: set its status to `retired`
(keep the row - the ledger may reference it). Per the governance four-moves table, a substantive
row change like this takes a `CHANGES.md` trailer; a bare status touch does not need an objection
window.

## Registered workspaces

| Workspace | Path | Agent | Linked | Status |
|---|---|---|---|---|
| _none yet_ | | | | |

## Related

- [<<STORE_NAME>>](../SHARED.md)
- [Dashboard - open cross-workspace handoffs](dashboard.md)
