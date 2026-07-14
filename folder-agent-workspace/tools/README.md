---
id: <<workspace_slug>>.tools.readme
name: Pre-distribution gates & maintenance
type: doc
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [tools, gates, distribution, scrub, okf, frontmatter, decomposition]
related:
  - {ref: AGENTS.md, dimension: why, polarity: explains}
---

# Pre-distribution gates

The deterministic, stdlib-only gates below must be **green before this template is distributed**.
They are gates, not linters: they fail loud (exit 1) so a leak, broken knowledge edge, runtime
lock-in, or oversized context file cannot ship. The maintenance and self-test tools are also pure
Python 3 standard library - no dependencies, no network. The gates read the live git tree via
`git ls-files`, so they check exactly what would be distributed.

The contract they enforce is set by the root manifest, [`AGENTS.md`](../AGENTS.md)
(OKF v0.1 compatibility + the typed-edge / body-link mirroring convention).

## `scrub-check.py` - zero in-house terms

Asserts that **no in-house term leaks** into the distributable template. It reads
the term list from [`scrub-terms.txt`](scrub-terms.txt) (one lowercase term per
line; `#` comments and blank lines ignored) and scans every git-tracked file
across **three surfaces**:

1. file **contents** (every line),
2. frontmatter **`id:`** values,
3. **filenames** (the tracked path itself).

Matching is case-insensitive and **whole-word** (regex `\b` boundaries), so a short
term never fires as a substring of a longer token (e.g. an in-house `cat` would not
match `category`, and a generic English homograph would not match `neighbouring`).
Collision-prone terms are still reported for human review - a hit is a prompt to
look, not proof of a leak. The terms file and the `tools/` check scripts are
excluded from the scan.

Output: `path:line: term` for each hit. Exit `1` on any hit, `0` if clean.

## `okf-check.py` - OKF frontmatter + body-link mirroring

Asserts that durable Markdown is **OKF-compatible** and that every typed
`related[].ref` edge is mirrored into the body so a plain OKF consumer sees it. For
every git-tracked `*.md` with frontmatter it verifies:

- required key **`type`** is present and non-empty;
- each **`related[].ref`** target **exists** (else `DANGLING`) **and** appears as an
  inline markdown body link - basename or path match (else `UNMIRRORED`);
- reserved files: **`index.md`** must carry **no** frontmatter; **`log.md`** is the
  date-grouped change log. Reserved files are exempt from the `type`/`related`
  requirements; a non-reserved concept file missing `type` is flagged.

Frontmatter is parsed by a minimal hand parser (the leading `---` block is split and
line-scanned for `type:` and `ref:`) - no PyYAML, stdlib only.

Output: `path: ref -> DANGLING|UNMIRRORED` or `path: missing type`. Exit `1` on any
violation, `0` if clean.

## `agnostic-check.py` - neutral core + thin adapters

Asserts the agent-agnostic law: **no vendor/runtime term outside the adapter layer**, and **every
adapter stays a thin pointer**. Each registered pointer file must stay within the line cap, name
`AGENTS.md` as the canonical manifest, and carry no content sections; every other tracked file
(outside the runtime config dirs and the sanctioned registry `core/RUNTIMES.md`) must be free of
vendor terms, whole-word and case-insensitive. This is what makes "no behaviour depends on a
specific vendor" checkable instead of aspirational.

Output: `path:line: vendor term ...` or a pointer-purity message per violation. Exit `1` on any
violation, `0` if clean.

## `gen-related.py` - mirror typed edges into a body section

Keeps `okf-check` green deterministically. For every content file with frontmatter
`related:` edges it generates or refreshes a uniform **`## Related`** body section
listing each ref as a markdown link (title derived from the target's `name:` or its
`# H1`). Reserved files (`index.md`, `log.md`) and edge-less files are skipped. It is
**idempotent** (re-running changes nothing) and supports `--check` (report-only, exit
`1` if any file would change) for CI.

The maintenance loop: add or change a `related:` edge, run `gen-related.py`, and
`okf-check` passes. Do not hand-maintain the `## Related` sections - regenerate them.

## `template-update.py` - safe live-instance template updates

Uses the instantiation origin stamp to classify the managed spine and fetch updates. Two independent
hashes make repeated cycles safe: `managed_manifest[path]` is the last reviewed upstream candidate,
and `accepted_local_manifest[path]` exists only when the reviewed local result differs.
`accepted-customized` is reviewed and protected; `customized` is unreviewed. Accepting with a
candidate advances the upstream base to the candidate hash and records the local result separately;
accepting without a candidate leaves the existing upstream base intact. Local-only paths stay outside
updater state until upstream introduces the same path. Apply emits `.template-new` only for a real
upstream delta or a manifest-backed missing file. `--status` is offline, and the tool never touches
instance-content paths. `update-selftest.py` proves this flow in disposable repositories.

## `decomposition-check.py` - context decomposition (concept folders with index maps)

A workspace health gate for the decomposition doctrine
([`10_doctrine/context-decomposition.md`](../10_doctrine/context-decomposition.md)): large durable
context decomposes into one-concept notes behind an index map so context loads granularly. Every
git-tracked file is in scope by default; exceptions are explicit, per-file, and must carry a reason
in `tools/decomposition-exceptions.txt`.

Five checks:

1. **Prose size** - a `.md` file outside the structural exemptions may not exceed the doctrine's
   150-line or 12,000-character ceiling unless it has a necessary exceptions entry. Concept notes
   have the same ceilings.
2. **Code size** - recognised code files (`.py`, `.js`, `.sh`, `.ts`, `.tsx`, `.jsx`, `.mjs`,
   `.cjs`, `.rs`, `.go`, `.rb`, `.java`, `.c`, `.h`, `.cpp`, `.hpp`, `.bash`) may not exceed the
   500-line ceiling unless an exception cites the atomic code/test-suite keep-intact class.
3. **Exception hygiene** - every row must be unique, reasoned, tracked, necessary, and outside a
   structural exemption; duplicate, stale, reasonless, and unnecessary rows fail.
4. **Owning index** - every concept note must have a genuine top-level frontmatter `status:` key
   and an actual Markdown link or related-edge ref to its owning `00-INDEX.md`. This still applies
   in exempt directories and to excepted notes.
5. **Readable inputs** - an unreadable tracked Markdown or recognised code file is a violation.

Structural exemptions mirror the doctrine's keep-whole classes: `AGENTS.md`, `50_registers/**`,
`20_memory/**`, `90_runs/**`, `30_schemas/**`, `40_templates/**`, `CHANGELOG.md`, and
non-code/non-Markdown files. Runtime pointer files need no size exemption because the adapter-purity
gate already caps them to a few lines.

Output: one violation line per hit. Exit `1` on any violation, `0` if clean.

## Running them

```bash
python3 tools/gen-related.py               # refresh the ## Related mirrors after editing edges
python3 tools/scrub-check.py;    echo "exit $?"
python3 tools/okf-check.py;      echo "exit $?"
python3 tools/agnostic-check.py; echo "exit $?"
python3 tools/memory-selftest.py; echo "exit $?"
python3 tools/update-selftest.py; echo "exit $?"
python3 tools/decomposition-check.py; echo "exit $?"
python3 tools/decomposition-selftest.py; echo "exit $?"
```

All gates must print a clean line and exit `0` before distribution. While the
build is in progress a gate may legitimately exit `1` (mirroring not yet completed,
scrub pass unfinished) - that is expected mid-build. The release gate is: **all
green**.

## Related

- [<<WORKSPACE_NAME>>](../AGENTS.md)
