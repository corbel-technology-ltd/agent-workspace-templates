---
name: memory-sleep
description: |
  Run the deep memory consolidation ("sleep") pass: synthesise durable memory atoms from
  unconsolidated journal entries and stock the depth layers. Use when the session brief reports
  unconsolidated journal entries, when the user asks to "run sleep", "consolidate memory",
  "fold the journal", or "stock the memory layers", or after any burst of journal-heavy work.
  The model only proposes claims as strict JSON; a deterministic validator writes the atoms.
---

# memory-sleep

The warehouse-stocking pass. The journal is the source of truth; this skill turns its recurring
facts into memory-card atoms that the reaper can then tier. You (the model) are a bounded
reasoning step inside a deterministic pipeline — you propose, `sleep-apply.py` disposes.

## Steps

1. **Prepare candidates (deterministic):**

   ```bash
   python3 core/hooks/sleep-prep.py
   ```

   Read `20_memory/_meta/sleep-candidates.json`. If `window.count` is 0, report "nothing to
   consolidate" and stop.

2. **Synthesise claims.** Study the staged entries, entity recurrence, and co-occurrence pairs.
   Write `20_memory/_meta/sleep-claims.json`:

   ```json
   {
     "claims": [
       {
         "claim": "<one durable, standalone factual sentence>",
         "kind": "observation | lesson | procedure | preference | decision | tool-recipe",
         "support_event_ids": ["<journal filename>", "..."],
         "confidence": 0.85,
         "changed_entities": ["<entity from known_entities>"],
         "importance": 0.6,
         "why": [], "how": [],
         "pivotal": false,
         "decision_impact": false,
         "supersedes": null,
         "proposed_edges": [
           {"from": "<entity>", "relation": "<verb>", "to": "<entity>", "assertable": false}
         ]
       }
     ]
   }
   ```

   Rules — the validator enforces every one of these, so save yourself the rejection:
   - One claim per durable fact-family: the *gist* that recurs, not a diary paraphrase.
     Skip anything that only happened once and carries no forward value.
   - `support_event_ids` must be real journal filenames from the candidates file.
   - `changed_entities` must come from `known_entities` — never invent an entity.
   - A user-stated preference or correction is `kind: preference` with high confidence.
   - A repeated procedure that worked is `kind: procedure` or `tool-recipe`.
   - Something that drove a commitment gets `decision_impact: true`.
   - Only mark `pivotal` for facts the user explicitly called critical.
   - Edges are optional, sparse, and always `assertable: false` (they prime, they never assert).
   - 5-15 claims per run is typical; quality over coverage — the journal remains forever.

3. **Validate + write (deterministic):**

   ```bash
   python3 core/hooks/sleep-apply.py
   ```

   This writes accepted atoms to `20_memory/short-term/`, edges to
   `subconscious/associations/`, a world-model snapshot, the sleep marker and log — then runs
   the reaper so the new atoms are tiered immediately.

4. **Report.** Tell the user: accepted/rejected counts (and why the rejections happened),
   where the atoms landed, and the reaper's resulting layer counts. If a claim was rejected for
   a fixable reason (typo in a filename), fix the JSON and re-run step 3 — apply is idempotent
   (duplicate hashes are skipped).

## When NOT to run

- Mid-task or on a half-finished story arc — sleep consolidates settled facts, not live state.
- When `window.count` is 0.
- Never edit journal entries to make a claim fit: the journal is append-only and immutable.
