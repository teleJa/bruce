---
name: api-test-orchestration
description: Orchestrate project-grounded API verification with bounded state, evidence, and persistence checks.
---

# API Test Orchestration

`api-test-orchestration` is a project-independent supporting Skill. It turns one confirmed,
requirement-scoped business flow into an API verification track that can be generated, executed,
and reported without inventing a project runtime. It consumes the shared Scenario v1 and Track
Result v1 contracts; it is not a replacement for either contract.

The Skill is deliberately an orchestration guide, not an HTTP client, database client, test DSL,
or project adapter. Project-specific route names, commands, fixtures, credentials, terminal states,
and persistence queries must come from repository evidence and a confirmed Environment Profile.

## When to use

Use this Skill when a requirement needs an API track for one or more of these purposes:

- exercise a synchronous or asynchronous business flow through a project's existing API test
  convention;
- connect request outputs to later requests and assertions;
- verify Job state transitions with a bounded poll;
- cover negative, permission, duplicate, retry, or idempotency behavior;
- prove a persisted outcome with an authoritative readback; or
- produce a redacted API Track Result for Test Dispatch and Verification Run/Checkpoint.

Use it only after the requirement's Scenario v1 identity and API mode are declared. A missing,
ambiguous, or stale mode is a blocking input problem, not a reason to select a convenient mode.

## Hard boundaries

1. **Do not guess project behavior.** Discover the exact route, method, request shape, response
   fields, auth requirement, test command, fixture, Job state, and readback path from the current
   repository, project documents, and confirmed Environment Profile. A placeholder in a design
   is not an executable endpoint or command.
2. **Do not silently downgrade a mode.** `memory-application`, `real-http`, and `live-acceptance`
   have different evidence claims. If the declared mode is unavailable, return `blocked` or
   `waiting_user` with the missing capability; do not substitute another mode and do not report
   `passed`.
3. **Do not create a generic HTTP runtime.** Reuse the project's existing test convention and
   confirmed Environment operation. Do not add a general-purpose HTTP client, database client,
   orchestration engine, or private test DSL under this Skill.
4. **Do not operate a browser.** API steps are limited to `request`, `poll`, `assert`, and
   `cleanup`. Browser actions, page locators, screenshots of UI state, and browser-provider
   access belong to the UI track and the host/main Agent. An API Track Result must keep
   `browser_actions` empty.
5. **Do not modify business code.** Generated or maintained artifacts must stay inside the task's
   declared test/evidence paths. Never change application routes, services, repositories, Job
   workers, schemas, migrations, CI, shared contracts, or Environment Profile templates to make a
   scenario pass.
6. **Do not expose secrets.** Use credential references and account aliases only. Never persist or
   print passwords, tokens, cookies, raw authorization headers, API keys, database URLs, or secret
   response values.
7. **Do not own model routing.** Agent delegation, model resolution, and fallback belong to the
   Bruce Functional Agent Profile/resolver. This Skill does not add a private model router or a
   per-Skill model selector.

## Shared contract inputs

The API track must remain traceable to the exact shared scenario version and result contract:

- [Scenario v1](../test-dispatch/references/scenario-schema.md) defines the stable scenario
  identity, declared `api_mode`, data namespace, API-only step actions, persistence requirement,
  failure cases, evidence, and scenario status.
- [Track Result v1](../test-dispatch/references/track-result-schema.md) defines the API result's
  repeated `scenario_id`/`scenario_version`, `execution_mode`, namespace, allowed paths, evidence,
  commands, empty `browser_actions`, assertions, blockers, and unverified gates.
- [Evidence and status](../test-dispatch/references/evidence-status.md) defines
  `designed`, `executed`, `passed`, `failed`, and `blocked`; a response status, created Job, or
  generated test alone is never enough for `passed`.
- [API mode contract](references/api-modes.md) defines the three mode boundaries and evidence
  claims.
- [Discovery boundaries](references/discovery-boundaries.md) defines what route, service,
  repository, Job, and persistence inspection may establish.
- [Evidence contract](references/evidence-contract.md) defines variable lineage, bounded polling,
  negative/permission/idempotency assertions, authoritative readback, and redaction.

Do not extend Scenario v1 with new runtime fields. Dynamic run identity, actual account binding,
source/build/deployment identity, polling observations, and evidence revisions belong in the
Track Result and Verification Run/Checkpoint.

## Three API modes

Select exactly the mode declared by the Scenario and preserve it in the Track Result's
`execution_mode`.

### `memory-application`

- Calls the existing in-process application/test harness selected by repository evidence.
- Does not claim a network hop, deployed route, middleware, proxy, or live service behavior.
- May use in-memory fixtures only when the project's test convention defines them.
- Must still exercise the declared service behavior, variable flow, assertions, and persistence
  contract that the fixture can actually prove.
- Evidence must be labeled `memory-application`; it must never be aggregated as `real-http` or
  `live-acceptance` evidence.

### `real-http`

- Sends actual HTTP requests through the project's declared API test convention to the confirmed
  Environment Profile target.
- Uses only the route, method, auth mechanism, test command, and fixture established by project
  evidence.
- Captures request/response summaries and authoritative state evidence without retaining secret
  headers or bodies.
- Proves an HTTP integration path, but does not by itself prove live user/browser acceptance.

### `live-acceptance`

- Exercises the deployed or otherwise live API and any required worker through a confirmed
  Environment operation, preflight, account binding, and authorization scope.
- Requires current runtime identity and health evidence, safe test-run namespace, and a declared
  cleanup or read-only policy.
- Requires the same business assertions and authoritative readback as the requirement demands;
  “live” is not a synonym for “passed”.
- If the operation, account, worker, or readback is unavailable, stop with `blocked` or
  `waiting_user`. Do not fall back to `real-http` or `memory-application`.

Mode selection is an explicit contract, not an inference from which tool happens to be available.
A mode mismatch is a failed contract input and must be visible in the result.

## Discovery boundary: route -> service -> repository -> Job -> persistence

Inspect this chain read-only before writing an API scenario or project test. Record the source file,
document, symbol, or existing test convention that supports each claim. Do not treat a guessed path,
framework default, or response example as evidence.

| Boundary | It may establish | It must not establish by itself |
| --- | --- | --- |
| **Route/controller/router** | public method/path, request decoding, response envelope, auth middleware, status mapping, and route-level validation | that the business outcome was persisted, that a Job completed, or that any 2xx is success |
| **Service/use-case** | business transition, validation, actor checks, duplicate/idempotency semantics, sync vs async handoff, and returned identifiers | the external URL, deployed revision, or database durability without a lower-level/authoritative source |
| **Repository/data access** | fields written/read, ownership relation, transaction boundary, uniqueness or idempotency constraint, and data needed for a readback | permission success, public API availability, or a safe mutation permission; do not mutate data for discovery |
| **Job/worker** | Job creation handoff, observable status field, progress/failure mapping, retry behavior, and evidence-backed terminal states | that Job creation is completion, that an unlisted status is terminal, or that a worker is healthy without runtime evidence |
| **Persistence authority** | the public API readback or an explicitly approved read-only database query that proves the required durable outcome | an inferred table/column, a stale in-memory object, a response snapshot, or a direct database write/reset |

Use the narrowest sufficient source at each boundary. If the route says only “accepted” and the
Job/service evidence says work is asynchronous, the scenario must include a bounded poll and a
post-terminal readback. If no authoritative source can prove the required persistence, keep the
scenario incomplete or blocked rather than weakening the assertion.

### Discovery stop conditions

Stop and report a blocker when any of these facts cannot be sourced:

- the exact route/method or project test convention;
- the declared API mode or confirmed operation for that mode;
- the variable needed by a later request;
- the Job status field and a finite terminal allowlist;
- the actor/account and permission state needed for a negative or permission case; or
- the authoritative readback for a required persistent outcome.

Do not fill the gap with a framework default, a neighboring endpoint, a guessed command, or a
manually edited business record.

## Scenario construction and variable flow

Build only the API portion of the shared Scenario:

- Use API actions `request`, `poll`, `assert`, and `cleanup`; never put `open`, `click`, `input`,
  `refresh`, `navigate`, or another browser/page action in `api.steps`.
- Keep request order explicit. A later request may consume only a value produced by an earlier
  response or declared fixture/precondition.
- Preserve a **variable lineage** table in the generated test design or evidence summary. This is
  documentation/evidence, not a new shared schema or test DSL:

  | variable | producer step/source | consumer step/assertion | sensitivity | handling |
  | --- | --- | --- | --- | --- |
  | resource/job identifier | discovered response field or fixture | status poll/readback | non-secret | pass by named reference |
  | namespace | confirmed test-run allocation | every mutable request | non-secret | keep isolated and record |
  | credential/account handle | confirmed Profile reference | auth setup | sensitive reference | use alias/handle; never persist value |

- Use exact response selectors and names from repository evidence. Fail closed when a selector is
  absent, duplicated, type-invalid, or owned by a different actor.
- Keep API and UI namespaces non-empty and distinct whenever both tracks are enabled. Never copy
  UI-only values into an API assertion or use a browser action as variable extraction.
- A secret-derived variable may be used transiently by the existing project harness, but its value
  must not enter a scenario, command line, result, log, screenshot, checkpoint, or evidence file.
- If a request is retried, state whether the same request identity/idempotency input is reused or a
  new request is intentionally created. Record the expected side effect before execution.

## Request, Job, and bounded polling rules

For each request, bind method, path, input, actor, expected response, and produced variables to
repository evidence. For an asynchronous flow:

1. Issue the discovered create/submit request.
2. Capture only the named identifier(s) required by the next step.
3. Poll the discovered status/read route using a Scenario `poll` step.
4. Stop only on the finite `terminal_statuses` allowlist or the declared positive timeout.
5. Treat only `success_statuses` (a subset of `terminal_statuses`) as success.
6. Perform required assertions and the authoritative persistence readback after a successful
   terminal state.

Every poll must declare positive `timeout_seconds` and `interval_seconds`; the resulting number of
attempts is bounded by that deadline. No unbounded loop, indefinite sleep, open-ended retry, or
“poll until it looks done” behavior is allowed. Use the exact field and statuses supported by the
project; do not invent `completed`, `done`, `ready`, or any other terminal state.

The following are never sufficient for a passed API track by themselves:

- an HTTP 2xx or accepted response;
- a created Job identifier;
- one successful poll that omits the terminal allowlist;
- an in-memory object or response snapshot when persistence is required; or
- a script that was generated but not actually invoked.

An unknown, malformed, or newly observed status is fail-closed: record the observation, stop the
poll safely, and classify the result as `failed` or `blocked` according to whether the required
assertion was reached and failed or an environment/control prerequisite prevented continuation.

## Negative, permission, idempotency, and recovery coverage

Add these cases only when the route/service contract or requirement makes them applicable, and
state the source of each expected result. Every case needs an expected status/result and a state
invariant; “any non-2xx” or “any 2xx” is not an assertion.

- **Negative validation:** malformed, missing, out-of-range, or unsupported input must produce the
  documented error shape/status and no unintended durable side effect.
- **Permission and ownership:** use the declared actor/account states. Verify the denied response,
  resource visibility boundary, and no unauthorized mutation. Do not use an administrator to prove
  a regular user's access or infer absence from a hidden response.
- **Duplicate/idempotency:** repeat the exact documented request or idempotency input through the
  existing convention. Assert the documented single-result, conflict, or replay behavior and verify
  the persisted identity/count through the authoritative source.
- **Retry/concurrency:** if retries or competing actors are in scope, assert the documented winner,
  conflict, or deduplication result and the post-conflict invariant. Do not accept whichever request
  happens to return first.
- **Failure/recovery:** exercise a documented failure only when the Environment Profile authorizes
  the setup. Do not damage shared or production data to manufacture a worker failure; otherwise
  classify the case as unavailable/blocked and preserve the stop reason.

## Authoritative persistence readback

When `api.persistence.required` is `true`, the Scenario must name at least one readback assertion.
Prefer a public API readback that is available to the same authorized actor and can prove the
business outcome after the terminal state. A read-only database query is acceptable only when the
confirmed Environment Profile explicitly authorizes that operation and the repository evidence
identifies its source; it is never a license to add a database client or perform a write.

A readback must check the required durable facts, such as stable resource identity, owner/actor,
relationship, status, or content invariants. It must not merely repeat the create response or an
in-memory object. If the authoritative readback is stale, unauthorized, unavailable, or ambiguous,
leave the API track `executed`, `failed`, or `blocked` as appropriate; never convert the gap to
`passed`.

## Evidence and redaction

Return evidence that another Agent can trace to the Scenario and current mode without learning a
secret. A useful API evidence bundle contains:

- exact `scenario_id`, `scenario_version`, `execution_mode`, and data namespace;
- repository evidence references for route, service, repository, Job, and persistence claims;
- redacted request/response summaries: method, route template, status, safe field names, and
  correlation identifiers after redaction;
- variable lineage and state-transition trace, including the bounded poll deadline and observed
  terminal status;
- negative/permission/idempotency assertions and their post-condition/readback;
- actual project command/test invocation, only if one was declared by project evidence;
- authoritative readback evidence and its actor/permission context;
- `browser_actions: []`, `modified_paths: []` when no test/evidence artifact was changed, and
  blockers/unverified gates when evidence is incomplete.

Redaction is applied before writing or printing evidence. Remove raw authorization headers,
cookies, passwords, tokens, API keys, database URLs, credential-bearing query parameters, and
secret response fields. Replace them with a stable reference such as a credential ID or account
alias, not the value. Do not put secrets in a command argument, fixture, source file, checkpoint,
Handoff, test output, or final response.

## Execution procedure

1. Read the exact requirement and Scenario v1; verify matching `scenario_id` and positive
   `scenario_version`.
2. Confirm `execution.api_mode`, namespace ownership, preconditions, failure cases, persistence,
   and required evidence. Keep the API/UI mode boundary explicit.
3. Read the confirmed Environment Profile and select only the declared operation, account/credential
   reference, test convention, and safe data policy. For `real-http` and `live-acceptance`, run
   only the non-destructive preflight required by that Profile.
4. Discover and record the route -> service -> repository -> Job -> persistence chain. Stop on
   missing or conflicting evidence.
5. Design the ordered API steps, variable lineage, bounded poll, assertions, cleanup/read-only
   policy, and negative/permission/idempotency cases. Do not add fields outside Scenario v1.
6. Reuse the project's existing test convention. If the needed command, fixture, endpoint, or
   adapter is not declared, return a blocker instead of creating a generic runtime or guessing.
7. Execute the declared mode only. Keep actual account binding, source/runtime identity, poll
   observations, and evidence revision in the Track Result/Verification Run, not the static
   Scenario or Environment Profile.
8. Redact evidence, record typed `evidence_records` and current Profile/basis/evidence revisions,
   perform the authoritative readback, and validate the Track Result. A passed API track requires
   evidence, assertions, no blockers/unverified gates, an actual command/test invocation, and all
   required persistence assertions.
9. Report `designed`, `executed`, `passed`, `failed`, or `blocked` using the shared evidence rules.
   If a user or external operation is needed, use the explicit waiting/blocking path and do not
   silently continue in another mode.

## Output

Produce a compact, traceable API verification packet containing:

1. Scenario identity/version, selected API mode, environment/profile operation reference, actor,
   namespace, and preconditions.
2. A discovery table for route, service, repository, Job, and persistence authority with source
   references and unresolved facts.
3. Ordered API steps with request/response variable lineage and the exact bounded polling contract.
4. Happy-path, negative, permission, duplicate/idempotency, concurrency/retry, and recovery cases
   marked applicable or not applicable with reasons.
5. Test-convention mapping: the existing project test file/harness and exact declared command, or a
   blocker if either is not known. Do not invent a command or endpoint.
6. Redacted evidence plan/result, authoritative readback, cleanup policy, and Track Result v1
   fields. Make `browser_actions` empty and list any modified paths explicitly.
7. Blockers, unverified gates, mode mismatch, stale profile, or required user action. Never return
   a false `passed` result.

## Does not own

- browser or page interaction, browser-provider selection, UI assertions, or screenshots of visible
  state;
- application route/controller, service/use-case, repository, Job/worker, or business-code
  implementation;
- shared Scenario/Track Result schema, migrations, database writes, or generic HTTP/database
  runtime;
- project endpoint discovery by guesswork, project command selection by convention alone, fixture
  creation outside the confirmed scope, or production/remote authorization;
- credential storage, account provisioning, secret values, model selection, model routing, or
  Completion/Design Gate decisions.
