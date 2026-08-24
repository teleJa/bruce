---
name: design-gate
description: Use before implementation when persisted requirements, architecture, contracts, schema design, plans, test designs, or UI prototypes will govern downstream work. Decide artifact completeness and document readiness together, persist one design-review.md, and return one Design verdict.
---

# Design Gate

Make the single implementation-entry decision for persisted downstream design. This gate owns both
artifact completeness and document readiness; callers do not run or combine separate author-check,
readiness, or artifact-gate protocols.

## Artifact placement

Resolve the change directory with [artifact-placement.md](../bruce/references/artifact-placement.md)
before enumerating candidates. For cross-repository work, the direct-parent comparison is bounded: a
shared direct parent may provide `.bruce/config.yaml`, while different direct parents require asking the
user for the document path.

## Inputs

- The task contract, resolved profile, risk, acceptance, and implementation boundary.
- The repository's artifact convention and resolved change directory.
- The actual design files and repository facts that justify generated or skipped candidates.
- The implementation boundary that the design will govern.
- The document language rule in [../bruce/references/document-language.md](../bruce/references/document-language.md).
- The deterministic [Design Review validator](scripts/validate_design_review.py).
- The task-contract package rule in [../bruce/references/task-contract.md](../bruce/references/task-contract.md).

## Candidate set

Resolve one change directory and enumerate these candidates in `design-review.md`:

- requirement or clarification;
- `architecture.md`;
- `api-contracts.md`;
- `table-design.md`;
- `plan.md`;
- `test-plan.md`;
- UI prototype, resolved through `prototype-manifest.md` when applicable.

Repository conventions may map a candidate to an equivalent filename but may not silently omit it.
For each candidate record applicability (`required|skipped`), delivery
(`generated|missing|skipped`), the resolved path, and repository-backed evidence. `required/missing`
is a valid blocked-state record; `required/skipped` and `skipped/generated` are invalid.

When the implementation plan is generated for a multi-step, `full`, guarded, long-running, or
handoff-worthy change, its delivery also includes one change-level `tasks/` package. The package is
an execution-contract companion to `plan.md`, not a second design verdict or a separate repository
plan. Inspect `tasks/index.yaml` and every referenced task file for stable ids, dependency order,
include/exclude scope, acceptance and verification mapping, and frozen contract revisions. A missing
or empty required task package blocks readiness; a trivial documentation-only omission must be
recorded with a concrete reason.

Record the fixed applicability decisions `Behavior implementation: yes|no`,
`Public/cross-component contract change: yes|no`, `Database/persistence design change: yes|no`, and
`Governing UI prototype: yes|no`. A required persisted implementation plan always makes Test design
required; a few verification bullets inside `plan.md` are not a substitute for `test-plan.md`. A `yes`
contract, persistence, or governing-prototype decision makes its corresponding candidate required.

For the UI prototype candidate, `generated` means the artifact is materialized in the current change
directory, including an imported user-supplied prototype. An external URL alone is not delivery.

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
   - UI prototypes: surface classification; brief grounding and positive/negative assertions;
     repository UI contract plus baseline for an existing-product extension; required
     pages/states/interactions; preflight evidence; effective changed output; explicit user
     confirmation; generated/confirmed snapshot separation; Functional, Visual, Safety, and
     Provenance findings; file hashes, lineage, gaps, and implementation acceptance evidence. For an
     existing-product extension, also verify the ordered visual authority, selected/effective
     generation skill and visual plugin/design-system, compatibility evidence, run input summary,
     filled visual anchors, and deterministic exact-token result. Reject template placeholders,
     empty evidence/verification cells, or a high-fidelity claim whose applicable shell/layout,
     palette, typography, brand, and geometry dimensions are not governed by baseline or anchors.
5. Record only evidence-backed blockers that can cause wrong implementation, unsafe execution, or
   unverifiable acceptance. Wording preferences and optional polish do not block.

Use a clean-context native reviewer only when the user explicitly requests independent design
review or the design carries critical security, data, migration, or irreversible-operation risk.
The reviewer receives objective, acceptance, the final document snapshot/diff, raw evidence, and
necessary constraints without the author's rationale or proposed verdict. Independence changes how
the check runs, not the output schema.

## Functional Agent routing

An independent design review uses the `reviewer` Profile with a clean-context Task Packet and returns a `review_packet`; any evidence reproduction used by the gate uses the `verifier` Profile and returns a `verification_packet`. Neither Packet may contain a terminal verdict. Design Gate remains the only owner of `Design: pass|blocked`.

## Procedure

1. Resolve or reuse the change directory with [artifact-placement.md](../bruce/references/artifact-placement.md).
   For cross-repository work, reuse only a task-identified directory; if participating repositories have
   different direct parents and no user path is available, ask the user before creating artifacts.
2. Populate the complete candidate matrix. Record a required absent artifact as `required/missing`;
   it cannot be marked skipped.
3. Verify every generated path exists and every skip cites concrete repository and scope evidence.
4. Perform the readiness checks against the actual files and current repository facts.
5. Return `blocked` when a candidate is omitted, a required artifact is missing or stale, a skip is
   unsupported, documents materially conflict, a blocking readiness issue remains, or required
   independent review cannot run. A governing prototype is also blocked when
   `prototype-manifest.md` is absent, confirmation is pending, material product facts remain
   unresolved, an existing-product high-fidelity claim lacks its UI contract or baseline, effective
   output is `no_artifact` or `no_effect`, hashes are stale, or its Functional, Safety, or Provenance
   check is not clear. A governing result must retain `effective_output_state = generated` and a
   separate `confirmation_state = confirmed`. Visual readiness accepts only
   `automated-clear + automated`, or `manual-confirmed + manual-only` with confirmation evidence that
   names the inspected exact snapshot. Pending or blocked Visual checks, unavailable Visual evidence,
   and every mismatched pair cannot govern implementation. `manual-confirmed + manual-only` cannot
   override `exact_token_assertions = blocked`; deterministic assertions must be `clear` first.
6. Write the review's natural-language fields in the user's language, using Simplified Chinese for
   a Chinese request; preserve candidate names, paths, statuses, and verdict tokens.
7. Persist or update exactly one same-directory `design-review.md` using
   [design-review.md](templates/design-review.md). Reuse it on re-review.
8. Run `python3 <plugin-root>/skills/design-gate/scripts/validate_design_review.py --change-dir
   <change-directory>` against the current files. A non-zero result or an unexecuted validator forces
   `Design: blocked`; never write or report `Design: pass` from prose inspection alone.
9. Inspect the review file itself and the validator output for matrix completeness, accurate evidence,
   placeholders, links, current paths, and verdict consistency.
10. Record validator `Result: pass` only from the current zero exit; the persisted result line is a
    trace field, not authority. The hook or direct validator subprocess exit code is authoritative;
    this validator result confirms document integrity and is independent of whether the Design verdict
    is `pass` or `blocked`. Return `Design: pass|blocked` with blocking findings, validator evidence,
    and the smallest next action.

Any later scope or design change invalidates the affected verdict. Rerun this gate before continuing
affected implementation.

## Output

Return the `design-review.md` path, candidate matrix, evidence boundary, review mode
(`main-agent|independent`), validator command/result, blocking findings, smallest next action, and one
final field:

`Design: pass|blocked`

## Does not own

Do not implement behavior, create Goal state, decide delivery completion, perform delivery actions,
or create parallel readiness records.
