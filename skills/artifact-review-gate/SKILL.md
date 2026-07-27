---
name: artifact-review-gate
description: Use before Bruce moves design-bearing work into implementation. Persist a same-directory artifact-review.md that enumerates candidate design artifacts, proves every required/generated/skipped decision with repository evidence, and blocks missing, stale, unreviewed, or unjustifiably skipped artifacts.
---

# Artifact review gate

Check design-artifact completeness independently from document-content review and execution logging.

## Inputs

- The task contract, profile, risk, acceptance, and current implementation boundary.
- The repository's documented artifact convention and resolved change directory.
- Outputs from selected design capabilities, including generated paths or `not needed` evidence.
- Current D0 and required D1 results for generated downstream-governing documents.
- The current repository facts used to justify every skipped candidate.

## Artifact placement

Reuse the same change directory that contains the task's design documents. When a `full` task has no
change directory yet, create `docs/change/<YYYYMMDD-HHmmss>-<short-slug>/`. Persist exactly one
`artifact-review.md` beside the design documents using
[artifact-review.md](templates/artifact-review.md). Update that file on re-review; do not create
parallel gate files.

## Candidate set

Always enumerate at least:

- requirement or clarification;
- `architecture.md`;
- `api-contracts.md`;
- `table-design.md`;
- `plan.md`;
- `test-plan.md`.

Repository conventions may map a candidate to an equivalent filename, but may not silently remove it
from the matrix. For each candidate record:

- applicability: `required` or `skipped`;
- delivery: `generated` or `skipped`;
- the resolved path when generated;
- repository-backed evidence for the applicability decision;
- current D0 and required D1 results.

Use `required` when the task or selected capability contract requires a durable artifact. Use
`generated` only after the file exists and its required review evidence is current. Use `skipped`
only when concrete repository and scope evidence proves the artifact is not needed. Configuration
schema wording alone does not require `table-design.md`; persistence schema, migration, table,
index, data-lifecycle, or repository-model changes do.

## Procedure

1. Resolve the same change directory used by the current task's design artifacts.
2. Inspect the task contract, repository facts, selected capabilities, and generated files.
3. Populate the complete candidate set. Preserve separate applicability and delivery columns so a
   required but missing file cannot be mislabeled as skipped.
4. Verify generated files exist and collect their current D0 plus any required D1 result. This gate
   consumes document-review results; it does not replace `doc-review-gate` or `plan-review`.
5. Verify every skip decision cites precise repository-backed evidence. A statement such as "not
   needed" without inspected scope or repository facts is insufficient.
6. Return `blocked` when any of these conditions is true:
   - a candidate is omitted;
   - a required artifact is missing, stale, or marked skipped;
   - a skipped candidate lacks repository-backed evidence;
   - a required D0 or D1 result is missing or failing;
   - paths, scope, contracts, or cross-document decisions materially conflict.
7. Persist or update `artifact-review.md`, including concrete findings and
   `Artifact gate: pass|blocked`. Inspect its actual diff, check facts, matrix completeness,
   placeholders, links, and consistency, and return `Document self-review: pass|issues`.
8. Do not begin behavior implementation unless the same-directory file exists, its self-review
   passes, and its current conclusion is `Artifact gate: pass`.
9. If task scope or implementation evidence changes any applicability decision, update the same
   file and rerun this gate before continuing affected implementation or reporting completion.

## Output

Return the resolved `artifact-review.md` path, candidate matrix, blocking findings, evidence
boundary, `Document self-review: pass|issues`, and `Artifact gate: pass|blocked`.

## Does not own

Do not write requirement, architecture, API, database, plan, or test content; approve unresolved
D1 issues; create Goal or execution state; copy candidate decisions into `execute_record.md`;
implement behavior; or declare delivery complete.
