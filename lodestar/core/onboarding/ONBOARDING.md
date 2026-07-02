---
id: core.onboarding
name: Onboarding - staged, confirm-before-write store instantiation
type: workflow
layer: C1
status: current
owner: shared
created: 2026-07-02
tags: [onboarding, instantiation, placeholders, apply, checkpointed, neutral-core]
related:
  - {ref: _meta/governance.md, dimension: how, polarity: requires}
  - {ref: CHANGES.md, dimension: where, polarity: enables}
---

# Onboarding playbook

Turn a freshly copied **blank Lodestar template** into a live, named shared-context store. The
interview is **staged and confirm-before-write**: nothing is written until the principal confirms
the collected values. The substitution is deterministic - this playbook gathers answers and drives
[`apply.py`](apply.py); it never hand-edits a `<<TOKEN>>`.

Runtime-neutral: any agent that can read files and run `python3` can execute it. Runtime
skill/command wrappers are thin pointers to THIS file (`core/RUNTIMES.md`).

**Two marker syntaxes, only one is filled here.** `<<NAME>>` markers are onboarding-fill tokens,
replaced exactly once by `apply.py`. `{{...}}` markers (in the `_`-prefixed templates) are runtime
markers filled per artefact - leave them untouched. The six tokens below are the complete fill
set; `placeholders.yml` is the single source of truth.

## When this runs

The template ships with a `.uninitialised` sentinel at its root. The session-start gate
(`core/hooks/onboarding-gate.py`, wired by your runtime adapter) detects it and routes a fresh
agent here before any other work. Run once, at first boot. After completion the sentinel is gone
and the gate is silent forever.

## The six tokens

| Token | Meaning | Source | Validation |
|---|---|---|---|
| `STORE_NAME` | The store's name (e.g. `Alex-Shared`) | asked | 1-60 chars, single line |
| `PRINCIPAL_NAME` | The person this store describes (e.g. `Alex`) | asked | 1-60 chars, single line |
| `store_slug` | Lowercase id handle (e.g. `alex-shared`) | derived from `STORE_NAME` | `^[a-z][a-z0-9-]{0,40}$` |
| `OBJECTION_WINDOW_HOURS` | Governance window length | asked (default 24) | `^[1-9][0-9]{0,2}$` |
| `FILE_CAP` | Max content files across the content folders | asked (default 30) | `^[1-9][0-9]{0,2}$` |
| `CREATED_DATE` | Instantiation date | auto = today | `^\d{4}-\d{2}-\d{2}$` |

Derivation: `store_slug` by the slugify rule in `placeholders.yml` (ask instead of derive if it
cannot be clean). `CREATED_DATE` auto-fills to today; confirm, do not ask.

## The staged flow

Each step is a checkpoint; a failure leaves a known, resumable state (the sentinel, `values.json`,
apply.py's own snapshot). Resume from the first incomplete step.

### Step A - detect the sentinel

Root `.uninitialised` present? Absent means already onboarded: stop and say so.

### Step B - gather values (read-only)

Ask the principal for `STORE_NAME`, `PRINCIPAL_NAME`, `OBJECTION_WINDOW_HOURS` (offer 24), and
`FILE_CAP` (offer 30). Derive `store_slug`; auto-fill `CREATED_DATE`. Validate each against its
`placeholders.yml` regex; re-ask rather than write a bad value. This step writes nothing.

### Step C - confirm (the gate)

Show all six values back and **wait for explicit confirmation**. Amend and re-show on any
correction; do not proceed without a clear "yes".

### Step D - write `values.json`

The confirmed map, one JSON object `{token: value}` (numbers as strings), at the store root.

### Step E - run `apply.py`

Preview: `python3 core/onboarding/apply.py --root . --dry-run`. Then run it without the flag.
Atomic + idempotent: snapshot, substitute with context-aware escaping, validate zero leftovers,
clean up on success, restore-and-abort on failure. Do not proceed past a non-zero exit.

### Step F - first ledger entry

Append the first entry to [`CHANGES.md`](../../CHANGES.md), directly under the marker line:

```text
<CREATED_DATE> | onboarding | Store initialised from the Lodestar template; six tokens filled; store blank pending calibration | window: n/a (initialisation)
```

Then flip `initialised: false` to `initialised: true` in `SHARED.md` frontmatter.

### Step G - delete the sentinel

Remove `.uninitialised`. Only after D-F succeeded, so an interrupted run stays re-runnable.

### Step H - you're live summary

Confirm the six values and that no `<<TOKEN>>` remains (`grep -rn "<<" .` - any `{{...}}` left is
an expected runtime marker). Then point at the two real next steps:

1. **Calibrate.** The store is deliberately blank: `identity/`, `boundaries/`, `glossary/`, and
   `calibration-os/preferences/` earn content through calibration sessions, never invention.
   Populating `boundaries/` first is recommended - then `python3 core/derive-scrub.py --write`
   arms the scrub gate.
2. **Link the first workspace.**
   `python3 core/link-workspace.py --name <ws> --path </abs/path> --agent <name>`.

## Guardrails

- **Confirm before write.** Steps A-C touch nothing; the first write is `values.json`.
- **Deterministic fill only.** Never hand-edit a `<<TOKEN>>`; apply.py owns escaping + validation.
- **The ledger starts at initialisation.** Step F's entry is the store's first history line;
  everything after follows [`_meta/governance.md`](../../_meta/governance.md).
- **No invention.** Onboarding sets parameters; it records zero facts about the principal.

## Related

- [Governance - the full edit protocol](../../_meta/governance.md)
- [Shared profile changelog](../../CHANGES.md)
