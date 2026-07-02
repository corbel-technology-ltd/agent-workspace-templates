# Commonplace

**A folder-based agent workspace.** Plain Markdown and git, that an AI agent operates as the
control plane for your business, and that you stay in front of.

Commonplace is CORBEL's flavour of a **Filesystem Agent Workspace (FAW)**: an open, file-based pattern
for an agent-run control plane. It is in the spirit of the
[Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf),
but extends it from *formatting knowledge* to *running a whole workspace*. FAW is the pattern;
Commonplace is the reference implementation you clone.

Not an autonomous AI CEO. Commonplace handles what does not need you and prepares what does, then
stops at a gate and hands you the decision. Preparation is automated; authority stays yours.

## Why

- **Plain files, no lock-in.** Markdown and YAML in a git repo. No app, no database, no service to
  depend on. Read every byte, diff every change, fork it, take it anywhere.
- **Deterministic first.** Ordinary code does the plumbing; the model enters only to summarise,
  draft, classify, or judge, never to decide or send. AI as a reasoning layer, not an authority layer.
- **It remembers.** An append-only journal is the truth; a reaper folds it into a memory that decays
  and surfaces what matters. Registers hold live state; canon holds what is settled.
- **Portable knowledge.** Frontmatter is OKF-compatible (the Open Knowledge Format), so the graph of
  what-relates-to-what travels with the files, not with a vendor.

**Agent-agnostic by construction.** The constitution (`AGENTS.md`), doctrine, schemas, registers,
and every executable (`core/`) are runtime-neutral; each runtime attaches through a thin pinned
adapter. Two adapters ship (one fully hook-wired, one a pointer); [`core/RUNTIMES.md`](core/RUNTIMES.md)
wires another in about 15 minutes, and a gate (`tools/agnostic-check.py`) proves no behaviour
depends on a specific vendor.

## Use it

Commonplace is a GitHub **template repository**:

1. Click **Use this template**, then **Create a new repository** (your own copy).
2. Clone it. Run `pip install -r requirements.txt` (one dependency: PyYAML).
3. Open the folder in your agent runtime (two adapters ship wired; see
   [`core/RUNTIMES.md`](core/RUNTIMES.md) for the list and for wiring any other).
4. On the first session the workspace is uninitialised, so the agent runs the **onboarding**
   playbook: it asks a handful of questions (your workspace name, your agent's name, and so on) and
   fills the template deterministically. No find-and-replace by hand.
5. You are live. Talk to your agent.

Before you ever share your own copy onward, two gates prove it is clean and portable:

```bash
python3 tools/scrub-check.py      # no in-house terms leak (you configure the list)
python3 tools/okf-check.py        # OKF-compatible frontmatter + linked knowledge graph
python3 tools/agnostic-check.py   # neutral core stays vendor-free, adapters stay pointers
```

## What is inside

```text
AGENTS.md         the constitution: identity, routing, doctrine, the gate
00_meta/          how the workspace describes and governs itself
10_doctrine/      the agent's standing judgment (read, not run)
15_canon/         durable reference: your direction, brand, offerings
20_memory/        journal (append-only truth) + the folded, decaying memory
30_schemas/       the shape contract for every artefact
40_templates/     fill-in scaffolds: daily brief, decision packet, ...
50_registers/     live ledgers: decisions, loops, risks, records
60_workflows/     the run-by-hand playbooks
70_integrations/  slots for your email, CRM, and feeds (you wire these)
80_projects/      per-project trackers and their open loops
90_runs/          working artefacts
core/             the neutral machinery: reflex hooks, onboarding engine, runtime guide
tools/            the pre-distribution gates
```

Plus one thin adapter per wired runtime (a pinned pointer file at the root and that runtime's
config dir - wiring only, never content; `core/RUNTIMES.md` is the registry). Every numbered folder
has a README explaining it. Start at [`AGENTS.md`](AGENTS.md).

## Onboarding tokens

Onboarding fills nine placeholders deterministically. On disk each appears as `<<TOKEN>>` (angle
brackets); the table below names them without the brackets on purpose, so this reference survives
onboarding intact (`core/onboarding/placeholders.yml` is the single source of truth):

| Token | Meaning | Source |
|---|---|---|
| `WORKSPACE_NAME` | Workspace / instance name | asked |
| `ENTITY` | Legal / operating entity it serves | asked |
| `OWNER` | Founder / operator name | asked |
| `AGENT_NAME` | Agent persona name | asked |
| `workspace_slug` | Lowercase id handle | derived |
| `agent_slug` | Lowercase agent handle | derived |
| `WORKSPACE_ROOT_ENV` | Env-var name for the root override | asked |
| `SHARED_CONTEXT_PATH` | Absolute path to the shared-context store (may be blank) | asked |
| `CREATED_DATE` | Instantiation date | auto |

Runtime `{{...}}` markers (like `{{YYYY-MM-DD}}` in the templates) are a different syntax on
purpose: they are filled per artefact as you work, never by onboarding.

## How it thinks

- **Source-or-abstain.** No factual claim without a source. "I don't know" beats a confident guess.
- **Autonomy by reversibility.** The more reversible an action, the more the agent simply does it; the
  less reversible, the more it stops for you.
- **Capture-back.** Durable learning is written back to memory. Nothing evaporates.
- **One concept per file**, linked into a graph you can walk.

## The family

Commonplace is the **workspace** member of the FAW template family - three templates that stand
alone and click together (the whole story lives in `FAMILY.md` at the family repo root,
`github.com/CORBEL-Technology/Harbour`):

- **Commonplace** (this one) - the workspace an agent runs.
- **Lodestar** - the shared-context store above every workspace: the principal's identity, rules,
  and calibration, governed and outranking anything local. Wire one by filling
  `SHARED_CONTEXT_PATH` at onboarding; its link-in contract does the rest.
- **Chandlery** - the capability registry a fleet fits out from: this template's gate scripts and
  onboarding engine are stocked there, so improvements flow between siblings instead of drifting.

**Taking just this part is fine.** Commonplace assumes neither sibling: leave
`SHARED_CONTEXT_PATH` blank and wire a store later without re-onboarding; port tooling by hand
until a registry earns its place.

## Licence

MIT, © 2026 CORBEL Ltd. See [LICENSE](LICENSE). Contributions are welcome, see
[CONTRIBUTING.md](CONTRIBUTING.md).
