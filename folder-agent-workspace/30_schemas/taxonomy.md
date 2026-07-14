---
id: <<workspace_slug>>.schema.taxonomy
name: Taxonomy - the shared vocabulary of concept types and relation types
type: schema
layer: C2
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [schema, taxonomy, glossary, ontology, concept-types, relations, okf, knowledge-pack]
related:
  - {ref: 30_schemas/README.md, dimension: where, polarity: explains}
  - {ref: 40_templates/knowledge-pack/README.md, dimension: how, polarity: enables}
  - {ref: AGENTS.md, dimension: why, polarity: derived_from}
---

# Taxonomy

The workspace's **shared vocabulary**: the concept types a durable artefact may declare in its
`type:` frontmatter, and the relation types a `related:` edge may carry. A compact, living
glossary - extend it deliberately over time; never invent a parallel vocabulary in an individual
file. Where a new distinction is needed, prefer adding a `profile` to an existing type over
minting a new top-level type.

Consumed by [the schemas contract](README.md) (every schema's `type` comes from here), stamped
into project repos via [the knowledge-pack template](../40_templates/knowledge-pack/README.md),
and required by [`AGENTS.md`](../AGENTS.md) rule 6.

## Concept types

Workspace-native types (already contracted in `30_schemas/`): `event`, `memory-card`,
`decision-packet`, `action-intent`, `opportunity`, `knowledge-gap`, `project`, plus the structural
`schema`, `template`, `reference`, `identity`, `workflow`.

Project/repo corpus types, by family:

| Family | Types |
|---|---|
| foundation | Concept, Project, Repository, Product, Person, Team, Organization, GlossaryTerm |
| software | System, Service, Module, Package, Library, Component, CLI, Job, Workflow, Environment, Dependency |
| api | Api, Endpoint, Operation, Event, Topic, Queue, Webhook, Schema, Contract |
| data | Dataset, Database, Table, View, Column, Metric, Dimension, Dashboard, Lineage |
| product | Requirement, Feature, UserStory, Persona, Journey, DesignDecision, UIComponent, AccessibilityRequirement |
| operations | Runbook, Playbook, Incident, Postmortem, SLO, SLA, Release, Migration, RollbackPlan |
| governance | Policy, Control, Risk, Threat, DecisionRecord, SecurityPolicy |
| ai | Agent, AgentInstructions, Skill, Prompt, Tool, Model, Eval, ModelCard, DatasetCard, Guardrail |
| legal | License, CitationMetadata, Attribution, SBOM - **stay native**: the LICENSE / CITATION.cff / SBOM file owns the facts; a concept only references it |

## Relation types

Edges for `related:` (workspace dialect: `{ref, dimension, polarity}`) and for corpus
`relations:` (`{type, target}`):

```yaml
structural: [part_of, contains, owned_by, maintained_by, applies_to]
dependency: [depends_on, uses, imports, calls, consumes, produces, emits, subscribes_to]
data:       [derived_from, joins_to, maps_to, validates, defines_metric, has_column]
lifecycle:  [supersedes, superseded_by, deprecates, replaces, version_of]
evidence:   [cites, sourced_from, generated_from, verified_by]
governance: [governed_by, controlled_by, mitigates, requires_approval_from, violates]
semantic:   [related_to, duplicates, conflicts_with, see_also]
```

The workspace's typed 5W1H `related:` edge (`dimension` + `polarity`) is the **richer form** of
the same idea: when a corpus edge needs evidence, ownership, or freshness, promote it from a bare
`{type, target}` pair to a record with `confidence`, `last_verified`, and `evidence[]`.

## The native-files rule

Some files own their own schema because external tooling and communities already know them:
`LICENSE`, `CITATION.cff`, SBOMs, `openapi.yaml` / `schema.graphql` / `*.proto`, `package.json` /
`pyproject.toml` / `Cargo.toml` / `go.mod`, `CODEOWNERS`, `AGENTS.md` and its runtime adapter
pointer files (see `core/RUNTIMES.md`), `llms.txt`. **Native files stay native**: the corpus references, mirrors, explains,
or *generates* them - it never overwrites a file that owns its own schema, and for the fields a
native file owns, the native file wins. Each native file takes one of three modes:

- **native** - hand-owned by its own tooling; a corpus concept may be its *companion*.
- **generated** - produced from a corpus concept, carries a do-not-edit header; drift from a
  rebuild is a validation failure.
- **companion** - a corpus concept that explains or indexes a native file without owning it.

## Anti-gaming rules

- No hundreds of types: if a candidate type is just a flavour of an existing one, it is a
  `profile`, not a new type.
- Legal types never get a second source of truth in a corpus.
- Every relation target must resolve (the `okf-check` gate's dangling-ref rule is the workspace
  form of this; a stamped pack's validation carries `require_relation_targets`).
- Update this glossary by proposing a diff (C2 contract - `AGENTS.md` safety gate); additions
  are append-friendly, renames need a `supersedes` note in the change log.

## Related

- [Schemas - the shape contracts for structured artefacts](README.md)
- [Knowledge-pack template - stampable knowledge corpus for a project repo](../40_templates/knowledge-pack/README.md)
- [<<WORKSPACE_NAME>>](../AGENTS.md)
