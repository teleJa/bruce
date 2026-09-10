# Delegation contract

This reference defines the shared mechanics for Codex-native subagent delegation. Capability Skills
remain responsible for their role-specific authority, write scope, task kind, evidence semantics, and
failure recovery; they must not create a private router or runtime.

The [Functional Agent contract](functional-agent-contracts.md) owns the exact packet schema and model
resolution rules; this reference defines dispatch sequencing, not a second packet schema.

## Common Task Packet requirements

Every delegated task must declare:

- `schema_version`, `profile_id`, `task_id`, `task_kind`, and `output`;
- objective, bounded allowed/excluded paths, repository evidence sources, acceptance ids, dependencies,
  required verification, prohibited side effects, and an explicit stop condition;
- the role-appropriate `model_resolution` record produced before dispatch.

Resolve the Functional Agent Profile through the shared resolver using task, project, user, built-in,
and current-model precedence. The caller must retain the pre-dispatch record and pass resolver-produced
host arguments unchanged. A worker's later record does not prove that pre-dispatch resolution occurred.

- `resolution_result=resolved`: pass the resolved `model` and `reasoning_effort`.
- `resolution_result=fallback`: omit `model`, inherit the permitted current-model fallback, and record
  `fallback_used`, `fallback_reason`, `effective_model`, and `capability_status=degraded`.
- `resolution_result=blocked`: do not dispatch. Report the missing capability or use the role's explicitly permitted
  direct fallback without pretending that the blocked capability was supplied.

For `reviewer`, model fallback and main-agent/direct review fallback are prohibited. Resolve the shared
reviewer Profile before dispatch; if its model is unavailable or unconfirmed, pause the affected review
and ask the user to name an available replacement. Resume only after that explicit choice resolves with
confirmed host capability. Missing clean context or reviewer tools also blocks review; a model change
does not waive those requirements. Never automatically substitute another model or a verifier.

Do not select provider-specific models, create a Runtime, scheduler, worker registry, permission wrapper,
second ledger, or persistent execution mode inside a capability Skill. Do not dispatch until the packet,
model resolution, host arguments, and write scope agree.

Reviewer results additionally carry the `review_basis` binding defined in the Functional Agent contract.
Retain the actual native dispatch receipt and the immutable reviewed snapshot alongside pre-dispatch
resolution. At consumption, use `validate_review_for_basis` with caller-held current values; do not
accept a packet solely because its fields look valid. Repairs invalidate affected snapshot evidence.

## Implementation evidence reuse

Every `task_kind=implement` dispatch, including same-model delegation, consumes the compact handoff
in [implementation-preparation.md](implementation-preparation.md). Put it in existing v1 fields;
do not add schema fields, create a separate ledger, or require a new document. A list of source paths
without the already verified findings is insufficient. Before every implementation dispatch, carry
verified facts, source basis, executor-only gaps, first edit/test target, and consumed/remaining focused
evidence rounds (including parent usage and extension-used state). When additional investigation is
needed, reconcile missing budget data from parent evidence before dispatch; unknown usage is not zero,
and call/read caps do not replenish rounds. If no investigation gaps remain and safety prerequisites
are confirmed, keep missing consumption unknown and proceed directly to editing or verification with
no additional investigation or extension allowance. Budget bookkeeping must not block a ready safe
slice or skip current-source safety checks.
Require delta checks of current instructions, dirty worktree, and exact editing source; for stale or
inaccessible evidence, reopen only affected facts and their direct dependencies, not the whole survey.
This reuse rule does not apply to independent reviewer conclusions: reviewers still receive clean
context and raw evidence, not author rationale or inherited approval. Verification still needs actual
current test/runtime evidence; design or inspection facts are not a passing result.

## Common evidence and recovery

The main Agent owns dependency order, scope, conflict resolution, integration, and the final workflow
 decision. A delegated `done` statement is never a Gate verdict or sufficient completion evidence.
Return structured evidence with task id, scope, result, changed files or inspected sources, acceptance ids,
verification layer, commands/checks and outcomes, evidence gaps, and remaining work. Preserve unrelated
worktree changes and classify failures using the shared recovery policy.

If delegation is unavailable, failed, or unsafe, retain successful evidence and use only the smallest
role-permitted direct fallback. Do not widen scope merely to compensate for a failed shard.
