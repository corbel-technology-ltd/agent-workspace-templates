---
id: <<workspace_slug>>.memory.model
name: Memory structure - the model
type: reference
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [memory, 5w1h, homeostasis, event-sourcing, depth-layers, consolidation]
related:
  - {ref: 00_meta/memory-architecture.md, dimension: what, polarity: derived_from}
  - {ref: 10_doctrine/memory-homeostasis.md, dimension: how, polarity: explains}
  - {ref: 30_schemas/memory-card.md, dimension: what, polarity: explains}
  - {ref: 60_workflows/memory-reaper.md, dimension: how, polarity: requires}
---

# Memory structure

A memory that **gets sharper as it gets deeper**: pivotal facts from years ago are kept, the
surrounding noise decays out. Event-sourced, sorted by depth. Full design + the research behind it:
[`../00_meta/memory-architecture.md`](../00_meta/memory-architecture.md).

## One truth, four projections by depth

```text
journal/        depth 0   the ONLY truth: append-only, immutable, never pruned
   │  deterministic folds (forgetting happens only below here, never in the journal)
   ▼
working/        depth 1   what's in hand now (open loops, live constraints)     ephemeral
short-term/     depth 2   recent episodes + cooling facts                       days→~90d, decays
long-term/      depth 3   canonical cards (facts/preferences/SOPs/landmarks)     months→years, selective
subconscious/   depth 4   associations + priors + world-model + trends          primes, never asserts
```

Each layer is a **rebuildable fold** over the journal. Because the journal is permanent, the upper
layers can decay, dedup, merge, and forget aggressively without ever losing anything - "forgotten"
means "no longer surfaced", not "deleted". This is the model that keeps memory sharp.

## The unit: a memory card (atom)

A Markdown file carrying the **5W1H footprint** + provenance + trust + the activation/validity
fields. Schema: [`../30_schemas/memory-card.md`](../30_schemas/memory-card.md). Mandatory rule: every
atom cites `sources:` into the journal; an atom with none is quarantined. `class:`
(observational/procedural/normative) is a tag; the depth layer is the folder.

## How an item moves (consolidation)

Enters as a journal event → the reaper folds it into a short-term atom → if **reinforced** (decision
impact, recurrence ≥2, reuse, surprise, or an explicit `pivotal` mark) it **consolidates** to
long-term; if not, it decays and archives. Ranking uses ACT-R base-level activation; layer membership
uses hysteresis (enter high, leave low) to avoid flicker. **`pivotal`/`do_not_drop` cards bypass decay
entirely.** Set-points: [`homeostasis.yml`](homeostasis.yml).

## Two passes

- **Reaper (fast, deterministic)** - every session / N events: membership, decay, supersession.
  [`../60_workflows/memory-reaper.md`](../60_workflows/memory-reaper.md).

- **Sleep (deep, bounded LLM)** - nightly/weekly: schema abstraction, subconscious synthesis, trend
  detection; strict source-linked JSON + a deterministic validator.
  [`../60_workflows/memory-sleep.md`](../60_workflows/memory-sleep.md).

## Housekeeping folders

`journal/` (truth) · `_quarantine/` (untrusted/sourceless, awaiting review) · `archive/`
(superseded/expired, verbatim fallback) · `_meta/build.md` (last reaper run) · `_review/`
(churn-alerts, created on demand).

## Retrieval & reconciliation

Deterministic loader first (frontmatter/tags/links), a semantic surface second; the subconscious
primes with a small bonus only. Convention: [`memory-index.md`](memory-index.md). Git is the
journal's tamper-evidence; a database + vector + graph store is deferred behind the graduation
trigger.

## Instance state

The memory **starts empty**: no atoms, no journal entries. The model above is carried; the content
accrues as the workspace runs. The four depth layers and `journal/` carry READMEs; the housekeeping
folders (`_quarantine/`, `archive/`, `_meta/`, the `subconscious/` subfolders) ship as empty
directories held in git by a `.gitkeep`.

## Related

- [Memory architecture (research-backed, v2)](../00_meta/memory-architecture.md)
- [Memory homeostasis - why the store will not bloat](../10_doctrine/memory-homeostasis.md)
- [Memory card (atom) schema](../30_schemas/memory-card.md)
- [Memory reaper - the fast consolidation pass](../60_workflows/memory-reaper.md)
