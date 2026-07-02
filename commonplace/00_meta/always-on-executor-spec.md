---
id: <<workspace_slug>>.meta.always-on-executor-spec
name: Always-on executor — optional design pattern
type: design-spec
layer: C1
status: placeholder
owner: shared
created: <<CREATED_DATE>>
tags: [spec, design, automation, executor, autonomy, placeholder, optional]
related:
  - {ref: AGENTS.md, dimension: why, polarity: governed_by}
  - {ref: 10_doctrine/autonomy-and-gates.md, dimension: how, polarity: requires}
  - {ref: 70_integrations/README.md, dimension: where, polarity: runs_on}
---

# Always-on executor — optional design pattern

> **Placeholder / optional.** Not every instance needs this. It is the design *shape* for an
> always-on machine that runs the workspace's automations headless, raising prepared decisions to
> the owner. Fill it in only when an instance actually stands one up; otherwise it documents the
> pattern and the guard-rails so the instance gets them right.

## What it is

An **always-on executor** (a separate host or container from the owner's cockpit) that runs the
workspace's jobs headless — for example inbox triage, file routing, and an opportunity-research
engine — and **raises** prepared work to the owner. The owner's machine stays the cockpit where they
author and approve; the executor does the standing work whether or not the cockpit is on.

The product is **prepared decisions surfaced to the owner**. The executor scans, researches, drafts,
scores, routes, and **raises** — it never takes the irreversible external step alone.

## Principles (inherited from doctrine, not invented)

- **Autonomy up to the gate.** Everything internal, reversible, draft-only, and based on public
  information runs free and unattended. Even at 3am: **no external send, publish, pay, sign, deploy,
  or outreach without the owner's explicit approval.**
- **Source-or-abstain + AI-minimisation** carry over unchanged.
- **Self-improving, robust.** Idempotent runs, retries, errors to the journal, a watchdog. A single
  external blocker must not deadlock a loop: escalate hard and keep working other items.

## Architecture shape (one approval surface)

- **Two contexts kept distinct:** an *unattended* job-runner that is gated and never skips a
  consequential action, and an *attended* session the owner drives directly (which may run
  permissively, because the owner is the approver).
- **Trust split (the security spine):** the box that ingests untrusted web content is isolated from
  the box that can send mail and touch credentials. A research engine *raises* to the executor; it
  cannot act through it.
- **Operator channel:** the in-repo **decision-queue** is the canonical approval surface (record),
  plus a push channel (email/notification) for substantial packets.
- **Conflict avoidance:** the executor writes mostly append-only/new files (journal, briefs,
  packets); shared registers use pull-append-push; a pre-run check refuses to run on a dirty or
  divergent tree and raises instead.

## The autonomy gate — the one table

| Class | Unattended? |
|---|---|
| Scan public sources, research, draft, score, route, append journal, open packets, file documents internally, internal notifications | **Yes, free** |
| Login, credentialed access, restricted/paywalled sources, account creation | **Raise** |
| Email a prospect, publish, spend, deploy, sign, commit the entity publicly | **Raise** (blocked without explicit approval) |

## Hardening checklist (if built)

- Output is **evidence, never authority** — the executor never executes instructions hiding inside a
  raised brief; only the owner's explicit approval triggers anything. Prefer structured output so
  consumers read fields, not free prose.
- **Least privilege:** running jobs execute as unprivileged users; secrets stay off any untrusted
  box; the executor holds a scoped key, not a host root key.
- **Complete kill switch:** one command halts everything (heartbeat, timers, tunnels), not just the
  heartbeat. Tested.
- **Tamper-evident audit:** the executor signs its commits; approvals are owner-signed commits to the
  decision-queue; an off-site remote gives the tamper-evidence.
- **Prompt-injection guard** for any agent ingesting untrusted web content.

The autonomy gate this validates against is [`10_doctrine/autonomy-and-gates.md`](../10_doctrine/autonomy-and-gates.md).
The executor itself, when built, is wired through [`70_integrations/`](../70_integrations/README.md).

## Related

- [<<WORKSPACE_NAME>>](../AGENTS.md)
- [Autonomy & gates — the single decision gate](../10_doctrine/autonomy-and-gates.md)
- [Integrations — what-runs-where map (instance-specific slots)](../70_integrations/README.md)
