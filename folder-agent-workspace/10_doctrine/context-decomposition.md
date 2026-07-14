---
id: faw.doctrine.context-decomposition
name: Context decomposition - concept folders with index maps
type: doctrine
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [doctrine, context, decomposition, concept-folder, index, granular-loading]
related:
  - {ref: 10_doctrine/principles.md, dimension: why, polarity: derived_from}
  - {ref: 40_templates/README.md, dimension: how, polarity: explains}
---

# Context decomposition - concept folders with index maps

Fill-in template: `40_templates/concept-folder/` (create it from the shape below the first time a
real decomposition needs one - spine up front, leaves on demand). This rule implements progressive
disclosure **of context**; it is distinct from any shared progressive-disclosure *graduation* model
a linked Shared-Context store defines for when ideas may cross between workspaces.

## The rule

Large durable context files are broken down, where possible, into singular ideas, concepts or
categories - one concept per file - behind an index file that maps them, so an agent can load
exactly the context a task needs and nothing more. An index is the only default read; concept
notes load on their retrieval cues.

## Decomposition test - chunk when ANY of these hold

- **D1 - multiple retrieval purposes:** different tasks reliably need different parts of the file.
- **D2 - mixed authority or freshness:** parts carry different status/authority, or change at
  different rates, and currently share one file's fate.
- **D3 - independently needed sections:** sections are commonly loaded on their own; a compact
  core would serve most sessions while the rest is situational.
- **D4 - size x mixture:** the file exceeds ~150 lines or ~12,000 characters AND covers more than
  one distinct concept or category.
- **Mechanical ceiling:** the checker flags non-structural tracked Markdown over either size
  threshold; human review then splits it or adds a reasoned keep-intact exception.

## Keep intact - do not chunk

These keep-intact classes **override D1-D4**: a file in one of these classes is not chunked even
when a decomposition trigger fires. Genuinely borderline cases become reasoned exceptions rather
than forced splits.

- `AGENTS.md` (the constitution is a single boot file by design).
- **Coherent specifications** (a spec is one contract; chopping harms buildability).
- **Decision packets** (one decision per packet, read whole by design).
- **Registers and ledgers** (`50_registers/**`; already row-granular tables).
- **The journal and derived memory layers** (`20_memory/**`; immutable evidence and rebuildable
  projections have their own structure).
- **Single-purpose doctrine** (one rule, one file - already concept-scoped).
- **Schemas and templates** (`30_schemas/**`, `40_templates/**`; each is a structural contract or
  authoring scaffold).
- **Run artefacts** (`90_runs/**`; C4 historical record) and sealed/verbatim evidence.
- **Atomic code engines and their test suites** (a tightly-coupled transaction, or a single test
  module) - a module split is a separate refactor, out of scope for a decomposition pass.
- Any file under ~150 lines expressing a single concept.

The directory-backed classes above are structural exemptions, not conditional exemptions based on
their current length or mixture.

## Anti-confetti rule

Decomposition means a **shallow index over a few substantial concept notes**, not shredding.
Prefer notes of roughly 30-120 lines that each stand alone; do not split below the coherent-concept
level; one index level is the norm (a nested index needs its own D1-D4 justification). If a split
would produce fragments that are only ever read together, they are one concept - keep them
together.

## The concept-folder shape

```text
<topic>/
  00-INDEX.md        the map; the ONLY default read; never preload the folder
  01-CORE.md         compact default payload (optional; preferred when a stable core exists)
  NN-<concept>.md    one concept per file; kebab-case; numbered for stable ordering
```

`00-INDEX.md` is deliberately not named `index.md` (that name is OKF-reserved for frontmatter-free
navigation files); the uppercase prefixed name carries full frontmatter.

## Index contract - `00-INDEX.md` must contain

1. Frontmatter (`id`, `name`, `type: index`, `status`, `owner`, dates, `tags`).
2. **Purpose** - one or two lines.
3. **Load policy table** - `File | Contains | Load when` with concrete retrieval cues.
4. **Load recipes** - the common task shapes and exactly which notes they load.
5. **Authority note** - what wins when sources conflict, and what this folder may not override.
6. **Maintenance rule** - update a concept note only when evidence for that concept changes;
   update the index when files, routing or authority change; record contradictions rather than
   flattening them.

## Concept-note contract - every chunk must carry all five

1. **Authority** - what governs it and what it may not override (a banner or frontmatter note;
   for decomposed authorities, the spine states precedence).
2. **Status** - its own frontmatter `status:` (staged/current/superseded), never inherited
   silently.
3. **Retrieval cues** - a concrete "load when ..." row in the owning index.
4. **Provenance** - where the content came from (source path, date, decision id; verbatim
   banner when decomposed from an existing authority).
5. **An owning index** - a `related:` edge (mirrored body link) to the sibling folder's
   `00-INDEX.md` (`tools/decomposition-check.py` enforces this); for a decomposed authority, the
   original spine separately links that index.

Plus: one concept per note; target <= ~120 lines; no cross-concept duplication - link siblings.
When decomposing an EXISTING authority, section text moves **verbatim**: structural glue only.
No rewording without the file's normal edit gate.

## Backdating procedure (applying the rule to an existing file)

1. Confirm the file's edit class and obtain whatever approval that class requires (canon and
   doctrine need explicit authority; this rule does not lower any gate).
2. Group the body into concept notes by concept; the index defines their load order. Preserve the
   source wording verbatim within each note, but thematic regrouping need not preserve one strict
   original linear order.
3. Convert the ORIGINAL path into the spine: keep its frontmatter and identity, keep the compact
   core inline where one exists, and add the load-policy map. Existing inbound links must keep
   resolving to the same path and meaning.
4. Mechanically verify content preservation: the concatenated concept bodies plus the spine must
   differ from the original only by structural glue.
5. Run `okf-check` (and `gen-related` if typed edges changed).
6. Record a journal event naming the file, the decision authority and the verification result;
   each new note carries a provenance banner.

## Where user context lives

User and principal context, and cross-workspace operating principles, live in the linked
Shared-Context store (see `AGENTS.md`'s Shared context section), not in a second workspace folder
inside this tree. This workspace's own `15_canon/` and `20_memory/` carry only the deltas over
that shared base; a user-profile intake artefact landing at the workspace root is an intake packet
whose canonical destination is proposed through the normal decision gates, not a second home.

## Related

- [Operating principles - the one vocabulary](principles.md)
- [Templates - copy-and-complete authoring scaffolds](../40_templates/README.md)
