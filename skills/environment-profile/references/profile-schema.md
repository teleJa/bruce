# Environment Profile schema

This schema describes a reusable, static environment contract. It is not a Verification Run,
Checkpoint, deployment record, test result, or completion verdict.

## Lifecycle

Every generated profile starts unconfirmed:

```yaml
profile_state: draft
confirmation:
  state: pending
```

The allowed lifecycle is:

```text
draft -> needs_input -> ready_for_confirmation -> confirmed -> stale
                                      |                 |
                                      v                 v
                                   rejected          superseded
```

`ready_for_confirmation` means the profile has enough information for a user review. It does not
mean that the profile may be consumed. Controlled Bruce verification requires all of:

```text
profile_state == confirmed
confirmation.state == confirmed
confirmation.confirmed_revision == profile_revision
confirmation.confirmed_content_hash == content_hash
```

A material change to facts, source references, environment identity, build/deployment target,
account policy, credential source, Skill selection, preflight, security policy, or freshness rules
increments `profile_revision`, recalculates `content_hash`, and resets `confirmation.state` to
`pending`. A referenced environment profile revision change makes dependent requirement-scoped
Verification Profiles stale.

## Identity and user declaration

```yaml
version: 1
profile_kind: environment
profile_id: joytime-local
profile_revision: 1
content_hash: sha256:pending
profile_state: draft
confirmation:
  state: pending
  confirmed_by: null
  confirmed_at: null
  confirmed_revision: null
  confirmed_content_hash: null

declaration:
  source: user
  statement: 用户声明的本地验证环境
  provided_at: 2026-09-01T00:00:00+08:00

project:
  name: joytime-studio
  root: /path/provided-by-user

environment:
  name: local
  kind: local
  production: false
  shared: false
```

`profile_id` identifies the reusable environment contract. It must not identify a particular
requirement or acceptance criterion. `content_hash` covers the profile content excluding mutable
confirmation metadata, or another explicitly documented canonicalization rule.

Environment Profile facts are user-provided and user-confirmed. Use `source.kind: user` for entries
in `facts`. Repository and project-document sources are not valid Environment Profile fact sources;
Bruce must not infer them from files it inspected.

Do not add a `source_of_truth` field to an Environment Profile. Repository paths, source-code paths,
implementation details, Git revisions, branches, and test scenario paths belong to codebase or
requirement-scoped verification documentation, not to the user's environment declaration.

Unknown information that the user wants included belongs in `unresolved_facts`:

```yaml
unresolved_facts:
  - fact_id: test-account-purpose
    question: Which user-confirmed account pool should be used for local browser verification?
    required_for: [browser-verification]
    blocking: true
```

Do not replace an unresolved fact with a guessed URL, account, default environment, historical value,
repository convention, or source-code inference.

## Environment scope

```yaml
environment:
  name: shared-test
  kind: local|shared-test|staging|production|other
  production: false
  shared: true
  purpose: integration-and-real-use-verification
  allowed_operations: [readiness-check, test-deploy]
  prohibited_operations: [production-write]
```

Use explicit safety and authorization boundaries. Do not silently infer that a shared environment
is disposable or that a listed operator may perform a write.

## Build and deployment

Build and deployment are separate contracts. Each must state the strategy, executor or external
system, inputs, terminal states, required evidence, and non-equivalence rules.

```yaml
build:
  strategy: cnb
  executor: external-system
  trigger:
    method: project-defined
    authorization_required: true
  terminal_states: [success, failed, canceled, unknown]
  required_evidence:
    - build_id
    - source_commit
    - terminal_status
    - artifact_identity
  invariants:
    - trigger-accepted-is-not-build-success

deployment:
  strategy: project-defined
  executor: project-adapter
  targets:
    - target_id: test-backend
      identity_ref: MULTICA_TEST_BACKEND
  terminal_states: [deployed, failed, rolled_back, unknown]
  required_evidence:
    - deployed_commit
    - deployed_artifact
    - rollout_status
    - readiness_result
  invariants:
    - build-success-is-not-deployment-success
    - deployment-success-is-not-user-verification
```

A static profile must not contain an actual build id, artifact result, deployed revision, rollout
result, current availability claim, runtime result, or selected account instance. Dynamic facts belong
only in Verification Run/Checkpoint. Profile fact values and references must not contain passwords,
API keys, tokens, cookies, private keys, or credential-bearing URLs.

## Local `.env` bootstrap

For a local environment, Bruce may create or update the project-root `.env` only after the user
provides the required values. The `.env` is a local secret sink, not Profile content. The Profile may
record the path, required variable names, and security conditions, but never the values:

```yaml
local_env:
  path: .env
  required: true
  ignored_by_vcs: required
  file_mode: "0600"
  required_variables:
    - BRUCE_AUTH_CENTER_PASSWORD
```

Before using it, check that the file is a regular owner-only file, is ignored by Git, is not tracked,
and contains every required variable with a non-empty value. If it is absent or incomplete, report
only the missing variable names and their purposes, guide the user to provide them, write the file
atomically while preserving unrelated entries, and repeat the metadata-only check. Never print,
copy, hash, or include the values in the Profile, confirmation summary, evidence, logs, screenshots,
or model-facing output. A successful check proves local presence only; it is not authentication or
runtime availability proof.

## Services, databases, and clients

Record safe target references and policies, not live results or secret values:

```yaml
services:
  - service_id: web
    purpose: browser-verification
    endpoint_ref: MULTICA_TEST_WEB_URL
    access: user-or-environment-provided
    runtime_preflight: endpoint-readiness

databases:
  - database_id: test-postgres
    purpose: integration-and-authoritative-readback
    connection_ref: MULTICA_TEST_DATABASE_URL
    mutation_policy: local-ephemeral-only|authorization-required|forbidden
    cleanup_policy: dedicated-fixture-or-approved-reset
    secret_value_persisted: false

clients:
  - client_id: desktop-macos
    purpose: real-client-verification
    artifact_source_ref: user-or-project-provided
    version_identity_required: true
    runtime_preflight: client-version-and-startup
```

`connection_ref`, `endpoint_ref`, and `artifact_source_ref` are references or handles. They must not
contain passwords, tokens, cookies, private keys, or credential-bearing URLs.

## Accounts and Credentials

Environment Profiles describe reusable account pools and credential sources. They do not bind the
specific account used by one requirement run.

```yaml
account_pools:
  - account_pool_id: auth-center-new-users
    provider: auth-center
    purpose: first-login-verification
    account_alias_policy: operator-selected
    required_state_predicates:
      - local_identity_exists: false
    allocation: user-or-operator-managed
    reset_strategy: create-new-account-or-approved-reset
    credential_source_ref: user-managed-browser-session
    authorization_required: false

credentials:
  - credential_id: auth-center-test
    kind: api-key
    source_ref: AUTH_CENTER_TEST_API_KEY
    owner: environment-operator
    scope: sso-ticket-exchange
    preflight_method: non-destructive-auth-check
    secret_value_persisted: false
    expose_to_model: false
    redact_logs: true
```

Use aliases, pools, roles, purposes, and initial-state predicates. Never persist API keys,
passwords, cookies, JWTs, SSO tickets, private keys, or raw credential-bearing connection strings.
If a user supplies a secret during conversation, do not copy it into the profile or output.

## Skills and capability boundaries

List Skills or project capabilities that the environment can make available. This is a capability
catalog, not an execution result:

```yaml
skills:
  - skill_id: cnb-pipeline
    capability_id: cnb-diagnosis
    purpose: inspect-and-diagnose-project-pipeline
    prerequisites: [user-confirmed-project-access]
    evidence_boundary:
      proves: [pipeline-configuration-facts]
      does_not_prove: [terminal-build-success, deployed-revision]
    runtime_preflight: cnb-access-and-target
    selection_authorization: user-or-workflow
```

Do not claim that a Skill is loaded, connected, authenticated, or currently successful unless a
later runtime preflight records that fact in a Verification Run/Checkpoint.

## Preflight and freshness

Preflight entries must be non-destructive and specify the check, target, expected observation, and
runtime evidence:

```yaml
preflight:
  - check_id: deployed-revision
    target: test-backend
    method: read-only-runtime-query
    expected: source-revision-is-reported
    required_evidence: [deployed_commit, readiness_result]
    failure_action: stop-and-notify-user
```

Freshness rules describe when a confirmed profile becomes stale. Ordinary repository source
changes do not make an Environment Profile stale unless the user-declared environment contract or a
user-selected reference changed. The Profile does not carry repository source revisions:

```yaml
freshness:
  basis: user-declared-facts-and-references
  invalidate_on:
    - user-declaration-change
    - environment-scope-change
    - endpoint-change
    - account-policy-change
    - credential-source-change
    - selected-capability-change
    - local-env-variable-scope-change
    - local-env-security-change
  revalidation_required: true
```

Current preflight outcomes belong in a Verification Run or Checkpoint, not in this static profile.
`runtime-preflight` is evidence collected during execution, not an Environment Profile fact source.

## Confirmation summary and ownership

The confirmation summary must identify:

- `profile_id`, `profile_revision`, and `content_hash`;
- environment identity, safety class, and intended verification scope;
- user-provided and user-confirmed facts;
- unresolved facts and exact user questions;
- build/deployment path and authorized operations;
- account pools, credential references, services, databases, clients, Skills, and preflight;
- security policy and freshness rules.

Confirmation is user acceptance of the profile as a controlled input. It is not a Design verdict,
Completion verdict, environment availability result, build result, deployment result, or test result.
