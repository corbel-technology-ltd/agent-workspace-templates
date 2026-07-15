#!/usr/bin/env python3
"""Session-start reflex: inject the Shared always set, governance and coordination.

Eligible content has `status: current`, `load: always`, and a substantive body. Seed and blank
files never load. If an older store lacks loading metadata, every current substantive governed
file is loaded conservatively with a warning. No payload; stdout is injected by the adapter.
Silent only while `.uninitialised` exists. Stdlib only.
"""
import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GOVERNED_DIRS = ("identity", "operating-rules", "boundaries")
REQUIRED_ALWAYS = (
    "SHARED.md",
    "identity/README.md",
    "operating-rules/README.md",
    "boundaries/README.md",
    "identity/principal.md",
    "boundaries/boundaries.md",
)
CORE_ORDER = REQUIRED_ALWAYS[:4]
ENTRY_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}) \| ([^|]+) \| (.+) \| window: (.+)$")
CLOSES_RE = re.compile(r"closes (\d{4}-\d{2}-\d{2})")


def split_frontmatter(text):
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


def substantive(text):
    meta, body_start = split_frontmatter(text)
    if meta is None or "> Blank by design" in text:
        return False
    body = text.splitlines()[body_start:]
    kept, in_comment, in_related = [], False, False
    for line in body:
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
        if in_related or stripped.startswith("#") or not stripped:
            continue
        kept.append(stripped)
    return bool(kept)


def safe_store_file(root, path):
    resolved = path.resolve(strict=True)
    if resolved != root and root not in resolved.parents:
        raise OSError(f"{path.relative_to(root)} resolves outside the configured store")
    if not resolved.is_file():
        raise OSError(f"{path.relative_to(root)} is not a regular file")
    return resolved


def governed_paths(root):
    paths = ["SHARED.md"]
    for directory in GOVERNED_DIRS:
        folder = (root / directory).resolve(strict=True)
        if folder != root and root not in folder.parents:
            raise OSError(f"{directory}/ resolves outside the configured store")
        if not folder.is_dir():
            raise OSError(f"{directory}/ is not a directory")
        paths.extend(path.relative_to(root).as_posix()
                     for path in sorted((root / directory).glob("*.md")))
    return paths


def select_always(root):
    """Return (ordered relative paths, warnings) for deterministic injection."""
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise OSError("configured store path is not a directory")
    records, warnings = {}, []
    for rel in governed_paths(root):
        path = root / rel
        try:
            text = safe_store_file(root, path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise OSError(f"cannot read {rel}: {exc}") from exc
        meta, _ = split_frontmatter(text)
        if meta is None:
            raise ValueError(f"{rel} has malformed frontmatter")
        records[rel] = (meta, text, substantive(text))

    missing_required = sorted(set(REQUIRED_ALWAYS) - set(records))
    if missing_required:
        raise ValueError("required always file(s) missing: " + ", ".join(missing_required))

    incomplete_load = sorted(rel for rel, (meta, _, _) in records.items()
                             if meta.get("load") not in ("always", "triggered"))
    if incomplete_load:
        warnings.append("loading metadata is incomplete or invalid; conservatively loading all current "
                        "substantive governed files")
    selected = set()
    for rel, (meta, _, has_body) in records.items():
        if rel in CORE_ORDER and (meta.get("status") != "current" or not has_body):
            raise ValueError(f"{rel} required core file must be current and substantive")
        if meta.get("status") == "current" and not has_body:
            raise ValueError(f"{rel} has status current but a blank body")
        if meta.get("status") != "current":
            continue
        if incomplete_load or meta.get("load") == "always":
            selected.add(rel)
        if rel in REQUIRED_ALWAYS and meta.get("load") != "always":
            selected.add(rel)
            warnings.append(f"{rel} is required always but declares load: {meta.get('load', 'missing')}")
    ordered = [rel for rel in CORE_ORDER if rel in selected]
    ordered.extend(sorted(selected - set(ordered)))
    return ordered, sorted(set(warnings))


def ledger_open_windows(root=ROOT):
    path = Path(root) / "CHANGES.md"
    if not path.exists():
        return []
    today, output = datetime.date.today(), []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = ENTRY_RE.match(line.strip())
        if not match or not match.group(4).strip().startswith("open"):
            continue
        closes = None
        close_match = CLOSES_RE.search(match.group(4))
        if close_match:
            try:
                closes = datetime.date.fromisoformat(close_match.group(1))
            except ValueError:
                pass
        output.append((match.group(1), match.group(2).strip(), match.group(3).strip(),
                       closes, bool(closes and closes < today)))
    return output


def table_rows(path, placeholder="_none yet_"):
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if (not cells or not cells[0] or set(cells[0]) <= set("-: ")
                or cells[0].lower() in ("id", "workspace") or placeholder in cells[0]):
            continue
        rows.append(cells)
    return rows


def open_handoffs(root=ROOT):
    path = Path(root) / "_coordination" / "dashboard.md"
    if not path.exists():
        return []
    lines, capturing = [], False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("## "):
            capturing = line.strip() == "## Open handoffs"
            continue
        if capturing:
            lines.append(line)
    rows = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|"):
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if (cells and cells[0] and not set(cells[0]) <= set("-: ")
                    and cells[0].lower() != "id" and "_none yet_" not in cells[0]):
                rows.append(cells)
    return rows


def main():
    try:
        json.load(sys.stdin)
    except Exception:
        pass
    if (ROOT / ".uninitialised").exists():
        return 0
    try:
        selected, warnings = select_always(ROOT)
    except (OSError, ValueError) as exc:
        print("Shared-context WARNING: safe loading could not be established "
              f"({exc}). Consequential work must wait for manual Shared-context review.")
        return 1

    lines = []
    for rel in selected:
        lines.append(f"<<< shared-context:{rel} >>>")
        lines.append(safe_store_file(ROOT.resolve(strict=True), ROOT / rel)
                     .read_text(encoding="utf-8").rstrip())
        lines.append(f"<<< end shared-context:{rel} >>>")
    for warning in warnings:
        lines.append(f"Shared-context WARNING: {warning}; run tools/shared-lint.py.")

    windows = ledger_open_windows()
    handoffs = open_handoffs()
    roster = table_rows(ROOT / "_coordination" / "roster.md")
    lines.append("[<<STORE_NAME>> store] SHARED.md governs shared-scope context and edits.")
    if windows:
        parts = []
        for date, who, summary, closes, overdue in windows[:5]:
            flag = " OVERDUE" if overdue else ""
            when = f"closes {closes}" if closes else "no close date"
            parts.append(f"{date} {who}: {summary[:70]} ({when}{flag})")
        lines.append(f"Open objection windows ({len(windows)}): " + "; ".join(parts))
    if handoffs:
        parts = [f"{row[0]}: {row[2][:60]}" if len(row) > 2 else row[0] for row in handoffs[:5]]
        lines.append(f"Open handoffs ({len(handoffs)}): " + "; ".join(parts))
    lines.append(f"Roster: {len(roster)} workspace(s) plugged in.")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
