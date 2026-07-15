---
id: core.runtimes
name: Runtime adapters - the contract and the 15-minute wiring guide
type: reference
layer: C0
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [runtimes, adapters, agent-agnostic, wiring, hooks, portability]
related:
  - {ref: core/README.md, dimension: why, polarity: derived_from}
  - {ref: core/hooks/README.md, dimension: what, polarity: requires}
---

# Runtime adapters

This workspace is **runtime-neutral by construction**: the constitution (`AGENTS.md`), the
doctrine, the schemas, and every executable ([`core/`](README.md)) work with any agent runtime.
A runtime is attached through a **thin adapter** - translation and wiring only, never policy.
This file is the adapter contract, the wiring guide, and the ONE sanctioned place where
runtime/vendor specifics are documented. Nothing outside the adapter layer may depend on a
specific vendor; `tools/agnostic-check.py` enforces that.

## The architecture

| Layer | Lives in | May name vendors? |
|---|---|---|
| Constitution (judgment) | `AGENTS.md` | no |
| Neutral core (all logic) | `core/`, `tools/` | no |
| Adapter (translate + wire) | one pointer file per runtime at root, plus that runtime's config dir (e.g. `.claude/`) | yes |
| This registry | `core/RUNTIMES.md` | yes |

An adapter has at most three parts:

1. **A pointer file** at the workspace root, named whatever the runtime auto-loads (`CLAUDE.md`,
   `GEMINI.md`, …). Canonical text, nothing else:

   ```markdown
   # <Runtime> adapter

   This workspace uses `AGENTS.md` as the canonical root manifest.

   Before doing anything, read `AGENTS.md` and follow its routing rules.

   If there is any conflict between this file and `AGENTS.md`, `AGENTS.md` wins.

   This file is a pinned pointer, not a document. Do not add content here;
   `tools/agnostic-check.py` fails if it grows beyond a pointer.
   ```

2. **Hook wiring**, if the runtime has lifecycle hooks: a shim that translates the runtime's
   payloads into the neutral contract below and calls `core/hooks/<name>.py`.
3. **A playbook pointer**, if the runtime has a skill/command mechanism: a thin file that says
   "follow `core/onboarding/ONBOARDING.md`" (see `.claude/skills/onboarding/SKILL.md`). Its
   presence alone does not prove support.

## The neutral hook contract

Every hook in `core/hooks/` is a standalone `python3` script:

- **Input:** one JSON object on stdin (may be `{}`).
- **Output:** stdout = context to hand to the agent; stderr = advisory/reason text.
- **Exit codes:** `0` = allow / continue; `2` = **block the operation** (the adapter maps this to
  its runtime's blocking mechanism). Any other non-zero = the hook itself failed; fail open.

| Hook | When to fire | Payload |
|---|---|---|
| `onboarding-gate.py` | session start | none |
| `session-brief.py` | session start | none |
| `journal-guard.py` | before any file edit / write / shell command | `{"op": "modify"\|"create-or-overwrite"\|"shell", "path": "<file>", "command": "<shell line>"}` |
| `session-digest.py` | session end | `{"reason": "...", "session_id": "..."}` (both optional) |
| `reaper.py` | session end (or by hand) | none (CLI flags: `--as-of`, `--dry-run`) |
| `registry-drift.py` | session end (optional) | none |

The `op` classes: `modify` = in-place edit of an existing file; `create-or-overwrite` = whole-file
write that may replace an existing file; `shell` = arbitrary command line. Map your runtime's tools
onto those three; anything unmapped is allowed (fail-open).

## Wire a new runtime in 15 minutes

1. **Pointer file (2 min).** Copy the canonical pointer text above into the file your runtime
   auto-loads, with the runtime's name in the heading. Add that filename to the `ADAPTER_POINTERS`
   list in `tools/agnostic-check.py`.
2. **Session start (5 min).** Wire `onboarding-gate.py` then `session-brief.py` to run at session
   start and inject their stdout as context. No hook system? Put "at session start, run
   `python3 core/hooks/onboarding-gate.py` and `python3 core/hooks/session-brief.py` and read their
   output before anything else" in the runtime's custom-instructions mechanism. The `AGENTS.md`
   "Session boot" section already carries the manual orientation those scripts automate, so a
   runtime that reads the pointer file still boots correctly by hand even before you wire them.
3. **The guard (5 min).** If the runtime has a pre-tool-use hook, write a shim mapping its payload
   to the `journal-guard.py` contract (copy `.claude/hooks/shim.py` - it is ~70 lines and mostly
   reusable). If it does not, install the git-level guard instead:
   `cp core/git-hooks/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit` -
   append-only then holds at commit time for ANY runtime.
4. **Session end (3 min).** Wire `session-digest.py`, `reaper.py`, `registry-drift.py` at session
   end if the runtime supports it; otherwise run them from the weekly-review workflow by hand.
5. **Prove it.** `python3 tools/agnostic-check.py` and `python3 tools/skill-surface-check.py` must
   exit 0. For every claimed skill, also prove
   that this runtime discovers it on an applicable cue, ignores its nearest non-applicable cue,
   and produces and validates the intended artefact. Re-verify after runtime changes; file
   presence or invocation alone is not support.

Reduced wiring is honest wiring: a runtime with no hooks still gets the full workspace (documents,
doctrine, onboarding, gates) plus git-level journal enforcement; it loses only the automatic
session reflexes, and this file says so.

## Adapter: Claude Code (ships wired)

- **Pointer:** `CLAUDE.md`.
- **Wiring:** `.claude/settings.json` routes every event through `.claude/hooks/shim.py <hook>`,
  which translates Claude's payload (`tool_name`, `tool_input.file_path` / `notebook_path` /
  `command`, `reason`, `session_id`) into the neutral contract and passes exit codes through
  (Claude Code treats exit 2 from a PreToolUse hook as "block", matching the contract directly).
  Tool mapping: `Edit`/`MultiEdit`/`NotebookEdit` -> `modify`; `Write` -> `create-or-overwrite`;
  `Bash` -> `shell`.
- **Playbook pointers present:** `.claude/skills/onboarding/SKILL.md` -> `core/onboarding/ONBOARDING.md`;
  `.claude/skills/template-update/SKILL.md` -> `60_workflows/template-update.md`;
  `.claude/skills/memory-sleep/SKILL.md` -> `60_workflows/memory-sleep.md`.
- **Verified hook reality** (checked against the live binary; re-verify before relying on it -
  hook surfaces drift across versions): events include `SessionStart`, `UserPromptSubmit`,
  `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `Stop`, `SubagentStop`, `SessionEnd`,
  `PreCompact`, `Notification`, `PermissionDenied`. Blocking (exit 2) works from `PreToolUse`,
  `UserPromptSubmit`, `Stop`, `SubagentStop`, `PreCompact`; `PreToolUse` may also return a
  `permissionDecision`. The rest are observational. Hook output costs no context unless injected.

## Adapter: Gemini CLI (pointer only)

- **Pointer:** `GEMINI.md`. The runtime loads it, follows it to `AGENTS.md`, and gets the manual
  session-boot protocol. No hook wiring ships; follow the guide above to add it, and install the
  git pre-commit guard for journal immutability in the meantime.

## Adapter: none (any file-reading agent)

`AGENTS.md` §"Session boot" is the manual protocol; `core/onboarding/ONBOARDING.md` is runnable by
hand; the git pre-commit guard enforces the journal invariant. The workspace degrades gracefully to
"documents plus discipline", which is exactly what a plain-files OS should do.

## Related

- [Neutral core - the runtime-agnostic machinery](README.md)
- [Reflex hooks (neutral core)](hooks/README.md)
