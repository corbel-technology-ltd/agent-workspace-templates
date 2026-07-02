---
id: <<workspace_slug>>.template.memory-card
name: Memory card (atom) template
type: template
layer: C2
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [template, memory, atom, 5w1h, frontmatter]
related:
  - {ref: 30_schemas/memory-card.md, dimension: what, polarity: derived_from}
  - {ref: 20_memory/README.md, dimension: what, polarity: explains}
---

# Memory card template

Copy the block below into `20_memory/<layer>/<slug>.md`, fill every field, and write the
claim in the body. One claim per atom. Empty `sources:` means the atom is quarantined, so cite a
journal entry. For a legal/statutory/factual claim with no primary source, set
`status: aspirational` and name what is unknown (source-or-abstain). Schema:
`30_schemas/memory-card.md`.

```markdown
---
id: <<workspace_slug>>.atom.<slug>
type: lesson | procedure | tool-recipe | legislation | preference | observation | decision
class: observational | procedural | normative

# 5W1H footprint
who: []                                 # people/orgs/agents/systems involved
what: ""                                # one-line claim this atom asserts
where: []                               # channel/system/market/doc
when: YYYY-MM-DD                        # when it occurred / became true
why: []                                 # cause/justification/goal
how: []                                 # tool/process/policy

# provenance (MANDATORY — empty sources => quarantined)
sources: []                             # journal/YYYY-MM-DD-HHMM-<slug>.md#L4-12

# typed relationships (the 5W1H graph, expressed as edges)
related:
  # - {ref: 20_memory/long-term/y.md, dimension: who|what|where|when|why|how,
  #    polarity: supports|contradicts|causes|enables|blocks|requires|explains|derived_from|supersedes}

# trust & confidence
confidence: 0.50                        # 0.0-1.0; up on corroboration, down on contradiction
trust: review                           # trusted | review | untrusted (monotonic; untrusted is retrieval-excluded)

# validity (S-VALID)
status: current                         # current | aspirational | stale | superseded
superseded_by:                          # only when status: superseded
last_verified: YYYY-MM-DD
valid_for: 30d                          # 30d | until-superseded | permanent
tier: warm                              # hot | warm | cold (set by the reaper)
content_hash:                           # hash of normalised `what` (dedup key)
sector: []                              # optional tags
jurisdiction: []                        # legislation atoms only, e.g. [uk]
---

One-line claim restated for a human, then the evidence/inference/speculation split that justifies
the confidence. Mark unverified factual claims [VERIFY].
```

## Related

- [Memory card (atom) schema](../30_schemas/memory-card.md)
- [Memory structure — the model](../20_memory/README.md)
