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
import sys, os, json, glob, re, datetime
from pathlib import Path

ROOT = Path(os.environ.get("<<WORKSPACE_ROOT_ENV>>") or Path(__file__).resolve().parents[2])
WORKSPACE_NAME = os.environ.get("<<WORKSPACE_ROOT_ENV>>_NAME") or "<<WORKSPACE_NAME>>"
SHARED = os.environ.get("<<WORKSPACE_ROOT_ENV>>_SHARED") or "<<SHARED_CONTEXT_PATH>>"
SHARED_DIRS = ("identity", "operating-rules", "boundaries")
SHARED_REQUIRED = (
    "SHARED.md", "identity/README.md", "operating-rules/README.md", "boundaries/README.md",
    "identity/principal.md", "boundaries/boundaries.md",
)
SHARED_CORE_ORDER = SHARED_REQUIRED[:4]


def shared_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, 0
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            values = {}
            for line in lines[1:index]:
                match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
                if match:
                    key = match.group(1)
                    if key in ("status", "load") and key in values:
                        raise ValueError(f"duplicate frontmatter key {key!r}")
                    values[key] = match.group(2).strip().strip("'\"")
            return values, index + 1
    return None, 0


def shared_substantive(text):
    meta, body_start = shared_frontmatter(text)
    if meta is None or "> Blank by design" in text:
        return False
    in_comment = in_related = False
    for line in text.splitlines()[body_start:]:
        stripped = line.strip()
        if in_comment:
            if "-->" in stripped:
                in_comment = False
            continue
        if "<!--" in stripped:
            if "-->" not in stripped:
                in_comment = True
            stripped = stripped.split("<!--", 1)[0].strip()
        if stripped == "## Related":
            in_related = True
            continue
        if not in_related and stripped and not stripped.startswith("#"):
            return True
    return False


def safe_shared_file(root, path):
    resolved = path.resolve(strict=True)
    if resolved != root and root not in resolved.parents:
        raise OSError(f"{path.relative_to(root)} resolves outside the configured store")
    if not resolved.is_file():
        raise OSError(f"{path.relative_to(root)} is not a regular file")
    return resolved


def shared_always_set(raw_root):
    """Read fixed Shared paths as data; never import or execute anything from that store."""
    configured = Path(raw_root)
    if not configured.is_absolute():
        raise OSError("configured store path is not absolute")
    root = configured.resolve(strict=True)
    if not root.is_dir():
        raise OSError("configured store path is not a directory")
    if (root / ".uninitialised").exists():
        raise ValueError("configured Shared store is uninitialised")
    paths = [root / "SHARED.md"]
    for directory in SHARED_DIRS:
        folder = (root / directory).resolve(strict=True)
        if folder != root and root not in folder.parents:
            raise OSError(f"{directory}/ resolves outside the configured store")
        paths.extend(sorted((root / directory).glob("*.md")))
    records = {}
    for path in paths:
        resolved = safe_shared_file(root, path)
        text = resolved.read_text(encoding="utf-8")
        rel = path.relative_to(root).as_posix()
        meta, _ = shared_frontmatter(text)
        if meta is None:
            raise ValueError(f"{rel} has malformed frontmatter")
        records[rel] = (meta, text, shared_substantive(text))
    missing_required = sorted(set(SHARED_REQUIRED) - set(records))
    if missing_required:
        raise ValueError("required always file(s) missing: " + ", ".join(missing_required))
    incomplete = sorted(rel for rel, (meta, _, _) in records.items()
                        if meta.get("load") not in ("always", "triggered"))
    warnings = (["loading metadata is incomplete or invalid; all current substantive governed "
                 "files were loaded conservatively"] if incomplete else [])
    selected = set()
    for rel, (meta, _, has_body) in records.items():
        if rel in SHARED_CORE_ORDER and (meta.get("status") != "current" or not has_body):
            raise ValueError(f"{rel} required core file must be current and substantive")
        if meta.get("status") == "current" and not has_body:
            raise ValueError(f"{rel} has status current but a blank body")
        if meta.get("status") != "current":
            continue
        if incomplete or meta.get("load") == "always":
            selected.add(rel)
        if rel in SHARED_REQUIRED and meta.get("load") != "always":
            selected.add(rel)
            warnings.append(f"{rel} is required always but declares load: {meta.get('load', 'missing')}")
    ordered = [rel for rel in SHARED_CORE_ORDER if rel in selected]
    ordered.extend(sorted(selected - set(ordered)))
    return [(rel, records[rel][1]) for rel in ordered], sorted(set(warnings))


def shared_context_lines():
    if not SHARED or not SHARED.strip() or "<<" in SHARED:
        return [], False
    try:
        selected, warnings = shared_always_set(SHARED)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        return (["Shared-context WARNING: safe loading could not be established "
                 f"({exc}). Consequential work must wait for manual Shared-context review."], False)
    lines = []
    for rel, text in selected:
        lines.extend((f"<<< shared-context:{rel} >>>", text.rstrip(),
                      f"<<< end shared-context:{rel} >>>"))
    lines.extend(f"Shared-context WARNING: {warning}; run the store's shared-lint gate."
                 for warning in warnings)
    return lines, True


def unconsolidated_entries():
    """Journal entries outside the sleep processed set (0 on failure — brief stays quiet)."""
    try:
        state = ROOT / "20_memory" / "_meta" / "sleep-state.json"
        processed = set(json.loads(state.read_text()).get("processed") or []) if state.exists() else set()
        return sum(1 for p in (ROOT / "20_memory" / "journal").glob("*.md")
                   if p.name.lower() != "readme.md" and p.name not in processed)
    except Exception:
        return 0


def sleep_nudge_threshold():
    """sleep_pass.nudge_after_entries from homeostasis.yml, read with a regex so this hook
    keeps its zero-dependency contract (no yaml import)."""
    try:
        text = (ROOT / "20_memory" / "homeostasis.yml").read_text()
        m = re.search(r"nudge_after_entries:\s*(\d+)", text)
        return int(m.group(1)) if m else 10
    except Exception:
        return 10


def template_nudge():
    """Offline update reminder from the last explicit check; malformed state means check due."""
    path = ROOT / "20_memory" / "_meta" / "template-check.json"
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
        if state.get("behind"):
            commit = str(state.get("latest_commit") or "unknown")[:12]
            return f"Template: update available at commit {commit} - run python3 tools/template-update.py --status"
        checked = str(state["last_checked"]).replace("Z", "+00:00")
        when = datetime.datetime.fromisoformat(checked)
        if when.tzinfo is None:
            when = when.replace(tzinfo=datetime.timezone.utc)
        if datetime.datetime.now(datetime.timezone.utc) - when <= datetime.timedelta(days=7):
            return ""
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        pass
    return "Template: update check due - run python3 tools/template-update.py --check"


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

    shared_lines, shared_loaded = shared_context_lines()
    lines = shared_lines + [f"[{WORKSPACE_NAME} brief]"]
    lines.append("You are <<AGENT_NAME>>, this workspace's agent (see AGENTS.md Identity for scope).")
    boot = "Boot: "
    if shared_loaded:
        boot += "the Shared always set is injected above; use its indexes for triggered context; "
    elif SHARED and SHARED.strip() and "<<" not in SHARED:
        boot += "Shared context is configured but was not safely injected; obey the warning above; "
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

    n = unconsolidated_entries()
    if n >= sleep_nudge_threshold():
        lines.append(f"Memory: {n} journal entries await consolidation - a memory-sleep run is due "
                     "(the memory-sleep skill folds them into the depth layers).")

    nudge = template_nudge()
    if nudge:
        lines.append(nudge)

    print("\n".join(lines))
    sys.exit(0)


if __name__ == "__main__":
    main()
