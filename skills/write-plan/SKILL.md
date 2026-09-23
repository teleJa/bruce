---
name: write-plan
description: Use when a software change has multiple dependent steps, cross-component coordination, or a handoff need that benefits from a persistent implementation plan. Translate confirmed architecture or task decisions into a development-ready plan with concrete integration work, dependency order, and verification, without silently redesigning upstream contracts or starting execution.
---

# Write plan

Translate confirmed design into the smallest plan that can guide development. Supplement the design
with implementation sequencing, integration work, and verification; do not merely restate architecture
or list task titles. A developer without the analysis history should be able to start from this plan
and its necessary references without re-deciding business rules or architecture.

## Design-to-implementation boundary

- Consume confirmed architecture, API/data contracts, or task decisions already established in the
  conversation. A simple change does not require an architecture document merely to write a plan.
  Reference the authoritative source and affected decision instead of copying the whole design.
- Complete the implementation arrangements that affect task boundaries or other developers: existing
  integration points, consumed/produced interfaces, prerequisites, dependency order, shared-file
  ownership, and applicable migration, compatibility, cutover, or recovery steps. Derive these from
  actual repository facts and confirmed constraints, not from a generic implementation checklist.
- Leave local choices such as private helper extraction, naming, and equivalent internal algorithms
  to the executor when they do not change contracts, task ownership, required behavior, or evidence.
  Distinguish these choices from frozen decisions; do not prescribe line-by-line code or require new
  approval for a permitted local choice.
- Within the first 15 lines of the persisted plan (immediately after the title), include two mandatory
  sections before any technical detail:
  - `## Behavior delta`: a table listing every scenario where behavior changes (before vs after), so
    the reviewer can scan behavioral impact without reading the full technical plan.
  - `## Inferred assumptions`: a numbered list of every behavior the AI inherited from existing code
    or existing flows and assumed applies to the new implementation. Even if the AI considers the
    assumption reasonable, it must be listed here explicitly; it must not appear only inside the
    solution description. Every listed assumption must include a user-confirmation reference or an
    explicit `Pending user confirmation` status. A pending or unconfirmed assumption blocks the
    document review and cannot be treated as an effective plan constraint.
  A plan that violates this structure is incomplete; do not persist it.
- If implementation planning exposes a missing business rule, incompatible interface, ambiguous
  state/data semantics, or a necessary change to confirmed architecture or authorization, return the
  concrete conflict, affected tasks, and options to Bruce/the user. Do not silently resolve it by
  redesigning the system or by writing “handle during development” into an executable task.

## Artifact placement

Use the shared resolver in [artifact-placement.md](../bruce/references/artifact-placement.md). A
cross-repository task keeps one `plan.md` and, when independently needed, one `tasks/` package in the shared change directory;
component ownership and repository paths stay inside the task contracts rather than becoming one plan
or task package per repository. Read [task-contract.md](../bruce/references/task-contract.md).

## Inputs

- Objective, scope, acceptance, constraints, execution profile, and risk.
- Current repository structure, commands, conventions, and dirty-worktree boundaries.
- Confirmed architecture, public contracts, database design, or conversation/task decisions, as applicable;
  include their authoritative locations and the constraints that implementation must preserve.
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
   Classify a gap by its effect: an unresolved upstream decision returns to design discussion; a
   material implementation fact needs bounded evidence collection; a permitted local coding choice
   is not a planning blocker. Identify the affected task and dependency boundary rather than treating
   every unknown as a whole-design failure. Preserve existing plan files and confirmed task decisions
   while a material gap remains; once resolved, revise only affected tasks and joins, reusing valid
   evidence instead of repeating the full investigation or regenerating unrelated work.
2. Split work into feature-bearing tasks with stable ids. For each task record title, dependencies,
   files/scope, consumed/produced interfaces, implementation detail, acceptance, and verification.
   Make the implementation detail actionable: locate existing files/symbols and their roles, label
   proposed new paths as new, describe the concrete change and task-local deliverable, and identify
   which predecessor output or execution precondition must be available first. Include migration,
   old/new compatibility, cutover, and recovery order only when the change needs them. Do not treat
   several subtasks touching the same file as independent without an ownership and integration order.
   Reference the parent Given/When/Then scenario ids and required evidence layer for behavior tasks.
   When a task creates, replaces, deletes, transfers, or projects a relationship, record a consistency
   classification, business-invariant and authoritative-state summary, competing writers/viewers,
   conflict consequence, and the `test-plan.md` matrix/scenario references in the task contract. Keep
   detailed conflict matrices and per-scenario evidence in `test-plan.md`; do not create two independent
   detailed sources of truth. Do not leave these semantics implicit in implementation detail.
3. Apply [artifact-policy.md](../bruce/references/artifact-policy.md) independently. A simple plan needs no `tasks/`, independent `test-plan.md`, omission record, or Design Gate solely because it is persisted;
   behavior changes still include minimum test design, commands, and evidence in the plan or task contract.
   When frozen per-task boundaries, handoff, or delivery tracking require a package, create one
   change-level `tasks/` package with `tasks/index.yaml` using
   [tasks-index.yaml](templates/tasks-index.yaml) and [task.md](templates/task.md). Preserve stable order, ownership, acceptance ids, and revisions.
4. Keep one `plan.md`. Without a package it holds the executable steps and verification directly;
   with a package it summarizes and references frozen contracts instead of copying them. When a
   persisted design will be consumed by a different execution model/profile, or when implementation
   needs a durable handoff, also persist one `execution-handoff.md` beside the plan using
   [execution-handoff.md](templates/execution-handoff.md). The handoff is an execution contract, not
   a second design source of truth: it must freeze allowed/excluded paths, implementation-map joins,
   confirmed decisions, executor-only verification facts, required checks, investigation budget, and
   stop conditions. Do not leave the executor to rediscover these boundaries from the full design set.
5. Mark `parallel_safe` only when dependencies and file ownership prove it. Bruce executes tasks
   sequentially by default; do not select a model, process, isolation mechanism, or scheduler.
6. Ensure every acceptance item maps to a task and verification, dependencies exist and are acyclic,
   every task has explicit included and excluded scope, and no task depends on unstated context. When
   an execution handoff is required, every `executor_must_verify` item must have a bounded source and
   every implementation step must join to an allowed path, acceptance item, and verification command. For
   relationship or permission-projected state, also ensure the plan identifies the invariant and
   authority that govern the state; otherwise return a planning gap instead of allowing the UI to
   define the business rule implicitly.
   Check the plan from the receiving developer's perspective: can they identify where to start, what
   result to produce, what must not change, which local decisions are theirs, and how to verify the
   result without reopening upstream design? If not, supply the missing implementation arrangement
   or return the specific planning gap. Record expected verification, commands/checks, prerequisites,
   and observable results; planning does not prove those tests have run or the feature has passed.
7. Persist the result using [plan.md](templates/plan.md), removing inapplicable optional sections.
   Only use task-package templates when that package is needed. Keep live status and approval outside
   frozen contracts; checkpoint triggers remain owned by the shared recovery policy.
8. Write natural-language fields in the user's language, using Simplified Chinese for a Chinese
   request; keep stable machine-facing tokens unchanged as specified by the language rule.
9. Inspect the plan and task-package diff and check requirement/acceptance coverage, task boundaries,
   dependencies, file/interface joins, Given/When/Then evidence anchors, omissions, placeholders,
   links, path ownership, and confirmation references for every inferred assumption. If any inferred
   assumption lacks user confirmation, return `Document check: issues`; do not pass the document
   review. Repair issues and return `Document check: clear|issues`. When the plan
   contains a governing design decision or downstream contract, return a mandatory `design-gate`
   handoff under the shared artifact policy. Bruce/the caller coalesces pending handoffs, finishes the
   already authorized design batch's required artifacts and local checks, then runs one Gate in the
   same turn the batch becomes ready, without another user instruction. A single-artifact batch runs
   the Gate immediately after its check. This
   writer does not own the Design verdict. An execution checklist alone does not require the handoff.

## Handoff to review and write-task

A plan that will enter development must first complete independent review. The Agent must wait for the
reviewer result and the user confirmation of the plan. Only after confirmation may it invoke `write-task`.
The plan defines the overall change; `write-task` creates the concrete frozen task contracts and
`tasks/index.yaml` before Design Gate. The old conditional task-package predicate does not apply to this
development path.

## Output

Return exactly one outcome:

- `Plan: ready`: persist one minimal executable plan, plus a task package only when independently
  required; summarize dependency order, risks, verification anchors, any task-package path, and
  `Document check: clear|issues` result.
- `Missing planning evidence`: do not create or update `plan.md` or `execution-handoff.md`; return the unresolved questions
  and smallest bounded inspection scopes to Bruce for evidence collection, or the required upstream
  decision when investigation cannot settle it. Preserve valid prior work and retry only the affected
  planning scope once the gap is resolved; do not label unresolved material work executable.

## Does not own

Do not generate a test plan, database design, architecture, review, approval, progress ledger, or
execution automatically. Do not choose Bruce risk/profile, launch subagents, or own repository
exploration. The mandatory Design Gate handoff is the only automatic continuation; other supporting
skills remain predicate-driven. Do not declare completion.
