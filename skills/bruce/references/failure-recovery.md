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

## Resume sources

For the same Codex task, inspect the current conversation, native plan, tool results, and actual
workspace before continuing. Re-run verification whose preconditions changed, plus every original
failed scenario and related regression required by an in-progress repair round.

When the previous task context is unavailable, inspect the repository from the user's stated goal
or an explicit handoff. Do not infer completion from old workflow artifacts. A handoff can list
facts and decisions, but the receiving task must revalidate workspace and external state.
