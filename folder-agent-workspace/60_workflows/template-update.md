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

## State across repeated updates

The origin stamp keeps two independent hashes. `managed_manifest[path]` is the last reviewed
upstream candidate; `accepted_local_manifest[path]` exists only when the reviewed local result
differs. Status therefore distinguishes `accepted-customized` (reviewed and protected) from
`customized` (unreviewed). Accepting with a candidate advances the upstream base to the candidate
hash and records the local result separately; accepting without a candidate leaves the existing
upstream base intact. Local-only paths stay outside updater state until upstream introduces the
same path. Apply emits `.template-new` only for a real upstream delta or a manifest-backed missing
file. A present symlink or other non-regular node produces no candidate when upstream bytes are
unchanged. Both maps permit only canonical relative POSIX paths in the managed spine, never a
`.template-new` path; every accepted-local key must also exist in the managed manifest. Legacy
stamps without the accepted-local map migrate automatically from the token-filled
tree at their recorded commit. Reconstruction uses that commit's registry and only a fill engine
whose SHA-256 the updater explicitly supports; unavailable inputs block writes rather than guessing.
If a manifest-backed legacy path still has `.template-new`, `--check` and `--apply` refuse migration
without changing the stamp, candidate, local file, or check state. Merge and explicitly `--accept`
each provenance-valid candidate. Acceptance records the merged local digest in the old one-hash map
and leaves the accepted-local map absent until all pending reviews are complete; the next `--check`
can then migrate the unambiguous stamp to two hashes.

## Run the update

1. From the workspace root, run `python3 tools/template-update.py --check`. Exit `0` means current;
   exit `10` means an update is available and is not an error. Read the printed changelog slice.
   This also migrates a reconstructable legacy one-hash stamp before any apply.
2. Run `python3 tools/template-update.py --status`. Review every `customized`, `missing`, and
   `new-upstream` path before continuing.
3. Preview with `python3 tools/template-update.py --apply --dry-run`, then run
   `python3 tools/template-update.py --apply`. Pristine files are updated, new managed files are
   added, and customized files remain byte-for-byte unchanged beside a token-filled
   `<path>.template-new` candidate. No non-updater content outside the managed spine is touched.
4. For each item under `Merge required`, compare the local file with its `.template-new`, merge the
   wanted upstream change into the local file, validate it, then run
   `python3 tools/template-update.py --accept <path>`. Accepting records the merged hash and removes
   that path's `.template-new` file only after its bytes are proven to match the token-filled blob
   for that path at the origin stamp's recorded commit. On a legacy stamp, repeat this for every
   provenance-valid pending candidate before rerunning `--check` to migrate.
5. Run `python3 tools/template-update.py --status` again. Do not call the update complete while a
   path remains `customized`, `missing`, or `new-upstream` unless the operator explicitly accepts
   that state.

If legacy reconstruction cannot find the recorded commit, make it fetchable from origin or restore
it to the updater's mirror cache, restore any missing fill values, then rerun `--check`. Upgrade
`tools/template-update.py` when it reports an unsupported recorded or target fill engine. Offline status
treats unverifiable legacy entries as customized. If check fails, stop without applying. If apply
fails part-way, inspect status and rerun only after the cause is understood; the tool never deletes
a managed or instance-content file.

If legacy `--accept` refuses because a sidecar was tampered with or its recorded upstream path was
deleted, it cannot resolve that candidate automatically. Restore the provenance-correct sidecar or,
after the operator confirms it is stale, remove it deliberately; then retry `--check`. Do not delete
a candidate merely to bypass review.

State and managed-file replacements use exclusive, unpredictable temporary files in the destination
directory, write until every byte is complete, then atomically replace the destination. A zero-progress
write refuses without replacing complete bytes. Before reading, writing, or unlinking, the updater
refuses any parent traversal or symlinked lexical ancestor, including one that resolves back inside
the workspace, and requires the resolved parent to remain under the workspace root. A managed path
may never tunnel into instance content. Legacy migration remains in memory through deterministic
check/apply validation; apply persists it only after target-engine, action, destination and origin
preflight, and before managed-file writes. Restore real directories before retrying a refusal.

## Related

- [Workspace user reference - files, scripts, memory, adapters, upkeep](../REFERENCE.md)
- [<<WORKSPACE_NAME>>](../AGENTS.md)
