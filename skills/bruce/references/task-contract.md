# Task contract package

A persisted Bruce change package normally contains a `tasks/` directory beside its design documents.
The package turns a complete requirement/design package into small, traceable execution contracts without
creating a second workflow, scheduler, or evidence store.

## When to create it

Create `tasks/` by default when Bruce persists an implementation plan, a handoff, or a multi-step
requirement. It is especially useful for `full` or `guarded` work, cross-component changes, long-running
work, and any request that benefits from explicit sequential tracking. A genuinely trivial,
documentation-only change may omit it, but the plan or design review must record the concrete reason.

The package normally contains:

```text
tasks/
  index.yaml
  T-001-<short-slug>.md
  T-002-<short-slug>.md
checkpoint.yaml
```

`tasks/` is one change-level package. Do not create one plan or task package per repository for a
cross-repository change; keep repository ownership and paths inside each task contract.

## Frozen task contract

Each task contract is frozen before execution. Each task file is frozen before its task starts. It records:

- stable `task_id` and title;
- objective and observable task-local result;
- included and excluded paths/components (`include`/`exclude`);
- dependencies and consumed/produced interfaces;
- parent acceptance/scenario ids;
- required verification layers and concrete evidence;
- authorization, risk, and stop conditions;
- `contract_revision` and links to the governing design documents.

A task contract records explicit include/exclude scope and may be revised only through an explicit
contract change or a new superseding task. Do not silently widen `include`, remove an `exclude`,
change acceptance, or change the required verification layer while executing the task.

Tasks are sequential by default. `depends_on` records dependency order even when Bruce is not using
parallel execution. `parallel_safe` is only a documented fact for future scheduling; it does not
activate a scheduler or authorize concurrent edits.

## Task state and checkpoint

The task file is the stable contract, not the live status ledger. The current status of every task is
recorded in the change-level `checkpoint.yaml` or in the current checkpoint message. Use these states:

- `pending`: not started;
- `in_progress`: current task is executing;
- `implemented`: the declared change exists but required verification is incomplete;
- `verifying`: required checks are running;
- `verified`: task-local acceptance and required evidence passed;
- `blocked`: authority, dependency, environment, or failure prevents safe progress;
- `superseded`: replaced by a newer task-contract revision.

A task can run for a long time. A checkpoint records its current state and evidence references; it does
not split, restart, or shorten the task. A long-running task may appear in several checkpoints while
remaining the same `task_id` and contract revision.

Checkpoint data is a progress snapshot, not a second evidence store. It records the canonical
`Checkpoint` status, task states, environment, batch matrix, paths, hashes, commands, evidence ids,
findings, blockers, and next actions; it does not copy large logs or replace repository evidence
artifacts.

A task is complete only when its status is `verified`, its required verification has passed, and the
current evidence revision still matches the task contract and working-tree basis.
