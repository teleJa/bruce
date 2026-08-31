---
name: verification-profile
description: Generate a requirement-scoped verification and repair profile from a user-provided requirements.md and confirmed environment profiles.
---

# Verification Profile

Generate a **Requirement Verification Profile** for one specific change. It describes how the
requirements in a user-provided `requirements.md` will be verified and repaired using confirmed
Environment Profiles, accounts, credentials, tools, and Skills.

This is a supporting capability inside Bruce's workflow. It does not execute project environments,
modify application code, or decide completion.

Natural-language document fields follow the user language; for Chinese requests use Simplified Chinese while preserving stable machine-facing tokens.

## Required input

The user must provide the exact `requirements.md` path for the current requirement. Do not infer it
from a directory scan, chat history, a similarly named change, or `test-plan.md` alone.

Example:

```text
/Users/tele/xjjk/aiworkbench/multica/docs/change/20260825-154000-sso-xiangjia-default-workspace/requirements.md
```

If the path is absent, return `Missing requirements input` and ask for that one path. If the file is
unreadable or has no stable Acceptance criteria, return `Missing verification evidence` without
creating a Requirement Verification Profile.

## Confirmed environment inputs

Consume one or more user-identified Environment Profiles. Each referenced Environment Profile must
have `confirmation.state=confirmed`, matching `profile_revision` and `content_hash`, unless this
skill is only producing an incomplete draft that explicitly lists the missing confirmation.

Environment Profiles provide reusable facts such as:

- build and deployment strategy;
- service, database, browser, Desktop, and client targets;
- account pools and required initial-state predicates;
- safe Credential references, not secret values;
- available Skills/capabilities and their evidence boundaries;
- preflight, authorization, freshness, and stop rules.

If the project environment is undocumented, report the smallest user questions needed to complete
an Environment Profile. Do not invent endpoints, commands, account state, credentials, or deployment
behavior.

## Procedure

1. Read the supplied `requirements.md` and preserve its content hash, path, Objective, Scope,
   Actors, confirmed decisions, exclusions, Acceptance IDs, and constraints.
2. Read the referenced Environment Profiles and verify their confirmation and revision. Record the
   environment revision used by this requirement; do not copy the entire environment definition.
3. For every material Acceptance, define the verification stages, selected environment/profile,
   account requirement, selected Skill/capability, required preconditions, evidence, expected
   result, failure diagnosis, allowed repair scope, and next action.
4. Keep requirement-level `acceptance_ids` and scenario mappings in this Profile. Do not write them
   into an Environment Profile.
5. Distinguish static strategy from dynamic execution. The Profile describes what to do; the current
   source revision, actual account binding, build/deployment identity, evidence, and stage result
   belong in Verification Run/Checkpoint.
6. Define `waiting_external` for planned asynchronous build/deployment or external results and
   `waiting_user` for prepared user testing or operational actions. Define `blocked` only when safe
   continuation is not possible.
7. For every blocker, define the affected Task/Batch, known and unknown facts, user action, exact
   unlock condition, and explicit resume requirement. A blocker stops the affected scope and its
   dependent work; it does not authorize guessing or silent fallback.
8. Define how a confirmed failure enters a bounded repair set, which original scenario and related
   regressions must rerun, and when the loop pauses for user decision instead of editing.
9. Generate `<change-dir>/verification-profile.yaml` with `confirmation.state=pending` and show the
   user a confirmation summary. Do not treat generation as authorization to execute.
10. On a later explicit confirmation, confirm the exact `profile_id`, `profile_revision`, and
    `content_hash`. Any substantive change resets confirmation to `pending`.

## Profile contract

Use [profile-schema.md](references/profile-schema.md) and
[document-language.md](../bruce/references/document-language.md). The generated Profile must include
these sections:

```yaml
version: 1
profile_kind: requirement-verification
profile_id: requirement-specific-id
profile_revision: 1
content_hash: sha256:...
profile_state: draft|needs_input|ready_for_confirmation|confirmed|stale|rejected|superseded
confirmation:
  state: pending|confirmed|rejected
  confirmed_by: null
  confirmed_at: null
  confirmed_revision: null
  confirmed_content_hash: null
requirements:
  path: /absolute/path/to/requirements.md
  content_hash: sha256:...
  acceptance_ids: []
environment_refs: []
account_requirements: []
skill_selections: []
acceptance: {}
blocking_rules: {}
resume_rules: {}
completion:
  owner: completion-gate
  profile_may_return_completion: false
```

Each `acceptance` entry must trace to `requirements.path` and contain a concrete verification and
repair mapping. A Profile with missing environment, account, credential-source, or evidence facts
must remain `draft`/`needs_input` or `issues`; it cannot be confirmed as complete.

## Confirmation and freshness

- Newly generated Profiles are never confirmed by default.
- User confirmation is an input authorization, not a Design Gate, Completion Gate, or test result.
- Requirements hash, referenced Environment Profile revision, account requirement, selected Skill,
  evidence layer, repair boundary, or external authorization changes make the Profile `stale` and
  reset confirmation to `pending`.
- A confirmed Profile can be consumed only when all referenced revisions and hashes still match.
- Runtime preflight remains mandatory after confirmation.

## Security

Record account aliases/pools, actor, purpose, initial-state predicates, and Credential source
references. Never write passwords, API Keys, Cookies, JWTs, SSO tickets, complete provider responses,
or other secret values into the Profile, Checkpoint, Handoff, logs, or the response.

## Output

Return exactly one outcome:

- `Missing requirements input` when the user did not provide the exact requirements.md path.
- `Missing verification evidence` when requirements or confirmed environment facts are insufficient to
  construct a safe requirement-level verification strategy.
- `Verification Profile: ready-for-confirmation` when the Profile is complete enough for the user to
  review but remains `confirmation.state=pending`.
- `Verification Profile: issues` when the generated draft has explicit repairable mapping or fact gaps.

Also return:

```yaml
requirements_path: ...
requirements_content_hash: ...
profile_path: ...
profile_revision: ...
confirmation_state: pending|confirmed|rejected
acceptance_coverage:
  covered: []
  uncovered: []
environment_refs: []
account_requirements: []
skill_selections: []
waiting_external: []
waiting_user: []
blockers: []
evidence_gaps: []
next_action: confirm-profile|collect-environment-input|repair-profile|none
```

Do not return `Design: pass`, `Completion: pass`, or any other Gate verdict.

## Does not own

Do not generate Environment Profiles, execute project commands, trigger CNB or deployment, operate
browsers or clients, retrieve or persist secrets, modify requirements.md, modify application code,
create a Verification Run, invoke Design Gate or Completion Gate automatically, or declare completion.
