---
id: <<workspace_slug>>.meta.agent-os-design.emergent-intelligence
name: Agent OS design — emergent-intelligence refinements
type: design-spec
layer: C0
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [agent-os, subconscious, priors, promotion-ladder, emergent-intelligence]
related:
  - {ref: 00_meta/agent-os-design/00-INDEX.md, dimension: where, polarity: part_of}
---

# Agent OS design — emergent-intelligence refinements

One concept: the small artificial ecology (observation budget, anti-superstition feedback, nudge
limits, promotion ladder) that lets repeatedly-useful behaviour graduate to policy without new
infrastructure. Folder map: [00-INDEX.md](00-INDEX.md).

> Decomposed 2026-07-12 under the context-decomposition rule (10_doctrine/context-decomposition.md); wording unchanged.

## Emergent-intelligence refinements

The aim: a small artificial ecology where observations are born cheaply, patterns compete for
survival, useful priors bias attention, and only repeatedly-useful behaviours graduate to policy or
automation. Folded in as doctrine/targets, not new infrastructure (they activate with the await-need
feedback hooks):

- **Observation budget (3 levels).** L1 raw event: always append cheap facts (command, file, test
  result, duration). L2 semantic observation: only when anomalous / repeated / risky / inefficient /
  goal-relevant. L3 pattern candidate: only by deterministic fold after thresholds. Stops narrating
  every tiny thing.
- **Anti-superstition feedback.** The feedback hooks MUST log `prior.used` and `prior.outcome` as
  SEPARATE events; never self-validate a prior because an action was taken. Confidence moves on a
  real outcome (caught regression / confirmed signal), not on mere use. See
  `20_memory/subconscious/README.md`.
- **Nudge limits.** Priors enter context as hypotheses only: ≤3 per turn, ≤80 words, confidence
  >~0.55, source-linked, never cited as fact.
- **Promotion ladder.** observation→pattern (≥3 occurrences / 2+ distinct sessions / 14d / avg-conf
  ≥0.6) → prior (≥5 / 45d / ≥0.7 / 2+ successful uses) → **policy candidate (human review required)**.
  Decay: half-life ~14d; archive below conf 0.25 or unused 30d. These are targets; wire into
  `homeostasis.yml` only when the journal actually feeds them (no data yet - plain counts until then).
- **Prior→policy graduation requires human review** unless purely local, reversible, low-risk - the
  gate, applied to self-modification.

## Evidence / provenance

Source: the spine, `00_meta/agent-os-design.md`, "Emergent-intelligence refinements" section, moved
verbatim when this folder was created under `10_doctrine/context-decomposition.md`. These remain
targets, not yet wired - update here when the journal actually starts feeding `homeostasis.yml`, per
the note's own text above.
