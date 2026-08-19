---
name: write-plan
description: Use when a software change has multiple dependent steps, cross-component coordination, or a handoff need that benefits from a persistent implementation plan. Build a minimal executable plan from the task contract and repository facts without generating tests, reviews, approvals, or execution state automatically.
---

# Write plan

Create the smallest plan that makes dependencies and verification unambiguous.

## Artifact placement

Use the shared resolver in [artifact-placement.md](../bruce/references/artifact-placement.md). A
cross-repository task keeps one `plan.md` in the shared change directory; component ownership and
repository paths stay inside the task list rather than becoming one plan per repository.

## Inputs

- Objective, scope, acceptance, constraints, execution profile, and risk.
- Current repository structure, commands, conventions, and dirty-worktree boundaries.
- Optional architecture, public contracts, or database design that the plan must consume.
- A requested output path; default to the repository's existing planning convention.
- The document language rule in [document-language.md](../bruce/references/document-language.md).

## Procedure

1. Inspect the task contract and repository evidence already provided by Bruce. For a `full` profile,
   require named components plus the propagated contract or independent delivery boundary. Consume
   synthesized `inspect-parallel` findings when Bruce already produced them. Do not launch subagents,
   invoke `inspect-parallel`, or own parallel repository inspection. If material facts about files,
   interfaces and consumers, verification commands, dependencies, ownership, or dirty-worktree
   boundaries remain missing, do not persist a plan. Return `Missing planning evidence` with the
   unresolved questions and smallest bounded scopes Bruce must inspect before invoking `write-plan`
   again. Do not plan against invented paths or APIs.
2. Split work into feature-bearing tasks with stable ids. For each task record title, dependencies,
   files/scope, consumed/produced interfaces, implementation detail, acceptance, and verification.
   Reference the parent Given/When/Then scenario ids and required evidence layer for behavior tasks.
3. Keep a single `plan.md` unless the repository or user explicitly requires another structure.
   For the full profile, tag component ownership and contract dependencies inside the task list rather
   than automatically creating one plan per component.
4. Mark parallel safety only when dependencies and file ownership prove it. Do not select a model,
   process, isolation mechanism, or scheduler.
5. Ensure every acceptance item maps to work and verification, dependencies exist and are acyclic,
   and no task depends on unstated context.
6. Persist the result using [plan.md](templates/plan.md). Keep status and approval outside the plan
   unless the target repository has an explicit, user-authorized convention requiring them.
7. Write natural-language fields in the user's language, using Simplified Chinese for a Chinese
   request; keep stable machine-facing tokens unchanged as specified by the language rule.
8. Inspect the plan diff and check requirement/acceptance coverage, task boundaries,
   dependencies, file/interface joins, Given/When/Then evidence anchors, omissions, placeholders,
   and links. Repair issues and return `Document check: clear|issues`. When the plan will govern
   implementation, tell Bruce that `design-gate` is required; do not invoke it automatically.

## Output

Return exactly one outcome:

- `Plan: ready`: persist one minimal executable plan and summarize its dependency order, high-risk
  steps, verification anchors, and `Document check: clear|issues` result.
- `Missing planning evidence`: do not create or update `plan.md`; return the unresolved questions
  and smallest bounded inspection scopes to Bruce for evidence collection before retrying this skill.

## Does not own

Do not generate a test plan, database design, architecture, review, approval, progress ledger, or
execution automatically. Do not choose Bruce risk/profile, launch subagents, own repository
exploration, invoke another supporting skill automatically, or declare completion.
