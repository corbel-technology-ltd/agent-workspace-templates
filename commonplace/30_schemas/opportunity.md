---
id: <<workspace_slug>>.schema.opportunity
name: Opportunity object schema
type: schema
layer: C2
status: current
owner: shared
created: <<CREATED_DATE>>
staging: v1-now
tags: [schema, opportunity, wedge, validation, scoring, decision-packet]
related:
  - {ref: 30_schemas/decision-packet.md, dimension: why, polarity: enables}
  - {ref: 30_schemas/memory-card.md, dimension: what, polarity: explains}
  - {ref: 30_schemas/event.md, dimension: how, polarity: derived_from}
  - {ref: 70_integrations/README.md, dimension: where, polarity: requires}
---

# Opportunity object schema

A written record of a candidate thing-to-build, scored by hand and ending in a recommendation.
One opportunity per file in `90_runs/`, named `YYYY-MM-DD-opp-<slug>.md`. The body is the
human-readable case; the frontmatter is the machine-checkable footprint. This schema is a
**template, not a build**: it captures one opportunity by hand. It complements any research/intel
engine (`70_integrations/README.md`) and does not duplicate it: the engine surfaces signals; this
object is where a surfaced signal is interrogated and scored. **If an intel pass already renders a
signal into a packet, this file is the template that pass fills in, not a second pipeline.** Every
statutory or factual claim follows **source-or-abstain**; the worksheet is **deterministic**
(AI-minimisation), so the score is reproducible by hand.

## Frontmatter

```yaml
---
id: <<workspace_slug>>.opp.<slug>
type: opportunity
status: candidate | scored | validating | accepted | parked | killed
created: YYYY-MM-DD
sector: [...]                             # optional
score: 0-100                              # from the worksheet below; null until scored
recommendation: pursue | validate-first | park | kill
sources: [journal/YYYY-MM-DD-HHMM-x.md#L4-12, ...]   # MANDATORY for any claimed fact
related:
  - {ref: 90_runs/..., dimension: why, polarity: supports}   # signals, packets, prior opps
---
```

## Fields (the body)

Each field is a heading in the file. Keep entries tight; a field you cannot answer from a source
is left explicitly as **"unknown"** (source-or-abstain), never guessed.

1. **pain** — the specific problem a real buyer has. One sentence. Whose pain, and in what moment.
2. **current_workaround** — what they do today instead (spreadsheet, admin, ignoring it, a rival
   tool). If there is no workaround, the pain may not be real; say so.

3. **wedge** — the narrow first cut that earns trust before anything wider. State the instance's
   locked wedge (if it has one) and how this fits, or why it deviates. The wedge is the entity's
   sharpest first angle, defined in the instance's canon.

4. **buyer** — who pays, by name of role, and from which budget. Distinguish the **buyer** from the
   user if they differ. No buyer = no opportunity.

5. **pain_frequency** — how often the pain bites: per-job, weekly, monthly, annual, one-off
   regulatory deadline. Drives willingness to pay and retention.

6. **MVP** — the smallest thing that relieves the pain enough to charge for, deliverable by hand
   first. State what is explicitly out.

7. **validation_experiment** — one falsifiable test with a stated pass/fail line before any build:
   the smallest move (a conversation, a paid pilot, a landing-page check) that would prove or kill
   the assumption. Name the assumption it tests.

8. **critique** — an adversarial pass on this opportunity's own case. List the strongest reasons it
   fails: who already serves this, why the buyer would not pay, what makes the wedge non-defensible,
   which claim rests on no source. **signpost, don't advise**: surface the case both ways; the
   founder decides. An opportunity with no honest critique is not ready to score.

## Scoring worksheet (deterministic, 0-100, run by hand)

Additive sub-scores with fixed weights. Score each dimension 0-5 against the rubric, multiply by
its weight, sum. The weights total 100, so the result is already a 0-100 score. **No LLM judgement
in the arithmetic** (AI-minimisation): a reasoning layer may *suggest* a sub-score with a cited
reason, but the founder sets the number and the sum is mechanical. Record every sub-score and its
one-line justification in the file so the total is auditable.

| # | Sub-score (0-5) | Weight | Max | Rubric anchor (0 vs 5) |
|---|---|---|---|---|
| 1 | Pain severity | 5 | 25 | 0 = mild annoyance · 5 = blocks work / risks penalty |
| 2 | Pain frequency | 3 | 15 | 0 = one-off · 5 = recurs every job / every month |
| 3 | Buyer clarity & budget | 4 | 20 | 0 = no named payer · 5 = named role, owns the budget, can sign |
| 4 | Wedge fit & defensibility | 3 | 15 | 0 = off-wedge, commodity · 5 = on the locked wedge, hard to copy |
| 5 | Evidence quality | 2 | 10 | 0 = assumed · 5 = primary sources / observed real buyers |
| 6 | Time-to-MVP (cost, inverse) | 1 | 5 | 0 = months of build · 5 = deliverable by hand this week |
| 7 | Reversibility (inverse) | 2 | 10 | 0 = hard to exit, big sunk cost · 5 = cheap to try, cheap to stop |
|   | **Total** |  | **100** | |

`score = (s1*5) + (s2*3) + (s3*4) + (s4*3) + (s5*2) + (s6*1) + (s7*2)`

Reversibility is scored here as well as gating the action later — a cheap, reversible bet is
worth more under **autonomy-by-reversibility** because it can be tried without a heavy approval.

### Bands → recommendation

- **70-100 → pursue** — strong case; proceed to a Decision Packet to commit a first move.
- **45-69 → validate-first** — promising but assumption-heavy; run `validation_experiment` before
  committing spend, then re-score.

- **20-44 → park** — keep the file; revisit if a new signal raises a sub-score.
- **0-19 → kill** — record why in `critique`; do not silently delete (capture-back).

### Hard floors (override the band)

- **Evidence quality = 0** (every claim assumed, no source) → cannot exceed **validate-first**,
  whatever the total. Source-or-abstain is a hard invariant; it outranks a high arithmetic score.

- **Buyer clarity = 0** (no named payer) → **park** at best.

## Feeds a Decision Packet

A `pursue` opportunity does **not** authorise spend by itself. It feeds
[`decision-packet.md`](decision-packet.md): the score and its sub-scores become the packet's
`evidence` (source-linked), the band becomes the `recommendation`, the `validation_experiment`
becomes the `if_approved` deterministic first action, and `critique` populates `risk` /
`if_rejected`. The founder approves the packet; the score never commits an action on its own (**Plan
→ Validate → Execute**).

## Memory hand-off

On a terminal decision (`accepted` / `parked` / `killed`), write a journal entry ([`event.md`](event.md)).
The reaper later derives an `observational` atom ([`memory-card.md`](memory-card.md)) capturing the
lesson, so a killed opportunity is not re-litigated from scratch.

## Worked stub

```markdown
---
id: <<workspace_slug>>.opp.contractor-evidence-pack
type: opportunity
status: scored
created: YYYY-MM-DD
sector: [<sector>]
score: 71
recommendation: pursue
sources: [journal/YYYY-MM-DD-HHMM-radar.md#L1-20]
---

## pain
A small operator cannot quickly produce a defensible evidence trail for completed work when a
client, insurer, or assessor asks months later.

## current_workaround
Photos on a phone plus paper records in a folder; reconstructed by memory under pressure.

## wedge
The instance's locked entry angle (defined in canon); state how this fits it.

## buyer
The owner-operator; pays from operating budget; can sign without a committee.

## pain_frequency
Per-job at hand-off, with sharp spikes around regulatory deadlines.

## MVP
A by-hand structured job record that renders a one-page evidence pack on request. No software.

## validation_experiment
Offer five operators a paid pack assembled by hand. Pass = >=2 pay before delivery.
Tests the assumption that the pain is worth money, not just sympathy.

## critique
Generic doc tools already store photos and records; defensibility, not storage, must be the wedge.
No paid pilot yet, so the buyer-will-pay claim is currently unknown.

## Scoring
1 Pain severity 4 x5 = 20  (blocks a clean hand-off, can risk disputes)
2 Pain frequency 4 x3 = 12  (per-job)
3 Buyer clarity 4 x4 = 16  (named owner, owns budget; not yet a signed payer)
4 Wedge fit 5 x3 = 15  (on the locked wedge)
5 Evidence quality 2 x2 = 4  (one verified signal; no observed buyers yet)
6 Time-to-MVP 4 x1 = 4  (by-hand pack this week)
7 Reversibility 5 x2 = 10  (cheap to try, cheap to stop)
Total = 81  -> pursue, but evidence is thin: run the experiment before committing build.
```

## Related

- [Decision Packet schema](decision-packet.md)
- [Memory card (atom) schema](memory-card.md)
- [Journal event schema](event.md)
- [Integrations — what-runs-where map (instance-specific slots)](../70_integrations/README.md)
