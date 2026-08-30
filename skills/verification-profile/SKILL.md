---
name: verification-profile
description: Generate a project-specific Verification Profile for Bruce when build, deployment, runtime, external, or user verification differs by project.
---

# Verification Profile

Generate a **Project Verification Profile** describing the project-specific verification strategy that Bruce's verification loop will consume.
See the generated schema and invariants in [profile-schema.md](references/profile-schema.md) when validating or reviewing a profile.
This skill adapts Bruce to a project's real environment; it does not turn Bruce into that project's
build, deployment, or runtime executor.

## When to use

Use this skill when a task needs a durable, project-specific description of how to verify changes,
including different local, CI/CNB, deployment, Web, Desktop, external-service, or user-manual stages.
Typical examples include a Multica flow that waits for CNB and then requires Desktop testing, or a
Joytime flow that starts a Web service and performs browser/runtime checks.

Do not use this skill to implement an adapter, modify application code, trigger deployment, or decide
whether a task is complete. If the project environment is not sufficiently evidenced, stop with the
missing facts instead of inventing commands, endpoints, credentials, or deployment guarantees.

## Inputs

Read the current Bruce Task Contract, acceptance scenarios, required evidence layers, project
repository rules, existing build/test/deployment documents, and any confirmed architecture or plan.
For persisted documents, apply [document-language.md](../bruce/references/document-language.md): use the
user's language for natural-language fields and Simplified Chinese for a Chinese request while keeping
stable machine-facing tokens unchanged.
Use actual repository commands and declared external capabilities. Distinguish repository evidence,
planned capability, live runtime evidence, and user-supplied evidence.

Before writing a profile, identify:

- stages and dependency order;
- executor for each stage: `local`, `project-adapter`, `external`, `browser-provider`, or `user`;
- synchronous versus asynchronous versus user-waiting behavior;
- required preconditions and terminal results;
- artifact, build, deployment, client, or target identity;
- evidence required for each acceptance id;
- failure mapping to Bruce `L0`–`L4`;
- retry/repair budget and hard stop conditions;
- how an external event or user response resumes the same Task/Batch.

## Procedure

1. Resolve the change directory with [artifact-placement.md](../bruce/references/artifact-placement.md).
2. Inspect the project-specific build, test, deployment, runtime, and manual-verification sources. Do
   not infer a Desktop test from a Web E2E command, a deployment from a build trigger, or a client
   version from an unrelated artifact.
3. Map each material acceptance id to one or more verification stages. Every stage must state its
   executor, dependency, required evidence, and next action.
4. Represent planned external waits as `waiting_external` and planned user testing as `waiting_user`.
   Represent an unsafe or unresolved condition as `blocked`; when blocked, freeze the affected
   Task/Batch and record the user notification and exact unlock condition.
5. Generate one `verification-profile.yaml` in the change directory using the profile schema. Keep
   project commands, targets, and environment facts in the profile or project adapter boundary, not
   in Bruce's core workflow documents.
6. Add a concise human-readable rationale or evidence note only when needed to explain an
   environment-specific decision. Do not copy logs into the profile.
7. Check that no stage can report Bruce completion, that evidence is revision-bound, that external
   actions are idempotent or explicitly bounded, and that a blocked run requires an explicit resume
   event before continuing.
8. Return the generated path, project facts, stage graph, external/user waits, failure mapping,
   unresolved evidence gaps, and the next implementation or verification action.

## Profile contract

The generated profile must contain these top-level fields:

```yaml
version: 1
profile_id: example-project-verification
project: example-project
source_of_truth:
  - path: docs/verification.md
    fact: example evidence-backed project rule
capabilities:
  - capability_id: local-check
    kind: local
    status: available|unavailable|unknown
stages:
  - stage_id: local-check
    executor: local|project-adapter|external|browser-provider|user
    mode: sync|async|user
    depends_on: []
    acceptance_ids: [AC-001]
    preconditions: []
    trigger: example command or handoff
    terminal_states: [pass, fail, blocked]
    required_evidence: [command-result]
    next_on_pass: next-stage|completion-gate
    next_on_fail: classify
    next_on_blocked: notify-user
failure_mapping:
  L0: retry only when idempotent
  L1: bounded repair and reverify
  L2: replan affected scope
  L3: ask user and pause
  L4: freeze and report known/unknown facts
blocking:
  affected_scope: task|batch|goal|incident
  notification_required: true
  unlock_requires_explicit_resume: true
resume:
  preserve: [task_id, batch_id, contract_revision, repair_round, retry_count]
  rerun: [preflight, stale-evidence, original-failure, related-regressions]
completion:
  owner: completion-gate
  adapter_may_return_completion: false
```

Replace example values with repository-backed facts. Keep the stable machine-facing tokens unchanged.
Do not add credentials, cookies, tokens, or secrets to the profile.

## Blocking and resume rules

- `waiting_external` means the expected external system has not returned a terminal result; do not
  repeatedly trigger the same action and do not report completion.
- `waiting_user` means the exact artifact/target and manual steps are ready; provide expected results
  and evidence requirements, then wait for a structured response.
- `blocked` means safe continuation is not possible. Stop the affected Task/Batch, its dependent
  work, and any repair/retry actions; notify the user with known facts, unknown facts, impact, and
  `unlock_condition`.
- Do not resume a blocked run because a new turn merely exists. Require explicit user handling or
  resume intent, re-run changed preflight checks, invalidate affected old evidence, and continue
  from the same Task/Batch/stage without resetting budgets.
- If the user's response changes scope, acceptance, authorization, or risk, return the change to
  Bruce for a new contract revision instead of silently continuing the old profile.

## Output

Return exactly one outcome:

- `Verification Profile: ready` when one repository-backed `verification-profile.yaml` is generated,
  every material acceptance has a stage/evidence mapping, waits and blockers are explicit, and the
  document check is clear.
- `Missing verification evidence` when the project facts cannot support a safe profile. Do not
  generate or update `verification-profile.yaml`; return the smallest bounded inspection needed.
- `Verification Profile: issues` when the profile exists but has repairable mapping, evidence, or
  boundary problems. Do not treat it as implementation approval or completion.

Also return `project`, `profile_path`, `stage_graph`, `waiting_external`, `waiting_user`, `blockers`,
`evidence_gaps`, `document_check`, and `next_action`. Use `[]` for empty collections.

## Does not own

Do not implement project code or adapters, execute CNB/deployment/runtime actions, collect credentials,
replace project test policy, invoke Design Gate or Completion Gate automatically, create a second
workflow or evidence store, or declare `Completion: pass|issues|blocked`.
