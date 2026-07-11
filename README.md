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
  by a self-test that runs as a family gate. It is not another recall database: it is the layer
  where an agent develops taste and learns how you like to work - curated, source-linked beliefs
  with governance - and it composes happily with any retrieval system underneath.
- [`shared-context/`](shared-context/README.md) - the **shared context**: one governed store above every
  workspace for identity, rules, calibration, and boundaries; shared outranks local.
- [`capability-registry/`](capability-registry/README.md) - the **capability registry**: versioned, checksummed
  tooling that installs into workspaces, flows improvements back, and makes drift visible.

Each stands alone; together they click. The whole story, the composition diagram, and the
take-just-one-part paths: **[FAMILY.md](FAMILY.md)**. Agents start at
**[AGENTS.md](AGENTS.md)** - the family-root constitution.

## Install

**Linux / Mac** — one command; checks git + Python 3.8+ (telling you exactly what to install if
missing), fetches everything, installs the one dependency, creates your workspace:

```bash
curl -fsSL https://raw.githubusercontent.com/CORBEL-Technology/agent-workspace-templates/main/install.sh | sh
```

**Windows** — one extra command, once. In PowerShell (run as administrator): `wsl --install`,
restart, then paste the Linux/Mac command into the Ubuntu window that appears. That window is
your terminal from now on. (Native Windows without WSL is not supported — the workspace would
create but its guard hooks would not fire.)

**Never used a terminal?** [START-HERE.md](START-HERE.md) spells out every step, nothing
assumed, ~15 minutes.

### Choosing what to install

The default command above creates a **workspace** — the thing most people want, and the thing
you may eventually have several of. Copy the exact line for what you need:

**A workspace** (at `~/my-workspace`):

```bash
curl -fsSL https://raw.githubusercontent.com/CORBEL-Technology/agent-workspace-templates/main/install.sh | sh
```

**Another workspace** (each additional one just needs its own name):

```bash
curl -fsSL https://raw.githubusercontent.com/CORBEL-Technology/agent-workspace-templates/main/install.sh | sh -s -- ~/second-workspace
```

**The shared brain** that sits above several workspaces (at `~/my-shared`):

```bash
curl -fsSL https://raw.githubusercontent.com/CORBEL-Technology/agent-workspace-templates/main/install.sh | sh -s -- shared-context
```

**The versioned tooling registry** (at `~/my-registry`):

```bash
curl -fsSL https://raw.githubusercontent.com/CORBEL-Technology/agent-workspace-templates/main/install.sh | sh -s -- capability-registry
```

Each stands alone; together they click ([FAMILY.md](FAMILY.md)). Typical growth path: one
workspace → a second workspace + the shared store → the registry once tooling is worth
versioning.

<details>
<summary>Manual install (no curl-pipe)</summary>

```bash
git clone https://github.com/CORBEL-Technology/agent-workspace-templates.git && cd agent-workspace-templates
python3 -m pip install --user "PyYAML>=6,<7"
python3 instantiate.py folder-agent-workspace ~/my-workspace   # or shared-context / capability-registry
cd ~/my-workspace   # open it in your agent runtime; onboarding runs on first session
```

</details>

## Health

```bash
python3 tools/family-check.py   # every member's gates green + vendored tools in sync
```

## Licence

MIT, © 2026 CORBEL Ltd. See [LICENSE](LICENSE).
