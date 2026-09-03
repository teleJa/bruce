---
name: environment-profile
description: Generate a reusable Agent test and verification Environment Profile with one confirmed execution scope for build, deployment, test data, authentication, and evidence.
---

# Environment Profile

Generate or update a reusable **Environment Profile** for Agent testing and verification from
user-provided and user-confirmed environment information. The Profile is the Agent's confirmed
execution context: it records how the Agent may build or deploy the project,
prepare isolated test data, authenticate, run tests, inspect evidence, and stop safely.

This is not a repository inventory, architecture report, test result, or Completion verdict. Repository
inspection is used only to form candidates. The user confirms the candidates and the execution scope.
Natural-language fields follow [document-language.md](../bruce/references/document-language.md); for
Chinese requests use Simplified Chinese while preserving stable machine-facing tokens.

## Core rule: one confirmation, one test scope

A confirmed Profile is an authorization contract for the declared test scope. The Agent must not ask
the user to approve every build, local deployment, test-data preparation, authentication, or test
operation again when:

- the Profile is exactly confirmed by `profile_id`, `profile_revision`, and `content_hash`;
- the operation is declared in `operations`;
- the operation uses `authorization: profile-confirmed`;
- the operation category or ID is covered by `test_context.authorization.approved_scopes`; and
- the operation is not critical or otherwise listed in `escalation_required_for`.

Operations outside this scope, destructive database actions, production access, remote deployment,
and credential rotation still require explicit per-invocation authorization. A Profile confirmation
never authorizes an unlisted operation.

## When to use

Use this Skill when the user wants an Agent to test or verify a project in a reusable environment,
including any combination of:

- build and local deployment/startup;
- test-data preparation, isolation, and cleanup;
- account pools, authentication method, and safe credential references;
- application and dependency endpoints;
- automated tests and read-only evidence collection.

Do not use it to define requirement-specific Acceptance criteria. Use `$verification-profile` for
that; it references this Profile instead of copying it.

## Required inputs

- Project root or explicitly named repository.
- Environment name, purpose, and local/shared/test/staging/production scope.
- The intended Agent test scope and any user-owned data or authorization boundaries that cannot be
  safely inferred.

Never silently select production. If the user leaves out a needed decision, ask only that decision;
otherwise derive bounded repository candidates.

## Candidate discovery

Inspect the target repository read-only. Check the applicable `AGENTS.md`, Git status, README/runbooks,
Makefiles, startup/deployment scripts, test commands, Compose/container descriptors, migration or
fixture tooling, endpoint configuration, and `.env.example`-style files. Extract variable names only;
never reveal or copy values.

Use `$inspect-parallel` only when at least two independent discovery surfaces materially reduce cost,
for example lifecycle/deployment and persistence/test-data configuration. Inspect directly when the
surface is small or tightly coupled. No discovery shard may write files, execute builds, contact
services, or decide Profile state.

Synthesize a short candidate list mapped to the compact `test_context` sections:

- `workflow`: build, deploy/start, test-data preparation/cleanup, authentication, and test operation IDs;
- `services`: application services, dependencies, and endpoints;
- `data`: isolation and allowed/prohibited mutations;
- `authentication`: account pool, method, and safe credential references;
- `configuration`: `.env` metadata and non-secret references;
- `preflight`: non-destructive checks;
- `authorization`: the scope that one user confirmation will cover.

Do not create a second generic `facts` entry for information already represented in `test_context`.
Use `facts` only for a user-confirmed residual fact with no structured home. Cite repository paths
in the chat candidate summary only; never put paths, source revisions, branches, or candidate labels
in the Profile.

## Compact confirmation

Ask for one compact confirmation or correction covering:

1. environment identity and safety scope;
2. the Agent workflow and operation IDs;
3. test-data isolation, cleanup, and permitted mutations;
4. authentication/account/credential references;
5. service endpoints and dependencies;
6. the operations covered by Profile confirmation versus escalation-required operations.

Accepted or corrected candidates become the corresponding `test_context` declarations. Do not turn
runtime observations, account availability, build results, or deployment results into static facts.

## Local `.env`

For a local environment, check only the project-root `.env` using
`scripts/check_local_env.py` or an equivalent metadata-only check. Do not search parent directories,
home directories, shell history, or unrelated repositories.

The Profile may record `.env` path, required variable **names**, ignored/untracked status, and owner-only
`0600` requirements. It must never record values. If `.env` is absent, create an empty-value template
with `scripts/create_local_env.py <project-root> --template`; it must be atomic, non-overwriting,
owner-only `0600`, and Git-ignored. Tell the user to add values directly in `.env`, never in chat.

A successful metadata check proves only local configuration presence. It does not prove authentication,
provider access, database availability, or service readiness.

## Generation procedure

1. Obtain environment identity, purpose, scope, and intended Agent test scope.
2. Run bounded candidate discovery; use `$inspect-parallel` only when justified.
3. Check or safely bootstrap the project-root `.env`; never read or print secret values.
4. Present one compact candidate confirmation request, including the authorization scope.
5. Generate the Profile using the compact `test_context` structure and one top-level `operations` catalog.
6. Set `profile_state` to `draft`, `needs_input`, or `ready_for_confirmation` and
   `confirmation.state: pending`.
7. Validate the Profile and show the exact `profile_id`, `profile_revision`, and `content_hash`.
   Report unresolved questions explicitly; a generated Profile starts with `confirmation.state: pending`
   and may be `ready_for_confirmation` or `needs_input`.
8. Wait for explicit exact confirmation. A vague “continue”, “looks good”, or “try it” is not
   confirmation. Any material change increments the revision and resets confirmation.
9. After confirmation, the user may separately request `$environment-operations` to generate the
   bounded executable project Skill. Generation does not execute any operation.

## Output contract

Use [profile-schema.md](references/profile-schema.md) and
[environment-profile.yaml](templates/environment-profile.yaml). New Profiles should contain:

- identity, declaration, project, and environment scope;
- one compact `test_context` for workflow, authorization, services, data, authentication,
  configuration, and preflight;
- one top-level `operations` catalog with exact commands and evidence requirements;
- freshness and security rules.

Do not emit `operation_manifest`, `confirmation_summary`, or a duplicated top-level inventory of
facts. Do not add a capabilities catalog by default.

## Confirmation and runtime boundary

The usable-state predicate is:

```text
profile_state == confirmed
confirmation.state == confirmed
confirmation.confirmed_revision == profile_revision
confirmation.confirmed_content_hash == content_hash
```

Confirmation authorizes only the declared `test_context` scope. It is not proof of current runtime
availability, build success, deployment success, authentication success, test success, or completion.
Current results, screenshots, logs, selected account instances, source/deployed revisions, stage
status, blockers, and repair rounds belong in Verification Run/Checkpoint or the requirement-scoped
Verification Profile.

## Does not own

## Security and non-ownership

Never persist or expose passwords, API keys, cookies, JWTs, SSO tickets, private keys, or credential-
bearing URLs. Keep credential references safe and retain:

```yaml
security:
  persist_secrets: false
  expose_secrets_to_model: false
  redact_logs: true
  credential_values_allowed: false
  credential_refs_only: true
```

This Skill does not own requirement acceptance, application code changes, runtime results, database
administration, external Secret Manager administration, or Completion decisions. Never report
`Design: pass` or `Completion: pass|issues|blocked` from this Skill. It does not execute
build, deployment, login, SQL, browser, or test operations. `$environment-operations` is the separate
explicit execution capability and must honor the Profile authorization scope.
