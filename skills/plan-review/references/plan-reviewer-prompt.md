# Plan reviewer prompt

Use this prompt for the mandatory independent review whenever `plan-review` is invoked. Start a fresh
Codex-native reviewer with `fork_turns="none"` or equivalent clean context, without author history.
Use the shared `reviewer` Functional Agent Profile and pre-dispatch routing gate (`fallback: blocked`). If any selected model is unavailable or unconfirmed, pause the affected review
and ask the user to explicitly name an available replacement; confirm host capability before dispatch.
Missing native subagent or clean context also blocks. Do not automatically switch models, inherit the
current model, or substitute main-agent self-review.

Provide objective, acceptance, the raw plan final diff or immutable snapshot, raw repository evidence,
necessary constraints, and only artifacts explicitly referenced by the plan. Do not provide the
author's rationale, confidence, or proposed conclusion. For repairs affecting reviewed evidence,
send the new snapshot to the original reviewer for re-review; do not replace re-review with the
main agent's confirmation. The original reviewer may continue without a fresh agent each time.

```text
Review the supplied implementation plan for execution readiness. Do not polish wording and do not
approve or execute it. Return findings only to the caller, never a terminal verdict.

Check:
- objective, scope, and acceptance coverage;
- task ids, dependency existence and cycles;
- file ownership and parallel-safety claims;
- exact interface and contract joins;
- whether each task is executable from real paths, APIs, and commands;
- material migration, recovery, external-side-effect, and verification gaps;
- referenced test coverage when a test design is actually supplied.

Do not require optional artifacts that the plan does not reference. Classify only problems that can
cause wrong implementation, unsafe execution, blocked work, or unverifiable acceptance as blocking.
Do not ignore unresolved blocking findings on re-review; check repairs against the new snapshot.

Return the shared v1 review_packet, not a new schema:
- status: completed|blocked|failed (execution status, not a verdict)
- output_type: review_packet
- review_subject: plan
- review_mode: independent
- review_mode_reason: mandatory-independent-review, or an applicable shared explicit-request/risk
  reason; never none
- review_basis: caller-provided task_id, actual native dispatch_id, and immutable current basis_revision
  (sha256 snapshot); return the basis actually reviewed, never invent an id or reuse a pre-repair hash
- findings: severity, path, evidence, and issue; include execution impact and smallest correction
  in the issue, and distinguish blocking issues from non-blocking advice
- review_matrix: acceptance_id, path, required_layer, evidence, result; identify the inspected
  snapshot and unverified facts; completed requires non-empty coverage of the reviewed basis
- model_resolution: actual shared routing evidence; completed requires resolved, never fallback
- gate_verdict: absent

Do not return Clean, Issues Found, Design, Completion, verdict, or approval. Only the caller forms
Clean or Issues Found from a valid completed independent packet; blocked or incomplete review cannot
be reported as Clean.
```
