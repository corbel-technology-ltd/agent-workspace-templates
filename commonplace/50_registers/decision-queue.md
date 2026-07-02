---
id: <<workspace_slug>>.register.decision-queue
name: Decision queue — open founder decisions
type: register
layer: C1
status: current
owner: shared
created: <<CREATED_DATE>>
staging: v1-now
tags: [register, decisions, founder, gate, daily-brief]
related:
  - {ref: 30_schemas/decision-packet.md, dimension: what, polarity: explains}
  - {ref: 50_registers/decision-log.md, dimension: when, polarity: derived_from}
  - {ref: 60_workflows/daily-brief.md, dimension: how, polarity: enables}
---

# Decision queue

The one place open founder decisions live. Every item that needs the founder (and only the founder)
arrives here as a row pointing at a prepared **Decision Packet** in `90_runs/`. The daily brief
renders the open rows; nothing else competes for the founder's attention.

This is the live working face of the gate: preparation is automated, **authority is always gated**
(`AGENTS.md` safety gate). The agent may draft, evidence, and recommend; it may not approve its own
packets, and never sends, publishes, pays, or signs without an explicit `approve` here.

## How it runs (by hand)

1. A decision is needed → write a packet against `30_schemas/decision-packet.md`, file it in
   `90_runs/`, add a row below with `status: open`.

2. The daily brief lists every `open` row, newest first, with its risk and packet link.
3. The founder settles each row with one action from the vocabulary below.
4. On `approve`/`reject`, append the outcome to `50_registers/decision-log.md` (append-only) and
   set this row's status accordingly. The row stays here only while it is live; settled rows are
   pruned once logged, so the log is the durable record and this table is the working set.

5. A `snooze` carries a `Review` date; an `ask` carries the missing dimension the packet must
   resolve before it can be decided.

## Action vocabulary (the only four)

- **approve** — sanction the packet's `if_approved` deterministic action. Log it; execute it.
- **reject** — decline. Log the reason; run the packet's `if_rejected`.
- **snooze** — defer to a stated date; the brief re-surfaces it then (anti-noise batching).
- **ask** — not yet decidable. Name the missing evidence or 5W1H dimension; the packet goes back
  for that input rather than being decided on a guess (source-or-abstain).

Mapped status: `approve`→`approved`, `reject`→`rejected`, `snooze`→`snoozed`,
`ask`→`awaiting-context`. A row stays `open` until acted on.

## Open decisions

| id | date | summary | packet | risk | status |
|---|---|---|---|---|---|
| (none yet) | | | | | |

<!-- Row shape, newest first. risk = low | medium | high (qualitative tiers,
     `10_doctrine/autonomy-and-gates.md`). Example:

| dq-YYYY-MM-DD-001 | YYYY-MM-DD | One-line decision_needed | [packet](../90_runs/YYYY-MM-DD-<slug>-packet.md) | medium | open |

-->

## Conventions

- **id:** `dq-YYYY-MM-DD-NNN` (date opened + same-day sequence).
- **risk:** low / medium / high, read straight off the packet (reversibility-weighted).
- **status:** `open` / `approved` / `rejected` / `snoozed` / `awaiting-context`.
- A high-risk or irreversible item is never auto-actioned; it waits here for an explicit
  `approve`. Mandatory-escalation classes (external send, publish, pay, sign) are blocked at the
  gate regardless of how this row reads.

## Related

- [Decision Packet schema](../30_schemas/decision-packet.md)
- [Decision log (append-only)](decision-log.md)
- [Daily brief — the run-by-hand morning assembly](../60_workflows/daily-brief.md)
