#!/usr/bin/env python3
"""Session-end reflex: append a terse L1 session-end event to the journal.

Captures workspace state (git status + last commit) as an immutable journal entry for the reaper
to fold. Silent. Append-only: never overwrites an existing entry.

Neutral hook contract (see core/RUNTIMES.md). Reads ONE JSON object on stdin:
    {"reason": "<why the session ended>", "session_id": "<opaque id, may be empty>"}
Both fields optional. The workspace root is taken from the <<WORKSPACE_ROOT_ENV>> env var if set,
else inferred from this file's location (repo root = two levels up from core/hooks/).
"""
import sys, os, json, subprocess, datetime, hashlib
from pathlib import Path

ROOT = Path(os.environ.get("<<WORKSPACE_ROOT_ENV>>") or Path(__file__).resolve().parents[2])
JOURNAL = ROOT / "20_memory" / "journal"
AGENT = "<<agent_slug>>"            # lowercase agent handle for the `who` field
WORKSPACE = "<<workspace_slug>>"    # lowercase workspace handle for the `where` field


def sh(args):
    try:
        return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return ""


def main():
    if (ROOT / ".uninitialised").exists():
        return  # not onboarded yet — don't write a journal entry full of unresolved <<tokens>>
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    reason = data.get("reason") or "other"
    sid = (str(data.get("session_id") or ""))[:8]
    now = datetime.datetime.now(datetime.timezone.utc)
    stamp = now.strftime("%Y-%m-%d-%H%M")
    status = sh(["git", "status", "--short"])
    last = sh(["git", "log", "-1", "--format=%h %s"]) or "(none)"
    JOURNAL.mkdir(parents=True, exist_ok=True)
    suffix = sid or hashlib.sha1((stamp + last).encode()).hexdigest()[:8]
    fn = JOURNAL / f"{stamp}-session-{suffix}.md"
    if fn.exists():  # append-only: do not overwrite
        sys.exit(0)
    changed = status if status else "(working tree clean)"
    fn.write_text(
        f"""---
id: journal.{stamp}-session-{suffix}
type: observation
who: [{AGENT}]
what: "Session ended ({reason}); workspace state captured."
where: [{WORKSPACE}-workspace]
when: {now.isoformat()}
source_type: system
trust: trusted
---

# Session end digest

- reason: {reason}
- last commit: {last}
- working tree at session end:

```text
{changed}
```

Raw L1 event appended by the SessionEnd hook. The reaper folds and compresses; do not edit.
""")
    sys.exit(0)


if __name__ == "__main__":
    main()
