#!/usr/bin/env python3
"""Neutral reflex: enforce the journal append-only/immutable invariant.

Blocks any operation that would edit, overwrite, delete, or move an EXISTING entry under
20_memory/journal/. Creating a NEW journal entry is allowed (append-only). Silent unless it blocks.
Fail-open on any parse error so it never wedges the agent on its own bug.

Neutral hook contract (see core/RUNTIMES.md). Reads ONE JSON object on stdin:

    {"op": "modify" | "create-or-overwrite" | "shell", "path": "<file>", "command": "<shell line>"}

  - "modify"              an in-place edit of an existing file (path required)
  - "create-or-overwrite" a whole-file write that may replace an existing file (path required)
  - "shell"               an arbitrary command line (command required)

Exit 0 allows the operation. Exit 2 with a reason on stderr blocks it - the runtime adapter maps
exit 2 to its runtime's blocking mechanism. Unknown ops are allowed (fail-open).

The workspace root is taken from the <<WORKSPACE_ROOT_ENV>> env var if set, else inferred from this
file's location (repo root = two levels up from core/hooks/).
"""
import sys, os, json, re
from pathlib import Path

ROOT = Path(os.environ.get("<<WORKSPACE_ROOT_ENV>>") or Path(__file__).resolve().parents[2])
JOURNAL = (ROOT / "20_memory" / "journal").resolve()


def _resolve(p):
    """Resolve a path against the workspace ROOT (never the process CWD), so the
    guard behaves identically whatever directory the runtime invokes it from."""
    rp = Path(p).expanduser()
    if not rp.is_absolute():
        rp = ROOT / rp
    return rp.resolve()


def protected_entry(p):
    """True for an EXISTING immutable journal entry. The journal README and the
    .gitkeep are structure, not entries, so they stay editable (matching the
    optional core/git-hooks/pre-commit guard)."""
    try:
        rp = _resolve(p)
        if not (rp == JOURNAL or JOURNAL in rp.parents):
            return False
        return rp.name not in ("README.md", ".gitkeep")
    except Exception:
        return False


def block(msg):
    sys.stderr.write("[journal-guard] " + msg + "\n")
    sys.exit(2)  # exit 2 = block, per the neutral hook contract


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    op = data.get("op") or ""
    path = data.get("path") or ""
    cmd = data.get("command") or ""

    if op == "modify":
        if path and protected_entry(path):
            block(f"journal/ is append-only and immutable. Refusing to modify an existing journal "
                  f"entry ({path}). A correction or retraction is a NEW journal entry.")
    elif op == "create-or-overwrite":
        if path and protected_entry(path):
            try:
                exists = _resolve(path).exists()
            except Exception:
                exists = False
            if exists:
                block(f"journal/ is append-only. Refusing to overwrite an existing journal entry "
                      f"({path}). Write a NEW entry instead.")
    elif op == "shell":
        # A tripwire, not a sandbox: it catches the common ways a command mutates the
        # journal, but shell evasion is unbounded (globs, unusual tools, interpreters).
        # The durable enforcement is core/git-hooks/pre-commit, which blocks ANY change
        # to an existing entry at commit time regardless of the command that made it.
        if "20_memory/journal" in cmd:
            destructive = (
                re.search(r'\b(rm|mv|cp|dd|truncate|shred|rsync|install|ln)\b', cmd)
                or re.search(r'\btee\b', cmd)
                or re.search(r'sed\s+-i', cmd)
                or re.search(r'(?<!>)>(?!>)\s*[^|&;]*20_memory/journal', cmd)  # single '>' overwrite, not '>>'
            )
            if destructive:
                block("Refusing a shell command that may delete, move, or overwrite journal "
                      "entries (20_memory/journal is append-only). Append a NEW entry instead "
                      "(>> is fine). Note: this is a tripwire; commit-time enforcement is "
                      "core/git-hooks/pre-commit.")
    sys.exit(0)


if __name__ == "__main__":
    main()
