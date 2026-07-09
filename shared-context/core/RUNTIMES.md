---
id: core.runtimes
name: Runtime adapters - the contract and the wiring guide
type: reference
layer: C0
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [runtimes, adapters, agent-agnostic, wiring, portability]
related:
  - {ref: core/README.md, dimension: why, polarity: derived_from}
---

# Runtime adapters

This store is **runtime-neutral by construction**; a runtime attaches through a thin adapter -
translation and wiring only, never policy. This file is the adapter contract and the ONE
sanctioned place where runtime/vendor specifics are documented (`tools/agnostic-check.py`
enforces that).

A store needs far less wiring than a workspace. The whole contract:

| Integration point | Wire | Payload |
|---|---|---|
| Pointer file at root | the file your runtime auto-loads, pointing at `AGENTS.md` (canonical text below) | - |
| Session start | `core/hooks/onboarding-gate.py` then `core/hooks/store-brief.py`; inject stdout as context | none (any stdin JSON ignored) |

Canonical pointer text (all adapters carry exactly this, with their runtime's name in the heading):

```markdown
# <Runtime> adapter

This store uses `AGENTS.md` as the canonical root manifest.

Before doing anything, read `AGENTS.md` and follow its routing rules.

If there is any conflict between this file and `AGENTS.md`, `AGENTS.md` wins.

This file is a pinned pointer, not a document. Do not add content here;
`tools/agnostic-check.py` fails if it grows beyond a pointer.
```

## Wire a new runtime (10 minutes)

1. **Pointer file (2 min).** Copy the canonical text into the file your runtime auto-loads; add
   the filename to `ADAPTER_POINTERS` in `tools/agnostic-check.py`.
2. **Session start (5 min).** Wire the two hooks if the runtime has hooks (a shim that pipes the
   runtime's payload to the scripts and prints their stdout is enough - copy
   `.claude/hooks/shim.py`). No hook system? Nothing breaks: `AGENTS.md` routes a fresh agent by
   intent, and the onboarding gate's check is one `ls .uninitialised` away.
3. **Prove it (1 min).** `python3 tools/agnostic-check.py` exits 0.

A consuming workspace needs **no wiring at all** to read the store - the link-in contract
(`SHARED.md` §link-in) works with any agent that can read files.

## Adapter: Claude Code (ships wired)

- **Pointer:** `CLAUDE.md`.
- **Wiring:** `.claude/settings.json` runs `.claude/hooks/shim.py onboarding-gate` and
  `.claude/hooks/shim.py store-brief` at `SessionStart`; the shim (shared family-wide) pipes the
  payload through and passes exit codes back.
- **Skill pointer:** `.claude/skills/onboarding/SKILL.md` -> `core/onboarding/ONBOARDING.md`.

## Adapter: Gemini CLI (pointer only)

- **Pointer:** `GEMINI.md`. The runtime follows it to `AGENTS.md` and gets the routing table; wire
  hooks per the guide above if wanted.

## Related

- [Neutral core - the runtime-agnostic machinery](README.md)
