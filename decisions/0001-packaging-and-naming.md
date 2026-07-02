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

**Resolved 2026-07-02:** the family is named **Harbour** (the working name during the build was `faw-family`; Jake chose Harbour, in-register with the members). The reasoning below stands; read `faw-family` as the interim label for the repo now called Harbour.

**Decided 2026-07-02.** One mono-repo, three member folders plus a thin family root. Names:
family repo **`Harbour`**, members **Commonplace** (workspace), **Lodestar** (shared context),
**Chandlery** (capability registry - see decision 0002).

## The packaging decision

**Chosen: one repo, three root folders, shipped together.**

```text
Harbour/
  README.md          the family front door (this folder's README)
  FAMILY.md          the whole story, told once
  LICENSE            MIT, (c) 2026 CORBEL Ltd
  instantiate.py     copy one member out into a fresh git repo (the take-just-one-part path)
  tools/family-check.py   the family gate: member gates green + vendored tools in sync
  decisions/         these notes
  commonplace/       the workspace template          (independently extractable)
  lodestar/          the shared-context template     (independently extractable)
  chandlery/         the capability-registry template (independently extractable)
```

### Why mono-repo

1. **One story, one version.** The three members share mechanics (`<<TOKEN>>` onboarding via
   `apply.py`, `.uninitialised` sentinel, the `tools/` gates, OKF frontmatter, the neutral-core /
   adapter split). A single repo keeps those mechanics evolving in lock-step and gives the family
   one coherent release history instead of three drifting ones.
2. **The gates still work per member.** Every member runs its own gates from its own folder
   (`git -C <member> ls-files` scopes to that folder), so nothing about the mono-repo weakens the
   per-template contracts.
3. **The family dogfoods Chandlery.** The five shared tools are vendored byte-identical into each
   member; `chandlery/registry/` carries them as capabilities and `tools/family-check.py` fails if
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
  upgrade: `git subtree split --prefix=commonplace` works on this layout unchanged. Deferred, not
  rejected.

## The naming decision

**Keep Commonplace and Lodestar. Name the third member Chandlery. Name the repo `Harbour`.**

Tested against the house naming rubric (earned elegance - a transparent, legible root; first-read
clarity; clean phonetics; distinction from the parent brand):

- **Commonplace** - a commonplace book is the centuries-old personal working notebook: everything
  worth keeping, filed by its owner, in one place. Exactly what the workspace is. Keeps.
- **Lodestar** - the star you steer by; the fixed reference that outranks local reckoning. Exactly
  the precedence doctrine ("shared outranks local"). Keeps.
- **Chandlery** - the outfitter that supplies every vessel in the harbour with standard, proven
  gear. Exactly what the capability registry does for a fleet of workspaces: one stocked store,
  each workspace fits out from it, drift is visible against the stock. Root is legible, phonetics
  clean, register matches Lodestar's (navigation / fitting-out) without echoing the parent brand.
  Names considered and dropped: *Patternbook* (collides with "FAW is the pattern"), *Quartermaster*
  (military register), *Outfitter* (flat), *Courier* (says transport, not stock + parity).
- **`Harbour`** (repo) - FAW (Filesystem Agent Workspace) is the canonical methodology term, so
  the repo name says exactly what the repo is: the FAW template family. An evocative repo name was
  considered and dropped: the members carry the evocative names; the container should be findable
  and self-describing. Note: the masonry/castle register (Stonework, Plinth, Portcullis, Keep) is
  deliberately avoided - those names are recorded as killed.

All names remain subject to the standing naming gate; the repo name is the cheapest to
change and the member names are used consistently so a rename is a mechanical sweep.

## What to create on GitHub

One public GitHub repo: **`CORBEL-Technology/Harbour`**.

Assembly from the local build:

```bash
mkdir Harbour && cd Harbour && git init
cp -r ~/Templates/Family-Root/. .                          # root files (this folder)
cp -r ~/Templates/Workspace-Template       commonplace     # then remove commonplace/.git
cp -r ~/Templates/Shared-Context-Template  lodestar        # then remove lodestar/.git
cp -r ~/Templates/Chandlery-Template       chandlery       # then remove chandlery/.git
rm -rf commonplace/.git lodestar/.git chandlery/.git
python3 tools/family-check.py                              # must exit 0
git add -A && git commit -m "Harbour v0.1"
```

The existing placeholder repos `CORBEL-Technology/Commonplace` and `CORBEL-Technology/Lodestar`:
either archive them with a pointer README to `Harbour`, or keep the names reserved for future
subtree-split mirrors. Recommendation: archive with a pointer now; split mirrors only if template
consumers ask for per-repo "Use this template".
