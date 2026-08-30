# Verification Profile schema

A profile is a project-owned input to Bruce's verification loop. It describes how a project proves its
acceptance criteria without giving the profile authority to declare Bruce completion.

## Required invariants

1. `version` is `1`, and `profile_id` and `project` are stable non-empty identifiers.
2. Every material acceptance id appears in at least one stage's `acceptance_ids`.
3. Every stage declares one executor, one mode, dependencies, preconditions, terminal states,
   required evidence, and next actions.
4. `waiting_external` and `waiting_user` are non-terminal waits; `blocked` freezes the affected
   scope and requires notification plus an explicit resume.
5. External results include a target or artifact identity and a basis revision before they can close an
   acceptance row.
6. Failure mapping points to Bruce's L0-L4 policy; profile-specific facts may refine classification but
   may not weaken the policy or extend retry/repair budgets silently.
7. `completion.owner` is `completion-gate`; an adapter or user response can provide evidence only.
8. Profiles contain no credentials, cookies, access tokens, or secrets.

## Stage modes

| Mode | Meaning | Typical executor |
|---|---|---|
| `sync` | The executor returns a terminal result during the current action. | `local`, `project-adapter`, `browser-provider` |
| `async` | An external action returns later through polling or an event. | `external`, `project-adapter` |
| `user` | The next action is an explicit user handoff and structured response. | `user` |

## Result handling

| Result | Bruce action |
|---|---|
| `pass` | Record current evidence and advance the graph. |
| `fail` | Normalize expected/observed facts and classify before repair. |
| `blocked` | Freeze affected scope, notify the user, and wait for unlock. |
| `unclear` | Request the smallest missing fact; do not guess a repair. |
| `unexecuted` | Keep the acceptance incomplete and record why it was not run. |

## Minimal examples

### Project with asynchronous build and manual client verification

```yaml
profile_id: example-desktop-project
project: example-project
stages:
  - stage_id: local-check
    executor: project-adapter
    mode: sync
    depends_on: []
    acceptance_ids: [AC-001]
    preconditions: [working-tree-basis-recorded]
    trigger: project local check command
    terminal_states: [pass, fail, blocked]
    required_evidence: [command-result]
    next_on_pass: external-build
    next_on_fail: classify
    next_on_blocked: notify-user
  - stage_id: external-build
    executor: external
    mode: async
    depends_on: [local-check]
    acceptance_ids: [AC-001]
    preconditions: [build-trigger-authorized]
    trigger: project build adapter
    terminal_states: [pass, fail, blocked]
    required_evidence: [build-result, artifact-identity]
    next_on_pass: user-client
    next_on_fail: classify
    next_on_blocked: notify-user
  - stage_id: user-client
    executor: user
    mode: user
    depends_on: [external-build]
    acceptance_ids: [AC-001]
    preconditions: [artifact-identity-confirmed]
    trigger: user verification handoff
    terminal_states: [pass, fail, blocked, unclear]
    required_evidence: [observed-result, screenshot-or-log]
    next_on_pass: completion-gate
    next_on_fail: classify
    next_on_blocked: notify-user
blocking:
  affected_scope: batch
  notification_required: true
  unlock_requires_explicit_resume: true
resume:
  preserve: [task_id, batch_id, contract_revision, repair_round, retry_count]
  rerun: [preflight, stale-evidence, original-failure, related-regressions]
completion:
  owner: completion-gate
  adapter_may_return_completion: false
```
