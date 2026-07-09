#!/usr/bin/env python3
"""Session-start reflex: orient a visiting agent inside the shared-context store.

Prints, only when there is something to say: open objection windows from CHANGES.md (flagging any
past their close date), open handoffs from _coordination/dashboard.md, and the roster size. A
visiting agent then knows in one glance whether governance or coordination needs it before it
touches anything.

Neutral hook contract (see core/RUNTIMES.md): no payload; prints on stdout for the runtime adapter
to inject at session start. Silent on an uninitialised store (the onboarding gate speaks instead)
and silent when there is nothing open. Stdlib only.
"""
import json
import re
import sys
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ENTRY_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}) \| ([^|]+) \| (.+) \| window: (.+)$")
CLOSES_RE = re.compile(r"closes (\d{4}-\d{2}-\d{2})")


def ledger_open_windows():
    """(date, who, summary, closes, overdue) for every 'window: open' ledger entry."""
    p = ROOT / "CHANGES.md"
    if not p.exists():
        return []
    today = datetime.date.today()
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        m = ENTRY_RE.match(line.strip())
        if not m or not m.group(4).strip().startswith("open"):
            continue
        closes = None
        cm = CLOSES_RE.search(m.group(4))
        if cm:
            try:
                closes = datetime.date.fromisoformat(cm.group(1))
            except ValueError:
                closes = None
        overdue = bool(closes and closes < today)
        out.append((m.group(1), m.group(2).strip(), m.group(3).strip(), closes, overdue))
    return out


def table_rows(path, placeholder="_none yet_"):
    """Data rows of the first pipe table(s) in a file, skipping headers/separators/placeholders."""
    p = ROOT / path
    if not p.exists():
        return []
    rows = []
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not cells or not cells[0]:
            continue
        if set(cells[0]) <= set("-: "):
            continue
        if cells[0].lower() in ("id", "workspace"):
            continue
        if placeholder in cells[0]:
            continue
        rows.append(cells)
    return rows


def open_handoffs():
    """Rows from the dashboard's Open handoffs section only."""
    p = ROOT / "_coordination" / "dashboard.md"
    if not p.exists():
        return []
    lines, capturing = [], False
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("## "):
            capturing = line.strip() == "## Open handoffs"
            continue
        if capturing:
            lines.append(line)
    rows = []
    for line in lines:
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not cells or not cells[0] or set(cells[0]) <= set("-: ") \
                or cells[0].lower() == "id" or "_none yet_" in cells[0]:
            continue
        rows.append(cells)
    return rows


def main():
    try:
        json.load(sys.stdin)
    except Exception:
        pass
    if (ROOT / ".uninitialised").exists():
        sys.exit(0)  # the onboarding gate speaks; this reflex stays quiet

    windows = ledger_open_windows()
    handoffs = open_handoffs()
    roster = table_rows("_coordination/roster.md")

    if not windows and not handoffs:
        sys.exit(0)  # silent when clean

    lines = ["[<<STORE_NAME>> store] You are in the shared-context store; SHARED.md governs edits."]
    if windows:
        parts = []
        for date, who, summary, closes, overdue in windows[:5]:
            flag = " OVERDUE" if overdue else ""
            when = f"closes {closes}" if closes else "no close date"
            parts.append(f"{date} {who}: {summary[:70]} ({when}{flag})")
        lines.append(f"Open objection windows ({len(windows)}): " + "; ".join(parts))
    if handoffs:
        parts = [f"{r[0]}: {r[2][:60]}" if len(r) > 2 else r[0] for r in handoffs[:5]]
        lines.append(f"Open handoffs ({len(handoffs)}): " + "; ".join(parts))
    lines.append(f"Roster: {len(roster)} workspace(s) plugged in.")
    print("\n".join(lines))
    sys.exit(0)


if __name__ == "__main__":
    main()
