# Implementation plan: <change name>

## Task contract

- Objective: <observable result>
- Scope: <included and excluded changes>
- Acceptance: <scenario ids with Given/When/Then and exact Evidence paths>
- Constraints: <repository/user/risk constraints>
- Topology: <standard or full, with evidence>
- Risk: <low, guarded, or critical, with trigger>

## Task package

Remove this entire optional section when a separate frozen task package is not needed.

- Path: `tasks/`
- Index: `tasks/index.yaml`
- Contract state: task files are frozen before their task starts
- Status source: `checkpoint.yaml` or the current checkpoint message
- Execution mode: `sequential`

## Task summary

| Task ID | Title | Depends on | Acceptance IDs | Allowed paths | Verification layer |
|---|---|---|---|---|---|
| T-001 | <short title> | <task ids or none> | <ids> | <paths> | <layer/check> |

Without a task package, record executable steps and acceptance directly in this plan. When a package
exists, detailed frozen contracts live in `tasks/T-<id>-<short-slug>.md`; reference them rather than
duplicating their scope. Change a frozen contract only through an explicit revision or superseding task.

## Repository evidence

- <path/API/command> — <fact the plan depends on>

## Dependency and risk notes

- <critical path, shared files/contracts, guarded/critical action and recovery>

## Whole-change verification

- <acceptance/scenario id> -> <Given/When/Then> -> <task id> -> <required layer> -> <current reproducible evidence>

## Delivery boundary

- <workspace only, commit, PR, deployment, or another explicitly authorized action>
