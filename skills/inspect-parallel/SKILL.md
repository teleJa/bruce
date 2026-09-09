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

1. Identify the remaining evidence gaps. If current evidence already answers the question, return
   `Inspection mode: direct` with that reason and do not repeat the investigation. Otherwise, use parallel
   inspection when at least two read-only scopes can be investigated independently and delegation will
   materially reduce latency or main-agent context. Known directory, file, or task boundaries do not mean
   the implementation facts are resolved and are not, by themselves, a reason to choose direct.
   Choose `Inspection mode: direct` with the reason when the remaining work is small, scopes are too
   tightly coupled to investigate independently, or delegation offers no material benefit.
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

This Skill consumes the `inspector` Profile and the shared [delegation contract](../bruce/references/delegation-contract.md).
Each shard uses `task_kind=inspect`, `output=task_evidence_packet`, `allowed_paths=[]`, and
`write_scope=none`; it returns repository-backed evidence and `model_resolution` only. Before calling
`spawn_agent`, apply the shared pre-dispatch routing gate separately to every shard. In
`Inspection mode: direct`, do not create a native subagent or run model routing merely to satisfy the gate.
The inspector's direct fallback is read-only inspection of only the missing scope.

## Does not own

Do not modify files, run external side effects, decide profile or risk, form the task contract, create
plans or design artifacts, begin implementation, maintain Goal state, or decide design readiness or
completion. Do not invoke another supporting skill automatically.
