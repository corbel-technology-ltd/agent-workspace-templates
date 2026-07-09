#!/usr/bin/env python3
"""Memory reaper — deterministic fast consolidation pass.

Spec: 60_workflows/memory-reaper.md. Set-points: 20_memory/homeostasis.yml. No LLM. Idempotent.
A run is reproducible from (journal, atoms, --as-of, set-points). The deep LLM "sleep" pass that
synthesises new atoms from journal prose is separate and deferred; this pass does membership,
decay/validity, supersession, quarantine, tiering and the build marker over the existing atom set.

Usage: python3 core/hooks/reaper.py [--as-of YYYY-MM-DD] [--root <20_memory>] [--dry-run]
Neutral hook contract (see core/RUNTIMES.md): no stdin payload; run it at session end or by hand.
The workspace root defaults to <<WORKSPACE_ROOT_ENV>> env var if set, else two levels up from here.
"""
import argparse
import datetime
import math
import os
import sys
from pathlib import Path

import yaml

LAYERS = ["working", "short-term", "long-term", "subconscious"]
WORKSPACE = "<<workspace_slug>>"   # lowercase handle for the build-marker id


def parse_atom(text):
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    return (yaml.safe_load(parts[1]) or {}), parts[2]


def dump_atom(meta, body):
    return "---\n" + yaml.safe_dump(meta, sort_keys=False) + "---" + body


def _to_date(v):
    if isinstance(v, datetime.datetime):
        return v.date()
    if isinstance(v, datetime.date):
        return v
    return datetime.date.fromisoformat(str(v)[:10])


def parse_valid_for(s):
    """timedelta for 'Nd'; None for permanent / until-superseded / unknown."""
    s = str(s or "").strip()
    if s.endswith("d") and s[:-1].isdigit():
        return datetime.timedelta(days=int(s[:-1]))
    return None


def activation(meta, as_of, cfg):
    act = cfg["activation"]
    decay = act["decay"]
    w = act["weights"]
    touches = (meta.get("touches") or [])[-act.get("touches_window", 12):]
    s = sum((max((as_of - _to_date(t)).days, 0) + 1) ** (-decay) for t in touches)
    base = math.log(s) if s > 0 else -10.0
    W = float(meta.get("importance", 0.0)) * w.get("importance", 0.0)
    W += (float(meta.get("trust_tier", 0)) / 5.0) * w.get("trust", 0.0)
    if meta.get("decision_impact"):
        W += w.get("decision_impact", 0.0)
    return base + W


def is_expired(meta, as_of, cfg):
    if meta.get("pivotal") or meta.get("do_not_drop"):
        return False  # the non-drop invariant: bypass the decay loop entirely
    vf = meta.get("valid_for") or cfg["decay"]["default_valid_for"].get(meta.get("layer", "short-term"))
    td = parse_valid_for(vf)
    lv = meta.get("last_verified")
    if td is None or not lv:
        return False
    return as_of > _to_date(lv) + td


def reap(memory_root, as_of, cfg, dry_run=False):
    memory_root = Path(memory_root)
    atoms = []  # [path, meta, body, layer]
    for layer in LAYERS:
        d = memory_root / layer
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            if p.name.lower() == "readme.md":
                continue
            meta, body = parse_atom(p.read_text())
            meta.setdefault("layer", layer)
            atoms.append([p, meta, body, layer])

    # journal-driven supersession (corrections/retractions)
    superseded_by = {}
    jdir = memory_root / "journal"
    if jdir.is_dir():
        for p in sorted(jdir.glob("*.md")):
            jmeta, _ = parse_atom(p.read_text())
            jid = jmeta.get("id") or p.stem
            for key in ("retracts", "corrects"):
                if jmeta.get(key):
                    superseded_by[jmeta[key]] = jid

    # plan structural changes (one per atom); content-hash dedup is first-writer-wins
    plan = []
    seen_hash = {}
    for i, (p, meta, body, layer) in enumerate(atoms):
        if not meta.get("sources"):
            plan.append(("quarantine", i, None))
            continue
        if meta.get("status") != "superseded" and meta.get("id") in superseded_by:
            plan.append(("supersede", i, superseded_by[meta["id"]]))
            continue
        h = meta.get("content_hash")
        if h:
            if h in seen_hash and meta.get("status") != "superseded":
                plan.append(("supersede", i, atoms[seen_hash[h]][1].get("id")))
                continue
            seen_hash.setdefault(h, i)
        if is_expired(meta, as_of, cfg):
            plan.append(("archive", i, None))

    total = len(atoms)
    changed = len(plan)
    st = cfg["stability"]
    frozen = total >= st.get("min_atoms_for_check", 8) and changed * 100 > st["churn_freeze_pct"] * total
    report = {"as_of": str(as_of), "total": total, "changed": changed, "frozen": frozen,
              "quarantined": 0, "archived": 0, "superseded": 0}

    if frozen:
        if not dry_run:
            rv = memory_root / "_review"
            rv.mkdir(parents=True, exist_ok=True)
            (rv / "churn-alert.md").write_text(
                f"# Churn alert\n\nReaper aborted on {as_of}: {changed}/{total} atoms "
                f"({changed * 100 // total}%) would change, over churn_freeze_pct="
                f"{st['churn_freeze_pct']}%. No changes applied; inspect before re-running.\n")
        return report

    if dry_run:
        return report

    for action, i, extra in plan:
        p, meta, body, layer = atoms[i]
        if action == "quarantine":
            _move(p, memory_root / "_quarantine" / p.name)
            report["quarantined"] += 1
        elif action == "archive":
            _move(p, memory_root / "archive" / p.name)
            report["archived"] += 1
        elif action == "supersede":
            meta["status"] = "superseded"
            meta["superseded_by"] = extra
            p.write_text(dump_atom(meta, body))
            report["superseded"] += 1
    _write_build(memory_root, as_of, report)
    return report


def _move(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    src.rename(dst)


def _write_build(memory_root, as_of, report):
    d = memory_root / "_meta"
    d.mkdir(parents=True, exist_ok=True)
    (d / "build.md").write_text(
        f"---\nid: {WORKSPACE}.memory.atoms.build\nname: Reaper build marker\ntype: state\n"
        "layer: C1\nstatus: current\nowner: shared\n---\n\n# Reaper build marker\n\n"
        "The last memory-reaper run. Deterministic: reproducible from journal, atoms, --as-of and "
        "set-points. Written by `core/hooks/reaper.py`.\n\n"
        "| Field | Value |\n|---|---|\n"
        f"| last_run | {as_of} |\n| as_of | {as_of} |\n| total_atoms | {report['total']} |\n"
        f"| quarantined | {report['quarantined']} |\n| archived | {report['archived']} |\n"
        f"| superseded | {report['superseded']} |\n| frozen | {report['frozen']} |\n")


def main():
    _root = Path(os.environ.get("<<WORKSPACE_ROOT_ENV>>") or Path(__file__).resolve().parents[2])
    if (_root / ".uninitialised").exists():
        return  # not onboarded yet — reaper stays dormant (no build marker / atom writes)
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--root", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    try:
        if a.root:
            root = Path(a.root)
        else:
            base = Path(os.environ.get("<<WORKSPACE_ROOT_ENV>>") or Path(__file__).resolve().parents[2])
            root = base / "20_memory"
        as_of = datetime.date.fromisoformat(a.as_of) if a.as_of else datetime.date.today()
        cfg = yaml.safe_load((root / "homeostasis.yml").read_text())
        print(reap(root, as_of, cfg, dry_run=a.dry_run))
    except Exception as e:  # hook-safe: a reaper failure must never disrupt session end
        print(f"reaper: skipped ({e})", file=sys.stderr)


if __name__ == "__main__":
    main()
