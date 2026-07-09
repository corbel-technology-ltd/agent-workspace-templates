---
id: <<workspace_slug>>.memory.journal
name: Journal - the append-only event log
type: reference
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [memory, journal, event-log, append-only, truth]
---

# Journal

The **only source of truth**. One immutable Markdown file per observation, decision, or import.
Atoms are folded from here; nothing here is folded from anything else.

**This journal starts empty.** Entries accrue as the workspace runs (the `session-digest` hook
appends one on each session end, and workflows append events as they happen).

- **Append-only. Immutable.** Never edit or delete an entry. A correction or retraction is a NEW
  entry (`type: correction|retraction`) that references the old one. Git is the tamper-evidence. The
  `journal-guard` reflex guards this at the tool boundary, and the optional `core/git-hooks/`
  pre-commit guard enforces it at commit time for any runtime.
- Filename `YYYY-MM-DD-HHMM-<slug>.md`. Schema: [`../../30_schemas/event.md`](../../30_schemas/event.md).
- Imports land `trust: untrusted`; their derived atoms go to `../_quarantine/`.

Why immutable: the atoms projection can decay, dedup, merge, and forget aggressively precisely
because the raw record here is never lost. This is the event-sourcing spine.
