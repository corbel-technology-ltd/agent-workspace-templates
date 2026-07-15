---
id: <<store_slug>>.identity.readme
name: Identity - the principal's canonical profile
type: reference
layer: C0
status: current
load: always
owner: shared
created: <<CREATED_DATE>>
tags: [identity, principal, canonical, voice, availability]
related:
  - {ref: SHARED.md, dimension: why, polarity: derived_from}
  - {ref: calibration-os/README.md, dimension: how, polarity: complements}
---

# Identity

The canonical, cross-workspace answer to **who the principal is**. Every workspace's local notes
on the principal are deltas over this folder; on conflict, this folder wins (precedence doctrine,
[`SHARED.md`](../SHARED.md)).

All three files ship as **blank skeletons** and never load until current and populated. They earn
content through confirmed calibration, never agent inference. An unwritten recollection becomes a
correction candidate, not a direct edit.

## Load policy

| File | Load | Trigger |
|---|---|---|
| [`principal.md`](principal.md) | always | Every session once current and populated, because it carries risk posture, approval rules and principal hard rules. |
| [`voice.md`](voice.md) | triggered | Drafting, editing or communication that must match the principal. |
| [`availability.md`](availability.md) | triggered | Scheduling, escalation, workload or capacity decisions. |

Owner note: files here are typically `owner: human` - agents propose, the principal confirms.

## Related

- [<<STORE_NAME>>](../SHARED.md)
- [Calibration OS - living scoped preferences](../calibration-os/README.md)
