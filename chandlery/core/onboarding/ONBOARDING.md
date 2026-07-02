---
id: core.onboarding
name: Onboarding - staged, confirm-before-write registry instantiation
type: workflow
layer: C1
status: current
owner: shared
created: 2026-07-02
tags: [onboarding, instantiation, placeholders, apply, neutral-core]
related:
  - {ref: ledger.md, dimension: where, polarity: enables}
---

# Onboarding playbook

Turn a freshly copied **blank Chandlery template** into a live, named capability registry. Staged
and confirm-before-write; the fill is deterministic via [`apply.py`](apply.py). Runtime-neutral:
any agent that can read files and run `python3` can execute it (`core/RUNTIMES.md`).

The four tokens (`placeholders.yml` is the single source of truth):

| Token | Meaning | Source |
|---|---|---|
| `CHANDLERY_NAME` | This registry's name (e.g. `Acme Chandlery`) | asked |
| `OWNER` | Who gates installs and packs | asked |
| `chandlery_slug` | Lowercase id handle | derived from `CHANDLERY_NAME` |
| `CREATED_DATE` | Instantiation date | auto = today |

## The staged flow

**A - sentinel.** Root `.uninitialised` present? Absent = already onboarded; stop and say so.

**B - gather (read-only).** Ask for `CHANDLERY_NAME` and `OWNER`; derive `chandlery_slug`
(slugify rule in `placeholders.yml`; ask if it cannot be clean); auto-fill `CREATED_DATE`.
Validate each against its regex; re-ask rather than write a bad value.

**C - confirm.** Show all four values; wait for an explicit "yes". Nothing is written before this.

**D - values.json.** Write the confirmed map at the registry root (one JSON object, strings).

**E - apply.** Preview with
`python3 core/onboarding/apply.py --root . --exclude 'registry/*/files/' --dry-run`, then run it
without `--dry-run`. **Keep the exclude**: capability payloads are cargo and may carry token
literals owned by other templates; onboarding must never rewrite them (`chandler.py verify` would
catch the corruption, but the exclude prevents it). The registry's own docs beside the cargo
(`registry/*/README.md`, manifests) are filled normally. Atomic + idempotent; restore-and-abort
on validation failure. Do not proceed past a non-zero exit.

**F - first ledger entry + verify.** Append under the marker line in [`ledger.md`](../../ledger.md):

```text
<CREATED_DATE> | onboarding | Chandlery initialised from the template; four tokens filled | seed stock carried: run `chandler.py list`
```

Flip `initialised: false` to `initialised: true` in `AGENTS.md` frontmatter, then prove the stock:
`python3 core/chandler.py verify` must be clean.

**G - delete the sentinel.** Only after D-F succeeded.

**H - you're live.** Confirm no `<<TOKEN>>` remains (`grep -rn "<<" .`; `{{...}}` markers are
expected). Then the two real next steps: `enrol` your workspaces, and `status` each one to see
where its tooling stands against the stock.

## Guardrails

Confirm before write; deterministic fill only (never hand-edit a token); the ledger starts at
initialisation and is append-only; onboarding records zero facts about anyone.

## Related

- [Registry ledger](../../ledger.md)
