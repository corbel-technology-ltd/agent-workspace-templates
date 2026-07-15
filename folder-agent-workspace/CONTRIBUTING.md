# Contributing to Folder-Agent-Workspace

Folder-Agent-Workspace is a blank operating system, so contributions are improvements to the **OS itself**, not
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

Run the canonical extraction-safe distribution checks in
[`tools/README.md`](tools/README.md). Every command in that section must pass on a clean checkout.
Family maintainers also run the separately listed updater proof from the family checkout.

If you add or change a `related:` frontmatter edge, run `python3 tools/gen-related.py` to refresh the
body-link mirrors so `okf-check` stays green.

Keep the house style: British English, no em dashes, one concept per file, OKF-compatible frontmatter.
