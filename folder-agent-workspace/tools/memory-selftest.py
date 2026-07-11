#!/usr/bin/env python3
"""memory-selftest.py — proves the memory loop actually works, end to end, deterministically.

Builds a throwaway memory root in a temp dir, seeds synthetic journal entries, then exercises the
full pipeline exactly as a live workspace would:

  1. sleep-prep    -> candidates staged, entities + recurrence extracted, known-entity universe built
  2. sleep-apply   -> claims bound to that window; trust and pivotal ceilings enforced; good claims
                      written; unsupported/invented claims rejected
  3. sleep replay  -> a backfilled entry is staged; duplicate evidence strengthens the existing card
  4. reaper        -> journal and atom supersession, tiering, quarantine and hysteresis all hold
  5. reaper (+40d) -> cooled atoms decay while preferences and pivotal memory survive

Run from the member root:  python3 tools/memory-selftest.py
Exit 0 = every assertion green. Registered as a member gate in the family check.
"""
import datetime
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

MEMBER = Path(__file__).resolve().parents[1]
HOOKS = MEMBER / "core" / "hooks"
TODAY = datetime.date.today()


def day(offset):
    return (TODAY - datetime.timedelta(days=offset)).isoformat()


FAILS = []


def check(name, cond, detail=""):
    tag = "ok" if cond else "FAIL"
    print(f"  [{tag}] {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


def journal_entry(when, ident, what, who, where, trust="trusted", source_type="system",
                  kind="observation", corrects=None, retracts=None):
    extra = ((f"corrects: {corrects}\n" if corrects else "")
             + (f"retracts: {retracts}\n" if retracts else ""))
    return (f"---\nid: {ident}\ntype: {kind}\nwho: [{', '.join(who)}]\n"
            f"what: \"{what}\"\nwhere: [{', '.join(where)}]\nwhen: {when}T12:00:00Z\n"
            f"source_type: {source_type}\ntrust: {trust}\n{extra}---\n\n# {what}\n")


def run(script, *args):
    r = subprocess.run([sys.executable, str(HOOKS / script), *args],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout, r.stderr)
    return r


def atom_records(root):
    records = []
    for layer in ["working", "short-term", "long-term", "archive"]:
        for path in (root / layer).glob("*.md"):
            parts = path.read_text().split("---", 2)
            if len(parts) == 3:
                records.append((path, yaml.safe_load(parts[1]) or {}))
    return records


def find_atom(root, text):
    text = text.lower()
    for path, meta in atom_records(root):
        if text in str(meta.get("what", "")).lower():
            return path, meta
    return None, {}


def write_atom(root, filename, ident, what, source, supersedes=None):
    meta = {
        "id": ident, "type": "observation", "layer": "short-term",
        "who": ["ada"], "what": what, "where": ["opal"], "when": day(0),
        "why": [], "how": [], "sources": [f"journal/{source}"],
        "trust_tier": 3, "importance": 0.2, "assertable": True,
        "touches": [f"{day(0)}T00:00:00Z"], "retrieval_count": 0,
        "pivotal": False, "do_not_drop": False, "status": "current",
        "last_verified": day(0), "valid_for": "until-superseded",
        "content_hash": ident,
    }
    if supersedes:
        meta["supersedes"] = supersedes
    path = root / "short-term" / filename
    path.write_text("---\n" + yaml.safe_dump(meta, sort_keys=False) + f"---\n\n# {what}\n")
    return path


def main():
    tmp = Path(tempfile.mkdtemp(prefix="memtest-"))
    root = tmp / "20_memory"
    for d in ["journal", "working", "short-term", "long-term",
              "subconscious", "_meta", "archive", "_quarantine"]:
        (root / d).mkdir(parents=True)
    shutil.copy(MEMBER / "20_memory" / "homeostasis.yml", root / "homeostasis.yml")

    # --- seed recurrence plus trust, principal-authorship and later-correction cases
    j = root / "journal"
    a_name = f"{day(3)}-1000-a.md"
    b_name = f"{day(2)}-1000-b.md"
    c_name = f"{day(1)}-1000-c.md"
    d_name = f"{day(1)}-1100-d.md"
    e_name = f"{day(0)}-0900-e.md"
    u_name = f"{day(0)}-0910-untrusted.md"
    h_name = f"{day(0)}-0920-human.md"
    f_name = f"{day(0)}-0930-correction-base.md"
    (j / a_name).write_text(journal_entry(
        day(3), "j.a", "ada fixed the printer queue on opal", ["ada"], ["opal"]))
    (j / b_name).write_text(journal_entry(
        day(2), "j.b", "printer queue on opal fixed again by ada", ["ada"], ["opal"]))
    (j / c_name).write_text(journal_entry(
        day(1), "j.c", "ada documented the opal printer fix", ["ada"], ["opal"]))
    (j / d_name).write_text(journal_entry(
        day(1), "j.d", "one-off note about the garden", ["ada"], ["garden"]))
    (j / e_name).write_text(journal_entry(
        day(0), "j.e", "ada re-verified the opal printer queue fix", ["ada"], ["opal"]))
    (j / u_name).write_text(journal_entry(
        day(0), "j.untrusted", "unreviewed report about the opal queue", ["ada"], ["opal"],
        trust="untrusted"))
    (j / h_name).write_text(journal_entry(
        day(0), "j.human", "the principal marked the opal recovery rule pivotal", ["ada"],
        ["opal"], source_type="human"))
    (j / f_name).write_text(journal_entry(
        day(0), "j.correction-base", "the opal queue uses the legacy route", ["ada"], ["opal"]))

    print("1. sleep-prep: current window and run binding")
    r = run("sleep-prep.py", "--root", str(root))
    check("prep exits 0", r.returncode == 0, r.stderr)
    cands = json.loads((root / "_meta" / "sleep-candidates.json").read_text())
    check("8 entries staged", cands["window"]["count"] == 8)
    check("candidate run_id emitted", len(cands.get("run_id", "")) == 64)
    check("ada recurs on 4 distinct days", cands["entities"].get("ada", {}).get("distinct_days") == 4)
    check("ada+opal co-occur", any(set(p[:2]) == {"ada", "opal"} for p in cands["cooccurrence"]))
    check("known entities include garden", "garden" in cands["known_entities"])

    # This real journal file was not in the candidate snapshot and must not launder a claim.
    backfill_name = f"{day(10)}-0800-backfill.md"
    (j / backfill_name).write_text(journal_entry(
        day(10), "j.backfill", "older evidence for the opal printer fix", ["ada"], ["opal"]))

    claims = {"run_id": "wrong-window", "claims": [
        {"claim": "Ada is the person who fixes the opal printer queue",
         "kind": "procedure", "support_event_ids": [a_name, b_name, c_name, e_name],
         "confidence": 0.9, "changed_entities": ["ada", "opal"], "importance": 0.8,
         "decision_impact": True,
         "proposed_edges": [{"from": "ada", "relation": "maintains", "to": "opal",
                             "assertable": False}]},
        {"claim": "The user prefers short answers", "kind": "preference",
         "support_event_ids": [d_name], "confidence": 0.85,
         "changed_entities": ["ada"], "importance": 0.6},
        {"claim": "The garden was noted once in passing", "kind": "observation",
         "support_event_ids": [d_name], "confidence": 0.7,
         "changed_entities": ["garden"], "importance": 0.3},
        {"claim": "The unreviewed opal queue report is operationally decisive",
         "kind": "decision", "support_event_ids": [u_name, h_name], "confidence": 0.95,
         "changed_entities": ["ada", "opal"], "importance": 0.9, "decision_impact": True,
         "pivotal": True},
        {"claim": "The garden note is permanently pivotal", "kind": "observation",
         "support_event_ids": [d_name], "confidence": 0.9,
         "changed_entities": ["garden"], "pivotal": True},
        {"claim": "Ada explicitly made the opal recovery rule pivotal", "kind": "decision",
         "support_event_ids": [h_name], "confidence": 0.9,
         "changed_entities": ["ada", "opal"], "pivotal": True},
        {"claim": "The opal queue uses the legacy route", "kind": "observation",
         "support_event_ids": [f_name], "confidence": 0.8,
         "changed_entities": ["ada", "opal"]},
        {"claim": "Zorgon runs the print server", "kind": "observation",
         "support_event_ids": [a_name], "confidence": 0.9,
         "changed_entities": ["zorgon"]},
        {"claim": "Ghost-sourced claim", "kind": "observation",
         "support_event_ids": ["nope.md"], "confidence": 0.9,
         "changed_entities": ["ada"]},
        {"claim": "Out-of-window evidence cannot support this claim", "kind": "observation",
         "support_event_ids": [backfill_name], "confidence": 0.9,
         "changed_entities": ["ada", "opal"]},
    ]}
    (root / "_meta" / "sleep-claims.json").write_text(json.dumps(claims))

    print("2. sleep-apply: run binding, validation and trust ceilings")
    r = run("sleep-apply.py", "--root", str(root))
    check("run_id mismatch refuses apply", r.returncode != 0 and "run_id" in r.stderr, r.stderr)
    check("run_id refusal writes no state", not (root / "_meta" / "sleep-state.json").exists())

    claims["run_id"] = cands["run_id"]
    (root / "_meta" / "sleep-claims.json").write_text(json.dumps(claims))
    r = run("sleep-apply.py", "--root", str(root))
    check("apply exits 0", r.returncode == 0, r.stderr)
    check("7 accepted, 3 rejected, 0 merged",
          "accepted 7, rejected 3, merged 0" in r.stdout, r.stdout)
    log_text = (root / "_meta" / "sleep-log.md").read_text()
    check("out-of-window support rejected", f"unsupported_claim:{backfill_name}" in log_text)

    _, untrusted = find_atom(root, "unreviewed opal queue report")
    untrusted_path, _ = find_atom(root, "unreviewed opal queue report")
    check("untrusted-source claim capped at tier 2", untrusted.get("trust_tier") == 2,
          str(untrusted))
    check("untrusted-source claim not promoted to long-term",
          untrusted_path is not None and untrusted_path.parent.name != "long-term",
          str(untrusted_path))
    _, stripped = find_atom(root, "garden note is permanently pivotal")
    honoured_path, honoured = find_atom(root, "opal recovery rule pivotal")
    check("model pivotal stripped without principal support", stripped.get("pivotal") is False)
    check("pivotal stripping logged",
          "pivotal stripped (no principal-authored support)" in log_text)
    check("principal-supported pivotal honoured",
          honoured.get("pivotal") is True and honoured_path.parent.name == "long-term",
          f"path={honoured_path} meta={honoured}")

    state = json.loads((root / "_meta" / "sleep-state.json").read_text())
    check("processed set contains only applied window entries",
          len(state.get("processed", [])) == 8 and backfill_name not in state.get("processed", []),
          str(state))
    brief_spec = importlib.util.spec_from_file_location("session_brief", HOOKS / "session-brief.py")
    brief = importlib.util.module_from_spec(brief_spec)
    brief_spec.loader.exec_module(brief)
    brief.ROOT = tmp
    check("session brief counts entries outside processed set", brief.unconsolidated_entries() == 1)
    check("association edge written",
          len(list((root / "subconscious" / "associations").glob("*.md"))) == 1)
    check("world-model snapshot written",
          len(list((root / "subconscious" / "world-model").glob("*.md"))) == 1)

    print("3. next sleep: backfill staging and duplicate strengthening")
    r = run("sleep-prep.py", "--root", str(root))
    next_cands = json.loads((root / "_meta" / "sleep-candidates.json").read_text())
    check("backfilled older entry staged on next prep",
          r.returncode == 0 and [e["file"] for e in next_cands["entries"]] == [backfill_name],
          r.stdout)
    before_cards = len(atom_records(root))
    _, canonical_before = find_atom(root, "person who fixes the opal printer queue")
    before_sources = len(canonical_before.get("sources") or [])
    before_touches = len(canonical_before.get("touches") or [])
    duplicate = {"run_id": next_cands["run_id"], "claims": [{
        "claim": "Ada is the person who fixes the opal printer queue",
        "kind": "procedure", "support_event_ids": [backfill_name], "confidence": 0.9,
        "changed_entities": ["ada", "opal"], "importance": 0.8,
    }]}
    (root / "_meta" / "sleep-claims.json").write_text(json.dumps(duplicate))
    r = run("sleep-apply.py", "--root", str(root))
    _, canonical_after = find_atom(root, "person who fixes the opal printer queue")
    check("duplicate claim merges into existing card",
          r.returncode == 0 and "accepted 0, rejected 0, merged 1" in r.stdout, r.stdout)
    check("duplicate merge grows sources and touches",
          len(canonical_after.get("sources") or []) == before_sources + 1
          and len(canonical_after.get("touches") or []) == before_touches + 1
          and f"journal/{backfill_name}" in canonical_after.get("sources", []),
          f"sources={canonical_after.get('sources')} touches={canonical_after.get('touches')}")
    check("duplicate merge writes no new atom", len(atom_records(root)) == before_cards)
    check("duplicate logged as merged not rejected",
          "MERGED into" in (root / "_meta" / "sleep-log.md").read_text())

    print("4. reaper: journal-source and atom supersession")
    correction_name = f"{day(0)}-1000-correction.md"
    (j / correction_name).write_text(journal_entry(
        day(0), "j.correction", "the legacy route statement was corrected", ["ada"], ["opal"],
        kind="correction", corrects="j.correction-base"))
    r = run("reaper.py", "--root", str(root), "--as-of", str(TODAY))
    _, corrected = find_atom(root, "opal queue uses the legacy route")
    check("journal correction supersedes atom built from corrected entry",
          r.returncode == 0 and corrected.get("status") == "superseded"
          and corrected.get("superseded_by") == "j.correction", str(corrected))

    direct_name = f"{day(0)}-1010-direct-correction.md"
    write_atom(root, "direct.md", "t.direct", "direct compatibility target", a_name)
    (j / direct_name).write_text(journal_entry(
        day(0), "j.direct-correction", "direct atom correction", ["ada"], ["opal"],
        kind="correction", corrects="t.direct"))
    run("reaper.py", "--root", str(root), "--as-of", str(TODAY))
    _, direct = find_atom(root, "direct compatibility target")
    check("direct atom-id correction remains compatible",
          direct.get("status") == "superseded"
          and direct.get("superseded_by") == "j.direct-correction", str(direct))

    write_atom(root, "atom-target.md", "t.atom-target", "atom supersession target", a_name)
    write_atom(root, "atom-replacement.md", "t.atom-replacement", "atom supersession replacement",
               b_name, supersedes="t.atom-target")
    run("reaper.py", "--root", str(root), "--as-of", str(TODAY))
    _, atom_target = find_atom(root, "atom supersession target")
    check("atom-level supersedes marks live target",
          atom_target.get("status") == "superseded"
          and atom_target.get("superseded_by") == "t.atom-replacement", str(atom_target))

    (root / "short-term" / "rogue.md").write_text(
        "---\nid: t.rogue\ntype: observation\nlayer: short-term\nwhat: no sources\n---\n\n# rogue\n")
    r = run("reaper.py", "--root", str(root), "--as-of", str(TODAY))
    check("sourceless atom quarantined", (root / "_quarantine" / "rogue.md").exists())
    r = run("reaper.py", "--root", str(root), "--as-of", str(TODAY))
    check("idempotent same-day run moves nothing", "'moved': 0" in r.stdout, r.stdout)

    print("5. reaper +40d: decay and protected memory")
    # The supersession fixtures make this store large enough for the production churn guard.
    # Raise its minimum only in the throwaway root so the decay path remains independently tested.
    cfg = yaml.safe_load((root / "homeostasis.yml").read_text())
    cfg["stability"]["min_atoms_for_check"] = 100
    (root / "homeostasis.yml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    later = TODAY + datetime.timedelta(days=40)
    r = run("reaper.py", "--root", str(root), "--as-of", str(later))
    check("reaper(+40d) exits 0", r.returncode == 0, r.stderr)
    archived = [p.name for p in (root / "archive").glob("*.md")]
    surviving = [p for d in ["working", "short-term", "long-term"]
                 for p in (root / d).glob("*.md")]
    pref_alive = any("prefers short answers" in p.read_text() for p in surviving)
    check("stale observation archived on layer default", len(archived) >= 1, str(archived))
    check("preference (until-superseded) survives decay", pref_alive)
    lt_still = any("person who fixes" in p.read_text().lower()
                   for p in (root / "long-term").glob("*.md"))
    check("long-term atom not archived after 40d (3-month clock)", lt_still)

    shutil.rmtree(tmp)
    if FAILS:
        print(f"\nmemory-selftest: {len(FAILS)} FAILURE(S): {FAILS}")
        return 1
    print("\nmemory-selftest: all green — the loop stocks, tiers, decays and protects correctly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
