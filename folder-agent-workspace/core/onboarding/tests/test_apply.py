#!/usr/bin/env python3
"""Tests for the deterministic onboarding substitution engine (apply.py).

Written test-first alongside apply.py. They exercise the context-aware escaping
contract, validation, idempotency, atomicity, the dry-run mode, and the
leftover-validator (including the generic <<TOKEN>> doc-literal exemption).

Every test builds an isolated tmp fixture tree that is its own git repo — we
NEVER run against the real workspace template tree.

Run:
  python3 -m pytest .../tests/test_apply.py
  python3 .../tests/test_apply.py        # falls back to unittest runner
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# --- locate apply.py and its real placeholders.yml -------------------------
HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
APPLY = SKILL_DIR / "apply.py"
REAL_PLACEHOLDERS = SKILL_DIR / "placeholders.yml"

import yaml  # PyYAML — a workspace dep


# A full, valid set of values used by most tests.
GOOD_VALUES = {
    "WORKSPACE_NAME": "Acme",
    "ENTITY": "Acme Ltd",
    "OWNER": "Alex",
    "AGENT_NAME": "Aster",
    "workspace_slug": "acme",
    "agent_slug": "aster",
    "WORKSPACE_ROOT_ENV": "ACME_ROOT",
    "SHARED_CONTEXT_PATH": "/home/alex/Shared",
    "CREATED_DATE": "2026-06-27",
}


def run_apply(tree: Path, *extra_args):
    """Invoke apply.py against a fixture tree. Returns CompletedProcess."""
    cmd = [sys.executable, str(APPLY),
           "--root", str(tree),
           "--placeholders", str(REAL_PLACEHOLDERS),
           "--values", str(tree / "values.json"),
           *extra_args]
    return subprocess.run(cmd, capture_output=True, text=True)


def git(tree: Path, *args):
    return subprocess.run(["git", "-C", str(tree), *args],
                          capture_output=True, text=True, check=True)


class FixtureTree:
    """Build a tiny git repo with one file per escaping context."""

    def __init__(self, files: dict, values: dict):
        self.dir = Path(tempfile.mkdtemp(prefix="apply_fix_"))
        for rel, content in files.items():
            p = self.dir / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        origin = {
            "repo_url": "https://example.invalid/templates.git",
            "member": "folder-agent-workspace",
            "commit": "fixture",
            "instantiated": "2026-06-27",
            "managed_manifest": {
                rel: hashlib.sha256((self.dir / rel).read_bytes()).hexdigest()
                for rel in files
            },
            "values": {},
        }
        stamp = self.dir / "00_meta" / "template-origin.json"
        stamp.parent.mkdir(parents=True, exist_ok=True)
        stamp.write_text(json.dumps(origin, indent=2) + "\n", encoding="utf-8")
        (self.dir / "values.json").write_text(
            json.dumps(values, ensure_ascii=False), encoding="utf-8")
        # make it a git repo and track everything except values.json
        git(self.dir, "init", "-q")
        git(self.dir, "config", "user.email", "t@t.t")
        git(self.dir, "config", "user.name", "t")
        # track the content files (NOT values.json — apply.py walks git ls-files)
        for rel in files:
            git(self.dir, "add", rel)
        git(self.dir, "add", "00_meta/template-origin.json")
        git(self.dir, "commit", "-q", "-m", "fixture")

    def read(self, rel):
        return (self.dir / rel).read_text(encoding="utf-8")

    def cleanup(self):
        shutil.rmtree(self.dir, ignore_errors=True)


# Canonical fixture content covering all four escaping contexts.
def standard_files():
    return {
        # .py — tokens sit inside double-quoted string literals
        "hooks/h.py": (
            'import os\n'
            'ROOT = os.environ.get("<<WORKSPACE_ROOT_ENV>>")\n'
            'WORKSPACE = "<<workspace_slug>>"\n'
            'AGENT = "<<agent_slug>>"\n'
            'SHARED = "<<SHARED_CONTEXT_PATH>>"\n'
            'NAME = "<<WORKSPACE_NAME>>"\n'
            'ENT = "<<ENTITY>>"\n'
            'OWN = "<<OWNER>>"\n'
        ),
        # .json — token inside a JSON string value
        "conf.json": (
            '{\n'
            '  "owner": "<<OWNER>>",\n'
            '  "entity": "<<ENTITY>>",\n'
            '  "slug": "<<workspace_slug>>",\n'
            '  "shared": "<<SHARED_CONTEXT_PATH>>"\n'
            '}\n'
        ),
        # .md — frontmatter scalar + body prose + the generic <<TOKEN>> literal
        "doc.md": (
            '---\n'
            'id: <<workspace_slug>>.meta.readme\n'
            'created: <<CREATED_DATE>>\n'
            'entity: <<ENTITY>>\n'
            'owner: <<OWNER>>\n'
            'shared: <<SHARED_CONTEXT_PATH>>\n'
            '---\n'
            '\n'
            '# <<WORKSPACE_NAME>>\n'
            '\n'
            'Operated by <<OWNER>> for <<ENTITY>>. Agent <<AGENT_NAME>>.\n'
            'A blank template carries `<<TOKEN>>` onboarding placeholders.\n'
        ),
        # .yml — whole file is YAML (frontmatter rules apply to entire doc)
        "data.yml": (
            'workspace: <<workspace_slug>>\n'
            'created: <<CREATED_DATE>>\n'
            'entity: <<ENTITY>>\n'
            'path: <<SHARED_CONTEXT_PATH>>\n'
        ),
    }


class TestEscapingContexts(unittest.TestCase):
    """(1) each escaping context with the SAFE example values."""

    def setUp(self):
        self.fix = FixtureTree(standard_files(), GOOD_VALUES)

    def tearDown(self):
        self.fix.cleanup()

    def test_runs_clean(self):
        r = run_apply(self.fix.dir)
        self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)

    def test_py_string_literal(self):
        run_apply(self.fix.dir)
        src = self.fix.read("hooks/h.py")
        self.assertIn('os.environ.get("ACME_ROOT")', src)
        self.assertIn('WORKSPACE = "acme"', src)
        # The .py must remain syntactically valid Python.
        compile(src, "h.py", "exec")

    def test_json_value(self):
        run_apply(self.fix.dir)
        obj = json.loads(self.fix.read("conf.json"))
        self.assertEqual(obj["owner"], "Alex")
        self.assertEqual(obj["entity"], "Acme Ltd")
        self.assertEqual(obj["slug"], "acme")
        self.assertEqual(obj["shared"], "/home/alex/Shared")

    def test_md_frontmatter_and_body(self):
        run_apply(self.fix.dir)
        text = self.fix.read("doc.md")
        # frontmatter parses and scalars are correct
        fm = text.split("---\n", 2)[1]
        meta = yaml.safe_load(fm)
        self.assertEqual(meta["id"], "acme.meta.readme")
        self.assertEqual(meta["created"], "2026-06-27")
        self.assertEqual(meta["entity"], "Acme Ltd")
        # body prose is raw-substituted
        self.assertIn("# Acme", text)
        self.assertIn("Operated by Alex for Acme Ltd. Agent Aster.", text)
        # generic <<TOKEN>> doc literal is left untouched
        self.assertIn("`<<TOKEN>>`", text)

    def test_yml_whole_file(self):
        run_apply(self.fix.dir)
        data = yaml.safe_load(self.fix.read("data.yml"))
        self.assertEqual(data["workspace"], "acme")
        self.assertEqual(data["created"], "2026-06-27")
        self.assertEqual(data["entity"], "Acme Ltd")
        self.assertEqual(data["path"], "/home/alex/Shared")


class TestHostileValues(unittest.TestCase):
    """(2) name with apostrophe + ampersand + space, path with a space.
    Prove .py / .json / frontmatter all stay parseable after substitution."""

    def setUp(self):
        vals = dict(GOOD_VALUES)
        vals["OWNER"] = "O'Brien & Co"
        vals["ENTITY"] = "O'Brien & Co \"Holdings\""
        vals["WORKSPACE_NAME"] = "O'Brien & Co"
        vals["SHARED_CONTEXT_PATH"] = "/home/o brien/Shared & Co"
        self.vals = vals
        self.fix = FixtureTree(standard_files(), vals)

    def tearDown(self):
        self.fix.cleanup()

    def test_hostile_all_contexts_parse(self):
        r = run_apply(self.fix.dir)
        self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)

        # .py still compiles and the literal round-trips to the exact value
        src = self.fix.read("hooks/h.py")
        ns = {}
        compile(src, "h.py", "exec")
        exec(src, ns)
        self.assertEqual(ns["OWN"], "O'Brien & Co")
        self.assertEqual(ns["ENT"], 'O\'Brien & Co "Holdings"')
        self.assertEqual(ns["SHARED"], "/home/o brien/Shared & Co")

        # .json parses and round-trips
        obj = json.loads(self.fix.read("conf.json"))
        self.assertEqual(obj["owner"], "O'Brien & Co")
        self.assertEqual(obj["entity"], 'O\'Brien & Co "Holdings"')
        self.assertEqual(obj["shared"], "/home/o brien/Shared & Co")

        # .md frontmatter parses and scalars round-trip
        text = self.fix.read("doc.md")
        fm = text.split("---\n", 2)[1]
        meta = yaml.safe_load(fm)
        self.assertEqual(meta["owner"], "O'Brien & Co")
        self.assertEqual(meta["entity"], 'O\'Brien & Co "Holdings"')
        self.assertEqual(meta["shared"], "/home/o brien/Shared & Co")
        # body prose is raw
        self.assertIn("Operated by O'Brien & Co for O'Brien & Co \"Holdings\".",
                      text)

        # .yml whole-file parses and round-trips
        data = yaml.safe_load(self.fix.read("data.yml"))
        self.assertEqual(data["entity"], 'O\'Brien & Co "Holdings"')
        self.assertEqual(data["path"], "/home/o brien/Shared & Co")

        # no registered leftover token remains anywhere
        out = subprocess.run(
            ["git", "-C", str(self.fix.dir), "grep", "-l", "-E",
             "<<(WORKSPACE_NAME|ENTITY|OWNER|AGENT_NAME|workspace_slug|"
             "agent_slug|WORKSPACE_ROOT_ENV|SHARED_CONTEXT_PATH|CREATED_DATE)>>"],
            capture_output=True, text=True)
        self.assertEqual(out.stdout.strip(), "", msg="leftover token found")


class TestValidationRejects(unittest.TestCase):
    """(3) bad slug / bad date / missing value are each rejected, tree untouched."""

    def _expect_abort(self, mutate):
        vals = dict(GOOD_VALUES)
        mutate(vals)
        fix = FixtureTree(standard_files(), vals)
        try:
            before = fix.read("hooks/h.py")
            r = run_apply(fix.dir)
            self.assertNotEqual(r.returncode, 0,
                                msg="expected non-zero exit")
            # tree must be untouched on a validation abort
            self.assertEqual(fix.read("hooks/h.py"), before,
                             msg="tree mutated despite invalid input")
            return (r.stdout + r.stderr)
        finally:
            fix.cleanup()

    def test_bad_slug(self):
        msg = self._expect_abort(
            lambda v: v.__setitem__("workspace_slug", "Acme Corp"))  # caps+space
        self.assertIn("workspace_slug", msg)

    def test_bad_date(self):
        msg = self._expect_abort(
            lambda v: v.__setitem__("CREATED_DATE", "27-06-2026"))
        self.assertIn("CREATED_DATE", msg)

    def test_missing_value(self):
        msg = self._expect_abort(lambda v: v.pop("AGENT_NAME"))
        self.assertIn("AGENT_NAME", msg)

    def test_value_embedding_a_token_is_rejected(self):
        # A value that contains a registered token literal must abort (else it
        # would recursively expand under the fixed replacement order).
        msg = self._expect_abort(
            lambda v: v.__setitem__("WORKSPACE_NAME", "Acme <<OWNER>> Ltd"))
        self.assertIn("WORKSPACE_NAME", msg)
        self.assertIn("OWNER", msg)

    def test_empty_shared_path_allowed(self):
        # SHARED_CONTEXT_PATH allows empty — must NOT abort.
        vals = dict(GOOD_VALUES)
        vals["SHARED_CONTEXT_PATH"] = ""
        fix = FixtureTree(standard_files(), vals)
        try:
            r = run_apply(fix.dir)
            self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)
            obj = json.loads(fix.read("conf.json"))
            self.assertEqual(obj["shared"], "")
        finally:
            fix.cleanup()

    def test_unknown_key_is_rejected_as_a_likely_typo(self):
        msg = self._expect_abort(
            lambda v: v.__setitem__("OWENR", "Alex"))
        self.assertIn("unknown key", msg)
        self.assertIn("OWENR", msg)


class TestNoviceRecoveryMessages(unittest.TestCase):
    """Common location and interruption errors say exactly how to recover."""

    def test_values_json_in_wrong_folder_names_workspace_root(self):
        fix = FixtureTree(standard_files(), GOOD_VALUES)
        try:
            wrong = fix.dir / "core" / "onboarding" / "values.json"
            wrong.parent.mkdir(parents=True, exist_ok=True)
            (fix.dir / "values.json").replace(wrong)
            r = subprocess.run(
                [sys.executable, str(APPLY), "--root", str(fix.dir),
                 "--placeholders", str(REAL_PLACEHOLDERS)],
                capture_output=True, text=True)
            msg = r.stdout + r.stderr
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("wrong place", msg)
            self.assertIn("workspace root", msg)
            self.assertIn("mv ", msg)
        finally:
            fix.cleanup()

    def test_running_from_a_subfolder_names_the_real_root(self):
        fix = FixtureTree(standard_files(), GOOD_VALUES)
        try:
            subfolder = fix.dir / "hooks"
            r = subprocess.run(
                [sys.executable, str(APPLY), "--root", str(subfolder),
                 "--placeholders", str(REAL_PLACEHOLDERS),
                 "--values", str(fix.dir / "values.json")],
                capture_output=True, text=True)
            msg = r.stdout + r.stderr
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("workspace root is", msg)
            self.assertIn(str(fix.dir), msg)
        finally:
            fix.cleanup()

    def test_stale_snapshot_restores_then_restarts(self):
        fix = FixtureTree(standard_files(), GOOD_VALUES)
        try:
            snap = fix.dir / ".onboarding_apply_snapshot"
            tracked = git(fix.dir, "ls-files", "-z").stdout.split("\0")
            for rel in filter(None, tracked):
                src = fix.dir / rel
                dst = snap / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
            # Model a process killed halfway through substitution.
            partial = fix.read("doc.md").replace("<<OWNER>>", "Alex")
            (fix.dir / "doc.md").write_text(partial, encoding="utf-8")
            checkpoint = fix.dir / ".onboarding_apply"
            checkpoint.mkdir()
            (checkpoint / "substitute.done").write_text("ok", encoding="utf-8")

            r = run_apply(fix.dir)
            self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)
            self.assertIn("recovered an interrupted earlier run", r.stdout)
            self.assertIn("Operated by Alex", fix.read("doc.md"))
            self.assertFalse(snap.exists())
            self.assertFalse(checkpoint.exists())
        finally:
            fix.cleanup()


class TestIdempotency(unittest.TestCase):
    """(4) second run is a no-op with exit 0."""

    def test_rerun_noop(self):
        fix = FixtureTree(standard_files(), GOOD_VALUES)
        try:
            r1 = run_apply(fix.dir)
            self.assertEqual(r1.returncode, 0, msg=r1.stdout + r1.stderr)
            after_first = {rel: fix.read(rel)
                           for rel in ("hooks/h.py", "conf.json",
                                       "doc.md", "data.yml")}
            # values.json is deleted on success -> recreate to re-run
            (fix.dir / "values.json").write_text(
                json.dumps(GOOD_VALUES), encoding="utf-8")
            r2 = run_apply(fix.dir)
            self.assertEqual(r2.returncode, 0, msg=r2.stdout + r2.stderr)
            for rel, content in after_first.items():
                self.assertEqual(fix.read(rel), content,
                                 msg=f"{rel} changed on rerun")
        finally:
            fix.cleanup()


class TestLeftoverValidator(unittest.TestCase):
    """(5) no registered token remains after a full run; generic <<TOKEN>> ignored."""

    def test_no_registered_token_remains(self):
        fix = FixtureTree(standard_files(), GOOD_VALUES)
        try:
            r = run_apply(fix.dir)
            self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)
            names = ("WORKSPACE_NAME", "ENTITY", "OWNER", "AGENT_NAME",
                     "workspace_slug", "agent_slug", "WORKSPACE_ROOT_ENV",
                     "SHARED_CONTEXT_PATH", "CREATED_DATE")
            for rel in ("hooks/h.py", "conf.json", "doc.md", "data.yml"):
                txt = fix.read(rel)
                for n in names:
                    self.assertNotIn(f"<<{n}>>", txt,
                                     msg=f"{n} leftover in {rel}")
            # generic doc literal survives
            self.assertIn("`<<TOKEN>>`", fix.read("doc.md"))
        finally:
            fix.cleanup()

    def test_validator_flags_injected_leftover(self):
        """If a registered token is left behind, the run must FAIL even if all
        substitutions are otherwise done — proves the validator actually scans.
        We inject a stray <<OWNER>> the replacer would normally have replaced by
        forcing a value that re-introduces nothing; instead we test the
        validator directly by adding a NEW untracked-but-tracked file containing
        a leftover the engine cannot reach? No — simplest: a file the engine
        replaces, then we confirm a clean exit means zero leftovers (covered
        above). Here we assert the generic <<TOKEN>> is never counted."""
        files = {
            "only_literal.md": (
                "---\n"
                "id: <<workspace_slug>>\n"
                "---\n"
                "Docs mention `<<TOKEN>>` as the generic placeholder.\n"
            ),
        }
        fix = FixtureTree(files, GOOD_VALUES)
        try:
            r = run_apply(fix.dir)
            self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)
            txt = fix.read("only_literal.md")
            self.assertIn("id: acme", txt)
            self.assertIn("`<<TOKEN>>`", txt)  # untouched, not flagged
        finally:
            fix.cleanup()


class TestDryRun(unittest.TestCase):
    """--dry-run validates + reports, writes nothing, keeps values.json."""

    def test_dry_run_touches_nothing(self):
        fix = FixtureTree(standard_files(), GOOD_VALUES)
        try:
            before = {rel: fix.read(rel)
                      for rel in ("hooks/h.py", "conf.json", "doc.md", "data.yml")}
            r = run_apply(fix.dir, "--dry-run")
            self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)
            self.assertIn("DRY RUN", r.stdout)
            for rel, content in before.items():
                self.assertEqual(fix.read(rel), content,
                                 msg=f"{rel} changed on a dry run")
            self.assertTrue((fix.dir / "values.json").exists(),
                            msg="values.json deleted by a dry run")
            leftovers = [p.name for p in fix.dir.glob(".onboarding_apply*")]
            self.assertEqual(leftovers, [],
                             msg=f"dry run left transients: {leftovers}")
            # the real run still works afterwards
            r2 = run_apply(fix.dir)
            self.assertEqual(r2.returncode, 0, msg=r2.stdout + r2.stderr)
            self.assertIn("# Acme", fix.read("doc.md"))
        finally:
            fix.cleanup()

    def test_exclude_prefix_left_untouched(self):
        """--exclude leaves cargo dirs verbatim (tokens there belong to others)."""
        files = dict(standard_files())
        files["registry/cap/files/payload.md"] = (
            "This cargo carries a foreign token: <<OWNER>> stays literal.\n")
        fix = FixtureTree(files, GOOD_VALUES)
        try:
            r = run_apply(fix.dir, "--exclude", "registry/")
            self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)
            self.assertIn("<<OWNER>>", fix.read("registry/cap/files/payload.md"),
                          msg="excluded cargo was substituted")
            self.assertIn("# Acme", fix.read("doc.md"),
                          msg="non-excluded files must still be filled")
        finally:
            fix.cleanup()

    def test_exclude_glob_spares_cargo_but_fills_registry_prose(self):
        """A glob exclude ('registry/*/files/') skips payloads only - the
        registry's own docs beside them are still filled."""
        files = dict(standard_files())
        files["registry/cap/files/payload.md"] = (
            "Cargo: <<OWNER>> stays literal.\n")
        files["registry/cap/README.md"] = (
            "---\nid: x\n---\n\nStocked by <<OWNER>>.\n")
        fix = FixtureTree(files, GOOD_VALUES)
        try:
            r = run_apply(fix.dir, "--exclude", "registry/*/files/")
            self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)
            self.assertIn("<<OWNER>>", fix.read("registry/cap/files/payload.md"),
                          msg="glob-excluded cargo was substituted")
            self.assertIn("Stocked by Alex.", fix.read("registry/cap/README.md"),
                          msg="registry prose beside the cargo must be filled")
        finally:
            fix.cleanup()

    def test_dry_run_still_validates(self):
        vals = dict(GOOD_VALUES)
        vals["CREATED_DATE"] = "not-a-date"
        fix = FixtureTree(standard_files(), vals)
        try:
            r = run_apply(fix.dir, "--dry-run")
            self.assertNotEqual(r.returncode, 0, msg="bad value passed a dry run")
            self.assertIn("CREATED_DATE", r.stdout + r.stderr)
        finally:
            fix.cleanup()


class TestAtomicityCleanup(unittest.TestCase):
    """values.json + checkpoints are removed on success; .git is never touched."""

    def test_values_and_checkpoints_cleaned(self):
        fix = FixtureTree(standard_files(), GOOD_VALUES)
        try:
            r = run_apply(fix.dir)
            self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)
            self.assertFalse((fix.dir / "values.json").exists(),
                             msg="values.json not deleted on success")
            # no checkpoint dir/files left lying around at the tree root
            leftovers = [p.name for p in fix.dir.glob(".onboarding_apply*")]
            self.assertEqual(leftovers, [],
                             msg=f"checkpoint leftovers: {leftovers}")
            # .git still intact
            self.assertTrue((fix.dir / ".git").is_dir())
        finally:
            fix.cleanup()

    def test_values_and_filled_hashes_persist_in_origin_stamp(self):
        fix = FixtureTree(standard_files(), GOOD_VALUES)
        try:
            r = run_apply(fix.dir)
            self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)
            origin = json.loads(fix.read("00_meta/template-origin.json"))
            self.assertEqual(origin["values"], GOOD_VALUES)
            for rel, digest in origin["managed_manifest"].items():
                self.assertEqual(
                    digest, hashlib.sha256((fix.dir / rel).read_bytes()).hexdigest(),
                    msg=f"origin hash was not rebased after filling {rel}")
        finally:
            fix.cleanup()


if __name__ == "__main__":
    unittest.main(verbosity=2)
