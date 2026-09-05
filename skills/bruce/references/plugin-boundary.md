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

## Optional native Goal boundary

Only when the user explicitly requests native Goal does `goal-execution` adapt its host-owned lifecycle
to existing Bruce evidence. Profile, duration, cross-turn recovery, audit needs, and ordinary continuation
do not activate it. Ordinary execution, checkpoint recovery, and delegation do not require Goal tools.
The adapter consumes the owning Gates' results without re-evaluating them and honors host pause,
cancellation, permissions, and budget limits. Native Goal state is never inferred from local files.

Do not create a Goal-specific audit record by default. A durable audit record is user-requested and
should reference existing task progress and evidence, not mirror them. Historical
`.goal/<goal-id>/execute_record.md` files remain optional references, not resume prerequisites.

## Approval versus business decision

A Codex host approval is an execution boundary. Obey its result and never create a second approval
record. If approval is denied, use an already-authorized alternative when one exists; otherwise
report the affected task as blocked.

A Bruce business decision is needed only when repository evidence cannot resolve scope, acceptance,
public-contract intent, or material business consequences. Ask one precise question and pause only
the dependent work.

Do not read, set, or attest a host sandbox mode. Do not generate permission hashes, grants, or
decision packages. Obey host results directly.
