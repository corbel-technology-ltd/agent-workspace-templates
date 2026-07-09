---
id: <<store_slug>>.tech-stack.TODO-entry-slug
name: "TODO: entry name (host / service / tool / runbook)"
type: reference
layer: C3
status: seed
owner: shared
created: "{{YYYY-MM-DD}}"
last_verified: "{{YYYY-MM-DD}}"
valid_for: 90d
tags: [tech-stack]
---

# TODO: entry name

> Copy per shared fact-cluster. State facts an agent can act on; date them (`last_verified`) so
> staleness is visible. No credentials, ever.

## What it is

<!-- The host/service/tool in one paragraph: what runs where, who owns it. -->

## What agents may assume

<!-- The stable facts: reachable how, backed up how often, restarts safe or not. -->

## What agents must check first

<!-- The volatile parts, and where the live truth lives (a workspace runbook, a status page). -->

## Cross-workspace impact

<!-- Which workspaces this touches, and what coordination an action here requires (e.g. a reboot
     interrupts sibling services for N minutes - pick a window). -->
