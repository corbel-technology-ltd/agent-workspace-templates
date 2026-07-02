---
id: <<workspace_slug>>.template.research-signal
name: Research signal — fill-in template
type: template
layer: C2
status: current
owner: shared
created: <<CREATED_DATE>>
staging: v1-now
tags: [template, research-signal, intel, observational, source-or-abstain]
related:
  - {ref: 30_schemas/memory-card.md, dimension: what, polarity: enables}
  - {ref: 30_schemas/opportunity.md, dimension: why, polarity: enables}
  - {ref: 30_schemas/event.md, dimension: how, polarity: derived_from}
  - {ref: 70_integrations/README.md, dimension: where, polarity: explains}
---

# Research signal — fill-in template

One captured signal: something observed outside the workspace (a statute change, a market move,
a customer pain, a sentiment shift) that might matter to the entity. This is the **capture-back**
entry for the research/intel fold-in (`70_integrations/README.md`).

A research signal is not yet knowledge. It earns its place by **source-or-abstain**: a signal with
no link, or a claim stronger than its source, is logged as `confidence: low` with the gap named,
never dressed up as fact. Capture is cheap; promotion is gated.

**Where it goes next:**

- File the signal as a journal entry (`30_schemas/event.md`) — that is the durable, immutable record.
- A signal seen **twice or more** in the journal is eligible to mint an **observational atom**
  (`30_schemas/memory-card.md`); the reaper does this, you do not hand-promote one-offs.

- A **strong** signal (high confidence, A/B source-tier, a clear buyer + workaround) is also fed into
  the **opportunity** worksheet (`30_schemas/opportunity.md`) for scoring. Weak signals stay parked.

This is **signpost, don't advise**: record the implication and a suggested action; the founder decides.

---

## Fill-in

```markdown
# Signal: <one-line, plain-English what changed>

- **Date observed:** YYYY-MM-DD
- **Date of the event itself:** YYYY-MM-DD   <!-- if different from observed; else "same" -->
- **Signal:** <one sentence. The single thing that is now true or has moved. One claim only.>

- **Source:** <title> — <url>
  <!-- A primary source where one exists (the statute, the official guidance, the standards body,
       the company's own page). A commentary or news piece is secondary; name it as such. -->
- **Source-tier:**  A primary | B official-secondary | C reputable-press | D forum/anecdote/unverified

- **Sector tags:** [...]        <!-- empty if cross-sector -->
- **Jurisdiction tags:** [uk, eu, global, ...]

- **Implication for the entity:** <2-3 sentences. Why this could matter to us or to the wedge.
  Mark inference vs fact plainly. -->

- **Confidence:** low | medium | high
  <!-- high only with an A/B source AND a clear, dated, verified claim. If the source is thinner
       than the claim, drop to low and write the gap below. -->
- **What is NOT yet verified:** <the open question, the missing dimension, the thing to check.
  Write "none" only if you genuinely have the primary source in hand.>

- **Suggested action:** observe-only | mint-atom-on-recurrence | feed-opportunity-worksheet | escalate-to-founder
- **Why that action:** <one line tying the action to the confidence + source-tier above.>
```

---

## Worked example

```markdown
# Signal: A new standard sets a hard compliance deadline for one product category

- **Date observed:** YYYY-MM-DD
- **Date of the event itself:** YYYY-MM-DD
- **Signal:** The new amendment's no-grandfather deadline applies to NEW categories only, not to
  every existing record.

- **Source:** the standard's publication — the standards body's page (primary)
- **Source-tier:** A primary

- **Sector tags:** [<sector>]
- **Jurisdiction tags:** [uk]

- **Implication for the entity:** The wedge is real but narrower than the trade press implies. Our
  framing should signpost the precise scope, not the scare version. Strengthens the wedge as a lens,
  not a separate offering.

- **Confidence:** high
- **What is NOT yet verified:** none — claim checked against the primary publication.

- **Suggested action:** feed-opportunity-worksheet
- **Why that action:** An A-tier source plus a clear dated buyer trigger clears the strong-signal bar.
```

## Rules

1. **One signal per file.** If the "Signal" line needs an "and", it is two signals.
2. **No claim above its tier.** A D-tier rumour cannot be `confidence: high`. Name the gap instead.
3. **Capture is not promotion.** Filing a signal does not mint an atom or open an opportunity;
   those are separate, gated steps (reaper for atoms, founder review for opportunities).

4. **No external action from a signal alone.** Reaching out to a market or buyer on the strength
   of a signal is a consequential action and is gated to founder approval (see the safety gate).

## Related

- [Memory card (atom) schema](../30_schemas/memory-card.md)
- [Opportunity object schema](../30_schemas/opportunity.md)
- [Journal event schema](../30_schemas/event.md)
- [Integrations — what-runs-where map (instance-specific slots)](../70_integrations/README.md)
