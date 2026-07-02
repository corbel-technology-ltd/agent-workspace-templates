---
id: <<store_slug>>.tools.readme
name: Pre-distribution gates - scrub, okf, agnostic, shared-lint
type: doc
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [tools, gates, distribution, scrub, okf, agnostic, shared-lint]
related:
  - {ref: SHARED.md, dimension: why, polarity: explains}
---

# Pre-distribution gates

Four deterministic, stdlib-only gates that must be **green before this store is distributed**,
plus one maintenance tool (`gen-related.py`). Gates, not linters: they fail loud (exit 1) so a
leak, a broken knowledge edge, vendor lock-in, or structural drift cannot ship. They read the live
git tree via `git ls-files`, so they check exactly what would be distributed.

Three are vendored byte-identical across the FAW family (scrub, okf, agnostic - the family's
capability registry tracks them); `shared-lint` is this template's own.

## `scrub-check.py` - zero private terms

Scans every tracked file (contents, frontmatter ids, filenames) for the terms in
[`scrub-terms.txt`](scrub-terms.txt) - case-insensitive, whole-word. In THIS template the terms
file is **generated**: populate `boundaries/boundaries.md` (Never share), then
`python3 core/derive-scrub.py --write`. The confidentiality line is written once; the denylist
derives.

Read the exit code as "is this tree safe to share?": a **live** store intentionally fails (its
own boundaries file, people files, and tech entries carry the private terms - that is their job).
Green is required for the **blank template** and for any copy you distribute; a distributable
copy must have its boundaries genericised, and this gate is what catches you if you forget.

## `okf-check.py` - OKF frontmatter + body-link mirroring

Every tracked `*.md` with frontmatter: `type` present; every `related[].ref` exists and is
mirrored as an inline body link (else `DANGLING` / `UNMIRRORED`); `index.md` reserved. Keep it
green with `gen-related.py` (regenerates the `## Related` sections; `--check` for CI).

## `agnostic-check.py` - neutral core + thin adapters

No vendor/runtime term outside the adapter layer + `core/RUNTIMES.md`; every adapter pointer
stays a pointer (line cap, must defer to `AGENTS.md`, no content sections).

## `shared-lint.py` - the store's own shape

Structure lock (no unknown top-level files/folders - dumping needs sign-off, not drift), the file
cap from `_meta/governance.md`, frontmatter completeness (`id`/`type`/`status`/`owner`), the
CHANGES trailer format, and the coordination table headers.

## Running them

```bash
python3 tools/gen-related.py                # refresh mirrors after editing related: edges
python3 tools/scrub-check.py;    echo "exit $?"
python3 tools/okf-check.py;      echo "exit $?"
python3 tools/agnostic-check.py; echo "exit $?"
python3 tools/shared-lint.py;    echo "exit $?"
```

All four must print a clean line and exit `0` before distribution.

## Related

- [<<STORE_NAME>>](../SHARED.md)
