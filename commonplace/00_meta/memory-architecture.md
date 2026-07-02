---
id: <<workspace_slug>>.meta.memory-architecture
name: Memory architecture (research-backed, v2)
type: design-spec
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
source: deep-research on layered cognitive memory, reconciled with an event-sourced homeostasis model
tags: [memory, cognitive-architecture, consolidation, forgetting, act-r, subconscious, world-model]
related:
  - {ref: 20_memory/README.md, dimension: what, polarity: explains}
  - {ref: 10_doctrine/memory-homeostasis.md, dimension: why, polarity: requires}
  - {ref: 60_workflows/memory-reaper.md, dimension: how, polarity: requires}
  - {ref: 60_workflows/memory-sleep.md, dimension: how, polarity: requires}
---

# Memory architecture (v2)

The authoritative memory design: an event-sourced spine (journal + projection + reaper) plus a
deep-research-backed depth model. `20_memory/README.md` is the operator's view of it.

## The model: one truth, four projections sorted by depth

```text
journal/  (Layer 0 — immutable truth, append-only, never pruned)
   │  deterministic folds (forgetting happens only here, never in the journal)
   ▼
working/        depth 1  current task state, open loops, active constraints   (ephemeral)
short-term/     depth 2  recent episodes, cooling facts awaiting proof         (days→~90d, decays)
long-term/      depth 3  canonical cards: facts, preferences, SOPs, landmarks  (months→years)
subconscious/   depth 4  sparse association graph + priors + world-model + trends (primes, never asserts)
```

Memory gets **smaller and sharper as it gets deeper.** The journal stays large; the deep layers are
selective. A card survives because it became *useful, corroborated, and compressible* — not because
it was mentioned once. This is Atkinson-Shiffrin (multi-store) + Complementary Learning Systems
(fast episodic capture, slow durable curation), implemented as event-sourcing.

Where we follow cognition loosely and diverge sharply: in the brain, forgetting can destroy the
trace; here, **forgetting only drops an item from a projection** — the journal entry is permanent,
so any period is fully recoverable. That is the guarantee that makes aggressive forgetting safe.

## The four layers

| Layer | Holds | Lifespan | Budget (default) | Enters when | Leaves when |
|---|---|---|---|---|---|
| **working** | active task, open loops, live constraints, just-retrieved evidence | minutes→days | ≤ ~2.5k tokens, 4–8 items | current session; direct instruction; high-rank hit | task closed / 24h stale → demote |
| **short-term** | recent episodes, commitments, cooling facts not yet durable | days→~90d | ≤ ~200 items + ~20 dossiers | recurrence, reuse, open-loop, or explicit mark | activation < exit threshold, or promotes |
| **long-term** | canonical cards: facts, preferences, procedures/SOPs, relationships, landmark decisions, recurring patterns | months→years | target ≤ ~2000 cards; one canonical card per fact-family | corroborated + reused + stable, or `pivotal` mark | never deleted from journal; non-pivotal cards may archive |
| **subconscious** | sparse typed association graph, low-weight priors, world-model snapshots, trend signals | months→years (weak edges decay) | top ~20 edges/node, weight floor ~0.15 | co-occurrence, confirmed relations, periodic synthesis | edge decays below floor, or superseded |

Class (`observational` / `procedural` / `normative`) is a **frontmatter tag**, not a folder — the
depth layer is the primary axis.

## Activation, consolidation, forgetting

**Retrieval ranking — ACT-R base-level activation** (rewards recency *and* spaced reuse):

```text
A_i = ln( Σ_j (t − t_j)^(−d) ) + W_i        d ≈ 0.5
W_i = w1·importance + w2·trust + w3·assoc_prime + w4·surprise + w5·decision_impact
        − w6·conflict − w7·obsolete
```

**Layer membership — hysteresis** (separate from ranking; prevents thrash): enter a layer at a high
threshold, leave only at a lower one (e.g. short-term enter 1.6 / exit 1.1; long-term enter 2.4 /
exit 1.5). Parameters live in `20_memory/homeostasis.yml`.

**Promotion signals** (short-term → long-term), strongest first: explicit `pivotal` mark · decision
impact (drove a commitment/SOP/deadline) · recurrence (same fact-family on ≥3 distinct days/60d) ·
reuse (≥4 successful retrievals/90d) · prediction-error/surprise (contradicts the current world
model) · salience (high-trust source, high downstream effect). **Decision-impact outranks
mention-count.** Consolidation is by **canonical fact-family**, not transcript chunk, so repeated
evidence strengthens one card instead of breeding summaries.

**The non-drop invariant:** a `pivotal: true` / `do_not_drop: true` card bypasses the decay loop
entirely. It is structurally impossible for a projection to drop it; updates create a supersession
chain, never an overwrite. This is "remember the pivotal points from years ago" made a guarantee.

## Two passes (two-speed consolidation)

- **Fast pass (reaper)** — after each session or every N events. **Fully deterministic.** Folds new
  journal events, updates activation, promotes/demotes by the thresholds, merges fact-families, marks
  supersessions. Spec: `60_workflows/memory-reaper.md`.

- **Deep pass (sleep)** — nightly/weekly, the only place a bounded LLM touches memory. Reads only
  changed items (capped), and emits **strict source-linked JSON** (`{claim, support_event_ids,
  confidence, changed_entities, proposed_edges}`). A deterministic validator **rejects any claim
  without support and any newly-invented named entity.** The LLM never writes prose into durable
  layers. This is replay/consolidation + the subconscious synthesis. Spec: `60_workflows/memory-sleep.md`.

## The subconscious layer

A derived **prior over interpretation and retrieval — never a second hidden truth.** Implemented as
a sparse typed association graph (5W1H + polarity/causal edges), low-weight prior cards, periodic
world-model snapshots, and trend signals. Every edge carries `weight`, `trust_tier`, validity
window, `assertable` (**default false**), and `source_event_ids`. Only an edge backed by a canonical
long-term card or a direct source may become assertable.

- **Minimal mode (v1, file-native):** a co-occurrence matrix for priming; deterministic trend stats
  over journal time-series (moving average, Theil-Sen slope, change-point) for "notice trends".

- **Ambitious mode (deferred):** temporal KG with validity windows + PageRank-style activation
  spreading for priming + community summaries. Behind the value-gate.

Priming rule: spreading activation adds a *small* bonus to retrieval candidates; it can never outrank
exact evidence, and it never injects asserted facts into context.

## Retrieval (deterministic first)

1. Intent filter (subjects, time window, trust floor, exact-vs-fuzzy).
2. Lexical candidates: subject ids, aliases, filenames, tags, links, dates, BM25/ripgrep.
3. Layer preference: operational → working/short-term; durable → long-term; global/trend → subconscious snapshots.
4. Semantic fallback (optional): vectors only over trust- and layer-eligible items.
5. Association priming: spread 1–2 hops, small score bonus only.
6. Auditable ranking + trust-floor exclusion; any asserted claim must cite a support event or card.

`score = 0.35 lexical + 0.20 activation + 0.15 importance + 0.10 recency + 0.10 trust + 0.05 semantic + 0.05 assoc_prime`

## Trust tiers

`5` exact / source-grounded · `4` direct user assertion · `3` corroborated derived · `2` weak derived
· `1` speculative. The retrieval trust-floor and the promotion rules read this.

## Evaluation (prove it gets sharper, not larger)

A small single-user harness built from the journal (gold facts, invalidated facts, open-loop tasks,
trend questions, a noise set). Metrics + v1 targets: precision@10 ≥0.80 · recall@10 ≥0.85 ·
signal-to-noise ≥0.60 and rising · consolidation precision ≥0.85 · supersession (forgetting-aware)
accuracy ≥0.90 · world-model claim support-coverage ≥0.95 · trend lead-time ≤14d. Spec:
`20_memory/evaluation.md` + `50_registers/measurement.md`.

## Prior art (borrow, don't adopt)

Generative Agents (recency-importance-relevance retrieval, reflection — but avoid reflection-of-
reflection bloat); MemGPT/Letta (tiered/virtual context — but be event-sourced, not mutable blocks);
Mem0 (selective extraction — but keep provenance); A-MEM (atomic linked notes — but bound drift);
Zep/Graphiti (temporal KG with validity windows — the deferred ambitious mode); GraphRAG (community
summaries — rare deep-pass only); SOAR/ACT-R (typed memory + activation — the conceptual template);
Titans/long-context (a reminder that capacity ≠ durable, auditable, selectively-forgetting memory).

## Build path

v1 file-native (this) → add async deep-pass synthesis + co-occurrence priming → graduate to a
database (JSONB/vector + a derived temporal graph) **only** when long-term exceeds ~10k cards OR
file retrieval latency exceeds ~200ms. Markdown remains the backup source of truth after migration.

## Anti-patterns (and the guard)

Summary swamp → build long-term from journal ground truth, never summarise summaries; ACT-R decay +
hysteresis prune the rest. Capture-tax → all consolidation/embedding is async, never blocks a turn.
Hallucinated consolidation → the deep-pass validator rejects unsupported claims and new entities.
Drift → supersession chains + immutable journal. Premature complexity → graph/vectors stay behind the
value-gate.

## Related

- [Memory structure — the model](../20_memory/README.md)
- [Memory homeostasis — why the store will not bloat](../10_doctrine/memory-homeostasis.md)
- [Memory reaper — the fast consolidation pass](../60_workflows/memory-reaper.md)
- [Memory sleep — the deep consolidation & synthesis pass](../60_workflows/memory-sleep.md)
