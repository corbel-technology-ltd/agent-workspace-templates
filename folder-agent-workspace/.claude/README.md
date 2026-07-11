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

`tools/agnostic-check.py` fails the build if this layer grows content beyond wiring.
