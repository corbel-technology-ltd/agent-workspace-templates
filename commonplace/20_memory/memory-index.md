---
id: <<workspace_slug>>.memory.memory-index
name: Memory retrieval convention
type: reference
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [memory, retrieval, ranking, context-loader, act-r]
related:
  - {ref: 00_meta/memory-architecture.md, dimension: why, polarity: derived_from}
  - {ref: 20_memory/README.md, dimension: what, polarity: explains}
---

# Memory retrieval convention

Deterministic first, semantic second, subconscious as a small bonus only. Built for provenance and
low false positives, not vector-search vibes.

## Pipeline

1. **Intent filter** — target subjects, time window, trust floor, exact-recall vs fuzzy-explore.
2. **Lexical candidates** — subject ids, aliases, filenames, titles, tags, `related:` links, dates;
   BM25 / a deterministic frontmatter loader / ripgrep over journal + projections.

3. **Layer preference** — operational query → `working/` + `short-term/`; durable → `long-term/`;
   global/trend → `subconscious/world-model` + `trends`.

4. **Semantic fallback (optional)** — vectors only over trust- and layer-eligible items, when lexical
   misses. Deferred until the graduation trigger; a cross-cutting semantic surface is the interim.

5. **Association priming** — spread activation 1–2 hops over `subconscious/associations`; add a *small*
   score bonus. Never injects asserted facts; never outranks exact evidence.

6. **Audit + trust floor** — exclude `trust_tier < request floor`; any claim stated as fact must cite a
   support journal event or canonical card.

## Ranking

```text
score = 0.35*lexical + 0.20*activation + 0.15*importance + 0.10*recency
      + 0.10*trust + 0.05*semantic + 0.05*assoc_prime
```

`activation` is the ACT-R base-level value (`homeostasis.yml`). Weights are tunable there.

## Rules

- **`untrusted` atoms are excluded** from assembled context (present on disk, never in a prompt);
  `review` atoms surface with a caveat.

- **Tier order:** `hot` first under a token budget; `cold` last. Low-tier atoms stay present but quiet.
- **Never trust a single retrieval answer for a high-stakes claim** — cross-check the cited source.
- Missing frontmatter = invisible to retrieval. Every atom carries it.

## Related

- [Memory architecture (research-backed, v2)](../00_meta/memory-architecture.md)
- [Memory structure — the model](README.md)
