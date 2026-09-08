# 文件契约：统一 Bruce 工作流状态机

## Workflow State

```yaml
version: 1
workflow_state:
  task_id: T-001
  state: unresolved
  state_revision: 0
  mode: design_only|implementation
  contract_revision: 1
  contract_frozen_revision: null
  basis_revision: <working-tree-or-commit>
  design_gate: not_required|pending|pass|blocked
  completion_result: null|pass|issues|blocked
  last_event: null
  stop_reason: null
  resume_state: null
  resume_conditions: []
```

## Event

```yaml
version: 1
event:
  event_id: EV-0001
  type: contract_frozen
  actor: main-agent|user|design-gate|completion-gate|adapter|verifier
  from_state: contracting
  to_state: contracting
  basis_revision: <same-as-state>
  observed_at: <RFC3339>
  evidence_refs:
    - design-review.md
  metadata: {}
```

`from_state` 和 `to_state` 是可选的输入校验字段；状态机以当前快照为准，不接受事件伪造历史状态。`resume` 只能由用户触发，且持久化的 `last_event.resume_state` 必须等于实际恢复目标。未知事件、状态或不允许的转移必须 fail closed。

## Events

- `inspection_complete`
- `contract_frozen`
- `design_required`
- `design_passed`
- `design_blocked`
- `implementation_authorized`
- `implementation_complete`
- `verification_started`
- `external_wait`
- `user_wait`
- `verification_passed`
- `verification_failed`
- `repair_started`
- `repair_complete`
- `reverification_passed`
- `completion_started`
- `completion_passed`
- `completion_issues`
- `completion_blocked`
- `pause`
- `blocked`
- `resume`
- `design_only_stop`

`design_passed` 和 `design_blocked` 必须由 `actor=design-gate` 产生；`completion_passed`、`completion_issues` 和 `completion_blocked` 必须由 `actor=completion-gate` 产生；状态机验证事件来源和前置状态，但不代替 Gate。`contract_frozen` 只增加状态版本并保持 `contracting`，不能替代 `implementation_authorized`。

## Invariants

1. `state_revision` 只能递增。
2. `completed` 必须同时满足 `completion_result=pass`；任何其他完成结果不能进入 `completed`。
3. `design_ready` 必须有 `design_gate=pass`；设计不适用时从 `contracting` 经显式实现授权直接进入 `implementing`。
4. `blocked` 必须有 blocker/stop reason 和可执行的 resume 条件。
5. `waiting_external`、`waiting_user` 和 `paused` 不得映射为 `completed`。
6. `paused`/`blocked` 必须保留 `resume_state` 和 `stop_reason`，恢复后回到记录的安全状态。
7. 事件不得重置 repair round、failure history、evidence revision 或 profile revision。
