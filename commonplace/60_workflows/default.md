---
id: <<workspace_slug>>.workflow.default
name: Default workflow
type: workflow
layer: C2
status: current
owner: shared
staging: v1-now
created: <<CREATED_DATE>>
tags: [workflow, default, routing, discover, execute, verify, closeout]
version: 0.1
stages: [discover, route, load, execute, verify, closeout]
risk: low
---

# Workflow: Default

## Purpose

Handle ordinary workspace tasks when no specialised workflow applies.

## When to use

- No more specific workflow exists for the task
- One-off work that does not justify creating a new workflow yet

## When not to use

- A specialised workflow exists for the task type
- The work is large enough to warrant designing its own workflow first

## Stages

| Stage | Action | Output | Check |
|---|---|---|---|
| 1 | **Discover** — read `AGENTS.md` | Task routing understood | Manifest read |
| 2 | **Route** — read `00_meta/staging.md` (`Now / In flight`) and the handover named in its `Latest handover` pointer | Current state understood | Active focus identified |
| 3 | **Load** — load only relevant context | Minimal context loaded | Context budget under 50% |
| 4 | **Execute** — create or update artefact under `90_runs/YYYY-MM-DD-<slug>.md` (or a folder for multi-file runs) | Work is durable | Artefact exists, has frontmatter |
| 5 | **Verify** — check against constraints in `15_canon/` (and `10_doctrine/` for hard rules) | Obvious drift caught | Constraints respected |
| 6 | **Closeout** — write a handover under `90_runs/` and update `00_meta/staging.md` if meaningful | Future session can resume | Closeout written |

## Output contract

A completed run of this workflow produces:

- A new run note (or folder) under `90_runs/YYYY-MM-DD-<slug>.md`
- The artefact(s) the task required
- A handover under `90_runs/` (the closeout)
- An updated `00_meta/staging.md` (`Now / In flight`, and its `Latest handover` pointer)

## Workflow expansion rule

Do not create a new workflow file unless the same task pattern has repeated several times. If you find yourself extending this default workflow inline, that is the signal to propose a new workflow — log it to `50_registers/improvement-backlog.md` rather than spawning a speculative workflow file.

## Reasoning

The default workflow exists so the workspace always has a fallback. The shape (discover → route → load → execute → verify → closeout) is the irreducible six-stage skeleton of any reviewable work. Specialised workflows expand individual stages; they do not skip any.
