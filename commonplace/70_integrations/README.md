---
id: <<workspace_slug>>.integrations.map
name: Integrations — what-runs-where map (instance-specific slots)
type: reference
layer: C3
status: placeholder
owner: shared
created: <<CREATED_DATE>>
tags: [integrations, fold-in, live-systems, event-store, placeholder]
related:
  - {ref: 00_meta/design-spec.md, dimension: why, polarity: derived_from}
  - {ref: 20_memory/README.md, dimension: what, polarity: explains}
  - {ref: 60_workflows/email-triage-approve.md, dimension: how, polarity: requires}
---

# Integrations — what-runs-where

> **Placeholder.** This control plane **folds in** an instance's live systems rather than rebuilding
> them. The template carries **no** integration code or config — no executor, no email tooling, no
> CRM, no feeds. This file lists the **slots** to fill per instance, mirroring the shape of a fully
> wired control plane. Replace each slot with the instance's real system (what it is, where it lives,
> which workspace concept it satisfies), and add a `component-registry.md` row for each moving part.

The deferred software control plane (a database, an event pipeline, UI surfaces) is fenced behind the
value-gate (design-spec §9). None of it is stood up by the template. The last slot names where that
software *would* run if a workflow ever earns automation.

## Fold-in map (slots to fill)

| Workspace concept | Folded into (live system) | Status |
|---|---|---|
| Email monitoring | (instance email loop: IMAP poller + send tool) | TODO |
| Research / opportunity engine | (instance intel/research engine) | TODO |
| Sentiment | (instance sentiment tool) | TODO |
| Obligations / evidence plane | (instance records store) | TODO |
| Memory retrieval | (deterministic loader + optional semantic surface) | built-in (files) |
| Event store | git over `20_memory/journal/` | built-in |
| Relationship memory / CRM | (instance CRM) | TODO |
| Always-on executor | (optional; see `00_meta/always-on-executor-spec.md`) | optional |
| Off-site backup | (instance off-site store) | TODO |
| Deferred-software runtime | (instance infra: a host/VPS, an automation hub, a git remote, monitoring) | reserved |

---

## Slots to fill (one section per system, when wired)

### 1. Email loop = email monitoring

- **What:** an IMAP poller that watches the workspace mailbox for inbound mail, paired with a sender
  (the single send path). Together they are the email channel: read inbound, draft outbound.
- **Where:** (set the poller + sender paths and the mailbox here).
- **Credentials:** the workspace-root `.env` (untracked, gitignored). Never commit or echo it.
- **How it is wrapped:** [`../60_workflows/email-triage-approve.md`](../60_workflows/email-triage-approve.md)
  is a thin wrapper. **Hard invariant:** no external send without explicit founder approval. The
  wrapper invokes the existing send tool; no new send API is built.

### 2. Research / opportunity engine

- **What:** the instance's intel/research engine that surfaces signals. Its outputs land as
  [`../30_schemas/opportunity.md`](../30_schemas/opportunity.md)-shaped artefacts and feed
  observational atoms.
- **Caveat (source-or-abstain):** engine signals are evidence, never authority; any claim lifted
  from it carries its primary source or is marked `aspirational`.

### 3. Sentiment

- **What:** a research tool that pulls recent posts/engagement for a topic. Output is observational
  signal, minted as atoms only on the recurrence bar (≥2 journal references).

### 4. Records store = obligations / evidence plane

- **What:** the records room: registered obligations and the evidence that satisfies them. Indexed by
  [`../50_registers/records.md`](../50_registers/records.md). Binaries live off-machine; the register
  holds the pointer.

### 5. Memory retrieval (built-in)

- **What:** the deterministic frontmatter loader is primary; an optional semantic surface is the
  cross-cutting backstop. No new store is stood up; a database + vector + graph is deferred behind the
  graduation trigger. See [`../20_memory/README.md`](../20_memory/README.md).

### 6. git = the event store (built-in)

- **What:** git over the append-only `20_memory/journal/`. Journal entries are immutable; a retraction
  is a NEW entry; git history is the tamper-evidence. This is why **no database** is built for v1.
  Set the off-machine remote per instance.

### 7. Relationship memory / CRM

- **What (optional):** a rolling, compressed per-correspondent context so drafts are warm, not cold;
  seeds contact/account profiles. Reuse the memory spine (emails → journal events → reaper-style fold
  keyed by correspondent → person/org atoms), do not fork a parallel store. Privacy is a design input:
  lawful basis, data-minimisation, retention.

### 8. Always-on executor (optional)

- **What:** an always-on machine that runs the workspace's jobs headless and raises prepared work.
  Design pattern + hardening checklist: [`../00_meta/always-on-executor-spec.md`](../00_meta/always-on-executor-spec.md).
  Build only when the instance needs it.

### 9. Off-site backup

- **What:** an off-site copy of the repo history (and any guest-data stores). Set the destination and
  the bundle/restore scripts per instance; prove restore before relying on it.

### 10. Where deferred software would run (reserved, not active)

When the value-gate fires (a workflow has run by hand ≥4 weeks and consistently costs >20 minutes to
assemble, or signal volume exceeds a stated threshold — design-spec §9), the software reuses the
instance's **existing** infrastructure rather than provisioning anything new: an automation hub for
the deferred event pipeline; a host/VPS for any database or vector store; a git remote for the
event store; monitoring for any stood-up service. Until the gate fires, this is reserved capacity,
not running software. The workspace is run **by hand over the filesystem**; do not describe the
deferred control plane as if it exists.

## Related

- [Workspace — founding design spec (founder control plane)](../00_meta/design-spec.md)
- [Memory structure — the model](../20_memory/README.md)
- [Email triage and approve — thin wrapper over the email loop](../60_workflows/email-triage-approve.md)
