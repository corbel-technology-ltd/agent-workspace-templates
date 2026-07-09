#!/usr/bin/env python3
"""chandler.py - the deterministic engine of a Capability-Registry capability registry.

A capability is a folder under registry/<name>/ holding a manifest.yml (name, version, files with
sha256 checksums and workspace target paths) plus the payload under files/. This engine stocks,
verifies, and moves capabilities between the registry and workspaces - nothing more. No network,
no dependency resolution, no auto-update; installing is copying files and recording checksums, and
every overwrite of local difference requires an explicit --yes (human at the gate).

Commands:
    list                                        stock overview (name, version, description)
    verify                                      registry self-check: manifests parse, payloads
                                                match their checksums (the registry gate; exit 1
                                                on any mismatch)
    status   --workspace PATH [NAME]            per capability x file: in-sync / drifted /
                                                missing, plus the workspace lockfile version
    diff     NAME --workspace PATH              unified diff registry vs workspace, per file
    install  NAME --workspace PATH [--yes]      copy payload to targets; write .capability-registry.yml
                                                lockfile; refuses to overwrite a differing file
                                                without --yes
    pack     NAME --from-workspace PATH [--yes] flow-back: pull improved files from a workspace
                                                into the registry, bump version, refresh
                                                checksums; prints the ledger line (--write-ledger
                                                appends it)
    fleet                                       list enrolled workspaces with aggregate status;
                                                cross-checks a linked shared-context roster if
                                                fleet.yml names one
    enrol    --name NAME --path PATH            add a workspace to fleet.yml (idempotent)

stdlib + PyYAML. Deterministic output (sorted), sha256 checksums, integer monotonic versions.
"""
import argparse
import datetime
import difflib
import hashlib
import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"
FLEET = ROOT / "fleet.yml"
LEDGER = ROOT / "ledger.md"
LEDGER_MARKER = "<!-- ledger: append new entries directly below this line, newest first -->"
LOCKFILE = ".capability-registry.yml"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def fail(msg):
    print(f"chandler: {msg}", file=sys.stderr)
    sys.exit(1)


def capabilities():
    """Sorted capability names present in the registry."""
    if not REGISTRY.is_dir():
        return []
    return sorted(p.name for p in REGISTRY.iterdir()
                  if p.is_dir() and (p / "manifest.yml").is_file())


def _safe_rel_path(name, kind, value):
    """A manifest path must be relative and contained (no '..', no '~', no absolutes).

    This is load-bearing: `target` decides where `install` writes inside a
    workspace, and manifests travel between machines - a poisoned target must
    fail EVERY command (including `verify`), never write outside the workspace.
    """
    p = Path(str(value))
    if p.is_absolute() or ".." in p.parts or str(value).startswith("~"):
        fail(f"{name}: illegal {kind} path {value!r} - must be relative, "
             f"no '..', no '~', no absolute paths")
    return str(value)


def load_manifest(name):
    mp = REGISTRY / name / "manifest.yml"
    if not mp.is_file():
        fail(f"unknown capability {name!r} (no {mp.relative_to(ROOT)})")
    try:
        m = yaml.safe_load(mp.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        fail(f"{name}: manifest.yml is not valid YAML: {e}")
    if not isinstance(m, dict):
        fail(f"{name}: manifest.yml must be a mapping")
    for key in ("name", "version", "files"):
        if key not in m:
            fail(f"{name}: manifest.yml missing key {key!r}")
    if m["name"] != name:
        fail(f"{name}: manifest name {m['name']!r} does not match its folder")
    if not isinstance(m["files"], list) or not m["files"]:
        fail(f"{name}: manifest 'files' must be a non-empty list")
    for f in m["files"]:
        if not isinstance(f, dict):
            fail(f"{name}: each manifest file entry must be a mapping")
        for key in ("src", "target", "sha256"):
            if key not in f or not f[key]:
                fail(f"{name}: a manifest file entry is missing {key!r}")
        _safe_rel_path(name, "src", f["src"])
        _safe_rel_path(name, "target", f["target"])
    return m


def cmd_list(_args):
    caps = capabilities()
    if not caps:
        print("chandler: registry is empty.")
        return 0
    width = max(len(c) for c in caps)
    for name in caps:
        m = load_manifest(name)
        print(f"{name.ljust(width)}  v{m['version']}  {m.get('description', '')}")
    return 0


def cmd_verify(_args):
    problems = []
    for name in capabilities():
        m = load_manifest(name)
        if not isinstance(m["version"], int) or m["version"] < 1:
            problems.append(f"{name}: version must be a positive integer")
        for f in m["files"]:
            src = REGISTRY / name / f["src"]
            if not src.is_file():
                problems.append(f"{name}: payload missing: {f['src']}")
                continue
            actual = sha256(src)
            if actual != f.get("sha256"):
                problems.append(
                    f"{name}: checksum mismatch for {f['src']} "
                    f"(manifest {str(f.get('sha256'))[:12]}…, actual {actual[:12]}…) - "
                    f"if the change is intended, this is a `pack` (version bump), not an edit")
    if problems:
        for p in sorted(problems):
            print(p)
        print(f"\nchandler verify: {len(problems)} problem(s).", file=sys.stderr)
        return 1
    print(f"chandler verify: clean - {len(capabilities())} capability(ies), "
          f"all payloads match their manifests.")
    return 0


def read_lock(ws: Path):
    lp = ws / LOCKFILE
    if not lp.is_file():
        return {}
    try:
        data = yaml.safe_load(lp.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        fail(f"lockfile {lp} is not valid YAML ({e}) - fix or delete it, then re-run")
    installed = data.get("installed", {}) if isinstance(data, dict) else None
    if not isinstance(installed, dict) \
            or not all(isinstance(v, dict) for v in installed.values()):
        fail(f"lockfile {lp} has an unexpected shape - fix or delete it, then re-run")
    return installed


def write_lock(ws: Path, installed: dict):
    lp = ws / LOCKFILE
    lp.write_text(
        "# .capability-registry.yml - what this workspace has installed from its capability-registry.\n"
        "# Written by chandler.py install; read by chandler.py status. Track it in git.\n"
        + yaml.safe_dump({"installed": installed}, sort_keys=True),
        encoding="utf-8")


def file_state(ws: Path, name, f):
    """(state, registry_sha, target_sha) for one manifest file against a workspace."""
    target = ws / f["target"]
    reg_sha = f.get("sha256", "")
    if not target.is_file():
        return "missing", reg_sha, None
    t_sha = sha256(target)
    return ("in-sync" if t_sha == reg_sha else "drifted"), reg_sha, t_sha


def cmd_status(args):
    ws = Path(args.workspace).resolve()
    if not ws.is_dir():
        fail(f"workspace not found: {ws}")
    names = [args.capability] if args.capability else capabilities()
    lock = read_lock(ws)
    drifted = 0
    for name in names:
        m = load_manifest(name)
        lock_note = ""
        lv = lock.get(name, {}).get("version")
        if isinstance(lv, int):
            lock_note = f" (installed v{lv}" + (
                ", registry ahead)" if lv < m["version"] else ")")
        print(f"{name} v{m['version']}{lock_note}")
        for f in m["files"]:
            state, _, _ = file_state(ws, name, f)
            if state != "in-sync":
                drifted += 1
            print(f"  {state:8}  {f['target']}")
    if drifted:
        print(f"\nchandler status: {drifted} file(s) not in sync. "
              f"`diff` to inspect; `install` to adopt registry -> workspace; "
              f"`pack` to flow workspace -> registry.")
        return 1
    print("\nchandler status: all in sync.")
    return 0


def cmd_diff(args):
    ws = Path(args.workspace).resolve()
    if not ws.is_dir():
        fail(f"workspace not found: {ws}")
    m = load_manifest(args.name)
    for f in m["files"]:
        src = REGISTRY / args.name / f["src"]
        target = ws / f["target"]
        if not target.is_file():
            print(f"--- {f['target']}: missing in workspace")
            continue
        a = src.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
        b = target.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
        sys.stdout.writelines(difflib.unified_diff(
            a, b, fromfile=f"registry/{args.name}/{f['src']}",
            tofile=str(target)))
    return 0


def cmd_install(args):
    ws = Path(args.workspace).resolve()
    if not ws.is_dir():
        fail(f"workspace not found: {ws}")
    m = load_manifest(args.name)
    # Refuse silently overwriting local difference without an explicit yes.
    blocked = []
    for f in m["files"]:
        state, _, _ = file_state(ws, args.name, f)
        if state == "drifted" and not args.yes:
            blocked.append(f["target"])
    if blocked:
        fail("these workspace files differ from the registry:\n  "
             + "\n  ".join(blocked)
             + "\nRun `diff` to inspect. Re-run install with --yes to overwrite, "
               "or `pack` first if the workspace copy is the improvement.")
    installed_files = {}
    for f in m["files"]:
        src = REGISTRY / args.name / f["src"]
        target = ws / f["target"]
        # Belt-and-braces containment (the manifest was already validated):
        # never write outside the workspace, whatever the path resolves to.
        if ws.resolve() not in target.resolve().parents:
            fail(f"{args.name}: refusing to write outside the workspace: {f['target']!r}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
        installed_files[f["target"]] = f["sha256"]
        print(f"installed  {f['target']}")
    lock = read_lock(ws)
    lock[args.name] = {"version": m["version"],
                       "date": datetime.date.today().isoformat(),
                       "files": installed_files}
    write_lock(ws, lock)
    print(f"chandler install: {args.name} v{m['version']} -> {ws} "
          f"({len(installed_files)} file(s); lockfile updated).")
    return 0


def cmd_pack(args):
    ws = Path(args.from_workspace).resolve()
    m = load_manifest(args.name)
    changed = []
    for f in m["files"]:
        target = ws / f["target"]
        if not target.is_file():
            fail(f"{args.name}: workspace copy missing: {target}")
        if sha256(target) != f.get("sha256"):
            changed.append(f)
    if not changed:
        print(f"chandler pack: {args.name} - workspace copy identical to registry; nothing to do.")
        return 0
    if not args.yes:
        for f in changed:
            print(f"would pack  {f['target']}  ->  registry/{args.name}/{f['src']}")
        print(f"chandler pack: {len(changed)} file(s) differ. Review with `diff`, then re-run "
              f"with --yes to pull them into the registry and bump "
              f"v{m['version']} -> v{m['version'] + 1}.")
        return 1
    # Pre-flight the ledger BEFORE mutating anything: a pack that cannot leave
    # its ledger line must not change the registry (append-only history is a
    # hard rule, and a half-done pack that exits non-zero is worse than none).
    if args.write_ledger:
        if not LEDGER.is_file() or LEDGER_MARKER not in LEDGER.read_text(encoding="utf-8"):
            fail("ledger.md is missing its marker line - restore it before packing "
                 "with --write-ledger (nothing was changed)")
    for f in m["files"]:
        target = ws / f["target"]
        src = REGISTRY / args.name / f["src"]
        shutil.copy2(target, src)
        f["sha256"] = sha256(src)
    m["version"] = int(m["version"]) + 1
    (REGISTRY / args.name / "manifest.yml").write_text(
        yaml.safe_dump(m, sort_keys=False), encoding="utf-8")
    today = datetime.date.today().isoformat()
    line = (f"{today} | pack | {args.name} v{m['version']} packed from {ws.name} "
            f"({len(changed)} file(s) changed) | install to the rest of the fleet to close drift")
    print(f"chandler pack: {args.name} -> v{m['version']} ({len(changed)} file(s)).")
    if args.write_ledger:
        text = LEDGER.read_text(encoding="utf-8")
        LEDGER.write_text(text.replace(LEDGER_MARKER, LEDGER_MARKER + "\n\n" + line, 1),
                          encoding="utf-8")
        print("ledger: entry appended.")
    else:
        print(f"\nAppend to ledger.md (or re-run with --write-ledger):\n  {line}")
    return 0


FLEET_HEADER = """\
# fleet.yml - the workspaces this capability-registry outfits.
# `chandler.py enrol` adds rows; `chandler.py fleet` reports drift across all of them.
# `shared_context` may name a Shared-Context shared-context store root; `fleet` then cross-checks
# its roster so a workspace plugged into the shared brain cannot be quietly missing here.
"""


def load_fleet():
    if not FLEET.is_file():
        return {"workspaces": [], "shared_context": ""}
    try:
        data = yaml.safe_load(FLEET.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        fail(f"fleet.yml is not valid YAML ({e}) - fix it, then re-run")
    if not isinstance(data, dict):
        fail("fleet.yml has an unexpected shape - fix it, then re-run")
    data.setdefault("workspaces", [])
    data.setdefault("shared_context", "")
    return data


def cmd_fleet(_args):
    fleet = load_fleet()
    if not fleet["workspaces"]:
        print("chandler fleet: no workspaces enrolled (use `enrol`).")
    for w in fleet["workspaces"]:
        ws = Path(w["path"])
        if not ws.is_dir():
            print(f"{w['name']}: {w['path']} (unreachable)")
            continue
        drifted = missing = insync = 0
        for name in capabilities():
            m = load_manifest(name)
            for f in m["files"]:
                state, _, _ = file_state(ws, name, f)
                if state == "in-sync":
                    insync += 1
                elif state == "drifted":
                    drifted += 1
                else:
                    missing += 1
        print(f"{w['name']}: {insync} in-sync, {drifted} drifted, {missing} missing "
              f"({w['path']})")
    # Optional composition: cross-check a shared-context store's roster.
    store = fleet.get("shared_context") or ""
    if store:
        roster = Path(store) / "_coordination" / "roster.md"
        if roster.is_file():
            fleet_names = {w["name"] for w in fleet["workspaces"]}
            unenrolled = []
            for line in roster.read_text(encoding="utf-8").splitlines():
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if len(cells) >= 5 and cells[0] not in ("Workspace", "_none yet_") \
                        and cells[0] and not set(cells[0]) <= set("-: ") \
                        and cells[4] == "active" and cells[0] not in fleet_names:
                    unenrolled.append(cells[0])
            if unenrolled:
                print("on the shared-context roster but not enrolled here: "
                      + ", ".join(sorted(unenrolled)))
    return 0


def cmd_enrol(args):
    fleet = load_fleet()
    if any(w["name"] == args.name for w in fleet["workspaces"]):
        print(f"chandler enrol: '{args.name}' already enrolled - nothing to do.")
        return 0
    if not Path(args.path).is_absolute():
        fail(f"--path must be absolute, got {args.path!r}")
    fleet["workspaces"].append({"name": args.name, "path": args.path,
                                "added": datetime.date.today().isoformat()})
    FLEET.write_text(FLEET_HEADER + yaml.safe_dump(fleet, sort_keys=False),
                     encoding="utf-8")
    print(f"chandler enrol: added '{args.name}'.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Capability-Registry capability registry engine.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    sub.add_parser("verify")
    p = sub.add_parser("status")
    p.add_argument("capability", nargs="?", default=None)
    p.add_argument("--workspace", required=True)
    p = sub.add_parser("diff")
    p.add_argument("name")
    p.add_argument("--workspace", required=True)
    p = sub.add_parser("install")
    p.add_argument("name")
    p.add_argument("--workspace", required=True)
    p.add_argument("--yes", action="store_true")
    p = sub.add_parser("pack")
    p.add_argument("name")
    p.add_argument("--from-workspace", required=True)
    p.add_argument("--yes", action="store_true")
    p.add_argument("--write-ledger", action="store_true")
    sub.add_parser("fleet")
    p = sub.add_parser("enrol")
    p.add_argument("--name", required=True)
    p.add_argument("--path", required=True)
    args = ap.parse_args(argv)
    return {"list": cmd_list, "verify": cmd_verify, "status": cmd_status,
            "diff": cmd_diff, "install": cmd_install, "pack": cmd_pack,
            "fleet": cmd_fleet, "enrol": cmd_enrol}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
