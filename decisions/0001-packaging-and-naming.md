---
id: family.decisions.packaging-and-naming
name: Decision 0001 - packaging and naming of the template family
type: decision
status: decided
owner: shared
created: 2026-07-02
tags: [decision, packaging, naming, mono-repo, family]
---

# Decision 0001 - packaging and naming

**Resolved 2026-07-02:** the family is named **Agent-Workspace-Templates** (the working name during the build was `faw-family`; Jake chose Agent-Workspace-Templates, in-register with the members). The reasoning below stands; read `faw-family` as the interim label for the repo now called Agent-Workspace-Templates.

**Decided 2026-07-02.** One mono-repo, three member folders plus a thin family root. Names:
family repo **`Agent-Workspace-Templates`**, members **Folder-Agent-Workspace** (workspace), **Shared-Context** (shared context),
**Capability-Registry** (capability registry - see decision 0002).

> **Amendment, 2026-07-15:** the five-tool statement below records the v0.1 decision-time stock.
> The current family vendors six shared capabilities after adding `skill-surface-check` v1.

## The packaging decision

**Chosen: one repo, three root folders, shipped together.**

```text
Agent-Workspace-Templates/
  README.md          the family front door (this folder's README)
  FAMILY.md          the whole story, told once
  LICENSE            MIT, (c) 2026 CORBEL Ltd
  instantiate.py     copy one member out into a fresh git repo (the take-just-one-part path)
  tools/family-check.py   the family gate: member gates green + vendored tools in sync
  decisions/         these notes
  folder-agent-workspace/       the workspace template          (independently extractable)
  shared-context/          the shared-context template     (independently extractable)
  capability-registry/         the capability-registry template (independently extractable)
```

### Why mono-repo

1. **One story, one version.** The three members share mechanics (`<<TOKEN>>` onboarding via
   `apply.py`, `.uninitialised` sentinel, the `tools/` gates, OKF frontmatter, the neutral-core /
   adapter split). A single repo keeps those mechanics evolving in lock-step and gives the family
   one coherent release history instead of three drifting ones.
2. **The gates still work per member.** Every member runs its own gates from its own folder
   (`git -C <member> ls-files` scopes to that folder), so nothing about the mono-repo weakens the
   per-template contracts.
3. **The family dogfoods Capability-Registry.** The five shared tools are vendored byte-identical into each
   member; `capability-registry/registry/` carries them as capabilities and `tools/family-check.py` fails if
   any vendored copy drifts. The mono-repo is what makes that loop checkable in CI.
4. **Independently extractable anyway.** `instantiate.py <member> <dest>` copies a member out and
   `git init`s it. A member folder is self-contained: own LICENSE, own gates, own README/INSTALL,
   no upward relative links that break on extraction (family references are GitHub URLs, not
   `../` paths).

### Why not the alternatives

- **Three template repos.** GitHub's "Use this template" button is nicer per-repo, but it triples
  maintenance, lets shared mechanics drift, and dilutes the family story across four READMEs. The
  cost of losing the button is one documented `instantiate.py` command.
- **Mono-repo + auto-split mirrors** (subtree-split each member into its own repo on release).
  Best of both, but it adds CI machinery the family does not need at v0.1. It remains the natural
  upgrade: `git subtree split --prefix=folder-agent-workspace` works on this layout unchanged. Deferred, not
  rejected.

## The naming decision

**Keep Folder-Agent-Workspace and Shared-Context. Name the third member Capability-Registry. Name the repo `Agent-Workspace-Templates`.**

Tested against the house naming rubric (earned elegance - a transparent, legible root; first-read
clarity; clean phonetics; distinction from the parent brand):

- **Folder-Agent-Workspace** - a folder-agent-workspace book is the centuries-old personal working notebook: everything
  worth keeping, filed by its owner, in one place. Exactly what the workspace is. Keeps.
- **Shared-Context** - the star you steer by; the fixed reference that outranks local reckoning. Exactly
  the precedence doctrine ("shared outranks local"). Keeps.
- **Capability-Registry** - the outfitter that supplies every vessel in the agent-workspace-templates with standard, proven
  gear. Exactly what the capability registry does for a fleet of workspaces: one stocked store,
  each workspace fits out from it, drift is visible against the stock. Root is legible, phonetics
  clean, register matches Shared-Context's (navigation / fitting-out) without echoing the parent brand.
  Names considered and dropped: *Patternbook* (collides with "FAW is the pattern"), *Quartermaster*
  (military register), *Outfitter* (flat), *Courier* (says transport, not stock + parity).
- **`Agent-Workspace-Templates`** (repo) - FAW (Filesystem Agent Workspace) is the canonical methodology term, so
  the repo name says exactly what the repo is: the FAW template family. An evocative repo name was
  considered and dropped: the members carry the evocative names; the container should be findable
  and self-describing. Note: the masonry/castle register (Stonework, Plinth, Portcullis, Keep) is
  deliberately avoided - those names are recorded as killed.

All names remain subject to the standing naming gate; the repo name is the cheapest to
change and the member names are used consistently so a rename is a mechanical sweep.

## What to create on GitHub

One public GitHub repo: **`CORBEL-Technology/Agent-Workspace-Templates`**.

Assembly from the local build:

```bash
mkdir Agent-Workspace-Templates && cd Agent-Workspace-Templates && git init
cp -r ~/Templates/Family-Root/. .                          # root files (this folder)
cp -r ~/Templates/Folder-Agent-Workspace-Template       folder-agent-workspace     # then remove folder-agent-workspace/.git
cp -r ~/Templates/Shared-Context-Template  shared-context        # then remove shared-context/.git
cp -r ~/Templates/Capability-Registry-Template       capability-registry       # then remove capability-registry/.git
rm -rf folder-agent-workspace/.git shared-context/.git capability-registry/.git
python3 tools/family-check.py                              # must exit 0
git add -A && git commit -m "Agent-Workspace-Templates v0.1"
```

The existing placeholder repos `CORBEL-Technology/Folder-Agent-Workspace` and `CORBEL-Technology/Shared-Context`:
either archive them with a pointer README to `Agent-Workspace-Templates`, or keep the names reserved for future
subtree-split mirrors. Recommendation: archive with a pointer now; split mirrors only if template
consumers ask for per-repo "Use this template".
