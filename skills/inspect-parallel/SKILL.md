---
name: inspect-parallel
description: Use when read-only repository inspection has unresolved component boundaries, cross-component contracts, cross-cutting behavior, or conventions that can be investigated as multiple independent scopes. Dispatch bounded native subagents and synthesize source-backed findings without changing files or deciding Bruce profile, risk, design readiness, or completion.
---

# Parallel Inspection

Reduce main-agent context and inspection latency by delegating independent repository evidence
collection while keeping synthesis and workflow decisions with the caller.

## Inputs

- The user request and the unresolved facts that inspection must answer.
- Candidate components, directories, layers, or concerns and their suspected boundaries.
- Concrete questions about entry points, interfaces, consumers, data flow, conventions, commands,
  tests, or dirty-worktree constraints.
- Applicable repository rules and the current workspace status.

## Procedure

1. Confirm that parallel inspection is warranted. Use it only when at least two read-only scopes can be
   investigated independently and their combined evidence will materially reduce latency or main-agent
   context. If boundaries are already clear, scopes are tightly coupled, or only one small area needs
   inspection, return `Inspection mode: direct` with the reason.
2. Define the smallest useful set of non-overlapping primary scopes. Dispatch no more than five
   read-only scopes. Give every shard a bounded directory, component, layer, or concern; three to five
   concrete questions; relevant repository rules; and the same result schema. Permit narrow overlap
   only for read-only evidence at a suspected cross-boundary edge.
3. Dispatch native subagents as read-only explorers. Require each one to preserve the working tree,
   avoid external side effects, distinguish observations from inferences, and cite exact repository
   paths, symbols, interfaces, commands, and tests. Do not select a provider-specific agent name,
   model, token budget, scheduler, or persistent execution mode.
4. Collect results without copying full subagent transcripts into the main context. If a subagent is
   unavailable or a shard fails, retain successful findings and inspect only the missing scope
   directly. Parallel-tool absence alone is not a blocker.
5. Synthesize the evidence into one component map. Resolve contradictory or load-bearing claims
   against the current workspace. Identify cross-component calls, imports, events, schemas, files,
   consumers, ownership boundaries, shared conventions, verification commands, and remaining
   ambiguities. Report profile-relevant evidence, but leave the actual profile and risk decisions to
   Bruce.

## Output

Return:

- `Inspection mode: parallel|direct` and the selection reason;
- investigated scopes and any direct-fallback scope;
- component and ownership map;
- public or cross-component contracts and their consumers;
- relevant repository conventions, commands, tests, and dirty-worktree boundaries;
- conflicts, inferences, confidence limits, and unresolved questions;
- profile-relevant structural evidence for the caller to evaluate.

## Functional Agent routing

This Skill is the `inspector` Profile consumer. Before dispatch, build a v1 Task Packet with `task_kind=inspect`, `output=task_evidence_packet`, `allowed_paths=[]`, while the `inspector` Profile declares `write_scope=none`; include repository evidence sources, allowed/denied tools, acceptance ids, and explicit stop conditions. Resolve the Profile through the shared Bruce resolver; do not select a provider-specific model or Runtime here. The inspector must return only repository-backed evidence and a `model_resolution` record.

### Mandatory pre-dispatch routing gate

When `Inspection mode: parallel`, apply this gate separately to every shard before calling the native `spawn_agent` tool:

1. Complete the v1 Task Packet and resolve the `inspector` Profile through the shared Bruce resolver using the current task, applicable user/project/task overrides, and confirmed host capabilities.
2. Treat the resolver output as a prerequisite, not as a suggestion. Do not call `spawn_agent` until a `model_resolution` record and resolver-produced host arguments are available for that shard.
3. Use the resolver-produced `model` and `reasoning_effort` values verbatim. Pass `model` only when `resolution_result=resolved`; when `resolution_result=fallback`, intentionally omit `model`, preserve the current-model fallback, and record `fallback_used`, `fallback_reason`, `effective_model`, and `capability_status=degraded`.
4. If resolution is `blocked`, the resolver fails, or the host arguments and `model_resolution` disagree, do not dispatch that shard. Return the blocked reason or inspect that missing scope directly according to the fallback procedure above.
5. Attach the same `model_resolution` record to the shard's Task Packet/result. A worker's later `model_resolution` output does not prove that pre-dispatch resolution occurred; the main Agent must retain the pre-dispatch record.

In `Inspection mode: direct`, do not create a native subagent and do not run model routing merely to satisfy this gate.

## Does not own

Do not modify files, run external side effects, decide profile or risk, form the task contract, create
plans or design artifacts, begin implementation, maintain Goal state, or decide design readiness or
completion. Do not invoke another supporting skill automatically.
