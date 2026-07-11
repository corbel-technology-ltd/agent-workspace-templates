#!/usr/bin/env python3
"""Memory reaper — deterministic fast consolidation pass.

Spec: 60_workflows/memory-reaper.md. Set-points: 20_memory/homeostasis.yml. No LLM. Idempotent.
A run is reproducible from (journal, atoms, --as-of, set-points). The deep LLM "sleep" pass that
synthesises new atoms from journal prose is separate (core/hooks/sleep-prep.py + sleep-apply.py,
driven by the memory-sleep skill); this pass does membership, decay/validity, supersession,
quarantine, tiering and the build marker over the existing atom set.

Two phases, one plan, one churn gate:
  STRUCTURAL — quarantine sourceless atoms; supersede on journal corrections/retractions and
               content-hash collisions (first-writer-wins); archive expired atoms.
  MEMBERSHIP — ACT-R activation over each surviving atom, then hysteresis layer moves:
               short-term -> working (enter >= short_term_enter, budgeted, hottest first)
               working    -> short-term (exit  <  short_term_exit)
               short-term -> long-term (enter >= long_term_enter AND a promotion signal)
               long-term  -> archive   (below long_term_exit for N consecutive months)
               short-term -> archive   (over budget; coldest non-pivotal first)
               subconscious is never moved here (sleep-managed; it primes, it does not assert).
Pivotal / do_not_drop atoms are never demoted, archived, or expired. Every atom gets its
activation_base and hot/warm/cold tier annotated each run.

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
    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}, text  # not machine-frontmatter (prose doc, legacy file) — treat as non-atom
    return (meta if isinstance(meta, dict) else {}), parts[2]


def dump_atom(meta, body):
    return "---\n" + yaml.safe_dump(meta, sort_keys=False, allow_unicode=True) + "---" + body


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
    if meta.get("surprise"):
        W += w.get("surprise", 0.0)
    if meta.get("conflict"):
        W += w.get("conflict", 0.0)
    if meta.get("status") in ("stale", "superseded"):
        W += w.get("obsolete", 0.0)
    return base + W


def is_expired(meta, as_of, cfg):
    if meta.get("pivotal") or meta.get("do_not_drop"):
        return False  # the non-drop invariant: bypass the decay loop entirely
    # working/ is a hot PROJECTION of short-term, not a home: an atom sitting there keeps
    # short-term expiry semantics (cooling demotes it; residence must never archive it faster)
    layer = meta.get("layer", "short-term")
    if layer == "working":
        layer = "short-term"
    vf = meta.get("valid_for") or cfg["decay"]["default_valid_for"].get(layer)
    td = parse_valid_for(vf)
    lv = meta.get("last_verified")
    if td is None or not lv:
        return False
    return as_of > _to_date(lv) + td


def promotion_ready(meta, as_of, cfg):
    """Short-term -> long-term needs a promotion SIGNAL on top of raw activation."""
    prom = cfg.get("promotion", {})
    if meta.get("pivotal") and prom.get("explicit_pivotal", True):
        return True
    if int(meta.get("trust_tier", 0) or 0) < int(prom.get("min_trust_for_long", 3)):
        return False
    if meta.get("decision_impact") and prom.get("decision_impact_promotes", True):
        return True
    touches = meta.get("touches") or []
    recent_days = set()
    for t in touches:
        try:
            d = _to_date(t)
        except Exception:
            continue
        if 0 <= (as_of - d).days <= 60:
            recent_days.add(d)
    if len(recent_days) >= int(prom.get("min_recurrence_days", 3)):
        return True
    if int(meta.get("retrieval_count", 0) or 0) >= int(prom.get("min_retrievals_90d", 4)):
        return True
    return False


def _protected(meta):
    return bool(meta.get("pivotal") or meta.get("do_not_drop"))


def reap(memory_root, as_of, cfg, dry_run=False):
    memory_root = Path(memory_root)
    atoms = []  # [path, meta, body, layer]
    for layer in LAYERS:
        d = memory_root / layer
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*.md")):
            if p.name.lower() == "readme.md":
                continue
            meta, body = parse_atom(p.read_text())
            if not isinstance(meta, dict) or not meta:
                continue  # not an atom (plain doc) — leave untouched
            meta.setdefault("layer", layer)
            atoms.append([p, meta, body, layer])

    # journal-driven supersession (corrections/retractions)
    superseded_by = {}
    jdir = memory_root / "journal"
    if jdir.is_dir():
        for p in sorted(jdir.glob("*.md")):
            jmeta, _ = parse_atom(p.read_text())
            if not isinstance(jmeta, dict):
                continue
            jid = jmeta.get("id") or p.stem
            for key in ("retracts", "corrects"):
                if jmeta.get(key):
                    superseded_by[jmeta[key]] = jid

    # PHASE 1 — structural plan (one action per atom); hash dedup is first-writer-wins
    plan = []
    structural = set()
    seen_hash = {}
    for i, (p, meta, body, layer) in enumerate(atoms):
        if not meta.get("sources"):
            plan.append(("quarantine", i, None))
            structural.add(i)
            continue
        if meta.get("status") != "superseded" and meta.get("id") in superseded_by:
            plan.append(("supersede", i, superseded_by[meta["id"]]))
            structural.add(i)
            continue
        h = meta.get("content_hash")
        if h:
            if h in seen_hash and meta.get("status") != "superseded":
                plan.append(("supersede", i, atoms[seen_hash[h]][1].get("id")))
                structural.add(i)
                continue
            seen_hash.setdefault(h, i)
        if is_expired(meta, as_of, cfg):
            plan.append(("archive", i, None))
            structural.add(i)

    # PHASE 2 — membership: activation + hysteresis moves over the survivors
    th = cfg.get("thresholds", {})
    budgets = cfg.get("budgets", {})
    st_enter = float(th.get("short_term_enter", 1.6))
    st_exit = float(th.get("short_term_exit", 1.1))
    lt_enter = float(th.get("long_term_enter", 2.4))
    lt_exit = float(th.get("long_term_exit", 1.5))
    archive_months = int(th.get("long_term_months_below_exit_before_archive", 3))

    acts = {}
    dirty = set()       # frontmatter mutated in place; must persist even if annotation is a no-op
    working_pool = []   # (activation, i) candidates entitled to sit in working/
    for i, (p, meta, body, layer) in enumerate(atoms):
        if i in structural or layer == "subconscious":
            continue
        A = acts[i] = activation(meta, as_of, cfg)
        if layer == "long-term":
            if A < lt_exit and not _protected(meta):
                since = meta.get("below_exit_since")
                if not since:
                    meta["below_exit_since"] = str(as_of)   # start the archive clock
                    dirty.add(i)
                elif (as_of - _to_date(since)).days >= archive_months * 30:
                    plan.append(("archive", i, None))
                    structural.add(i)
            elif meta.get("below_exit_since"):
                meta.pop("below_exit_since", None)          # recovered; clear the clock
                dirty.add(i)
        elif layer == "short-term":
            # pivotal always promotes (homeostasis promotion.explicit_pivotal); everything
            # else needs raw activation over the bar AND a promotion signal
            if (A >= lt_enter or meta.get("pivotal")) and promotion_ready(meta, as_of, cfg):
                plan.append(("move", i, "long-term"))
            elif A >= st_enter:
                working_pool.append((A, i))
        elif layer == "working":
            if A < st_exit and not _protected(meta):
                plan.append(("move", i, "short-term"))
            else:
                working_pool.append((A, i))

    # working/ is the budgeted hot set: hottest first, overflow returns to short-term
    max_working = int(budgets.get("working_max_items", 8))
    working_pool.sort(key=lambda t: (-t[0], atoms[t[1]][0].name))
    planned_moves = {i for a, i, x in [(a, i, x) for a, i, x in plan] if a == "move"}
    kept = 0
    for A, i in working_pool:
        p, meta, body, layer = atoms[i]
        if kept < max_working:
            kept += 1
            if layer == "short-term" and i not in planned_moves:
                plan.append(("move", i, "working"))
        elif layer == "working":
            plan.append(("move", i, "short-term"))

    # short-term budget: archive the coldest unprotected overflow (skip atoms already moving)
    moving = {i for a, i, x in plan if a == "move"}
    st_max = int(budgets.get("short_term_max_items", 200))
    st_atoms = [(acts.get(i, -10.0), i) for i, (p, m, b, l) in enumerate(atoms)
                if l == "short-term" and i not in structural and i not in moving]
    if len(st_atoms) > st_max:
        st_atoms.sort(key=lambda t: t[0])
        excess = len(st_atoms) - st_max
        for A, i in st_atoms:
            if excess <= 0:
                break
            if not _protected(atoms[i][1]):
                plan.append(("archive", i, None))
                structural.add(i)
                excess -= 1

    total = len(atoms)
    changed = len(plan)
    # The circuit-breaker guards against destructive rewrites (quarantine/archive/supersede).
    # Hysteresis layer MOVES are the mechanism working as designed and never trip it — otherwise
    # the first post-sleep promotion wave would freeze the store.
    destructive = sum(1 for a, i, x in plan if a != "move")
    stc = cfg["stability"]
    frozen = total >= stc.get("min_atoms_for_check", 8) and destructive * 100 > stc["churn_freeze_pct"] * total
    report = {"as_of": str(as_of), "total": total, "changed": changed, "frozen": frozen,
              "quarantined": 0, "archived": 0, "superseded": 0, "moved": 0}

    if frozen:
        if not dry_run:
            rv = memory_root / "_review"
            rv.mkdir(parents=True, exist_ok=True)
            (rv / "churn-alert.md").write_text(
                f"# Churn alert\n\nReaper aborted on {as_of}: {changed}/{total} atoms "
                f"({changed * 100 // total}%) would change, over churn_freeze_pct="
                f"{stc['churn_freeze_pct']}%. No changes applied; inspect before re-running.\n")
        return report

    if dry_run:
        return report

    handled = set()
    for action, i, extra in plan:
        p, meta, body, layer = atoms[i]
        handled.add(i)
        if action == "quarantine":
            _move(p, memory_root / "_quarantine" / p.name)
            report["quarantined"] += 1
        elif action == "archive":
            meta["activation_base"] = round(acts.get(i, -10.0), 3)
            _annotate(meta, acts.get(i), st_enter, st_exit)
            p.write_text(dump_atom(meta, body))
            _move(p, memory_root / "archive" / p.name)
            report["archived"] += 1
        elif action == "supersede":
            meta["status"] = "superseded"
            meta["superseded_by"] = extra
            p.write_text(dump_atom(meta, body))
            report["superseded"] += 1
        elif action == "move":
            meta["layer"] = extra
            _annotate(meta, acts.get(i), st_enter, st_exit)
            p.write_text(dump_atom(meta, body))
            _move(p, memory_root / extra / p.name)
            report["moved"] += 1

    # annotation pass: keep activation/tier fresh on every remaining atom
    for i, (p, meta, body, layer) in enumerate(atoms):
        if i in handled or layer == "subconscious":
            continue
        new = dict(meta)
        _annotate(new, acts.get(i), st_enter, st_exit)
        if new != meta or i in dirty:
            _annotate(meta, acts.get(i), st_enter, st_exit)
            p.write_text(dump_atom(meta, body))

    _write_build(memory_root, as_of, report)
    return report


def _annotate(meta, A, st_enter, st_exit):
    if A is None:
        return
    meta["activation_base"] = round(A, 3)
    meta["tier"] = "hot" if A >= st_enter else ("warm" if A >= st_exit else "cold")


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
        f"| superseded | {report['superseded']} |\n| moved | {report['moved']} |\n"
        f"| frozen | {report['frozen']} |\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--root", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if not a.root:
        # dormancy gate applies only to the workspace's own store; an explicit --root
        # (tests, tooling) means the caller knows what it is operating on
        _root = Path(os.environ.get("<<WORKSPACE_ROOT_ENV>>") or Path(__file__).resolve().parents[2])
        if (_root / ".uninitialised").exists():
            return  # not onboarded yet — reaper stays dormant (no build marker / atom writes)
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
