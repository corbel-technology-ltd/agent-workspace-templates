# AGENTS.md - Harbour family root

You are an agent working in the **Harbour** repository: the FAW template family, not a workspace
to operate. Read this before doing anything.

## What this repo is

Three clone-ready templates plus the machinery that keeps them in parity:

- `commonplace/` - the workspace template (constitution, memory, registers, workflows, gate).
- `lodestar/` - the shared-context template (identity, rules, calibration, boundaries).
- `chandlery/` - the capability registry (versioned, checksummed tooling + fleet drift).
- `tools/`, `instantiate.py`, `FAMILY.md`, `decisions/` - family root.

Each member is a **template**: its `AGENTS.md` is written for the *instantiated* workspace and
carries `<<TOKENS>>` that onboarding fills in. Do not follow a member's boot steps here - nothing
is onboarded at the family root.

## What you do here

| Task | Action |
|---|---|
| Take one member out to use | `python3 instantiate.py <commonplace\|lodestar\|chandlery> <dest>` - copies it into a fresh git repo; its onboarding takes over on first session there |
| Check family health | `python3 tools/family-check.py` - every member's gates + vendored-tool parity + licence parity |
| Edit a shared tool | Change it in `chandlery/registry/`, then `pack` + `install` to the members (never hand-edit a vendored copy - `family-check.py` fails on drift) |
| Edit a member's own content | Edit in that member folder; run that member's gates before sharing |
| Publish | `bash /home/jake/Templates/harbour-publish.sh` (needs a CORBEL-Technology owner `gh` login) |

## Rules

- **Never operate the family root as a live workspace** - do not run onboarding here, do not fill
  member `<<TOKENS>>` in place, do not write instance content into a template.
- **Templates ship blank and clean.** No secrets, no personal names, no instance-specific content
  in any member (the scrub gate enforces it per member; keep the root the same way).
- **Shared tools have one source of truth** - the Chandlery registry. Improvements flow
  upstream-fix → `pack` → `install`, never sideways into a vendored copy.
- **British English; stdlib-first Python; MIT.** Match the member conventions.
- Full story and composition diagram: `FAMILY.md`. Packaging/naming decisions: `decisions/`.

On any conflict between this file and a member's `AGENTS.md`, this file governs family-root
behaviour and the member's file governs that member.
