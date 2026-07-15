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

This registry is **runtime-neutral by construction**; a runtime attaches through a thin adapter -
translation and wiring only, never policy. This file is the adapter contract and the ONE
sanctioned place for runtime/vendor specifics (`tools/agnostic-check.py` enforces that).

A registry needs almost no wiring - the engine is a CLI run at the operator's gate. The whole
contract:

| Integration point | Wire |
|---|---|
| Pointer file at root | the file your runtime auto-loads, pointing at `AGENTS.md` (canonical text below) |
| Session start | `core/hooks/onboarding-gate.py`; inject stdout as context (only speaks while the sentinel exists) |

Canonical pointer text (all adapters carry exactly this, with their runtime's name in the heading):

```markdown
# <Runtime> adapter

This registry uses `AGENTS.md` as the canonical root manifest.

Before doing anything, read `AGENTS.md` and follow its routing rules.

If there is any conflict between this file and `AGENTS.md`, `AGENTS.md` wins.

This file is a pinned pointer, not a document. Do not add content here;
`tools/agnostic-check.py` fails if it grows beyond a pointer.
```

## Wire a new runtime (5 minutes)

1. **Pointer file.** Copy the canonical text into the file your runtime auto-loads; add the
   filename to `ADAPTER_POINTERS` in `tools/agnostic-check.py`.
2. **Session start** (optional). Wire the onboarding gate if the runtime has hooks; without it,
   `AGENTS.md` still routes a fresh agent to onboarding by intent.
3. **Prove it.** `python3 tools/agnostic-check.py` and `python3 tools/skill-surface-check.py` exit 0.

## Adapter: Claude Code (ships wired)

- **Pointer:** `CLAUDE.md`.
- **Wiring:** `.claude/settings.json` runs `.claude/hooks/shim.py onboarding-gate` at
  `SessionStart` (the shim is shared family-wide).
- **Skill pointer:** `.claude/skills/onboarding/SKILL.md` -> `core/onboarding/ONBOARDING.md`.

## Adapter: Gemini CLI (pointer only)

- **Pointer:** `GEMINI.md`; wire the gate per the guide above if wanted.

## Related

- [Neutral core - the runtime-agnostic machinery](README.md)
