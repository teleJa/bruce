---
name: environment-profile
description: Generate a reusable Environment Profile from user-provided and user-confirmed environment information, with safe credential references, confirmation, preflight, and freshness boundaries.
---

# Environment Profile

Generate or update a reusable **Environment Profile** for one project environment. The profile
records the environment information provided and confirmed by the user, without pretending that the
environment is currently available or that any requirement has passed.

An Environment Profile is a user environment declaration, not a repository scan, code index,
architecture report, or implementation inventory. Repository files may be inspected later by a
requirement-scoped Verification Profile or Verification Run, but they are not automatically copied
into this Profile.

This is a supporting capability inside Bruce's workflow. It prepares a confirmed input for
requirement-scoped `$verification-profile`; it does not execute the environment.

Natural-language document fields follow [document-language.md](../bruce/references/document-language.md); for Chinese requests use Simplified Chinese while preserving stable machine-facing tokens.
Validate a generated static profile with [validate_profile.py](scripts/validate_profile.py) before presenting its confirmation summary.

## Invocation decision

Use this skill when the user wants to record reusable information about one environment, such as
its identity, endpoints, database references, account pools, credential references, allowed
operations, local `.env` variables, or user-selected capabilities.

Do not use this Profile as a reason to scan repository implementation files. If a verification task
needs repository commands, source paths, implementation details, or current runtime facts, record
those in the requirement-scoped Verification Profile or Verification Run instead.

Do not use this skill to define the acceptance criteria for a particular requirement. Use
`$verification-profile` with an explicit `requirements.md` for that requirement.

## Required inputs

- Project root or an explicitly named repository.
- Environment identity or a user-confirmed description of the target environment.
- User-provided environment identity, scope, services, accounts, credentials, permissions, and
  operational boundaries.
- Optional user-selected references to project instructions or runbooks; these are pointers supplied
  by the user, not facts Bruce should discover by scanning source files.

If the environment identity is missing, ask for the single smallest clarification needed. If a
required fact is unknown, record it as an `unresolved_fact` and ask a precise user question instead
of guessing from history, project conventions, or a similarly named environment.

## Local `.env` bootstrap

For a local environment, check the project-root `.env` before generating the Profile. Do not search
parent directories, home directories, shell history, or unrelated repositories for credentials.
Use `scripts/check_local_env.py` or an equivalent metadata-only check and never print any value from
the file. Use `scripts/create_local_env.py` for the explicit, hidden-prompt bootstrap; never pass secret values as command-line arguments.

The check must verify:

- `.env` exists as a regular file, or is absent and needs bootstrap;
- every required variable explicitly provided or confirmed by the user is present and non-empty;
  Bruce must not infer the required-variable list from source code, config files, or `.env.example`;
- `.env` is ignored by Git and is not already tracked;
- the file is readable only by the current user (owner-only permissions, normally `0600`).

When `.env` is absent or required variables are missing:

1. Report only the missing variable names and their user-confirmed purposes; never report existing
   values.
2. Ask the user which missing variables belong to this Environment Profile before creating or
   updating `.env`; do not infer them from repository files. Guide the user to provide the
   corresponding account, API key, password, token, or other value privately through a hidden local
   prompt or manual local editing. Do not ask for values that are not required by the confirmed
   environment scope.
3. Before writing, ensure the project `.gitignore` contains the exact `.env` entry and the
   generated temporary-file pattern `.bruce-env-*`. If either is absent, add only those narrow
   entries; do not broaden the rule to `.env.*` because `.env.example` may be intentionally
   committed.
4. Create or update the project-root `.env` atomically, preserve unrelated existing entries, set
   owner-only permissions, and do not echo the submitted values in tool output, logs, summaries, or
   the generated Profile. Prefer `scripts/create_local_env.py`, which collects values with hidden
   prompts; never pass them through command-line arguments. Do not ask the user to paste secrets into
   ordinary chat when a hidden local prompt or manual local editing is available.
5. Re-run the metadata-only check. If the file is tracked, not ignored, unreadable, or missing a
   required value, stop with `needs_input` or a security error instead of continuing.

The local `.env` is the explicitly approved Phase 1 secret sink for this Skill. It is not part of the
static Environment Profile and does not turn Bruce into a general Secret Manager. Browser cookies,
SSO sessions, private keys, and other credentials that cannot be safely represented as local
variables must remain user-managed or use a separately confirmed provider. A successful `.env`
check proves only local configuration presence, not that an account works or that a service is
available; runtime preflight remains required.

## User declaration and security boundaries

Environment Profile facts are user-provided and user-confirmed environment information. Use
`source.kind: user` for Profile facts. Do not promote repository files, source code, project
implementation paths, test scenario files, Git revisions, branch names, or runtime observations into
this Profile.

A user may provide a safe pointer to a runbook or project instruction, but that pointer is not an
Environment Profile fact inferred from the repository. Bruce must not generate `source_of_truth`
from files it happened to inspect. The `source_of_truth` field is not part of the Environment Profile
contract.

Repository implementation details belong to architecture/codebase documentation or the
requirement-scoped Verification Profile. Runtime availability, selected accounts, build/deployment
results, and other dynamic observations belong to Verification Run/Checkpoint.

Never write secret values to the Profile or repeat them in output. This includes API keys, passwords,
cookies, JWTs, SSO tickets, private keys, and credential-bearing connection strings. The only local
persistence exception is the user-authorized project-root `.env` bootstrap described above; those
values must not be copied into the Profile, confirmation summary, runtime evidence, logs, screenshots,
or model-facing tool output. Record only safe references such as `env:VARIABLE_NAME`, a user-managed
browser session, or an operator-provided credential handle. Keep `secret_value_persisted: false`,
`expose_to_model: false`, and `redact_logs: true` for Profile credential entries.

## Generation procedure

1. Obtain the environment identity and intended scope from the user. Record whether it is local,
   shared, test, staging, production, or another explicit kind. Never silently select production.
2. Ask the user for the environment facts they want Bruce to remember: services and endpoints,
   database references, account pools, credential references, allowed/prohibited operations,
   selected capabilities, local `.env` variable names, and relevant user-owned runbook pointers.
3. Do not scan source files to discover or populate Environment Profile facts. In particular, do not
   add Go/TypeScript/Python paths, implementation modules, startup call chains, test scenarios,
   Makefiles, or Git revisions merely because they are available in the repository.
4. For a local environment, check `.env` only against the user-confirmed variable names. If the file
   is missing or incomplete, report the missing names and guide the user through the explicit local
   bootstrap flow. Do not mark an unconfirmed variable as required.
5. Record user facts with `source.kind: user`, preserve the user's statement and confirmation
   boundary, and record safe credential references rather than credential values.
6. Describe only the environment-level capabilities the user selected. Do not turn capability
   implementation details or runtime results into Profile facts.
7. Define non-destructive preflight checks and the evidence they should return at execution time.
8. Define freshness and invalidation rules for changes to the user's environment declaration,
   environment scope, endpoints, account policy, credential references, selected capability set,
   `.env` variable scope, or local file security conditions.
9. Generate the profile with `profile_state: draft` or `needs_input` and
   `confirmation.state: pending`. Generate a concise confirmation summary containing only the
   user-declared environment information, safe references, preflight, security policy, and
   unresolved questions.
10. Wait for the user to confirm the exact profile revision and content hash. Do not treat a vague
    “continue”, “looks good”, or “try it” as confirmation when the profile will govern verification.
    A material edit increments `profile_revision` and resets `confirmation.state` to `pending`.

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
- project and environment identity, scope, safety classification, and user declaration metadata;
- user-provided facts and safe references; it must not contain repository implementation paths or a
  generated `source_of_truth` list;
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
CNB/CI execution, deployment, database reads or writes, browser or client operation, external Secret
Manager administration, or external runtime state. It owns only the narrow, user-authorized local
`.env` bootstrap described above; it does not provide general credential retrieval or authorization.
It never executes a build, deploy, login, SQL statement, client test, or Skill on the project's behalf.
