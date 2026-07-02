---
id: <<workspace_slug>>.memory.short-term
name: Short-term memory (depth 2)
type: reference
layer: C3
status: current
owner: shared
created: <<CREATED_DATE>>
tags: [memory, short-term, depth-2, episodic]
---

# Short-term memory (depth 2)

Recent, still-noisy memory: recent episodes, commitments, dossiers for active people/projects, and
facts that are not yet durable (the "cooling" queue awaiting proof). Decays (default `valid_for:
30d`); an atom is minted here only on **≥2 journal references** so one-off noise never enters.

An atom leaves short-term by one of two routes: it **promotes** to long-term when it earns it
(decision-impact, recurrence, reuse, surprise, or an explicit `pivotal` mark — see `../homeostasis.yml`
and the reaper), or its activation falls below the exit threshold and it **decays to `../archive/`**.
The journal entry always persists, so "forgotten" here means "no longer surfaced", never "lost".

Starts empty.
