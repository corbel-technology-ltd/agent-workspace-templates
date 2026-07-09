#!/usr/bin/env python3
"""Session-start reflex: boot orientation + a near-zero-cost micro-brief.

Always injects a short orientation block at session start so a fresh agent knows who it is, where
current state lives, and to stand by rather than act unprompted. Then appends any open
decision-queue items + open project loops if they exist. Kept tight by design (situational
awareness, not the backlog).

Open loops live per-project under 80_projects/*/loops.md (see 30_schemas/project.md); this hook
aggregates the `## Open` tables across them. A workspace that names its tracker differently (e.g.
product_loops) keeps the same 80_projects/<slug>/loops.md shape, so the glob below is unchanged.

Neutral hook contract (see core/RUNTIMES.md): no payload; prints the brief on stdout for the
runtime adapter to inject at session start. The workspace root is taken from the
<<WORKSPACE_ROOT_ENV>> env var if set, else inferred from this file's location (repo root = two
levels up from core/hooks/).
"""
import sys, os, json, glob, re
from pathlib import Path

ROOT = Path(os.environ.get("<<WORKSPACE_ROOT_ENV>>") or Path(__file__).resolve().parents[2])
WORKSPACE_NAME = os.environ.get("<<WORKSPACE_ROOT_ENV>>_NAME") or "<<WORKSPACE_NAME>>"
SHARED = os.environ.get("<<WORKSPACE_ROOT_ENV>>_SHARED") or "<<SHARED_CONTEXT_PATH>>"


def parse_table_lines(lines):
    """Return data rows (lists of cells) from Markdown pipe-table lines, skipping headers,
    separators, comment blocks, and placeholder rows."""
    out = []
    in_comment = False
    for line in lines:
        s = line.strip()
        if in_comment:  # skip example rows inside <!-- ... --> blocks
            if "-->" in s:
                in_comment = False
            continue
        if s.startswith("<!--"):
            if "-->" not in s:
                in_comment = True
            continue
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not cells or not cells[0]:
            continue
        head = cells[0].lower().strip("_* ")
        if head in ("id", "date", "item", "who"):
            continue
        if set(cells[0]) <= set("-: "):  # separator row
            continue
        low = s.lower()
        if "none yet" in low or "(none" in low or "(no " in low:  # placeholder row
            continue
        out.append(cells)
    return out


def rows(md_rel):
    p = ROOT / md_rel
    if not p.exists():
        return []
    return parse_table_lines(p.read_text().splitlines())


def section_lines(path, heading):
    """Lines strictly under `heading` (an exact `## ...` line) up to the next `## ` heading."""
    try:
        lines = Path(path).read_text().splitlines()
    except Exception:
        return []
    out, capturing = [], False
    for line in lines:
        if line.strip().startswith("## "):
            capturing = line.strip() == heading
            continue
        if capturing:
            out.append(line)
    return out


def current_focus():
    """First `**Current focus:** ...` line from staging.md (the Now / In flight block)."""
    p = ROOT / "00_meta" / "staging.md"
    if not p.exists():
        return ""
    for line in p.read_text().splitlines():
        s = line.strip()
        if s.lower().startswith("**current focus"):
            txt = s.split(":", 1)[1] if ":" in s else s
            return txt.strip().lstrip("*").strip().rstrip(".")
    return ""


def latest_handover():
    """Prefer the explicit `**Latest handover:**` pointer in staging.md (single source of truth);
    fall back to the newest dated `90_runs/YYYY-MM-DD-*.md` run note (handovers are not always
    named `*handover*`)."""
    p = ROOT / "00_meta" / "staging.md"
    if p.exists():
        for line in p.read_text().splitlines():
            if line.strip().lower().startswith("**latest handover"):
                m = re.search(r"90_runs/[^\s)\]`]+\.md", line)
                if m:
                    return m.group(0)
    dated = sorted(f for f in glob.glob(str(ROOT / "90_runs" / "*.md"))
                   if re.match(r"\d{4}-\d{2}-\d{2}", Path(f).name))
    return ("90_runs/" + Path(dated[-1]).name) if dated else ""


def project_loops():
    """Open loops across 80_projects/*/loops.md (direct children, incl. _general), tagged by
    project. Parses only each file's `## Open` section so a populated `## Closed` is never misread."""
    out = []
    for p in sorted(glob.glob(str(ROOT / "80_projects" / "*" / "loops.md"))):
        project = Path(p).parent.name.lstrip("_") or "general"
        for cells in parse_table_lines(section_lines(p, "## Open")):
            out.append((project, cells[0]))
    return out


def main():
    try:
        json.load(sys.stdin)
    except Exception:
        pass

    # Before onboarding, this template still carries <<TOKEN>> placeholders; the
    # onboarding-gate speaks instead, so stay dormant rather than print raw tokens.
    if (ROOT / ".uninitialised").exists():
        sys.exit(0)

    lines = [f"[{WORKSPACE_NAME} brief]"]
    lines.append("You are <<AGENT_NAME>>, this workspace's agent (see AGENTS.md Identity for scope).")
    boot = "Boot: "
    if SHARED and SHARED.strip():
        boot += f"load the shared context at {SHARED} (identity, operating-rules); "
    boot += ("read 00_meta/staging.md; re-verify the newest handover. If no task is queued, "
             "stand by for <<OWNER>> and do not act unprompted.")
    lines.append(boot)
    lines.append("Projects: active projects + their loops live in 80_projects/ (see 80_projects/index.md).")

    focus = current_focus()
    if focus:
        lines.append(f"Current focus: {focus}")

    hand = latest_handover()
    if hand:
        lines.append(f"Latest handover: {hand} (a claim; re-verify before trusting it).")

    dq = [r for r in rows("50_registers/decision-queue.md") if any(c.lower() == "open" for c in r)]
    ol = project_loops()
    if dq:
        lines.append(f"Open decisions ({len(dq)}): "
                     + "; ".join((r[2] if len(r) > 2 else r[0]) for r in dq[:5]))
    if ol:
        lines.append(f"Open loops ({len(ol)}): "
                     + "; ".join(f"{proj}: {item}" for proj, item in ol[:5]))

    print("\n".join(lines))
    sys.exit(0)


if __name__ == "__main__":
    main()
