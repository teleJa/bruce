---
name: explore-prototype
description: >
  Use when a user wants a throwaway prototype to answer one unresolved design question: whether
  business logic, a state model, or a data shape behaves correctly, or which of several structurally
  different UI approaches fits an existing product surface. Build a bounded logic demo or UI-variant
  exploration, optionally delegate generation to one native subagent after the question and file
  boundary are frozen, and keep the result outside production and formal prototype readiness.
---

# Explore prototype

Answer one question with disposable code. Do not use this skill merely because a task changes UI, or
when a confirmed implementation-governing prototype is already required; use `write-prototype` for
the latter.

This method is adapted from Matt Pocock's Prototype skill. Read
[source-attribution.md](references/source-attribution.md) for provenance and license information.

## Inputs

- One concrete `prototype_question` and the decision it may change.
- Objective, scope, constraints, profile, risk, allowed/excluded paths, and dirty-worktree facts.
- Current repository entry points, components, data shapes, theme/style system, and runtime evidence
  required to keep the exploration realistic.
- The expected scenarios or variants and one direct way to run the result.
- The document language rule in [document-language.md](../bruce/references/document-language.md) when
  persisting a question, decision, or handoff note. For a Chinese request, use Simplified Chinese for
  natural-language content while preserving paths, identifiers, statuses, and protocol tokens.

## Select exactly one mode

- `logic`: answer whether a state model, transition rule, API shape, or data transformation behaves
  correctly when exercised. Read [logic.md](references/logic.md).
- `ui-variants`: answer what an existing or proposed UI surface should look like by comparing two to
  five structurally different variants. Read [ui-variants.md](references/ui-variants.md).

If the question genuinely spans both modes, split it into two sequential questions. If the primary
question cannot be resolved from the request or repository facts, ask at most one blocking question.

## Generation delegation

Use one native subagent as a generation worker only when all of these facts are frozen. The worker uses the shared `implementer` Functional Agent Profile with `task_kind=throwaway_prototype`; its input is a v1 Task Packet and its Functional Agent result is a `task_evidence_packet`. The outer exploration Skill may wrap that evidence as its separate `prototype_evidence_packet`; this wrapper is not a fifth Functional Agent output. Do not reintroduce the legacy `generation_packet` as a separate Functional Agent output. It must not choose a model, create a Runtime, or return a Gate verdict.

- the exact question and selected mode;
- exclusive allowed paths and explicit excluded paths;
- repository facts the worker may treat as authoritative;
- complete scenarios or variant requirements;
- run instructions, observable checks, and prohibited side effects.

Build the worker Task Packet from those fields. Do not delegate product decisions,
scope changes, user confirmation, shared-file integration, production promotion, Design Gate, or
Completion Gate. Do not choose a provider-specific agent name, model, token budget, scheduler, worker
registry, or persistent execution mode.

After the worker returns, the outer exploration Skill may wrap its task evidence as a `prototype_evidence_packet` with:

- `status: generated|needs-input|failed`;
- changed files;
- commands or actions actually run and their outcomes;
- assumptions and evidence gaps;
- the specific user feedback still needed.

Inspect the actual workspace diff and rerun proportionate checks after the worker returns. A worker's
`generated` statement is not acceptance evidence. If native subagents are unavailable, the paths
overlap, or the packet cannot be frozen without hidden context, generate sequentially in the main
agent; unavailable delegation alone never blocks the prototype.

## Shared procedure

1. State the question visibly in the prototype and keep every element relevant to answering it.
2. Place the throwaway code near its real host module or page, following repository conventions and
   using an unmistakable `prototype` name. Preserve unrelated files.
3. Keep state in memory and external effects stubbed unless persistence itself is the question. Never
   use production credentials, services, mutations, or data.
4. Make the prototype trivial to run: one self-contained HTML file for `logic`, or one existing
   project command and shareable variant URL for `ui-variants`.
5. Run the declared checks. For a visible Web result, use the browser Provider selected by
   `verification.browser_provider`; do not silently substitute another Provider or use undocumented
   fallback evidence.
6. Ask the user to exercise the exact question. Record `answered`, `needs-iteration`, or
   `inconclusive`, plus the observation and decision.
7. Remove the throwaway code from the production change when the question is answered. Preserve it
   outside the production branch only when the user requests archival and authorizes the Git action.

## Promotion boundary

Exploration code is never an implementation-governing UI prototype by itself. If the result must
govern production UI, pass the chosen decision and relevant artifact through `write-prototype` as an
imported or regenerated candidate so it receives grounding, Safety, Visual, Functional, Provenance,
generated/confirmed snapshot, manifest, and explicit confirmation checks. Only that confirmed result
may enter Design Gate.

Validated logic may inform production implementation, but rewrite it under the target repository's
normal quality, test, error-handling, and integration requirements. Do not copy the demo shell into
production.

## Output

Return:

```text
status: answered | needs-iteration | inconclusive
question: <exact question>
mode: logic | ui-variants
delegation: main-agent | native-subagent
artifact_paths: <throwaway paths>
run_instructions: <one direct action or command>
verification: <actual checks and outcomes>
observations: <what the prototype demonstrated>
decision: <validated answer or none>
production_promotion: not-promoted | requires-write-prototype
known_gaps: <remaining uncertainty>
```

## Does not own

Do not generate a formal Open Design artifact, create a prototype manifest, make product decisions,
modify production behavior, add persistence or real backend integration, manage subagent runtime,
approve design readiness, or declare delivery complete. Do not invoke another supporting skill
automatically.
