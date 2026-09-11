---
name: plan-review
description: Use when an actual implementation plan has meaningful execution risk or the user asks to review it. Check scope and acceptance coverage, dependencies, interfaces, file ownership, risk, and executable verification, then return blocking issues or a clean verdict without approving the plan or creating workflow state.
---

# Plan review

Review readiness, not writing style. This remains an optional standalone entry: do not automatically
add a `plan-review` invocation to another workflow. Once invoked, independent review is mandatory.
Author self-checks are allowed but never replace this review.

## Inputs

- The actual plan under review.
- The task contract or source requirement.
- Only the architecture, contracts, schema design, or test plan explicitly referenced by that plan.
- Current repository facts needed to verify high-risk claims.

## Functional Agent routing

Every invocation uses the shared `reviewer` Functional Agent Profile and a v1 Task Packet with
`task_kind=review`, clean context, no author conversation inheritance, read-only tools, and
`output=review_packet`; carry `review_subject=plan` in the resulting `review_packet`, not in the Task
Packet. Apply the shared [delegation contract](../bruce/references/delegation-contract.md) before
spawning. Resolve the model and effort through the shared Profile, never local routing.
The existing `fallback: blocked` policy applies to every selected reviewer model. An unavailable or
unconfirmed model must pause the affected review and ask the user to explicitly name an available
replacement, then re-resolve and confirm host capability. Never automatically switch models, inherit
the current model, or substitute main-agent self-review or a verifier. Missing native subagent or
clean-context capability also blocks the review. Do not introduce a private router or runtime.

The reviewer returns findings in the shared `review_packet`, with `review_mode=independent` and
`review_mode_reason=mandatory-independent-review` by default. Retain the shared explicit-request and
risk reasons when applicable; `none` is not allowed. It does not approve the plan, return `Clean` or
`Issues Found`, or emit any terminal verdict. Only the caller interprets a valid independent packet.

## Procedure

1. Check objective/scope/acceptance coverage and identify work that changes behavior without a
   mapped acceptance condition.
2. Validate task ids, dependency existence and acyclicity, file ownership, interface joins, and
   parallel-safety claims.
3. Check that task detail is executable from real paths, APIs, commands, and repository conventions.
4. Check risk, migration/recovery, external side effects, and verification where they materially
   affect execution safety.
5. Check referenced test design when present. Do not fail a plan merely because an optional sibling
   artifact does not exist.
6. For the initial review, use a fresh native reviewer with `fork_turns="none"` or equivalent clean
   context and the minimal input packet in
   [plan-reviewer-prompt.md](references/plan-reviewer-prompt.md). Do not inherit author history,
   rationale, confidence, or proposed conclusions. Report `Review mode: independent`.
7. Validate the returned packet against the shared contract and the current plan snapshot. A completed
   packet requires resolved model evidence and a non-empty review matrix covering the reviewed basis.
   Do not ignore blocking findings. If repairs affect reviewed evidence, send the new snapshot to the
   original independent reviewer for re-review; a fresh reviewer is not required for every repair.
   Main-agent confirmation of a repair cannot replace reviewer re-review. If the original reviewer
   cannot continue, use a fresh clean-context reviewer under the same routing requirements.

## Repair and re-review limit

A repair changing objective, scope, acceptance, task boundaries, dependencies, file ownership, interfaces, risk, or verification evidence is a material plan revision. Recompute the snapshot and `basis_revision`, then send it to the independent reviewer. Cosmetic wording, formatting, or link repairs need only the document check.

The initial review is round 0. Allow at most two material repair-and-re-review rounds for one plan review. If the second re-review still has blocking findings, stop with the plan unresolved; do not continue an unbounded author-review loop. A new user-approved direction starts a new plan review.

## Review evidence binding

Before consuming a completed reviewer result, use `validate_review_for_basis` from
`scripts/functional_agent_profiles.py` with the current task id, actual native reviewer dispatch id,
current artifact/acceptance/evidence snapshot hash, retained pre-dispatch `model_resolution`, and this
review's subject. The result must carry the matching `review_basis`; do not copy returned values into
the expected context. Shape validation alone is insufficient. A repair or material evidence change
requires a new snapshot and independent re-review; do not accept an old packet or a different dispatch's
model record. Record these references in existing review/task evidence, not a new ledger.

## Output

The caller returns the existing `Clean` or `Issues Found` result only from a valid, completed
independent `review_packet` for the current snapshot. `Clean` requires no unresolved blocking
findings and sufficient review coverage; never invent a `pass` result. Each blocking issue must cite
a task or source location, explain the execution impact, and suggest the smallest correction. Keep
non-blocking advice separate. If required review was not executed, failed, or is incomplete, report
not executed / blocked with the evidence boundary and smallest next action, not `Clean`. For model
unavailability or uncertainty, that next action is the user's explicit selection of an available
replacement model, followed by capability confirmation and independent review. Write a review file
only when the user explicitly requests a persistent record.

## Does not own

Do not approve the plan, change its status, maintain hashes or workflow state, require unrelated
artifacts, fix implementation, start execution, or declare completion.
