# Registry ledger

Append-only history of the stock: every pack (version bump), every capability added or retired.
One line per change, **newest first**, directly under the marker line. Format:

```text
YYYY-MM-DD | <actor or action> | <what changed> | <follow-up or note>
```

Never edit or delete an entry - a correction is a new entry. `chandler.py pack --write-ledger`
appends its own line; everything else is written by hand in the same shape. The mutable
counterpart is the live drift report (`python3 core/chandler.py fleet`), computed, never stored.

<!-- ledger: append new entries directly below this line, newest first -->

2026-07-11 | pack | onboarding-engine v6 packed from Folder-Agent-Workspace-Template-v6 (1 file(s) changed) | install to the rest of the fleet to close drift

2026-07-11 | pack | onboarding-engine v5 packed from tmp.L20JUrXkZH (1 file(s) changed) | install to the rest of the fleet to close drift

2026-07-02 | pack | scrub-check v2 packed from Folder-Agent-Workspace-Template (1 file(s) changed) | install to the rest of the fleet to close drift

2026-07-02 | pack | onboarding-engine v4 packed from Folder-Agent-Workspace-Template (1 file(s) changed) | install to the rest of the fleet to close drift

2026-07-02 | pack | gen-related v2 packed from Folder-Agent-Workspace-Template (1 file(s) changed) | install to the rest of the fleet to close drift

2026-07-02 | pack | onboarding-engine v3 packed from Folder-Agent-Workspace-Template (1 file(s) changed) | install to the rest of the fleet to close drift

2026-07-02 | pack | onboarding-engine v2 packed from Folder-Agent-Workspace-Template (1 file(s) changed) | install to the rest of the fleet to close drift

2026-07-02 | pack | agnostic-check v2 packed from Folder-Agent-Workspace-Template (1 file(s) changed) | install to the rest of the fleet to close drift

2026-07-02 | stocked | seed capabilities v1: scrub-check, okf-check, gen-related, agnostic-check, onboarding-engine (the FAW family's shared tools) | family templates vendor these; family-check verifies against this registry
