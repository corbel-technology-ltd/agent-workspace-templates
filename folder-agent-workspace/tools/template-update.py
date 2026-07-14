#!/usr/bin/env python3
"""Non-clobbering update channel for a live Folder-Agent-Workspace instance."""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from template_paths import is_managed


ROOT = Path(__file__).resolve().parents[1]
ORIGIN_PATH = ROOT / "00_meta" / "template-origin.json"
CHECK_PATH = ROOT / "20_memory" / "_meta" / "template-check.json"
CACHE = Path.home() / ".cache" / "agent-workspace-templates" / "repo.git"


class UpdateError(Exception):
    pass


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    return sha256_bytes(path.read_bytes())


def regular_local(path):
    return path.is_file() and not path.is_symlink()


def run_git(args, *, git_dir=None, check=True, text=True):
    cmd = ["git"]
    if git_dir:
        cmd += ["--git-dir", str(git_dir)]
    cmd += list(args)
    result = subprocess.run(cmd, capture_output=True, text=text)
    if check and result.returncode:
        err = result.stderr.strip() if text else result.stderr.decode(errors="replace").strip()
        raise UpdateError(f"git {' '.join(args)} failed: {err or 'exit ' + str(result.returncode)}")
    return result


def read_json(path, label):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise UpdateError(f"cannot read {label} at {path}: {exc}")
    if not isinstance(value, dict):
        raise UpdateError(f"{label} at {path} must be one JSON object")
    return value


def read_origin():
    origin = read_json(ORIGIN_PATH, "template origin")
    for key in ("repo_url", "member", "commit", "managed_manifest"):
        if key not in origin:
            raise UpdateError(f"template origin is missing {key!r}")
    if not isinstance(origin["managed_manifest"], dict):
        raise UpdateError("template origin managed_manifest must be one object")
    accepted = origin.setdefault("accepted_local_manifest", {})
    if not isinstance(accepted, dict):
        raise UpdateError("template origin accepted_local_manifest must be one object")
    return origin


def write_json_atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    try:
        temp.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        os.replace(temp, path)
    finally:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass


def cache_has(commit):
    if not CACHE.is_dir() or not commit or commit == "unknown":
        return False
    return run_git(["cat-file", "-e", f"{commit}^{{commit}}"],
                   git_dir=CACHE, check=False).returncode == 0


def remote_head(repo_url):
    result = run_git(["ls-remote", repo_url, "refs/heads/main", "HEAD"])
    refs = {}
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) == 2:
            refs[fields[1]] = fields[0]
    latest = refs.get("refs/heads/main") or refs.get("HEAD")
    if not latest:
        raise UpdateError("origin has neither refs/heads/main nor HEAD")
    return latest


def refresh_cache(repo_url):
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    if CACHE.exists() and not CACHE.is_dir():
        raise UpdateError(f"cache path exists but is not a repository directory: {CACHE}")
    if not CACHE.exists():
        result = subprocess.run(
            ["git", "clone", "--mirror", repo_url, str(CACHE)],
            capture_output=True, text=True)
        if result.returncode:
            shutil.rmtree(CACHE, ignore_errors=True)
            raise UpdateError(f"git clone failed: {result.stderr.strip()}")
    else:
        run_git(["remote", "set-url", "origin", repo_url], git_dir=CACHE)
        run_git(["fetch", "--prune", "origin"], git_dir=CACHE)


def changelog_slice(old, new):
    if cache_has(old):
        diff = run_git(
            ["diff", "--unified=0", old, new, "--", "CHANGELOG.md"],
            git_dir=CACHE).stdout
        return "\n".join(
            line[1:] for line in diff.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        ).strip()
    shown = run_git(["show", f"{new}:CHANGELOG.md"], git_dir=CACHE, check=False)
    return shown.stdout.strip() if shown.returncode == 0 else ""


def check_mode():
    origin = read_origin()
    latest = remote_head(origin["repo_url"])
    refresh_cache(origin["repo_url"])
    if not cache_has(latest):
        raise UpdateError(f"cache does not contain remote commit {latest}")

    old = origin["commit"]
    ahead = behind_count = None
    if cache_has(old):
        counts = run_git(["rev-list", "--left-right", "--count", f"{old}...{latest}"],
                         git_dir=CACHE).stdout.split()
        ahead, behind_count = map(int, counts)
        behind = behind_count > 0
        relation = f"ahead {ahead}, behind {behind_count}"
    else:
        behind = old != latest
        relation = "ahead/behind unavailable (origin commit is not in the fetched history)"

    state = {
        "last_checked": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
        "latest_commit": latest,
        "behind": behind,
    }
    write_json_atomic(CHECK_PATH, state)
    print(f"Template: origin {str(old)[:12]}; latest {latest[:12]}; {relation}.")
    changes = changelog_slice(old, latest)
    if changes:
        print("CHANGELOG since this instance was created/last updated:")
        print(changes)
    else:
        print("CHANGELOG: no recorded delta for this range.")
    print("Template update available." if behind else "Template is up to date.")
    return 10 if behind else 0


def tree_entries(commit, member):
    prefix = member.rstrip("/") + "/"
    result = run_git(
        ["ls-tree", "-r", "-z", commit, "--", prefix], git_dir=CACHE, text=False)
    entries = {}
    for record in result.stdout.split(b"\0"):
        if not record:
            continue
        meta, raw_path = record.split(b"\t", 1)
        mode, kind, object_id = meta.decode().split()
        path = raw_path.decode("utf-8")
        if kind == "blob" and path.startswith(prefix):
            rel = path[len(prefix):]
            if is_managed(rel) and not rel.endswith(".template-new"):
                entries[rel] = (mode, object_id)
    return entries


def cached_target(need_check_state=False):
    if not CACHE.is_dir():
        return None
    state = None
    if CHECK_PATH.is_file():
        state = read_json(CHECK_PATH, "template check state")
        commit = state.get("latest_commit")
        if cache_has(commit):
            return commit
    if need_check_state:
        return None
    result = run_git(["rev-parse", "refs/heads/main"], git_dir=CACHE, check=False)
    commit = result.stdout.strip()
    return commit if result.returncode == 0 and cache_has(commit) else None


def classify(origin, upstream):
    manifest = origin["managed_manifest"]
    accepted = origin["accepted_local_manifest"]
    paths = set(manifest) | set(upstream)
    groups = {
        name: []
        for name in (
            "unchanged",
            "accepted-customized",
            "customized",
            "missing",
            "new-upstream",
        )
    }
    for rel in sorted(paths):
        local = ROOT / rel
        if rel in manifest:
            if local.is_symlink():
                groups["customized"].append(rel)
            elif not regular_local(local):
                groups["missing"].append(rel)
            else:
                local_digest = sha256_file(local)
                accepted_digest = accepted.get(rel)
                if local_digest == manifest[rel]:
                    groups["unchanged"].append(rel)
                elif accepted_digest is not None and local_digest == accepted_digest:
                    groups["accepted-customized"].append(rel)
                else:
                    groups["customized"].append(rel)
        elif regular_local(local) or local.is_symlink():
            groups["customized"].append(rel)
        elif rel in upstream:
            groups["new-upstream"].append(rel)
    return groups


def status_mode():
    origin = read_origin()
    target = cached_target()
    upstream = tree_entries(target, origin["member"]) if target else {}
    groups = classify(origin, upstream)
    print("Template status" + (f" against cached {target[:12]}" if target else " (offline; no cache)"))
    for name in (
        "unchanged",
        "accepted-customized",
        "customized",
        "missing",
        "new-upstream",
    ):
        print(f"{name}: {len(groups[name])}")
        for rel in groups[name]:
            print(f"  {rel}")
    return 0


def blob(commit, member, rel):
    return run_git(["show", f"{commit}:{member}/{rel}"], git_dir=CACHE, text=False).stdout


def load_fill_engine():
    path = ROOT / "core" / "onboarding" / "apply.py"
    spec = importlib.util.spec_from_file_location("onboarding_apply", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    registry = module.load_registry(ROOT / "core" / "onboarding" / "placeholders.yml")
    return module, registry


def fill_upstream(rel, data, values, engine, registry):
    # The onboarding engine and its tests deliberately carry token literals as
    # machinery/documentation; first onboarding excludes this directory too.
    if rel.startswith("core/onboarding/"):
        return data
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    needed = [name for name in registry["tokens"] if f"<<{name}>>" in text]
    missing = [name for name in needed if name not in values]
    if missing:
        raise UpdateError("origin stamp lacks onboarding value(s) needed by " + rel + ": "
                          + ", ".join(missing))
    filled, _ = engine.substitute_text(text, Path(rel).suffix, registry["order"], values)
    return filled.encode("utf-8")


def ensure_safe_destination(path):
    root = ROOT.resolve()
    parent = path.parent.resolve()
    if parent != root and root not in parent.parents:
        raise UpdateError(f"refusing to write through a path outside the workspace: {path}")


def write_file(path, data, mode):
    ensure_safe_destination(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    try:
        temp.write_bytes(data)
        os.chmod(temp, int(mode[-3:], 8))
        os.replace(temp, path)
    finally:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass


def apply_mode(dry_run=False):
    origin = read_origin()
    target = cached_target(need_check_state=True)
    if not target:
        raise UpdateError("no checked update is cached; run --check first")
    upstream = tree_entries(target, origin["member"])
    engine, registry = load_fill_engine()
    values = origin.get("values") or {}
    manifest = dict(origin["managed_manifest"])
    accepted = dict(origin["accepted_local_manifest"])
    actions = []
    merge = []

    for rel in sorted(set(manifest) | set(upstream)):
        if rel not in upstream:
            continue  # upstream deletion never deletes or reclassifies a local file
        mode, _ = upstream[rel]
        data = fill_upstream(
            rel,
            blob(target, origin["member"], rel),
            values,
            engine,
            registry,
        )
        digest = sha256_bytes(data)
        local = ROOT / rel
        baseline = manifest.get(rel)
        present = local.exists() or local.is_symlink()
        local_digest = sha256_file(local) if regular_local(local) else None
        upstream_changed = baseline is None or digest != baseline

        if baseline is None and not present:
            actions.append(("added", rel, local, data, mode))
            manifest[rel] = digest
            accepted.pop(rel, None)
        elif baseline is not None and local_digest == baseline:
            manifest[rel] = digest
            accepted.pop(rel, None)
            expected_mode = int(mode[-3:], 8)
            if local_digest != digest or (local.stat().st_mode & 0o777) != expected_mode:
                actions.append(("replaced", rel, local, data, mode))
        elif baseline is not None and not regular_local(local):
            pacnew = local.with_name(local.name + ".template-new")
            actions.append(("preserved", rel, pacnew, data, mode))
            merge.append(rel)
        elif upstream_changed:
            # Accepted and unreviewed local content are both protected on upstream delta.
            pacnew = local.with_name(local.name + ".template-new")
            actions.append(("preserved", rel, pacnew, data, mode))
            merge.append(rel)

    label = "DRY RUN" if dry_run else target[:12]
    print(f"Template apply: {label}")
    if not dry_run:
        for _, _, destination, _, _ in actions:
            ensure_safe_destination(destination)
    if not actions:
        print("  no file changes")
    for verb, rel, destination, data, mode in actions:
        if verb == "preserved":
            print(f"  preserved {rel}; wrote {rel}.template-new")
        else:
            print(f"  {verb} {rel}")
        if not dry_run:
            write_file(destination, data, mode)
    if merge:
        print("Merge required:")
        for rel in merge:
            print(f"  {rel} <- {rel}.template-new; then --accept {rel}")
    if not dry_run:
        origin["commit"] = target
        origin["managed_manifest"] = manifest
        origin["accepted_local_manifest"] = accepted
        write_json_atomic(ORIGIN_PATH, origin)
        print(f"Origin advanced to {target}.")
    return 0


def accept_mode(rel):
    candidate = Path(rel)
    if (
        candidate.is_absolute()
        or ".." in candidate.parts
        or not is_managed(candidate)
        or candidate.name.endswith(".template-new")
    ):
        raise UpdateError(f"--accept path is outside the managed spine: {rel}")
    rel = candidate.as_posix()
    if rel.startswith("./"):
        rel = rel[2:]
    local = ROOT / rel
    if not regular_local(local):
        raise UpdateError(f"cannot accept missing file: {rel}")

    origin = read_origin()
    manifest = origin["managed_manifest"]
    accepted = origin["accepted_local_manifest"]
    pacnew = local.with_name(local.name + ".template-new")
    candidate_present = pacnew.exists() or pacnew.is_symlink()
    if candidate_present and not regular_local(pacnew):
        raise UpdateError(f"template candidate is not a regular file: {rel}.template-new")
    if candidate_present:
        manifest[rel] = sha256_file(pacnew)
    elif rel not in manifest:
        raise UpdateError(
            f"cannot accept local-only path without an upstream candidate: {rel}"
        )

    local_digest = sha256_file(local)
    if local_digest == manifest[rel]:
        accepted.pop(rel, None)
    else:
        accepted[rel] = local_digest

    origin["managed_manifest"] = manifest
    origin["accepted_local_manifest"] = accepted
    write_json_atomic(ORIGIN_PATH, origin)
    if candidate_present:
        pacnew.unlink()
    state = "upstream base plus accepted local hash" if rel in accepted else "upstream base"
    suffix = "; .template-new deleted." if candidate_present else "."
    print(f"Accepted {rel}; recorded {state}{suffix}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", action="store_true", help="fetch and report template updates")
    modes.add_argument("--status", action="store_true", help="classify managed files offline")
    modes.add_argument("--apply", action="store_true", help="apply the last checked update safely")
    modes.add_argument("--accept", metavar="PATH", help="accept a human-merged managed file")
    parser.add_argument("--dry-run", action="store_true", help="preview --apply without writing")
    args = parser.parse_args(argv)
    if args.dry_run and not args.apply:
        parser.error("--dry-run is valid only with --apply")
    try:
        if args.check:
            return check_mode()
        if args.status:
            return status_mode()
        if args.apply:
            return apply_mode(args.dry_run)
        return accept_mode(args.accept)
    except (OSError, UpdateError, subprocess.SubprocessError) as exc:
        print(f"template-update: ERROR - {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
