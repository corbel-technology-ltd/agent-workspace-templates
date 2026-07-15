---
name: onboarding
description: Use only when .uninitialised exists at the current workspace root and never at the family template root or in an initialised live workspace
type: skill
---

# Onboarding (Claude Code adapter)

This skill applies only when `.uninitialised` exists at the current workspace root. If it is
absent, stop; never run onboarding at the family template root or in an initialised live instance.

The neutral playbook lives at
[`core/onboarding/ONBOARDING.md`](../../../core/onboarding/ONBOARDING.md).

Follow it exactly, including its validation and recovery rules. Stop if validation fails.

Keep procedure in that neutral playbook so every runtime inherits the same flow.
