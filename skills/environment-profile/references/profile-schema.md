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

Environment Profile facts are user-confirmed. Use `source.kind: user` for entries in `facts`, including
facts accepted after Bruce presents repository-derived candidates. Repository and project-document
sources are not valid Environment Profile fact sources: discovery evidence may guide a user question,
but Bruce must not write it as accepted fact until the user confirms or corrects it.

Do not add a `source_of_truth` field, repository-candidate labels, or repository paths to an
Environment Profile. Source-code paths, implementation details, Git revisions, branches, and test
scenario paths remain discovery/verification evidence, not part of the user's environment declaration.

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

## Environment topology for development and testing

An Environment Profile describes a user-confirmed runtime topology that supports development and
 testing. Its baseline domains are:

1. `environment`: identity, purpose, kind, and safety scope;
2. `deployment`: how application services run and who owns their lifecycle;
3. `build`: how the user builds application units and what artifact is expected;
4. `lifecycle`: user-confirmed prepare/start/stop/status/log operations;
5. `dependencies`: databases, caches, queues, object stores, middleware, or local service adapters;
6. `network`: host/container/remote access scope and declared entrypoints;
7. `identities`: operator and application/test accounts, roles, and initial-state policies;
8. `data_policy`: persistence, isolation, mutation, migration, reset, and cleanup boundaries;
9. `configuration`: local `.env` and other safe configuration/credential references;
10. `preflight`: non-destructive checks and expected evidence.

The user may explicitly mark a domain `not-in-scope`. That is a confirmed boundary and must not be
turned into an unresolved question. These fields describe reusable environment conditions and
operations, not current runtime results or requirement-specific test steps.

```yaml
deployment:
  mode: local-process
  owner: developer
  application_services:
    - service_id: joytime-backend
      deployment_unit: local-process
    - service_id: joytime-frontend
      deployment_unit: local-process

build:
  strategy: user-confirmed-local-build
  executor: local-operator
  working_directory: user-confirmed-project-root
  operations: [build-application]
  artifact_expectations: [user-confirmed-local-artifact]

dependencies:
  - dependency_id: postgres
    category: database
    deployment_unit: docker-container
    locality: local
    purposes: [application-runtime, integration-test]
  - dependency_id: newsnow
    category: middleware-or-external-adapter
    deployment_unit: docker-container
    locality: local
    purposes: [application-runtime]

network:
  access_scope: local-machine-and-local-container-network
  endpoints: []

identities:
  - identity_id: local-developer
    kind: operator
    purpose: [service-lifecycle, local-debug]

data_policy:
  ownership: user-confirmed
  persistence: user-confirmed
  database_write: authorization-required
  migration_write: explicit-authorization-required
  reset_or_drop: explicit-authorization-required

lifecycle:
  prepare: []
  start: []
  stop: []
  status: []
  logs: []

operations:
  - operation_id: build-application
    category: build
    executor: local-process
    authorization: per-invocation
    risk: low
```

## Local `.env` bootstrap

For a local environment, Bruce may create a missing project-root `.env` template before the user
provides values. The template contains only empty values for safe candidate variable names, is ignored
by VCS, and is owner-only `0600`; Bruce then tells the user to populate local account/credential values
directly in `.env` or through a hidden local prompt. Candidate names become required only after user
confirmation. Bruce may update an existing `.env` through hidden prompts only for confirmed variables.
The `.env` is a local secret sink, not Profile content. The Profile may record the path, confirmed
required variable names, and security conditions, but never the values:

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

## Resource references

Use `deployment.application_services`, `dependencies`, and `network.endpoints` to identify reusable
application and middleware resources. A database is a dependency with data policy; an interactive
client is a declared network/identity access path. Record safe references and policies, not live
results or secret values:

```yaml
dependencies:
  - dependency_id: test-postgres
    category: database
    deployment_unit: docker-container
    locality: local
    connection_ref: user-confirmed-test-postgres
    mutation_policy: authorization-required
    cleanup_policy: dedicated-fixture-or-approved-reset

network:
  access_scope: local-machine-and-local-container-network
  endpoints:
    - endpoint_id: web
      purpose: browser-verification
      endpoint_ref: user-confirmed-local-web
      runtime_preflight: endpoint-readiness
```

`connection_ref` and `endpoint_ref` are safe references or handles. They must not contain passwords,
tokens, cookies, private keys, or credential-bearing URLs.

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
user-selected reference changed. Topology, operation, and authorization changes are material. The
Profile does not carry repository source revisions:

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
    - topology-change
  revalidation_required: true
```

Current preflight outcomes belong in a Verification Run or Checkpoint, not in this static profile.
`runtime-preflight` is evidence collected during execution, not an Environment Profile fact source.

## Executable environment operations

A confirmed Environment Profile may optionally produce an executable project-local Skill through
`$environment-operations`. The generated Skill and bounded runner use the confirmed `operations`
entries and their `argv`, risk, authorization, ownership, and evidence requirements. This is an
explicit derived code artifact, not Profile content, and no `operations.yaml` is generated. A legacy
`operation_manifest` field may be read for backward compatibility but is ignored and is not emitted by
new Profiles.

## Confirmation summary and ownership

The confirmation summary must identify:

- `profile_id`, `profile_revision`, and `content_hash`;
- environment identity, safety class, and intended verification scope;
- user-provided and user-confirmed facts;
- unresolved facts and exact user questions;
- build/deployment path and authorized operations;
- account pools, credential references, topology domains, capabilities, and preflight;
- security policy and freshness rules.

Confirmation is user acceptance of the profile as a controlled input. It is not a Design verdict,
Completion verdict, environment availability result, build result, deployment result, or test result.
