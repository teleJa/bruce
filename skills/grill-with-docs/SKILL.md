---
name: grill-with-docs
description: Use when a software task has multiple dependent domain, terminology, lifecycle, or scope decisions that repository evidence cannot settle, when durable domain documentation is needed, or when the user explicitly asks for a grilling session. Do not use for an isolated blocking ambiguity that Bruce can resolve with one direct question.
---

# Grill with docs

Resolve connected domain decisions without turning ordinary task clarification into an interview.

## Inputs

- The unresolved question and its effect on scope or acceptance.
- The current Bruce task contract when called by Bruce.
- Relevant code, `CONTEXT.md`, `CONTEXT-MAP.md`, ADRs, and repository documentation.
- The document language rule in [../bruce/references/document-language.md](../bruce/references/document-language.md).

## Procedure

1. Confirm that the work involves multiple dependent decisions, durable domain documentation, or an
   explicit grilling request. For one isolated blocking ambiguity, return control to Bruce so it can
   ask the question directly.
2. Inspect repository evidence before asking the user. Do not ask a question that code or docs can
   answer reliably.
3. Name the exact ambiguities, affected behavior, dependencies between decisions, and recommended
   interpretations.
4. Ask one focused question at a time through the dependent decisions.
5. Challenge inconsistent terminology and concrete lifecycle edge cases. Distinguish domain facts,
   current implementation, and a new decision.
6. Write natural-language content in the user's language, using Simplified Chinese for a Chinese
   request; preserve canonical terms, identifiers, and quoted source text.
7. Update durable docs only when requested or when the decision has lasting domain value:
   - use [CONTEXT-FORMAT.md](CONTEXT-FORMAT.md) for stable glossary terms;
   - use [ADR-FORMAT.md](ADR-FORMAT.md) only for hard-to-reverse, surprising trade-offs.
8. When files changed, inspect their diff, factual grounding, terminology/cross-reference
   consistency, omissions, placeholders, and links. Repair in-scope issues and return
   `Document check: clear|issues` with the checks performed.

## Output

Return the resolved terminology, decision dependencies, constraints, acceptance impact, remaining
unknowns, and any files explicitly updated. A chat answer is the default; do not create a
clarification artifact merely because the skill ran. Include the document-check result when
files changed.

## Does not own

Do not choose Bruce execution profile or risk, create workflow state, approve work, generate architecture or
plans, or invoke another supporting skill automatically.
