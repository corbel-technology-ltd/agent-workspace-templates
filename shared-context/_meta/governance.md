---
id: <<store_slug>>.meta.governance
name: Governance - the full edit protocol
type: doctrine
layer: C0
status: current
owner: shared
created: <<CREATED_DATE>>
file_cap: <<FILE_CAP>>
objection_window_hours: <<OBJECTION_WINDOW_HOURS>>
tags: [governance, protocol, objection-window, sign-off, ownership, ledger]
related:
  - {ref: SHARED.md, dimension: why, polarity: derived_from}
  - {ref: CHANGES.md, dimension: where, polarity: enables}
  - {ref: _coordination/roster.md, dimension: who, polarity: requires}
---

# Governance - the full edit protocol

The store is co-owned by every agent on the [roster](../_coordination/roster.md);
<<PRINCIPAL_NAME>> retains override authority on everything. This file is the complete protocol;
[`SHARED.md`](../SHARED.md) carries the summary. The two frontmatter keys above (`file_cap`,
`objection_window_hours`) are the machine-readable parameters `tools/shared-lint.py` and
`core/hooks/store-brief.py` read.

## The four moves

| Move | Protocol |
|---|---|
| **Edit an existing file** | Make the edit. Append a trailer to [`CHANGES.md`](../CHANGES.md). Window opens for <<OBJECTION_WINDOW_HOURS>> hours. |
| **Add or remove a file** | Propose first (the file may land with `status: proposed`). Needs **every roster agent's sign-off**, recorded in each workspace's own decision log, plus the trailer + window. Must pass the scope test and the file cap. |
| **Update a `_coordination/` row** | Low-risk: status updates to existing dashboard/roster rows need a trailer only if substantive, and no window. Changing those files' *structure* is a normal edit. |
| **Close a lapsed window** | Flip that entry's `window:` from `open (closes ...)` to `closed`. This is the ONE edit an existing ledger entry ever receives; do not touch its date, author, or summary. |
| **Retract / correct** | The ledger is append-only otherwise: write a NEW entry that names what it corrects. Never rewrite an old entry's prose. |

## The trailer format (machine-checked)

One line per change, newest first, directly under the marker line in `CHANGES.md`. The `window:`
field takes **exactly one** of three forms (not all three - the `|` alternation below is
this-or-this-or-this):

```text
YYYY-MM-DD | <who> | <summary> | window: open (closes YYYY-MM-DD)
YYYY-MM-DD | <who> | <summary> | window: closed
YYYY-MM-DD | <who> | <summary> | window: n/a (<reason>)
```

A worked entry:

```text
2026-07-02 | Acme via aster | added tech-stack entry for the shared NAS | window: open (closes 2026-07-03)
```

`tools/shared-lint.py` fails the build if any dated line does not parse. `n/a` needs a reason
(informational, principal-directed, or a low-risk `_coordination/` row update).

## The objection window

- Opens when the trailer lands; runs <<OBJECTION_WINDOW_HOURS>> hours. The trailer records the
  close as a calendar date (`closes YYYY-MM-DD`): round the hours up to the end of the day they
  land on, so a window is effectively "reviewed by end of its close date". `store-brief.py` flags
  an entry OVERDUE once that date is past.
- Every roster agent reviews open windows at its next session boot
  (`core/hooks/store-brief.py` surfaces them, including overdue ones).
- An objection is a new ledger entry naming the disputed change. The change stays but is frozen
  (no dependent edits) until resolved.
- Silence past the close date = accepted; the author flips that entry's `window:` to `closed`
  (the one permitted edit to a past entry, per the four-moves table above).

## Disagreement

One round of written agent-to-agent exchange (a ledger entry each, or a dashboard handoff row with
the positions). Still deadlocked? The principal decides. Never edit-war the file itself.

## The scope test and the file cap

Anything added must pass [`operating-rules/scope-test.md`](../operating-rules/scope-test.md): two
or more plugged-in workspaces would independently need it, it is rules-or-identity (not domain
knowledge), and it contains no secrets. The store holds at most **<<FILE_CAP>>** content files
(`shared-lint` counts the content folders, excluding READMEs and `_`-prefixed templates). At the
cap, adding a file means consolidating or retiring another - growth is a decision.

## What governance does NOT cover

Each workspace's own files, decisions, and registers - those are governed by the workspace's own
constitution. This protocol binds only what lives in this store.

## Related

- [<<STORE_NAME>>](../SHARED.md)
- [Shared profile changelog](../CHANGES.md)
- [Workspace roster - who is plugged in](../_coordination/roster.md)
