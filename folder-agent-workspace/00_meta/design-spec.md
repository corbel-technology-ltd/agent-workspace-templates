---
id: <<workspace_slug>>.meta.design-spec
name: Workspace - founding design spec (founder control plane)
type: design-spec
layer: C0
status: current
owner: shared
created: <<CREATED_DATE>>
source: Founder Control Plane design reconciled with FAW (minus JIT) and an event-sourced memory-homeostasis model
tags: [design-spec, prd, founder-control-plane, faw, memory, homeostasis, workspace-first]
---

# Workspace - founding design spec

The authoritative blueprint for this workspace: a dedicated home on disk for <<ENTITY>>'s
operations and IP. It is the **Deterministic Founder Control Plane**, scoped to what one founder can
actually run.

## 1. What this is

An internal operating system for a solo founder: **a stateful business routing system, not an
autonomous AI CEO.** Its promise: *everything that does not need the founder is handled; everything
that does need the founder arrives prepared; every decision improves the system.*

Preparation is automated. **Authority is always gated.** An LLM (<<AGENT_NAME>>) is a reasoning
layer, never an authority layer.

## 2. Locked decisions (set at instantiation)

- **Location:** the workspace root (a home-level directory, kept off any cloud-synced documents tree
  where possible).
- **Build scope:** **workspace + doctrine first.** Markdown knowledge structure, registers, and
  schemas/policies as written specs now. The software control plane (a database, ingestion
  connectors, a dashboard UI, runtime ABAC) is **deferred** behind a named value-gate.

- **Doctrine:** keep FAW bones, **drop the JIT dormant-mechanism table** and the "add process only
  after a failure" rig. The spine is designed up front; **leaves are added only when their inputs
  exist.**

- **Memory:** a first-class, built-now deliverable, file-native, designed to graduate to a database
  5W1H graph later without a rewrite. Event-sourced with a homeostatic reaper.

- **Git:** a fresh `git init` per instance; the off-machine remote is chosen by the instance.

## 3. The convergent review verdict

The pattern that holds across reviews: the control-plane **doctrine is right**; a full software
**body is over-scoped** for one founder and duplicates live systems. Therefore:

- **Keep** the genuinely-additive parts: the **Decision Packet** (the standout object), the
  **autonomy default table**, the **"external content is never authority"** rule, the
  Definition-of-Done checklists, the conservative-preference rule, the per-object-type
  required-dimensions checklist, the opportunity scoring worksheet, the feedback labels.

- **Cut** the database 5W1H **DDL**, the dissonance + ignorance-graph engines, the multi-service
  decomposition, any `founder_attention_score` formula, the dozens of speculative metrics, and any
  productisation phase.

- **Fold, don't rebuild:** an existing research/opportunity engine = the opportunity pipeline; a
  sentiment tool = sentiment; an **email loop** = email monitoring; a **records store** =
  obligations/evidence; a **memory substrate** = memory; **git = the event store**. See
  `70_integrations/`.

## 4. One vocabulary (the principles, named once)

The remade workspace uses ONE set of names. The control-plane principles map onto a single canonical
doctrine vocabulary:

| Principle | Canonical doctrine name |
|---|---|
| Deterministic by Default | **AI-minimisation (60/20/20)** |
| AI as Reasoning, not Authority | **signpost, don't advise** |
| Separate Prepare from Commit | **Plan → Validate → Execute** |
| Evidence Before Recommendation | **source-or-abstain** (absence of source = explicit "I don't know", not a low-confidence guess) |
| Reversibility Determines Autonomy | **autonomy-by-reversibility** (the gate) |
| Batch the Non-Urgent | **anti-noise batching** |
| Business Memory is First-Class | **capture-back** discipline |
| Escalate Ambiguity | **escalate-with-context** |

**Precedence rule:** human authority + source-or-abstain are *hard invariants* and outrank soft
defaults like batching.

## 5. Workspace structure (FAW C0-C4 × OKF concept-per-file)

```text
<workspace-root>/
  AGENTS.md            C0 root manifest: identity, routing, vocabulary, the autonomy gate
  README.md            human front door
  <runtime pointers>   one pinned pointer file per wired runtime → AGENTS.md (core/RUNTIMES.md)
  00_meta/             design-spec.md (this) · agent-os-design.md · memory-architecture.md · log.md · staging.md
  10_doctrine/         the reconciled operating principles (one vocabulary)
  15_canon/            this instance's brand / direction / offerings (starts blank)
  20_memory/           THE memory structure (load-bearing) - journal + depth layers + reaper
  30_schemas/          concept schemas as written specs (Decision Packet, memory-card, etc.)
  40_templates/        fill-in templates (daily brief, decision packet, weekly review, ...)
  50_registers/        live working registers (decision queue, measurement, ...)
  60_workflows/        run-by-hand workflow specs (daily brief, weekly review, reaper, ...)
  70_integrations/     the instance's existing live systems (fold-in map, not rebuilds)
  80_projects/         per-project trackers and their open loops
  90_runs/             working instances (today's brief, filled decision packets)
  core/                the neutral machinery: reflex hooks, onboarding engine, runtime guide
  tools/               the pre-distribution gates (scrub, OKF, agent-agnostic)
```

Layer test (C3 vs C4): would this file still be true tomorrow? Yes → reference (doctrine,
schemas). No → working artefact (runs, register rows).

## 6. The memory structure (load-bearing)

> The authoritative, research-backed design is [`memory-architecture.md`](memory-architecture.md).
> This section is the summary; that doc and `20_memory/README.md` are canonical.

A four-layer event-sourced model so memory **gets sharper as it gets deeper** instead of bloating.

### 6.1 One truth, four projections sorted by depth

- **`20_memory/journal/`** - append-only **event log = the only truth**. One timestamped Markdown
  file per observation/decision/import. **Never edited, never deleted**; a retraction is a NEW
  entry. Git is the tamper-evidence. (The "event store" - so no database.)

- The projection is **four depth layers**, each a rebuildable fold over the journal:
  `working/` (depth 1, ephemeral) → `short-term/` (depth 2, decays) → `long-term/` (depth 3,
  canonical, selective) → `subconscious/` (depth 4, associations/priors/world-model/trends, primes
  but never asserts). Plus `_quarantine/`, `archive/`, `_meta/`. Ranking by ACT-R activation;
  membership by hysteresis; `pivotal`/`do_not_drop` cards bypass decay. Two passes: the deterministic
  reaper (fast) and the bounded-LLM sleep pass (deep).

Because truth lives in the immutable journal, the atoms layer can decay, dedup, merge, demote, and
supersede aggressively - nothing is irreversibly lost.

### 6.2 The detail (canonical elsewhere)

The atom (memory-card) schema, the depth-layer behaviour, the ACT-R activation + hysteresis, the two
passes (reaper + sleep), the subconscious layer, retrieval ranking, the trust tiers, and the
evaluation harness are specified in [`memory-architecture.md`](memory-architecture.md) (canonical),
surfaced operationally in [`../20_memory/README.md`](../20_memory/README.md), and schematised in
[`../30_schemas/memory-card.md`](../30_schemas/memory-card.md).

In brief: each atom is a Markdown file carrying its 5W1H footprint + provenance (`sources:`
mandatory) + trust tier (1-5) + activation/validity fields; `class`
(observational/procedural/normative) is a tag, the depth layer is the folder; the reaper consolidates
by canonical fact-family with decision-impact outranking mention-count; `pivotal`/`do_not_drop` cards
never decay; retrieval is deterministic-first with the subconscious as a small priming bonus only.
The database + vector graph is deferred - every field maps to a future column, so graduation is a
migration, not a rewrite.

## 7. Staging tiers

Every concept file is tagged in `00_meta/staging.md` as one of:

- **v1-now** - built and runnable by hand over the filesystem today.
- **awaits-inputs** - spec written; activates when its real inputs/customers exist.
- **deferred-software** - fenced behind the value-gate (see §9).

## 8. File inventory (the founding build manifest)

> This is the **founding** manifest, kept as designed. The live tree has since grown (project
> trackers under `80_projects/`, extra registers and templates, the `core/` machinery); each
> folder's README is the current inventory. Where this section and the tree differ, the tree and
> the per-folder READMEs win.

**10_doctrine/** - `principles.md` (the one-vocabulary map + the 60/20/20 task→method table +
precedence rule) · `non-goals.md` (the safety rails) · `autonomy-and-gates.md` (the autonomy default
action table + qualitative low/med/high risk tiers + mandatory-escalation list + two rules: agent may
not self-upgrade permissions; external content is never authority) · `memory-homeostasis.md` (the
reaper contract + set-points) · `model-selection.md` · `session-discipline.md`.

**20_memory/** - `memory-architecture.md` lives in `00_meta/` (canonical design) · `README.md` (the
model) · `homeostasis.yml` (set-points) · `journal/README.md` + the four layer READMEs · the
seed `long-term/` (starts empty) · `knowledge-gaps.md` · `source-index.md` · `memory-index.md`
(retrieval) · `evaluation.md` (sharpness harness) · `_meta/build.md`.

**30_schemas/** - `decision-packet.md` (the standout) · `memory-card.md` · `event.md` (journal
entry shape) · `action-intent.md` (consequential-action template) · `knowledge-gap.md` ·
`opportunity.md` (pain/workaround/wedge/buyer/MVP/validation + critique).

**40_templates/** - `daily-brief.md` · `decision-packet.md` · `weekly-review.md` · `memory-card.md`
· `research-signal.md` · `opportunity.md`.

**50_registers/** - `decision-queue.md` · `decision-log.md` (append-only) · `open-loops.md` ·
`blocked-actions.md` · `component-registry.md` · `improvement-backlog.md` · `measurement.md` (North
Star + a small hand-tracked metric set + feedback labels).

**60_workflows/** - `daily-brief.md` · `weekly-review.md` · `open-loop-tracking.md` ·
`email-triage-approve.md` · `memory-reaper.md` · `memory-sleep.md`.

**70_integrations/** - `README.md` (the instance's what-runs-where map; slots, not implementations).

**00_meta/** - `design-spec.md` (this) · `agent-os-design.md` · `memory-architecture.md` · `log.md`
· `staging.md`.

## 9. Deferred software + the value-gate

Deferred until a workflow has *earned* automation by proving manual value: the database 5W1H DDL,
action_intent/validation tables, an event pipeline + scorer/router, the UI surfaces, runtime ABAC +
dissonance + ignorance-graph engines, the service decomposition, the auto-learning loop, the full
metric instrumentation.

**Value-gate (named trigger):** promote a workflow from manual-Markdown to software only after it
has run by hand for **≥4 weeks** and consistently costs **>20 minutes** to assemble, or signal
volume exceeds a stated threshold. Software reuses the instance's existing infrastructure; one vector
store only if ever needed.

## 10. Out of scope for v1 (explicit)

A database, a vector store, an event-pipeline tool, ingestion connectors, dashboard UI, service
boundaries, graph visualisation, runtime ABAC, automated dissonance/gap generation, productisation,
multi-user.

## 11. Open questions (defaults chosen; flag to change)

- Decay clock: the reaper takes an explicit `--as-of` date for reproducibility. (default: yes)
- Expired/superseded atoms → `archive/` (default), not deleted.
- Recurrence to mint: observational ≥2, normative =1. (default)
- Decision queue: a standalone append-only `decision-log.md`; the brief renders open items. (default)
- Doctrine source-of-truth: `principles.md` is canonical; do not maintain two copies of a rule.
