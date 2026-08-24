# Task <task-id>: <title>

- Contract revision: 1
- Contract state: frozen before execution
- Status source: `../checkpoint.yaml`
- Parent plan: `../plan.md`

## Objective

<observable task-local result>

## Included scope

- <repository path, component, or direct call site>

## Excluded scope

- <path, component, contract, or action that this task must not change>

## Dependencies

- Depends on: <task ids or none>
- Consumes: <interfaces, artifacts, or none>
- Produces: <interfaces, artifacts, or none>

## Acceptance

- Parent scenario ids: <stable acceptance ids>
- Given: <starting state>
- When: <task action or change>
- Then: <observable task-local result>
- Evidence: <required evidence ids, paths, or commands>

## Verification

- Required layer: <unit|integration|API|database|build|real-use|Chrome>
- Commands/checks: <concrete checks>
- Environment: <required runtime/database/browser environment or none>

## Authorization and risks

- Authorization: <normal|explicit capability|user confirmation>
- Risk trigger: <low|guarded|critical and reason>
- Stop condition: <when to return the task checkpoint>

## Contract change rule

Do not silently widen this task. If scope, acceptance, dependency, authorization, or required
verification changes, create a new contract revision or a superseding task and record the reason in
the next checkpoint.
