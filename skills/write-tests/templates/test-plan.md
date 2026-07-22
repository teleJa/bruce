# Test plan: <change name>

## Acceptance mapping

| Acceptance | Scenario | Verification layer | Evidence |
|---|---|---|---|
| <acceptance id> | <scenario id> | <unit/component/integration/API/database/Chrome> | <command or current observation> |

## Preconditions and real dependencies

- <service, database, credentials, fixture, browser session, or none>

## State and intent matrix

| Pre-state | User/system intent | Expected behavior | Data consequence |
|---|---|---|---|
| <state> | <action> | <result> | <write/history/current-pointer effect> |

## Scenarios

### <scenario-id>: <name>

- Maps to: <acceptance and optional task id>
- Type: <happy/edge/error/integration/permission/regression>
- Given: <concrete user/system state, data, permissions, and real dependencies>
- When: <user or system action>
- Then: <observable behavior and data/state consequence>
- Evidence: <exact command, API/database check, or Chrome-visible observation for each material Then>
- Required layer: <unit/component/integration/API/database/Chrome>

## Regression sources

- <bug or previous coverage gap> -> <scenario id>

## Limits

- <what fixtures or mocks do not prove and what real check remains>

## Self-check

- Every acceptance item maps to evidence.
- Every behavior scenario has concrete Given/When/Then and each material Then has a feasible evidence path.
- Stateful behavior covers repeat use, failure, and recovery where relevant.
- Commands and environments exist in the target repository.
- User-visible Web acceptance uses real Chrome evidence unless an explicit SOP requires Playwright.
