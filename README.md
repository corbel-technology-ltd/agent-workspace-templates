# Agent-Workspace-Templates

> **Never used a terminal?** Follow **[START-HERE.md](START-HERE.md)**: every step spelled out,
> nothing assumed, about 15 minutes.
>
> **Comfortable with git and Python?** The quick start below is for you.

The **Filesystem Agent Workspace** template family: three clone-ready, agent-agnostic templates
for running your work as plain Markdown + git that an AI agent operates and you stay in front of.

- [`folder-agent-workspace/`](folder-agent-workspace/README.md) - the **workspace**: a folder-based agent control plane
  (constitution, memory, registers, workflows, safety gate). Its four-layer memory - journal ->
  sleep synthesis -> activation-based tiering with hysteresis - is fully implemented and proven
  by a self-test that runs as a family gate.
- [`shared-context/`](shared-context/README.md) - the **shared context**: one governed store above every
  workspace for identity, rules, calibration, and boundaries; shared outranks local.
- [`capability-registry/`](capability-registry/README.md) - the **capability registry**: versioned, checksummed
  tooling that installs into workspaces, flows improvements back, and makes drift visible.

Each stands alone; together they click. The whole story, the composition diagram, and the
take-just-one-part paths: **[FAMILY.md](FAMILY.md)**. Agents start at
**[AGENTS.md](AGENTS.md)** - the family-root constitution.

## Quick start

```bash
python3 instantiate.py folder-agent-workspace ~/my-workspace   # copy a member out into a fresh git repo
cd ~/my-workspace                                   # open it in your agent runtime;
                                                    # onboarding runs on first session
```

Or take the whole family as-is and instantiate members as you need them.

## Health

```bash
python3 tools/family-check.py   # every member's gates green + vendored tools in sync
```

## Licence

MIT, © 2026 CORBEL Ltd. See [LICENSE](LICENSE).
