# API mode contract

This Skill consumes the shared Scenario v1 `execution.api_mode` and repeats the same value as the
API Track Result `execution_mode`. The value is a declared evidence boundary, not an implementation
preference.

## Mode matrix

| API mode | Execution boundary | Evidence it can claim | Required stop rule |
| --- | --- | --- | --- |
| `memory-application` | Existing in-process application/test harness and its declared fixtures | Application behavior that the harness actually exercises; no network or deployment claim | Missing harness, fixture, or expected state is `blocked`; never relabel as HTTP |
| `real-http` | Actual HTTP request path through the project's existing test convention and confirmed target | HTTP integration behavior for the declared target, including the discovered route and auth boundary | Missing route, command, target, or auth preflight is `blocked`; never relabel as in-process |
| `live-acceptance` | Confirmed live/deployed API operation, required worker, account, and Environment Profile authorization | Current runtime API behavior plus required terminal-state and authoritative readback evidence | Missing authorization, runtime identity, account, worker, cleanup, or readback is `blocked`/`waiting_user` |

## Rules

- Select the mode from the frozen Scenario; do not infer it from tool availability or downgrade a
  failed live operation to a local test.
- `memory-application` must not claim middleware, network, proxy, deployed revision, or live
  service behavior.
- `real-http` must use an exact project-evidenced method/path and an actual declared test command;
  do not invent an endpoint or command.
- `live-acceptance` requires a confirmed Environment operation and non-destructive preflight. It
  does not grant production access, destructive setup, credential rotation, or browser access.
- All modes share request ordering, variable lineage, negative/permission/idempotency assertions,
  bounded polling, and authoritative persistence rules when the Scenario requires them.
- Evidence labels, Track Result mode, and status must remain consistent. A mode mismatch is not a
  passing result.
