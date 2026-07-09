---
id: <<workspace_slug>>.meta.log
name: Workspace change log
type: log
layer: C1
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [log, changelog]
---

# Workspace change log

Append-only history of structural changes to this workspace: doctrine edits, schema/workflow
additions, hook installs, migrations. One dated section per change set, newest at the top. Generic
OS improvements should also flow upstream to the Folder-Agent-Workspace-Template (see the upstreaming rule in the
template `README.md`).

## <<CREATED_DATE>> - Instantiated from the Folder-Agent-Workspace-Template

- Created this workspace from the canonical blank template. Filled the identity placeholders and
  set the shared-context path (blank if no store is wired). Wiring the instance's live systems
  (`70_integrations/`) is a later, per-instance step.
- Six now-tier reflexes present in `core/hooks/` (`journal-guard`, `onboarding-gate`,
  `session-brief`, `session-digest`, `reaper`, `registry-drift`), wired per runtime by a thin
  adapter. Memory model, doctrine, schemas, templates, and workflow specs carried from the
  template. Canon, registers, and memory start blank.
