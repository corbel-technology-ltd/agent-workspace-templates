# Claude Code adapter

The wiring layer for one runtime. Translation only - no policy, no playbooks, no logic. Policy
lives in `AGENTS.md`; logic lives in `core/`. The adapter contract and the guide for wiring any
other runtime are in `core/RUNTIMES.md`.

Contents:

- `settings.json` - routes Claude Code's hook events through the shim.
- `hooks/shim.py` - translates Claude Code payloads into the neutral hook contract and calls the
  matching `core/hooks/` script.
- `skills/onboarding/SKILL.md` - thin pointer to the neutral onboarding playbook
  (`core/onboarding/ONBOARDING.md`).
- `skills/template-update/SKILL.md` - thin pointer to the neutral safe-update playbook
  (`60_workflows/template-update.md`).
- `skills/memory-sleep/SKILL.md` - thin pointer to the neutral bounded memory-synthesis playbook
  (`60_workflows/memory-sleep.md`).

Skill pointers follow the neutral [promotion contract](../60_workflows/README.md#skill-promotion-contract);
runtime support requires the discovery-and-effect proof in `core/RUNTIMES.md`.

`tools/agnostic-check.py` keeps this layer runtime-only; `tools/skill-surface-check.py` keeps its
skills as valid neutral pointers.
