# Implementation plan: <change name>

## Task contract

- Objective: <observable result>
- Scope: <included and excluded areas>
- Acceptance: <scenario ids with Given/When/Then and exact Evidence paths>
- Constraints: <repository/user/risk constraints>
- Topology: <standard or full, with evidence>
- Risk: <low, guarded, or critical, with trigger>

## Repository evidence

- <path/API/command> — <fact the plan depends on>

## Tasks

### <task-id>

- Title: <action>
- Component: <real component, when useful>
- Depends on: <task ids or contract anchors; empty when none>
- Parallel safe: <true only with evidence>
- Files/scope: <real paths and ownership boundary>
- Consumes: <interfaces or none>
- Produces: <interfaces/files or none>
- Detail: <self-contained implementation instructions>
- Acceptance: <parent scenario ids and task-local observable result>
- Verification: <required layer and real command/API/database/Chrome-visible check>

## Dependency and risk notes

- <critical path, shared files/contracts, guarded/critical action and recovery>

## Whole-change verification

- <acceptance/scenario id> -> <Given/When/Then> -> <required layer> -> <current reproducible evidence>

## Delivery boundary

- <workspace only, commit, PR, deployment, or another explicitly authorized action>
