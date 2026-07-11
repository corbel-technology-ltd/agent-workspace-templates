# Reflex hooks (neutral core)

The reflexes that enforce the constitution at the tool-call and session boundaries, so the
load-bearing invariants do not depend on the agent remembering them. The logic lives HERE,
runtime-neutral; each runtime wires it through a thin adapter (the wired adapters, and the guide
for wiring any other, are in [`../RUNTIMES.md`](../RUNTIMES.md)). Discipline (per `AGENTS.md`):
silent by default, narrow matchers, no write-only logs, notify only when a human is needed.

> Installing or changing hook wiring edits runtime settings, so it is an operator-approved change.

## The hooks

| Hook | Fires at | What it does | Can block? |
|---|---|---|---|
| `journal-guard.py` | before a file/shell operation | Blocks any operation that would edit, overwrite, delete, or move an EXISTING `20_memory/journal/` entry. Creating a NEW entry is allowed (append-only). The reflex behind the immutability invariant. | **yes** (exit 2) |
| `onboarding-gate.py` | session start | If the `.uninitialised` sentinel is present, instructs the agent to run the onboarding playbook (`core/onboarding/ONBOARDING.md`) before ANY other work. Silent once onboarded. | no |
| `session-brief.py` | session start | Injects boot orientation plus open decision-queue items + open loops, only if any exist. Situational awareness at near-zero cost. | no |
| `session-digest.py` | session end | Appends one terse L1 journal event (reason, last commit, working tree) so the session is captured as truth for the reaper. Silent. | no |
| `reaper.py` | session end | The deterministic fast memory pass (membership, decay, supersession, quarantine, tiering, build marker). Spec: `60_workflows/memory-reaper.md`. Hook-safe (a failure never disrupts session end). | no |
| `registry-drift.py` | session end (optional) | Advisory drift sensor: flags any ops component not catalogued in `50_registers/component-registry.md`. Silent when clean. | no |

## The neutral contract

Every hook is a standalone `python3` script: JSON payload on stdin (documented per hook in its
docstring and in [`../RUNTIMES.md`](../RUNTIMES.md)), context for the agent on stdout, advisories
on stderr. Exit `0` allows/continues; exit `2` means **block this operation** - the adapter maps
that to its runtime's blocking mechanism. Nothing in this folder knows which runtime called it.

## Hook runtime

The adapter invokes `python3` from its environment. Most hooks are standard-library only;
`reaper.py`, `sleep-prep.py`, and `sleep-apply.py` import **PyYAML**. The family installer provides
it and, when PEP 668 protects system Python, creates a root `.venv`; activate that environment
before starting the runtime. For a direct template clone, run `python3 -m venv .venv`, then
`. .venv/bin/activate`, then `python -m pip install -r requirements.txt`. If PyYAML is absent,
memory consolidation stops but the other hooks remain available.

## Workspace root resolution

Each hook resolves the workspace root from the `<<WORKSPACE_ROOT_ENV>>` environment variable if set,
else two levels up from the hook file (the repo root). Set the env var only if the hooks are invoked
from outside the repo.

## Placeholders to fill at instantiation

These files carry placeholders alongside the rest of the template:

- `<<WORKSPACE_ROOT_ENV>>` - the env-var name for the root override (e.g. `ACME_ROOT`; every hook).
- `<<WORKSPACE_NAME>>` / `<<AGENT_NAME>>` / `<<OWNER>>` - the brief label and boot line printed by
  `session-brief.py`.
- `<<SHARED_CONTEXT_PATH>>` - the shared-store path in the `session-brief.py` boot line (blank = no
  store, and the line is omitted).
- `<<workspace_slug>>` - the build-marker id namespace (`reaper.py`) and the journal `where:` field
  (`session-digest.py`).
- `<<agent_slug>>` - the lowercase agent handle written to the journal `who:` field
  (`session-digest.py`).

## Tests

The onboarding engine is fully tested (`core/onboarding/tests/test_apply.py`). The hooks are
deliberately small and readable; exercise them by hand with a synthetic payload, e.g.:

```bash
echo '{"op": "modify", "path": "20_memory/journal/x.md"}' | python3 core/hooks/journal-guard.py
echo "exit: $?"   # 2 = blocked, as it should be
```

Add instance-side tests once your instance has real atoms/components to test against.
