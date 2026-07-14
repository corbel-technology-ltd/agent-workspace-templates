#!/usr/bin/env python3
"""Disposable end-to-end proof for the non-clobbering template update channel."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


MEMBER = Path(__file__).resolve().parents[1]
FAMILY = MEMBER.parent
VALUES = {
    "WORKSPACE_NAME": "Acme",
    "ENTITY": "Acme Ltd",
    "OWNER": "Alex",
    "AGENT_NAME": "Aster",
    "workspace_slug": "acme",
    "agent_slug": "aster",
    "WORKSPACE_ROOT_ENV": "ACME_ROOT",
    "SHARED_CONTEXT_PATH": "",
    "CREATED_DATE": "2026-07-11",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args, *, cwd, env, expected=0):
    result = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True)
    if result.returncode != expected:
        raise AssertionError(
            f"expected exit {expected}, got {result.returncode}: {' '.join(map(str, args))}\n"
            + result.stdout + result.stderr)
    return result


def git(cwd, env, *args):
    return run(["git", *args], cwd=cwd, env=env)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    if not (FAMILY / "instantiate.py").is_file():
        print("update-selftest: ERROR - run this gate from the template family checkout", file=sys.stderr)
        return 1
    try:
        with tempfile.TemporaryDirectory(prefix="template-update-selftest-") as raw:
            temp = Path(raw)
            home = temp / "home"
            home.mkdir()
            env = dict(os.environ, HOME=str(home), GIT_AUTHOR_NAME="Test", GIT_AUTHOR_EMAIL="t@t.t",
                       GIT_COMMITTER_NAME="Test", GIT_COMMITTER_EMAIL="t@t.t")
            family = temp / "family"
            family.mkdir()
            shutil.copy2(FAMILY / "instantiate.py", family / "instantiate.py")
            shutil.copy2(FAMILY / "CHANGELOG.md", family / "CHANGELOG.md")
            shutil.copytree(MEMBER, family / "folder-agent-workspace",
                            ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))

            git(family, env, "init", "-q")
            git(family, env, "add", "-A")
            git(family, env, "commit", "-q", "-m", "initial template")
            git(family, env, "branch", "-M", "main")
            remote = temp / "remote.git"
            git(temp, env, "init", "-q", "--bare", str(remote))
            git(family, env, "remote", "add", "origin", str(remote))
            git(family, env, "push", "-q", "-u", "origin", "main")

            instance = temp / "instance"
            run([sys.executable, "instantiate.py", "folder-agent-workspace", str(instance)],
                cwd=family, env=env)
            origin_path = instance / "00_meta/template-origin.json"
            origin = json.loads(origin_path.read_text(encoding="utf-8"))
            new_stamp_has_empty_accepted = origin.get("accepted_local_manifest") == {}
            (instance / "values.json").write_text(json.dumps(VALUES), encoding="utf-8")
            run([sys.executable, "core/onboarding/apply.py", "--root", "."],
                cwd=instance, env=env)
            origin = json.loads((instance / "00_meta/template-origin.json").read_text())
            require(origin["values"] == VALUES, "onboarding values were not persisted")
            managed = origin["managed_manifest"]
            require("AGENTS.md" in managed and "tools/template-update.py" in managed,
                    "origin manifest omitted the managed spine")
            require(not any(path.startswith(("00_meta/", "10_doctrine/", "15_canon/",
                                             "20_memory/", "50_registers/", "80_projects/",
                                             "90_runs/")) for path in managed),
                    "origin manifest included instance content or doctrine")
            (instance / ".uninitialised").unlink()
            brief = run([sys.executable, "core/hooks/session-brief.py"],
                        cwd=instance, env=env).stdout
            require("Template: update check due" in brief,
                    "session brief did not nudge when check state was absent")
            check_state = instance / "20_memory/_meta/template-check.json"
            check_state.write_text(json.dumps({
                "last_checked": "2000-01-01T00:00:00Z",
                "latest_commit": origin["commit"],
                "behind": False,
            }), encoding="utf-8")
            brief = run([sys.executable, "core/hooks/session-brief.py"],
                        cwd=instance, env=env).stdout
            require("Template: update check due" in brief,
                    "session brief did not nudge when check state was stale")

            pristine_rel = "60_workflows/default.md"
            custom_rel = "30_schemas/action-intent.md"
            new_rel = "40_templates/update-proof.md"
            pristine = instance / pristine_rel
            custom = instance / custom_rel
            custom_baseline = origin["managed_manifest"][custom_rel]
            custom_before = custom.read_text(encoding="utf-8") + "\nLocal custom line.\n"
            custom.write_text(custom_before, encoding="utf-8")
            status = run([sys.executable, "tools/template-update.py", "--status"],
                         cwd=instance, env=env).stdout
            require("customized: 1" in status and custom_rel in status,
                    "offline status did not identify the customized file")

            for rel in (pristine_rel, custom_rel):
                path = family / "folder-agent-workspace" / rel
                path.write_text(path.read_text(encoding="utf-8")
                                + "\nUpstream owner: " + "<<" + "OWNER>>.\n", encoding="utf-8")
            new_path = family / "folder-agent-workspace" / new_rel
            new_path.write_text("---\nid: " + "<<" + "workspace_slug>>.update-proof\n"
                                "type: template\n---\n\nOwner: " + "<<" + "OWNER>>.\n",
                                encoding="utf-8")
            changelog = family / "CHANGELOG.md"
            changelog.write_text(changelog.read_text(encoding="utf-8")
                                 + "\n- Self-test simulated upstream change.\n", encoding="utf-8")
            git(family, env, "add", "-A")
            git(family, env, "commit", "-q", "-m", "upstream template change")
            latest = git(family, env, "rev-parse", "HEAD").stdout.strip()
            git(family, env, "push", "-q", "origin", "main")

            checked = run([sys.executable, "tools/template-update.py", "--check"],
                          cwd=instance, env=env, expected=10)
            require("Template update available" in checked.stdout,
                    "check did not report the available update")
            require("ahead 0, behind 1" in checked.stdout
                    and "Self-test simulated upstream change" in checked.stdout,
                    "check did not report ahead/behind and the changelog slice")
            brief = run([sys.executable, "core/hooks/session-brief.py"],
                        cwd=instance, env=env).stdout
            require("Template: update available at commit " + latest[:12] in brief,
                    "session brief did not report the cached available commit")
            status = run([sys.executable, "tools/template-update.py", "--status"],
                         cwd=instance, env=env).stdout
            require("new-upstream: 1" in status and new_rel in status,
                    "cached status did not identify the new upstream file")

            preview = run([sys.executable, "tools/template-update.py", "--apply", "--dry-run"],
                          cwd=instance, env=env).stdout
            require("replaced " + pristine_rel in preview and "preserved " + custom_rel in preview,
                    "apply preview did not classify pristine/customized paths")
            applied = run([sys.executable, "tools/template-update.py", "--apply"],
                          cwd=instance, env=env).stdout
            require("replaced " + pristine_rel in applied and "added " + new_rel in applied,
                    "apply output omitted replaced/added actions")
            require("Upstream owner: Alex." in pristine.read_text(encoding="utf-8"),
                    "pristine file was not replaced and token-filled")
            require(custom.read_text(encoding="utf-8") == custom_before,
                    "customized file was changed")
            pacnew = custom.with_name(custom.name + ".template-new")
            require(pacnew.is_file() and "Upstream owner: Alex." in pacnew.read_text(encoding="utf-8"),
                    "customized file did not receive a token-filled .template-new")
            require((instance / new_rel).is_file()
                    and "Owner: Alex." in (instance / new_rel).read_text(encoding="utf-8"),
                    "new upstream file was not added and token-filled")

            origin = json.loads((instance / "00_meta/template-origin.json").read_text())
            require(origin["commit"] == latest, "origin commit was not advanced")
            require(origin["managed_manifest"][pristine_rel] == digest(pristine),
                    "pristine manifest hash was not updated")
            require(origin["managed_manifest"][new_rel] == digest(instance / new_rel),
                    "new-file manifest hash was not added")
            require(origin["managed_manifest"][custom_rel] == custom_baseline,
                    "customized manifest hash advanced before human acceptance")

            u2_candidate_digest = digest(pacnew)
            custom.write_text(
                pacnew.read_text(encoding="utf-8") + "\nLocal merged line.\n",
                encoding="utf-8",
            )
            local_l2 = custom.read_bytes()
            run([sys.executable, "tools/template-update.py", "--accept", custom_rel],
                cwd=instance, env=env)

            upstream_custom = family / "folder-agent-workspace" / custom_rel
            upstream_custom.write_text(
                upstream_custom.read_text(encoding="utf-8")
                + "\nUpstream generation: U3.\n",
                encoding="utf-8",
            )
            git(family, env, "add", f"folder-agent-workspace/{custom_rel}")
            git(family, env, "commit", "-q", "-m", "third upstream generation")
            third = git(family, env, "rev-parse", "HEAD").stdout.strip()
            git(family, env, "push", "-q", "origin", "main")

            run(
                [sys.executable, "tools/template-update.py", "--check"],
                cwd=instance,
                env=env,
                expected=10,
            )
            run(
                [sys.executable, "tools/template-update.py", "--apply"],
                cwd=instance,
                env=env,
            )

            require(
                custom.read_bytes() == local_l2,
                "accepted local merge was clobbered by the next upstream update",
            )
            pacnew = custom.with_name(custom.name + ".template-new")
            require(
                pacnew.is_file()
                and "Upstream generation: U3." in pacnew.read_text(encoding="utf-8"),
                "third upstream generation was not isolated as .template-new",
            )

            origin = json.loads(origin_path.read_text(encoding="utf-8"))
            require(
                origin["managed_manifest"][custom_rel] == u2_candidate_digest,
                "pending U3 incorrectly advanced the accepted upstream base",
            )
            require(
                origin["accepted_local_manifest"][custom_rel] == digest(custom),
                "accepted local hash was not retained while U3 awaited review",
            )
            require(
                new_stamp_has_empty_accepted,
                "new origin stamp omitted an empty accepted-local manifest",
            )

            custom.write_text(
                pacnew.read_text(encoding="utf-8") + "\nLocal merged U3 line.\n",
                encoding="utf-8",
            )
            run(
                [sys.executable, "tools/template-update.py", "--accept", custom_rel],
                cwd=instance,
                env=env,
            )

            origin = json.loads(origin_path.read_text(encoding="utf-8"))
            origin.pop("accepted_local_manifest", None)
            origin_path.write_text(json.dumps(origin, indent=2) + "\n", encoding="utf-8")
            legacy = run(
                [sys.executable, "tools/template-update.py", "--status"],
                cwd=instance,
                env=env,
            ).stdout
            require("Template status" in legacy, "legacy origin without accepted-local map did not load")
            run(
                [sys.executable, "tools/template-update.py", "--accept", custom_rel],
                cwd=instance,
                env=env,
            )
            origin = json.loads(origin_path.read_text(encoding="utf-8"))
            accepted_local = origin.get("accepted_local_manifest")
            require(
                isinstance(accepted_local, dict)
                and accepted_local.get(custom_rel) == digest(custom),
                "post-legacy acceptance did not restore the accepted-local map",
            )

            local_only_rel = "40_templates/local-only-proof.md"
            local_only = instance / local_only_rel
            local_only.write_text("local-only content\n", encoding="utf-8")
            status = run(
                [sys.executable, "tools/template-update.py", "--status"],
                cwd=instance,
                env=env,
            ).stdout
            require(local_only_rel not in status, "local-only path appeared in updater status")
            refused = run(
                [sys.executable, "tools/template-update.py", "--accept", local_only_rel],
                cwd=instance,
                env=env,
                expected=1,
            )
            require(
                "cannot accept local-only path without an upstream candidate" in refused.stderr,
                "local-only --accept did not refuse a synthetic baseline",
            )

            upstream_local_only = family / "folder-agent-workspace" / local_only_rel
            upstream_local_only.write_text("upstream local-only collision\n", encoding="utf-8")
            git(family, env, "add", f"folder-agent-workspace/{local_only_rel}")
            git(family, env, "commit", "-q", "-m", "introduce colliding upstream path")
            fourth = git(family, env, "rev-parse", "HEAD").stdout.strip()
            git(family, env, "push", "-q", "origin", "main")

            local_only_before = local_only.read_bytes()
            run(
                [sys.executable, "tools/template-update.py", "--check"],
                cwd=instance,
                env=env,
                expected=10,
            )
            run(
                [sys.executable, "tools/template-update.py", "--apply"],
                cwd=instance,
                env=env,
            )
            require(
                local_only.read_bytes() == local_only_before,
                "new upstream path clobbered a pre-existing local-only file",
            )
            local_only_candidate = local_only.with_name(local_only.name + ".template-new")
            require(
                local_only_candidate.is_file(),
                "upstream collision did not create a .template-new candidate",
            )
            candidate_digest = digest(local_only_candidate)
            run(
                [sys.executable, "tools/template-update.py", "--accept", local_only_rel],
                cwd=instance,
                env=env,
            )
            origin = json.loads(origin_path.read_text(encoding="utf-8"))
            require(
                origin["managed_manifest"][local_only_rel] == candidate_digest,
                "collision acceptance did not record the upstream candidate hash",
            )
            require(
                origin["accepted_local_manifest"][local_only_rel] == digest(local_only),
                "collision acceptance did not record the local hash separately",
            )

            backfill_rel = "60_workflows/weekly-review.md"
            backfill = instance / backfill_rel
            backfill_base = origin["managed_manifest"][backfill_rel]
            backfill.write_text(
                backfill.read_text(encoding="utf-8") + "\nBackfilled local line.\n",
                encoding="utf-8",
            )
            preview = run(
                [sys.executable, "tools/template-update.py", "--apply", "--dry-run"],
                cwd=instance,
                env=env,
            ).stdout
            require("no file changes" in preview, "no-delta backfill manufactured an apply action")
            require(
                not backfill.with_name(backfill.name + ".template-new").exists(),
                "no-delta backfill manufactured a .template-new candidate",
            )
            run(
                [sys.executable, "tools/template-update.py", "--accept", backfill_rel],
                cwd=instance,
                env=env,
            )
            origin = json.loads(origin_path.read_text(encoding="utf-8"))
            require(
                origin["managed_manifest"][backfill_rel] == backfill_base,
                "no-candidate acceptance replaced the upstream base",
            )
            require(
                origin["accepted_local_manifest"][backfill_rel] == digest(backfill),
                "no-candidate acceptance did not record the reviewed local hash",
            )
            require(origin["commit"] == fourth, "origin did not advance to the fourth fixture commit")

            final = run([sys.executable, "tools/template-update.py", "--status"],
                        cwd=instance, env=env).stdout
            groups = (
                "unchanged",
                "accepted-customized",
                "customized",
                "missing",
                "new-upstream",
            )
            count_lines = {}
            for line in final.splitlines():
                group, separator, count = line.partition(": ")
                if group in groups and separator and count.isdigit():
                    count_lines[group] = int(count)
            require(set(count_lines) == set(groups), "status omitted a standalone count group")
            require(
                count_lines["accepted-customized"] == 3
                and count_lines["customized"] == 0
                and count_lines["missing"] == 0
                and count_lines["new-upstream"] == 0,
                "final status was not clean",
            )

        print(
            "update-selftest: all green - repeated updates preserve accepted local results, "
            "collisions isolate candidates, legacy stamps load, and manifests remain current."
        )
        return 0
    except (AssertionError, OSError, subprocess.SubprocessError) as exc:
        print(f"update-selftest: FAILURE - {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
