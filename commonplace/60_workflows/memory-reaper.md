---
id: <<workspace_slug>>.workflow.memory-reaper
name: Memory reaper — the fast consolidation pass
type: workflow
layer: C2
status: current
owner: shared
staging: v1-now
created: <<CREATED_DATE>>
tags: [workflow, memory, reaper, consolidation, act-r, deterministic]
related:
  - {ref: 20_memory/homeostasis.yml, dimension: how, polarity: requires}
  - {ref: 60_workflows/memory-sleep.md, dimension: how, polarity: complements}
  - {ref: 00_meta/memory-architecture.md, dimension: why, polarity: derived_from}
---

# Memory reaper — fast pass

The **fast, fully deterministic** consolidation pass. Runs after each session or every N journal
events. No LLM. Folds the journal into the depth-layer projections and keeps activation/membership
correct. Idempotent; takes an explicit `--as-of <date>`. Set-points: `20_memory/homeostasis.yml`.

(The deep, LLM-assisted restructuring — schema/world-model/trend synthesis — is the separate
`memory-sleep.md` pass. Keep them separate: fast = deterministic membership; deep = bounded synthesis.)

## Steps

1. **Fold.** Read `journal/` since `_meta/build.md`'s watermark; deterministically extract candidates
   (facts, commitments, corrections, closures, explicit `pivotal` marks). Re-read current atoms.

2. **Merge into fact-families.** Group candidates by `(entity, relation)` / `content_hash`
   (normalise: lowercase + collapse-whitespace). First-writer-wins; repeated evidence **strengthens
   the one canonical card** (adds a `touch`, bumps activation) rather than creating a duplicate.

3. **Score activation.** For each atom compute the ACT-R base-level activation
   `A = ln(Σ (t−t_j)^−decay) + W` from `touches` and the `W` weights in `homeostasis.yml`.

4. **Promote / demote by hysteresis.**
   - Explicit `pivotal` (+ trust ≥4) → long-term, `do_not_drop: true`.
   - Else short-term→long-term if `A ≥ long_term_enter` AND trust ≥ `min_trust_for_long` AND
     (recurrence ≥ `min_recurrence_days` OR retrievals ≥ `min_retrievals_90d` OR decision-impact).
   - working/short-term items below their `*_exit` threshold (and not an open loop) demote a layer.
   - Decision-impact outranks mention-count throughout.
5. **Decay & validity.** Recompute `status` from `last_verified` + `valid_for` vs `--as-of`. Long-term
   non-pivotal cards below `long_term_exit` for ≥3 months → `archive/`. **`pivotal`/`do_not_drop`
   atoms bypass this loop entirely** (the non-drop invariant — structurally cannot be demoted).

6. **Supersession.** Per `(entity, relation)` key the freshest valid non-superseded atom wins; mark
   the prior `status: superseded`, set `superseded_by`. Never overwrite.

7. **Tier.** Recompute `tier` (hot/warm/cold) from recency + inbound `related:`/link count.
8. **Budgets.** Per tag over `max_atoms_per_tag` (or set over `long_term_target_cards`) → merge or
   demote lowest-tier atoms to `archive/`, never below `redundancy_floor_per_entity`.

9. **Stability check.** If this pass would rewrite > `churn_freeze_pct` of atoms, **abort** and write
   `20_memory/_review/churn-alert.md` instead of thrashing.

10. **Record.** Update `20_memory/_meta/build.md`: `--as-of`, watermark, set-points version, and counts
    (by layer; promoted / demoted / archived / quarantined / merged).

## Invariants enforced

Every promoted atom cites non-empty `sources:` (else `_quarantine/`). The journal is never mutated.
`untrusted` atoms are never promoted and never enter assembled context. Trust only escalates.
`pivotal`/`do_not_drop` atoms never demote. A contrary journal entry (`corrects:`/`retracts:`)
overrides its atom at the next pass — fold-driven, survives re-import.

## Implementation

Implemented deterministically at [`../core/hooks/reaper.py`](../core/hooks/reaper.py), wired to run
at **session end** by the runtime adapter (`core/RUNTIMES.md`). It runs this
fast pass over the existing atom set. The prose-to-atom synthesis (minting NEW atoms from journal
narrative) is the separate LLM **sleep** pass ([`memory-sleep.md`](memory-sleep.md)), still deferred.
Run by hand: `python3 core/hooks/reaper.py --as-of YYYY-MM-DD [--dry-run]`.

## Related

- [Memory homeostasis — the set-points panel (v2, research-backed).](../20_memory/homeostasis.yml)
- [Memory sleep — the deep consolidation & synthesis pass](memory-sleep.md)
- [Memory architecture (research-backed, v2)](../00_meta/memory-architecture.md)
