---
id: <<workspace_slug>>.doctrine.session-discipline
name: Session discipline — context budget, degradation, handoff
type: doctrine
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [doctrine, session, context, degradation, handoff]
related:
  - {ref: 10_doctrine/principles.md, dimension: why, polarity: derived_from}
  - {ref: 20_memory/journal/README.md, dimension: how, polarity: requires}
---

# Session discipline

A founder control plane is operated through long agent sessions. Reasoning degrades as context
fills, and you cannot directly measure your own saturation. Recognise the symptoms and act.

## Context budget

Quality degrades past roughly **50% context utilisation**. Plan work to finish within ~50%. When
orchestrating subagents, keep the orchestrator lean and give heavy work to subagents with fresh
windows; **pass file paths between agents, not file contents**.

## Degradation symptoms (any of these)

- The operator is repeating instructions you should already hold.
- You are re-reading files you read earlier this session.
- Outputs are getting longer without getting more useful.
- You are missing details from instructions given earlier.

## When you detect them

1. **Preserve state durably.** The journal is already the truth for decisions and durable facts, so
   anything load-bearing should already be written there or to the relevant register. Do not rely on
   conversation memory surviving.
2. **Hand off rather than push on.** Write a structured handover (task, progress, pending decisions,
   files touched, resumption point) and, if wanted, spin up a fresh session to continue. A resumable
   handover beats a degraded restart.
3. **Surface it.** Tell the operator plainly. Trust is higher when you flag degradation than when
   you silently produce worse output.

This is `escalate-with-context` applied to your own limits: name the ceiling, preserve the work,
hand the baton over cleanly.

## Resuming a session

The other end of a handover. At session start, before acting:

1. Read [`00_meta/staging.md`](../00_meta/staging.md) (the `Now / In flight` block) for current focus.
2. Read the handover named in `00_meta/staging.md`'s `Latest handover` pointer (the newest run note)
   and re-verify its live-state claims; a handover is a claim, not ground truth.
3. State a one-line current-state summary, then route per `AGENTS.md`. If no task is queued, stand by
   for <<OWNER>> and do not act unprompted.

The `session-brief` `SessionStart` hook injects this orientation automatically; the steps are the
fallback and the authority if it does not.

## Related

- [Operating principles — the one vocabulary](principles.md)
- [Journal — the append-only event log](../20_memory/journal/README.md)
