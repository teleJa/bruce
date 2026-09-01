---
name: environment-operations
description: Use a confirmed Environment Profile to generate or apply a bounded environment operation manifest for later development and test operations.
---

# Environment Operations

Use one exact, confirmed Environment Profile to generate or apply a project-local **Environment
Operation Manifest**. The manifest packages user-confirmed build, deployment, dependency, lifecycle,
network, data, identity, configuration, and preflight operations for later explicit use.

Natural-language fields follow [document-language.md](../bruce/references/document-language.md); for Chinese requests use Simplified Chinese while preserving stable machine-facing tokens.

This Skill is a static, generic capability. It does not dynamically register a project-level
`SKILL.md`, install global Skills, or silently execute operations when a Profile is generated.

## Preconditions

The source Environment Profile must satisfy all of:

```text
profile_state == confirmed
confirmation.state == confirmed
confirmation.confirmed_revision == profile_revision
confirmation.confirmed_content_hash == content_hash
```

The user must explicitly request manifest generation or operation use and confirm:

- the manifest ID and project-local output path;
- which declared operations are included;
- which operations remain excluded or require per-invocation authorization;
- resource ownership and stop boundaries;
- whether local `.env` may be used as a process input (never values in the manifest).

A `draft`, `needs_input`, `ready_for_confirmation`, or `stale` Profile cannot produce a usable
operation manifest.

## Manifest location and binding

For a project environment, use:

```text
<project-root>/.bruce/environments/<environment-id>.operations.yaml
```

The manifest must bind to the source Profile path, `profile_revision`, and `content_hash`. If the
source Profile changes or becomes stale, the manifest is stale and cannot be used until regenerated
or explicitly updated and reconfirmed.

## Allowed source information

Use only operations already declared and confirmed in the Environment Profile. The Manifest contains
only selected `operation_id` values; it does not copy or override `argv`, executor, risk,
authorization, ownership, targets, or other operation fields. When applying a Manifest, the consumer
loads those complete definitions from the exact bound Profile. The selected operation IDs may cover:

- application deployment topology and lifecycle;
- build and artifact expectations;
- dependency or middleware preparation and status checks;
- network endpoint and readiness checks;
- data, identity, credential-reference, and configuration preconditions;
- non-destructive preflight operations.

Do not infer commands, paths, ports, containers, credentials, accounts, or dependencies from
Go/TypeScript/Python source, Makefiles, repository conventions, historical commands, or test files.
If an operation is not declared by the user, leave it out and request new Environment Profile input.

## Operation risk classes

```text
read-only:
  status, health-check, inspect-declared-resources, bounded-redacted-logs

guarded:
  prepare, build, up, down for explicitly owned resources

critical:
  migrate, seed, reset, drop, destroy, publish, deploy-remote, production-access,
  credential-rotation
```

`read-only` operations may run within their declared scope. `guarded` operations require explicit
per-invocation confirmation. `critical` operations require concrete per-operation authorization and
must state target, impact, rollback/cleanup, and evidence requirements. A manifest never grants
production, remote deployment, database write, or credential-read access merely by listing it.

`down` and cleanup operations must be limited to resources owned by the current invocation or
explicitly declared as safe to stop. They must not stop unrelated processes, containers, networks,
or databases.

## Secret and runtime boundaries

The manifest may contain environment-variable names and safe credential references, but never
passwords, API keys, tokens, cookies, JWTs, private keys, credential-bearing URLs, or `.env` values.
Do not pass secret values as command-line arguments. Tool output, logs, screenshots, Checkpoints, and
model-facing summaries must contain metadata and redacted evidence only.

Applying an operation manifest must run the source Profile's declared preflight first. Operation
success is not environment availability, application acceptance, deployment success, or Completion
Gate approval. Runtime results belong in Verification Run/Checkpoint, not in the static Profile or
manifest.

## Output

Use [operation-manifest.yaml](templates/operation-manifest.yaml) as the manifest shape and validate
it with [validate_operation_manifest.py](scripts/validate_operation_manifest.py). Return the manifest
path, source Profile identity, included operations, excluded/high-risk operations, and confirmation
state. Do not return a Design or Completion verdict.

## Does not own

This Skill does not define or modify Environment Profiles, infer operations from repository source,
install or register project/global Skills, retrieve credentials, execute unlisted build/deploy/start/
stop/database operations, authorize production or destructive actions, record runtime results, or
decide verification/completion status.
