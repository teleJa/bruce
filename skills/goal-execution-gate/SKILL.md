---
name: goal-execution-gate
description: Use when Bruce routes a full delivery profile, or when the user explicitly requests Goal mode, continuous execution, cross-turn continuation, or an auditable execution record. Manage the native Codex Goal lifecycle and maintain one execute_record.md audit file without creating another runtime.
---

# Goal execution gate

Connect a persistent Bruce delivery to Codex native Goal management. Native Goal is the only source
of execution status; `.goal/<goal-id>/execute_record.md` is the human audit source only.

## Entry

Enter this gate when Bruce routes a `full` task. A `standard` task enters only when the user
explicitly asks for Goal mode, continuous execution, cross-turn continuation, or an auditable
record. Complexity, duration, risk, or subagent use alone does not promote a `standard` task.

Before creating a Goal, use `get_goal` and prepare:

- objective and allowed/excluded scope;
- verifiable acceptance criteria and evidence paths;
- repository and user constraints;
- the Bruce execution profile and independent business-risk level.
- the passed `artifact-review.md` path and verdict from Bruce.

Continue a matching active Goal. Do not silently replace a conflicting unfinished Goal. Create a
new Goal only for a confirmed entry and include objective, acceptance, scope, and constraints in its
objective. Pass a token budget only when the user explicitly specified one.
Do not create or resume execution state for a design-bearing task until the referenced artifact gate
is current and passed.

## Audit record

After Goal creation or resumption, create or reuse
`.goal/<goal-id>/execute_record.md`. If no usable Goal id is returned, use a stable timestamp slug and
record the native objective. Include:

- objective, acceptance, scope, and constraints;
- the passed `artifact-review.md` path and verdict as the design-stage prerequisite;
- material decisions and their evidence;
- executed verification and current outcomes;
- blocking facts and exact unlock condition;
- final conclusion.

Update the record at creation, material decisions, verification, blocking confirmation, and final
closure. Do not mirror every Goal transition or infer native status from the file.
The record may link to the design gate, but it does not copy candidate-artifact or skip decisions
and never substitutes for the same-directory `artifact-review.md`.

## Execute and close

Maintain the nearest executable plan with native planning tools. Use `spawn-execute` only for
boundary-clear delegated work under the active Goal; ordinary implementation, testing, and review
remain owned by Bruce and its selected skills.

Continue implementation, verification, bounded repair, and re-verification until every acceptance
criterion has current evidence or a real blocking condition remains. One failure, a long task, or a
completed subtask is not a terminal result.

Call `update_goal(status="complete")` only after the objective is delivered, every acceptance item
has current evidence, required C0/D0/D1 and risk-proportional reviews pass, the audit record contains
the final execution evidence and artifact-gate reference, and no required work remains.

Call `update_goal(status="blocked")` only after the same blocking condition recurs for at least three
consecutive Goal turns, safe in-scope alternatives are exhausted, and the audit record states the
reproduction evidence and unlock condition.

## Does not own

Do not widen user authority, commit, push, publish, deploy, mutate infrastructure, or perform other
delivery actions unless separately authorized. Do not implement a scheduler, worker registry,
permission wrapper, sandbox, alternate state machine, second ledger, or transcript mirror.
