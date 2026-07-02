---
id: <<workspace_slug>>.template.design-system
name: DESIGN.md template (AI-readable design system, blank fill-in)
type: template
layer: C2
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [template, design-system, design, tokens, brand, fill-in]
related:
  - {ref: 15_canon/index.md, dimension: why, polarity: derived_from}
---

# DESIGN.md template

A blank fill-in instance of the **DESIGN.md** format (the google-labs AI-readable design-system spec:
`github.com/google-labs-code/design.md`) — machine-readable design **tokens** in YAML front matter
plus human-readable **rationale** in the body, so an agent applies the identity consistently instead
of inventing styling.

**How to use it.** Copy this into the design system's own home (a site repo, a `tokens/` directory, or
a client/project repo) as `DESIGN.md`, then fill every token. The filled file is the design-system
**source of truth**; the workspace **references** it (reference, don't absorb) and the canon
([`../15_canon/index.md`](../15_canon/index.md)) links to it. Adopt the **format**, not any alpha CLI.

**Filling rules.** The token groups and variable names below are a neutral starting set — rename them
to match the system you are dressing. Every value is a placeholder marked for replacement. Any
accessibility claim (contrast ratios) must be **measured**, never guessed (source-or-abstain): point a
WCAG-contrast lint at the colours source. Delete bracketed guidance once filled; leave nothing as
"TBD".

## Front matter for the filled DESIGN.md

```yaml
---
name: <System name>
# every value below is a placeholder — replace before shipping.
colors:
  surfaces:   { bg: "<hex>", panel: "<hex>" }
  ink:        { fg: "<hex>", muted: "<hex>", faint: "<hex>" }   # note measured contrast vs bg
  structure:  { rule: "<rgba>", rule-2: "<rgba>" }
  signal:     { signal: "<hex>", glow: "<rgba>", wash: "<rgba>", on-signal: "<hex>" }
typography:
  families:   { sans: "<font>", mono: "<font>" }
  tracking:   { display: "<em>", head: "<em>", mono: "<em>" }
  leading:    { display: 1.0, head: 1.1, body: 1.5 }
  steps:      { hero: "clamp(<min>,<vw>,<max>)", title: "clamp(<min>,<vw>,<max>)", lead: "<size>", body: "<size>" }
spacing:
  frame:      { maxw: "<px>", gut: "clamp(<min>,<vw>,<max>)" }
  rhythm:     { sect-y: "clamp(<min>,<vh>,<max>)", sect-gap: "clamp(<min>,<vh>,<max>)" }
  measure:    { base: "<ch>", wide: "<ch>" }
  scale:      { s-1: "<px>", s-2: "<px>", s-3: "<px>", s-4: "<px>", s-5: "<px>", s-6: "<px>", s-7: "<px>", s-8: "<px>", s-9: "<px>" }
rounded:      { base: "<px>" }
motion:       { ease: "<cubic-bezier>", t-state: "<s>", t-reveal: "<s>" }
components:   {}   # fill per component (see ## Components)
---
```

Keep the front-matter tokens and any CSS variables in sync. One source of truth — when a value
changes, change it in both, or generate one from the other.

## 1. Overview

<!-- One paragraph: what this system is and the single feeling it serves. Cite the brand soul. -->

- **Name / what it dresses:**  <!-- e.g. <System name> — the site + flagship surface -->
- **The feeling (one line):**  <!-- the one emotion every choice serves -->
- **North star + anti-references:**  <!-- what to move toward; what to never look like -->

## 2. Colour (roles are law)

<!-- A role-based palette, not a swatch list. State what each colour MEANS, not just its hex.
     Keep the discipline: a small, role-bound palette. -->

- **Surfaces** (`bg`, `panel`):
- **Ink** (`fg`, `muted`, `faint`) — with **measured** contrast vs `bg`:
- **Structure lines** (`rule`, `rule-2`):
- **The one signal** (`signal` + glow/wash/on-signal) — what it is allowed to mean:
- **Forbidden:**  <!-- the colour moves this system never makes -->

## 3. Typography

<!-- Families, the registers they play, and the numeric tokens. Keep to two families. -->

- **Families** (`sans`, `mono`) and each one's job:
- **Tracking / leading** (display / head / body / mono):
- **Fluid steps** (`hero`, `title`, `lead`, `body`) and the measure they sit in:
- **Rules:**  <!-- e.g. no gradient text, no stylised display faces, body never tiny -->

## 4. Layout & spacing

<!-- The frame, the vertical rhythm, the measure, and the spacing scale. -->

- **Frame** (`maxw`, `gut`, `pad`):
- **Vertical rhythm** (`sect-y`, `sect-gap`) and how sections separate:
- **Measure** (`base`, `wide`):
- **Spacing scale** (`s-1`…`s-9`):

## 5. Motion & depth (elevation)

<!-- What motion is FOR, the timing bands, and the atmosphere layer. -->

- **What motion means:**
- **Timing bands** (`t-state`, `t-reveal`, …) + the one easing (`ease`):
- **Atmosphere** (grain, light) and its limits:
- **Depth:**  <!-- shadow elevation vs hairline rules + light; state the approach -->
- **Reduced-motion:**  <!-- the static, meaningful end-state; never required to understand the page -->

## 6. Shapes

<!-- Border-radius and form language. State the radius scale (`rounded.base`) and any exceptions. -->

## 7. Components

<!-- Per component: the tokens it composes and the one rule that keeps it on-brand. -->

| Component | Tokens it uses | The one rule |
|---|---|---|
| <!-- e.g. button --> |  |  |
| <!-- e.g. chip --> |  |  |
| <!-- e.g. dropdown --> |  |  |
| <!-- e.g. the flagship surface --> |  |  |

## 8. Do's and Don'ts

<!-- The guardrails an agent must not cross. -->

### Do

-

### Don't

-

## Related

- [Canon](../15_canon/index.md)
