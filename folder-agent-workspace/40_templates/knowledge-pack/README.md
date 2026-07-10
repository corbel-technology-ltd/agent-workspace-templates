---
id: <<workspace_slug>>.template.knowledge-pack
name: Knowledge-pack template - stampable knowledge corpus for a project repo
type: template
layer: C2
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [template, knowledge-pack, corpus, taxonomy, native-files, manifest, fill-in]
related:
  - {ref: 30_schemas/taxonomy.md, dimension: what, polarity: derived_from}
  - {ref: 40_templates/README.md, dimension: where, polarity: explains}
---

# Knowledge-pack template

A **stampable knowledge corpus** for a project or product repository: the standardised file set
that makes a repo readable by humans, coding agents, docs tooling, and knowledge graphs at once.
Copy this folder into the target repo as `knowledge/`, replace every `CHANGE_ME`, and delete the
example concepts once real ones exist. The type and relation vocabulary is the workspace
[taxonomy](../../30_schemas/taxonomy.md) - the pack's `registry/` files are a stamped copy of it,
extendable per repo but never contradicting the glossary. Sibling scaffolds:
[templates index](../README.md).

## What gets stamped

| File | Role |
|---|---|
| `manifest.yaml` | Machine entry point: corpus id, registries, native-file inventory, generated adapters, validation switches |
| `index.md` | Human entry point: links to the concepts |
| `log.md` | Append-only corpus change log, newest first |
| `registry/types.yaml` | Concept-type vocabulary (from the taxonomy) |
| `registry/relations.yaml` | Relation-type vocabulary (from the taxonomy) |
| `concepts/` | One concept per file: frontmatter for structured filtering, body for meaning |

## The one rule

> **Native files stay native.** The corpus references, mirrors, explains, or generates them - it
> never overwrites a file that owns its own schema (`LICENSE`, `openapi.yaml`, `package.json`,
> `CODEOWNERS`, `CITATION.cff`, SBOMs...). For the fields a native file owns, the native file wins.

Each native file declares a `mode` in `manifest.yaml`:

- **native** - hand-owned by its own tooling; the corpus may link a *companion* concept.
- **generated** - produced from a corpus concept with a do-not-edit header (`README.md`,
  `AGENTS.md`, `CLAUDE.md`, `llms.txt`); a checked-in copy that drifts from a rebuild fails
  validation.
- **companion** - a corpus concept that explains or indexes a native file.

## Authoring rules

- One concept per file; `type` from `registry/types.yaml`; relations from
  `registry/relations.yaml`; relation targets must resolve.
- Facts live in concepts (Service, System, Dataset...); instructions live in
  `AgentInstructions`; secrets live nowhere in the corpus.
- Add detail with `profile:` on an existing type, not a new top-level type.
- Every change appends a line to `log.md`.
