# Shared verification Scenario v1 schema

A shared scenario describes one user-observable business outcome and is the coordination anchor for
API/UI verification tracks. It is requirement-scoped test design, not an Environment Profile, runtime
result, model routing file, or Completion verdict.

## Canonical shape

The values below are **non-executable placeholders**. Replace route, target, namespace, and evidence
paths only with repository-backed values before use.

```yaml
version: 1
scenario_id: CONTENT-CREATION-001
scenario_version: 1
feature_area: content-creation
business_flow: select-topic -> generate-artifact -> reload-recovery
actor: regular-user
visual_scope: browser-smoke
execution:
  environment_profile: project-local
  api_mode: real-http
  ui_mode: browser-provider
data:
  api_namespace: "<unique-api-namespace>"
  ui_namespace: "<unique-ui-namespace>"
  ownership: test-run
  cleanup: "<declared-safe-cleanup-strategy>"
preconditions: [<declared-backend-health>, <declared-frontend-ready>, <declared-worker-ready>]
api:
  steps:
    - id: create-job
      action: request
      request: {method: POST, path: "<evidence-backed-submit-route>"}
    - id: wait-job
      action: poll
      request: {method: GET, path: "<evidence-backed-status-route>/{job_id}"}
      until:
        terminal_statuses: [succeeded, failed, canceled]
        success_statuses: [succeeded]
        timeout_seconds: 180
        interval_seconds: 2
  assertions: [job-reaches-succeeded]
  persistence:
    required: true
    readback: [artifact-readable-through-public-api]
ui:
  steps:
    - {id: open-page, action: open, target: "<evidence-backed-page-target>"}
    - {id: submit, action: click, target: "<evidence-backed-submit-control>"}
    - {id: observe-result, action: observe, target: "<evidence-backed-result>"}
  assertions: [artifact-visible-after-reload]
  forbidden_shortcuts: [submit-via-api]
failure_cases: [worker-failure, cross-user-access]
evidence:
  required: [redacted-request-summary, state-trace, visible-state, screenshot]
  directory: "<project-relative-evidence-directory>"
status: designed
```

## Identity and version

- `scenario_id` is stable for one user-facing business outcome.
- `scenario_version` is a positive integer. Any material actor, flow, step, assertion, dependency,
  mode, data, or evidence change creates a new version.
- API and UI results may be aggregated only when both fields match exactly.

## Execution and data

- `api_mode` is `memory-application`, `real-http`, `live-acceptance`, or `null`.
- `ui_mode` is `browser-provider` or `null`.
- A UI-enabled Scenario must explicitly declare `visual_scope=browser-smoke|browser-layout`;
  `none` is valid only when no material rendered outcome is being verified.
- At least one track is enabled.
- Enabled mutable tracks require non-empty, safe lowercase namespaces. API and UI namespaces must be
  distinct.
- `ownership` is `test-run`, `dedicated-test-database`, or `read-only-existing-data`.
- `cleanup` states the declared safe strategy. Destructive reset/drop is not implied.

## Track separation

API step actions are limited to `request`, `poll`, `assert`, and `cleanup`. Browser/page actions such
as `open`, `click`, `input`, `upload`, `select`, `drag`, `refresh`, and `navigate` are invalid in the
API track.

UI step actions are limited to `open`, `observe`, `click`, `input`, `upload`, `select`, `drag`,
`refresh`, `navigate`, `confirm`, and `assert`. A UI step must not contain an HTTP `request`; APIs may
be declared only as setup, cleanup, or authoritative readback outside the page action list.

## Status and evidence

Scenario status is exactly one of `designed`, `executed`, `passed`, `failed`, or `blocked`. The scenario
file normally remains `designed`; current run status belongs in a Track Result and Verification
Run/Checkpoint. Secret values, credential-bearing URLs or query parameters, raw authorization headers,
cookies, passwords, tokens, API keys, and database URLs are forbidden.
