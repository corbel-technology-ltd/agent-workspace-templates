---
id: <<workspace_slug>>.register.measurement
name: Measurement register
type: register
layer: C1
status: current
owner: shared
created: <<CREATED_DATE>>
staging: v1-now
tags: [register, measurement, north-star, feedback-labels, inward-signal]
related:
  - {ref: 50_registers/decision-log.md, dimension: what, polarity: derived_from}
  - {ref: 60_workflows/weekly-review.md, dimension: how, polarity: explains}
  - {ref: 30_schemas/decision-packet.md, dimension: what, polarity: explains}
---

# Measurement register

What the control plane is graded on. Hand-tracked, weekly, by the founder during the
[weekly review](../60_workflows/weekly-review.md). No dashboard, no software. Full metric
instrumentation (a large metric set, an attention-score formula, automated counters) is **deferred**
behind the value-gate (design-spec §9); it is not absence, it is sequencing.

This register is the **inward signal**: it tells the system whether preparation is actually
saving founder attention, and feeds the reaper as normative learning. Numbers are estimates, not
telemetry. We are honest about that (source-or-abstain applies to our own metrics too).

## North Star

**Founder decisions made from prepared packets per week.**

One number. It rises when the system does its job: turning raw inbound into
[Decision Packets](../30_schemas/decision-packet.md) the founder can act on quickly. It does not
reward volume of packets, only decisions actually *taken* off them. A week of fifty packets and
two decisions is a worse week than five packets and five decisions.

## Hand-tracked starter set (6 metrics)

Counted weekly from the [decision log](decision-log.md) and the run folders. Keep the table; add a
dated row each weekly review.

| Metric | What it counts | Source | Reads as |
|---|---|---|---|
| **North Star** | Founder decisions taken from prepared packets this week | `decision-log.md` | higher = better |
| **Approval rate** | Approved packets / total packets decided | `decision-log.md` | a calibration signal, not a target (see below) |
| **Manual-override rate** | Decisions where the founder ignored the recommendation and chose otherwise | `decision-log.md` | high = packets are misreading priorities |
| **Missed-critical-item count** | Things that needed the founder but never reached a packet (caught late) | weekly review recall | the most important number; target 0 |
| **False-alert count** | Items escalated as needing the founder that did not | review of `decision-queue` | high = batching threshold too low |
| **Hours-saved estimate** | Founder's rough estimate of time the prepared work saved this week | founder judgement | directional only, never precise |

## Weekly readings

| week_of | North Star | Approval rate | Override rate | Missed-critical | False-alert | Hours saved |
|---|---|---|---|---|---|---|
| (none yet) | | | | | | |

### Reading the set

- **Missed-critical and false-alert are the load-bearing pair.** They bound the system at both
  ends: missed-critical is the recall failure (the gate let something through unprepared);
  false-alert is the precision failure (anti-noise batching is miscalibrated). Both feed
  `autonomy-and-gates` tuning, never silently.

- **Approval rate is a calibration signal, not a goal.** Near 100% means the system only surfaces
  safe-to-approve work, or the founder is rubber-stamping; near 0% means recommendations are
  off. There is no good fixed value; watch the trend against override-rate.

- **No metric is allowed to override a hard invariant.** A low false-alert count never justifies
  withholding an item that needs the founder. source-or-abstain and human authority win.

## Founder Feedback Labels

The controlled vocabulary the founder tags a decided packet with. One or more labels per packet,
written on the packet and into the [decision log](decision-log.md). These are the **inward signal's
raw input**: recurring labels are reaped into normative atoms
(`20_memory/long-term/`) that retune preparation. Do not invent new labels ad hoc; if a new failure
mode recurs, propose adding it here as a doctrine diff.

| Label | Means | Feeds |
|---|---|---|
| **Useful** | The packet prepared the decision well; acted on it as-shaped | reinforces current preparation |
| **Wrong priority** | Surfaced, but ranked above / below what mattered | priority weights, manual-override rate |
| **Bad tone** | Right content, wrong register or framing | normative tone preferences |
| **Too verbose** | Buried the decision in detail; should have been tighter | brief/packet length norms |
| **Should have escalated** | Handled or batched something that needed the founder sooner | missed-critical count, the gate |

A packet with no label is an unfinished review. The weekly pass tallies label frequency; any label
crossing its recurrence bar (`20_memory/homeostasis.yml`) becomes a candidate preference atom.

## What this is not

- Not a KPI dashboard. Hand-tracked, weekly, deliberately small.
- Not automated. No counters, no scoring formula, no instrumentation pipeline; all deferred.
- Not a performance target on the founder. It grades the **system's** preparation, not the person.

## Related

- [Decision log (append-only)](decision-log.md)
- [Weekly review — the once-a-week scan, reap, and re-prioritise](../60_workflows/weekly-review.md)
- [Decision Packet schema](../30_schemas/decision-packet.md)
