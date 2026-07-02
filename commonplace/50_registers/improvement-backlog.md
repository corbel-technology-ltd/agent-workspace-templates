---
id: <<workspace_slug>>.register.improvement-backlog
name: Improvement backlog
type: register
layer: C1
status: current
owner: shared
staging: v1-now
created: <<CREATED_DATE>>
tags: [register, improvements, proactivity, backlog]
related:
  - {ref: AGENTS.md, dimension: why, polarity: derived_from}
  - {ref: 50_registers/measurement.md, dimension: where, polarity: complements}
---

# Improvement backlog

Where proactivity lands so it does not become noise. When the agent notices something worth
improving — a recurring manual sequence, an unused signal, a friction, a missed opportunity — it goes
here with a **priority tag**, not into the founder's attention. The daily brief may surface the top
`do-now` / `suggest` item; everything else waits here.

Priority hierarchy: **blocking** → **strategic** → **opportunistic**. Action gate per item:
`do-now` (high-impact, low-risk, reversible — just do it and log) · `suggest` (worth a Decision
Packet) · `log` (capture, revisit at the weekly review) · `ignore` (recorded then closed).

| id | date | observation | rank | action | status | note |
|---|---|---|---|---|---|---|
| (none yet) | | | | | | |

<!-- Row shape. id = IMP-NNN, monotonic. rank = blocking | strategic | opportunistic.
     action = do-now | suggest | log | ignore. status = open | in-progress | done. -->

When an item is actioned, move it to the decision-log (if it was a decision) or note its outcome
here and close it. Sensed-but-unactioned signals accumulate here and feed the weekly review and the
inward coverage-gap signal. Improvements that are generic to the operating system should also flow
upstream to the Workspace-Template (see the upstreaming rule in the template `README.md`).

## Related

- [<<WORKSPACE_NAME>>](../AGENTS.md)
- [Measurement register](measurement.md)
