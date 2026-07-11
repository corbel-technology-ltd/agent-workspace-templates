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

            custom.write_text(pacnew.read_text(encoding="utf-8") + "\nLocal merged line.\n",
                              encoding="utf-8")
            run([sys.executable, "tools/template-update.py", "--accept", custom_rel],
                cwd=instance, env=env)
            require(not pacnew.exists(), "--accept did not remove .template-new")
            origin = json.loads((instance / "00_meta/template-origin.json").read_text())
            require(origin["managed_manifest"][custom_rel] == digest(custom),
                    "--accept did not record the merged hash")
            final = run([sys.executable, "tools/template-update.py", "--status"],
                        cwd=instance, env=env).stdout
            require("customized: 0" in final and "missing: 0" in final
                    and "new-upstream: 0" in final, "final status was not clean")

        print("update-selftest: all green - pristine replaced, custom preserved/pacnew/accepted, new added, manifests current.")
        return 0
    except (AssertionError, OSError, subprocess.SubprocessError) as exc:
        print(f"update-selftest: FAILURE - {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
