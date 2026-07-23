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
- The repository's documented convention and any existing change directory for the current task.

## Artifact placement

Resolve persisted architecture and contract artifacts in this order:

1. Use the repository's documented convention when it defines a location for the current change.
2. Otherwise, reuse the existing change directory for the current task when one already exists.
3. Otherwise, create `docs/change/<YYYYMMDD-HHmmss>-<short-slug>/` under the repository root.

Place `api-contracts.md` in the resolved directory. Place `architecture.md` beside it when an
architecture artifact is required. A user-requested path may override the fallback only when it does
not conflict with an applicable repository convention. The complete fallback API contract path is
`docs/change/<YYYYMMDD-HHmmss>-<short-slug>/api-contracts.md`.

## Mandatory API contract artifact

Every public or cross-component API, event, or file-contract change must generate or update
`api-contracts.md` before behavior implementation begins. This includes adding, removing,
deprecating, or changing routes, methods, RPCs, events, request or response fields, status or error
semantics, authentication or authorization, idempotency, compatibility, or versioning.

An existing OpenAPI, Proto, schema, or README may remain an authoritative source, but it does not
replace the change-scoped `api-contracts.md`. Link that source from the artifact and describe the
actual change. Purely private implementation changes with no observable contract effect do not
trigger this requirement.

## Procedure

1. Inspect the current repository with available Codex tools. Use a native subagent only when the
   exploration boundary is clear; otherwise inspect sequentially.
2. Identify architecture decisions and every public or cross-component API, event, or file-contract
   change. A single-component task may still require a contract artifact.
3. Define components from real ownership, build, deployment, or delivery boundaries. Do not turn
   internal layers into artificial components.
4. Define each changed public or cross-component contract with provider, consumers, request or
   event shape, success/error behavior, authentication, compatibility, versioning, and verification.
5. Cover data flow, failure handling, rollout/rollback, observability, security, and verification in
   proportion to the decision.
6. Generate `architecture.md` from [architecture.md](templates/architecture.md) only when a durable
   structural decision must be persisted or handed off. For every contract change described above,
   generate or update `api-contracts.md` from [api-contracts.md](templates/api-contracts.md) in the
   resolved artifact directory before behavior implementation begins.
7. When an artifact was persisted, separately inspect its diff, verify claims against repository
   evidence, check contracts and cross-document references for consistency, and remove material
   omissions, unresolved placeholders, and broken links. Repair issues and return
   `Document self-review: pass|issues`. Flag D1 document readiness review when the artifact will
   govern downstream work; do not invoke another supporting skill automatically.

## Output

Return the selected design, alternatives and rationale, affected components/contracts, risks,
recovery and verification impact. List any generated artifacts and include the document self-review
verdict when one was persisted. Absence of optional `architecture.md` is not a failure; absence of
required `api-contracts.md` is a blocking contract gap and must be returned to Bruce before
implementation.

## Does not own

Do not select the execution profile or business risk, request host approval, generate database design or plans
automatically, freeze a user approval state, schedule execution, or declare implementation complete.
