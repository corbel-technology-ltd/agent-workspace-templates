---
id: <<store_slug>>.calibration-os.readme
name: Calibration OS - living scoped preferences
type: reference
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [calibration, preferences, corrections, raw-mode, living]
related:
  - {ref: SHARED.md, dimension: why, polarity: derived_from}
  - {ref: calibration-os/authority.md, dimension: how, polarity: requires}
  - {ref: calibration-os/corrections.md, dimension: what, polarity: enables}
---

# Calibration OS

A living operating manual that helps agents work the way the principal works - judgement defaults,
quality bar, voice in practice - and that **changes safely over time**. Not a profile, not a
diary: a practical context layer agents load *before* acting, kept honest by a pipeline that
separates "observed once" from "confirmed durable".

## The loop

1. **Observe.** An agent notices a correction ("that doesn't sound like me", a redirected
   decision, a repeated preference). It logs a candidate in
   [`corrections.md`](corrections.md) - it does NOT edit a preference file.
2. **Confirm.** A calibration pass (a short staged interview, or the principal confirming a
   candidate) promotes it: the preference file gains a line, the candidate is marked promoted,
   and the edit follows governance (trailer + window).
3. **Apply, scoped.** Preferences carry their scope; [`authority.md`](authority.md) says what
   beats what when they conflict with instructions or context.

## What lives here

- [`authority.md`](authority.md) - the override hierarchy in day-to-day detail, and **raw mode**
  (the principal's bypass switch).
- [`preferences/`](preferences/voice-and-writing.md) - the durable, confirmed preferences, blank
  by design: [`voice-and-writing.md`](preferences/voice-and-writing.md),
  [`decision-defaults.md`](preferences/decision-defaults.md),
  [`quality-bar.md`](preferences/quality-bar.md). Split a file only when a section earns it.
- [`corrections.md`](corrections.md) - the append-only candidate log feeding the loop.

## Operate lean (important)

Load the minimum a task needs. **Never load blank files** - they cost tokens and add nothing.
Markdown cannot stop an agent doing anything: these files document *intent*; enforcement belongs
in each workspace's runtime settings and gates.

## Related

- [<<STORE_NAME>>](../SHARED.md)
- [Authority and override rules](authority.md)
- [Corrections - the candidate log](corrections.md)
