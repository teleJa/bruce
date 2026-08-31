---
name: environment-profile
description: Generate a reusable, repository-grounded Environment Profile from project facts and user-provided environment knowledge, with safe credential references, confirmation, preflight, and freshness boundaries.
---

# Environment Profile

Generate or update a reusable **Environment Profile** for one project environment. The profile
records how an environment can support Bruce verification without pretending that the environment
is currently available or that any requirement has passed.

This is a supporting capability inside Bruce's workflow. It prepares a confirmed input for
requirement-scoped `$verification-profile`; it does not execute the environment.

Natural-language document fields follow [document-language.md](../bruce/references/document-language.md); for Chinese requests use Simplified Chinese while preserving stable machine-facing tokens.
Validate a generated static profile with [validate_profile.py](scripts/validate_profile.py) before presenting its confirmation summary.

## Invocation decision

Use this skill when verification depends on environment facts that should be reused across changes,
such as build and deployment paths, service targets, databases, clients, account pools, credential
references, project Skills, or preflight checks. Use it even when some facts are known only by the
user and are not documented in the repository.

Do not use this skill to define the acceptance criteria for a particular requirement. Use
`$verification-profile` with an explicit `requirements.md` for that requirement.

## Required inputs

- Project root or an explicitly named repository.
- Environment identity or a user-confirmed description of the target environment.
- Any available repository and project-document paths that govern build, deployment, runtime, test,
  account, credential, or operational behavior.
- User-provided environment facts when the repository cannot establish them.

If the environment identity is missing, ask for the single smallest clarification needed. If a
required fact is unknown, record it as an `unresolved_fact` and ask a precise user question instead
of guessing from history, project conventions, or a similarly named environment.

## Fact and security boundaries

Classify every material fact with one of these source kinds:

- `repository`: directly supported by current repository files;
- `project-document`: supported by a project-owned document or runbook;
- `user`: supplied by the user because it is not discoverable from the repository.

`runtime-preflight` and `external-system` are dynamic evidence sources and belong in a Verification
Run/Checkpoint, not in a static Environment Profile.

A user-supplied fact is a declared environment fact, not runtime proof. Preserve its source,
statement reference or note, provided time, confirmation requirement, and whether runtime preflight
is still required.

Never write secret values to the profile or repeat them in the output. This includes API keys,
passwords, cookies, JWTs, SSO tickets, private keys, and connection strings containing credentials.
Record only a safe reference, such as an environment-variable name, secret-manager key, user-managed
browser session, or operator-provided credential handle. Set `secret_value_persisted: false`,
`expose_to_model: false`, and `redact_logs: true` for credential entries unless a stricter policy
is required.

## Generation procedure

1. Identify the environment and its intended verification scope. Record whether it is local, shared,
   test, staging, production, or another explicit kind. Never silently select production.
2. Inspect only the named project repository and relevant project documents. Extract build, deploy,
   service, database, client, test, Skill, and preflight facts with source paths and revisions when
   available.
3. Ask the user for facts that cannot be established, including deployment targets, manual steps,
   account lifecycle, credential source, operational authorization, and client artifact access.
4. Record reusable account pools and state predicates, not passwords or tokens. Record credential
   references and allowed scopes, not credential values.
5. Describe build and deployment transitions separately. A trigger being accepted is not a build
   success; a build success is not a deployment success; a deployment success is not user-facing
   verification.
6. List available Skills or project capabilities with their purpose, prerequisites, evidence
   boundary, and limitations. Skill presence is not proof that the capability is available now.
7. Define non-destructive preflight checks and the evidence they should return at execution time.
8. Define freshness and invalidation rules for changes to pipelines, targets, endpoints, account
   policy, credential sources, client artifacts, or selected Skills.
9. Generate the profile with `profile_state: draft` or `needs_input` and
   `confirmation.state: pending`. Generate a concise confirmation summary containing the profile
   identity, revision, content hash, sources, unresolved facts, environment, account pools,
   credential references, build/deploy path, Skills, preflight, security policy, and authorized
   operations.
10. Wait for the user to confirm the exact profile revision and content hash. Do not treat a vague
    “continue”, “looks good”, or “try it” as confirmation when the profile will govern verification.
    A material edit increments `profile_revision` and resets confirmation to `pending`.

## Confirmation and use rules

The profile is usable as a controlled Bruce input only when all of the following hold:

```text
profile_state == confirmed
confirmation.state == confirmed
confirmation.confirmed_revision == profile_revision
confirmation.confirmed_content_hash == content_hash
```

A profile may be `ready_for_confirmation` while still having `confirmation.state: pending`. If a
required fact is missing, use `needs_input`; if a previously confirmed fact or referenced contract
changes, mark the profile `stale` and require reconfirmation.

Confirmation means that the user accepts the recorded environment facts and boundaries. It does not
prove current availability, authorize an unlisted operation, or produce a Design or Completion
verdict. Bruce must still run the required runtime preflight before controlled verification.

## Output

Create or update the requested Environment Profile, normally at:

```text
<project-root>/.bruce/environments/<environment-id>.profile.yaml
```

The output must include:

- profile identity, revision, content hash, lifecycle state, and confirmation metadata;
- project and environment identity, scope, safety classification, and source-of-truth paths;
- repository, project-document, and user-provided facts with source metadata;
- build and deployment strategies, targets, terminal evidence, and non-equivalence rules;
- service, database, client, account-pool, and safe Credential references;
- available Skills/capabilities and their evidence boundaries;
- non-destructive preflight checks and required runtime evidence;
- freshness/invalidation rules, security policy, unresolved facts, and minimal user questions.

Return a short confirmation summary after writing the draft. Report `Environment Profile: draft`,
`needs_input`, `ready_for_confirmation`, `confirmed`, `stale`, or `rejected` as a profile lifecycle
state only. Never report `Design: pass` or `Completion: pass|issues|blocked` from this skill.

Use [profile-schema.md](references/profile-schema.md) for field semantics and
[environment-profile.yaml](templates/environment-profile.yaml) as the output shape. The template is
an unconfirmed static profile, not a live run record.

## Does not own

This skill does not own requirements or acceptance criteria, requirement-scoped verification plans,
Verification Run or Checkpoint state, Design Gate, Completion Gate, project adapters, schedulers,
CNB/CI execution, deployment, database reads or writes, browser or client operation, credential
retrieval, secret storage, user authorization, or external runtime state. It never executes a
build, deploy, login, SQL statement, client test, or Skill on the project's behalf.
