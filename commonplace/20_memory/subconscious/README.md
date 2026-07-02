---
id: <<workspace_slug>>.memory.subconscious
name: Subconscious layer (depth 4)
type: reference
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [memory, subconscious, depth-4, associations, priors, world-model, trends]
related:
  - {ref: 60_workflows/memory-sleep.md, dimension: how, polarity: requires}
  - {ref: 00_meta/memory-architecture.md, dimension: why, polarity: derived_from}
---

# Subconscious layer (depth 4)

A **derived prior over interpretation and retrieval — never a second hidden truth.** It shapes what
the agent notices and how it reads new input (priming), and it builds a world model and spots trends.
It does **not** assert facts: every item here is `assertable: false` by default. It can supply
evidence and bias ranking; it can never create authority.

| Subfolder | Holds |
|---|---|
| `associations/` | sparse typed edges between memories/entities (5W1H + polarity/causal); `weight`, validity window, `source_event_ids`; capped at ~20 edges/node, floor ~0.15 |
| `priors/` | low-weight standing biases ("sector X + new legislation → anxiety spike → wedge"); decay on a half-life |
| `world-model/` | periodic snapshots `<YYYY-MM>.md` (changed entities, stable vs invalidated claims, new patterns, open questions) |
| `trends/` | trend signals from deterministic time-series stats (moving average / Theil-Sen / change-point) over the journal, with lead-time |

Built by the **sleep pass** (`../../60_workflows/memory-sleep.md`), under strict guardrails: bounded
input, strict source-linked JSON output, a deterministic validator that rejects unsupported claims and
new entities. Retrieval uses this layer only as a **small priming bonus** that can never outrank
exact evidence (`../homeostasis.yml: subconscious.priming_score_weight`).

**Minimal mode now:** a co-occurrence matrix for priming + deterministic trend stats. **Ambitious
mode (deferred behind the graduation trigger):** a full temporal knowledge graph with PageRank-style
activation spreading and community summaries.

All four subfolders start empty; the sleep pass populates them once the journal has weeks of entries.

## Priming discipline (how nudges enter context)

Priors surface as **hypotheses, never facts**, under strict limits: at most ~3 nudges per turn, ≤80
words total, only priors above confidence ~0.55, only when related to the current target, always
phrased as a hypothesis, always source-linked. A nudge biases attention; it is never cited as
evidence.

## Anti-superstition (the confirmation-bias guard)

A prior is **not** validated just because an action was taken on it. Log two SEPARATE journal events:
`prior.used` (the prior shaped a choice) and `prior.outcome` (what actually happened). Only a real
outcome moves confidence — a caught regression or a confirmed signal, not mere use. Without this
split the system reinforces its own hunches ("agent superstition").

## Related

- [Memory sleep — the deep consolidation & synthesis pass](../../60_workflows/memory-sleep.md)
- [Memory architecture (research-backed, v2)](../../00_meta/memory-architecture.md)
