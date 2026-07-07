# Harbour

The **Filesystem Agent Workspace** template family: three clone-ready, agent-agnostic templates
for running your work as plain Markdown + git that an AI agent operates and you stay in front of.

- [`commonplace/`](commonplace/README.md) - the **workspace**: a folder-based agent control plane
  (constitution, memory, registers, workflows, safety gate).
- [`lodestar/`](lodestar/README.md) - the **shared context**: one governed store above every
  workspace for identity, rules, calibration, and boundaries; shared outranks local.
- [`chandlery/`](chandlery/README.md) - the **capability registry**: versioned, checksummed
  tooling that installs into workspaces, flows improvements back, and makes drift visible.

Each stands alone; together they click. The whole story, the composition diagram, and the
take-just-one-part paths: **[FAMILY.md](FAMILY.md)**. Agents start at
**[AGENTS.md](AGENTS.md)** — the family-root constitution.

## Quick start

```bash
python3 instantiate.py commonplace ~/my-workspace   # copy a member out into a fresh git repo
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
