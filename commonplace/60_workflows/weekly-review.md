---
id: <<workspace_slug>>.workflow.weekly-review
name: Weekly review — the once-a-week scan, reap, and re-prioritise
type: workflow
layer: C2
status: current
owner: shared
created: <<CREATED_DATE>>
staging: v1-now
tags: [workflow, weekly-review, registers, runs, anti-noise-batching, homeostasis, capture-back]
related:
  - {ref: 40_templates/weekly-review.md, dimension: what, polarity: enables}
  - {ref: 60_workflows/memory-reaper.md, dimension: how, polarity: requires}
  - {ref: 50_registers/decision-log.md, dimension: what, polarity: derived_from}
  - {ref: 50_registers/decision-queue.md, dimension: what, polarity: derived_from}
  - {ref: 80_projects/index.md, dimension: what, polarity: derived_from}
---

# Weekly review

The once-a-week pass that keeps the workspace honest. Run by hand (the agent executes the steps; the
founder decides) over the week's run folders (`90_runs/`) and the live registers
(`50_registers/`). It is the **anti-noise batching** endpoint: everything non-urgent that piled up
over the week is read here, once, instead of interrupting the days. The output is one file,
`90_runs/YYYY-Www-review.md`, built from [`../40_templates/weekly-review.md`](../40_templates/weekly-review.md).

This workflow is the procedure; the template is the form it fills. Read both. The template says
what each section holds; this says how to gather it and in what order.

## When and what it produces

- **Cadence:** weekly. `Www` is the ISO week number (e.g. `2026-W25`).
- **Output:** `90_runs/YYYY-Www-review.md` (a working artefact, C4).
- **Side effects:** the memory reaper runs as step 4; capture-back journal entries may be minted
  (step 6). No external send, publish, or commit happens inside the review without the gate.

## Steps

1. **Copy the template.** Copy [`../40_templates/weekly-review.md`](../40_templates/weekly-review.md)
   to `90_runs/YYYY-Www-review.md`. Set `week_of` to the Monday under review and `reviewed_on` to
   today. Fill `sources_scanned` as you go, so every later line traces to where it came from
   (**source-or-abstain**: a line with no source reads "no source", never a guess).

2. **Scan the week's runs for patterns.** Read the `90_runs/` files dated within the week: filled
   decision packets, daily briefs, prior reviews. Look for what actually shipped, and for repeats
   that a single atom or procedure should now capture (the same friction handled twice, the same
   question asked twice). Fill section 1 (what shipped) and note recurrence candidates for step 6.
   Do not invent outcomes the run files do not record.

3. **Reconcile the registers for drift and stale items.** Read the live decision registers and the
   per-project loops, and check them against the run folders and against each other:
   - [`../50_registers/decision-log.md`](../50_registers/decision-log.md) — pull this week's decisions
     and their reversibility tier into section 2. Append-only; do not re-litigate.
   - [`../50_registers/decision-queue.md`](../50_registers/decision-queue.md) — list items still open
     (carried, not decided); the queue stays the live truth.
   - [`../80_projects/`](../80_projects/index.md) — read each project's `loops.md` `## Open` table;
     list loops still open into section 3 and flag any past its `due` (`overdue`) or older than
     expected. A loop that now needs a founder decision moves to the queue with a Decision Packet and
     is marked `blocked` there, not guessed at here.
   - **Mismatches** (a register that disagrees with a run folder, or two registers that disagree)
     go in section 4 with which one is right and the source. The journal is the tiebreak.
   When the `measurement.md` register has data, scan its hand-tracked metrics here too and record
   any that moved against the North Star.

4. **Run the memory reaper.** Run [`memory-reaper.md`](memory-reaper.md) with an
   explicit `--as-of` of today's date, so the pass is reproducible. It folds the week's journal
   entries into the atoms projection, dedups, gates, decays, budgets, and tiers. Then read
   the reaper build marker it writes (`20_memory/_meta/build.md`, regenerated locally) and record the run note in
   section 5: the `--as-of` used, the counts (promoted / merged / demoted / quarantined / archived),
   and whether the stability check aborted. If it aborted, link the churn-alert file it wrote and do
   not force it; flag it for the founder.

5. **Surface staleness the reaper cannot decide.** The reaper handles atom decay and budgets. The
   review handles the rest: doctrine or schemas (C3) that a week's events have contradicted, and
   atoms marked `stale` or past `last_verified + valid_for` that need a human re-verify. Record
   these in section 4. **Do not silently rewrite C3 reference or doctrine** — propose a diff for
   review per the safety gate. **signpost, don't advise**: surface what diverged and the options;
   the founder decides whether to change it.

6. **Capture-back.** Anything durable that surfaced in steps 2 to 5 (a repeated lesson, a procedure
   that earned its place, a preference the founder stated) is written back as a new
   `20_memory/journal/` entry so the next reaper run can mint it. The review file itself is a run
   artefact, not memory; the journal is where durable learning lands. Record the journal refs minted
   in section 5, or "none".

7. **Re-prioritise.** Fill section 6 with three to five ranked priorities for the coming week. Each
   one is an existing open loop, a queued decision, or a new journal-backed intent — nothing here is
   a fresh commitment invented in the review. This is the **signpost** into next week, not a plan
   committed on the founder's behalf.

8. **Close out.** Save the review file. If the review surfaced anything needing a decision, confirm
   it sits in the decision queue with a packet. Per the gate, a git commit of the week's work is
   confirmed with the founder, not done silently.

## Invariants

- The review reads and summarises; it does not decide. Decisions live in the queue and log, made
  through Decision Packets, not minted inside the review (**signpost, don't advise**).

- Every line in the output traces to a run file, a register row, a journal entry, or `build.md`
  (**source-or-abstain**). An empty section reads "none this week", never padding.

- The journal is never edited by the review; durable findings become NEW journal entries
  (**capture-back**).

- No external send, publish, or commit happens from inside the review without explicit approval per
  the safety gate.

## What this defers

No automated drift detector, no scheduled run, no metrics dashboard, no scoring of the week. At
solo volume the hand pass over a handful of run files and the registers is sufficient. The pass
graduates to software only when it has run by hand for the value-gate window and consistently costs
more than the threshold to assemble (design-spec §9).

## Related

- [Weekly review template](../40_templates/weekly-review.md)
- [Memory reaper — the fast consolidation pass](memory-reaper.md)
- [Decision log (append-only)](../50_registers/decision-log.md)
- [Decision queue — open founder decisions](../50_registers/decision-queue.md)
- [Active projects](../80_projects/index.md)
