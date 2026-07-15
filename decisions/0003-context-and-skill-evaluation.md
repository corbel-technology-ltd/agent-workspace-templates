---
id: family.decisions.context-and-skill-evaluation
name: Decision 0003 - paired evaluation for context and skill changes
type: decision
status: decided
owner: shared
created: 2026-07-15
tags: [decision, evaluation, context, skills, paired-test, leakage]
---

# Decision 0003 - paired evaluation for context and skill changes

**Decided 2026-07-15.** Changes to always-loaded context and new family-distributed skills are
judged by a pre-registered paired evaluation, not by intuition. The protocol is deliberately
small: candidate-specific scenarios and verifiers are created only when a real candidate exists.
There is no standing scenario bank or fourth family member.

## Evidence and scope

The protocol follows the measurement discipline in *Evaluating AGENTS.md: Are Repository-Level
Context Files Helpful for Coding Agents?* (arXiv:2602.11988, especially section 6) and
*SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks* (arXiv:2602.12670,
sections 3 and 4).

The SkillsBench uplift is not a forecast for arbitrary skills. Only 87 of 400 submitted tasks
survived filtering, tasks without skill separation were rejected, and the retained skills were
top-quartile quality. Its results are a reason to test applicable skills, not permission to assume
that adding one helps. The AGENTS.md study measures Python coding tasks, while these templates also
support long-lived operational work. Neither paper directly establishes benefit in every family
use case.

## Pre-registration record

Before looking at outcomes, record all of the following beside the candidate:

1. The candidate identifier, hypothesis, intended file diff, member, and exact baseline and
   candidate source-tree identifiers or content digests.
2. The model, harness, and versions. Report each model-harness pair separately.
3. Applicable scenarios, the nearest non-applicable scenario for a skill, hard invariants, and the
   identity or digest of each deterministic pass/fail verifier.
4. Evaluator-only fixtures, budgets, timeout, retry allowance, invalid-run replacement rule, and
   trial count. Three trials per condition and task case is the floor; use more for high-variance
   or high-risk changes.
5. Primary and secondary outcomes, any non-inferiority margin, the uncertainty method, and the
   shipping rule.
6. Expected step, token, and cost effects, including the largest increase acceptable and the
   measured safety or correctness gain that would justify it.

Do not change these choices after results are visible. If an execution fault meets the declared
replacement rule, replace the run under that rule and retain the fault record. Otherwise count it.

## Paired execution

- Instantiate the current and candidate members freshly for every trial. Match task inputs,
  fixtures, harness settings, dependency versions, budgets, timeouts, retries, and available tools
  between the pair. The source snapshots differ only by the declared candidate.
- Keep deterministic verifiers outside the instantiated workspace. Evaluator-only fixtures,
  verifier paths, and golden answers must not appear in the workspace, a skill, or agent-visible
  task text.
- Reusable output-format constraints that the task genuinely requires are not leakage. They may
  appear in a skill or workflow, but hidden answers and verifier implementation details may not.
- Freeze scenarios and verifiers before either condition runs. Sandbox or prohibit external side
  effects not required by the scenario.
- A timeout is a task failure unless it meets the predeclared infrastructure-invalidity rule. Do
  not silently rerun, replace, or discard an unfavourable result.
- Record resolution, hard-invariant violations, steps, tokens or cost, skill discovery and
  invocation, resolution conditional on invocation, and a candidate-specific exposure measure such
  as always-loaded bytes. Invocation alone is not success.
- Preserve raw run outputs and verifier results with the candidate record so another maintainer can
  audit the decision.

The namespace `evaluations/<candidate-id>/` is reserved for each pre-registration, scenarios,
external verifiers, and result record. Create it only when the first real candidate is evaluated;
it must not ship as an empty scaffold.

## Predeclared shipping rules

### Always-loaded context

A context reduction ships only if the pre-registered uncertainty rule supports non-inferiority on
the primary outcome under the pre-registered margin, no hard invariant regresses, and the claimed
step, token, or cost benefit is observed. Otherwise revise or retain the current context. A cost
increase is accepted only when the pre-registered rule ties it to a measured safety or correctness
gain. A hard-invariant failure blocks release; it is not averaged away.

### Skills

A new family-distributed skill ships only if its applicable-task benefit meets or exceeds the
pre-registered threshold, causes no hard-invariant regression, and does not regress the nearest
non-applicable case. Otherwise revise it or keep it instance-local. Existing family skills
are not removed retroactively merely because this protocol did not exist when they shipped.
Repeated journal evidence may justify an instance-local provisional skill, but does not authorise
family distribution.

### Optional task-acceptance fields

The optional objective, output-path, output-format, and acceptance-check prompts proposed for the
default workflow use this same paired protocol. They ship only under their pre-registered
correctness and cost rule; reference-patch confounding remains a stated risk.

## Why this stays small

Decision 0002 deferred a standing evaluation member until real instance history exists. A
permanent bank would add blank machinery and invite optimisation to familiar fixtures. A fresh,
candidate-specific record preserves the useful discipline without manufacturing inputs or making
evaluation a fourth template.

## Protocol integrity

Append a dated summary under Evaluation outcomes after each completed candidate evaluation,
including source identifiers, harnesses, trial count, primary results, invariant findings,
step/cost result, and release verdict. Record the eventual context-diet result there. Do not
rewrite the protocol after results are visible; a methodological change requires a dated addendum
or a superseding decision.

## Evaluation outcomes
