---
name: write-task
description: Split a confirmed implementation plan into concrete frozen execution task contracts.
---

# Write task

Convert the confirmed `plan.md` into concrete execution tasks. This Skill is mandatory after
`write-plan` and before Design Gate for any plan that will enter development.

## Procedure

1. Confirm that the current plan has a completed independent reviewer packet for its current snapshot and
that the user has confirmed the plan. A reviewer result alone does not authorize task generation.
2. Read the current plan and its referenced requirements, architecture, contracts, database design,
   and test plan. Do not redesign confirmed decisions.
3. Split the plan into feature-bearing tasks with stable IDs. Each task must define objective,
   dependencies, included and excluded paths, consumed and produced interfaces, implementation target,
   acceptance IDs, verification commands, stop condition, and `parallel_safe`.
4. Create one change-level `tasks/` package with `tasks/index.yaml` and one `T-<id>-<slug>.md`
   contract per task, using the [task template](../write-plan/templates/task.md) and index template under
   `write-plan/templates/`. Keep ownership explicit and
   dependencies acyclic. Tasks touching shared files or unresolved contracts stay sequential.
5. Apply the execution-detail checks below. Check that every plan acceptance item maps to a task and
   every concrete change maps to an acceptance scenario and verification path. Keep index and task
   ownership, dependencies, and `parallel_safe` consistent.
   Return `Task decomposition: clear|issues` and the task package path.

## Execution-detail checks

Write for an executor who did not participate in planning and may use a different model. The task and
its explicitly referenced material must supply the settled decisions without relying on conversation
history. Use the template's per-change section to name the actual file/symbol, verified current behavior,
target behavior, required integration, and behavior that must remain unchanged. Mark new paths as new;
do not invent source facts to fill the template. Record the source basis and the smallest required reads.

Reject title-only actions such as "implement the service" or "add permission checks" even when all
headings are filled. For a permission-check task, for example, identify the handler and existing policy
API, actor/resource inputs, placement before writes, denied/error outcomes, preserved success behavior,
and corresponding assertions from the confirmed design. If that design leaves the policy undecided,
return the missing decision instead of choosing it while decomposing tasks.

Before returning `clear`, check whether an unfamiliar executor can identify the first edit/check,
allowed and excluded edits, fixed decisions, local implementation freedom, dependency readiness,
positive and preservation assertions, and conditions for returning to the planner. Missing facts or
decisions that affect execution yield `issues`; report the affected task IDs and missing decisions in
the decomposition result and do not generate or freeze those contracts until the gaps are resolved.
Do not present a partial package as ready for Design Gate or dispatch. Unresolved contracts cannot become
executable merely by scheduling their tasks sequentially. Detail should remove design guessing, not prescribe every line
or create more tasks merely to make them smaller.

## Boundary

This Skill only freezes execution task contracts. It does not implement behavior, approve design,
run Design Gate, dispatch workers, or decide completion. A task package is a prerequisite for Design
Gate and development after `write-plan`.
