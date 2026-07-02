---
id: <<store_slug>>.identity.readme
name: Identity - the principal's canonical profile
type: reference
layer: C0
status: current
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

All three files ship as **blank skeletons**: headings and guidance, no facts. They earn content
through calibration sessions and confirmed corrections
([`calibration-os/`](../calibration-os/README.md)) - never through agent inference. An agent that
"remembers" something about the principal not written here logs it as a correction candidate; it
does not write it here directly.

- [`principal.md`](principal.md) - roles, context, risk posture, hard rules.
- [`voice.md`](voice.md) - how the principal writes and wants to be written for.
- [`availability.md`](availability.md) - time shape, response expectations, escalation windows.

Owner note: files here are typically `owner: human` - agents propose, the principal confirms.

## Related

- [<<STORE_NAME>>](../SHARED.md)
- [Calibration OS - living scoped preferences](../calibration-os/README.md)
