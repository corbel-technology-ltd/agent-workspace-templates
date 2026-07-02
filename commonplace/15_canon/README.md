---
id: <<workspace_slug>>.canon.model
name: Canon — durable curated reference (the C3 reference layer)
type: reference
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [canon, reference, c3, settled-background, direction, brand, voice, offerings]
related:
  - {ref: AGENTS.md, dimension: why, polarity: derived_from}
  - {ref: 15_canon/index.md, dimension: what, polarity: explains}
  - {ref: 10_doctrine/principles.md, dimension: how, polarity: explains}
  - {ref: 20_memory/README.md, dimension: what, polarity: relates_to}
  - {ref: 50_registers/decision-log.md, dimension: how, polarity: requires}
---

# Canon

The workspace's **durable curated reference knowledge** — the C3 layer. Canon is the settled
background the agent treats as given: the locked business direction, brand, voice, offerings, and a
references library. It is **decided knowledge**, not live state: distinct from the registers
([`../50_registers/`](../50_registers/)), which track what is moving (decisions in flight, open
loops, risks, metrics). If a register answers *what is happening now*, canon answers *what is settled
and true about this entity*. Where this sits in the whole: [`../AGENTS.md`](../AGENTS.md) (the OS map,
Context layers — C3).

## The contract

- **Settled, not speculative.** Material enters as `status: staged` (working canon under review) and
  is only authority once it locks (`status: current`). Keep **established canon** (genuinely decided
  and written down) separate from **head-canon** (aspirational or newly floated) until it is earned.
- **Read-only by reflex.** Canon is C3 reference: the agent **does not silently rewrite it**
  ([`../AGENTS.md`](../AGENTS.md), non-negotiable rule 4). Changes are proposed as diffs for the
  owner, and the decision that shaped a lock traces back to
  [`../50_registers/decision-log.md`](../50_registers/decision-log.md). The standing rules behind that
  read-only reflex live in [`../10_doctrine/principles.md`](../10_doctrine/principles.md).
- **Canon vs. memory.** Durable *facts and principles* about how the owner works graduate to
  long-term atoms in [`../20_memory/`](../20_memory/README.md); the entity's *direction, brand, and
  offerings* live here. Memory is folded and decays; canon is curated and stable.
- **Deltas only.** When a shared-context store is wired
  ([`../AGENTS.md`](../AGENTS.md), Shared context), this folder carries only what is specific to **this
  instance** — never a second copy of the owner's profile or cross-workspace rules.
- **OKF body.** One concept per file, frontmatter with `type`, relationships as `related:` edges
  mirrored as inline body links. `index.md` is reserved (no frontmatter; a `* [Title](rel) - desc`
  list).

## A short tour of what lives here

The template ships this folder **blank** — no two instances share a brand or a direction, so canon is
entirely instance-specific. Today it carries one file:

- [`index.md`](index.md) — the canon index. It names what belongs here once established (**direction**,
  **brand**, **voice**, **offerings/**, **references/**) and holds the table that lists each canon
  file with its provenance and status. Start here.

The directory-name slots — `offerings/` and `references/` — are conventions, not pre-made folders;
they appear when the owner establishes that material. Until then, canon is an empty shell with its
index, waiting to be filled at instantiation.

## Related

- [<<WORKSPACE_NAME>>](../AGENTS.md)
- [Canon](index.md)
- [Operating principles — the one vocabulary](../10_doctrine/principles.md)
- [Memory structure — the model](../20_memory/README.md)
- [Decision log (append-only)](../50_registers/decision-log.md)
