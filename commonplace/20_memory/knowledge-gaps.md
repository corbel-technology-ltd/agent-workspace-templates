---
id: <<workspace_slug>>.memory.knowledge-gaps
name: Knowledge gaps register
type: register
layer: C1
status: current
owner: shared
staging: v1-now
created: <<CREATED_DATE>>
tags: [memory, knowledge-gaps, ignorance-graph, register]
related:
  - {ref: 30_schemas/knowledge-gap.md, dimension: what, polarity: explains}
---

# Knowledge gaps register

The simplified "ignorance graph": missing or low-confidence 5W1H dimensions that must be filled
before a decision or action can be trusted. A forcing function against acting on under-specified
context — not an autonomous research engine. One row per gap; close or waive only with a reason.

Required dimensions by object type (block a high-risk action until its required gaps are closed):

- decision packet → who, what, when, why, evidence
- external email approval → who, what, where, when, why, how
- payment / contract action → all 5W1H + validation evidence
- research opportunity → who, what, why, how, evidence strength

| id | parent | missing dimension | question | required_for | priority | status |
|---|---|---|---|---|---|---|
| (none yet) | | | | | | |

Statuses: `open` · `investigating` · `answered` · `waived` · `stale`. Route a gap to: search
memory · inspect source · research task · ask founder · daily brief · weekly review · block.

## Related

- [Knowledge gap (row) schema](../30_schemas/knowledge-gap.md)
