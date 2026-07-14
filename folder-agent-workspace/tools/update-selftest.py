#!/usr/bin/env python3
"""Disposable end-to-end proof for the non-clobbering template update channel."""
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
MEMBER = Path(__file__).resolve().parents[1]
FAMILY = MEMBER.parent
VALUES = {"WORKSPACE_NAME": "Acme", "ENTITY": "Acme Ltd", "OWNER": "Alex", "AGENT_NAME": "Aster",
          "workspace_slug": "acme", "agent_slug": "aster", "WORKSPACE_ROOT_ENV": "ACME_ROOT",
          "SHARED_CONTEXT_PATH": "", "CREATED_DATE": "2026-07-11"}
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def run(args, *, cwd, env, expected=0):
    result = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True)
    if result.returncode != expected:
        raise AssertionError(f"expected exit {expected}, got {result.returncode}: {' '.join(map(str, args))}\n"
                             + result.stdout + result.stderr)
    return result
def updater(cwd, env, *args, expected=0):
    return run([sys.executable, "tools/template-update.py", *args], cwd=cwd, env=env, expected=expected)
def git(cwd, env, *args):
    return run(["git", *args], cwd=cwd, env=env)
def require(condition, message):
    if not condition:
        raise AssertionError(message)
def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))
def store_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
def copied(value):
    return json.loads(json.dumps(value))
def prove_atomic_writes(temp):
    tools = MEMBER / "tools"
    sys.path.insert(0, str(tools))
    try:
        spec = importlib.util.spec_from_file_location("template_update_atomic_test", tools / "template-update.py")
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    root = temp / "atomic-writer"; root.mkdir(); module.ROOT = root
    target = root / "target.json"
    payload = b'{"complete": "atomic payload"}\n'
    original_fdopen = module.os.fdopen
    class ControlledWriter:
        def __init__(self, stream, outcome): self.stream, self.outcome = stream, outcome
        def __enter__(self): self.stream.__enter__(); return self
        def __exit__(self, *args): return self.stream.__exit__(*args)
        def fileno(self): return self.stream.fileno()
        def write(self, data): return self.stream.write(data[:3]) if self.outcome == "short" else self.outcome
    try:
        module.os.fdopen = lambda *args, **kwargs: ControlledWriter(original_fdopen(*args, **kwargs), "short")
        module.write_atomic(target, payload, 0o644)
        require(target.read_bytes() == payload, "atomic writer installed truncated bytes after a short write")
        for stalled in (0, None):
            target.write_bytes(b"previous complete bytes\n")
            module.os.fdopen = lambda *args, _stalled=stalled, **kwargs: ControlledWriter(original_fdopen(*args, **kwargs), _stalled)
            try:
                module.write_atomic(target, payload, 0o644)
            except module.UpdateError: pass
            else: raise AssertionError(f"atomic writer accepted stalled write result {stalled!r}")
            require(target.read_bytes() == b"previous complete bytes\n",
                    "stalled atomic write replaced complete destination bytes")
    finally:
        module.os.fdopen = original_fdopen
    try:
        module.safe_path(root / "40_templates/../90_runs/private.md")
    except module.UpdateError: pass
    else: raise AssertionError("safe_path normalised a parent traversal before refusing it")
def refuse(*args, cwd, env, origin_path, needle, candidate=None):
    before = origin_path.read_bytes()
    result = updater(cwd, env, *args, expected=1)
    require(needle in result.stderr, f"refusal omitted {needle!r}: {result.stderr}")
    require(origin_path.read_bytes() == before, "refusal changed the origin stamp")
    require(candidate is None or candidate.is_file(), "refusal removed the candidate")
    return result
def status_paths(output, group, next_group):
    lines = output.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(group + ": "))
    end = next(i for i, line in enumerate(lines) if line.startswith(next_group + ": "))
    return {line.strip() for line in lines[start + 1 : end]}
def main():
    if not (FAMILY / "instantiate.py").is_file():
        print("update-selftest: ERROR - run this gate from the template family checkout", file=sys.stderr)
        return 1
    try:
        with tempfile.TemporaryDirectory(prefix="template-update-selftest-") as raw:
            temp = Path(raw)
            prove_atomic_writes(temp)
            home = temp / "home"
            home.mkdir()
            env = dict(os.environ, HOME=str(home), GIT_AUTHOR_NAME="Test", GIT_AUTHOR_EMAIL="t@t.t",
                       GIT_COMMITTER_NAME="Test", GIT_COMMITTER_EMAIL="t@t.t")
            family = temp / "family"
            family.mkdir()
            shutil.copy2(FAMILY / "instantiate.py", family / "instantiate.py")
            shutil.copy2(FAMILY / "CHANGELOG.md", family / "CHANGELOG.md")
            shutil.copytree(MEMBER, family / "folder-agent-workspace", ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
            git(family, env, "init", "-q")
            git(family, env, "add", "-A")
            git(family, env, "commit", "-q", "-m", "initial template")
            git(family, env, "branch", "-M", "main")
            remote = temp / "remote.git"
            git(temp, env, "init", "-q", "--bare", str(remote))
            git(family, env, "remote", "add", "origin", str(remote))
            git(family, env, "push", "-q", "-u", "origin", "main")
            instance = temp / "instance"
            run([sys.executable, "instantiate.py", "folder-agent-workspace", str(instance)], cwd=family, env=env)
            origin_path = instance / "00_meta/template-origin.json"
            origin = json.loads(origin_path.read_text(encoding="utf-8"))
            new_stamp_has_empty_accepted = origin.get("accepted_local_manifest") == {}
            (instance / "values.json").write_text(json.dumps(VALUES), encoding="utf-8")
            run([sys.executable, "core/onboarding/apply.py", "--root", "."], cwd=instance, env=env)
            origin = json.loads((instance / "00_meta/template-origin.json").read_text())
            require(origin["values"] == VALUES, "onboarding values were not persisted")
            managed = origin["managed_manifest"]
            require("AGENTS.md" in managed and "tools/template-update.py" in managed, "origin manifest omitted the managed spine")
            require(not any(path.startswith(("00_meta/", "10_doctrine/", "15_canon/", "20_memory/",
                                             "50_registers/", "80_projects/", "90_runs/")) for path in managed),
                    "origin manifest included instance content or doctrine")
            clean_origin = copied(origin)
            bad_paths = (str(temp / "absolute.md"), "40_templates/../90_runs/private.md", "90_runs/private.md",
                         "40_templates/private.md.template-new", "./40_templates/private.md", "40_templates//private.md")
            for manifest_name in ("managed_manifest", "accepted_local_manifest"):
                for bad_rel in bad_paths:
                    probe = copied(clean_origin)
                    probe[manifest_name][bad_rel] = "0" * 64
                    store_json(origin_path, probe)
                    refuse("--status", cwd=instance, env=env, origin_path=origin_path, needle=f"invalid {manifest_name} path")
            probe = copied(clean_origin)
            probe["accepted_local_manifest"]["40_templates/orphan.md"] = "0" * 64
            store_json(origin_path, probe)
            refuse("--status", cwd=instance, env=env, origin_path=origin_path, needle="accepted_local_manifest path is absent from managed_manifest")
            store_json(origin_path, clean_origin)
            origin = clean_origin
            (instance / ".uninitialised").unlink()
            brief = run([sys.executable, "core/hooks/session-brief.py"], cwd=instance, env=env).stdout
            require("Template: update check due" in brief, "session brief did not nudge when check state was absent")
            check_state = instance / "20_memory/_meta/template-check.json"
            check_state.write_text(json.dumps({"last_checked": "2000-01-01T00:00:00Z", "latest_commit": origin["commit"],
                                               "behind": False}), encoding="utf-8")
            brief = run([sys.executable, "core/hooks/session-brief.py"], cwd=instance, env=env).stdout
            require("Template: update check due" in brief, "session brief did not nudge when check state was stale")
            pristine_rel = "60_workflows/default.md"
            custom_rel = "30_schemas/action-intent.md"
            new_rel = "40_templates/update-proof.md"
            pristine = instance / pristine_rel
            custom = instance / custom_rel
            custom_baseline = origin["managed_manifest"][custom_rel]
            custom_before = custom.read_text(encoding="utf-8") + "\nLocal custom line.\n"
            custom.write_text(custom_before, encoding="utf-8")
            status = updater(instance, env, "--status").stdout
            require("customized: 1" in status and custom_rel in status, "offline status did not identify the customized file")
            for rel in (pristine_rel, custom_rel):
                path = family / "folder-agent-workspace" / rel
                path.write_text(path.read_text(encoding="utf-8") + "\nUpstream owner: " + "<<" + "OWNER>>.\n", encoding="utf-8")
            new_path = family / "folder-agent-workspace" / new_rel
            new_path.write_text("---\nid: " + "<<" + "workspace_slug>>.update-proof\n"
                                "type: template\n---\n\nOwner: " + "<<" + "OWNER>>.\n", encoding="utf-8")
            changelog = family / "CHANGELOG.md"
            changelog.write_text(changelog.read_text(encoding="utf-8") + "\n- Self-test simulated upstream change.\n", encoding="utf-8")
            git(family, env, "add", "-A")
            git(family, env, "commit", "-q", "-m", "upstream template change")
            latest = git(family, env, "rev-parse", "HEAD").stdout.strip()
            git(family, env, "push", "-q", "origin", "main")
            state_parent = check_state.parent
            state_backup = state_parent.with_name("_meta.saved")
            state_escape = temp / "outside-state-parent"
            state_escape.mkdir()
            escaped_check = state_escape / check_state.name
            escaped_check.write_bytes(b"outside check state\n")
            state_parent.rename(state_backup)
            state_parent.symlink_to(state_escape, target_is_directory=True)
            escaped_bytes = escaped_check.read_bytes()
            refuse("--check", cwd=instance, env=env, origin_path=origin_path, needle="symlinked ancestor")
            require(escaped_check.read_bytes() == escaped_bytes, "state write followed a symlinked parent outside the workspace")
            state_parent.unlink()
            state_backup.rename(state_parent)
            state_sentinel = temp / "outside-state-sentinel"
            state_bytes = b"outside state sentinel\n"
            state_sentinel.write_bytes(state_bytes)
            state_temp = check_state.with_name(check_state.name + ".tmp")
            state_temp.symlink_to(state_sentinel)
            checked = updater(instance, env, "--check", expected=10)
            require(state_sentinel.read_bytes() == state_bytes, "predictable state temp followed a symlink outside the workspace")
            state_temp.unlink()
            require("Template update available" in checked.stdout, "check did not report the available update")
            require("ahead 0, behind 1" in checked.stdout and "Self-test simulated upstream change" in checked.stdout,
                    "check did not report ahead/behind and the changelog slice")
            escape_rel = "40_templates/concept-folder/README.md"
            escape_parent = instance / "40_templates/concept-folder"
            escape_bytes = (instance / escape_rel).read_bytes()
            escape_backup = escape_parent.with_name("concept-folder.saved")
            escape_targets = (instance / "90_runs/escape-target", temp / "outside-managed-parent")
            for escape_target in escape_targets:
                escape_target.mkdir(parents=True)
                escaped_local = escape_target / "README.md"
                escaped_local.write_bytes(escape_bytes + b"\noutside local\n")
                escaped_candidate = escaped_local.with_name(escaped_local.name + ".template-new")
                escaped_candidate.write_bytes(escape_bytes)
                escape_parent.rename(escape_backup)
                escape_parent.symlink_to(escape_target, target_is_directory=True)
                outside_before = (escaped_local.read_bytes(), escaped_candidate.read_bytes())
                refuse("--accept", escape_rel, cwd=instance, env=env, origin_path=origin_path, needle="symlinked ancestor", candidate=escaped_candidate)
                require((escaped_local.read_bytes(), escaped_candidate.read_bytes()) == outside_before,
                        "symlinked-parent accept read, changed, or deleted protected content")
                escape_parent.unlink()
                escape_backup.rename(escape_parent)
            brief = run([sys.executable, "core/hooks/session-brief.py"], cwd=instance, env=env).stdout
            require("Template: update available at commit " + latest[:12] in brief, "session brief did not report the cached available commit")
            status = updater(instance, env, "--status").stdout
            require("new-upstream: 1" in status and new_rel in status, "cached status did not identify the new upstream file")
            preview = updater(instance, env, "--apply", "--dry-run").stdout
            require("replaced " + pristine_rel in preview and "preserved " + custom_rel in preview, "apply preview did not classify pristine/customized paths")
            file_sentinel = temp / "outside-file-sentinel"
            file_bytes = b"outside file sentinel\n"
            file_sentinel.write_bytes(file_bytes)
            file_temp = pristine.with_name(pristine.name + ".tmp")
            file_temp.symlink_to(file_sentinel)
            applied = updater(instance, env, "--apply").stdout
            require(file_sentinel.read_bytes() == file_bytes, "predictable managed-file temp followed a symlink outside the workspace")
            file_temp.unlink()
            require("replaced " + pristine_rel in applied and "added " + new_rel in applied, "apply output omitted replaced/added actions")
            require("Upstream owner: Alex." in pristine.read_text(encoding="utf-8"), "pristine file was not replaced and token-filled")
            require(custom.read_text(encoding="utf-8") == custom_before, "customized file was changed")
            pacnew = custom.with_name(custom.name + ".template-new")
            require(pacnew.is_file() and "Upstream owner: Alex." in pacnew.read_text(encoding="utf-8"), "customized file did not receive a token-filled .template-new")
            require((instance / new_rel).is_file() and "Owner: Alex." in (instance / new_rel).read_text(encoding="utf-8"), "new upstream file was not added and token-filled")
            origin = json.loads((instance / "00_meta/template-origin.json").read_text())
            require(origin["commit"] == latest, "origin commit was not advanced")
            require(origin["managed_manifest"][pristine_rel] == digest(pristine), "pristine manifest hash was not updated")
            require(origin["managed_manifest"][new_rel] == digest(instance / new_rel), "new-file manifest hash was not added")
            require(origin["managed_manifest"][custom_rel] == custom_baseline, "customized manifest hash advanced before human acceptance")
            require(new_stamp_has_empty_accepted, "new origin stamp omitted an empty accepted-local manifest")
            u2_candidate_digest = digest(pacnew)
            second_candidate = pristine.with_name(pristine.name + ".template-new")
            second_candidate.write_bytes(pristine.read_bytes())
            origin.pop("accepted_local_manifest")
            store_json(origin_path, origin)
            pending_snapshot = (origin_path.read_bytes(), custom.read_bytes(), pacnew.read_bytes(), second_candidate.read_bytes(), check_state.read_bytes())
            for mode in ("--check", "--apply"):
                refuse(mode, cwd=instance, env=env, origin_path=origin_path, needle="pending template candidate", candidate=pacnew)
                require((origin_path.read_bytes(), custom.read_bytes(), pacnew.read_bytes(), second_candidate.read_bytes(),
                         check_state.read_bytes()) == pending_snapshot, f"legacy {mode} changed pending-review state")
            custom.write_text(pacnew.read_text(encoding="utf-8") + "\nLocal merged line.\n", encoding="utf-8")
            local_l2 = custom.read_bytes()
            updater(instance, env, "--accept", custom_rel)
            legacy_pending = load_json(origin_path)
            require("accepted_local_manifest" not in legacy_pending and legacy_pending["managed_manifest"][custom_rel] == digest(custom)
                    and not pacnew.exists() and second_candidate.is_file(), "legacy candidate acceptance did not preserve one-hash review state")
            refuse("--check", cwd=instance, env=env, origin_path=origin_path, needle="pending template candidate", candidate=second_candidate)
            updater(instance, env, "--accept", pristine_rel)
            updater(instance, env, "--check")
            migrated_pending = load_json(origin_path)
            require(migrated_pending["managed_manifest"][custom_rel] == u2_candidate_digest
                    and migrated_pending["accepted_local_manifest"][custom_rel] == digest(custom) and not second_candidate.exists(),
                    "reviewed legacy candidates did not migrate to two-hash state")
            upstream_custom = family / "folder-agent-workspace" / custom_rel
            upstream_custom.write_text(upstream_custom.read_text(encoding="utf-8") + "\nUpstream generation: U3.\n", encoding="utf-8")
            git(family, env, "add", f"folder-agent-workspace/{custom_rel}")
            git(family, env, "commit", "-q", "-m", "third upstream generation")
            third = git(family, env, "rev-parse", "HEAD").stdout.strip()
            git(family, env, "push", "-q", "origin", "main")
            updater(instance, env, "--check", expected=10)
            updater(instance, env, "--apply")
            require(custom.read_bytes() == local_l2, "accepted local merge was clobbered by the next upstream update")
            pacnew = custom.with_name(custom.name + ".template-new")
            require(pacnew.is_file() and "Upstream generation: U3." in pacnew.read_text(encoding="utf-8"), "third upstream generation was not isolated as .template-new")
            origin = json.loads(origin_path.read_text(encoding="utf-8"))
            require(origin["managed_manifest"][custom_rel] == u2_candidate_digest, "pending U3 incorrectly advanced the accepted upstream base")
            require(origin["accepted_local_manifest"][custom_rel] == digest(custom), "accepted local hash was not retained while U3 awaited review")
            custom.write_text(pacnew.read_text(encoding="utf-8") + "\nLocal merged U3 line.\n", encoding="utf-8")
            updater(instance, env, "--accept", custom_rel)
            origin = load_json(origin_path)
            legacy_upstream_digest = origin["managed_manifest"][custom_rel]
            legacy_pristine_digest = origin["managed_manifest"][pristine_rel]
            legacy_local_digest = digest(custom)
            legacy_local_bytes = custom.read_bytes()
            legacy_only_rel = "40_templates/legacy-stamp-only.md"
            legacy_only = instance / legacy_only_rel
            legacy_only.write_text("legacy local-only content\n", encoding="utf-8")
            origin["managed_manifest"][custom_rel] = legacy_local_digest
            origin["managed_manifest"][legacy_only_rel] = digest(legacy_only)
            origin.pop("accepted_local_manifest", None)
            store_json(origin_path, origin)
            live_engine = instance / "core/onboarding/apply.py"
            live_registry = instance / "core/onboarding/placeholders.yml"
            engine_bytes = live_engine.read_bytes()
            registry_bytes = live_registry.read_bytes()
            live_engine.write_bytes(engine_bytes + b'\n\ndef substitute_text(text, suffix, order, values):\n    return text.replace("<<OWNER>>", "LIVE-DRIFT"), text.count("<<OWNER>>")\n')
            live_registry.write_bytes(registry_bytes + b"\ntokens: []\nreplacement_order: []\n")
            upstream_custom.write_text(upstream_custom.read_text(encoding="utf-8") + "\nUpstream generation: U4.\n", encoding="utf-8")
            git(family, env, "add", f"folder-agent-workspace/{custom_rel}")
            git(family, env, "commit", "-q", "-m", "fourth upstream generation")
            fourth = git(family, env, "rev-parse", "HEAD").stdout.strip()
            git(family, env, "push", "-q", "origin", "main")
            legacy_state_parent = check_state.parent
            legacy_state_backup = legacy_state_parent.with_name("_meta.legacy-saved")
            legacy_state_escape = temp / "legacy-check-escape"
            legacy_state_escape.mkdir()
            escaped_legacy_check = legacy_state_escape / check_state.name
            escaped_legacy_check.write_bytes(b"protected external check state\n")
            legacy_check_before = (origin_path.read_bytes(), check_state.read_bytes(), custom.read_bytes(), escaped_legacy_check.read_bytes())
            legacy_state_parent.rename(legacy_state_backup)
            legacy_state_parent.symlink_to(legacy_state_escape, target_is_directory=True)
            refused = updater(instance, env, "--check", expected=1)
            legacy_check_after = (origin_path.read_bytes(), (legacy_state_backup / check_state.name).read_bytes(),
                                  custom.read_bytes(), escaped_legacy_check.read_bytes())
            legacy_state_parent.unlink()
            legacy_state_backup.rename(legacy_state_parent)
            require("symlinked ancestor" in refused.stderr, "legacy --check did not refuse its symlinked check-state parent")
            require(legacy_check_after == legacy_check_before, "legacy --check persisted migration before refusing unsafe check-state parent")
            updater(instance, env, "--check", expected=10)
            migrated = load_json(origin_path)
            migrated_accepted = migrated.get("accepted_local_manifest")
            require(migrated["managed_manifest"].get(custom_rel) == legacy_upstream_digest and isinstance(migrated_accepted, dict)
                    and migrated_accepted.get(custom_rel) == legacy_local_digest, "legacy accepted state was not persisted as two hashes before apply")
            require(migrated["managed_manifest"].get(pristine_rel) == legacy_pristine_digest and legacy_only_rel not in migrated["managed_manifest"]
                    and not any("migration" in key or "legacy" in key for key in migrated), "legacy migration changed a pristine base, retained an absent path, or leaked a marker")
            updater(instance, env, "--apply")
            require(custom.read_bytes() == legacy_local_bytes, "legacy accepted local content was clobbered by a later upstream update")
            pacnew = custom.with_name(custom.name + ".template-new")
            require(pacnew.is_file() and "Upstream owner: Alex." in (candidate_text := pacnew.read_text(encoding="utf-8"))
                    and "LIVE-DRIFT" not in candidate_text and "Upstream generation: U4." in candidate_text, "legacy accepted local content did not receive the newer upstream candidate")
            origin = load_json(origin_path)
            require(origin["managed_manifest"][custom_rel] == legacy_upstream_digest and origin["accepted_local_manifest"][custom_rel] == legacy_local_digest,
                    "legacy accepted state was not migrated to separate upstream and local hashes")
            updater(instance, env, "--accept", custom_rel)
            require(not pacnew.exists(), "valid legacy-migration candidate was not removed")
            live_engine.write_bytes(engine_bytes)
            live_registry.write_bytes(registry_bytes)
            migrated_origin = load_json(origin_path)
            dry_run_origin = copied(migrated_origin)
            dry_run_origin["managed_manifest"][custom_rel] = legacy_local_digest
            dry_run_origin.pop("accepted_local_manifest")
            store_json(origin_path, dry_run_origin)
            dry_run_stamp = origin_path.read_bytes()
            dry_run = updater(instance, env, "--apply", "--dry-run").stdout
            require(origin_path.read_bytes() == dry_run_stamp and custom.read_bytes() == legacy_local_bytes
                    and f"replaced {custom_rel}" not in dry_run, "legacy dry-run persisted migration, changed local content, or used local as base")
            missing_values = dict(migrated_origin["values"])
            missing_values.pop("OWNER")
            legacy_failures = (("unknown", migrated_origin["values"], "--check"), (fourth, missing_values, "lacks onboarding value"),
                               (fourth, [], "values must be one object"))
            for commit, values, needle in legacy_failures:
                probe = copied(migrated_origin)
                probe["commit"] = commit
                probe["managed_manifest"][custom_rel] = legacy_local_digest
                probe.pop("accepted_local_manifest")
                probe["values"] = values
                store_json(origin_path, probe)
                if commit == "unknown":
                    status_stamp = origin_path.read_bytes()
                    status = updater(instance, env, "--status").stdout
                    require(origin_path.read_bytes() == status_stamp and custom_rel in status_paths(status, "customized", "missing")
                            and custom_rel not in status_paths(status, "unchanged", "accepted-customized"), "offline status persisted migration or claimed a legacy entry was pristine")
                    check_stamp = check_state.read_bytes()
                    refuse("--check", cwd=instance, env=env, origin_path=origin_path, needle="mirror cache")
                    require(check_state.read_bytes() == check_stamp, "failed legacy --check changed the cached check state")
                refused = refuse("--apply", cwd=instance, env=env, origin_path=origin_path, needle=needle)
                require("legacy" in refused.stderr and custom.read_bytes() == legacy_local_bytes, "failed legacy reconstruction changed local content or omitted context")
            store_json(origin_path, migrated_origin)
            local_only_rel = "40_templates/local-only-proof.md"
            local_only = instance / local_only_rel
            local_only.write_text("local-only content\n", encoding="utf-8")
            status = updater(instance, env, "--status").stdout
            require(local_only_rel not in status, "local-only path appeared in updater status")
            refused = updater(instance, env, "--accept", local_only_rel, expected=1)
            require("cannot accept local-only path without an upstream candidate" in refused.stderr, "local-only --accept did not refuse a synthetic baseline")
            mismatch_candidate = pristine.with_name(pristine.name + ".template-new")
            mismatch_candidate.write_text("tampered candidate content\n", encoding="utf-8")
            origin_before_refusal = origin_path.read_bytes()
            refused = refuse("--accept", pristine_rel, cwd=instance, env=env, origin_path=origin_path, needle="does not match", candidate=mismatch_candidate)
            require("recorded upstream" in refused.stderr, "tampered candidate was not refused for failed upstream provenance")
            mismatch_candidate.unlink()
            unavailable_candidate = pristine.with_name(pristine.name + ".template-new")
            unavailable_candidate.write_bytes(pristine.read_bytes())
            unavailable_accept_origin = json.loads(origin_before_refusal)
            unavailable_accept_origin["commit"] = "unknown"
            store_json(origin_path, unavailable_accept_origin)
            refused = refuse("--accept", pristine_rel, cwd=instance, env=env, origin_path=origin_path, needle="unavailable", candidate=unavailable_candidate)
            require("recorded origin commit" in refused.stderr, "candidate acceptance did not refuse an unavailable recorded origin")
            origin_path.write_bytes(origin_before_refusal)
            unavailable_candidate.unlink()
            upstream_local_only = family / "folder-agent-workspace" / local_only_rel
            upstream_local_only.write_text("upstream local-only collision\n", encoding="utf-8")
            git(family, env, "add", f"folder-agent-workspace/{local_only_rel}")
            git(family, env, "commit", "-q", "-m", "introduce colliding upstream path")
            fifth = git(family, env, "rev-parse", "HEAD").stdout.strip()
            git(family, env, "push", "-q", "origin", "main")
            local_only_before = local_only.read_bytes()
            updater(instance, env, "--check", expected=10)
            local_only_candidate = local_only.with_name(local_only.name + ".template-new")
            local_only_candidate.write_bytes(upstream_local_only.read_bytes())
            refuse("--accept", local_only_rel, cwd=instance, env=env, origin_path=origin_path, needle="absent from the recorded upstream tree", candidate=local_only_candidate)
            local_only_candidate.unlink()
            updater(instance, env, "--apply")
            require(local_only.read_bytes() == local_only_before, "new upstream path clobbered a pre-existing local-only file")
            require(local_only_candidate.is_file(), "upstream collision did not create a .template-new candidate")
            candidate_digest = digest(local_only_candidate)
            updater(instance, env, "--accept", local_only_rel)
            require(not local_only_candidate.exists(), "valid accepted candidate was not removed")
            origin = load_json(origin_path)
            require(origin["managed_manifest"][local_only_rel] == candidate_digest, "collision acceptance did not record the upstream candidate hash")
            require(origin["accepted_local_manifest"][local_only_rel] == digest(local_only), "collision acceptance did not record the local hash separately")
            backfill_rel = "60_workflows/weekly-review.md"
            backfill = instance / backfill_rel
            backfill_base = origin["managed_manifest"][backfill_rel]
            backfill.write_text(backfill.read_text(encoding="utf-8") + "\nBackfilled local line.\n", encoding="utf-8")
            preview = updater(instance, env, "--apply", "--dry-run").stdout
            require("no file changes" in preview, "no-delta backfill manufactured an apply action")
            require(not backfill.with_name(backfill.name + ".template-new").exists(), "no-delta backfill manufactured a .template-new candidate")
            updater(instance, env, "--accept", backfill_rel)
            origin = load_json(origin_path)
            require(origin["managed_manifest"][backfill_rel] == backfill_base, "no-candidate acceptance replaced the upstream base")
            require(origin["accepted_local_manifest"][backfill_rel] == digest(backfill), "no-candidate acceptance did not record the reviewed local hash")
            require(origin["commit"] == fifth, "origin did not advance to the fifth fixture commit")
            symlink_rel = "60_workflows/daily-brief.md"
            symlink_path = instance / symlink_rel
            symlink_bytes = symlink_path.read_bytes()
            symlink_mode = symlink_path.stat().st_mode & 0o777
            symlink_target = instance / "local-symlink-target.md"
            symlink_target.write_text("local symlink target\n", encoding="utf-8")
            symlink_path.unlink()
            symlink_path.symlink_to(symlink_target)
            symlink_candidate = symlink_path.with_name(symlink_path.name + ".template-new")
            preview = updater(instance, env, "--apply", "--dry-run").stdout
            require(f"preserved {symlink_rel}" not in preview, "no-delta symlink was reported as receiving a template candidate")
            applied = updater(instance, env, "--apply").stdout
            require(f"preserved {symlink_rel}" not in applied and not symlink_candidate.exists(), "no-delta symlink produced a template candidate")
            symlink_path.unlink()
            symlink_path.write_bytes(symlink_bytes)
            os.chmod(symlink_path, symlink_mode)
            symlink_target.unlink()
            upstream_engine = family / "folder-agent-workspace/core/onboarding/apply.py"
            upstream_engine.write_text(upstream_engine.read_text(encoding="utf-8") + "\n# unsupported engine fixture\n", encoding="utf-8")
            git(family, env, "add", "folder-agent-workspace/core/onboarding/apply.py")
            git(family, env, "commit", "-q", "-m", "unsupported fill engine")
            git(family, env, "push", "-q", "origin", "main")
            updater(instance, env, "--check", expected=10)
            modern_origin = load_json(origin_path)
            legacy_apply = copied(modern_origin)
            for rel, accepted_digest in legacy_apply.pop("accepted_local_manifest").items():
                legacy_apply["managed_manifest"][rel] = accepted_digest
            store_json(origin_path, legacy_apply)
            legacy_apply_before = (origin_path.read_bytes(), check_state.read_bytes(), custom.read_bytes(), backfill.read_bytes())
            refused = updater(instance, env, "--apply", expected=1)
            require("unsupported onboarding fill engine" in refused.stderr, "legacy --apply did not reach the unsupported target-engine refusal")
            require((origin_path.read_bytes(), check_state.read_bytes(), custom.read_bytes(), backfill.read_bytes()) == legacy_apply_before,
                    "legacy --apply persisted migration before refusing target engine")
            store_json(origin_path, modern_origin)
            refused = refuse("--apply", cwd=instance, env=env, origin_path=origin_path, needle="unsupported onboarding fill engine")
            require("upgrade" in refused.stderr and live_engine.read_bytes() == engine_bytes, "unsupported engine refusal omitted recovery or changed the live engine")
            final = updater(instance, env, "--status").stdout
            groups = ("unchanged", "accepted-customized", "customized", "missing", "new-upstream")
            count_lines = {}
            for line in final.splitlines():
                group, separator, count = line.partition(": ")
                if group in groups and separator and count.isdigit():
                    count_lines[group] = int(count)
            require(set(count_lines) == set(groups), "status omitted a standalone count group")
            require(count_lines["accepted-customized"] == 3 and count_lines["customized"] == 0
                    and count_lines["missing"] == 0 and count_lines["new-upstream"] == 0, "final status was not clean")
        print("update-selftest: all green - manifest keys and pending reviews preserve authority; "
              "write-all, provenance, containment, and legacy refusal atomicity are enforced.")
        return 0
    except (AssertionError, OSError, subprocess.SubprocessError) as exc:
        print(f"update-selftest: FAILURE - {exc}", file=sys.stderr)
        return 1
if __name__ == "__main__":
    sys.exit(main())
