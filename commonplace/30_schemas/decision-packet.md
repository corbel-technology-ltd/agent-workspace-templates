---
id: <<workspace_slug>>.schema.decision-packet
name: Decision Packet schema
type: schema
layer: C2
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [schema, decision, human-in-the-loop, signpost-dont-advise, plan-validate-execute]
related:
  - {ref: 10_doctrine/autonomy-and-gates.md, dimension: how, polarity: requires}
  - {ref: 30_schemas/memory-card.md, dimension: what, polarity: derived_from}
  - {ref: 30_schemas/event.md, dimension: why, polarity: derived_from}
  - {ref: 50_registers/decision-queue.md, dimension: where, polarity: enables}
  - {ref: 50_registers/decision-log.md, dimension: where, polarity: enables}
  - {ref: 40_templates/decision-packet.md, dimension: what, polarity: explains}
---

# Decision Packet schema

The standout object of this workspace: a **one-page, human-in-the-loop decision surface**. It is
the data shape that encodes **Plan -> Validate -> Execute** and **signpost, don't advise**.

A packet is the only way a consequential or irreversible action reaches the founder. The agent does
the plan and validate; the packet carries everything the founder needs to commit or decline in one
read, and nothing more. The founder never has to open the source to decide, yet the source is always
one link away. **Preparation is automated; authority is gated** — the packet is where the gate lives.

A filled packet is a working artefact: it lives in `90_runs/` (layer C4) with an open row in
[`../50_registers/decision-queue.md`](../50_registers/decision-queue.md). The verbatim outcome and
the action taken are appended to [`../50_registers/decision-log.md`](../50_registers/decision-log.md).
Fill from the template at [`../40_templates/decision-packet.md`](../40_templates/decision-packet.md).

## Frontmatter

```yaml
---
id: <<workspace_slug>>.decision.<slug>     # stable id; matches the decision-queue row
name: <short imperative title>
type: decision-packet
layer: C4
status: open | approved | rejected | snoozed | needs-info
owner: shared
created: <YYYY-MM-DD>
decided: <date>                            # set when status leaves `open`
tags: [...]
related:
  - {ref: 20_memory/journal/YYYY-MM-DD-HHMM-x.md, dimension: why, polarity: derived_from}
---
```

`status` mirrors the four decision-queue actions plus `needs-info`. A packet never self-resolves;
only the founder moves it off `open`.

## Fields (the one page, in order)

Every field is mandatory. An empty field is a packet that is not ready to surface; hold it, don't
ship it with a gap.

1. **decision_needed** — the single explicit question, phrased as a yes/no or a pick-one. One
   decision per packet. If it needs "and", it is two packets.

2. **why_this_matters** — one or two lines: the consequence of acting and of not acting. What this
   unblocks, what it risks, why it cannot simply batch into the weekly review.

3. **confidence** — `low | medium | high`, with the one phrase that sets it. Under
   **source-or-abstain**, if the evidence does not exist, say so here as an explicit "unknown" and
   set `recommendation` to gather it, rather than dressing a guess as low confidence.

4. **risk** — `low | medium | high` (the qualitative tiers from `autonomy-and-gates.md`), naming
   the worst credible outcome.

5. **reversibility** — `reversible | recoverable | irreversible`. This drives the gate under
   **autonomy-by-reversibility**: the less reversible, the more this packet must be explicit and
   the slower the default. External send / publish / pay / sign is treated as irreversible.

6. **evidence** — the source-linked facts the decision rests on. Each line is one claim plus a link
   into [`../20_memory/journal/`](../20_memory/journal/) or
   [`../20_memory/source-index.md`](../20_memory/source-index.md). No claim without a link; a claim
   with no source is named as a gap, not stated as fact (**source-or-abstain**).

7. **options** — the real choices, each with its one-line trade-off. Include the do-nothing option
   when it is live. No false binaries.

8. **recommendation** — the agent's single recommended option with the reason in one line. This is a
   **signpost, not advice**: the founder still decides; the packet never executes itself.

9. **if_approved** — the EXACT deterministic action that runs on approval: the command, the draft
   to send, the file to write, the register row to change. Verbatim and copy-runnable, with the
   gate it must clear named (e.g. "external send: requires this approval"). This is the Execute
   step pre-computed so approval is one step, not a fresh task.

10. **if_rejected** — what happens on decline: the fallback action, who or what gets told, the loop
    that stays open. Never a dead end.

11. **memory_update** — what gets captured back on resolution: the journal entry to append (shape:
    [`event.md`](event.md)) and any atom to mint or supersede (shape:
    [`memory-card.md`](memory-card.md)). This closes **capture-back**: every decision improves the
    system, and a normative atom mints here on a first explicit preference.

## How it encodes the doctrine

- **Plan** = fields 1-8 (question, stakes, evidence, options, recommendation): assembled before
  the founder is touched.

- **Validate** = fields 4-5 plus `if_approved`'s named gate: the action is checked against
  [`../10_doctrine/autonomy-and-gates.md`](../10_doctrine/autonomy-and-gates.md) before it is offered.

- **Execute** = `if_approved`, run only on approval; **signpost, don't advise** is enforced by
  fields 7-8 (options before recommendation) and by the rule that the packet has no power to act.

## Decision Packet Done (8-point checklist)

A packet may only be surfaced to the founder when all eight hold:

1. The founder can decide **without opening the source** — the page stands alone.
2. The **source is still linked** — every evidence line resolves into `journal/` or
   `source-index.md`, so the claim can be checked in one click.

3. The **question is explicit** — one decision, phrased as yes/no or pick-one, in `decision_needed`.
4. The **action preview is exact** — `if_approved` is verbatim and copy-runnable, not a description
   of what would happen.

5. **Risk and reversibility are stated**, and the matching gate from `autonomy-and-gates.md` is
   named; an irreversible action defaults to slow and explicit.

6. **No unsourced claim is stated as fact** — gaps are named as gaps (**source-or-abstain**);
   confidence reflects evidence, not vibes.

7. **Both branches resolve** — `if_approved` and `if_rejected` each leave the system in a defined
   state; neither is a dead end or a silent drop.

8. **The write-back is named** — `memory_update` says exactly which journal entry and which atom
   the resolution produces, so **capture-back** is not left to chance.

## Related

- [Autonomy & gates — the single decision gate](../10_doctrine/autonomy-and-gates.md)
- [Memory card (atom) schema](memory-card.md)
- [Journal event schema](event.md)
- [Decision queue — open founder decisions](../50_registers/decision-queue.md)
- [Decision log (append-only)](../50_registers/decision-log.md)
- [Decision packet (blank instance)](../40_templates/decision-packet.md)
