---
id: <<workspace_slug>>.workflow.daily-brief
name: Daily brief — the run-by-hand morning assembly
type: workflow
layer: C2
status: current
owner: shared
staging: v1-now
created: <<CREATED_DATE>>
tags: [workflow, daily-brief, decision-queue, open-loops, email, anti-noise-batching]
related:
  - {ref: 40_templates/daily-brief.md, dimension: what, polarity: requires}
  - {ref: 50_registers/decision-queue.md, dimension: what, polarity: requires}
  - {ref: 80_projects/index.md, dimension: what, polarity: requires}
  - {ref: 60_workflows/email-triage-approve.md, dimension: how, polarity: requires}
  - {ref: 30_schemas/decision-packet.md, dimension: what, polarity: explains}
---

# Daily brief

The morning assembly. One run produces today's brief from the template
([`../40_templates/daily-brief.md`](../40_templates/daily-brief.md)) into
`90_runs/YYYY-MM-DD-brief.md`. Run by hand (the agent executes the steps); a script is **deferred**
until the manual pass earns it (design-spec §9). The brief is the only thing that competes for the
founder's attention: everything non-urgent batches here rather than interrupting (anti-noise
batching).

The work is **mostly deterministic gathering** — reading register rows and dates, applying fixed
filters. An LLM is used **only** to summarise the gathered rows into tight prose; it never decides
what is urgent, never approves a packet, and never sends. AI is a reasoning layer, never an
authority layer (AI-minimisation; signpost, don't advise).

Determinism: take an explicit `--as-of <date>` (default: today). Same registers + same journal +
same `--as-of` → same gathered set. Only the section summaries vary.

## Steps

1. **Date the run.** Resolve `--as-of` (default today). Copy
   [`../40_templates/daily-brief.md`](../40_templates/daily-brief.md) into
   `90_runs/<as-of>-brief.md` and substitute the date. If the file already exists, regenerate in
   place; the brief is a working artefact, not a record.

2. **Gather open decisions (deterministic).** Read the `## Open decisions` table in
   [`../50_registers/decision-queue.md`](../50_registers/decision-queue.md). Take every row with
   `status: open` (and `snoozed` rows whose `Review` date is `<= as-of`). Sort by `risk`
   descending, then by `date` ascending. For each, carry through its `summary`, `risk`, packet
   link, and queue `id`. Read the packet's `recommendation` field straight from
   `30_schemas/decision-packet.md` shape — do not re-derive it. These fill **§2 Immediate
   decisions**. Less reversible means more explicit approval (autonomy-by-reversibility).

3. **Gather open loops due (deterministic).** Read the `## Open` table of every project's loops file
   under [`../80_projects/`](../80_projects/index.md) (`80_projects/*/loops.md`, including
   `_general/loops.md`). Take rows whose `status` is `overdue` or `nudged`, or whose `due` is
   `<= as-of + 2d` (the near-due window), or `blocked`. A `ball: mine` row that is due becomes a
   candidate for **§1 Top founder actions**; a `blocked` loop is already a decision-queue row, so
   surface it under §2, not twice. Loops with a distant or `none` due date stay in their project file
   and are not surfaced (anti-noise batching).

4. **Gather email needing approval (from the email loop).** Follow
   [`email-triage-approve.md`](email-triage-approve.md) to read the drafts the email loop has
   prepared and parked at the gate. Each holds because **no external send happens without explicit
   founder approval** (hard invariant). List sender/thread, a one-line summary of the drafted reply,
   and the awaiting action (approve / edit / discard). These fill **§3 Email needing approval**. The
   brief surfaces them; it does not send. Approval and the send-tool invoke happen only after the
   founder settles the row.

5. **Gather what was handled automatically (deterministic).** Read `20_memory/journal/` entries
   since the previous brief's `--as-of`. Take entries tagged as deterministic, no-decision actions
   (routine captures, scheduled checks, register housekeeping). These fill **§4 Handled
   automatically** as read-only reassurance, each citing its journal entry so it stays auditable.
   This is not a to-do list.

6. **Pick the top founder actions (judgement).** From the §2 decisions wanting a call today and the
   §1-candidate due `ball: mine` loops, select the highest-leverage items only — what *only* the
   founder can move. This is the one genuinely judgement-laden step; keep it short. Empty is a valid
   answer, do not pad.

7. **Summarise (LLM, bounded).** Render each gathered set into the template's tables and one-line
   entries. The LLM compresses wording only; it must not introduce a row, a recommendation, or a
   claim that was not in the gathered source. Any statutory or factual line carries its source or is
   omitted (source-or-abstain).

8. **Save.** Write the filled brief to `90_runs/<as-of>-brief.md`. Loops and decisions not actioned
   today carry forward in their registers untouched; the brief is regenerated tomorrow.

## Inputs and output

| Section | Source (deterministic) | Filter |
|---|---|---|
| §1 Top founder actions | §2 set + due `ball: mine` loops | founder-only, highest leverage |
| §2 Immediate decisions | `decision-queue.md` open rows + their packets | `status: open`; due `snoozed` |
| §3 Email needing approval | the email loop via `email-triage-approve.md` | parked drafts awaiting the gate |
| §4 Handled automatically | `journal/` since last brief | deterministic, no-decision entries |

Output: `90_runs/<as-of>-brief.md`.

## Invariants

- The brief never sends, publishes, pays, or signs, and never approves a decision packet. It
  prepares; the founder settles items in [`decision-queue.md`](../50_registers/decision-queue.md)
  and §3, then any send goes through `email-triage-approve.md`.

- The LLM summarises only. It never decides urgency, invents a row, or re-derives a recommendation
  the packet did not state (AI-minimisation).

- Every §4 line cites a `journal/` entry; an uncited line is not a fact (source-or-abstain).
- The brief is a working artefact in `90_runs/` (C4). It reads the registers; it does not edit
  them. Settling a decision updates `decision-queue.md` and appends to `decision-log.md`, not this
  file.

## What this defers

An attention-score formula, automated urgency ranking, an email connector, a scheduler, and a
dashboard render are all out of scope. At solo volume the deterministic filters above plus one
bounded summarisation step are sufficient. Promote to software only when this pass has run by hand
for >=4 weeks and consistently costs >20 minutes to assemble (the value-gate, design-spec §9).

## Related

- [Daily founder brief — fill-in template](../40_templates/daily-brief.md)
- [Decision queue — open founder decisions](../50_registers/decision-queue.md)
- [Active projects](../80_projects/index.md)
- [Email triage and approve — thin wrapper over the email loop](email-triage-approve.md)
- [Decision Packet schema](../30_schemas/decision-packet.md)
