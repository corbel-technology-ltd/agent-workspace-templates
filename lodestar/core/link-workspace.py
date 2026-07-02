#!/usr/bin/env python3
"""link-workspace.py - the executable half of the link-in contract (SHARED.md §link-in).

Registers a consuming workspace in _coordination/roster.md (idempotent by workspace name), prints
the boot rule to paste into that workspace's constitution, and prints the ready-made CHANGES.md
trailer (or writes it with --write-changes). Deterministic, stdlib only, local-files only.

Usage:
    python3 core/link-workspace.py --name Acme --path /home/you/acme-workspace --agent aster
    python3 core/link-workspace.py --name Acme --path ... --agent ... --write-changes

Unlinking is a governed edit done by hand (set the roster row's status to `retired`); this script
only adds.
"""
import argparse
import datetime
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "_coordination" / "roster.md"
CHANGES = ROOT / "CHANGES.md"
LEDGER_MARKER = "<!-- ledger: append new entries directly below this line, newest first -->"
PLACEHOLDER_ROW = "| _none yet_ | | | | |"


def fail(msg):
    print(f"link-workspace: {msg}", file=sys.stderr)
    sys.exit(1)


RESERVED_NAMES = {"Workspace", "_none yet_"}  # collide with the table header / placeholder row


def add_roster_row(name, path, agent, today):
    if name in RESERVED_NAMES:
        fail(f"{name!r} is reserved (it is the roster table header/placeholder) - pick another name")
    text = ROSTER.read_text(encoding="utf-8")
    # Idempotency: a row whose first cell is exactly this name means already registered.
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and cells[0] == name:
            if len(cells) >= 3 and (cells[1] != path or cells[2] != agent):
                print(f"link-workspace: note - '{name}' is already on the roster with a different "
                      f"path/agent ({cells[1]} / {cells[2]}); leaving it unchanged. Edit the roster "
                      f"by hand (a governed edit) to change it.", file=sys.stderr)
            return False
    row = f"| {name} | {path} | {agent} | {today} | active |"
    if PLACEHOLDER_ROW in text:
        text = text.replace(PLACEHOLDER_ROW, row, 1)
    else:
        # Append after the roster table header separator.
        m = re.search(r"\| Workspace \| Path \| Agent \| Linked \| Status \|\n\|[-| ]+\|\n",
                      text)
        if not m:
            fail("roster table header not found in _coordination/roster.md")
        text = text[:m.end()] + row + "\n" + text[m.end():]
    ROSTER.write_text(text, encoding="utf-8")
    return True


def changes_line(name, agent, today):
    return (f"{today} | {name} via {agent} | linked workspace '{name}' into the store "
            f"(roster row added; boot rule issued) | window: n/a (link-in registration)")


def write_changes(line):
    text = CHANGES.read_text(encoding="utf-8")
    if line in text:
        return False
    if LEDGER_MARKER not in text:
        fail("ledger marker not found in CHANGES.md")
    text = text.replace(LEDGER_MARKER, LEDGER_MARKER + "\n\n" + line, 1)
    CHANGES.write_text(text, encoding="utf-8")
    return True


BOOT_RULE = """\
> **Load the shared context first.** Read `{store}/SHARED.md`, then `identity/` and
> `operating-rules/`. The store outranks this workspace's local notes on the principal. Check
> `_coordination/dashboard.md` for open handoffs owed to this workspace."""


def main():
    ap = argparse.ArgumentParser(description="Register a workspace in the store roster.")
    ap.add_argument("--name", required=True, help="workspace name (roster key)")
    ap.add_argument("--path", required=True, help="absolute path to the workspace root")
    ap.add_argument("--agent", required=True, help="the workspace's agent name/slug")
    ap.add_argument("--write-changes", action="store_true",
                    help="also append the trailer to CHANGES.md (default: print it only)")
    a = ap.parse_args()

    if "|" in (a.name + a.path + a.agent):
        fail("'|' is not allowed in values (it breaks the roster table)")
    if not Path(a.path).is_absolute():
        fail(f"--path must be absolute, got {a.path!r}")
    if not Path(a.path).is_dir():
        print(f"link-workspace: note - {a.path} does not exist (yet) on this machine; "
              f"registering anyway.", file=sys.stderr)

    today = datetime.date.today().isoformat()
    added = add_roster_row(a.name, a.path, a.agent, today)
    print("roster: " + (f"registered '{a.name}'." if added
                        else f"'{a.name}' already registered - nothing to do."))

    line = changes_line(a.name, a.agent, today)
    if a.write_changes:
        wrote = write_changes(line)
        print("ledger: " + ("trailer appended to CHANGES.md." if wrote
                            else "trailer already present."))
    else:
        print("\nAppend this trailer to CHANGES.md (or re-run with --write-changes):\n")
        print("  " + line)

    print("\nPaste this boot rule into the workspace's constitution "
          "(a Commonplace workspace instead fills SHARED_CONTEXT_PATH at onboarding):\n")
    print(BOOT_RULE.format(store=str(ROOT)))
    print("\nIf the workspace symlinks this store into its tree, make sure its search tooling "
          "follows symlinks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
