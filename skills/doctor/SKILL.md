---
name: doctor
description: Use only when the user explicitly asks for Bruce Doctor, execution-log auditing, or Codex thread audit; prepare read-only evidence without changing Bruce workflow state or deciding completion.
---

# Bruce Doctor

Bruce Doctor is an explicitly invoked, read-only diagnostic capability. It prepares a compact,
source-linked audit view from a Codex rollout JSONL log. It is not a third Bruce gate and must not
be selected for ordinary implementation, design review, testing, or completion work.

## Explicit invocation boundary

Invoke this skill only when the user explicitly names `doctor`, `Bruce Doctor`, execution-log
auditing, or asks to audit a Codex thread. Do not infer it from a long task, a Goal, a failed test,
or a request to use Bruce. Do not add or use a hook to invoke it automatically.

## Workflow

1. Resolve the requested `codex://threads/<id>` to one local rollout JSONL file using read-only
   inspection. If the user provides a path, use that exact file. Do not scan unrelated sessions.
2. Check whether the source is still growing. For a live source, pin an explicit `--until`
   timestamp to the last relevant task-complete record, or report that the snapshot is unstable.
3. Run `scripts/audit_codex_thread.py` in a user-selected or temporary output directory. The source
   is opened read-only, large text is spilled to indexed evidence files, and generated text is
   redacted using common credential patterns.
4. Read `inventory.json` and `timeline.md` first. Inspect only the evidence files needed to explain
   a finding. Preserve source line numbers and SHA-256 references in the report.
5. Report findings as `evidenced`, `incomplete`, `blocked`, or `unexecuted`. Keep designed,
   executed, passed, blocked, and unexecuted evidence separate.

## Output

Return:

- source path or thread id, snapshot boundary, line count, and source SHA-256;
- event/turn/time statistics and parsing errors;
- checkpoint-protocol statistics: valid/incomplete checkpoints, work-interval overruns, missing
  checkpoints, and clearly labelled suspected `update_plan` substitutions or single-finding churn;
- Bruce-specific findings with source line references;
- evidence coverage: designed, executed, passed, blocked, unexecuted;
- residual privacy and snapshot risks;
- the smallest next diagnostic action.

Doctor findings are diagnostic inputs only. Do not emit or change `Design: pass`,
`Completion: pass|issues|blocked`, or native Goal status on Doctor's authority. If a completion
decision is needed, hand the current evidence to `completion-gate`; if Goal persistence is needed,
hand the result to `goal-execution` according to its own explicit predicate.

## Does not own

Doctor does not own the main Bruce workflow, Design Gate, Completion Gate, Goal state,
`execute_record.md`, hooks, browser control, database/model execution, delivery actions, a second
authoritative evidence store, or a transcript mirror. It never mutates the source rollout, the
repository, or external runtime state.
