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
   contract per task, using the templates under `write-plan/templates/`. Keep ownership explicit and
   dependencies acyclic. Tasks touching shared files or unresolved contracts stay sequential.
5. Check that every plan acceptance item maps to a task and every task maps to a verification path.
   Return `Task decomposition: clear|issues` and the task package path.

## Boundary

This Skill only freezes execution task contracts. It does not implement behavior, approve design,
run Design Gate, dispatch workers, or decide completion. A task package is a prerequisite for Design
Gate and development after `write-plan`.
