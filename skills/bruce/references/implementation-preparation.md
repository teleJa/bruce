# Implementation preparation and evidence reuse

This is guidance for authorized implementation, not a timer, runtime, new Gate, or Packet schema.
It applies to the parent, direct execution, same-model workers, and cross-model workers. Analysis-only
and design-only requests retain their own scope; this rule never authorizes implementation.

## 1. Stop at the first safe slice

Reuse the confirmed design and available repository evidence. Read applicable instructions and check
workspace identity and unrelated changes first. List only unresolved facts that block the next slice,
with an acceptance id or direct call site for each. Do not enumerate speculative adjacent concerns.

Preparation is sufficient when the next slice has:

- current authorization, required design readiness, and resolved profile/task-contract prerequisites;
- a concrete acceptance outcome, allowed/excluded paths, and preserved dirty-worktree boundaries;
- known entry points, interfaces, dependency preconditions, and applicable conventions;
- an exact first edit or focused test target plus its verification command;
- no unresolved fact that could make that slice unsafe or invalidate its contract.

Start that slice immediately once these conditions hold, even before the investigation budget is used.
A slice need not be a complete feature, but cannot bypass an unresolved shared contract or dependency.
Do not delay ready work for full call-graph coverage, all locales, unrelated platform rules, or future
CNB/browser/deployment details. Resolve external authorization and environment prerequisites before
crossing their boundary; investigate earlier only when they constrain the implementation itself.

## 2. Bound missing-fact investigation

Default to at most two focused evidence rounds before the first edit or implementation dispatch.
A round is one bounded set of queries for the listed blockers followed by a readiness decision, not
an individual tool call. Parallel shards share the parent's round; delegation or a new worker cannot
reset already consumed investigation for the same gap. Do not disguise an open-ended scan as one round.
A narrower existing handoff budget wins; do not create config to obtain this default.

After each round, choose: start the ready slice; inspect only named remaining blockers; or stop the
affected slice with the precise missing fact. Non-blocking questions become deferred work, not new
entry requirements. At the limit, one additional bounded round is allowed only with the named blocker,
new evidence expected, concrete queries, and stop condition stated in progress/the current handoff.
If it remains unresolved, report that boundary and continue independent ready work when authorized;
do not silently renew the budget or claim implementation started while still only inspecting.

The limit never permits unsafe edits, skipped mandatory instructions, missing authority, or fabricated
facts. If mandatory checks cannot finish within it, report the actual missing check and affected slice
instead of opening broader investigation or asking the user to reconfirm already granted authority.
Read a relevant source window rather than whole documents repeatedly. If output is truncated, read only
the missing relevant range. Do not rescan global memory or all repository rules to rediscover known facts.

## 3. Carry facts, not only reading lists

Before every implementation dispatch, supply this compact handoff in the existing task context:

- Frozen scope, acceptance ids, allowed/excluded paths, dependencies, and prohibited side effects.
- Already verified findings: concrete behavior, path/symbol or document section, and source basis.
  Use the observed revision plus affected working-tree diff/content identity where applicable;
  HEAD alone does not cover dirty or untracked sources. Mark assumptions and unavailable sources unknown.
- Applicable rule findings and their source references, without treating a summary as a rule override.
- Executor-only gaps: exact question, why it blocks, and the smallest check; use "none" when absent.
- First edit/test target, focused verification commands, consumed/remaining investigation, and stop rule.

Use `task_packet.objective` for the concise scope, facts/basis, gaps, first action, and remaining budget;
`context.sources` for supporting repository paths or evidence ids; `evidence.required` for verification;
and `stop_conditions` for the investigation and safety limits. Keep `allowed_paths` and other existing
v1 fields intact. No new required field or persistent handoff artifact is introduced. If a durable
execution handoff already exists, cite its relevant section and supply only missing or changed facts.
`fork_context=true`, a file inventory, or "read current source" does not substitute for this handoff.

For older handoffs, recover missing budget consumption only when more investigation is needed.
If no investigation gaps remain and safety prerequisites are confirmed, keep missing consumption
unknown and proceed directly to editing or verification with no additional investigation or extension
allowance. Budget bookkeeping must not block a ready safe slice or skip current-source safety checks.
Unknown is not zero; a later blocking gap still requires budget reconciliation before further discovery.

## 4. Executor startup is a delta check

Consume the handoff as the slice contract; do not restart the top-level Bruce discovery workflow.
Confirm applicable current instructions, repository/worktree identity and dirty state, inspect exact
source to be edited, and resolve only executor-only gaps. Reuse unchanged findings; do not reread the
entire design package, full memory registry, or unrelated rules solely because a new agent started.

If basis is stale, contradictory, missing, or inaccessible, reopen only the affected fact and its direct
dependencies. A changed HEAD alone is not a reason to repeat unaffected inspection; determine whether
the cited scope changed. Newly applicable instructions and changed user constraints take precedence.
Never trust a handoff summary over current source or mandatory rules. If a gap invalidates the slice's
contract, return the bounded conflict rather than silently redesigning it. Otherwise proceed to the
first edit/test and report remaining non-blocking questions with the result.

The main agent works on non-overlapping integration or ready slices while a worker runs. It does not
repeat the worker's active investigation as a precaution. Integrate and verify the actual returned diff.
Independent reviewers retain clean context and raw-evidence review; this rule cannot transfer author
approval to a reviewer or turn inspection/design evidence into execution/test success.

## Compact v1 example

Illustrative paths and basis below must be replaced with observed task evidence; they are not facts
about the current repository. The schema validator checks shape, not truth or agent compliance.

```yaml
schema_version: 1
profile_id: implementer
task_packet:
  task_id: project-picker
  task_kind: implement
  objective: |
    范围：仅修复选择器跨分类保留选择，禁止修改 API 和移动端。
    已核实：src/picker.ts 的 toggleSelection 保留其他分类；缺陷在容器重置草稿。
    依据：父线程已读 src/picker.ts 的 toggleSelection 及容器调用点；派发时附实际内容哈希。
    规则：AGENTS.md 要求保留未知资源 ID；执行者复核当前适用规则和工作区。
    待查：容器的 focused test 是否已有关闭重开 fixture；仅查 tests/picker.test.ts。
    首步：读取待编辑容器和 fixture，增加跨分类回归断言，再修复容器草稿重置。
    预算：父线程已用 1 轮；本缺口剩余 1 轮，不能重新全量调查。
  context:
    inherit: task
    sources: [AGENTS.md, src/picker.ts, tests/picker.test.ts]
  tools:
    allow: [read, write, edit, test]
    deny: [deploy, push]
  allowed_paths: [src/picker.ts, tests/picker.test.ts]
  model_capabilities:
    required: [bounded-editing, test-execution]
    preferred: [repository-context]
    independence: none
  evidence:
    acceptance_ids: [AC-1]
    required: ["pnpm test -- tests/picker.test.ts; report exit code and changed paths"]
  output: task_evidence_packet
  stop_conditions:
    - 当前规则、源码或脏工作区与交接冲突时只核查受影响事实，不自行扩大范围。
    - 缺口耗尽剩余轮次仍未解决时报告受影响边界；最多一次具名的有界补查，不跳过安全前提。
```
