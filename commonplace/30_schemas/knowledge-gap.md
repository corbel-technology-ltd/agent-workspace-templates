---
id: <<workspace_slug>>.schema.knowledge-gap
name: Knowledge gap (row) schema
type: schema
layer: C2
status: current
owner: shared
created: <<CREATED_DATE>>
staging: v1-now
tags: [schema, memory, 5w1h, ignorance-graph, gap, source-or-abstain]
related:
  - {ref: 20_memory/knowledge-gaps.md, dimension: what, polarity: explains}
  - {ref: 30_schemas/decision-packet.md, dimension: why, polarity: requires}
  - {ref: 30_schemas/memory-card.md, dimension: what, polarity: derived_from}
  - {ref: 10_doctrine/autonomy-and-gates.md, dimension: how, polarity: requires}
---

# Knowledge gap (row) schema

A knowledge gap is one named thing the workspace does not yet know but needs to. Each gap is a
single row in the register `20_memory/knowledge-gaps.md`. This is the **simplified
ignorance-graph**: a hand-maintained list of missing 5W1H dimensions, run by hand over the
filesystem. There is **no engine** that mints gaps automatically; the dissonance and
ignorance-graph engines are deferred (design-spec §9). A human or the agent adds a row when a packet,
sprint, or action surfaces a question with no source.

A gap exists because of **source-or-abstain**: when an answer is missing, the workspace names the
missing fact as an open gap rather than guessing. Closing a gap is the act of finding a source
and writing it back (capture-back) as a journal entry, from which the reaper may mint an atom.

## Fields

| field | values | meaning |
|---|---|---|
| `parent` | ref | what the gap belongs to: an atom (`long-term/x.md`), a decision packet, an opportunity, or a run folder. The thing whose 5W1H footprint has a hole. |
| `missing_dimension` | `who` \| `what` \| `where` \| `when` \| `why` \| `how` | which 5W1H dimension is absent. Mirrors the atom footprint in `memory-card.md`. |
| `question` | text | the one specific thing we do not know, phrased so a found source can close it. One question per row. |
| `required_for` | `decision_packet` \| `execution_validation` \| `research_sprint` \| `meeting_prep` \| `admin_action` \| `customer_response` \| `opportunity_scoring` | the workflow that is waiting on this answer. Drives whether the gap blocks. |
| `priority` | `low` \| `med` \| `high` \| `critical` | how much the waiting work needs it. Set against the parent's reversibility, not the gap's effort. |
| `status` | `open` \| `investigating` \| `answered` \| `waived` \| `stale` | lifecycle (below). |
| `route` | text | where the answer comes from: a research sprint, a named source to read, a person to ask, an intel pass, or `escalate` to the founder. |

Optional: `id` (`<<workspace_slug>>.gap.<slug>`), `opened` / `closed` (YYYY-MM-DD), `answer` (the
found fact), `source` (the journal entry or primary source that closed it).

## Status lifecycle

- **open** — named, not yet being worked.
- **investigating** — a route is in flight (`Plan -> Validate -> Execute` applies to the route).
- **answered** — a source was found; the answer and `source` are recorded, and the finding is
  written back to `journal/` so the reaper can mint or update an atom.

- **waived** — the founder has decided the work can proceed without this answer; record who waived
  it and why. Only the founder waives a gap that is `required_for` a consequential action.

- **stale** — the parent or the question no longer applies; closed without an answer.

## The blocking rule (the gate)

**High-risk actions block until their required gaps close.** A gap whose `required_for` is a
consequential or low-reversibility step (per `10_doctrine/autonomy-and-gates.md`) holds that step
until its `status` is `answered` or `waived`. The blocked step is listed in
`50_registers/blocked-actions.md` with a link back to the gap.

- This enforces **source-or-abstain**: the workspace would rather block than act on an unknown.
- It enforces **autonomy-by-reversibility**: reversible work proceeds with `open` gaps noted as
  caveats; irreversible work does not.

- Only the founder may `waive` a critical gap. The agent **signposts** the gap and its route; it does
  not waive on the founder's behalf (signpost, don't advise).

- `low`/`med` gaps on reversible work do not block; they are caveats carried into the brief
  (anti-noise batching) and worked on a research sprint.

## Example row

```markdown
| parent | missing_dimension | question | required_for | priority | status | route |
|---|---|---|---|---|---|---|
| long-term/regulatory-deadline.md | when | Does the deadline apply to existing records or only new categories? | decision_packet | critical | answered | source: read the primary standard; journal/YYYY-MM-DD-HHMM-radar.md |
| opportunity: evidence-wedge | who | Which trade body endorses a standard we can cite? | opportunity_scoring | med | open | research_sprint |
| 90_runs/YYYY-MM-DD-supplier-switch | why | Why was the current supplier chosen; is there a contractual lock-in before we switch? | admin_action | high | investigating | escalate |
```

## Related

- [Knowledge gaps register](../20_memory/knowledge-gaps.md)
- [Decision Packet schema](decision-packet.md)
- [Memory card (atom) schema](memory-card.md)
- [Autonomy & gates — the single decision gate](../10_doctrine/autonomy-and-gates.md)
