---
id: <<workspace_slug>>.workflow.memory-sleep
name: Memory sleep - the deep consolidation & synthesis pass
type: workflow
layer: C2
status: current
created: <<CREATED_DATE>>
owner: shared
tags: [workflow, memory, sleep, dream, consolidation, world-model, trends, bounded-llm]
related:
  - {ref: 60_workflows/memory-reaper.md, dimension: how, polarity: complements}
  - {ref: 20_memory/subconscious/README.md, dimension: what, polarity: explains}
  - {ref: 00_meta/memory-architecture.md, dimension: why, polarity: derived_from}
---

# Memory sleep - deep pass

The rare, deep restructuring pass (nightly or weekly) - the software analogue of sleep/replay
consolidation. It is the **only** place an LLM writes into the memory layers, and it is tightly
fenced. It does what the deterministic reaper cannot: abstract schemas, synthesise the subconscious
world-model, and detect slow trends. Runs **asynchronously** (never blocks a turn - avoids the
capture-tax). Bounds and guardrails: `20_memory/homeostasis.yml` (`sleep_pass:`).

## Inputs (bounded)

Only items changed since the last sleep run, capped at `max_changed_items_per_run` (default 50), plus
the relevant slices of the long-term layer and the subconscious graph. Never the whole store.

## Output contract (strict)

The LLM emits **structured JSON only** - never prose into a durable layer:

```json
{
  "claims": [
    {"claim": "...", "support_event_ids": ["evt_..."], "confidence": 0.0,
     "changed_entities": ["..."], "proposed_edges": [{"from":"...","relation":"...","to":"...","polarity":"...","assertable":false}]}
  ]
}
```

## Deterministic validator (runs after the LLM, before anything is written)

Reject a claim if it: cites no `support_event_ids`; introduces a **new named entity** not already in
the store; asserts a contradiction that cannot be traced to a supersession event; or proposes an
`assertable: true` edge without a backing long-term card or direct source. Rejected claims are
logged, not written. This is the anti-hallucination guard - the model proposes, the validator
disposes.

## What it produces

1. **Schema abstraction** - promote recurring short-term patterns into canonical long-term cards
   (gist over verbatim), each still source-linked. Never summarise summaries; build from the journal.

2. **Subconscious synthesis** - strengthen/weaken association edges; mint low-weight priors
   (`assertable: false`); write a `subconscious/world-model/<YYYY-MM>.md` snapshot
   (`scope, period, changed_entities, stable_claim_ids, invalidated_claim_ids, new_patterns, open_questions`).

3. **Trend detection** - over journal time-series, run the deterministic stats in `homeostasis.yml`
   (`moving_average`, `theil_sen_slope`, `change_point`); when a metric or a sentiment polarity shifts
   across successive windows, write a `subconscious/trends/<slug>.md` signal with its lead-time.

4. **Reconsolidation** - when new evidence updates a durable card, append a correction journal event
   and create a supersession chain; never overwrite.

## Implementation (v1, shipped)

The pass is implemented and self-tested; run it via the **memory-sleep skill** (or by hand):

1. `python3 core/hooks/sleep-prep.py` — deterministic: stages unconsolidated journal entries
   (bounded by `max_changed_items_per_run`), extracts entity recurrence + co-occurrence, and
   builds the known-entity universe into `20_memory/_meta/sleep-candidates.json`.
2. The model synthesises `20_memory/_meta/sleep-claims.json` — strict JSON, one claim per durable
   fact-family. v1 extends the contract with `kind`, `importance`, and optional 5W1H fields; the
   core shape above is unchanged.
3. `python3 core/hooks/sleep-apply.py` — the deterministic validator + writer: rejects
   unsupported claims, invented entities, untraceable contradictions, assertable edges, and
   duplicates; writes accepted claims as schema-valid atoms (`short-term/`), association edges
   (`subconscious/associations/`, `assertable: false`), the monthly world-model snapshot, the
   sleep marker and log — then runs the reaper so new atoms tier immediately.

The session brief nudges when `sleep_pass.nudge_after_entries` unconsolidated entries pile up.
Proof: `python3 tools/memory-selftest.py` exercises the full loop (synthesis, every rejection
class, promotion, working projection, hysteresis, expiry, quarantine, idempotency) and runs as
a member gate in the family check.

## Running the pass (the playbook the runtime skills wrap)

1. `python3 core/hooks/sleep-prep.py`, then read `20_memory/_meta/sleep-candidates.json`.
   If `window.count` is 0, report "nothing to consolidate" and stop.
2. Study the staged entries, entity recurrence, and co-occurrence pairs, then write
   `20_memory/_meta/sleep-claims.json` in exactly this shape:

   ```json
   {"claims": [{
       "claim": "<one durable, standalone factual sentence>",
       "kind": "observation | lesson | procedure | preference | decision | tool-recipe",
       "support_event_ids": ["<journal filename>"],
       "confidence": 0.85,
       "changed_entities": ["<entity from known_entities>"],
       "importance": 0.6,
       "why": [], "how": [],
       "pivotal": false, "decision_impact": false, "supersedes": null,
       "proposed_edges": [{"from": "<entity>", "relation": "<verb>", "to": "<entity>",
                           "assertable": false}]}]}
   ```

   Synthesis rules (the validator enforces every one):
   - One claim per durable fact-family - the gist that recurs, not a diary paraphrase. Skip
     one-off events with no forward value; the journal keeps them forever anyway.
   - `support_event_ids` must be real journal filenames from the candidates file.
   - `changed_entities` must come from `known_entities` - never invent an entity.
   - A stated user preference or correction is `kind: preference`, high confidence.
   - A repeated procedure that worked is `kind: procedure` or `tool-recipe`.
   - Something that drove a commitment gets `decision_impact: true`; only mark `pivotal`
     when the principal explicitly called it critical.
   - Edges are sparse and always `assertable: false` (they prime, they never assert).
   - 5-15 quality claims per run beats exhaustive coverage.
3. `python3 core/hooks/sleep-apply.py` - validates, writes, logs, advances the marker, and
   runs the reaper. Report accepted/rejected counts and where atoms landed. A claim rejected
   for a fixable reason can be corrected in the JSON and re-applied (idempotent: duplicate
   hashes are skipped).

Never run mid-task on a half-settled story, and never edit journal entries to make a claim
fit - the journal is append-only.

## Cadence & staging

Run on the brief's nudge, after journal-heavy stretches, or weekly. Minimal mode is live (entity
recurrence + co-occurrence into candidates); the ambitious mode (temporal KG, PageRank priming,
community summaries) stays behind the graduation trigger in `homeostasis.yml`.

## Guardrails (recap)

Bounded input · strict JSON out · deterministic validator · async only · no prose into durable
layers · no new entities · everything source-linked · `assertable: false` by default. AI-minimisation
holds: the LLM is a bounded reasoning step inside a deterministic pipeline, never the authority.

## Related

- [Memory reaper - the fast consolidation pass](memory-reaper.md)
- [Subconscious layer (depth 4)](../20_memory/subconscious/README.md)
- [Memory architecture (research-backed, v2)](../00_meta/memory-architecture.md)
