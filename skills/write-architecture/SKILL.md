---
name: write-architecture
description: Use when a software task needs an explicit structural decision, public or cross-component contract, component boundary design, or durable architecture handoff. Inspect the current repository, produce only the necessary architecture and contract artifacts, and keep implementation planning and approval outside this skill.
---

# Write architecture

Design only when the task needs a durable structural or contract decision.

## Inputs

- Objective, scope, acceptance, constraints, execution profile, and known risk.
- Current repository components, toolchains, deployables, interfaces, and architecture conventions.
- Existing decisions or domain clarification when available.
- A requested output location when artifacts must be persisted.

## Procedure

1. Inspect the current repository with available Codex tools. Use a native subagent only when the
   exploration boundary is clear; otherwise inspect sequentially.
2. Identify the decision that needs architecture treatment. A single-component task may still need
   this skill for a public contract or hard-to-reverse structural choice.
3. Define components from real ownership, build, deployment, or delivery boundaries. Do not turn
   internal layers into artificial components.
4. Define each changed external or cross-component contract with provider, consumer, request or
   event shape, success/error behavior, authentication, compatibility, and versioning.
5. Cover data flow, failure handling, rollout/rollback, observability, security, and verification in
   proportion to the decision.
6. Generate `architecture.md` from [architecture.md](templates/architecture.md) only when a durable
   architecture artifact is requested or needed for handoff. Generate `api-contracts.md` from
   [api-contracts.md](templates/api-contracts.md) only when an actual contract must be frozen.
7. When an artifact was persisted, separately inspect its diff, verify claims against repository
   evidence, check contracts and cross-document references for consistency, and remove material
   omissions, unresolved placeholders, and broken links. Repair issues and return
   `Document self-review: pass|issues`. Flag D1 document readiness review when the artifact will
   govern downstream work; do not invoke another supporting skill automatically.

## Output

Return the selected design, alternatives and rationale, affected components/contracts, risks,
recovery and verification impact. List any generated artifacts and include the document self-review
verdict when one was persisted. Absence of an optional artifact is not a failure.

## Does not own

Do not select the execution profile or business risk, request host approval, generate database design or plans
automatically, freeze a user approval state, schedule execution, or declare implementation complete.
