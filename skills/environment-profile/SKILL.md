---
name: environment-profile
description: Generate a reusable Environment Profile from user-provided and user-confirmed environment information, with safe credential references, confirmation, preflight, and freshness boundaries.
---

# Environment Profile

Generate or update a reusable **Environment Profile** for one project environment. The profile
records the environment information provided and confirmed by the user, without pretending that the
environment is currently available or that any requirement has passed.

An Environment Profile is a user-confirmed environment declaration, not a repository inventory,
code index, architecture report, or implementation inventory. Before drafting it, Bruce may perform a
bounded read-only exploration of the target repository to reduce the user's data-entry burden. That
exploration produces **candidates only**: it is never copied into Profile facts or treated as an
accepted environment declaration until the user confirms or corrects it.
The environment exists to support development and testing. Its baseline therefore describes
the user-confirmed runtime topology and controlled operations: application deployment, build,
lifecycle, dependencies and middleware, network access, identities and accounts, data policy,
configuration and credentials, and health/preflight requirements.

This is a supporting capability inside Bruce's workflow. It prepares a confirmed input for
requirement-scoped `$verification-profile`; it does not execute the environment.

Natural-language document fields follow [document-language.md](../bruce/references/document-language.md); for Chinese requests use Simplified Chinese while preserving stable machine-facing tokens.
Validate a generated static profile with [validate_profile.py](scripts/validate_profile.py) before presenting its confirmation summary.

## Invocation decision

Use this skill when the user wants to record reusable information about one environment, such as
its identity, endpoints, database references, account pools, credential references, allowed
operations, local `.env` variables, or user-selected capabilities.

Do not use this Profile for broad implementation archaeology or requirement acceptance. Its bounded
repository exploration is limited to candidate local topology, lifecycle commands, dependency
references, endpoints, and configuration-variable **names** needed to draft this environment. If a
verification task needs runtime facts, test scenarios, source-level call chains, or acceptance
criteria, record those in the requirement-scoped Verification Profile or Verification Run instead.

Do not use this skill to define the acceptance criteria for a particular requirement. Use
`$verification-profile` with an explicit `requirements.md` for that requirement.

## Required inputs

- Project root or an explicitly named repository.
- Environment identity, purpose, and intended local/shared/test/staging/production scope. Never
  silently select production.
- Any user-owned operational boundary that cannot be safely inferred or confirmed from candidates,
  such as prohibited data actions, account-policy exceptions, or selected external credential
  provider.

The initial user input does **not** need to enumerate the whole topology. If identity or purpose is
missing, ask only the smallest clarification needed, then derive a candidate declaration as described
below. A relevant domain may be explicitly declared `not-in-scope`; that is a confirmed environment
boundary, not an unresolved fact.

## Repository-assisted candidate discovery

Before drafting a Profile, inspect the target repository read-only to prepare a concise candidate
baseline. This lowers repeated questions; it does not replace user confirmation.

1. First check the target root, applicable `AGENTS.md`, Git status, and safe declarative files such as
   README/runbooks, package/build manifests, Compose or container descriptors, Makefiles, startup
   scripts, CI configuration, migration tooling, and `.env.example`-style files. From environment
   files, extract variable **names only**; never reveal or copy their values.
2. When at least two independent discovery surfaces are necessary (for example application lifecycle
   and persistence/configuration), invoke `$inspect-parallel` with bounded read-only shards. Each
   shard must return exact paths, symbols or commands, candidate facts, and confidence; no shard may
   write files, execute builds, contact services, or decide Profile state. When there is only one
   small/tightly coupled surface, inspect directly instead of spawning agents merely to parallelize.
3. Synthesize a short candidate declaration: deployment/build/lifecycle, dependencies and data
   stores, network endpoints, likely identity/account boundary, candidate `.env` variable names, and
   non-destructive preflight. Mark every item `repository-candidate`, cite its path in the **chat
   summary only**, and distinguish direct observations from inferences.
4. Ask the user to confirm or correct the candidate declaration in one compact confirmation request.
   The user may accept individual candidates, change them, or mark domains `not-in-scope`. Only the
   accepted/corrected result becomes Profile facts with `source.kind: user`; source paths and
   repository-candidate labels do not enter the static Profile. Use `unresolved_fact` only for a
   remaining user-owned decision that is required for the requested Profile scope.
5. Do not use discovery to infer credential values, login sessions, account availability, permission
   grants, production authorization, current service health, or destructive data authority. Keep
   these as user declarations, `not-in-scope`, or unresolved input.

## Local `.env` bootstrap

For a local environment, check the project-root `.env` before finalizing the Profile. Do not search
parent directories, home directories, shell history, or unrelated repositories for credentials.
Use `scripts/check_local_env.py` or an equivalent metadata-only check and never print a value from
the file. Repository discovery may identify **candidate names** but not required variables until the
user confirms them.

The check must verify:

- `.env` exists as a regular file, or is absent and needs bootstrap;
- every required variable explicitly provided or confirmed by the user for this environment is
  present and non-empty; Bruce must not infer the required-variable list from source code, config
  files, or `.env.example`;
- `.env` is ignored by Git and is not already tracked;
- the file is readable only by the current user (owner-only permissions, normally `0600`).

When `.env` is absent or required variables are missing:

1. Report only the candidate/missing variable names and their inferred or user-confirmed purposes;
   never report existing values. Candidate names found in the repository remain candidates until the
   user confirms their scope.
2. If `.env` is absent, proactively create a project-root template using
   `scripts/create_local_env.py <project-root> --template` plus one `--required NAME` for each safe
   candidate name. It must add only `.env` and `.bruce-env-*` ignore entries when absent, create an owner-only
   `0600` regular file atomically, and write names with empty values. It must never generate a secret,
   copy an example value, or overwrite an existing `.env`.
3. Tell the user that the template has been created and ask them to add the required local account,
   password, token, API-key, or other credential values **directly in `.env`** (or through a hidden
   local prompt). Do not ask them to paste values into chat, and do not print, read back, store in the
   Profile, or expose values in logs.
4. Once the user confirms which candidate names belong to this environment, use the hidden-prompt
   `scripts/create_local_env.py <project-root> --required NAME` only to fill missing confirmed values
   if the user explicitly chooses that route. Preserve unrelated entries and never pass values as
   command-line arguments.
5. Re-run the metadata-only check against the confirmed variable names. If the file is tracked, not
   ignored, unreadable, or missing a confirmed value, retain `needs_input` (or report a security
   error) instead of treating the Profile as ready.

The local `.env` is the explicitly approved Phase 1 secret sink for this Skill. It is not part of the
static Environment Profile and does not turn Bruce into a general Secret Manager. Browser cookies,
SSO sessions, private keys, and other credentials that cannot be safely represented as local
variables must remain user-managed or use a separately confirmed provider. A successful `.env`
check proves only local configuration presence, not that an account works or that a service is
available; runtime preflight remains required.

## User declaration and security boundaries

Environment Profile facts are user-confirmed environment information. Use `source.kind: user` for
Profile facts, including a fact the user accepted after seeing a repository candidate. Do not promote
repository paths, source code, test scenario files, Git revisions, branch names, candidate labels, or
runtime observations into this Profile.

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

1. Obtain the environment identity, purpose, and intended scope. Never silently select production.
2. Run the bounded Repository-assisted candidate discovery above. Use `$inspect-parallel` only where
   its independent read-only shards are warranted; otherwise inspect directly.
3. For local scope, metadata-check `.env`. If it is absent, create the secure empty-value template
   from candidate variable names and tell the user to populate local account/credential values outside
   chat. Do not count candidate names as confirmed required variables yet.
4. Present one compact candidate confirmation summary rather than a long domain-by-domain
   questionnaire. Include only material candidates, explicit uncertainties, `not-in-scope` options,
   `.env` template status, and the small number of user decisions still needed.
5. Convert only user-accepted or user-corrected candidates into Profile facts with `source.kind: user`.
   Keep dynamic command results, service availability, selected accounts, and runtime observations in
   Verification Run/Checkpoint.
6. For confirmed local variable names, run the metadata-only check. If values remain missing, write a
   `needs_input` draft and point the user to the existing `.env`; do not delay profile drafting by
   asking for secret values in chat.
7. Define freshness/invalidation for changes to the user-confirmed declaration, topology,
   operations, endpoints, dependencies, account policy, credential references, `.env` variable scope,
   or local file security conditions.
8. Generate the profile with `profile_state: draft`, `needs_input`, or `ready_for_confirmation` and
   `confirmation.state: pending`. Validate it, then return a concise summary of user-confirmed facts,
   safe references, candidate decisions, security policy, preflight, and unresolved questions.
9. Wait for explicit confirmation of the exact profile revision and content hash. A vague “continue”,
   “looks good”, or “try it” is not confirmation. A material edit increments `profile_revision` and
   resets `confirmation.state` to `pending`.
10. After exact confirmation, offer `$environment-operations` as a separate explicit opt-in. It may
    generate a project-local operation manifest from confirmed Profile declarations; it does not run
    operations automatically.

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
- user-confirmed facts and safe references; it must not contain repository implementation paths,
  repository-candidate labels, or a generated `source_of_truth` list;
- application deployment topology, build strategy, lifecycle operations, dependency/middleware,
  network, identity, data, configuration, and preflight declarations;
- optional Environment Operation Manifest request/metadata; it is generated only from a confirmed
  Profile by the explicit `$environment-operations` Skill;
- dependency/middleware, network, identity/account-pool, and safe Credential references;
- user-confirmed capabilities and their evidence boundaries;
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
Manager administration, or external runtime state. It owns only the narrow local `.env` template/bootstrap described above;
it does not provide general credential retrieval or authorization.
It never executes a build, deploy, login, SQL statement, client test, or Environment Operation Manifest on the project's behalf. `$environment-operations` is a separate explicit Skill and does not auto-run when this Profile is generated.
