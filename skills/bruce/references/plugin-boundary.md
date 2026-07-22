# Codex and Bruce responsibility boundary

## Codex owns

- File, command, shell, app, MCP, and network execution.
- Filesystem and network restrictions plus host approval prompts.
- Task conversation, tool results, native plans, native Goal status, and subagent lifecycle.
- The authoritative working tree and actual external tool responses.

## Bruce owns

- The minimal task contract and proportional workflow route.
- `standard`/`full` execution profile and `low`/`guarded`/`critical` business risk.
- Selection of optional supporting skills.
- L0-L4 response to returned failures.
- Acceptance coverage and the evidence-backed completion decision.

## Goal audit boundary

For `full` by default, and for `standard` when the user explicitly requests Goal,
continuous/cross-turn, or auditable execution,
`goal-execution-gate` creates or resumes the native Goal and maintains
`.goal/<goal-id>/execute_record.md`. Native Goal remains the execution-state truth; the Markdown file
is the human audit source only. `spawn-execute` returns structured evidence to the gate and never
creates a second ledger or derives Goal status from the audit file.

## Approval versus business decision

A Codex host approval is an execution boundary. Obey its result and never create a second approval
record. If approval is denied, use an already-authorized alternative when one exists; otherwise
report the affected task as blocked.

A Bruce business decision is needed only when repository evidence cannot resolve scope, acceptance,
public-contract intent, or material business consequences. Ask one precise question and pause only
the dependent work.

Do not read, set, or attest a host sandbox mode. Do not generate permission hashes, grants, or
decision packages. The plugin consumes host results; it does not prove or replace them.
