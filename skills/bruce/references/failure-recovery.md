# Failure and recovery policy

Classify a returned failure before deciding whether to continue. Apply the decision to the smallest
dependency or incident boundary supported by current facts.

| Level | Class | Default response | Propagation |
|---|---|---|---|
| L0 | Transient: rate limit, connection reset, temporary lock, occasional tool timeout | Retry only when idempotent; after the first failure allow at most two retries with backoff | Failed task and its dependents wait |
| L1 | Repairable: compile, test, lint, type, assertion, scenario, or local implementation error | Make an actual correction, inspect the changed code, then rerun the original failed scenario and related regressions; allow at most two complete repair-and-reverify rounds | Failed task and its dependents wait |
| L2 | Replan: missing dependency, incompatible interface, invalid approach, or denied host action with an authorized alternative | Replan the affected task, descendants, and unsafe shared-file/contract peers | Proven dependency-independent work continues |
| L3 | Business authority: unresolved scope, acceptance change, or unauthorized guarded/critical action | Ask one precise question and pause only work that needs the answer | Independent work continues |
| L4 | Unknown or incident: non-idempotent external action may be half-complete, data/security state is unknown, or integrity risk is reported | Freeze writes, retries, and work depending on the unknown result inside the incident boundary; report known and unknown facts | Only read-only diagnosis and proven-isolated work may continue |

## Deterministic limits

- `retry_count` counts attempts after the first L0 failure. Retry only while `retry_count < 2`.
- `repair_round` counts only after an actual L1 correction, author inspection, the unchanged original
  failed scenario, and related regressions were run. Move to L2 when two complete rounds still fail.
- Do not call an unchanged compile, type, assertion, or lint error transient.
- Move exhausted L0/L1 work to L2; do not extend the budget informally.
- Treat unknown external side-effect state, data integrity risk, and security incidents as L4.
- Treat host permission denial as authoritative. Use an authorized alternative through L2 or report
  blocked; never elevate privileges or replay behind the host.
- Do not weaken acceptance, replace the original failure with a smaller passing check, or claim a
  user-visible Web scenario passed from unit evidence alone.

## Work interval

For multi-batch or long-running work, use `max_tool_calls=40` and `max_elapsed=45m` unless the task
contract records a smaller repository-driven limit. Count all tool invocations, including retries and
polls. When either limit is reached, stop starting new work, inspect live handles, record current
evidence and remaining work, and run the batch checkpoint. Do not begin another behavior edit,
dependent batch, or work interval until an assistant message records the complete checkpoint schema
from [verification-loop.md](verification-loop.md); an `update_plan`, progress summary, or test output
is not a checkpoint. Ordinary work returns control after the checkpoint. Explicit Goal or continuous
execution may begin a new interval only after recording the checkpoint and resetting both counters; a
reset never erases retry or repair counts.

A long-running command may remain active across an interval when it is known, owned by the current
task, and safe to leave running. Do not terminate it merely to satisfy the interval boundary.

## Tool-handle lifecycle

- Track each active async handle with its owning batch, command purpose, creation result, and latest
  observed state in the current task; Goal mode records only material long-running handles in its
  existing audit record.
- Wait or write only through the latest live handle returned by that exact tool call. Mark it closed
  after completion, termination, rejection, or a definitive invalid-handle response, and never use it
  again.
- Do not treat repeated no-output polls as progress. Use bounded waits of at most 60 seconds; after
  two no-progress polls, inspect the process or dependency state before another wait.
- When a handle disappears, inspect the actual process and external state before retrying. Classify an
  unknown external side effect as L4; otherwise use L2 when the result cannot be recovered safely.
- Never terminate or adopt a process that the current task did not start.

## Resume sources

For the same Codex task, inspect the current conversation, native plan, tool results, and actual
workspace before continuing. Re-run verification whose preconditions changed, plus every original
failed scenario and related regression required by an in-progress repair round.

For an unfinished `full` task after a user-turn boundary, first enter or resume `goal-execution` and
return a `Resume checkpoint`. Establish only the native Goal, current workspace basis, live handles,
and latest batch evidence before that checkpoint; do not start new code discovery, behavior edits, or
verification first. The Resume checkpoint records the current batch, basis, latest checkpoint or its
absence, known findings/repair set, allowed paths/direct call sites, deferred concerns, next evidence,
and stop condition. A continuation request does not reset the work interval or authorize unmapped
inspection.

When the previous task context is unavailable, inspect the repository from the user's stated goal
or an explicit handoff. Do not infer completion from old workflow artifacts. A handoff can list
facts and decisions, but the receiving task must revalidate workspace and external state.
