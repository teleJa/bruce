---
name: plan-review
description: Use when an actual implementation plan has meaningful execution risk or the user asks to review it. Check scope and acceptance coverage, dependencies, interfaces, file ownership, risk, and executable verification, then return blocking issues or a clean verdict without approving the plan or creating workflow state.
---

# Plan review

Review readiness, not writing style.

## Inputs

- The actual plan under review.
- The task contract or source requirement.
- Only the architecture, contracts, schema design, or test plan explicitly referenced by that plan.
- Current repository facts needed to verify high-risk claims.

## Functional Agent routing

Independent plan review uses the `reviewer` Functional Agent Profile and a v1 Task Packet with `task_kind=review`, clean context, no author conversation inheritance, read-only tools, and `output=review_packet`; carry `review_subject=plan` in the resulting `review_packet`, not in the Task Packet. The reviewer returns findings only; it does not approve the plan or emit a Design/Completion verdict.

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
6. Use `main-agent` review mode by default. When the user explicitly requests independent plan
   review, use a fresh native subagent with `fork_turns="none"` or equivalent clean context and the
   minimal input packet in [plan-reviewer-prompt.md](references/plan-reviewer-prompt.md). Report
   `Review mode: main-agent|independent`.

## Output

Return `Clean` or `Issues Found`. Each blocking issue must cite a task or source location, explain
the execution impact, and suggest the smallest correction. Keep non-blocking advice separate. Write
a review file only when the user explicitly requests a persistent record.

## Does not own

Do not approve the plan, change its status, maintain hashes or workflow state, require unrelated
artifacts, fix implementation, start execution, or declare completion.
