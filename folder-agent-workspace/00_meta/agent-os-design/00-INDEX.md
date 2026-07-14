---
id: <<workspace_slug>>.meta.agent-os-design.index
name: Agent OS design — situational detail index
type: index
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [agent-os, hooks, index, concept-folder]
related:
  - {ref: 00_meta/agent-os-design.md, dimension: why, polarity: derived_from}
---

# Agent OS design — situational detail index

## Purpose

Map for the situational detail split out of [`00_meta/agent-os-design.md`](../agent-os-design.md)
(the spine, which keeps the stable design core). This folder is not a second authority - the spine
plus this map remain the design's home; do not preload the whole folder.

## Load policy

Read the spine first. Load a concept note only on its own retrieval cue.

| File | Contains | Load when |
| --- | --- | --- |
| `01-staged-plan.md` | what's built NOW, what AWAIT-NEEDs an input, what's DEFERred | checking hook build status, or deciding what to build/wire next |
| `02-emergent-intelligence.md` | observation budget, anti-superstition feedback, nudge limits, the promotion ladder | working on the subconscious/learning system or `homeostasis.yml` |

## Load recipes

- **Why the workspace is designed this way / onboarding a new contributor:** the spine
  ([`00_meta/agent-os-design.md`](../agent-os-design.md)) only.
- **What's already wired vs. still planned:** `01-staged-plan.md`.
- **Building or reviewing the subconscious/priors/promotion-ladder mechanics:** `02-emergent-intelligence.md`.
- **Full design review:** the spine, then both notes in order.

## Authority

Use this precedence when sources conflict:

1. the spine's stated design decision (`00_meta/agent-os-design.md`)
2. the most recent journal entry recording a structural change to either note
3. this index's load-policy table
4. older context

This folder may never override the spine's core mapping - judgment stays in `AGENTS.md`; the stable
design core stays in the spine. This folder only holds the situational plan/refinement detail the
spine's own load-policy section points at.

## Maintenance rule

Update a concept note only when evidence for that concept changes (a hook ships, a target's status
moves). Update this index when files, load cues or authority change. Record any contradiction
between the spine and a note rather than silently flattening it.

## Related

- [Agent OS design - constitution / reflexes / playbooks / cognition / memory](../agent-os-design.md)
