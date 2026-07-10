# Changelog

Template-level history (what changed in Folder-Agent-Workspace itself, not in any instance). Newest first.

## 0.5 - 2026-07-10 - taxonomy glossary + knowledge-pack template

- **`30_schemas/taxonomy.md`** (new): the living glossary of concept types (10 families) and
  relation types (7 groups) every durable artefact draws its `type:` and edges from, plus the
  native-files rule (native files own their facts; the corpus references, mirrors, or generates -
  never overwrites). Adapted from the Penchant knowledge-pack proposal, genericised.
- **`40_templates/knowledge-pack/`** (new): a stampable knowledge corpus for project repos -
  `manifest.yaml` (native-file inventory, generated adapters, validation switches),
  `registry/{types,relations}.yaml` (stamped from the taxonomy), `index.md`, `log.md`, and two
  example concepts. Copied into a target repo as `knowledge/`.
- `AGENTS.md`: rule 6 now names the taxonomy as the type/relation vocabulary and carries the
  native-files precedence rule; two routing rows added (structure a repo's knowledge; define a
  term/type).
- `30_schemas/README.md` + `40_templates/README.md`: listings updated.

## 0.4 - 2026-07-02 - agent-agnostic hardening + audit fixes

A fresh-context adversarial critic pass followed the work below; its findings were fixed in the
same release: the onboarding token table named tokens in `<<...>>` form and so mangled itself
during substitution (now named without brackets, verified to survive); a blank
`SHARED_CONTEXT_PATH` left broken boot text in `AGENTS.md` (now graceful); the "Instance status"
section was stuck reading "not yet initialised" forever and claimed onboarding wires
`70_integrations/` (now evergreen and accurate); the journal guard resolved paths against the
process CWD, exempted nothing, and only tripped on `rm|mv` (now resolves against ROOT, exempts the
journal README/`.gitkeep` to match the git hook, widens the shell tripwire, and names
`core/git-hooks/pre-commit` as the real enforcement); the adapter shim passed CPython's exit-2
through when a core hook was missing, wedging every tool call (now fails open); `session-brief`
printed raw tokens pre-onboarding (now dormant); `apply.py` accepted a value embedding a token
literal (now rejected); `gen-related` mangled names containing an apostrophe/colon (now
YAML-unquotes); and `okf_version` is now a real frontmatter key. The shared gate fixes
(`gen-related`, `apply.py`, `scrub-check`) flowed to the sibling templates through the Capability-Registry
registry.

An audit-first hardening pass. Every claim in the docs was verified against the files; the
neutral-core split that `INSTALL.md` used to defer ("future work, not a v1 claim") is now built.

**Neutral core + thin adapters (the big one):**

- All executable logic moved to `core/`: the six reflex hooks (`core/hooks/`) and the onboarding
  engine + playbook (`core/onboarding/` - `apply.py`, `placeholders.yml`, tests, `ONBOARDING.md`).
- The journal guard now speaks a neutral contract (`op: modify | create-or-overwrite | shell` on
  stdin, exit 2 blocks); the runtime adapter translates. The primary wired adapter shrank to a
  settings file + one ~70-line shim + a pointer skill; the second adapter stays a pure pointer.
- New `core/RUNTIMES.md`: the adapter contract, a "wire a new runtime in 15 minutes" guide, and
  the ONE sanctioned home for vendor specifics (the verified hook-event reality moved there from
  `00_meta/agent-os-design.md`).
- New optional `core/git-hooks/pre-commit`: journal append-only enforced at commit time for any
  runtime, hooks or no hooks.
- New gate `tools/agnostic-check.py`: fails if a vendor term appears outside the adapter layer or
  if an adapter pointer grows content. Wired into README/INSTALL/CONTRIBUTING gate lists.

**Onboarding robustness:**

- `apply.py --dry-run`: validate values and preview per-file replacement counts without writing;
  the playbook now recommends it before the real run. Tests extended (16 pass).
- The long-promised token table now exists in `README.md` (three docs pointed at a table that was
  never written); `placeholders.yml` stays the single source of truth.

**Truth fixes (docs vs files):**

- Hook counts reconciled everywhere (three docs said 3, one said 4; there are six) and the hooks
  README table now includes `onboarding-gate.py`.
- Dropped the false "adapters are generated" claim (no generator existed); adapters are now
  "pinned pointers", enforced by the new gate - which is a stronger guarantee than generation.
- The constitution's routing map no longer hardcodes a vendor docs tool; the doc-lookup row routes
  through `70_integrations/`.
- `00_meta/design-spec.md` structure diagram updated (it omitted `80_projects/`, `tools/`, the
  adapter layer) and its file inventory marked as the founding manifest with the tree as truth.
- Removed "reference workspace / reference instance" mentions a public cloner cannot access;
  replaced with self-contained guidance.
- `20_memory/README.md` no longer claims READMEs for housekeeping folders that ship as `.gitkeep`
  stubs; the weekly-review template no longer dead-links the gitignored reaper build marker.
- `escalate-with-context` added to the constitution's doctrine list (the design-spec's one
  vocabulary named eight principles; the constitution listed seven).
- `{{placeholders}}` wording in `40_templates/README.md` renamed to `{{...}}` runtime markers so
  the two-marker-syntax rule stays unambiguous.

**Gate status after the pass:** scrub-check, okf-check, agnostic-check, `gen-related --check`,
and the onboarding test suite all green.

## 0.3 - 2026-06-28 - public face

Landing README, CONTRIBUTING, install guide, FAW/OKF framing (pre-family history; see git log).
