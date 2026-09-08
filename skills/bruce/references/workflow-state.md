# Unified workflow state

This is the authoritative task-level lifecycle state for Bruce. It does not create a scheduler,
Goal ledger, second evidence store, or another verdict owner. The current snapshot belongs in the
requirement-level `checkpoint.yaml`; execution details remain in `verification-run.yaml` and its
immutable evidence.

## States

```text
unresolved -> contracting -> designing -> design_ready
                                      \-> design_blocked
contracting -------------------------> implementing
 design_ready ------------------------> implementing
 implementing -> verifying
 verifying -> waiting_external | waiting_user | repairing | re_verifying | completion_review | blocked
 repairing -> re_verifying | blocked
 re_verifying -> verifying | repairing | completion_review | blocked
 waiting_external -> verifying | blocked
 waiting_user -> verifying | blocked
 completion_review -> completed | completion_issues | blocked
 completion_issues -> repairing | blocked
 active state -> paused -> previous active state
 design_blocked -> designing | blocked
 blocked -> recorded resume_state or an explicit recovery transition
```

`design_ready` is the safe stop point for `design_only`; it is not a completion state. Only
a Gate-emitted `completion_passed` event can enter `completed`; `completion_issues` and
`completion_blocked` preserve the other Completion Gate results.

## Snapshot contract

```yaml
version: 1
task_id: T-001
state: unresolved
state_revision: 0
mode: design_only|implementation
contract_revision: 1
contract_frozen_revision: null
basis_revision: <working-tree-or-commit>
design_gate: not_required|pending|pass|blocked
completion_result: null|pass|issues|blocked
last_event: null
stop_reason: null
resume_state: null
resume_conditions: []
```

Every accepted event increments `state_revision` and records `last_event`. `pause` and `blocked` retain the prior safe lifecycle node in `resume_state`; `resume` is a user-only event, records the resolved target in `last_event.resume_state`, returns to that node, and clears the stop fields. Events cannot reset repair rounds, failure history, evidence revision, Profile revision, or contract revision.

## Event rules

The implementation is `scripts/workflow_state.py`; static validation is available through
`scripts/validate_workflow_state.py`. Unknown states/events, mismatched basis revisions, illegal
transitions, missing pause/block reasons or resume targets, and completion without `Completion: pass` fail closed. `contract_frozen` stays in `contracting`; only an authorized implementation event may enter `implementing`.

`Design Gate` remains the only owner of `Design: pass|blocked` and emits `actor=design-gate`;
`Completion Gate` remains the only owner of `Completion: pass|issues|blocked` and emits
`actor=completion-gate`. The state machine only records normalized events from
those owners and maps their result into the task lifecycle.

## Existing object mapping

| Existing object | Existing state | Unified task state |
|---|---|---|
| Checkpoint task | pending | contracting / implementing |
| Checkpoint task | in_progress | implementing / verifying |
| Checkpoint task | verifying | verifying / re_verifying |
| Checkpoint task | blocked | blocked |
| Verification Run | running/evaluating | verifying |
| Verification Run | waiting_external | waiting_external |
| Verification Run | waiting_user | waiting_user |
| Verification Run | repairing | repairing |
| Verification Run | re_verifying | re_verifying |
| Verification Run | passed | completion_review |
| Verification Run | paused | paused |
| Verification Run | blocked | blocked |
| Design Gate | pass | design_ready |
| Completion Gate | issues | completion_issues |
| Completion Gate | pass | completed |
| Completion Gate | blocked | blocked |

Verification Run remains a sub-run state machine. It cannot write `completed` or a Gate verdict
without a corresponding normalized event from the owning workflow/Gate.

## Legacy checkpoint migration

A pre-state-machine checkpoint without `workflow_state` remains historical evidence, not a valid current
snapshot. At the next material checkpoint or structured resume, reconstruct the current lifecycle from
the frozen task contract, current Design/Completion Gate evidence, current workspace, Verification Run,
repair history, and external state. Create `workflow_state` at `state_revision: 0`, cite the migration
basis in checkpoint evidence, and preserve all known repair/evidence/Profile revisions. Missing or
contradictory evidence stays unknown or blocked; never infer `design_ready`, `verified`, or `completed`
from a legacy task label alone. `validate_workflow_state.py` intentionally fails closed until this
migration is explicit.


## Integration boundary

The state machine and validator are the canonical contract for new checkpoint/run writers. Existing
callers that construct YAML directly must invoke `validate_document` before persistence; this change does
not silently rewrite historical checkpoints or claim that every project adapter has been migrated.
