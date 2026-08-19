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

## Mandatory review-mode selection

Before author-quality checks or review-matrix construction, evaluate the final task contract, diff,
evidence, and repair history and record exactly one `review_mode` plus one stable
`review_mode_reason`. Select the first matching reason in this precedence order:

1. `explicit-independent-request`: the user explicitly requested independent review;
2. `critical-risk`: risk is `critical`;
3. `guarded-multi-component-contract`: risk is `guarded` and the final state spans multiple
   components or propagated contracts;
4. `guarded-migration-rollout`: risk is `guarded` and the task combines migration and rollout;
5. `guarded-semantic-ambiguity`: risk is `guarded` and material semantic ambiguity remains;
6. `guarded-weak-evidence`: risk is `guarded` and the result relies mainly on weak executable
   evidence;
7. `guarded-repeated-repair`: risk is `guarded` and the current task completed two or more L1 repair
   rounds;
8. `guarded-broad-security-data-impact`: risk is `guarded` and the final state has broad security or
   data impact;
9. `none`: no independent trigger remains.

Reasons 1-8 require `review_mode: independent`; reason 9 requires `review_mode: main-agent`.

A `full` profile, multiple files, task duration, or subagent availability alone does not select
`independent`. Perform this check before any other internal review work, and repeat it when a repair
changes the final scope, risk trigger, review basis, or independence-triggering concern. Do not
silently downgrade a required independent review; if a clean-context native reviewer is unavailable,
return `Completion: blocked`.

## Internal checks

### Author quality

Inspect the final diff and affected call sites for unintended scope, omissions, error paths, edge
inputs, state transitions, resource cleanup, compatibility, security, permissions, concurrency,
idempotency, data integrity, and missing regression coverage as relevant. For changed documents,
verify factual grounding, terminology, contracts, cross-document consistency, acceptance coverage,
placeholders, and links.

### Review completeness

Before reporting findings, build one review matrix for the final state. It covers every acceptance
id, direct changed entry point and direct call site needed by that acceptance, material
early-return/error/empty/null/partial/duplicate/state paths identified by the acceptance or changed
code, the required verification layer, and current evidence. Group equivalent paths and do not expand
transitive callers unless a propagated contract crosses that boundary. Mark every row `checked`,
`pass`, `incomplete`, or `finding`; do not return the terminal verdict while a material row is
unexamined. Report all findings from the completed matrix together in one packet, grouped by severity
and affected row. Do not stop after the first finding or issue an interim verdict. At minimum, each
row records `batch_id`, `acceptance_id`, `path`, `required_layer`, `basis_revision`,
`evidence_revision`, `evidence`, `result`, and `affected_scope`.

Repairable findings make the result `issues`. Any later change invalidates a row when its evidence
revision differs from the current review basis, a changed path intersects its affected scope, or
impact cannot be determined. Rerun stale rows, the unchanged original failed scenario, and related
regressions; this does not invalidate unaffected matrix rows, which may be reused. Batch compatible repairs and do not force a fresh
independent reviewer. Start one only when the repair changes an independence-triggering concern or
risk trigger, or when critical risk or the user explicitly requires it. This repair path does not
create a per-finding review chain.

### Acceptance evidence

Map every acceptance condition to current, reproducible evidence at the required layer. A unit test
does not prove required integration, persistence, deployment, or user-visible behavior. Treat stale,
missing, mocked-only, or natural-language evidence as a gap when stronger evidence is required.

### Proportional visual completeness

Read the task contract's `visual_scope` before deciding Web evidence. Do not turn every frontend or
UI-file diff into a full visual run:

- `none` is valid only when the final diff and acceptance have no material rendered, layout,
  responsive, or user-visible interaction outcome; record the repository-backed reason.
- `chrome-smoke` requires a current Codex App Chrome pass consisting of a real interaction against
  the target, the resulting visible state, and a screenshot or equivalent Chrome visual artifact;
  it does not require layout geometry when no layout invariant changed.
- `chrome-layout` requires current Chrome evidence plus the relevant screenshot, geometry/overflow,
  and interaction checks. For layout-sensitive changes, a DOM snapshot or text assertion cannot
  substitute for these artifacts.

Before returning a verdict, compare `visual_scope` with the final diff. A declaration that is weaker
than the changed visible risk is an `issues` finding, and its missing visual row is material. Evidence
must identify the target, capture time, basis revision, and screenshot/artifact path or hash; evidence
captured before a later affected change is stale and must be rerun. If a user reports a visual defect
after a pass, reopen the affected acceptance rows and do not reuse the old visual result.

Cross-check the declared risk against the changed scope. A `low` task records `trigger=none` plus
the repository evidence that rules out guarded and critical triggers; `guarded` and `critical` tasks
name the matching risk-policy trigger. A missing or contradictory trigger is an `issues` finding.

For `chrome-smoke` and `chrome-layout` Web acceptance, require current Codex App Chrome evidence
against the real target and current user session. The evidence must show the action, resulting
visible state, and visual artifact; `chrome-layout` must also show the relevant geometry/overflow
checks. When the declared scope is missing or Chrome is required but unavailable, keep the scenario
incomplete or blocked. Playwright is prohibited and any Playwright-only evidence is invalid; do not
substitute it for the required Chrome pass under any circumstance.

When a confirmed prototype governed implementation, map its required pages, states, interactions,
failure feedback, positive and negative assertions, layout invariants, reuse anchors, and visual
tokens to the real target. For an existing-product extension, also check the ordered visual authority,
selected/effective generation skill and visual plugin/design-system, compatibility evidence, exact
run-input summary, and the artifact checker's result. Check the manifest's exact confirmed identity,
effective-output state, lineage, hashes, four independent findings, and Visual state/evidence pair.
The governing manifest
must retain `effective_output_state = generated`, a separate `confirmation_state = confirmed`, and
either `automated-clear + automated` or exact-snapshot `manual-confirmed + manual-only`; pending,
blocked, unavailable, or mismatched Visual combinations are design-alignment issues. A blocked exact
token assertion remains a design-alignment issue even when the provider succeeded or the user supplied
manual-only confirmation. A provider score, prototype source, preview URL, prototype screenshot, or
`manual-only` prototype confirmation does
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

Apply the mandatory selection recorded above. In `main-agent` mode, perform the matrix and all
internal checks directly. In `independent` mode, give the clean-context native reviewer only the
objective, acceptance, final diff, raw evidence, necessary repository constraints, and review-matrix
schema. Exclude author rationale, confidence, and proposed verdict. The reviewer must return the
completed matrix and one consolidated findings packet. Independence is a mode of this gate, not a
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

Return `Completion: pass|issues|blocked`, `review_mode: main-agent|independent`,
`review_mode_reason`, the completed review matrix, consolidated findings packet, scenario-level
acceptance evidence, design alignment, scope findings, repair-loop results, residual risks, and the
smallest next action. Keep the result in the current task; `goal-execution` may record it when Goal
mode is active.

### Output format example

Use the stable top-level fields in the order shown below. `Completion` is the only terminal verdict;
all remaining fields are supporting evidence, context, or follow-up action rather than additional
verdicts. Do not use aliases such as `completion_verdict`. Use `[]` for an empty collection rather
than omitting the field or returning `null`. `review_mode: main-agent` requires
`review_mode_reason: none`; `review_mode: independent` requires one of reasons 1-8 from the mandatory
review-mode selection.

```yaml
Completion: pass
review_mode: independent
review_mode_reason: guarded-multi-component-contract
review_matrix:
  - batch_id: batch-1
    acceptance_id: AC-1
    path: src/example.ts
    required_layer: integration
    basis_revision: abc123
    evidence_revision: abc123
    evidence: integration-test
    result: pass
    affected_scope:
      - src/example.ts
findings: []
acceptance_evidence:
  - acceptance_id: AC-1
    evidence: integration-test
design_alignment: clear
scope_findings: []
repair_loop_results: []
residual_risks: []
next_action: none
```

## Does not own

Do not modify implementation, fabricate evidence, maintain Goal or audit state, approve host
permissions, or execute delivery actions.
