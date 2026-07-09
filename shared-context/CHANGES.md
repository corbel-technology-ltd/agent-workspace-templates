# Shared profile changelog

Append-only ledger of every change to this store. One trailer line per change, **newest first**,
directly under the marker line. Format (machine-checked by `tools/shared-lint.py`):

```text
YYYY-MM-DD | <workspace or agent> | <one-line summary> | window: open (closes YYYY-MM-DD) | closed | n/a (<reason>)
```

An entry's date, author, and summary are immutable. The **one** permitted edit to a past entry is
its `window:` field flipping `open` -> `closed` exactly once, when the objection window lapses with
no objection. Everything else - a correction, a retraction, an objection - is a NEW entry naming
what it addresses. The protocol (windows, sign-off, disagreement) is
[`_meta/governance.md`](_meta/governance.md); the mutable who-owes-what counterpart is
[`_coordination/dashboard.md`](_coordination/dashboard.md).

<!-- ledger: append new entries directly below this line, newest first -->
