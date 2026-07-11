#!/usr/bin/env python3
"""recall-tiered.py — depth-ordered memory search with a never-lost fallback.

Walks the memory the way the architecture means it to be read:

    working -> short-term -> long-term -> subconscious -> archive -> journal

Curated beliefs first (cheapest, highest-salience), raw evidence last (nothing is ever lost).
By default the walk STOPS at the first depth that answers; --all walks every depth. Subconscious
hits are labelled PRIMING (assertable: false — they bias interpretation, they are never facts).
Archive hits are labelled EXPIRED (they decayed or were superseded; verify before trusting).
Journal hits are ground truth but raw.

Matching is frontmatter-aware (id/what/who/where/tags/type) plus body text, case-insensitive,
all query terms must match somewhere in the file. Results show layer, tier, activation, and the
matching `what` so the reader can decide without opening anything.

--touch records the retrieval on atom hits (appends a touch + bumps retrieval_count), feeding
ACT-R activation so that USE strengthens memory. Off by default: browsing is not remembering.
On an ARCHIVE hit, --touch REELS THE ATOM BACK IN: it returns to short-term with a fresh
last_verified, and the reaper re-tiers it from there (the deep-sea catch; unused, it will float
back down through decay as designed).

--follow walks each hit's `related:` frontmatter edges one hop and shows the linked atoms -
retrieval by graph edge instead of grepping everything.

Usage:
    python3 tools/recall-tiered.py <query terms>            # stop at first answering depth
    python3 tools/recall-tiered.py --all <query terms>      # walk every depth
    python3 tools/recall-tiered.py --follow <query terms>   # show 1-hop linked atoms per hit
    python3 tools/recall-tiered.py --touch <query terms>    # count retrieval as a touch; reel
                                                            # archive hits back to short-term
"""
import datetime
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("<<WORKSPACE_ROOT_ENV>>") or Path(__file__).resolve().parents[1])
MEM = ROOT / "20_memory"

DEPTHS = [
    ("working", MEM / "working", ""),
    ("short-term", MEM / "short-term", ""),
    ("long-term", MEM / "long-term", ""),
    ("subconscious", MEM / "subconscious", "PRIMING - assertable:false, do not state as fact"),
    ("archive", MEM / "archive", "EXPIRED - decayed or superseded, verify before trusting"),
    ("journal", MEM / "journal", "RAW EVENT - ground truth, uncurated"),
]


def parse_front(text):
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta = {}
    for line in parts[1].splitlines():
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if m:
            meta[m.group(1)] = m.group(2).strip()
    return meta, parts[2]


def matches(terms, text):
    low = text.lower()
    return all(t in low for t in terms)


def search_depth(d, terms):
    hits = []
    if not d.is_dir():
        return hits
    for p in sorted(d.rglob("*.md")):
        if p.name.lower() == "readme.md":
            continue
        try:
            text = p.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        if matches(terms, text):
            meta, _ = parse_front(text)
            hits.append((p, meta))
    return hits


def touch(p):
    """Append a retrieval touch (best-effort, plain-text frontmatter surgery)."""
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        text = p.read_text()
        if "touches:" not in text:
            return False
        text = re.sub(r"(touches:\n(?:- [^\n]+\n)*)", rf"\g<1>- '{now}'\n", text, count=1)
        text = re.sub(r"retrieval_count: (\d+)",
                      lambda m: f"retrieval_count: {int(m.group(1)) + 1}", text, count=1)
        p.write_text(text)
        return True
    except OSError:
        return False


def reel_in(p):
    """An archive hit that proved useful returns to short-term: fresh last_verified, layer
    rewritten, file moved. The reaper re-tiers it from there — and lets it float back down
    if it goes unused again."""
    today = datetime.date.today().isoformat()
    try:
        text = p.read_text()
        text = re.sub(r"^layer: .*$", "layer: short-term", text, count=1, flags=re.M)
        text = re.sub(r"^last_verified: .*$", f"last_verified: '{today}'", text, count=1, flags=re.M)
        text = re.sub(r"^status: (stale|superseded)$", "status: current", text, count=1, flags=re.M)
        dst = MEM / "short-term" / p.name
        dst.write_text(text)
        p.unlink()
        touch(dst)
        return dst
    except OSError:
        return None


def related_refs(text):
    """Every ref target in the frontmatter's related: block - both the house flow style
    ({ref: path, ...}) and the block style yaml.safe_dump emits (- ref: path)."""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return []
    fm = parts[1]
    refs = [r.strip() for r in re.findall(r"\{ref:\s*([^,}]+)", fm)]
    refs += [r.strip().strip("'\"") for r in re.findall(r"^\s*-\s+ref:\s*(.+)$", fm, re.M)]
    return list(dict.fromkeys(refs))


def main():
    args = [a for a in sys.argv[1:]]
    walk_all = "--all" in args
    do_touch = "--touch" in args
    follow = "--follow" in args
    terms = [a.lower() for a in args if not a.startswith("--")]
    if not terms:
        print(__doc__.split("Usage:")[1])
        sys.exit(2)

    found_any = False
    for name, d, warning in DEPTHS:
        hits = search_depth(d, terms)
        if not hits:
            continue
        found_any = True
        print(f"\n== {name} ({len(hits)} hit{'s' if len(hits) != 1 else ''})"
              + (f"  [{warning}]" if warning else ""))
        for p, meta in hits[:10]:
            badge = ""
            if meta.get("tier") or meta.get("activation_base"):
                badge = f" [{meta.get('tier','?')} A={meta.get('activation_base','?')}]"
            what = (meta.get("what") or meta.get("name") or "").strip('"')[:100]
            print(f"  {p.relative_to(ROOT)}{badge}")
            if what:
                print(f"    {what}")
            if follow:
                for ref in related_refs(p.read_text())[:6]:
                    tgt = ROOT / ref
                    if tgt.exists():
                        tmeta, _ = parse_front(tgt.read_text())
                        twhat = (tmeta.get("what") or tmeta.get("name") or "").strip('"')[:80]
                        print(f"    ~ linked: {ref}" + (f" - {twhat}" if twhat else ""))
                    else:
                        print(f"    ~ linked: {ref} (moved or archived - search by name)")
            if do_touch and name in ("working", "short-term", "long-term"):
                touch(p)
            elif do_touch and name == "archive":
                dst = reel_in(p)
                if dst:
                    print(f"    ^ REELED IN -> {dst.relative_to(ROOT)} (back in short-term; "
                          "the reaper re-tiers it from here)")
        if len(hits) > 10:
            print(f"  ... and {len(hits) - 10} more")
        if not walk_all and name != "journal":
            deeper = [n for n, dd, _ in DEPTHS[[x[0] for x in DEPTHS].index(name) + 1:]]
            print(f"\n(stopped at first answering depth; deeper layers not searched: "
                  f"{', '.join(deeper)} - use --all to walk everything)")
            break

    if not found_any:
        print(f"no hits at any depth for: {' '.join(terms)}")
        print("(the journal is append-only and complete - if it is not there, it never happened)")
        sys.exit(1)


if __name__ == "__main__":
    main()
