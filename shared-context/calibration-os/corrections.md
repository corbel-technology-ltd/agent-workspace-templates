---
id: <<store_slug>>.calibration-os.corrections
name: Corrections - the candidate log
type: log
layer: C1
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [corrections, candidates, calibration, append-only]
related:
  - {ref: calibration-os/README.md, dimension: why, polarity: derived_from}
---

# Corrections - the candidate log

Append-only. Every observed correction or preference candidate lands here first; **nothing enters
a preference file without confirmation**. A candidate that recurs is due for promotion; a
candidate the principal rejects is marked so agents stop re-observing it.

Format, newest first:

```text
YYYY-MM-DD | <workspace/agent> | observed: <what happened> | candidate: <the inferred preference> | status: pending
```

`status` moves `pending` -> `promoted (-> file#section)` or `rejected (<reason>)` - update the
line's status only (the observation text is immutable).

<!-- candidates: append new lines directly below, newest first -->

## Related

- [Calibration OS - living scoped preferences](README.md)
