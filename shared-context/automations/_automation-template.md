---
id: <<store_slug>>.automations.TODO-automation-slug
name: "TODO: automation name"
type: context
layer: C3
status: seed
owner: shared
created: "{{YYYY-MM-DD}}"
tags: [automations]
---

# TODO: automation name

> Copy per standing automation (cron, timer, watcher, webhook, scheduled agent). Existence,
> location, and ownership - enough that another agent finds it BEFORE breaking it.

## What it does

<!-- One paragraph: trigger, action, why it exists. -->

## Where it runs

<!-- Host / container / service, schedule (cron line or timer), and the paths involved.
     | Field | Value | table works well: host, schedule, script path, logs, state. -->

## Owner & blast radius

<!-- Which workspace/agent owns it (changes go through them). What breaks if it stops -
     and what breaks if it fires twice. How its failure is noticed (dead-man switch? alert?). -->

## What this is not

<!-- The boundary: e.g. do not re-point its output; do not duplicate it per-workspace. -->
