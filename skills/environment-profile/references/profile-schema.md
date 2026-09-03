# Environment Profile schema

This schema defines a reusable **Agent test and verification environment contract**. It records
what an Agent may use and do for the confirmed test scope. It is not a test result, deployment
record, runtime checkpoint, or Completion verdict.

## Purpose and confirmation

The Profile exists to give an Agent one confirmed execution context for building, deploying or
starting the target, preparing isolated test data, authenticating, running tests, and collecting
read-only evidence. Confirmation is also the authorization boundary for the declared test scope:
the Agent must not ask the user again for each operation inside that scope.

The Profile is usable only when:

```text
profile_state == confirmed
confirmation.state == confirmed
confirmation.confirmed_revision == profile_revision
confirmation.confirmed_content_hash == content_hash
```

A material change to the test context, operation set, endpoints, dependencies, credentials,
account policy, or security rules increments `profile_revision`, recalculates `content_hash`, and
resets confirmation to `pending`.

```yaml
version: 1
profile_kind: environment
profile_id: local-dev
profile_revision: 1
content_hash: sha256:pending
profile_state: draft
confirmation:
  state: pending
  confirmed_by: null
  confirmed_at: null
  confirmed_revision: null
  confirmed_content_hash: null
```

## Identity and declaration

```yaml
declaration:
  source: user
  statement: 用户确认的 Agent 测试环境
  provided_at: 2026-09-02T00:00:00+08:00
project:
  name: project-name
  root: /absolute/project/path
environment:
  name: local-dev
  kind: local
  production: false
  shared: false
  purpose: local-development-and-integration-testing
```

Repository inspection produces candidates only. Accepted information is written into the compact
`test_context`; do not copy the same candidate into a generic `facts` inventory. An optional
`facts` list is allowed only for user-confirmed residual information with no structured home.
Never store repository paths, source revisions, branch names, implementation inventories, or
runtime results as environment facts.

## Compact Agent test context

`test_context` is the canonical home for all information needed by Agent testing and verification.
It intentionally groups setup, access, data, authentication, configuration, services, and
preflight instead of spreading them across many top-level sections.

```yaml
test_context:
  scope: local-development-and-integration-testing
  authorization:
    mode: profile-confirmed
    approved_scopes:
      - build
      - deploy-local
      - test-data-prepare
      - authenticate-local
      - test
      - read-only-inspection
    escalation_required_for:
      - production-access
      - remote-deployment
      - database-drop
      - destructive-data-reset
      - credential-rotation
  workflow:
    build_operation: build-application
    deploy_operation: start-services
    test_data:
      prepare_operation: prepare-test-data
      cleanup_operation: cleanup-test-data
      isolation: dedicated-test-database-or-fixture
      strategy: project-approved-test-fixtures
    authenticate_operation: null
    test_operation: test-application
  services:
    application: []
    dependencies: []
    endpoints: []
  data:
    allowed_mutations: []
    prohibited_mutations: [database-drop, direct-sql]
  authentication:
    account_pool: local-test-accounts
    credential_refs: []
    method: user-managed-local-auth
  configuration:
    env_file:
      path: .env
      required: true
      required_variables: []
      file_mode: "0600"
      ignored_by_vcs: required
    references: {}
  preflight: []
```

### Authorization

`test_context.authorization.mode: profile-confirmed` means one exact user confirmation authorizes
all operations whose `authorization` is `profile-confirmed` and whose category or operation ID is
listed in `approved_scopes`. This prevents repeated privilege prompts during one test run while
keeping the scope explicit.

Use `explicit-per-invocation` for destructive, production, remote, credential-rotation, or other
operations outside the approved test scope. Critical categories must always use
`explicit-per-invocation`. `none` is only for genuinely read-only operations.

### Workflow

The workflow identifies the normal Agent sequence through operation IDs:

```text
build -> deploy/start -> prepare test data -> preflight -> authenticate -> test -> evidence
```

Any missing operation needed by the requested verification must be represented as an unresolved
user decision, not invented at execution time. Cleanup may be omitted when the environment is
explicitly disposable, but the data isolation policy must remain stated.

### Services, data, authentication, and configuration

- `services` is the single place for application services, dependencies, and endpoints.
- `data` is the single place for test-data isolation and allowed/prohibited data mutations.
- `authentication` is the single place for account-pool and credential references. It never stores
  passwords, API keys, cookies, JWTs, tickets, or credential-bearing URLs.
- `configuration.env_file` is the single place for `.env` metadata and required variable names.
  `configuration.references` is only for safe non-secret references outside `.env`.
- `preflight` contains checks to run before the workflow; it contains no current results.

## Operations

`operations` is the one executable operation catalog. Each entry contains the exact `argv`, risk,
authorization mode, ownership, and evidence requirements. Do not duplicate command details in
`test_context.workflow` or another manifest; workflow fields contain IDs only.

```yaml
operations:
  - operation_id: build-application
    category: build
    purpose: build-project
    executor: local-process
    working_directory_ref: project-root
    argv: [make, build]
    authorization: profile-confirmed
    risk: guarded
    mutates: build-artifacts
    ownership: developer
    target: local-machine
    required_evidence: [command-exit-status, artifact-observation]
```

The generated `$environment-operations` Skill may execute declared operations. Generation itself
does not execute them. A profile-confirmed routine operation does not require another user prompt;
its bounded runner still fails closed on stale hashes, undeclared commands, unsafe paths, missing
`.env` values, and operations outside the approved scopes.

## Static and dynamic boundaries

The static Profile may contain declarations, safe references, authorization scope, and expected
evidence. It must not contain:

- actual source or deployed revision;
- current service, database, provider, or account availability;
- build IDs, artifact results, screenshots, logs, or user responses;
- selected account instances for one run;
- stage status, repair rounds, runtime evidence, or Completion verdict.

Those belong in Verification Run/Checkpoint or the requirement-scoped Verification Profile.

## Local `.env` and security

A missing local `.env` may be bootstrapped with empty values only. It must be a regular, ignored,
untracked, owner-only `0600` file. The Profile stores names and safe references, never values.
A metadata check proves only local configuration presence; it does not prove authentication or
service availability.

Every Profile must retain:

```yaml
security:
  persist_secrets: false
  expose_secrets_to_model: false
  redact_logs: true
  credential_values_allowed: false
  credential_refs_only: true
```

## Freshness and blocking

Freshness rules must cover changes to the declaration, scope, authorization policy, workflow,
endpoints, dependencies, account or credential references, `.env` variable scope, security, and
operation set. Runtime blocking and resume state belong to Verification Run/Checkpoint; the static
Profile only declares stop conditions and required user decisions.

Do not emit `operation_manifest` or a persisted `confirmation_summary`. Generate the confirmation
summary for display from the canonical Profile. Do not add a separate capabilities catalog unless
it represents a distinct capability not already represented by `test_context` and `operations`.
