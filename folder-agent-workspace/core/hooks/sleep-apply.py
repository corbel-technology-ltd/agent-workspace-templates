#!/usr/bin/env python3
"""Sleep pass, stage 2 of 2 — deterministic validator + atom writer. The model proposes,
this script disposes. No claim reaches a durable layer except through here.

Reads the synthesis output (20_memory/_meta/sleep-claims.json, written by the memory-sleep
skill) against the candidates file (sleep-prep.py), validates every claim, writes the accepted
ones as schema-valid memory-card atoms, then runs the reaper so the new atoms are tiered
immediately.

Validation (homeostasis `sleep_pass.validator_rejects`):
  unsupported_claim          — no support_event_ids, or an id outside the current candidate window
  new_named_entity           — a changed_entity not already known to the store
  untraceable_contradiction  — supersedes-ref that matches no existing atom id
  (plus: bad kind, confidence out of [0,1], assertable edges, empty claim)

A duplicate hash strengthens the existing card with the new sources and touches. Model-supplied
`pivotal` is kept only when a supporting event is principal-authored (`source_type: human`).

Writes:
  20_memory/short-term/<date>_<slug>.md            one atom per accepted claim
  20_memory/subconscious/associations/<slug>.md    one low-weight edge per accepted proposal
                                                   (assertable: false — primes, never asserts)
  20_memory/subconscious/world-model/<YYYY-MM>.md  monthly snapshot of what changed
  20_memory/_meta/sleep-log.md                     append-only accept/reject record
  20_memory/_meta/sleep-state.json                 processed journal filenames + run count

Usage: python3 core/hooks/sleep-apply.py [--root <20_memory>] [--dry-run]
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import sys
from pathlib import Path

import yaml

import reaper as R

KINDS = {"lesson", "procedure", "tool-recipe", "preference", "observation", "decision"}
WORKSPACE = "<<workspace_slug>>"


def slugify(s, n=6):
    words = re.sub(r"[^a-z0-9 ]", "", str(s).lower()).split()
    return "-".join(words[:n]) or "claim"


def content_hash(claim):
    return hashlib.sha1(re.sub(r"\s+", " ", str(claim).strip().lower()).encode()).hexdigest()[:16]


def existing_hashes(root):
    seen = {}
    for layer in R.LAYERS + ["archive"]:
        d = root / layer
        if not d.is_dir():
            continue
        for p in d.rglob("*.md"):
            meta, _ = R.parse_atom(p.read_text()) if p.name.lower() != "readme.md" else ({}, "")
            if isinstance(meta, dict) and meta.get("content_hash"):
                seen[meta["content_hash"]] = (meta.get("id"), p)
    return seen


def existing_atom_ids(root):
    ids = set()
    for layer in R.LAYERS + ["archive"]:
        d = root / layer
        if not d.is_dir():
            continue
        for p in d.rglob("*.md"):
            if p.name.lower() == "readme.md":
                continue
            meta, _ = R.parse_atom(p.read_text())
            if isinstance(meta, dict) and meta.get("id"):
                ids.add(meta["id"])
    return ids


def entity_atom_map(root):
    """entity -> [(relpath, atom_id)] over the live layers, for related-edge derivation."""
    m = {}
    for layer in R.LAYERS:
        d = root / layer
        if not d.is_dir():
            continue
        for p in d.rglob("*.md"):
            if p.name.lower() == "readme.md":
                continue
            meta, _ = R.parse_atom(p.read_text())
            if not (isinstance(meta, dict) and meta.get("id")):
                continue
            ents = (meta.get("who") or []) + (meta.get("where") or [])
            rel = str(p.relative_to(root.parent))
            for e in ents:
                m.setdefault(str(e).strip(), []).append((rel, meta["id"]))
    return m


def derive_related(claim, ent_map, own_id, cap=4):
    """Typed edges to existing atoms that share this claim's entities - the graph Jake described:
    frontmatter carries the interconnections so retrieval can walk edges instead of grepping."""
    seen, out = set(), []
    for e in claim.get("changed_entities") or []:
        for rel, aid in ent_map.get(str(e).strip(), []):
            if aid == own_id or aid in seen:
                continue
            seen.add(aid)
            out.append({"ref": rel, "dimension": "who", "polarity": "complements"})
            if len(out) >= cap:
                return out
    return out


def trust_tier(claim, entries_by_file):
    conf = float(claim.get("confidence", 0))
    trusted = all(entries_by_file.get(f, {}).get("trust") == "trusted"
                  for f in claim.get("support_event_ids", []))
    if not trusted:
        return 2
    if conf >= 0.8:
        return 4
    if conf >= 0.6:
        return 3
    return 2


def validate(claim, entries_by_file, known, atom_ids):
    if not str(claim.get("claim", "")).strip():
        return "empty_claim"
    kind = claim.get("kind", "observation")
    if kind not in KINDS:
        return f"bad_kind:{kind}"
    try:
        conf = float(claim.get("confidence"))
    except (TypeError, ValueError):
        return "bad_confidence"
    if not 0.0 <= conf <= 1.0:
        return "bad_confidence"
    support = claim.get("support_event_ids") or []
    if not support:
        return "unsupported_claim"
    for f in support:
        if str(f) not in entries_by_file:
            return f"unsupported_claim:{f}"
    for e in claim.get("changed_entities") or []:
        if str(e).strip() and str(e).strip() not in known:
            return f"new_named_entity:{e}"
    sup = claim.get("supersedes")
    if sup and sup not in atom_ids:
        return f"untraceable_contradiction:{sup}"
    for edge in claim.get("proposed_edges") or []:
        if edge.get("assertable"):
            return "assertable_edge_without_backing"
    return None


def principal_supported(claim, entries_by_file):
    return any(entries_by_file.get(str(f), {}).get("source_type") == "human"
               for f in claim.get("support_event_ids") or [])


def merge_atom(path, claim, today, entries_by_file):
    meta, body = R.parse_atom(path.read_text())
    support = [str(f) for f in claim["support_event_ids"]]
    sources = list(meta.get("sources") or [])
    touches = list(meta.get("touches") or [])
    for f in support:
        source = f"journal/{f}"
        if source not in sources:
            sources.append(source)
            when = entries_by_file[f].get("when") or today
            touches.append(f"{when}T00:00:00Z")
    meta["sources"] = sources
    meta["touches"] = touches
    meta["trust_tier"] = min(int(meta.get("trust_tier", 2)), trust_tier(claim, entries_by_file))
    meta["last_verified"] = today
    path.write_text(R.dump_atom(meta, body))


def atom_frontmatter(claim, today, tier, h, entries_by_file):
    support = claim["support_event_ids"]
    whens = sorted({entries_by_file.get(f, {}).get("when") or today for f in support})
    who = claim.get("who") or sorted({e for f in support for e in entries_by_file.get(f, {}).get("who", [])})
    where = claim.get("where") or sorted({e for f in support for e in entries_by_file.get(f, {}).get("where", [])})
    meta = {
        "id": f"{WORKSPACE}.atom.{slugify(claim['claim'])}",
        "type": claim.get("kind", "observation"),
        "class": "normative" if claim.get("kind") == "preference" else "observational",
        "layer": "short-term",
        "who": who, "what": str(claim["claim"]).strip()[:300],
        "where": where, "when": whens[-1],
        "why": claim.get("why") or [], "how": claim.get("how") or [],
        "sources": [f"journal/{f}" for f in support],
        "trust_tier": tier,
        "importance": round(float(claim.get("importance", 0.5)), 2),
        "assertable": True,
        "touches": [f"{w}T00:00:00Z" for w in whens],
        "retrieval_count": 0,
        "pivotal": bool(claim.get("pivotal", False)),
        "do_not_drop": False,
        "status": "current",
        "last_verified": today,
        # preferences persist until superseded; everything else decays on the layer
        # default (homeostasis decay.default_valid_for) unless the claim says otherwise
        "valid_for": claim.get("valid_for") or (
            "until-superseded" if claim.get("kind") == "preference" else None),
        "content_hash": h,
    }
    if meta["valid_for"] is None:
        meta.pop("valid_for")
    if claim.get("decision_impact"):
        meta["decision_impact"] = True
    if claim.get("supersedes"):
        meta["supersedes"] = claim["supersedes"]
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    base = Path(os.environ.get("<<WORKSPACE_ROOT_ENV>>") or Path(__file__).resolve().parents[2])
    root = Path(a.root) if a.root else base / "20_memory"
    meta_dir = root / "_meta"
    today = datetime.date.today().isoformat()

    cands = json.loads((meta_dir / "sleep-candidates.json").read_text())
    claims_doc = json.loads((meta_dir / "sleep-claims.json").read_text())
    if claims_doc.get("run_id") != cands.get("run_id"):
        raise ValueError("sleep-claims.json run_id does not match current sleep-candidates.json")
    claims = claims_doc.get("claims") or []
    known = set(cands.get("known_entities") or [])
    entries_by_file = {e["file"]: e for e in cands.get("entries", [])}
    atom_ids = existing_atom_ids(root)
    seen_hashes = existing_hashes(root)

    ent_map = entity_atom_map(root)
    accepted, rejected, merged, pivotal_stripped = [], [], [], []
    pending = {}
    for raw in claims:
        c = dict(raw)
        why = validate(c, entries_by_file, known, atom_ids)
        if why:
            rejected.append((c, why))
            continue
        if c.get("pivotal") and not principal_supported(c, entries_by_file):
            c["pivotal"] = False
            pivotal_stripped.append(c)
        h = content_hash(c["claim"])
        if h in seen_hashes:
            target_id, path = seen_hashes[h]
            if path is None:
                target = pending[h]
                for f in c["support_event_ids"]:
                    if f not in target["support_event_ids"]:
                        target["support_event_ids"].append(f)
            merged.append((c, target_id, path))
            continue
        pending[h] = c
        seen_hashes[h] = (f"{WORKSPACE}.atom.{slugify(c['claim'])}", None)
        accepted.append((c, h))

    written, edges_written = [], 0
    if not a.dry_run:
        st = root / "short-term"
        st.mkdir(parents=True, exist_ok=True)
        for c, h in accepted:
            tier = trust_tier(c, entries_by_file)
            meta = atom_frontmatter(c, today, tier, h, entries_by_file)
            rel_edges = derive_related(c, ent_map, meta["id"])
            if rel_edges:
                meta["related"] = rel_edges
            body = (f"\n\n# {meta['what']}\n\n{str(c.get('claim')).strip()}\n\n"
                    f"Synthesised by the sleep pass on {today} from "
                    f"{len(c['support_event_ids'])} journal event(s).\n")
            fname = f"{today}_{slugify(c['claim'])}.md"
            path = st / fname
            n = 1
            while path.exists():
                n += 1
                path = st / f"{today}_{slugify(c['claim'])}-{n}.md"
            path.write_text(R.dump_atom(meta, body))
            written.append(path.name)
            seen_hashes[h] = meta["id"]
            # same-run atoms can link to each other too
            for e in (meta.get("who") or []) + (meta.get("where") or []):
                ent_map.setdefault(str(e).strip(), []).append(
                    (str(path.relative_to(root.parent)), meta["id"]))

            for edge in c.get("proposed_edges") or []:
                ed = root / "subconscious" / "associations"
                ed.mkdir(parents=True, exist_ok=True)
                eslug = slugify(f"{edge.get('from')} {edge.get('relation')} {edge.get('to')}", 8)
                ep = ed / f"{eslug}.md"
                if ep.exists():
                    emeta, ebody = R.parse_atom(ep.read_text())
                    emeta["weight"] = round(float(emeta.get("weight", 0.1)) + 0.1, 2)
                    emeta["touches"] = (emeta.get("touches") or []) + [f"{today}T00:00:00Z"]
                    emeta["last_verified"] = today
                    ep.write_text(R.dump_atom(emeta, ebody))
                else:
                    emeta = {
                        "id": f"{WORKSPACE}.atom.assoc-{eslug}",
                        "type": "association", "class": "observational",
                        "layer": "subconscious",
                        "who": [], "what": f"{edge.get('from')} -[{edge.get('relation')}]-> {edge.get('to')}",
                        "where": [], "when": today, "why": [], "how": [],
                        "sources": [f"journal/{f}" for f in c["support_event_ids"]],
                        "trust_tier": 2, "importance": 0.2,
                        "assertable": False, "weight": 0.1,
                        "touches": [f"{today}T00:00:00Z"],
                        "status": "current", "last_verified": today,
                        "valid_for": "until-superseded",
                        "content_hash": content_hash(f"assoc {eslug}"),
                    }
                    ep.write_text(R.dump_atom(
                        emeta, f"\n\n# Association: {emeta['what']}\n\nLow-weight prior. "
                               "Primes retrieval; never asserted as fact.\n"))
                edges_written += 1

        for c, target_id, path in merged:
            if path is not None:
                merge_atom(path, c, today, entries_by_file)

        # monthly world-model snapshot
        wm = root / "subconscious" / "world-model"
        wm.mkdir(parents=True, exist_ok=True)
        month = today[:7]
        snap = wm / f"{month}.md"
        ents = sorted({e for c, _ in accepted for e in (c.get("changed_entities") or [])})
        block = (f"\n## Sleep run {today}\n\n"
                 f"- window: {cands['window'].get('from')} .. {cands['window'].get('to')} "
                 f"({cands['window'].get('count')} entries)\n"
                 f"- accepted claims: {len(accepted)} | rejected: {len(rejected)} | "
                 f"merged: {len(merged)} | edges: {edges_written}\n"
                 f"- changed entities: {', '.join(ents) if ents else '(none)'}\n"
                 f"- new atoms: {', '.join(written) if written else '(none)'}\n")
        if snap.exists():
            snap.write_text(snap.read_text() + block)
        else:
            head = {
                "id": f"{WORKSPACE}.atom.world-model-{month}",
                "type": "prior", "class": "observational", "layer": "subconscious",
                "who": [], "what": f"World-model snapshot for {month}",
                "where": [], "when": today, "why": [], "how": [],
                "sources": [f"journal/{e['file']}" for e in cands.get("entries", [])[:5]] or ["journal/"],
                "trust_tier": 3, "importance": 0.3, "assertable": False,
                "touches": [f"{today}T00:00:00Z"], "status": "current",
                "last_verified": today, "valid_for": "permanent",
                "content_hash": content_hash(f"world-model {month}"),
            }
            snap.write_text(R.dump_atom(head, f"\n\n# World model — {month}\n" + block))

        # marker + log
        old_state = (json.loads((meta_dir / "sleep-state.json").read_text())
                     if (meta_dir / "sleep-state.json").exists() else {})
        processed = set(old_state.get("processed") or [])
        processed.update(entries_by_file)
        state = {"processed": sorted(processed), "last_run": today,
                 "runs": old_state.get("runs", 0) + 1}
        (meta_dir / "sleep-state.json").write_text(json.dumps(state, indent=2))
        log = meta_dir / "sleep-log.md"
        lines = [f"\n## {today}\n",
                 f"- accepted {len(accepted)}, rejected {len(rejected)}, merged {len(merged)}, "
                 f"edges {edges_written}\n"]
        for c in pivotal_stripped:
            lines.append("- pivotal stripped (no principal-authored support): "
                         f"{str(c.get('claim', ''))[:120]}\n")
        for c, target_id, path in merged:
            lines.append(f"- MERGED into {target_id}: {str(c.get('claim', ''))[:120]}\n")
        for c, why in rejected:
            lines.append(f"- REJECTED ({why}): {str(c.get('claim',''))[:120]}\n")
        log.write_text((log.read_text() if log.exists() else "# Sleep log\n") + "".join(lines))

    print(f"sleep-apply: accepted {len(accepted)}, rejected {len(rejected)}, merged {len(merged)}, "
          f"edges {edges_written}{' (dry-run: nothing written)' if a.dry_run else ''}")
    for c, why in rejected:
        print(f"  rejected [{why}]: {str(c.get('claim',''))[:100]}")

    if not a.dry_run:
        cfg = yaml.safe_load((root / "homeostasis.yml").read_text())
        rep = R.reap(root, datetime.date.today(), cfg)
        print(f"reaper: {rep}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"sleep-apply: failed ({e})", file=sys.stderr)
        sys.exit(1)
