---
id: <<store_slug>>.boundaries.boundaries
name: The boundary tiers - never-share / share-with-care / public
type: doctrine
layer: C0
status: seed
load: always
owner: human
created: <<CREATED_DATE>>
tags: [boundaries, never-share, scrub-source, privacy]
related:
  - {ref: boundaries/README.md, dimension: where, polarity: derived_from}
---

# The boundary tiers

> Blank by design - populate at calibration. The **Never share** list is machine-read by
> `core/derive-scrub.py`: each bullet must start with the term in backticks, optionally followed
> by ` - ` and a note. Keep terms lowercase, one concept per bullet.

## Never share

Terms that must not appear in anything that leaves the principal's machines - shared templates,
published copies, screenshots, external messages. Typical members: real names of people in the
circle, employer/client names, internal hostnames, project codenames, personal email addresses.

<!-- - `example-hostname` - internal server name
     - `example-codename` - unannounced project -->

## Share with care

May appear in work products for known audiences, never in public artefacts: commercial terms with
clients, rough capacity/availability details, tooling choices that reveal strategy.

<!-- - describe each item and the audience it is limited to -->

## Public

Safe anywhere: the principal's public roles, published work, anything already on the public
record. Listing it here stops over-scrubbing.

<!-- - list the public anchors so agents stop second-guessing them -->

## Related

- [Boundaries - the confidentiality line](README.md)
