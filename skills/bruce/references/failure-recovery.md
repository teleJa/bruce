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

## Event-driven checkpoints

This section is the single authority for checkpoint and recovery triggers. Require a structured
checkpoint at a material task/batch handoff, scope or contract revision change, environment or risk
change, evidence invalidation, or before crossing an external verification or side-effect boundary.
Record the affected scope, current basis, evidence and next safe action before dependent work proceeds.
Use the schema in [verification-loop.md](verification-loop.md) only for these structured checkpoints.

Elapsed time, tool-call count, profile, and user-turn boundaries alone do not require a checkpoint.
For a long unchanged operation, give a brief progress update when useful; do not count calls merely
to trigger a full schema. Progress messages may omit checkpoint ids and empty matrices.
A progress update never substitutes for a checkpoint at an actual material boundary.
Ordinary authorized implementation continues after the required checkpoint unless a user pause, host
limit, scope/authority change, exhausted repair budget, or real blocker requires stopping.
Checkpoint recording or continuation never resets L0/L1 retry or repair counts.

A long-running command may remain active when it is known, owned by the current task, and safe to
leave running. Do not terminate or restart it merely to produce progress feedback.

## Tool-handle lifecycle

- Track each active async handle with its owning batch, command purpose, creation result, and latest
  observed state in the current task; record material long-running handles in the existing checkpoint
  when applicable, without requiring a Goal or separate audit record.
- Wait or write only through the latest live handle returned by that exact tool call. Mark it closed
  after completion, termination, rejection, or a definitive invalid-handle response, and never use it
  again.
- Do not treat repeated no-output polls as progress. Use bounded waits of at most 60 seconds; after
  two no-progress polls, inspect the process or dependency state before another wait.
- When a handle disappears, inspect the actual process and external state before retrying. Classify an
  unknown external side effect as L4; otherwise use L2 when the result cannot be recovered safely.
- Never terminate or adopt a process that the current task did not start.

## Resume sources

For the same Codex task, inspect the current conversation, native plan, tool results, task contract,
existing checkpoint when present, and actual workspace. When context, basis, environment, and evidence
remain usable, perform a lightweight consistency check and continue the existing next action.
A `full` profile, a new user turn, or “继续” alone does not require a `Resume checkpoint`.

Require a structured `Resume checkpoint` when context is missing, the workspace/contract/environment
materially changed, evidence became stale, or a prior operation has an unknown result. Establish the
current basis, live handles, latest evidence, affected acceptance, known findings, allowed paths, and
next safe action before new dependent inspection, edits, or verification. Unknown external side effects
remain L4; do not replay them. Rerun checks whose preconditions changed, the unchanged original failed
scenario, and required related regressions. Neither continuation nor checkpoint recording resets
retry or repair counts or authorizes unmapped inspection.

Ordinary recovery does not require Goal or `execute_record.md`. Consult native Goal only for an
explicitly requested Goal lifecycle; unavailable Goal tools do not block ordinary recovery.
When prior context is unavailable, use the user objective or explicit handoff and current repository
evidence. Do not infer completion from old workflow artifacts. Missing evidence means unknown, not
verified. Preserve unrelated working-tree changes and do not reopen unrelated investigation.
