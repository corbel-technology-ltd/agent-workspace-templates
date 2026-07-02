---
id: <<workspace_slug>>.register.records
name: Records index — stored documents (evidence plane)
type: register
layer: C1
status: current
owner: shared
created: <<CREATED_DATE>>
staging: v1-now
tags: [register, records, evidence, documents, source-or-abstain]
related:
  - {ref: 50_registers/open-loops.md, dimension: what, polarity: supports}
  - {ref: 20_memory/journal/README.md, dimension: why, polarity: derived_from}
  - {ref: 70_integrations/README.md, dimension: where, polarity: enables}
---

# Records index

The thin index over stored documents: invoices, receipts, statutory filings, contracts, statements,
correspondence worth keeping. The **binary lives off-machine**; this register holds a one-line
pointer so the file never has to be opened to know what it is. Keeps git lean (no binaries in
history) and context cheap (read a row, not a PDF).

## How it works

- **Binary store (off-site):** an off-machine store path (set per instance in `70_integrations/`),
  e.g. `<sync-root>/records/<year>/`. Naming: `YYYY-MM-DD-vendor-slug.ext`. Binaries never enter the
  git workspace.
- **The pointer (here):** one row per document. The row is the summary; the `file` column is the
  path inside the off-site store; `source` links the journal entry (when the document is also an
  event, e.g. a receipt) or names the origin.
- **source-or-abstain:** a row with no `file` and no `source` is unverified.
- **Disclosure (OKF):** this is the index. A document needing more than a row (a contract, a long
  report) graduates to its own stub `.md` linked from here. Most never will.

## Documents

| date | category | summary | key fields | file (off-site store) | source |
|---|---|---|---|---|---|
| (none yet) | | | | | |

## Conventions

- **category:** invoice · receipt · statutory · contract · statement · correspondence · other.
- **file:** path relative to the off-site sync root. Flag a row `(pending)` if the binary is not yet
  in the store.
- Newest first. A document that is also a tracked obligation cross-links its open-loops /
  decision-queue row rather than duplicating it here.

## Related

- [Open loops register (moved)](open-loops.md)
- [Journal — the append-only event log](../20_memory/journal/README.md)
- [Integrations — what-runs-where map (instance-specific slots)](../70_integrations/README.md)
