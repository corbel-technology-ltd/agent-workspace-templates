# Shared-Context

**The shared brain above your agent workspaces.** One plain-files store that holds who the
principal is, how their agents behave, and what environment they operate in - agent-neutral,
governed, and outranking anything local. Every workspace plugs in and inherits the whole brain;
every correction lands once and reaches all of them.

Shared-Context is the shared-context member of the **FAW template family** (Filesystem Agent Workspace):
Markdown + git, deterministic-first, no app, no database, no vendor. Its sibling **Folder-Agent-Workspace** is
the workspace an agent runs; Shared-Context is the star all of those workspaces steer by.

## Why

- **One principal, many workspaces, zero drift.** Without a shared store, every workspace keeps
  its own copy of who you are - and the copies diverge. Here identity, rules, people, tech, and
  calibration live once, and the precedence doctrine ("shared outranks local") makes the single
  copy authoritative.
- **The link-in contract.** Registering a workspace is one command: it lands on the roster, gets
  the boot rule to paste, and from then on loads the shared brain at every session start. Adding
  your fifth workspace costs the same as your second.
- **Multi-agent governance, first-class.** Every edit gets an append-only ledger entry and an
  objection window; adding or removing a file needs every registered agent's sign-off; the
  principal holds override. Agents co-own the brain without being able to quietly rewrite it.
- **The confidentiality line is a file.** `boundaries/` states what may never leave your machines,
  and the scrub gates in every family template can derive their denylist from it mechanically.

## Use it

1. Click **Use this template**, then **Create a new repository** (your own copy).
2. Clone it. Run `pip install -r requirements.txt` (one dependency: PyYAML).
3. Open the folder in your agent runtime (adapters ship pinned; `core/RUNTIMES.md` covers wiring).
4. On the first session the store is uninitialised, so the agent runs the **onboarding** playbook:
   a handful of questions (store name, principal name, objection-window hours, file cap), filled
   deterministically. The store ships **blank** - every fact about a real person was scrubbed out;
   your facts arrive through calibration, never invention.
5. Register your first workspace:
   `python3 core/link-workspace.py --name Acme --path /home/you/acme-workspace --agent aster`.

Before sharing your copy onward, four gates prove it is clean, portable, and in shape:

```bash
python3 tools/scrub-check.py      # no private terms leak (boundaries/ feeds the list)
python3 tools/okf-check.py        # OKF-compatible frontmatter + linked knowledge graph
python3 tools/agnostic-check.py   # neutral core stays vendor-free, adapters stay pointers
python3 tools/shared-lint.py      # structure lock, file cap, frontmatter, ledger format
```

## What is inside

```text
SHARED.md          the constitution: precedence, scope, the link-in contract, governance
AGENTS.md          the store manifest agents read when working inside this repo
identity/          the principal's canonical profile, voice, availability (blank skeletons)
operating-rules/   cross-workspace rules - how agents behave, not what they know
people/            shared people (only those 2+ workspaces deal with)
places/            shared locations and venues (aliased where sensitive)
concepts/          shared ideas with depth; the glossary points here
automations/       the shared standing machinery (jobs, watchers, crons - catalogued before trodden on)
tech-stack/        the shared machine/software estate
calibration-os/    living scoped preferences + the corrections pipeline (blank by design)
boundaries/        the confidentiality line; scrub lists derive from it
glossary/          the shared vocabulary, including names ruled OUT
_coordination/     live dashboard of open handoffs + the workspace roster
CHANGES.md         the append-only ledger every edit lands in
_meta/             the governance protocol + this store's design spec
core/              neutral machinery: onboarding engine, store hooks, link-in + scrub-derive tools
tools/             the four gates
```

Plus one thin adapter per wired runtime (a pinned pointer file at the root and that runtime's
config dir - wiring only; `core/RUNTIMES.md` is the registry). Every folder has a README. Start at
[`SHARED.md`](SHARED.md).

## How it thinks

- **Shared outranks local** - on shared-scope conflicts, this store wins; corrections flow back
  through governance instead of forking in one workspace.
- **Rules, not knowledge** - `operating-rules/` governs how agents operate; what they know lives
  in their workspaces.
- **Blank by design** - skeletons earn content through calibration sessions and confirmed
  corrections. Nothing here is invented; source-or-abstain applies to the principal above all.
- **Scope test + file cap** - two consumers must need a file, and growth past the cap is a
  decision, not a drift.

## The family

Shared-Context is the **shared-context** member of the FAW template family - three templates that stand
alone and click together (the whole story lives in `FAMILY.md` at the family repo root,
`github.com/corbel-technology-ltd/agent-workspace-templates`):

- **Folder-Agent-Workspace** - the workspace an agent runs; its onboarding asks for this store's path and its
  session brief loads the shared brain first.
- **Shared-Context** (this one) - the store above every workspace.
- **Capability-Registry** - the capability registry a fleet fits out from; point its `fleet.yml` at this
  store and the fleet report cross-checks the roster.

**Taking just this part is fine.** The link-in contract speaks plain files: any workspace layout
that can read a folder can consume this store, not just Folder-Agent-Workspace.

## Licence

MIT, © 2026 CORBEL Ltd. See [LICENSE](LICENSE).
