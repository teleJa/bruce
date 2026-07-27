---
name: write-plan
description: Use when a software change has multiple dependent steps, cross-component coordination, or a handoff need that benefits from a persistent implementation plan. Build a minimal executable plan from the task contract and repository facts without generating tests, reviews, approvals, or execution state automatically.
---

# Write plan

Create the smallest plan that makes dependencies and verification unambiguous.

## Inputs

- Objective, scope, acceptance, constraints, execution profile, and risk.
- Current repository structure, commands, conventions, and dirty-worktree boundaries.
- Optional architecture, public contracts, or database design that the plan must consume.
- A requested output path; default to the repository's existing planning convention.

## Procedure

1. Inspect the files and commands each step will touch. Do not plan against invented paths or APIs.
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
7. Inspect the plan diff and check requirement/acceptance coverage, task boundaries,
   dependencies, file/interface joins, Given/When/Then evidence anchors, omissions, placeholders,
   and links. Repair issues and return `Document check: clear|issues`. When the plan will govern
   implementation, tell Bruce that `design-gate` is required; do not invoke it automatically.

## Output

Produce one minimal executable plan and summarize its dependency order, high-risk steps, and
verification anchors. Include the document-check result.

## Does not own

Do not generate a test plan, database design, architecture, review, approval, progress ledger, or
execution automatically. Do not choose Bruce risk/profile or declare completion.
