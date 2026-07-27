---
name: design-gate
description: Use before implementation when persisted requirements, architecture, contracts, schema design, plans, or test designs will govern downstream work. Decide artifact completeness and document readiness together, persist one design-review.md, and return one Design verdict.
---

# Design Gate

Make the single implementation-entry decision for persisted downstream design. This gate owns both
artifact completeness and document readiness; callers do not run or combine separate author-check,
readiness, or artifact-gate protocols.

## Inputs

- The task contract, resolved profile, risk, acceptance, and implementation boundary.
- The repository's artifact convention and resolved change directory.
- The actual design files and repository facts that justify generated or skipped candidates.
- The implementation boundary that the design will govern.

## Candidate set

Resolve one change directory and enumerate these candidates in `design-review.md`:

- requirement or clarification;
- `architecture.md`;
- `api-contracts.md`;
- `table-design.md`;
- `plan.md`;
- `test-plan.md`.

Repository conventions may map a candidate to an equivalent filename but may not silently omit it.
For each candidate record applicability (`required|skipped`), delivery (`generated|skipped`), the
resolved path, and repository-backed evidence.

## Readiness checks

For every generated document:

1. Verify important factual claims against code, configuration, schema, or authoritative upstream
   documents.
2. Check terminology, fields, states, interfaces, and cross-document references for consistency.
3. Check acceptance coverage, material omissions, unresolved placeholders, and broken links.
4. Apply the relevant readiness view:
   - requirements: scope, actors, rules, main/error flows, and verifiable acceptance;
   - architecture/contracts: boundaries, interfaces, failures, compatibility, security, recovery,
     observability, and testability;
   - plans: acceptance coverage, dependency order, file ownership, interface joins, risk, and
     executable verification;
   - test design: environment/data prerequisites, real dependencies, actions, assertions, failure,
     permission, regression, and traceability.
5. Record only evidence-backed blockers that can cause wrong implementation, unsafe execution, or
   unverifiable acceptance. Wording preferences and optional polish do not block.

Use a clean-context native reviewer only when the user explicitly requests independent design
review or the design carries critical security, data, migration, or irreversible-operation risk.
The reviewer receives objective, acceptance, the final document snapshot/diff, raw evidence, and
necessary constraints without the author's rationale or proposed verdict. Independence changes how
the check runs, not the output schema.

## Procedure

1. Reuse the current change directory. When no repository convention or current directory exists,
   create `docs/change/<YYYYMMDD-HHmmss>-<short-slug>/`.
2. Populate the complete candidate matrix. A required but missing file cannot be marked skipped.
3. Verify every generated path exists and every skip cites concrete repository and scope evidence.
4. Perform the readiness checks against the actual files and current repository facts.
5. Return `blocked` when a candidate is omitted, a required artifact is missing or stale, a skip is
   unsupported, documents materially conflict, a blocking readiness issue remains, or required
   independent review cannot run.
6. Persist or update exactly one same-directory `design-review.md` using
   [design-review.md](templates/design-review.md). Reuse it on re-review.
7. Inspect the review file itself for matrix completeness, accurate evidence, placeholders, links,
   and consistency.
8. Return `Design: pass|blocked` with blocking findings and the smallest next action.

Any later scope or design change invalidates the affected verdict. Rerun this gate before continuing
affected implementation.

## Output

Return the `design-review.md` path, candidate matrix, evidence boundary, review mode
(`main-agent|independent`), blocking findings, smallest next action, and one final field:

`Design: pass|blocked`

## Does not own

Do not implement behavior, create Goal state, decide delivery completion, perform delivery actions,
or create parallel readiness records.
