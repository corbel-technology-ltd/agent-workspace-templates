---
id: <<store_slug>>.boundaries.readme
name: Boundaries - the confidentiality line
type: reference
layer: C0
status: current
load: always
owner: shared
created: <<CREATED_DATE>>
tags: [boundaries, confidentiality, scrub, privacy, never-share]
related:
  - {ref: SHARED.md, dimension: why, polarity: derived_from}
  - {ref: boundaries/boundaries.md, dimension: what, polarity: enables}
---

# Boundaries

The **confidentiality line, stated as a file**: what may never leave the principal's machines,
what needs care, what is public. Everything privacy-mechanical in the family derives from here -
`tools/scrub-terms.txt` denylists (in this store and in every workspace) are generated from the
never-share list by `python3 core/derive-scrub.py`, so the line is written once and enforced
mechanically everywhere.

## Load policy

| File | Load | Trigger |
|---|---|---|
| [`boundaries.md`](boundaries.md) | always | Every session once current and populated, because it carries privacy and publication constraints. |

`boundaries.md` is human-owned: agents may propose tightening, but only the principal relaxes a
boundary.

Two rules agents apply without being asked:

1. **When unsure which tier something is, treat it as never-share** until the principal says
   otherwise.
2. **New sensitive term -> boundaries first.** A new person, hostname, or codename lands in the
   never-share list in the same change that introduces it, then `derive-scrub.py --write`
   refreshes the denylist.

Expected behaviour, not a bug: once the denylist is armed, a **live** store fails
`tools/scrub-check.py` - this file itself carries the terms. That is the gate saying "this tree
is not safe to share as-is". Green is for the blank template and for genericised copies only.

## Related

- [<<STORE_NAME>>](../SHARED.md)
- [The boundary tiers - never-share / share-with-care / public](boundaries.md)
