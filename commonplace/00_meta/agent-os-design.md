---
id: <<workspace_slug>>.meta.agent-os-design
name: Agent OS design — constitution / reflexes / playbooks / cognition / memory
type: design-spec
layer: C0
status: current
owner: shared
created: <<CREATED_DATE>>
source: design principle (operator) + verified runtime hook reality (per adapter, core/RUNTIMES.md)
tags: [agent-os, hooks, skills, subagents, constitution, instrumentation]
related:
  - {ref: AGENTS.md, dimension: what, polarity: explains}
  - {ref: 10_doctrine/autonomy-and-gates.md, dimension: how, polarity: requires}
  - {ref: 20_memory/README.md, dimension: where, polarity: requires}
---

# Agent OS design

How this workspace becomes intelligent **by instrumenting the environment**, not by lengthening the
prompt. The principle:

> `AGENTS.md` describes **judgment**. Hooks enforce **reflexes**. Skills hold **playbooks**.
> Subagents handle **heavy cognition**. The journal + registers hold **memory/evidence**.

## The mapping

| Principle layer | Lives in | Status |
|---|---|---|
| **Constitution** (judgment) | `AGENTS.md` | exists |
| **Reflexes** (enforce) | `core/hooks/` (logic), wired per runtime by a thin adapter (`core/RUNTIMES.md`) | **installed** (all six: journal-guard, onboarding-gate, session-brief, session-digest, reaper, registry-drift) |
| **Playbooks** | `core/` (e.g. `core/onboarding/`), surfaced per runtime as skills/commands; the `60_workflows/` specs graduate here when invoked often | onboarding shipped; others graduate on use |
| **Heavy cognition** | the runtime's subagent surface (adapter-specific) | deferred (no input/consumer yet) |
| **Memory / evidence** | `20_memory/journal/` (events) + `50_registers/` (observations, decisions, backlog, metrics) | **exists — reuse, do not rebuild** |

The key fit: **hooks are the sensory organs that append to the immutable journal.** The reaper folds
the journal; the subconscious spots trends. There is no parallel `ops/metrics/` tree — that collapses
into reuse of the journal + registers. No new evidence tree.

## Verified hook reality (per runtime)

Hook capability differs per runtime: which lifecycle events exist, which can block, and what the
context cost is. That detail is adapter-specific, so it lives with the adapters — the verified
event list, block semantics, and configuration surface for each wired runtime are documented in
[`core/RUNTIMES.md`](../core/RUNTIMES.md). Two rules travel with every runtime:

- **The neutral contract is fixed.** Core hooks read a documented JSON payload on stdin and signal
  "block" with exit 2 (`core/hooks/README.md`); the adapter maps that onto whatever its runtime
  offers. A runtime with no hooks degrades to the documented manual protocol plus the git-level
  journal guard.
- **Verify before relying.** Hook surfaces drift across runtime versions, and even a verifier can
  hallucinate events — re-check the live binary's event names before wiring anything new.

## Hook discipline (the rule that keeps this from re-bloating)

- **Silent by default.** Write to the journal/registers; return `additionalContext` only when it
  changes the current decision.

- **Block only the unsafe**, with **narrow matchers** (not a blanket BLOCK on whole tool classes —
  that is chatty and obstructive).

- **No write-only dead logs** — wire a consumer in the same step, or don't write.
- **Notify only when a human is needed.**

## Staged plan

### NOW (built / shipped with the template)

- **`AGENTS.md`** is the full constitution (operating loop, proactivity + prioritisation hierarchy,
  sensor doctrine, the OS map, definition of done). Judgment only.

- **`50_registers/improvement-backlog.md`** — where proactivity output lands, with a prose priority
  tag (do-now / suggest / log / ignore).

- **Reflex hooks**, logic in `core/hooks/`, wired per runtime (installing or changing wiring edits
  runtime settings, so it needs operator approval):
  1. **Journal-immutability guard** (pre-tool-use) — block any modify/overwrite/delete targeting
     `20_memory/journal/*`. Turns the load-bearing append-only invariant into a reflex. Narrow
     matcher; silent unless it blocks. An optional git pre-commit guard (`core/git-hooks/`) backs it
     at commit time for any runtime.
  2. **Onboarding gate** (session start) — while the `.uninitialised` sentinel exists, route the
     agent to the onboarding playbook before any other work.
  3. **Session brief** (session start) — a boot-orientation block (who you are, load shared context,
     read `00_meta/staging.md`, re-verify the newest handover) plus open `decision-queue` items and
     the per-project `## Open` loops aggregated from `80_projects/*/loops.md` (`## Closed` excluded).
     A few lines; situational awareness at near-zero cost.
  4. **Session digest** (session end) — append one journal event (what changed, decisions, files) so
     the session is captured as truth for the reaper. Silent (writes to `journal/`).
  5. **Reaper** (session end) — the deterministic fast memory pass.
  6. **Registry-drift sensor** (session end, advisory) — flag uncatalogued ops components.

### AWAIT-NEED (specced, switch on when the input exists)

- A prompt-submit task-router (deterministic classify) — once prompt volume justifies it.
- Post-tool-use metric/data-stream detection + a `metric-scout` subagent — once the journal has real
  volume for it to scan (a subagent with no journal to read is pointless now).

- A file-changed data-stream scout — once there are real data streams to map.
- Playbooks — graduate a `60_workflows/` spec into `core/` (surfaced as a runtime skill) when it is
  invoked repeatedly.
- A pre-compaction snapshot — useful insurance once sessions carry heavy context.

### DEFER (no data / over-strict)

- Any statistical graduation apparatus (no events logged yet — use plain counts if/when fed).
- A broad `PreToolUse` BLOCK on send/publish/push (over-strict vs the gate's CONFIRM; match narrowly
  on `--force` / protected branches only, and only once such tooling exists here).

- `risk-reviewer` / `simplifier` subagents — reuse a review skill / a doctrine line first.

## Prioritisation (prose hierarchy, not a formula)

Proactivity without prioritisation is noise. Rank by, in order: **blocking** (unblocks the founder or
a commitment) → **strategic** (advances the locked direction) → **opportunistic** (nice-to-have).
Within that, gate each surfaced improvement: **do-now** (clearly high-impact + low-risk + reversible)
· **suggest** (worth a Decision Packet) · **log** (to the backlog) · **ignore**. No multiplicative
score with inputs we don't yet measure — that reads precise and gets hand-waved. Promote to a real
score only when the inputs (confidence, recurrence, cost-to-delay) are actually tracked.

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
  `homeostasis.yml` only when the journal actually feeds them (no data yet — plain counts until then).
- **Prior→policy graduation requires human review** unless purely local, reversible, low-risk — the
  gate, applied to self-modification.

## What stays in `AGENTS.md` vs moves out

- **Stays (judgment):** mission, the one vocabulary, hard invariants, the gate's *intent*, the
  operating loop, the prioritisation hierarchy, the sensor doctrine, the OS map, definition of done.

- **Moves out (enforcement/inventory):** the gate's *enforcement* → a `PreToolUse` hook; long
  playbooks → skills; heavy audits → subagents; events/metrics → the journal + registers.

## Related

- [<<WORKSPACE_NAME>>](../AGENTS.md)
- [Autonomy & gates — the single decision gate](../10_doctrine/autonomy-and-gates.md)
- [Memory structure — the model](../20_memory/README.md)
