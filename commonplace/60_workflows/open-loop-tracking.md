---
id: <<workspace_slug>>.workflow.open-loop-tracking
name: Open-loop tracking workflow
type: workflow
layer: C2
status: current
owner: shared
created: <<CREATED_DATE>>
staging: v1-now
tags: [workflow, open-loops, projects, waiting-on, daily-brief, capture-back, anti-noise-batching]
related:
  - {ref: 80_projects/index.md, dimension: what, polarity: explains}
  - {ref: 30_schemas/project.md, dimension: what, polarity: explains}
  - {ref: 30_schemas/event.md, dimension: why, polarity: derived_from}
  - {ref: 50_registers/decision-queue.md, dimension: how, polarity: enables}
  - {ref: 30_schemas/decision-packet.md, dimension: how, polarity: requires}
---

# Open-loop tracking

Run by hand. Keeps each project's loops true: open a loop when a promise or dependency appears, close
it when it resolves, surface overdue loops in the daily brief. Loops live per project under
[`../80_projects/`](../80_projects/index.md) — each `80_projects/<slug>/loops.md` (and
`_general/loops.md` for loops tied to no project), per the contract in
[`../30_schemas/project.md`](../30_schemas/project.md). The loops file is the live view; the journal
is the truth. This is **capture-back** for commitments and **anti-noise batching** for the chase.

A loop is any open commitment waiting on someone or something. Its `ball` says who it hangs on:
`mine` (the owner to act), `theirs` (a counterparty owes), or `external` (a dated event with no
owner to chase). Sources are the journal, the decision log, email (the email loop), and notes.

## When to run

- Inside the daily brief ([`daily-brief.md`](daily-brief.md)) — the overdue sweep below.
- The moment a promise or dependency surfaces (an email reply expected, a date committed, a
  third-party process started) — open the loop then, not later.

- When something resolves — close the loop then.

## Plan -> Validate -> Execute

### A. Open a loop (a promise or dependency appears)

1. **Plan.** Identify the trigger: a sentence in an email, a row in
   [`../50_registers/decision-log.md`](../50_registers/decision-log.md), a journal entry, or a note
   where a commitment or dependency is created. Decide which **project** it belongs to (its
   `80_projects/<slug>/loops.md`, or `_general/loops.md` if none), and its **ball**: `mine`,
   `theirs`, or `external`.

2. **Validate (source-or-abstain).** A loop needs a journal source. If the trigger is not already a
   journal entry, write one first (`30_schemas/event.md`); a loop with no `source` is unverified and
   is not added. Confirm the loop is not a duplicate of an existing open row. If the project folder
   does not exist yet and now has live content, create it per
   [`../30_schemas/project.md`](../30_schemas/project.md).

3. **Execute.** Add one row to that project's `loops.md` `## Open` table:
   - **item** — the commitment, in one line.
   - **ball** — `mine` / `theirs` / `external`.
   - **who** — the counterparty, the owner's name when the ball is `mine`, or the external thing.
   - **since** — today (YYYY-MM-DD).
   - **due** — the date a response or event is expected, or `none` if open-ended. A `ball: mine` loop
     with no hard date still wants a review date so the brief surfaces it.
   - **status** — `open`.
   - **source** — the journal entry the loop traces to.

### B. Surface overdue loops (the daily-brief sweep)

1. **Plan.** Read every open row across all `80_projects/*/loops.md` `## Open` tables.
2. **Validate.** For each row with a dated `due`, compare `due` against today.
3. **Execute.**
   - `due` is past and status is still `open` or `nudged` -> set **status: overdue**.
   - A `ball: theirs` loop is `open`/`overdue` and a chase is warranted -> the brief proposes a
     nudge; on **founder approval** the draft goes out via the email-triage-approve workflow (no
     external send without approval), then set **status: nudged**. **signpost, don't advise**: the
     brief lists the loop and a suggested nudge; the founder decides.
   - A loop cannot progress without a founder decision -> set **status: blocked**, raise a Decision
     Packet ([`30_schemas/decision-packet.md`](../30_schemas/decision-packet.md)) and a row in
     [`../50_registers/decision-queue.md`](../50_registers/decision-queue.md), and cross-link the
     packet from the loop's `source`. Do not guess the decision in the loops table.
   - The brief's "waiting on / overdue" section is just the overdue and blocked rows, plus any
     `due` within the next 2 days. Non-urgent open loops stay batched in their project file.

### C. Close a loop (it resolves)

1. **Plan.** Confirm the loop is genuinely resolved: the reply landed, the deliverable shipped, the
   external date passed and was actioned, or the commitment was withdrawn.

2. **Validate.** Write a closing journal entry (`30_schemas/event.md`) recording the outcome. This
   is the truth; the loops-file move follows it.

3. **Execute.** Move the row out of the project's `## Open` table and append it to that file's
   `## Closed` with: **item**, **ball**, **who**, **opened** (the old `since`), **closed** (today),
   **outcome** (one line), **source** (the closing journal entry). The Closed table is append-only.
   A loop that re-opens is a NEW row in `## Open` with a fresh `since` and its own journal entry,
   never an edit of a closed row.

## Definition of done

- Every open commitment or dependency in email, the decision log, or notes has exactly one open row
  in the right project's `loops.md`.

- Every loop row has a `source` pointing at a journal entry.
- No `due`-dated row sits past its date still marked `open` (it is `overdue`, `nudged`, or closed).
- Closed loops have a closing journal entry; the loops file and journal agree.
- No external nudge has gone out without founder approval.

## Notes

- **Anti-noise batching:** a loop waits silently in its project file until its `due` nears or its
  status changes; only then does the daily brief surface it. The SessionStart brief lists open loops
  at boot regardless, as situational awareness.

- **Derived view:** a `loops.md` is rebuildable from the journal. If it disagrees with a journal
  entry, the journal wins; correct the loops file, never the journal.

## Related

- [Active projects](../80_projects/index.md)
- [Project schema](../30_schemas/project.md)
- [Journal event schema](../30_schemas/event.md)
- [Decision queue — open founder decisions](../50_registers/decision-queue.md)
- [Decision Packet schema](../30_schemas/decision-packet.md)
