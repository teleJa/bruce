---
name: verify-completion
description: Use when guarded or critical Bruce work reaches completion, when the user asks for a completion review, or when a separate evidence-based pass is needed before claiming a software task is done. Use a structured main-agent second pass for ordinary guarded work, and prefer an independent Codex-native reviewer for broad guarded work, critical work, or an explicitly requested independent review.
---

# Verify completion

Review current evidence rather than agent confidence or historical artifacts.

## Inputs

- Current objective, scope, acceptance, constraints, execution profile, and risk.
- Actual `git status`/diff or equivalent workspace changes, including pre-existing unrelated changes.
- Current test, lint, build, page, integration, or external-tool results.
- Current C0 code self-review and Given/When/Then acceptance-to-evidence mapping when code or runtime
  behavior changed.
- Current D0 document self-review and required D1 gate results when documentation changed.
- The resolved `api-contracts.md` path and current contract-to-diff mapping for every public or
  cross-component contract change.
- L0-L4 failures, open decisions, residual risks, and requested delivery actions.

## Procedure

1. Compare the actual change set with objective and scope. Identify unexplained out-of-scope changes
   and distinguish them from pre-existing user work.
2. Map every acceptance item to current, reproducible evidence. Treat missing, stale, mocked-only,
   or natural-language evidence as a gap when the acceptance requires more.
3. For behavior changes, verify concrete Given/When/Then scenarios and confirm the evidence layer
   matches each `Then`. A unit test does not prove a required integration or user-visible flow.
   Require current Codex App Chrome evidence for user-visible Web acceptance; when Chrome was
   required but unavailable, keep the scenario incomplete and reject a silent Playwright fallback.
4. When code changed, require C0 `pass` after the final code change. If verification entered an L1
   repair loop, require evidence that the unchanged original scenario and related regressions passed
   after repair. Never demand a replay that violates an unresolved L3/L4 boundary.
5. Check risk-proportional verification, migration/recovery evidence, external side effects, and
   unresolved L2/L3/L4 conditions.
6. Confirm requested delivery actions were authorized and completed, or clearly remain outside the
   completed boundary.
7. Inspect the actual change set for any public or cross-component API, event, or file-contract
   change. Require `api-contracts.md` at the location resolved by `write-architecture`, and verify it
   covers the provider, consumers, changed shape or semantics, compatibility, authentication,
   errors, and verification. If the artifact is missing, stale, or does not cover the actual contract diff,
   return `issues`; an OpenAPI, Proto, schema, or README alone does not satisfy this change artifact.
8. When documentation changed, require a current D0 `pass`. Also require a current D1 `通过`, or an
   explicitly authorized and recorded `有条件通过`, for important or downstream-governing documents.
   When `plan-review` substituted for D1, accept `Clean` as `通过` and treat `Issues Found` as
   `不通过`. Treat a missing required review, D0 `issues`, or D1 `不通过` as a completion issue.
9. Return one verdict:
   - `pass`: scope and every acceptance item have sufficient current evidence;
   - `issues`: repairable scope or evidence gaps remain;
   - `blocked`: authority, external state, or an unresolved L2/L3/L4 prevents completion.
10. Select the review mode proportionally:
   - ordinary guarded work: perform a separated pass and label it `main-agent-second-pass`;
   - broad guarded work spanning multiple components/contracts, combining migration and rollout, or
     carrying a broad security/data blast radius: prefer a fresh Codex-native subagent;
   - critical work or an explicitly requested independent review: require a fresh Codex-native
     reviewer; if unavailable, return `blocked` and do not present a main-agent fallback as
     independent.

## Output

Return review mode, verdict, scenario-level acceptance-to-evidence mapping, C0 result, API contract
artifact path and coverage result, scope findings, verification and repair-loop results, unresolved
risks, and the smallest next action. Keep the result in the current task by default; persist a review
artifact only when the user explicitly requests one.

## Does not own

Do not modify implementation, fabricate evidence, infer completion from an agent saying `done`,
approve host permissions, maintain evidence hashes or workflow state, or execute delivery actions.
