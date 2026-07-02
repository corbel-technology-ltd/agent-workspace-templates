---
id: <<workspace_slug>>.doctrine.memory-homeostasis
name: Memory homeostasis — why the store will not bloat
type: doctrine
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
source: event-sourced memory-subsystem study (deterministic projections over an immutable log)
tags: [doctrine, memory, homeostasis, compression, anti-pollution, event-sourcing]
related:
  - {ref: 20_memory/README.md, dimension: what, polarity: explains}
  - {ref: 60_workflows/memory-reaper.md, dimension: how, polarity: requires}
  - {ref: 20_memory/homeostasis.yml, dimension: how, polarity: requires}
---

# Memory homeostasis

The discipline that keeps memory healthy instead of letting it bloat into "a swamp of low-value
summaries" (non-goal 15). The store is event-sourced with deterministic projections, file-native.

## The ten principles

1. **Separate immutable truth from disposable derived views.** The `journal/` is the only truth and
   is never edited or deleted; the depth layers are a rebuildable projection. Compression and forgetting are
   safe precisely because the source is never lost. Every atom keeps a `sources:` pointer back to
   the journal (verbatim fallback).

2. **Recompute, don't accumulate.** The reaper regenerates atoms from the journal; it overwrites,
   it does not append. Stale rows cannot silently pile up.

3. **Decay needs an equilibrium, not just a downward push.** Validity windows (`last_verified` +
   `valid_for`) give each atom a decay curve; fully-expired atoms leave the active set.

4. **Local homeostasis beats global deletion.** Per-tag budgets (over budget → merge/demote) keep
   the store lean without a global garbage-collect that throws away useful things.

5. **Asymmetric gates stop bloat.** Cheap to create a candidate; expensive to promote (confidence
   bar) and to kill. A hysteresis band (promote ≥0.60, archive <0.30) stops atoms flickering.

6. **Keep a diverse insured minimum.** Never prune a live entity below the redundancy floor; when
   merging duplicates, keep the most distinct/clearest, not the newest.

7. **Quarantine untrusted by default; earn promotion.** `trust` is monotonic — it only escalates via
   review and can never auto-launder. `untrusted` atoms are excluded from assembled context.

8. **Dedup on a content-hash, first-writer-wins.** Identical re-derivation is a no-op; two atoms
   that differ by a meaningful token never merge.

9. **Freshness ≠ validity.** Supersession (which version is current, per `(entity, relation)` key)
   and validity windows (is it true now) are separate concerns; both gate what surfaces.

10. **Deterministic.** The reaper takes an explicit `--as-of` date; same inputs + same set-points →
    same result.

## The reaper contract

The homeostasis pass is specified in [`60_workflows/memory-reaper.md`](../60_workflows/memory-reaper.md):
fold → re-derive candidates → dedup → gate → decay/validity → budget → tier → stability-check →
record. It enforces: every promoted atom cites sources; the journal is never mutated; untrusted is
never promoted; trust only escalates; a contrary journal entry overrides an atom at the next pass.

## The set-points

All tunable in [`../20_memory/homeostasis.yml`](../20_memory/homeostasis.yml): budgets
(`target_total_atoms`, `max_atoms_per_tag`, `redundancy_floor_per_entity`), gates
(`min_recurrence_to_mint`, `promote_confidence_bar`, `archive_confidence_floor`), decay
(`default_valid_for` per class), dedup normalisation, tiering inputs, trust policy, and the
`churn_freeze_pct` circuit-breaker. Nothing is hardcoded elsewhere.

## What we deliberately keep crude

We do not adopt a hash-chained ledger (git is the coarse analogue), conductance/PageRank/Kalman
graph maths, semantic-vector reaping, FFT churn analysis, or a Bayesian re-estimation organ. At solo
volume the crude analogues — inbound links for centrality, validity windows for decay, a
churn-percentage abort for the slowing-down alarm — are enough. These richer organs are reconsidered
only if/when the store graduates to the deferred database software.

## The same anti-sprawl logic applies to the skill library

The reaper governs *atom* bloat. It does not touch the playbook library (`core/` playbooks and
their runtime skill surfaces, where `60_workflows/` graduate). That library sprawls the same way:
count rises monotonically without
active reshaping, and **high count is the failure mode, not the goal**. Periodically ask the question
decay and promotion never ask: would a competent maintainer write this as N narrow skills, or fewer
umbrella skills with labelled sections? A skill with zero uses is absence-of-evidence, not a cull
signal. This is the insight only, no failsafe apparatus or graduation ladder until the library is
big enough to need one (spine-not-leaves).

## Related

- [Memory structure — the model](../20_memory/README.md)
- [Memory reaper — the fast consolidation pass](../60_workflows/memory-reaper.md)
- [Memory homeostasis — the set-points panel (v2, research-backed).](../20_memory/homeostasis.yml)
