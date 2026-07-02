---
id: <<workspace_slug>>.register.risk-register
name: Risk register
type: register
layer: C1
status: current
owner: shared
created: <<CREATED_DATE>>
staging: v1-now
tags: [register, risk, governance, daily-brief]
related:
  - {ref: 50_registers/open-loops.md, dimension: what, polarity: complements}
  - {ref: 50_registers/decision-queue.md, dimension: what, polarity: complements}
---

# Risk register

Material risks to the entity. One row per live risk; every entry traces to a source. No invented
risk. Severity: HIGH / MED / LOW.

## Live

| id | risk | severity | status | next | source |
|---|---|---|---|---|---|
| (none yet) | | | | | |

<!-- Row shape. id = RSK-NNN, monotonic. severity = HIGH | MED | LOW.
     status = open | mitigating | accepted. source = a journal entry. -->

## Recently closed (traceability)

| id | risk | closed | how |
|---|---|---|---|
| (none yet) | | | |

## Related

- [Open loops register (moved)](open-loops.md)
- [Decision queue — open founder decisions](decision-queue.md)
