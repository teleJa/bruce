---
name: write-plan
description: Use when a software change has multiple dependent steps, cross-component coordination, or a handoff need that benefits from a persistent implementation plan. Build a minimal executable plan from the task contract and repository facts without generating tests, reviews, approvals, or execution state automatically.
---

# Write plan

Create the smallest plan that makes dependencies and verification unambiguous.

## Artifact placement

Use the shared resolver in [artifact-placement.md](../bruce/references/artifact-placement.md). A
cross-repository task keeps one `plan.md` and one `tasks/` package in the shared change directory;
component ownership and repository paths stay inside the task contracts rather than becoming one plan
or task package per repository. Read [task-contract.md](../bruce/references/task-contract.md).

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
   When a task creates, replaces, deletes, transfers, or projects a relationship, record a consistency
   classification, business-invariant and authoritative-state summary, competing writers/viewers,
   conflict consequence, and the `test-plan.md` matrix/scenario references in the task contract. Keep
   detailed conflict matrices and per-scenario evidence in `test-plan.md`; do not create two independent
   detailed sources of truth. Do not leave these semantics implicit in implementation detail.
3. When persisting an implementation plan, create one change-level `tasks/` package by default. Write
   `tasks/index.yaml` for stable order, dependencies, acceptance ids, and path ownership, and write
   one `T-<id>-<slug>.md` from [task.md](templates/task.md) for each frozen task contract. A trivial
   documentation-only change may omit the package only with a concrete recorded reason.
4. Keep a single `plan.md` in the shared change directory. It summarizes the task package; task-local
   contract detail belongs in `tasks/`, not in one oversized plan or one plan per repository.
5. Mark `parallel_safe` only when dependencies and file ownership prove it. Bruce executes tasks
   sequentially by default; do not select a model, process, isolation mechanism, or scheduler.
6. Ensure every acceptance item maps to a task and verification, dependencies exist and are acyclic,
   every task has explicit included and excluded scope, and no task depends on unstated context. For
   relationship or permission-projected state, also ensure the plan identifies the invariant and
   authority that govern the state; otherwise return a planning gap instead of allowing the UI to
   define the business rule implicitly.
7. Persist the result using [plan.md](templates/plan.md), [tasks-index.yaml](templates/tasks-index.yaml),
   and [task.md](templates/task.md). Keep live status, checkpoint state, and approval outside the
   frozen task contracts; use the change-level `checkpoint.yaml` during execution.
8. Write natural-language fields in the user's language, using Simplified Chinese for a Chinese
   request; keep stable machine-facing tokens unchanged as specified by the language rule.
9. Inspect the plan and task-package diff and check requirement/acceptance coverage, task boundaries,
   dependencies, file/interface joins, Given/When/Then evidence anchors, omissions, placeholders,
   links, and path ownership. Repair issues and return `Document check: clear|issues`. When the plan
   will govern implementation, tell Bruce that `design-gate` is required; do not invoke it automatically.

## Output

Return exactly one outcome:

- `Plan: ready`: persist one minimal executable plan plus its frozen `tasks/` package and summarize
  the dependency order, high-risk steps, verification anchors, task-package path, and
  `Document check: clear|issues` result.
- `Missing planning evidence`: do not create or update `plan.md`; return the unresolved questions
  and smallest bounded inspection scopes to Bruce for evidence collection before retrying this skill.

## Does not own

Do not generate a test plan, database design, architecture, review, approval, progress ledger, or
execution automatically. Do not choose Bruce risk/profile, launch subagents, own repository
exploration, invoke another supporting skill automatically, or declare completion.
