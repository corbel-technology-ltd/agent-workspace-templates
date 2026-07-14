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
import tempfile
from pathlib import Path
from template_paths import is_managed
ROOT = Path(__file__).resolve().parents[1]
ORIGIN_PATH = ROOT / "00_meta" / "template-origin.json"
CHECK_PATH = ROOT / "20_memory" / "_meta" / "template-check.json"
CACHE = Path.home() / ".cache" / "agent-workspace-templates" / "repo.git"
SUPPORTED_FILL_ENGINES = {"b8a21ee63a4f6da2098f8f340a8e48e9ed353e1f656195b3bf8725afc446011f"}
class UpdateError(Exception):
    pass
def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()
def sha256_file(path):
    return sha256_bytes(path.read_bytes())
def regular_local(path):
    return not path.is_symlink() and path.is_file()
def safe_path(path):
    path = Path(path)
    if ".." in path.parts:
        raise UpdateError(f"refusing path with parent traversal: {path}")
    root = ROOT.resolve()
    path = Path(os.path.abspath(path))
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise UpdateError(f"refusing path outside workspace: {path}") from exc
    cursor = root
    for part in relative.parts[:-1]:
        cursor /= part
        if cursor.is_symlink():
            raise UpdateError(f"refusing path with symlinked ancestor: {path}")
    parent = path.parent.resolve()
    if parent != root and root not in parent.parents:
        raise UpdateError(f"refusing resolved parent outside workspace: {path}")
    return path
def write_atomic(path, data, mode):
    path = safe_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path = safe_path(path)
    descriptor, raw_temp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp = Path(raw_temp)
    try:
        with os.fdopen(descriptor, "wb", buffering=0) as stream:
            view = memoryview(data)
            while view:
                written = stream.write(view)
                if written is None or written <= 0 or written > len(view):
                    raise UpdateError(f"atomic write made no progress for {path}")
                view = view[written:]
            os.fchmod(stream.fileno(), mode)
            os.fsync(stream.fileno())
        os.replace(safe_path(temp), safe_path(path))
    finally:
        safe_path(temp).unlink(missing_ok=True)
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
    path = safe_path(path)
    if path.is_symlink():
        raise UpdateError(f"refusing to read symlinked {label} at {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise UpdateError(f"cannot read {label} at {path}: {exc}")
    if not isinstance(value, dict):
        raise UpdateError(f"{label} at {path} must be one JSON object")
    return value
def validate_manifest(manifest, label):
    for rel in manifest:
        path = Path(rel)
        if (path.is_absolute() or ".." in path.parts or rel != path.as_posix() or not is_managed(path)
                or path.name.endswith(".template-new")):
            raise UpdateError(f"invalid {label} path: {rel!r}")
def read_origin():
    origin = read_json(ORIGIN_PATH, "template origin")
    for key in ("repo_url", "member", "commit", "managed_manifest"):
        if key not in origin:
            raise UpdateError(f"template origin is missing {key!r}")
    if not isinstance(origin["managed_manifest"], dict):
        raise UpdateError("template origin managed_manifest must be one object")
    legacy = "accepted_local_manifest" not in origin
    if not legacy and not isinstance(origin["accepted_local_manifest"], dict):
        raise UpdateError("template origin accepted_local_manifest must be one object")
    validate_manifest(origin["managed_manifest"], "managed_manifest")
    if not legacy:
        accepted = origin["accepted_local_manifest"]
        validate_manifest(accepted, "accepted_local_manifest")
        absent = set(accepted) - set(origin["managed_manifest"])
        if absent:
            raise UpdateError(f"accepted_local_manifest path is absent from managed_manifest: {min(absent)!r}")
    return origin, legacy
def write_json_atomic(path, value):
    data = (json.dumps(value, indent=2) + "\n").encode("utf-8")
    write_atomic(path, data, 0o644)
def cache_has(commit):
    if not CACHE.is_dir() or not commit or commit == "unknown":
        return False
    return run_git(["cat-file", "-e", f"{commit}^{{commit}}"], git_dir=CACHE, check=False).returncode == 0
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
        result = subprocess.run(["git", "clone", "--mirror", repo_url, str(CACHE)],
                                capture_output=True, text=True)
        if result.returncode:
            shutil.rmtree(CACHE, ignore_errors=True)
            raise UpdateError(f"git clone failed: {result.stderr.strip()}")
    else:
        run_git(["remote", "set-url", "origin", repo_url], git_dir=CACHE)
        run_git(["fetch", "--prune", "origin"], git_dir=CACHE)
def changelog_slice(old, new):
    if cache_has(old):
        diff = run_git(["diff", "--unified=0", old, new, "--", "CHANGELOG.md"], git_dir=CACHE).stdout
        return "\n".join(line[1:] for line in diff.splitlines()
                         if line.startswith("+") and not line.startswith("+++")).strip()
    shown = run_git(["show", f"{new}:CHANGELOG.md"], git_dir=CACHE, check=False)
    return shown.stdout.strip() if shown.returncode == 0 else ""
def check_mode():
    origin, legacy = read_origin()
    safe_path(CHECK_PATH)
    latest = remote_head(origin["repo_url"])
    refresh_cache(origin["repo_url"])
    if not cache_has(latest):
        raise UpdateError(f"cache does not contain remote commit {latest}")
    if legacy:
        origin = migrate_legacy_origin(origin)
    old = origin["commit"]
    ahead = behind_count = None
    if cache_has(old):
        counts = run_git(["rev-list", "--left-right", "--count", f"{old}...{latest}"], git_dir=CACHE).stdout.split()
        ahead, behind_count = map(int, counts)
        behind = behind_count > 0
        relation = f"ahead {ahead}, behind {behind_count}"
    else:
        behind = old != latest
        relation = "ahead/behind unavailable (origin commit is not in the fetched history)"
    state = {"last_checked": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
             "latest_commit": latest, "behind": behind}
    changes = changelog_slice(old, latest)
    safe_path(ORIGIN_PATH)
    safe_path(CHECK_PATH)
    if legacy:
        write_json_atomic(ORIGIN_PATH, origin)
    write_json_atomic(CHECK_PATH, state)
    print(f"Template: origin {str(old)[:12]}; latest {latest[:12]}; {relation}.")
    if changes:
        print("CHANGELOG since this instance was created/last updated:")
        print(changes)
    else:
        print("CHANGELOG: no recorded delta for this range.")
    print("Template update available." if behind else "Template is up to date.")
    return 10 if behind else 0
def tree_entries(commit, member):
    prefix = member.rstrip("/") + "/"
    result = run_git(["ls-tree", "-r", "-z", commit, "--", prefix], git_dir=CACHE, text=False)
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
    check_path = safe_path(CHECK_PATH)
    if check_path.is_symlink():
        raise UpdateError(f"refusing to read symlinked template check state at {check_path}")
    if check_path.is_file():
        state = read_json(check_path, "template check state")
        commit = state.get("latest_commit")
        if cache_has(commit):
            return commit
    if need_check_state:
        return None
    result = run_git(["rev-parse", "refs/heads/main"], git_dir=CACHE, check=False)
    commit = result.stdout.strip()
    return commit if result.returncode == 0 and cache_has(commit) else None
def classify(origin, upstream, legacy_unverified=False):
    manifest = origin["managed_manifest"]
    accepted = origin["accepted_local_manifest"]
    paths = set(manifest) | set(upstream)
    names = ("unchanged", "accepted-customized", "customized", "missing", "new-upstream")
    groups = {name: [] for name in names}
    for rel in sorted(paths):
        local = safe_path(ROOT / rel)
        if rel in manifest:
            if legacy_unverified and (regular_local(local) or local.is_symlink()):
                groups["customized"].append(rel)
            elif local.is_symlink():
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
    origin, legacy = read_origin()
    legacy_error = None
    if legacy:
        try:
            origin = migrate_legacy_origin(origin)
        except UpdateError as exc:
            legacy_error = str(exc)
            origin = dict(origin)
            origin["accepted_local_manifest"] = {}
    target = cached_target()
    upstream = tree_entries(target, origin["member"]) if target else {}
    groups = classify(origin, upstream, legacy_unverified=legacy_error is not None)
    print("Template status" + (f" against cached {target[:12]}" if target else " (offline; no cache)"))
    if legacy_error:
        print(f"Legacy stamp unverified: {legacy_error}")
    for name in ("unchanged", "accepted-customized", "customized", "missing", "new-upstream"):
        print(f"{name}: {len(groups[name])}")
        for rel in groups[name]:
            print(f"  {rel}")
    return 0
def blob(commit, member, rel):
    return run_git(["show", f"{commit}:{member}/{rel}"], git_dir=CACHE, text=False).stdout
def load_fill_engine(commit, member):
    engine_data = blob(commit, member, "core/onboarding/apply.py")
    engine_digest = sha256_bytes(engine_data)
    if engine_digest not in SUPPORTED_FILL_ENGINES:
        raise UpdateError(f"unsupported onboarding fill engine {engine_digest} at {commit[:12]}; upgrade "
                          "tools/template-update.py or restore a commit with a supported engine")
    registry_data = blob(commit, member, "core/onboarding/placeholders.yml")
    with tempfile.TemporaryDirectory(prefix="template-fill-") as raw:
        path = Path(raw) / "apply.py"
        registry_path = Path(raw) / "placeholders.yml"
        path.write_bytes(engine_data)
        registry_path.write_bytes(registry_data)
        spec = importlib.util.spec_from_file_location(f"onboarding_apply_{commit[:12]}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module, module.load_registry(registry_path)
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
        raise UpdateError("origin stamp lacks onboarding value(s) needed by " + rel + ": " + ", ".join(missing))
    filled, _ = engine.substitute_text(text, Path(rel).suffix, registry["order"], values)
    return filled.encode("utf-8")
def reconstruction_context(origin, purpose, recovery=None):
    commit = origin["commit"]
    recovery = recovery or ("make the recorded commit fetchable from origin or restore it in the "
                            "mirror cache, then run --check")
    if not cache_has(commit):
        raise UpdateError(f"cannot {purpose}: recorded origin commit {commit!r} is unavailable in the "
                          f"local cache; {recovery}")
    values = origin.get("values", {})
    if not isinstance(values, dict):
        raise UpdateError(f"cannot {purpose}: values must be one object; {recovery}")
    try:
        engine = load_fill_engine(commit, origin["member"])
    except UpdateError as exc:
        raise UpdateError(f"cannot {purpose}: {exc}; {recovery}") from exc
    return commit, tree_entries(commit, origin["member"]), values, *engine
def recorded_upstream_data(origin, rel, purpose, context=None):
    commit, upstream, values, engine, registry = context or reconstruction_context(origin, purpose)
    if rel not in upstream:
        raise UpdateError(f"cannot {purpose}: {rel} is absent from the recorded upstream tree")
    try:
        return fill_upstream(rel, blob(commit, origin["member"], rel), values, engine, registry)
    except UpdateError as exc:
        raise UpdateError(f"cannot {purpose}: {exc}") from exc
def migrate_legacy_origin(origin):
    purpose = "migrate legacy template origin"
    recovery = ("restore the recorded onboarding values and make the recorded commit fetchable from "
                "origin or restore it in the mirror cache, then run --check")
    pending = []
    for rel in sorted(origin["managed_manifest"]):
        candidate = safe_path((ROOT / rel).with_name(Path(rel).name + ".template-new"))
        if candidate.is_symlink() or candidate.exists():
            pending.append(rel)
    if pending:
        raise UpdateError("cannot migrate legacy origin while pending template candidate(s) await review: "
                          + ", ".join(pending) + "; --accept each provenance-valid candidate, or restore/remove "
                          "operator-confirmed stale candidates, before --check")
    context = reconstruction_context(origin, purpose, recovery)
    upstream = context[1]
    manifest = {}
    accepted = {}
    for rel, stored_digest in sorted(origin["managed_manifest"].items()):
        if rel not in upstream:
            continue
        try:
            upstream_digest = sha256_bytes(recorded_upstream_data(origin, rel, purpose, context))
        except UpdateError as exc:
            raise UpdateError(f"{exc}; {recovery}") from exc
        manifest[rel] = upstream_digest
        if stored_digest != upstream_digest:
            accepted[rel] = stored_digest
    migrated = dict(origin)
    migrated["managed_manifest"] = manifest
    migrated["accepted_local_manifest"] = accepted
    return migrated
def write_file(path, data, mode):
    write_atomic(path, data, int(mode[-3:], 8))
def apply_mode(dry_run=False):
    origin, legacy = read_origin()
    target = cached_target(need_check_state=True)
    if not target:
        raise UpdateError("no checked update is cached; run --check first")
    if legacy:
        origin = migrate_legacy_origin(origin)
    upstream = tree_entries(target, origin["member"])
    engine, registry = load_fill_engine(target, origin["member"])
    values = origin.get("values") or {}
    manifest = dict(origin["managed_manifest"])
    accepted = dict(origin["accepted_local_manifest"])
    actions = []
    merge = []
    for rel in sorted(set(manifest) | set(upstream)):
        if rel not in upstream:
            continue  # upstream deletion never deletes or reclassifies a local file
        mode, _ = upstream[rel]
        data = fill_upstream(rel, blob(target, origin["member"], rel), values, engine, registry)
        digest = sha256_bytes(data)
        local = safe_path(ROOT / rel)
        baseline = manifest.get(rel)
        present = local.is_symlink() or local.exists()
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
        elif baseline is not None and not regular_local(local) and (not present or upstream_changed):
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
            safe_path(destination)
        safe_path(ORIGIN_PATH)
        if legacy:
            write_json_atomic(ORIGIN_PATH, origin)
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
    if (candidate.is_absolute() or ".." in candidate.parts or not is_managed(candidate)
            or candidate.name.endswith(".template-new")):
        raise UpdateError(f"--accept path is outside the managed spine: {rel}")
    rel = candidate.as_posix()
    if rel.startswith("./"):
        rel = rel[2:]
    local = safe_path(ROOT / rel)
    if not regular_local(local):
        raise UpdateError(f"cannot accept missing file: {rel}")
    pacnew = safe_path(local.with_name(local.name + ".template-new"))
    candidate_present = pacnew.is_symlink() or pacnew.exists()
    if candidate_present and not regular_local(pacnew):
        raise UpdateError(f"template candidate is not a regular file: {rel}.template-new")
    origin, legacy = read_origin()
    manifest = dict(origin["managed_manifest"])
    accepted = {} if legacy else dict(origin["accepted_local_manifest"])
    if candidate_present:
        upstream_digest = sha256_bytes(recorded_upstream_data(origin, rel, "verify template candidate"))
        if sha256_file(pacnew) != upstream_digest:
            raise UpdateError(f"template candidate for {rel} does not match recorded upstream bytes")
        if legacy:
            manifest[rel] = sha256_file(local)
            origin["managed_manifest"] = manifest
            write_json_atomic(ORIGIN_PATH, origin)
            safe_path(pacnew).unlink()
            print(f"Accepted {rel}; recorded legacy accepted-local hash; .template-new deleted.")
            return 0
        manifest[rel] = upstream_digest
    elif legacy:
        origin = migrate_legacy_origin(origin)
        manifest = dict(origin["managed_manifest"])
        accepted = dict(origin["accepted_local_manifest"])
    if not candidate_present and rel not in manifest:
        raise UpdateError(f"cannot accept local-only path without an upstream candidate: {rel}")
    local_digest = sha256_file(local)
    if local_digest == manifest[rel]:
        accepted.pop(rel, None)
    else:
        accepted[rel] = local_digest
    origin["managed_manifest"] = manifest
    origin["accepted_local_manifest"] = accepted
    write_json_atomic(ORIGIN_PATH, origin)
    if candidate_present:
        safe_path(pacnew).unlink()
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
