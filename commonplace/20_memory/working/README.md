---
id: <<workspace_slug>>.memory.working
name: Working memory (depth 1)
type: reference
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [memory, working, depth-1]
---

# Working memory (depth 1)

What is in hand right now: the active task state, open loops, live constraints, and just-retrieved
evidence. Ephemeral — strictly budgeted (≤ ~2.5k tokens, 4–8 items, per `../homeostasis.yml`). Mostly
this is the live session context + today's daily brief + the open decision queue, not stored files.

Anything durable here is **folded into the journal and dropped at day's end**; if it earned it, the
reaper promotes it to short-term. Working memory should never accumulate — it is a desk, not a drawer.

Starts empty.
