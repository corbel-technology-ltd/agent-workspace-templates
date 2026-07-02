# Contributing to Commonplace

Commonplace is a blank operating system, so contributions are improvements to the **OS itself**, not
to any one instance's content.

## What belongs upstream

Generic improvements that would help every future workspace:

- doctrine, schemas, templates, and workflow specs
- the reflex hooks and the onboarding engine (`core/`)
- the runtime adapters and the wiring guide (`core/RUNTIMES.md`)
- the memory model and the safety gate
- the `tools/` gates and the shared conventions

## What does not

Anything specific to one instance: its canon, brand, integrations, register rows, journal entries, or
run artefacts. Those live in your own copy, never here.

## Before you open a PR

Run the gates and the onboarding tests. All should pass on a clean checkout:

```bash
python3 tools/scrub-check.py
python3 tools/okf-check.py
python3 tools/agnostic-check.py
python3 tools/gen-related.py --check
python3 core/onboarding/tests/test_apply.py
```

If you add or change a `related:` frontmatter edge, run `python3 tools/gen-related.py` to refresh the
body-link mirrors so `okf-check` stays green.

Keep the house style: British English, no em dashes, one concept per file, OKF-compatible frontmatter.
