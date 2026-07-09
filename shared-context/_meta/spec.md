---
id: <<store_slug>>.meta.spec
name: Shared-Context - founding design spec (the shared brain)
type: design-spec
layer: C0
status: current
owner: shared
created: <<CREATED_DATE>>
source: generalised from a live multi-workspace deployment; all identifying content removed
tags: [design-spec, shared-context, precedence, governance, link-in]
related:
  - {ref: SHARED.md, dimension: what, polarity: explains}
  - {ref: _meta/governance.md, dimension: how, polarity: enables}
---

# Shared-Context - founding design spec

## 1. What this is

A **shared-context store**: the single source of truth for one principal across many agent
workspaces. Where a workspace answers "how does this venture run?", the store answers "who is the
principal, how do their agents behave anywhere, and what estate do they operate in?". It is a
constitution plus a small governed library, not a knowledge base.

## 2. Why it exists (the failure modes it kills)

Generalised from a live multi-workspace deployment, where each failure mode below actually
happened before the store existed:

- **Identity drift** - each workspace keeps its own notes on the principal; the copies diverge;
  agents calibrate differently and corrections do not propagate.
- **Rule scatter** - operating rules live inside domain files or nowhere; two agents resolve the
  same situation differently.
- **Invisible coordination** - work handed between workspaces lives in chat history; nobody can
  answer "what do I owe / what am I owed" without archaeology.
- **Ungoverned edits** - whichever agent writes last wins; there is no objection step and no
  append-only history of who changed the shared brain and why.
- **Leak-by-default** - nothing states the confidentiality line, so every distribution scrub is
  improvised.

## 3. Locked decisions

- **Shared outranks local**, but only on shared scope; workspace domains stay sovereign.
- **The ledger is append-only** (`CHANGES.md`); the dashboard (`_coordination/`) is its mutable
  counterpart. History and state never share one file.
- **Blank by design.** Skeletons never ship with invented facts. Calibration and governance are
  the only two ways content arrives.
- **A file cap with a scope test** rather than an open-ended library - the store is a spine, not
  an attic.
- **Parameters are onboarding tokens** (`FILE_CAP`, `OBJECTION_WINDOW_HOURS`) recorded in
  machine-readable frontmatter, so the gates and hooks enforce the numbers the principal chose.
- **No secrets, ever.** The store is designed to be read by every agent and shipped as a template;
  secrets live in each workspace's untracked `.env`, never here.

## 4. The shape

Nine content surfaces (`identity/`, `operating-rules/`, `people/`, `tech-stack/`,
`calibration-os/`, `boundaries/`, `glossary/`, `_coordination/`, `CHANGES.md`), one constitution
(`SHARED.md`), one manifest for in-store work (`AGENTS.md`), governance + this spec (`_meta/`),
and the family-standard machinery (`core/`, `tools/`, thin runtime adapters).

## 5. Staging

- **v1-now:** the constitution, governance, link-in contract (`core/link-workspace.py`), the
  store brief, the four gates, scrub derivation from boundaries.
- **awaits-inputs:** calibration content (needs a principal), roster (needs workspaces),
  dashboard rows (need two consumers), evaluation of agent calibration (needs history).
- **deferred:** any UI, any database, any automated merge of contradictory edits - the ledger +
  window + principal is the conflict engine, deliberately.

## Related

- [<<STORE_NAME>>](../SHARED.md)
- [Governance - the full edit protocol](governance.md)
