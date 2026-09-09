---
name: write-architecture
description: Use when a software task needs an explicit structural decision, public or cross-component contract, component boundary design, or durable architecture handoff. Inspect the current repository, produce only the necessary architecture and contract artifacts, and keep implementation planning and approval outside this skill.
---

# Write architecture

Design only when the task needs a durable structural or contract decision.

## Artifact placement

Use the shared resolver in [artifact-placement.md](../bruce/references/artifact-placement.md). For a
cross-repository task, compare only the participating repositories' direct parent directories: if they
match, place the complete change package under that parent (using its `.bruce/config.yaml` when present);
if they differ, ask the user for the shared document path. Do not search higher ancestors or split one
design across repositories.

## Inputs

- Objective, scope, acceptance, constraints, execution profile, and known risk.
- Current repository components, toolchains, deployables, interfaces, and architecture conventions.
- Existing decisions or domain clarification when available.
- Prior `solution-analysis` findings and bounded `inspect-parallel` evidence; reuse valid evidence and
  investigate only architecture-specific gaps.
- The repository's documented convention and any existing change directory for the current task.
- The document language rule in [document-language.md](../bruce/references/document-language.md).

The complete fallback API contract path is
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

1. Consume existing analysis findings and identify only the facts needed to make the structural or
   contract decision. If new evidence is needed, use the shared `inspect-parallel` boundary and routing
   rules with the `inspector` Profile; do not repeat a completed repository survey or select a model/Runtime here. If a material
   fact remains unresolved, return the bounded evidence gap rather than inventing a boundary.
2. Separate the current implementation from the target design: record reusable existing capabilities,
   changed behavior, preserved behavior, new responsibilities, and unverified assumptions.
3. Identify architecture decisions and every public or cross-component API, event, or file-contract
   change. A single-component task may still require a contract artifact.
4. Define components from real ownership, build, deployment, or delivery boundaries. Do not turn
   internal layers into artificial components.
5. For applicable stateful, asynchronous, permissioned, or relationship-based behavior, define domain
   objects, state ownership/transitions, authoritative state, invariants, concurrency/retry/idempotency,
   and conflict/error semantics. Mark the dimension not_applicable with a reason when it does not apply.
6. Define each changed public or cross-component contract with provider, consumers, request or
   event shape, success/error behavior, authentication, compatibility, versioning, and verification.
7. Cover data flow, failure handling, rollout/rollback, observability, security, and verification in
   proportion to the decision. Do not use tests or the implementation plan to silently decide missing
   business rules, authority, or conflict semantics; return those as open decisions.
8. Generate `architecture.md` from [architecture.md](templates/architecture.md) only when a durable
   structural decision must be persisted or handed off. For every contract change described above,
   generate or update `api-contracts.md` from [api-contracts.md](templates/api-contracts.md) in the
   resolved artifact directory before behavior implementation begins.
9. Write natural-language content in the user's language, using Simplified Chinese for a Chinese
   request; preserve stable contract tokens, identifiers, paths, and protocol names.
10. When an artifact was persisted, inspect its diff, verify claims against repository evidence,
   check contracts and cross-document references, and remove material omissions, placeholders, and
   broken links. Repair issues and return `Document check: clear|issues`. When the artifact will
   govern implementation, return a mandatory `design-gate` handoff. Bruce/the caller must coalesce pending handoffs under
   [artifact-policy.md](../bruce/references/artifact-policy.md): finish the already authorized design
   batch's required artifacts and local checks; once ready, run one Gate in the same turn without another user instruction. A single-artifact batch runs the Gate immediately after its check. This writer does not own the Design verdict.

## Output

Return the selected design, alternatives and rationale, affected components/contracts, risks,
recovery and verification impact. List any generated artifacts and include the document author-check
check result when one was persisted. Absence of optional `architecture.md` is not a failure; absence of
required `api-contracts.md` is a blocking contract gap and must be returned to Bruce before
implementation.

## Does not own

Do not select the execution profile or business risk, request host approval, generate database design or plans
automatically, freeze a user approval state, schedule execution, or declare implementation complete.
The mandatory Design Gate handoff is the only automatic continuation; other supporting skills remain
predicate-driven.
