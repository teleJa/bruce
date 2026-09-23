# Implementation plan: <change name>

## Behavior delta

| Scenario | Before | After |
|---|---|---|
| <user/system scenario> | <current behavior> | <new or changed behavior> |

List every observable behavior added, removed, or changed by this plan. If no behavior changes, state
"No behavior change" and remove the table.

## Inferred assumptions

1. <assumption inherited from existing code or existing flow that the AI resolved without explicit
   user instruction; even if it seems reasonable, list it here so the user can confirm or reject it>
   - Confirmation: <user message/date or "Pending user confirmation">

If there are no inferred assumptions, state "None" and remove this section. Every assumption must
have a user-confirmation reference. Any `Pending user confirmation` or otherwise unconfirmed
assumption blocks document review and is not an effective plan constraint.

## Task contract

- Objective: <observable result>
- Scope: <included and excluded changes>
- Acceptance: <scenario ids with Given/When/Then and exact Evidence paths>
- Constraints: <repository/user/risk constraints>
- Topology: <standard or full, with evidence>
- Risk: <low, guarded, or critical, with trigger>

## Confirmed design basis

- <authoritative design path/section or confirmed task decision> — <constraint this implementation must preserve>

Reference the relevant decision, not the full architecture. If there is no separate design document,
use the confirmed task decisions; do not create architecture solely to fill this section.

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

## Task implementation details

Without a task package, repeat the following for each task. With a package, put these details in the
frozen task files and reference them from the summary; do not duplicate the task contracts here.

### T-001 — <observable task-local deliverable>

- Existing integration point: <actual path/symbol and current responsibility>
- Changes and outputs: <concrete implementation work and consumed/produced interfaces; label new paths as new>
- Prerequisites and order: <predecessor output, shared-file ownership, and execution preconditions>
- Fixed constraints / executor choices: <design constraints to preserve and local choices left to the developer>
- Verification: <acceptance id, known command/check, environment/precondition, and expected observable result>

Add migration, old/new compatibility, cutover, and recovery steps only when applicable. Keep unrelated
fields out; do not leave material business or architecture decisions for the executor to invent.

## Repository evidence

- <path/API/command> — <fact the plan depends on>

## Dependency and risk notes

- <critical path, shared files/contracts, guarded/critical action and recovery>

## Whole-change verification

- <acceptance/scenario id> -> <Given/When/Then> -> <task id> -> <required layer> -> <command/check, prerequisites, and expected observable evidence>

Planned checks are not executed results. Cite existing evidence only for what it actually proves.

## Delivery boundary

- <workspace only, commit, PR, deployment, or another explicitly authorized action>
