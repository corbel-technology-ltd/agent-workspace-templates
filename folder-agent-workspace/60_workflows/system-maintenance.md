---
id: <<workspace_slug>>.workflow.system-maintenance
name: System maintenance
type: workflow
layer: C2
status: current
owner: shared
staging: v1-now
created: <<CREATED_DATE>>
tags: [workflow, system-maintenance, snapshot, approve, execute, verify, closeout]
version: 0.1
stages: [scope, snapshot, approve, execute, verify, closeout]
risk: medium
---

# Workflow: System Maintenance

## Purpose

Handle local machine or homelab maintenance where changes may be R1: reversible with effort, but not casually undoable.

## When to use

- Filesystem, disk, package, service, timer, mount, or daemon maintenance.
- Any task that may modify system settings.
- Any task where a before/after snapshot would materially reduce recovery pain.

## When not to use

- Pure repo edits.
- Read-only investigation with no proposed system changes.
- R2 or R3 actions such as external publishing, payments, production database writes, or contract/signature actions. Those remain blocked or require a separate approval path.

## Stages

| Stage | Skill or action | Input | Output | Check |
|---|---|---|---|---|
| 1 | scope | user request | impact class and target list | R-level named |
| 2 | snapshot | `70_integrations/tools/system-snapshot.sh <slug> pre-change` | run snapshot | snapshot path exists |
| 3 | approve | ask <<OWNER>> for approval if system settings change | explicit approval | approval text captured |
| 4 | execute | smallest approved change | changed system state | command output reviewed |
| 5 | verify | direct live-state check | verification result | claim verified against actual system |
| 6 | closeout | final state | handover entry in `90_runs/` | next action recorded |

## Final output contract

- impact class
- snapshot path
- commands run
- verification performed
- files or system settings changed
- rollback or follow-up note

## Rules

- Never modify <<OWNER>>'s system settings without approval.
- Snapshot before R1 changes, not after.
- Do not read, print, or store credential values.
- Prefer one small working integration over mixed-in polish.

## Automation Note

This workflow is intentionally session-based. It should not become cron-driven unless repeated maintenance produces identical inputs, no novel decisions, and a named reader for the output.
