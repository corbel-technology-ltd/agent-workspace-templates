---
id: <<workspace_slug>>.memory.evaluation
name: Memory evaluation harness
type: reference
layer: C3
status: awaits-inputs
created: <<CREATED_DATE>>
owner: shared
tags: [memory, evaluation, metrics, sharpness, forgetting-aware]
related:
  - {ref: 00_meta/memory-architecture.md, dimension: why, polarity: derived_from}
  - {ref: 50_registers/measurement.md, dimension: where, polarity: complements}
---

# Memory evaluation harness

How we prove the memory is getting **sharper, not larger**. A small single-user harness built from
the journal, following the better agent-memory benchmarks (LoCoMo, MemoryArena, forgetting-aware
FAMA/Memora). `awaits-inputs`: build the gold set once the journal has real volume.

## The gold set (built from the journal)

- ~150 **gold facts** (durable, each with its exact support journal events).
- ~40 **invalidated facts** (later corrected/superseded — tests forgetting-awareness).
- ~40 **open-loop tasks** whose success depends on prior commitments/preferences.
- ~20 **trend questions** with known change-points.
- a **noise set** of decoy/irrelevant events from the same periods (tests sharpness).

## Metrics + v1 targets

| Metric | Definition | Target |
|---|---|---|
| Precision@10 | retrieved candidates that actually support the query | ≥ 0.80 |
| Recall@10 | gold supports surfaced in top-10 | ≥ 0.85 |
| Signal-to-noise | supporting tokens / total retrieved tokens (must rise over time) | ≥ 0.60, rising |
| Consolidation precision | promoted long-term cards that match human "should-keep" labels | ≥ 0.85 |
| Supersession accuracy | invalidated facts correctly avoided or marked superseded (forgetting-aware) | ≥ 0.90 |
| World-model support coverage | asserted snapshot claims with a valid source | ≥ 0.95 |
| Trend lead-time | median delay between a change-point in the journal and the trend signal | ≤ 14 days |
| Compression-with-retention | journal tokens / active long-term tokens, without dropping a gold pivotal fact | high, rising |
| Action utility | success on memory-dependent tasks across sessions | tracked |

## How to run

Replay the journal up to an `--as-of` date, run the reaper (and sleep pass), then query the gold set
and score. Because passes are deterministic given `(journal, --as-of, set-points)`, the harness is
reproducible. Record runs in `50_registers/measurement.md`.

Two metrics matter most for the stated goal: **signal-to-noise rising over time** (the memory
sharpens) and **supersession accuracy** (it does not keep reusing obsolete facts).

## Related

- [Memory architecture (research-backed, v2)](../00_meta/memory-architecture.md)
- [Measurement register](../50_registers/measurement.md)
