---
id: <<capability-registry_slug>>.tools.readme
name: Pre-distribution gates - scrub, okf, agnostic, skill-surface (+ chandler verify)
type: doc
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [tools, gates, distribution, scrub, okf, agnostic, skill-surface, verify]
related:
  - {ref: AGENTS.md, dimension: why, polarity: explains}
---

# Pre-distribution gates

Four deterministic, stdlib-only gates plus the registry's own (`core/chandler.py verify`), all of
which must be **green before this registry is distributed**, plus one maintenance tool
(`gen-related.py`). The four shared gates are vendored byte-identical across the FAW family - and
stocked in this very registry as capabilities, which is how the family keeps the copies honest.

- **`scrub-check.py`** - zero private terms across contents, frontmatter ids, and filenames
  (whole-word, case-insensitive; configure [`scrub-terms.txt`](scrub-terms.txt) with your fleet's
  private names).
- **`okf-check.py`** - OKF-compatible frontmatter + body-link mirroring (`gen-related.py` keeps
  the mirrors green; `--check` for CI).
- **`agnostic-check.py`** - no vendor/runtime term outside the adapter layer; adapter pointers
  stay thin pointers.
- **`skill-surface-check.py`** - tracked skill metadata, names, neutral links and thin pointers.
- **`core/chandler.py verify`** - every stocked payload matches its manifest checksum; versions
  are positive integers.

## Running them

```bash
python3 tools/scrub-check.py;    echo "exit $?"
python3 tools/okf-check.py;      echo "exit $?"
python3 tools/agnostic-check.py; echo "exit $?"
python3 tools/skill-surface-check.py; echo "exit $?"
python3 core/chandler.py verify; echo "exit $?"
```

All five must print a clean line and exit `0` before distribution.

## Related

- [<<CHANDLERY_NAME>>](../AGENTS.md)
