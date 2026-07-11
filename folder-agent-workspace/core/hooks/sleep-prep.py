#!/usr/bin/env python3
"""Sleep pass, stage 1 of 2 — deterministic candidate preparation. No LLM.

Gathers the journal entries not yet consolidated (everything after the last sleep marker),
bounded by homeostasis `sleep_pass.max_changed_items_per_run`, and emits a machine-readable
candidates file the synthesis step works from:

    20_memory/_meta/sleep-candidates.json
      window          — which journal files this run covers
      entries         — id / what / who / where / when / trust per entry
      entities        — recurrence per entity (mentions + distinct days)
      cooccurrence    — entity pairs that appear together, with counts
      known_entities  — every entity already named in the journal or an existing atom;
                        the validator (sleep-apply.py) rejects claims that invent new ones

Spec: 60_workflows/memory-sleep.md. Driven by the memory-sleep skill; safe to run by hand.
Usage: python3 core/hooks/sleep-prep.py [--root <20_memory>] [--all]  (--all ignores the marker)
"""
import argparse
import datetime
import itertools
import json
import os
import sys
from pathlib import Path

import yaml

from reaper import parse_atom, LAYERS  # same-dir import; shared parsing


def _listify(v):
    if v is None:
        return []
    if isinstance(v, str):
        return [v]
    return [str(x) for x in v]


def load_marker(meta_dir):
    f = meta_dir / "sleep-state.json"
    if f.exists():
        try:
            return json.loads(f.read_text())
        except Exception:
            pass
    return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--all", action="store_true", help="ignore the sleep marker; consider every entry")
    a = ap.parse_args()
    base = Path(os.environ.get("<<WORKSPACE_ROOT_ENV>>") or Path(__file__).resolve().parents[2])
    root = Path(a.root) if a.root else base / "20_memory"
    meta_dir = root / "_meta"
    meta_dir.mkdir(parents=True, exist_ok=True)

    cfg = yaml.safe_load((root / "homeostasis.yml").read_text())
    cap = int(cfg.get("sleep_pass", {}).get("max_changed_items_per_run", 50))

    marker = {} if a.all else load_marker(meta_dir)
    last = marker.get("last_processed", "")

    # Entries only: skip the README and anything without machine frontmatter. Crucial for the
    # marker too — "README.md" sorts AFTER date-named entries, so staging it would advance
    # last_processed past every future entry and silently end all future sleeps.
    journal = [p for p in sorted((root / "journal").glob("*.md"))
               if p.name.lower() != "readme.md" and parse_atom(p.read_text())[0]]
    fresh = [p for p in journal if p.name > last][:cap]
    dropped = max(0, len([p for p in journal if p.name > last]) - cap)

    entries, entity_days, entity_count = [], {}, {}
    known = set()
    for p in journal:  # known-entity universe comes from the WHOLE journal, not just the window
        meta, _ = parse_atom(p.read_text())
        if not isinstance(meta, dict):
            continue
        ents = _listify(meta.get("who")) + _listify(meta.get("where"))
        known.update(e.strip() for e in ents if e and str(e).strip())

    for layer in LAYERS:  # plus every entity already carried by an atom
        d = root / layer
        if not d.is_dir():
            continue
        for p in d.rglob("*.md"):
            if p.name.lower() == "readme.md":
                continue
            meta, _ = parse_atom(p.read_text())
            if isinstance(meta, dict):
                known.update(str(e).strip() for e in
                             _listify(meta.get("who")) + _listify(meta.get("where")) if str(e).strip())

    pair_count = {}
    for p in fresh:
        meta, _ = parse_atom(p.read_text())
        if not isinstance(meta, dict):
            continue
        who = [str(e).strip() for e in _listify(meta.get("who")) if str(e).strip()]
        where = [str(e).strip() for e in _listify(meta.get("where")) if str(e).strip()]
        when = str(meta.get("when", ""))[:10]
        entries.append({
            "file": p.name,
            "id": meta.get("id") or p.stem,
            "what": str(meta.get("what", ""))[:400],
            "who": who, "where": where, "when": when,
            "trust": meta.get("trust", ""),
            "source_type": meta.get("source_type", ""),
        })
        ents = sorted(set(who + where))
        for e in ents:
            entity_count[e] = entity_count.get(e, 0) + 1
            entity_days.setdefault(e, set()).add(when)
        for x, y in itertools.combinations(ents, 2):
            pair_count[(x, y)] = pair_count.get((x, y), 0) + 1

    out = {
        "generated": datetime.date.today().isoformat(),
        "window": {"from": fresh[0].name if fresh else None,
                   "to": fresh[-1].name if fresh else None,
                   "count": len(fresh), "over_cap_dropped": dropped},
        "entries": entries,
        "entities": {e: {"mentions": entity_count[e], "distinct_days": len(entity_days[e])}
                     for e in sorted(entity_count)},
        "cooccurrence": sorted(([x, y, c] for (x, y), c in pair_count.items() if c >= 2),
                               key=lambda t: -t[2]),
        "known_entities": sorted(known),
    }
    (meta_dir / "sleep-candidates.json").write_text(json.dumps(out, indent=2))
    print(f"sleep-prep: {len(fresh)} entries staged ({dropped} beyond cap), "
          f"{len(entity_count)} entities, {len(out['cooccurrence'])} recurring pairs "
          f"-> {meta_dir / 'sleep-candidates.json'}")
    if not fresh:
        print("sleep-prep: nothing new since the last sleep — no synthesis needed.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"sleep-prep: failed ({e})", file=sys.stderr)
        sys.exit(1)
