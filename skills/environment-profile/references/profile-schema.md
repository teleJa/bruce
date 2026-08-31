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

## Identity and sources

```yaml
version: 1
profile_kind: environment
profile_id: multica-shared-test
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

`profile_id` identifies the reusable environment contract. It must not identify a particular
requirement or acceptance criterion. `content_hash` covers the profile content excluding mutable
confirmation metadata, or another explicitly documented canonicalization rule.

Material facts should carry source metadata:

```yaml
facts:
  - fact_id: deployment-target
    value: test-cluster
    source:
      kind: repository
      path: .cnb.yml
      revision: current
      provided_at: null
      statement: pipeline deploy target
    confirmation_required: true
    runtime_preflight_required: true
```

Allowed static `source.kind` values are `repository`, `project-document`, and `user`. A user fact
must preserve a short statement or reference without storing secrets. `runtime-preflight` and
`external-system` are dynamic evidence sources and belong only in Verification Run/Checkpoint.
A repository fact should name the path and, when available, the revision used to inspect it.

Unknown material facts belong in `unresolved_facts`:

```yaml
unresolved_facts:
  - fact_id: deployment-target
    question: Which non-production cluster receives the successful build?
    required_for: [deployment-verification]
    blocking: true
```

Do not replace an unresolved fact with a guessed URL, account, default environment, historical
value, or project convention.

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
    prerequisites: [repository-access]
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

Freshness rules describe when a confirmed profile becomes stale:

```yaml
freshness:
  basis: profile-facts-and-source-revisions
  invalidate_on:
    - pipeline-change
    - deployment-target-change
    - endpoint-change
    - account-policy-change
    - credential-source-change
    - client-artifact-change
    - selected-skill-change
  revalidation_required: true
```

Current preflight outcomes belong in a Verification Run or Checkpoint, not in this static profile.

## Confirmation summary and ownership

The confirmation summary must identify:

- `profile_id`, `profile_revision`, and `content_hash`;
- environment identity, safety class, and intended verification scope;
- repository/project-document sources and user-provided facts;
- unresolved facts and exact user questions;
- build/deployment path and authorized operations;
- account pools, credential references, services, databases, clients, Skills, and preflight;
- security policy and freshness rules.

Confirmation is user acceptance of the profile as a controlled input. It is not a Design verdict,
Completion verdict, environment availability result, build result, deployment result, or test result.
