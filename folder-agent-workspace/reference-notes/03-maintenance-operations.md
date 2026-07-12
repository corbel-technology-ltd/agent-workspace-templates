---
id: <<workspace_slug>>.reference.maintenance-operations
name: Workspace reference — maintenance operations
type: reference
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [reference, maintenance]
related:
  - {ref: reference-notes/00-INDEX.md, dimension: where, polarity: part_of}
  - {ref: 60_workflows/README.md, dimension: how, polarity: enables}
---

# Workspace reference — maintenance operations

> Decomposed 2026-07-12 under the context-decomposition rule (10_doctrine/context-decomposition.md); wording unchanged.

Folder map: [00-INDEX.md](00-INDEX.md).

## Updating from the template

The safe flow is check, inspect, apply, then merge only the paths the tool flags:

```bash
python3 tools/template-update.py --check
python3 tools/template-update.py --status
python3 tools/template-update.py --apply
```

`--check` prints the upstream changelog slice and exits `10` when an update is available. `--status`
is offline. `--apply` replaces only files still matching the origin manifest, adds brand-new managed
files, and preserves a customized file beside `<path>.template-new`. Merge each candidate by hand,
then run `python3 tools/template-update.py --accept <path>`. The complete small-model-safe procedure,
including dry-run and final verification, is in
[`60_workflows/template-update.md`](../60_workflows/template-update.md).

Instance content, doctrine, canon, memory, registers, projects, runs, and integrations are outside
the managed spine and are never touched. Generic local improvements still belong upstream; shared
capability development continues to use the Capability Registry's pack/install flow.

## Backup and mirror

1. Keep the workspace's off-machine repository private; memory and canon may be sensitive.
2. Commit approved changes, add a private backup remote once, then push the `main` branch:

   ```bash
   git remote add backup <private-repository-url>
   git push -u backup main
   ```

3. Mirror every branch and tag when required: `git push --mirror <private-mirror-url>`.
4. Back up `.env` separately in a secrets manager: it is intentionally ignored by git.

## Uninstall

The workspace installs no service and owns no global database. First push or copy anything to
keep, preserve the untracked `.env` separately, and close the runtime. Then, from its parent folder:

```bash
rm -rf -- '<workspace-folder>'
```

That removes the workspace and its local `.venv`. Delete the separate template download only when
you no longer need it to create or compare workspaces.

## Related

- [Reference notes index](00-INDEX.md)
- [Workflows](../60_workflows/README.md)
