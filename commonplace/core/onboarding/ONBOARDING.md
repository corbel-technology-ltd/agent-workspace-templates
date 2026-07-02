---
id: core.onboarding
name: Onboarding - staged, confirm-before-write workspace instantiation
type: workflow
layer: C1
status: current
owner: shared
created: 2026-06-27
tags: [onboarding, instantiation, placeholders, apply, checkpointed, neutral-core]
related:
  - {ref: 20_memory/journal/README.md, dimension: where, polarity: enables}
  - {ref: 30_schemas/event.md, dimension: what, polarity: requires}
---

# Onboarding playbook

Turn a freshly copied **blank template** into a live, named instance. The interview is **staged and
confirm-before-write**: nothing is written until the operator confirms the collected values. The
substitution itself is deterministic - this playbook gathers the answers and drives
[`apply.py`](apply.py); it never hand-edits a `<<TOKEN>>`.

This playbook is **runtime-neutral**: any agent that can read files and run `python3` can execute
it. Runtime skill/command wrappers are thin pointers to THIS file - see `core/RUNTIMES.md` for the
wired adapters.

**Two marker syntaxes, only one is filled here.** `<<NAME>>` markers are onboarding-fill tokens,
replaced exactly once at instantiation by `apply.py`. `{{...}}` markers (e.g. `{{YYYY-MM-DD}}` in
`40_templates/daily-brief.md`) are runtime markers filled per-artefact, per-run - leave them
untouched. The nine tokens below are the complete fill set; the generic literal `<<TOKEN>>` that
appears in prose is documentation, not a fill token.

## When this runs

The template ships with a `.uninitialised` sentinel at its root. The session-start gate
(`core/hooks/onboarding-gate.py`, wired by your runtime adapter) detects it and tells a fresh agent
to run THIS playbook before any other work. Run it once, at first boot of a new instance. After it
completes the sentinel is gone and the gate is silent forever.

## The nine tokens

`placeholders.yml` is the single source of truth for the token set, validation rules, and
replacement order. Do not invent tokens or rules here - read them from `placeholders.yml` at run
time. The table is a quick reference only.

| Token | Meaning | Source | Validation |
|---|---|---|---|
| `WORKSPACE_NAME` | Workspace / instance name (e.g. `Acme`) | asked | 1-60 chars, single line |
| `ENTITY` | Legal / operating entity (e.g. `Acme Ltd`) | asked | 1-80 chars, single line |
| `OWNER` | Founder / operator name (e.g. `Alex`) | asked | 1-60 chars, single line |
| `AGENT_NAME` | Agent persona name (e.g. `Aster`) | asked | 1-40 chars, single line |
| `workspace_slug` | Lowercase id handle (e.g. `acme`) | derived from `WORKSPACE_NAME` | `^[a-z][a-z0-9-]{0,40}$` |
| `agent_slug` | Lowercase agent handle (e.g. `aster`) | derived from `AGENT_NAME` | `^[a-z][a-z0-9-]{0,40}$` |
| `WORKSPACE_ROOT_ENV` | Env-var name for the root override (e.g. `ACME_ROOT`) | asked | `^[A-Z][A-Z0-9_]{0,40}$` |
| `SHARED_CONTEXT_PATH` | Absolute path to the shared-context store (may be empty) | asked | single line; empty allowed |
| `CREATED_DATE` | Instantiation date | auto = today | `^\d{4}-\d{2}-\d{2}$` |

## Derivation rules

- **`workspace_slug` / `agent_slug`** derive from the matching `*_NAME` by slugify: lowercase;
  collapse each run of characters outside `[a-z0-9]` to a single `-`; strip leading/trailing `-`.
  The result must match `^[a-z][a-z0-9-]{0,40}$`. If it would start with a digit, be empty, or
  exceed 41 chars, **ask the operator** for the slug instead of deriving.
- **`CREATED_DATE`** auto-fills to today (`YYYY-MM-DD`). Confirm it; do not ask.

## The staged flow

Each step is a checkpoint. A failure leaves a **known, resumable state**: you can always tell where
you stopped from the on-disk artefacts (the sentinel still present, `values.json` written or not,
`apply.py`'s own snapshot/checkpoints, the journal entry present or not). Resume from the first
incomplete step; never redo a completed write blindly.

### Step A - detect the sentinel

Confirm the root `.uninitialised` file exists. If it is **absent**, this workspace is already
onboarded: stop and say so (do not re-run; re-running would have nothing to fill). If present,
proceed.

### Step B - gather values (conversationally, read-only)

Ask the operator, in a short batch, for the six **asked** tokens:

1. `WORKSPACE_NAME` - the workspace/instance name.
2. `ENTITY` - the legal/operating entity it serves (drop any company number unless wanted).
3. `OWNER` - the founder/operator's name.
4. `AGENT_NAME` - the agent's name/persona.
5. `WORKSPACE_ROOT_ENV` - the env-var name the hooks read for the root override (e.g. `ACME_ROOT`).
6. `SHARED_CONTEXT_PATH` - the absolute path to the shared-context store, or blank if none is wired.
   If the owner runs a **Lodestar** shared-context store, this is its root; the store's own
   link-in contract then registers this workspace in its roster.

Then **derive** `workspace_slug` and `agent_slug` (slugify rule above; ask only if a clean slug
can't be derived) and **auto-fill** `CREATED_DATE = today`. Validate each value against its
`placeholders.yml` regex as you go; re-ask any that fail rather than writing a bad value. This step
writes nothing.

### Step C - confirm (the gate)

Show the full collected set back to the operator - all nine values, including the derived slugs and
the auto date - and **wait for explicit confirmation**. This is the confirm-before-write line. If
the operator corrects anything, amend and re-show. Do not cross into Step D without a clear "yes".

### Step D - write `values.json`

Write the confirmed map as `values.json` at the workspace root (one JSON object `{token: value}`,
all nine keys, strings). This is the first on-disk write and the first checkpoint: if a later step
fails, `values.json` is already on disk and the run resumes from here.

### Step E - run `apply.py` (snapshot -> replace -> validate)

Optionally preview first: `python3 core/onboarding/apply.py --root . --dry-run` reports what would
change without writing. Then run `python3 core/onboarding/apply.py --root .` from the workspace
root. `apply.py` is atomic and idempotent: it snapshots the tracked tree, substitutes every
`<<TOKEN>>` with context-aware escaping (`.py`/`.json`/YAML-frontmatter/prose), validates that no
registered token is left over, then on success deletes the snapshot, its checkpoints, and
`values.json`. On validation failure it **restores the tree from the snapshot** and aborts non-zero
- fix the offending value (or `values.json`) and re-run; a re-run from a clean tree with no
`values.json` is a safe no-op. Do not proceed past a non-zero exit.

### Step F - seed registers + first journal entry

- **Registers:** the `50_registers/` files ship as blank zero-row skeletons; confirm they are in
  that clean state (headers present, no example rows in the live `## Open` tables). Seeding here
  means *leaving them empty and correct*, not inventing rows.
- **Identity:** in `AGENTS.md` frontmatter, flip `initialised: false` to `initialised: true`, and
  write the first state line in `00_meta/staging.md` (Instance status / Current focus).
- **First journal entry:** append ONE new immutable entry under `20_memory/journal/` named
  `YYYY-MM-DD-HHMM-workspace-initialised.md`, conforming to [`30_schemas/event.md`](../../30_schemas/event.md)
  (`type: import` or `observation`, `who: [<agent_slug>]`, `where: [<workspace_slug>-workspace]`,
  `source_type: system`, `trust: trusted`). The journal is **append-only** - write a NEW file, never
  edit an existing one (the `journal-guard` reflex enforces this where the runtime wires it; the
  optional git pre-commit guard in `core/git-hooks/` enforces it for every runtime). Body:
  "Workspace initialised from the template; placeholders filled via apply.py; nine tokens set."

### Step G - delete the sentinel

Delete the root `.uninitialised` file. This is the completion marker: once gone, the
onboarding gate is silent on every future session. Do this only after Steps D-F succeeded,
so an interrupted run is always re-runnable while the sentinel survives.

### Step H - you're live summary

Print a short "you're live, here's how to use it" summary:

- Confirm the nine values that were set and that no *registered* token survived outside the
  substitution-excluded machinery. The check:
  `grep -rn "<<" --include='*.md' --include='*.py' --include='*.yml' --include='*.json' . | grep -v 'core/onboarding/'`
  should show only the documented literals - the generic `<<TOKEN>>`/`<<NAME>>` marker examples in
  prose and hook docstrings, never a filled token like `<<OWNER>>`. (`core/onboarding/` is excluded
  from substitution by design and legitimately keeps the token names verbatim.) Any `{{...}}` left
  is an expected runtime marker.
- Point at the entry doors: `AGENTS.md` (identity, routing, the safety gate), `00_meta/staging.md`
  (current state), `20_memory/journal/` (the truth log), `50_registers/` (the live registers).
- Note that the session-start brief (`core/hooks/session-brief.py`) now orients every future
  session, and that authority stays gated - the agent prepares, the owner approves.

## Resumability cheatsheet

| If you find… | You stopped at | Resume by |
|---|---|---|
| `.uninitialised` present, no `values.json` | before Step D | re-running from Step B/C |
| `.uninitialised` + `values.json` present | after Step D, before/at Step E | re-running `apply.py` (Step E) |
| `.uninitialised` present, no `values.json`, tree has NO leftover `<<TOKEN>>` | apply.py succeeded; Steps F-G pending | doing Steps F, then G |
| `.uninitialised` absent | fully onboarded | nothing - stop |

## Guardrails

- **Confirm before write.** Steps A-C touch nothing on disk. The first write is `values.json` (Step
  D), only after explicit confirmation.
- **Deterministic fill only.** Never hand-edit a `<<TOKEN>>`; always go through `apply.py`. It owns
  escaping and the leftover validator.
- **Append-only journal.** The initialisation entry is a NEW file; never overwrite an entry.
- **Authority stays gated.** Onboarding sets up the workspace; it does not send, publish, pay, or
  sign anything. That posture is the whole point of the control plane (see `AGENTS.md` safety gate).

## Related

- [Journal — the append-only event log](../../20_memory/journal/README.md)
- [Journal event schema](../../30_schemas/event.md)
