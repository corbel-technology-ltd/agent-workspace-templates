# Changelog

All notable changes to the Agent-Workspace-Templates family are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses semantic versioning.

## [Unreleased]

### Added

- A non-clobbering live-instance template update channel: origin manifests, cached update checks,
  pacnew-style apply/accept semantics, a seven-day session nudge, and end-to-end proof.
- A context-decomposition doctrine and constitution rule: large durable context is broken into
  concept folders behind an index map so an agent loads exactly what a task needs, with a
  decomposition test, keep-intact classes, an anti-confetti rule, and a backdating procedure for
  existing files. Enforced by a `decomposition-check` gate (wired into `family-check`) with a
  reasoned exceptions file and a disposable-repo self-test.
- A subagent-dispatch constitution rule: each subagent gets one bounded task and an explicitly
  chosen model tier matched to its difficulty, so bulk or parallel work never silently inherits the
  session model; dispatch depth and concurrency stay bounded. Runtime-conditional where the runtime
  exposes per-subagent model selection.

### Fixed

- Preserved accepted local customisations across repeated template updates by separating reviewed
  upstream baselines from accepted local hashes; local-only paths no longer acquire synthetic
  baselines.

## [0.6.0] - 2026-07-11

### Added

- Completed the memory loop end to end with depth-ordered recall, related-edge following, archive
  resurrection, bounded sleep synthesis, deterministic validation, and a disposable self-test.
- Added a member-aware installer, literal install one-liners, OS-specific guidance, novice-proof
  recovery messages, and `REFERENCE.md` as the after-week-one operational lookup sheet.

### Changed

- Explained the two independent layer axes at their points of use and made all member installation
  commands complete, copy-pasteable one-liners.

### Fixed

- Closed the Tier 1 memory-review defects, including evidence binding, rejection handling,
  hysteresis, expiry, quarantine, idempotency, and hardening for real-world stores.
- Made installation and onboarding failure paths atomic, resumable, and explicit for first-time
  command-line users.

[Unreleased]: https://github.com/CORBEL-Technology/agent-workspace-templates/compare/v0.6.0...HEAD
[0.6.0]: https://github.com/CORBEL-Technology/agent-workspace-templates/releases/tag/v0.6.0
