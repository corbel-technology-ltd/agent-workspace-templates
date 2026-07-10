---
okf_version: "0.1"
id: "CHANGE_ME.repo#agents/repo"
type: "AgentInstructions"
profile: "full"
title: "Repo agent instructions (EXAMPLE - delete once real concepts exist)"
description: "Instructions (not facts) for coding agents in this repo. Generates AGENTS.md / CLAUDE.md."
status: "active"
owners:
  - id: "CHANGE_ME.repo#teams/platform"
    role: "owner"
relations:
  - type: "part_of"
    target: "CHANGE_ME.repo"
lifecycle:
  updated_at: "YYYY-MM-DD"
  review_after: "YYYY-MM-DD"
---

# Repo agent instructions

Instructions belong here; facts belong in Service/System/Dataset concepts. Never inline secrets.
Generated `AGENTS.md`/`CLAUDE.md` carry a do-not-edit header and are projections of this concept.

## Constraints

```yaml
constraints:
  must:
    - "Run the test suite before opening a PR."
  must_not:
    - "Do not edit generated files by hand."
requires_human_approval:
  - "database migrations"
  - "new production dependencies"
```
