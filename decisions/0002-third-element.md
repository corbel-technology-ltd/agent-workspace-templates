---
id: family.decisions.third-element
name: Decision 0002 - the third element is Chandlery, a capability registry + parity ledger
type: decision
status: decided
owner: shared
created: 2026-07-02
tags: [decision, third-element, chandlery, registry, parity, drift]
---

# Decision 0002 - the third element

**Decided 2026-07-02.** The third member of the family is **Chandlery**: a plain-files capability
registry with a parity ledger - the mechanism by which deterministic capabilities (gate scripts,
hooks, onboarding engines, schemas, workflow specs) move between workspaces, and by which drift
between siblings becomes visible instead of silent.

## The gap it fills

Commonplace is **one workspace**. Lodestar is **one principal's shared brain** above many
workspaces. What neither carries is the relationship *between* the workspaces' machinery over time:

- Commonplace's constitution says generic improvements "should flow back upstream to the template"
  - doctrine with no mechanism. Nothing tracks which template version an instance came from or
  what it has locally improved.
- The moment a principal runs two workspaces, harness parity becomes a live problem: hooks, tools,
  and skills get ported by hand, then silently drift. This is not hypothetical - it is the
  documented failure mode in the live system this family generalises (a 2026-05-31 harness-parity
  audit found exactly this: rules shared and compounding, harness re-implemented per workspace
  with no propagation mechanism; the proposed fix was a parity register plus a drift-diff script).
- The family itself has the same problem in miniature: three templates vendoring the same five
  tools, with nothing asserting they stay identical.

So the missing piece is not another knowledge store. It is the **supply chain**: workspaces are
vessels, Lodestar is the star they steer by, and the Chandlery is where every vessel fits out with
standard, proven gear.

## What was considered (seven candidates)

Scored against the five criteria: (1) structurally load-bearing for the other two, (2) composable
and optional, (3) same ethos (plain files, deterministic-first, OKF, agent-agnostic, human at the
gate), (4) independently useful, (5) genuinely surprising / "of course" in hindsight.

| # | Candidate | Verdict |
|---|---|---|
| 1 | **Chandlery** - capability registry + parity ledger + flow-back mechanism | **Chosen.** Strong on all five; grounded in a documented live pain, not speculation. |
| 2 | Cockpit - human command-surface (aggregated briefs, approvals, remote control) | Rejected: violates the family's own value-gate. UI surfaces are explicitly deferred-software in the Commonplace design spec; a cockpit template would ship the thing the doctrine says to defer. |
| 3 | Accord - federation between *different principals'* workspaces and spines | Rejected for now: no real inputs exist (one principal). Breaks the "add leaves only when their inputs exist" rule the family preaches. Strongest future candidate once two principals actually federate. |
| 4 | Vade-Mecum - the FAW doctrine/handbook as its own template | Rejected: not load-bearing. FAMILY.md plus each member's doctrine already carries the story; a standalone handbook is documentation wearing a template costume. |
| 5 | Baton - continuity/relay layer (multi-session handover as a reusable pattern) | Rejected as a member: real but thin. Commonplace already carries the handover discipline (staging pointer + run notes + re-verify rule). The generalisable remainder is a *capability* - exactly the kind of thing Chandlery distributes - not a sibling template. |
| 6 | Gauntlet - agent evaluation layer (scenario banks, scorecards, calibration tests) | Runner-up. Independently useful and ethos-clean, but it amplifies Lodestar's calibration corner rather than connecting all three, and it needs accumulated instance data to be more than empty scaffolding. Revisit once instances have history to test against. |
| 7 | Almanac - shared external-signal layer (feeds, sources, watchlists) | Rejected: that is instance content (70_integrations / canon), not operating system. |

## Why Chandlery wins

- **Load-bearing (criterion 1):** it closes Commonplace's open flow-back loop (upstreaming gets a
  mechanism: `pack` a capability from an instance, version it, `install` it into siblings) and
  gives Lodestar's coordination layer the thing it coordinates *about* (the roster of workspaces
  is the fleet; parity offers between workspaces become registry entries instead of prose
  handoffs).
- **Composable and optional (2):** a lone Commonplace never needs it. Two workspaces want it. It
  also works with neither sibling - any folder-shaped tooling can be stocked and synced.
- **Ethos (3):** manifests are YAML, payloads are plain files, versions are integers, checksums
  are sha256, and nothing installs unattended - `install` is an operator-gated action that writes
  a visible lockfile. Deterministic plumbing end to end; the LLM is never in the loop.
- **Independently useful (4):** anyone who maintains agent tooling across several projects
  (hooks, lint gates, prompt templates) has this drift problem today, with dotfiles-grade tooling
  as the state of the art.
- **Surprising but obvious (5):** the family's own build proves it. The three members vendor the
  same five tools; `chandlery/registry/` stocks those tools as its seed capabilities and
  `family-check.py` verifies every vendored copy against the registry checksums. The registry is
  not a demo - it is load-bearing for the repo that ships it.

## What v0.1 is (and is not)

**Is:** a registry of capabilities (manifest + payload + docs per capability), a deterministic
`chandler.py` (list / verify / status / diff / install / pack / fleet / enrol), a fleet file, an
append-only ledger, the standard family mechanics (AGENTS.md constitution, thin runtime adapters, onboarding,
gates including the agent-agnostic lint), and the five seed capabilities that the family itself
uses.

**Is not:** a package manager. No dependency resolution, no remote fetch, no registry server, no
auto-update. Capabilities are folders of files; installing one is copying files and recording
checksums; everything else is a human decision at a gate.
