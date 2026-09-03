# Requirement Verification Profile schema

A Requirement Verification Profile is a static, requirement-scoped strategy. It is generated from one
explicit `requirements.md` and one or more confirmed Environment Profiles. It is not a test result,
execution ledger, or completion verdict.

## Lifecycle

```text
draft -> needs_input -> ready_for_confirmation -> confirmed -> stale
                                      |                 |
                                  rejected          superseded
```

`confirmation.state` is separate from `profile_state`:

```yaml
profile_state: ready_for_confirmation
confirmation:
  state: pending
```

Only an explicit user confirmation of the exact profile identity, revision, and content hash can set
both the profile and confirmation to confirmed. Confirmation is an input authorization, not a Bruce
Gate.

## Required top-level fields

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
scenario_refs: []
acceptance: {}
blocking_rules: {}
resume_rules: {}
completion:
  owner: completion-gate
  profile_may_return_completion: false
```

## Environment reference

```yaml
environment_refs:
  - profile_id: multica-sharkcloud-test
    path: /project/.bruce/environments/sharkcloud-test.profile.yaml
    profile_revision: 2
    content_hash: sha256:...
    required_confirmation: true
    used_for: [AC-02, AC-03]
```

The referenced Profile is reusable environment input. Do not copy its current runtime results into
this file.

## Acceptance mapping

```yaml
acceptance:
  AC-02:
    source: requirements.md#AC-02
    actors: [new-sso-user]
    environments: [multica-local, multica-sharkcloud-test]
    skills: [test-dispatch, api-test-orchestration, browser-ui-verification]
    scenarios: [SSO-WORKSPACE-001@1]
    verification_stages:
      - stage_id: transaction-integration
        executor: project-adapter
        environment: multica-local
        mode: sync
        depends_on: []
        scenario_id: SSO-WORKSPACE-001
        scenario_version: 1
        tracks: [api]
        preconditions: [test-database-available]
        expected: identity-user-member-onboarding-atomic
        evidence_required: [command-result, database-assertions]
        on_pass: next-stage
        on_fail: classify
        on_blocked: notify-user
      - stage_id: real-sso-login
        executor: browser-provider
        environment: multica-sharkcloud-test
        mode: sync
        depends_on: [build-deploy]
        scenario_id: SSO-WORKSPACE-001
        scenario_version: 1
        tracks: [ui]
        account: new-sso-user
        preconditions: [deployed-revision-matches, unused-sso-subject-confirmed]
        expected: workspace-route-without-onboarding
        evidence_required: [final-url, visible-state, screenshot]
        on_pass: completion-gate
        on_fail: classify
        on_blocked: notify-user
    repair_rules:
      - condition: member-missing-on-matching-revision
        classification: L1
        allowed_scope: server-auth-and-related-tests
        rerun: [transaction-integration, real-sso-login]
      - condition: deployed-revision-mismatch
        classification: L2
        action: stop-and-notify-user
```


Each material Acceptance must appear in `requirements.acceptance_ids` and in at least one acceptance
mapping. A stage is evidence for its mapped Acceptance; passing one stage does not close the entire
Acceptance unless all required stages and evidence are satisfied.

## Shared Scenario and track references

The requirement Profile may select shared Scenario v1 documents without copying their complete
steps or runtime results:

```yaml
scenario_refs:
  - scenario_id: SSO-WORKSPACE-001
    scenario_version: 1
    path: docs/test/scenarios/sso-workspace-001.yaml
    environment_profile: multica-sharkcloud-test
    tracks: [api, ui]
    used_for: [AC-02, AC-03]
```

`scenario_id + scenario_version` is the immutable coordination key for API/UI evidence. The
Requirement Verification Profile records the selected scenario, tracks, and Acceptance mapping only.
The current API/UI Track Result, `overall_status`, command/action output, account instance, and
evidence revision belong to Verification Run/Checkpoint. A Track Result with
`overall_status=passed` is not a Completion verdict.

## Environment, account, and Skill selection

Environment references select reusable environments. Account requirements select aliases or pools and
initial-state predicates. Skill selections record purpose and evidence boundary; availability still
requires runtime preflight.

```yaml
account_requirements:
  - binding_id: new-sso-user
    environment_profile: multica-sharkcloud-test
    account_pool: auth-center-new-users
    required_initial_state: local_identity_absent
    used_for: [AC-02, AC-03]
skill_selections:
  - skill_id: test-dispatch
    purpose: lock-scenario-and-isolate-tracks
    evidence_boundary: scenario-and-track-result
    used_for: [AC-02, AC-03]
  - skill_id: api-test-orchestration
    purpose: api-state-transition-and-authoritative-readback
    evidence_boundary: redacted-api-track-evidence
    used_for: [AC-02]
  - skill_id: browser-ui-verification
    purpose: real-provider-page-actions-and-visible-state
    evidence_boundary: current-provider-browser-evidence
    used_for: [AC-03]
```

## Waiting, blocking, and resume

```yaml
blocking_rules:
  notification_required: true
  explicit_resume_required: true
  stop_scope: affected-task-batch-and-dependent-work
  rules:
    - blocker_id: deployment-revision-mismatch
      condition: deployed_commit_does_not_match_source_revision
      known_facts: []
      unknown_facts: []
      user_action: confirm-or-fix-deployment
      unlock_condition: deployed_commit_equals_source_revision
      resume_from: deployment-check
resume_rules:
  preserve: [task_id, batch_id, contract_revision, profile_revision, retry_count, repair_round]
  rerun: [changed-preflight, stale-evidence, original-failure, related-regressions]
```

`waiting_external` and `waiting_user` are planned non-terminal waits. `blocked` means safe progress is
not possible and must stop, notify, and wait for explicit resume. These states belong to the dynamic
Verification Run/Checkpoint; the static Profile only defines the rules.

## Dynamic boundary

Do not put these in the static Profile:

- actual source revision or deployed revision;
- actual build id or artifact result;
- selected account instance used by one run;
- current preflight result;
- screenshots, logs, or user response;
- current stage status or repair round;
- `Completion` verdict.

Store those in Verification Run/Checkpoint with references to the confirmed Profile revision.

## Security invariant

Credential entries may record `credential_id`, source reference, owner, scope, preflight method, and
redaction policy. They must never record the secret value. Account entries may record alias/pool and
state predicates, not passwords, tokens, cookies, or provider tickets.
