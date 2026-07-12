---
id: <<workspace_slug>>.reference.memory-map
name: Workspace reference — memory map
type: reference
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [reference, memory]
related:
  - {ref: reference-notes/00-INDEX.md, dimension: where, polarity: part_of}
  - {ref: 20_memory/README.md, dimension: where, polarity: explains}
---

# Workspace reference — memory map

> Decomposed 2026-07-12 under the context-decomposition rule (10_doctrine/context-decomposition.md); wording unchanged.

Folder map: [00-INDEX.md](00-INDEX.md).

## Memory map

| Location | Meaning |
|---|---|
| `20_memory/journal/` | Append-only ground truth; corrections and retractions are new events. |
| `20_memory/working/` | Small, hottest set for immediate work. |
| `20_memory/short-term/` | Current useful atoms outside the working budget. |
| `20_memory/long-term/` | Durable, repeatedly supported memory. |
| `20_memory/subconscious/` | Non-assertable associations, priors, trends, and world-model cues. |
| `20_memory/archive/` | Cold, expired, or superseded atoms retained for recall. |
| `20_memory/_quarantine/` | Invalid or unsourced atoms awaiting review. |
| `20_memory/_meta/` | Rebuild markers and sleep state; generated rather than authoritative. |
| `20_memory/homeostasis.yml` | Working-set budgets, decay, hysteresis, promotion, and sleep set-points. |

Search it:

```bash
python3 tools/recall-tiered.py <search words>
```

Add `--all` to search every depth, `--follow` for one-hop links, or `--touch` only when retrieval
should strengthen the matching atom. The full model is in [`20_memory/README.md`](../20_memory/README.md).

## Related

- [Reference notes index](00-INDEX.md)
- [Memory](../20_memory/README.md)
