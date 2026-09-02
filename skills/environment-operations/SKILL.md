---
name: environment-operations
description: Generate an executable project-local Skill and bounded runner from a confirmed Environment Profile for build, start, stop, health, and other explicitly declared environment operations.
---

# Environment Operations

Use one exact, confirmed Environment Profile to generate an **executable project-local Skill**. The
primary delivery is a project-local `SKILL.md` plus a bounded runner script. The generated Skill uses
the commands already declared in the Profile, normally by invoking an existing project script or
Makefile target for build, start, stop, health, logs, and other explicitly declared operations.

This Skill does **not** generate `operations.yaml` or another operation manifest. A list of operation
IDs without an executable implementation is not a useful delivery artifact.

Natural-language fields follow [document-language.md](../bruce/references/document-language.md); for Chinese requests use Simplified Chinese while preserving stable machine-facing tokens.

## Preconditions

The source Environment Profile must satisfy all of:

```text
profile_state == confirmed
confirmation.state == confirmed
confirmation.confirmed_revision == profile_revision
confirmation.confirmed_content_hash == content_hash
```

A `draft`, `needs_input`, `ready_for_confirmation`, or `stale` Profile cannot generate an executable
project Skill. The user must explicitly request this generation and confirm the target project and
scope. Generation writes only the selected project-local Skill directory; it does not execute build,
start, stop, database, deployment, or credential operations.

## Repository Skill location and existing Skill check

Before generation, inspect the target project for its supported local Skill roots, in this order:

1. existing `.codex/skills/`;
2. existing `.agents/skills/`;
3. existing project `skills/`;
4. otherwise the user-confirmed new root `.codex/skills/`.

Search those roots for existing `SKILL.md` files whose description or instructions already cover the
Profile's build/start/stop operations. If an existing Skill already owns the operation, do not create
a duplicate silently: present its path and ask whether to reuse it or update it. If no suitable Skill
exists, generate `<skill-root>/<environment-id>-operations/SKILL.md` and its companion executable
`scripts/run_operation.py`. Never overwrite an existing non-Bruce-owned Skill. A prior generated
Skill may be updated only with an explicit update request.

## Generation workflow

1. Load and validate the exact confirmed Environment Profile. Do not use an old revision or a stale
   confirmation.
2. Read the Profile's confirmed `operations` entries. Each entry must have an `operation_id`, a
   non-empty `argv` list, risk, authorization, and required evidence. The `argv` is the executable
   command; it may call an existing project script such as `./start.sh`, or a Makefile target such as
   `make build`. Do not invent a command or replace a declared command with a generic fallback.
3. Resolve the project-local Skill root and check for an existing owner as described above.
4. Run `scripts/generate_operation_skill.py`. It creates:

   ```text
   <project-root>/<skill-root>/<environment-id>-operations/
   ├── SKILL.md
   ├── agents/openai.yaml
   └── scripts/run_operation.py
   ```

5. The generated runner binds to the Profile ID, revision, and content hash. It fails closed if the
   Profile changes, loses exact confirmation, contains an unsafe command, or the operation is not
   declared by the Profile.
6. The generated Skill documents every declared operation and gives the exact command to invoke it.
   `guarded` operations such as build/start/stop require an explicit `--confirm`; `critical`
   operations additionally require `--authorize-critical`.
7. Report generated files and operation IDs. Do not report a successful build/start/stop: generation
   is not execution. Runtime results belong in Verification Run/Checkpoint.

## Execution model of the generated Skill

The generated `scripts/run_operation.py` is the actual bounded executor:

- executes only the Profile's `argv` list, without shell interpolation;
- uses the Profile's project-root or contained working directory;
- loads the confirmed project-root `.env` as child-process input when declared, after checking it is
  a current-user-owned `0600` regular file; it never prints `.env` values;
- blocks undeclared operations, stale Profile bindings, secret assignments in `argv`, and unsafe
  paths;
- requires `--confirm` for guarded operations and an additional `--authorize-critical` for critical
  operations;
- supports `--dry-run` without executing the command;
- returns redacted output and exit status; detailed runtime evidence must be stored by the caller in a
  Verification Run/Checkpoint.

The generated Skill can therefore execute real project commands, for example:

```bash
python3 .codex/skills/joytime-local-operations/scripts/run_operation.py \
  --operation local-build --confirm

python3 .codex/skills/joytime-local-operations/scripts/run_operation.py \
  --operation local-service-start --confirm

python3 .codex/skills/joytime-local-operations/scripts/run_operation.py \
  --operation local-service-stop --confirm
```

The paths above are examples; the generated Skill always uses the actual project-local path and
Profile operation IDs.

## Safety boundaries

- Generating a Skill does not authorize or execute any operation.
- The generated runner does not infer commands from source, Makefiles, repository conventions,
  historical commands, or test files; those may be used by `environment-profile` only to form
  candidates before user confirmation.
- Start/stop commands remain limited to resources explicitly owned by the Profile. They must not
  stop unrelated processes, containers, networks, or databases.
- Migration, seed, reset, drop, destroy, remote deployment, production access, and credential
  rotation remain critical and require explicit per-invocation authorization.
- Credentials are referenced through `.env` or safe handles only. Values never enter generated
  Skill files, command-line arguments, logs, screenshots, Profile summaries, or model-facing output.
- Generation and operation success are not environment availability, requirement acceptance,
  deployment success, or a Completion Gate verdict.

## Output

Return:

- generated project-local `SKILL.md` path;
- generated runner script path;
- source Profile identity and exact revision/hash binding;
- included operation IDs and their risk/authorization classes;
- existing Skill reuse/update decision, if any;
- explicit statement that no operation was executed during generation.

Do not return a Design or Completion verdict.

## Does not own

This Skill does not modify Environment Profiles, generate `operations.yaml`, create generic operation
IDs without Profile declarations, silently overwrite existing Skills, retrieve credentials, execute
operations during generation, authorize production or destructive actions, record runtime results, or
decide verification/completion status.
