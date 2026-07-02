---
id: <<workspace_slug>>.schema.event
name: Journal event schema
type: schema
layer: C2
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [schema, journal, event, append-only]
related:
  - {ref: 20_memory/journal/README.md, dimension: where, polarity: explains}
  - {ref: 30_schemas/memory-card.md, dimension: what, polarity: enables}
---

# Journal event schema

A journal entry is one **immutable** Markdown file in `20_memory/journal/`. It is the only source
of truth; atoms are folded from it. Never edit or delete an entry — a correction is a new entry.

Filename: `YYYY-MM-DD-HHMM-<slug>.md`.

## Frontmatter

```yaml
---
id: journal.YYYY-MM-DD-HHMM-<slug>
type: observation | decision | import | correction | retraction
who: [entity-ref, ...]
what: <one-line summary of what happened>
where: [channel/system/source, ...]
when: YYYY-MM-DDTHH:MM:SSZ
source_type: email | note | research | meeting | system | manual | import
source_url: <optional>
trust: trusted | review | untrusted     # imports default untrusted
corrects: <journal-ref>                 # for type: correction
retracts: <journal-ref>                 # for type: retraction
---
```

## Body

The verbatim or near-verbatim content: the email excerpt, the decision and its rationale, the
research finding with its source link, the meeting note. Keep enough that an atom folded from it
is traceable. This is the "verbatim fallback" — atoms point back here.

## Rules

- Append-only. Immutable. Git is the tamper-evidence.
- A `correction`/`retraction` references the entry it supersedes; the reaper honours it at the
  next pass and drops/overrides the affected atom.

- Imports land `trust: untrusted` and route their atoms to `_quarantine/`.

## Related

- [Journal — the append-only event log](../20_memory/journal/README.md)
- [Memory card (atom) schema](memory-card.md)
