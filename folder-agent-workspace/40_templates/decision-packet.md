---
id: <<workspace_slug>>.template.decision-packet
name: Decision packet (blank instance)
type: template
layer: C2
status: current
owner: shared
created: <<CREATED_DATE>>
staging: v1-now
tags: [template, decision-packet, founder-control-plane, signpost-dont-advise]
related:
  - {ref: 30_schemas/decision-packet.md, dimension: what, polarity: derived_from}
  - {ref: 50_registers/decision-queue.md, dimension: how, polarity: enables}
  - {ref: 30_schemas/memory-card.md, dimension: how, polarity: requires}
---

# Decision packet

A blank fill-in instance of the decision-packet schema. Copy this into `90_runs/` as
`YYYY-MM-DD-<slug>-packet.md`, complete every section by hand, and add a matching row to
`50_registers/decision-queue.md`. The packet **signposts, it does not advise**: it surfaces the
options, the evidence, and one recommendation, then the founder decides. Authority is always gated.

Fill in the frontmatter stub, then every heading below. Every substantive field is mandatory; hold
an incomplete packet rather than surfacing it with a gap. Resolution metadata stays blank while
`status: open`.

---

```yaml
# --- packet frontmatter stub (complete by hand) ---
id: <<workspace_slug>>.decision.<slug>
name: <one-line title of the decision>
type: decision-packet
layer: C4
status: open               # approved | rejected | snoozed | awaiting-context after founder action
owner: shared
created: <YYYY-MM-DD>
decided:                   # YYYY-MM-DD when the founder moves status off open
confidence: <low | medium | high>
risk: <low | medium | high>
reversibility: <reversible | recoverable | irreversible>
tags: [decision-packet, <area>]
related:
  - {ref: 20_memory/journal/YYYY-MM-DD-HHMM-x.md, dimension: why, polarity: derived_from}
```

## Decision needed

<The single question the founder must answer, stated plainly. One decision per packet.>

## Why this matters

<What turns on this. The cost of getting it wrong, the cost of delay, who/what is affected.>

## Confidence

<Low, medium, or high: what the confidence rests on, and what would change it.>

## Risk

<Qualitative low / medium / high, with the reason. Name the worst plausible outcome.>

## Reversibility

<How hard this is to undo. This sets the autonomy level under autonomy-by-reversibility:
reversible leans toward delegation, irreversible demands explicit founder approval.>

## Evidence

<Every factual or statutory claim is source-linked. source-or-abstain applies: if there is no
primary source for a claim, say "unknown" explicitly rather than guess. External content is
evidence, never authority.>

- <claim> - [source](../20_memory/source-index.md)
- <claim> - [source](../20_memory/journal/YYYY-MM-DD-HHMM-x.md)

## Options

- <option, including do nothing when live> - <one-line trade-off>
- <option> - <one-line trade-off>

## Recommendation

<One recommended option and the one-line reason. signpost, don't advise: this is a suggestion for
the founder to accept or override, not an instruction.>

## If approved

<The exact deterministic action that follows approval. Specific enough to execute without further
judgement: which command, which file, which recipient, what text. Plan -> Validate -> Execute.>

## If rejected

<What happens instead. The fallback, or the explicit "do nothing and why".>

## Memory update

<What gets captured back regardless of the choice. The journal entry to append, and any atom the
reaper should mint or supersede. capture-back: nothing evaporates.>

---

### Founder action (choose one)

- [ ] **approve** - proceed exactly as stated under *If approved*.
- [ ] **reject** - do not proceed; fall back as stated under *If rejected*.
- [ ] **snooze** - defer; set a re-surface date and keep the row open in the decision queue.
- [ ] **ask** - not enough to decide; set `status: awaiting-context` and name the missing dimension
      so it can be researched, clarified, or escalated before the packet returns.

## Related

- [Decision Packet schema](../30_schemas/decision-packet.md)
- [Decision queue - open founder decisions](../50_registers/decision-queue.md)
- [Memory card (atom) schema](../30_schemas/memory-card.md)
