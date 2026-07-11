---
id: <<workspace_slug>>.workflow.template-update
name: Safe template update - check, inspect, apply, merge, accept
type: workflow
layer: C2
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [template, update, maintenance, pacnew, non-clobbering]
related:
  - {ref: REFERENCE.md, dimension: where, polarity: explains}
  - {ref: AGENTS.md, dimension: why, polarity: requires}
---

# Safe template update

Use this playbook when the session brief says a template check is due or an update is available.
The tool may be called by cron, but this workspace never creates or enables a schedule itself.
Scheduling is a separate operator decision under doctrine.

## Run the update

1. From the workspace root, run `python3 tools/template-update.py --check`. Exit `0` means current;
   exit `10` means an update is available and is not an error. Read the printed changelog slice.
2. Run `python3 tools/template-update.py --status`. Review every `customized`, `missing`, and
   `new-upstream` path before continuing.
3. Preview with `python3 tools/template-update.py --apply --dry-run`, then run
   `python3 tools/template-update.py --apply`. Pristine files are updated, new managed files are
   added, and customized files remain byte-for-byte unchanged beside a token-filled
   `<path>.template-new` candidate. Nothing outside the managed spine is touched.
4. For each item under `Merge required`, compare the local file with its `.template-new`, merge the
   wanted upstream change into the local file, validate it, then run
   `python3 tools/template-update.py --accept <path>`. Accepting records the merged hash and removes
   that path's `.template-new` file.
5. Run `python3 tools/template-update.py --status` again. Do not call the update complete while a
   path remains `customized`, `missing`, or `new-upstream` unless the operator explicitly accepts
   that state.

If check fails, stop without applying. If apply fails part-way, inspect status and rerun only after
the cause is understood; the tool never deletes a managed or instance-content file.

## Related

- [Workspace user reference](../REFERENCE.md)
- [<<WORKSPACE_NAME>>](../AGENTS.md)
