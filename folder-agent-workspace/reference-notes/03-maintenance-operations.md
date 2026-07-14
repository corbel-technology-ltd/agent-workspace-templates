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

Updater state uses two independent hashes. `managed_manifest[path]` is the last reviewed upstream
candidate; `accepted_local_manifest[path]` exists only when the reviewed local result differs.
`accepted-customized` is reviewed and protected; `customized` is unreviewed. Accepting with a
candidate advances the upstream base to the candidate hash and records the local result separately;
accepting without a candidate leaves the existing upstream base intact. Local-only paths stay
outside updater state until upstream introduces the same path. Apply emits `.template-new` only for
a real upstream delta or a manifest-backed missing file; an unchanged symlink or other present
non-regular node stays untouched and produces no candidate. Both manifests require canonical
relative POSIX managed paths, and accepted-local keys must be a subset of the managed map. Legacy
one-hash stamps migrate automatically from the recorded commit's registry and hash-allowlisted fill engine.
The commit must be fetchable from origin or restored to the mirror cache. Missing fill values block
writes, as does an unsupported recorded or target engine; both keep status conservative with recovery
or upgrade guidance. Acceptance verifies sidecar bytes against the same recorded upstream provenance
before updating the stamp or removing the sidecar.

A pending manifest-backed candidate makes a legacy stamp ambiguous, so check/apply leave the origin,
check state, candidate, and local file unchanged and require explicit review. Each provenance-valid
legacy acceptance records the merged local hash in the old one-hash map and removes only that
candidate; after the last candidate, check migrates the stamp. A tampered sidecar or deleted recorded
path cannot be accepted automatically. Restore the valid candidate or remove it only after operator
review confirms it is stale.

Atomic state and managed-file writes use exclusive, unpredictable same-directory temporaries and a
progress-checked write-all loop; no-progress writes refuse before replacement. Parent traversal is
rejected before normalisation. Every lexical ancestor must be a real directory, not a symlink, even
when the link resolves elsewhere inside the workspace; resolved parents must remain under the root.
Legacy migration stays in memory until deterministic check/apply preflight succeeds; apply persists
the reconstructable two-hash state immediately before any managed-file write.

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
