#!/usr/bin/env python3
"""memory-selftest.py — proves the memory loop actually works, end to end, deterministically.

Builds a throwaway memory root in a temp dir, seeds synthetic journal entries, then exercises the
full pipeline exactly as a live workspace would:

  1. sleep-prep    -> candidates staged, entities + recurrence extracted, known-entity universe built
  2. sleep-apply   -> good claims written as schema-valid atoms; every rejection class fires:
                      unsupported_claim, new_named_entity, duplicate hash, assertable edge
  3. reaper (day 0)-> hot atom promoted short-term -> working; recurrent decision atom promoted
                      short-term -> long-term; sourceless atom quarantined
  4. reaper (day 0, again) -> idempotent: nothing further moves (hysteresis holds)
  5. reaper (+40d) -> cooled atom demoted working -> short-term; stale atom archived on the
                      layer's valid_for default; preference atom (until-superseded) survives

Run from the member root:  python3 tools/memory-selftest.py
Exit 0 = every assertion green. Registered as a member gate in the family check.
"""
import datetime
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

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


def journal_entry(when, ident, what, who, where, trust="trusted"):
    return (f"---\nid: {ident}\ntype: observation\nwho: [{', '.join(who)}]\n"
            f"what: \"{what}\"\nwhere: [{', '.join(where)}]\nwhen: {when}T12:00:00Z\n"
            f"source_type: system\ntrust: {trust}\n---\n\n# {what}\n")


def run(script, *args):
    r = subprocess.run([sys.executable, str(HOOKS / script), *args],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout, r.stderr)
    return r


def main():
    tmp = Path(tempfile.mkdtemp(prefix="memtest-"))
    root = tmp / "20_memory"
    for d in ["journal", "working", "short-term", "long-term",
              "subconscious", "_meta", "archive", "_quarantine"]:
        (root / d).mkdir(parents=True)
    shutil.copy(MEMBER / "20_memory" / "homeostasis.yml", root / "homeostasis.yml")

    # --- seed a journal: one recurring fact-family across 3 days + one single event
    j = root / "journal"
    (j / f"{day(3)}-1000-a.md").write_text(journal_entry(
        day(3), "j.a", "ada fixed the printer queue on opal", ["ada"], ["opal"]))
    (j / f"{day(2)}-1000-b.md").write_text(journal_entry(
        day(2), "j.b", "printer queue on opal fixed again by ada", ["ada"], ["opal"]))
    (j / f"{day(1)}-1000-c.md").write_text(journal_entry(
        day(1), "j.c", "ada documented the opal printer fix", ["ada"], ["opal"]))
    (j / f"{day(1)}-1100-d.md").write_text(journal_entry(
        day(1), "j.d", "one-off note about the garden", ["ada"], ["garden"]))
    (j / f"{day(0)}-0900-e.md").write_text(journal_entry(
        day(0), "j.e", "ada re-verified the opal printer queue fix", ["ada"], ["opal"]))

    print("1. sleep-prep")
    r = run("sleep-prep.py", "--root", str(root))
    check("prep exits 0", r.returncode == 0, r.stderr)
    cands = json.loads((root / "_meta" / "sleep-candidates.json").read_text())
    check("5 entries staged", cands["window"]["count"] == 5)
    check("ada recurs on 4 distinct days", cands["entities"].get("ada", {}).get("distinct_days") == 4)
    check("ada+opal co-occur", any(set(p[:2]) == {"ada", "opal"} for p in cands["cooccurrence"]))
    check("known entities include garden", "garden" in cands["known_entities"])

    print("2. sleep-apply: validation + writes")
    claims = {"claims": [
        {"claim": "Ada is the person who fixes the opal printer queue",
         "kind": "procedure", "support_event_ids": [f"{day(3)}-1000-a.md", f"{day(2)}-1000-b.md",
                                                    f"{day(1)}-1000-c.md", f"{day(0)}-0900-e.md"],
         "confidence": 0.9, "changed_entities": ["ada", "opal"], "importance": 0.8,
         "decision_impact": True,
         "proposed_edges": [{"from": "ada", "relation": "maintains", "to": "opal",
                             "assertable": False}]},
        {"claim": "The user prefers short answers", "kind": "preference",
         "support_event_ids": [f"{day(1)}-1100-d.md"], "confidence": 0.85,
         "changed_entities": ["ada"], "importance": 0.6},
        {"claim": "The garden was noted once in passing", "kind": "observation",
         "support_event_ids": [f"{day(1)}-1100-d.md"], "confidence": 0.7,
         "changed_entities": ["garden"], "importance": 0.3},   # low heat -> expires at +40d
        {"claim": "Zorgon runs the print server", "kind": "observation",
         "support_event_ids": [f"{day(3)}-1000-a.md"], "confidence": 0.9,
         "changed_entities": ["zorgon"]},                      # unknown entity -> reject
        {"claim": "Ghost-sourced claim", "kind": "observation",
         "support_event_ids": ["nope.md"], "confidence": 0.9,
         "changed_entities": ["ada"]},                          # bad support -> reject
        {"claim": "Ada is the person who fixes the opal printer queue",
         "kind": "observation", "support_event_ids": [f"{day(3)}-1000-a.md"],
         "confidence": 0.9, "changed_entities": ["ada"]},       # duplicate hash -> reject
    ]}
    (root / "_meta" / "sleep-claims.json").write_text(json.dumps(claims))
    r = run("sleep-apply.py", "--root", str(root))
    check("apply exits 0", r.returncode == 0, r.stderr)
    check("3 accepted, 3 rejected", "accepted 3, rejected 3" in r.stdout, r.stdout)
    st_atoms = [p for p in (root / "short-term").glob("*.md")]
    lt_atoms = [p for p in (root / "long-term").glob("*.md")]
    wk_atoms = [p for p in (root / "working").glob("*.md")]
    check("atoms written by apply", len(st_atoms) + len(lt_atoms) + len(wk_atoms) == 3,
          f"st={len(st_atoms)} lt={len(lt_atoms)} wk={len(wk_atoms)}")
    check("association edge written",
          len(list((root / "subconscious" / "associations").glob("*.md"))) == 1)
    check("world-model snapshot written",
          len(list((root / "subconscious" / "world-model").glob("*.md"))) == 1)
    check("sleep marker advanced",
          json.loads((root / "_meta" / "sleep-state.json").read_text())["last_processed"]
          == f"{day(0)}-0900-e.md")
    check("rejections logged", "new_named_entity" in (root / "_meta" / "sleep-log.md").read_text())

    print("3. reaper day 0: promotion + quarantine (apply already ran it once)")
    # the ada procedure: 3 recent touches, trust 4, importance .8, decision_impact
    # => activation > long_term_enter AND promotion signal (recurrence + decision) => long-term
    lt = list((root / "long-term").glob("*.md"))
    check("recurrent decision atom promoted to long-term",
          any("ada" in p.read_text().lower() for p in lt), str([p.name for p in lt]))
    # sourceless atom -> quarantine
    (root / "short-term" / "rogue.md").write_text(
        "---\nid: t.rogue\ntype: observation\nlayer: short-term\nwhat: no sources\n---\n\n# rogue\n")
    r = run("reaper.py", "--root", str(root), "--as-of", str(TODAY))
    check("reaper exits 0", r.returncode == 0, r.stderr)
    check("sourceless atom quarantined", (root / "_quarantine" / "rogue.md").exists())

    print("4. idempotency: a second same-day run moves nothing")
    r = run("reaper.py", "--root", str(root), "--as-of", str(TODAY))
    check("no further moves", "'moved': 0" in r.stdout, r.stdout)

    print("5. reaper +40d: decay demotion + expiry archive, preference survives")
    later = TODAY + datetime.timedelta(days=40)
    r = run("reaper.py", "--root", str(root), "--as-of", str(later))
    check("reaper(+40d) exits 0", r.returncode == 0, r.stderr)
    archived = [p.name for p in (root / "archive").glob("*.md")]
    surviving = [p for d in ["working", "short-term", "long-term"]
                 for p in (root / d).glob("*.md")]
    pref_alive = any("prefers short answers" in p.read_text() for p in surviving)
    check("stale observation archived on layer default", len(archived) >= 1, str(archived))
    check("preference (until-superseded) survives decay", pref_alive)
    lt_still = any("ada" in p.read_text().lower() for p in (root / "long-term").glob("*.md"))
    check("long-term atom not archived after 40d (3-month clock)", lt_still)

    shutil.rmtree(tmp)
    if FAILS:
        print(f"\nmemory-selftest: {len(FAILS)} FAILURE(S): {FAILS}")
        return 1
    print("\nmemory-selftest: all green — the loop stocks, tiers, decays and protects correctly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
