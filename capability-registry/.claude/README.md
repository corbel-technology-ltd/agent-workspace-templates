# Claude Code adapter

The wiring layer for one runtime. Translation only - no policy, no logic. Rules live in
`AGENTS.md`; the engine in `core/`. The adapter contract and the guide for wiring any other
runtime are in `core/RUNTIMES.md`.

Contents:

- `settings.json` - runs the onboarding gate at session start through the shim.
- `hooks/shim.py` - pipes hook payloads to the matching `core/hooks/` script (shared family-wide).
- `skills/onboarding/SKILL.md` - thin pointer to `core/onboarding/ONBOARDING.md`.

`tools/agnostic-check.py` fails the build if this layer grows content beyond wiring.
