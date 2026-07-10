---
okf_version: "0.1"
id: "CHANGE_ME.repo#services/payments"
type: "Service"
profile: "full"
title: "Payments Service (EXAMPLE - delete once real concepts exist)"
description: "Authorises, captures, refunds, and reconciles payment transactions."
status: "active"
owners:
  - id: "CHANGE_ME.repo#teams/payments-platform"
    role: "owner"
source:
  path: "src/payments/"
  kind: "code-tree"
relations:
  - type: "depends_on"
    target: "CHANGE_ME.repo#data/postgres-primary"
  - type: "part_of"
    target: "CHANGE_ME.repo"
lifecycle:
  updated_at: "YYYY-MM-DD"
  review_after: "YYYY-MM-DD"
---

# Payments Service

One concept per file. Frontmatter = structured filtering; this body = semantic meaning.

## Facts

Facts belong in the concept, never in agent instructions.

- Database: PostgreSQL (version owned by the native `Dockerfile` / `package.json`, not asserted
  here).
- Public contract: owned by the native `openapi.yaml`; this file is its companion, not its
  source.

## Responsibilities

- What the service does, in prose a newcomer or an agent can act on.

## Boundaries

- What it explicitly does not do, and which concept owns that instead.
