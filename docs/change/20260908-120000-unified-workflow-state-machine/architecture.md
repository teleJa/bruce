# 架构：统一 Bruce 工作流状态机

## 决策

增加一个任务级 `Workflow State Machine` 作为生命周期事实源，挂载在 requirement-level checkpoint 中。它不替换已有 Gate、Verification Run 或 Failure Policy，而是统一它们的生命周期位置和转移入口。

## 状态

```text
unresolved -> contracting -> designing -> design_ready
                                      \-> design_blocked
contracting -------------------------> implementing
 design_ready ------------------------> implementing
 implementing -> verifying
 verifying -> waiting_external | waiting_user | repairing | re_verifying | completion_review | blocked
 repairing -> re_verifying | blocked
 re_verifying -> verifying | repairing | completion_review | blocked
 waiting_external -> verifying | blocked
 waiting_user -> verifying | blocked
 completion_review -> completed | completion_issues | blocked
 completion_issues -> repairing | blocked
 active state -> paused -> previous active state
 design_blocked -> designing | blocked
 blocked -> recorded resume_state or an explicit recovery transition
```

`design_ready` 可以作为 `design-only` 的安全停止点；它不是 `Completion` 终态。只有完成实现授权后才能转入 `implementing`。

## 所有权边界

- 状态机：验证生命周期和事件转移，不产生业务或 Gate verdict。
- Design Gate：产生唯一 `Design: pass|blocked`，成功后允许进入 `design_ready`。
- Completion Gate：产生唯一 `Completion: pass|issues|blocked`，只有 `Completion: pass` 才允许进入 `completed`。
- Verification Run：记录一次验证执行的 stage、attempt、evidence 和外部等待；其状态映射到任务状态，但不能产生任务终态。
- Failure Policy：决定 L0-L4、retry、repair、replan 和 freeze；状态机只接收归一化事件。
- Checkpoint：持久化统一状态快照、证据引用和恢复条件，不是第二状态机。

## 持久化对象

```yaml
workflow_state:
  version: 1
  task_id: T-001
  state: unresolved
  state_revision: 0
  mode: implementation
  contract_revision: 1
  contract_frozen_revision: null
  basis_revision: <working-tree-or-commit>
  design_gate: pending|pass|blocked|not_required
  completion_result: null|pass|issues|blocked
  last_event: null
  stop_reason: null
  resume_state: null
  resume_conditions: []
```

每次合法事件使 `state_revision` 加一并记录 `last_event`。状态快照不得重置 repair round、failure_id、evidence revision 或 Profile revision。

## 与现有状态的映射

| 现有对象 | 现有状态 | 统一任务状态 |
|---|---|---|
| Checkpoint task | pending | contracting / implementing |
| Checkpoint task | in_progress | implementing / verifying |
| Checkpoint task | verifying | verifying / re_verifying |
| Checkpoint task | blocked | blocked |
| Verification Run | running/evaluating | verifying |
| Verification Run | waiting_external | waiting_external |
| Verification Run | waiting_user | waiting_user |
| Verification Run | repairing | repairing |
| Verification Run | re_verifying | re_verifying |
| Verification Run | passed | completion_review |
| Verification Run | paused | paused |
| Verification Run | blocked | blocked |
| Design Gate | pass | design_ready |
| Completion Gate | issues | completion_issues |
| Completion Gate | pass | completed |
| Completion Gate | blocked | blocked |

映射是单向归一化：子对象不能绕过状态机直接写入任务终态；Gate 仍保留最终裁决权。

## 旧 checkpoint 迁移

缺少 `workflow_state` 的历史 checkpoint 只作为证据输入，不能继续充当当前状态。下一次 material checkpoint 或 structured resume 必须基于冻结契约、当前工作区、Gate 结果、Verification Run、repair history 和外部状态显式建立 `state_revision: 0` 的快照。缺失或冲突证据保持 unknown/blocked，不从旧 task label 推断 `completed`。
