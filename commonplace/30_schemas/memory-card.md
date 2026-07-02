---
id: <<workspace_slug>>.schema.memory-card
name: Memory card (atom) schema
type: schema
layer: C2
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [schema, memory, atom, 5w1h, frontmatter, act-r, depth-layers]
related:
  - {ref: 00_meta/memory-architecture.md, dimension: why, polarity: derived_from}
  - {ref: 20_memory/README.md, dimension: what, polarity: explains}
  - {ref: 30_schemas/event.md, dimension: why, polarity: derived_from}
---

# Memory card (atom) schema

An atom is one Markdown file in a **depth layer** (`20_memory/{working,short-term,long-term,
subconscious}/`). Body = the human-readable claim; frontmatter = the machine-checkable footprint.
Every field maps to a future SQL column so the file store graduates to a database + vector + graph as
a migration. The reaper sets the derived fields (activation, tier, layer transitions); humans set the
authored ones (the claim, sources, pivotal mark).

## Frontmatter

```yaml
---
id: <<workspace_slug>>.atom.<slug>
type: lesson | procedure | tool-recipe | legislation | preference | observation | decision | association | prior
class: observational | procedural | normative      # now a TAG, not a folder
layer: working | short-term | long-term | subconscious   # the depth axis; reaper moves this

# 5W1H footprint
who: [entity-ref, ...]
what: <one-line claim>
where: [channel/system/market/doc, ...]
when: YYYY-MM-DD
why: [cause | justification | goal, ...]
how: [tool | process | policy, ...]

# provenance (MANDATORY — empty sources => quarantined)
sources: [journal/YYYY-MM-DD-HHMM-x.md#L4-12, ...]

# typed relationships (the 5W1H graph)
related:
  - {ref: 20_memory/long-term/y.md, dimension: who|what|where|when|why|how,
     polarity: supports|contradicts|causes|enables|blocks|requires|explains|derived_from|supersedes}

# trust & salience
trust_tier: 1-5          # 5 exact/source-grounded · 4 direct user · 3 corroborated · 2 weak · 1 speculative
importance: 0.0-1.0
assertable: true         # subconscious atoms default FALSE: they prime, they do not assert

# activation (ACT-R; reaper-maintained)
activation_base: 0.0     # ln(sum (t-t_j)^-d) + W
touches: [YYYY-MM-DDTHH:MM:SSZ, ...]   # mentions + successful retrievals + reviews (last ~12)
retrieval_count: 0
last_retrieved: <ts>

# durability invariants
pivotal: false           # founder-marked or decision-critical
do_not_drop: false       # true => bypasses the decay/demotion loop entirely

# validity (S-VALID + temporal)
status: current | aspirational | stale | superseded
superseded_by: <ref>     # set on supersession (never overwrite)
supersedes: <ref>
last_verified: YYYY-MM-DD
valid_for: 30d | until-superseded | permanent     # staleness window per layer default
valid_from: <date>       # optional: temporal validity of the fact itself
valid_to: <date>

# homeostasis
tier: hot | warm | cold  # reaper-set from recency + inbound links
content_hash: <hash of normalised `what`>          # dedup key, first-writer-wins
sector: [...]            # optional tags
jurisdiction: [...]      # legislation atoms only
---
```

## Rules

1. **Evidence chain:** `sources` non-empty, pointing at `journal/` entries; else quarantined.
2. **Source-or-abstain:** an unsourced legal/factual claim is not stated as fact — `aspirational`/`[VERIFY]`.
3. **One claim per atom** (one canonical card per fact-family; repeated evidence strengthens, it does not duplicate).
4. **Non-drop invariant:** `pivotal`/`do_not_drop` atoms bypass decay; they can only be superseded, never demoted out.
5. **Supersession, not deletion:** a newer atom with the same `(entity, relation)` key supersedes; the old one gets `superseded_by` and archives.
6. **assertable:** normal atoms `true`; subconscious associations/priors default `false` (they bias retrieval, they never enter context as asserted facts).
7. **Promotion by decision-impact first, mention-count last** (see `homeostasis.yml`).

## Layer notes

- **working** atoms are ephemeral (open loops, live constraints); folded into the journal and dropped at day's end.
- **short-term** atoms decay (default `valid_for: 30d`); promote on the signals or decay to `archive/`.
- **long-term** atoms are canonical and durable; pivotal ones permanent.
- **subconscious** atoms are low-weight, `assertable: false` (associations, priors, world-model snapshots, trend signals).

## Related

- [Memory architecture (research-backed, v2)](../00_meta/memory-architecture.md)
- [Memory structure — the model](../20_memory/README.md)
- [Journal event schema](event.md)
