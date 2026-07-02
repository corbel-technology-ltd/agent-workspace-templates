---
id: <<workspace_slug>>.template.opportunity
name: Opportunity template (blank fill-in instance)
type: template
layer: C2
status: current
owner: shared
created: <<CREATED_DATE>>
staging: v1-now
tags: [template, opportunity, wedge, validation, fill-in]
related:
  - {ref: 30_schemas/opportunity.md, dimension: what, polarity: derived_from}
  - {ref: 40_templates/research-signal.md, dimension: why, polarity: derived_from}
  - {ref: 30_schemas/decision-packet.md, dimension: how, polarity: enables}
---

# Opportunity template

A blank fill-in instance of the opportunity schema (`30_schemas/opportunity.md`), to complete by
hand. Copy this file into `90_runs/` as `YYYY-MM-DD-opp-<slug>.md`, fill every field, score it on
the worksheet, then either kill it or raise a Decision Packet (`30_schemas/decision-packet.md`) to
pursue it. **source-or-abstain:** any market/legal/factual claim cites a journal entry or a primary
source; absence of a source is an explicit "I don't know", not a guess.

Replace the prompts below. Delete bracketed guidance once filled. Leave nothing as "TBD" — an empty
field is a knowledge gap; log it in `20_memory/knowledge-gaps.md` rather than inventing an answer.

## Frontmatter for the filled instance

```yaml
---
id: <<workspace_slug>>.opportunity.<slug>
name: <short opportunity name>
type: opportunity
layer: C4
status: current
owner: shared
created: YYYY-MM-DD
tags: [opportunity, <sector>, <wedge-tag>]
sources: [journal/YYYY-MM-DD-HHMM-<slug>.md#L0-0]   # >=1 journal/primary ref per evidenced claim
related:
  - {ref: 20_memory/long-term/<pain-atom>.md, dimension: why, polarity: derived_from}
---
```

## 1. Pain

<!-- The specific job/frustration, whose it is, and how often it bites. One sentence. Source it. -->

- **Who has it:**
- **The pain (in their words):**
- **Frequency / severity:**
- **Evidence:**  <!-- journal ref or primary source; if none, mark [VERIFY] and stop here -->

## 2. Current workaround

<!-- What they do today instead. The status quo is the real competitor. -->

- **How it is handled now:**
- **What that costs them (time/money/risk):**
- **Why the workaround persists:**

## 3. Wedge

<!-- The narrow first entry: the one thing the entity does first that is sharper than the workaround. -->

- **The wedge:**  <!-- the entity's locked entry angle (from canon), or why this deviates -->
- **Why this entity specifically (unfair advantage / fit to doctrine):**
- **AI-minimisation read:** <!-- which 60% is deterministic plumbing, where AI earns its 20% -->

## 4. Buyer

<!-- Who pays, who decides, who blocks. Not the same as the user. -->

- **Economic buyer:**
- **User:**
- **Reachable via:** <!-- existing channel, e.g. the email loop, an intel signal -->
- **Willingness/ability to pay (evidence):**

## 5. MVP

<!-- The smallest deliverable that tests the wedge by hand. Workspace-first; no software assumed. -->

- **Smallest testable offer:**
- **Built/run how (by hand now):**
- **Deferred software, if any:** <!-- name the value-gate it sits behind; do not build speculatively -->

## 6. Validation

<!-- The cheapest experiment that could kill this. Pre-commit to the kill criterion. -->

- **Hypothesis (falsifiable):**
- **Test:**
- **Kill criterion (what result ends it):**
- **Signal to date:**

## 7. Critique (source-or-abstain, signpost don't advise)

<!-- Argue against yourself. The strongest reason this fails. List unknowns honestly. -->

- **Strongest reason this fails:**
- **Key assumptions still unproven:**
- **Knowledge gaps:** <!-- log each in 20_memory/knowledge-gaps.md -->

## Scoring worksheet

Score each dimension 1-5 (1 = weak, 5 = strong). Multiply by weight, sum to a total out of 100.
The score is a signpost for triage, not a decision: a high score still routes through a Decision
Packet; a low score is killed and folded back as a lesson.

| Dimension | What a 5 looks like | Weight | Score (1-5) | Weighted (score x weight) |
|---|---|---:|:---:|---:|
| Pain intensity | Acute, frequent, evidenced in the buyer's own words |  5 |  |  |
| Workaround weakness | Status quo is costly and brittle; clear room to beat it |  4 |  |  |
| Wedge sharpness | Narrow, defensible, fits the entity's doctrine and assets |  4 |  |  |
| Buyer reachability | Identified buyer reachable through an existing channel |  3 |  |  |
| Willingness to pay | Evidence of budget and intent, not just interest |  3 |  |  |
| MVP feasibility (by hand) | Testable now, workspace-first, no new software |  3 |  |  |
| Reversibility | Cheap to enter, cheap to exit if the test fails |  2 |  |  |
| Founder fit | Plays to the founder's strengths and the entity's standing |  1 |  |  |
| **Total** |  | **25** |  | **/100** |

Weighted total = sum of the right-hand column (max 100, since max weighted = sum of weights x 5).

### Reading the score (signpost, not a rule)

- **>= 70** — strong: raise a Decision Packet to commit a validation experiment.
- **45-69** — promising: cheapest validation test first; re-score after the signal lands.
- **< 45** — kill: fold the reasoning into `20_memory/journal/` as a decision, mint the lesson.

## Disposition

<!-- Plan -> Validate -> Execute. Reversible-by-default; consequential spend or commitment is gated. -->

- **Decision:** pursue / validate-first / park / kill
- **Score:**  /100
- **Next action (deterministic, exact):**
- **Routed to:** <!-- Decision Packet ref in 90_runs/, or journal decision entry if killed -->
- **Memory update:** <!-- the atom(s) to mint; capture-back so nothing evaporates -->

## Related

- [Opportunity object schema](../30_schemas/opportunity.md)
- [Research signal — fill-in template](research-signal.md)
- [Decision Packet schema](../30_schemas/decision-packet.md)
