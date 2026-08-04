---
name: completion-gate
description: Use after implementation as Bruce's only completion decision. Check final scope, author quality, acceptance evidence, design alignment, failures, and delivery boundaries, adding an independent reviewer only when risk or the user requires it, then return one Completion verdict.
---

# Completion Gate

Decide whether the task is complete from current evidence. This is Bruce's only completion decision;
callers do not rerun its checks or combine separate author, verification, and review verdicts.

## Inputs

- Objective, scope, acceptance, constraints, profile, and risk.
- Actual workspace status and final diff, including pre-existing unrelated changes.
- Current test, lint, build, integration, page, database, and external-tool evidence.
- Given/When/Then acceptance scenarios when behavior changed.
- Current `design-review.md` when Design Gate was required.
- Current `prototype-manifest.md` and confirmed snapshot when a prototype governed UI implementation.
- L0-L4 failures, repair history, open decisions, residual risks, and requested delivery actions.

## Internal checks

### Author quality

Inspect the final diff and affected call sites for unintended scope, omissions, error paths, edge
inputs, state transitions, resource cleanup, compatibility, security, permissions, concurrency,
idempotency, data integrity, and missing regression coverage as relevant. For changed documents,
verify factual grounding, terminology, contracts, cross-document consistency, acceptance coverage,
placeholders, and links.

Repairable findings make the result `issues`. Any later change invalidates the affected check and
requires this gate to run again.

### Acceptance evidence

Map every acceptance condition to current, reproducible evidence at the required layer. A unit test
does not prove required integration, persistence, deployment, or user-visible behavior. Treat stale,
missing, mocked-only, or natural-language evidence as a gap when stronger evidence is required.

For user-visible Web acceptance, require current Codex App Chrome evidence against the real target
and current user session. When Chrome is required but unavailable, keep the scenario incomplete and
do not silently substitute Playwright.

When a confirmed prototype governed implementation, map its required pages, states, interactions,
failure feedback, positive and negative assertions, layout invariants, reuse anchors, and visual
tokens to the real target. Check the manifest's exact confirmed identity, effective-output state,
lineage, hashes, four independent findings, and Visual state/evidence pair. The governing manifest
must retain `effective_output_state = generated`, a separate `confirmation_state = confirmed`, and
either `automated-clear + automated` or exact-snapshot `manual-confirmed + manual-only`; pending,
blocked, unavailable, or mismatched Visual combinations are design-alignment issues. A provider score,
prototype source, preview URL, prototype screenshot, or `manual-only` prototype confirmation does
not prove the implementation matches it; require current Codex App Chrome evidence for every
material visible outcome.

### Design alignment

When Design Gate was required, compare the final diff and scope with `design-review.md`. Return
`issues` if the review is missing, stale, blocked, omits a candidate, no longer supports a skip, or
does not cover an actual public/cross-component contract, schema, plan, test-design, or UI prototype
obligation.
Do not rerun Design Gate inside completion; return the mismatch to Bruce for one explicit rerun.

### Failure and delivery boundaries

Require the unchanged original failed scenario and related regressions after an L1 repair. Return
`blocked` for unresolved authority, unsafe external state, or L2-L4 conditions that prevent a valid
completion decision. Confirm requested delivery actions were authorized and completed, or report
them outside the completed boundary.

## Review mode

Use `main-agent` mode for low risk and ordinary guarded work. Use an `independent` clean-context
native reviewer when:

- guarded work spans multiple components/contracts, combines migration and rollout, has material
  semantic ambiguity, relies mainly on weak executable evidence, follows repeated repair, or has
  broad security/data impact;
- risk is critical; or
- the user explicitly requests independent review.

Give the reviewer only objective, acceptance, the final diff, raw evidence, and necessary repository
constraints. Exclude author rationale, confidence, and proposed verdict. If independent review is
required but unavailable, return `Completion: blocked`. Independence is a mode of this gate, not a
second externally combined verdict.

## Decision

Return exactly one terminal field:

- `Completion: pass` when scope matches, every acceptance item has sufficient current evidence,
  author-quality checks are clear, required design remains aligned, required independent review
  found no blocking issue, and no required work remains.
- `Completion: issues` when in-scope implementation, documentation, design alignment, or evidence
  gaps are repairable.
- `Completion: blocked` when authority, unavailable required independent review, external state, or
  unresolved L2-L4 prevents completion.

## Output

Return `Completion: pass|issues|blocked`, review mode (`main-agent|independent`), scenario-level
acceptance evidence, design alignment, scope findings, repair-loop results, residual risks, and the
smallest next action. Keep the result in the current task; `goal-execution` may record it when Goal
mode is active.

## Does not own

Do not modify implementation, fabricate evidence, maintain Goal or audit state, approve host
permissions, or execute delivery actions.
