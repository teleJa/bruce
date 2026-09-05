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

## Budget ownership and precedence

This reference owns both budget scopes and their precedence. A failed original scenario keeps one stable
`failure_id` across batches, Completion, and resume. A genuinely different failure gets a new id with its
own evidence; renaming a repeated failure never grants more attempts. Record `failure_id` and
`l1_repair_rounds` on the existing checkpoint `findings` row, with the original scenario and evidence refs.
No new ledger is required. A successful repair can resolve that finding; the table below applies only
while a failure remains unresolved. If an old checkpoint has no reliable count, recover it from existing
evidence before repair; missing history is unknown, not zero. Do not reset a count on recurrence.

- Local L1 budget: at most two complete repair-and-reverify rounds per failure, in any phase. A declared
  smaller task/batch budget also applies. Exhaustion moves that affected failure to L2.
- Completion budget: `workflow.repair_loop.max_rounds` (integer 1 through 5, default 5) limits overall
  repair rounds after the initial Completion scan (round 0), across all findings in that Completion.
  Store this counter in existing `repair_loop.current_round`; do not reuse it as a per-failure count.
- Batch verification never reads or spends the Completion budget. During Completion, each actual
  repair set spends one global round and each repaired failure spends its own L1 round after complete
  correction, inspection and re-verification. A no-op or mere poll does not earn another attempt.
- Stop at the first applicable local or global limit. Global exhaustion returns Completion issues
  for repairable residuals; L2-L4 or missing authority/evidence return blocked at the affected boundary.
  A new finding may have local budget left but cannot bypass an exhausted global budget.

### Unresolved-failure decision table

Evaluate in order; `below_limit`/`at_limit` refer to the configured Completion maximum, not a hardcoded five.
Unknown external state is L4 before either budget is considered. Partial/incomplete attempts do not
justify unbounded reruns; inspect actual state under L0-L4 first.

| Rule | External state | L1 rounds | Phase | Completion rounds | Action |
|---|---|---|---|---|---|
| BUDGET-01 | unknown | any | any | any | freeze_L4 |
| BUDGET-02 | known | unknown | any | any | recover_counts |
| BUDGET-03 | known | 2+ | any | any | replan_L2 |
| BUDGET-04 | known | 0-or-1 | completion | unknown | recover_counts |
| BUDGET-05 | known | 0-or-1 | completion | at_limit | stop_completion |
| BUDGET-06 | known | 0-or-1 | completion | below_limit | repair_both |
| BUDGET-07 | known | 0-or-1 | batch | any | repair_local |

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

Ordinary recovery does not require native Goal state or `execute_record.md`. Native Goal state is
outside Bruce's workflow and unavailable Goal tools do not block ordinary recovery.
When prior context is unavailable, use the user objective or explicit handoff and current repository
evidence. Do not infer completion from old workflow artifacts. Missing evidence means unknown, not
verified. Preserve unrelated working-tree changes and do not reopen unrelated investigation.
