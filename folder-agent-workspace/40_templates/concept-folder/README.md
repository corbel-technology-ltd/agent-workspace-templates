---
id: faw.template.concept-folder
name: Concept folder — fill-in template for decomposed context
type: template
layer: C2
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [template, concept-folder, index, context-decomposition]
related:
  - {ref: 10_doctrine/context-decomposition.md, dimension: why, polarity: derived_from}
---

# Concept-folder template

The fill-in skeleton for the [context-decomposition rule](../../10_doctrine/context-decomposition.md):
large durable context decomposes into one-concept notes behind an index map, so context loads
granularly. Copy this folder, rename it to the topic, fill the three skeletons, delete what a
given topic genuinely does not need (and say why in the index).

## The formula

1. Run the decomposition test (D1–D4 in the doctrine). If no trigger fires, do not decompose.
2. Name the folder after the topic; keep `00-INDEX.md` as the only default read.
3. Put the compact always-relevant core in `01-CORE.md` if one exists.
4. One concept per numbered note; ≤ ~120 lines each; no cross-note duplication — link siblings.
5. Fill the index's load-policy table with honest retrieval cues ("Load when …"), not categories.
6. State authority: what wins on conflict; what the folder may never override.
7. When decomposing an EXISTING file, move text verbatim and follow the doctrine's backdating
   procedure (edit gate → verbatim split → spine conversion → mechanical verification →
   okf-check → journal event).

## Files in this template

| file | role |
|---|---|
| [00-INDEX.md](00-INDEX.md) | the map: purpose, load policy, recipes, authority, maintenance |
| [01-CORE.md](01-CORE.md) | compact default payload skeleton |
| [02-example-concept.md](02-example-concept.md) | one-concept note skeleton |

Worked pattern: reach for this once a topic fails the decomposition test — for example an owner or
agent identity profile, or a policy/canon document that has outgrown a single-file read. Once
decomposed, the result is an index (shaped like `00-INDEX.md`) plus one concept note per idea,
exactly as sketched above.

## Related

- [Context decomposition - concept folders with index maps](../../10_doctrine/context-decomposition.md)
