# File and workflow contracts: Bruce 设计产物完整性门禁

## artifact-review-file-v1

- Change: `added`
- Provider: `artifact-review-gate`
- Consumers: Bruce 主入口、`goal-execution-gate`、`verify-completion`、人类审计者
- Authoritative source: 本文件；实现目标为 `skills/artifact-review-gate/SKILL.md` 和 `skills/artifact-review-gate/templates/artifact-review.md`
- Compatibility: additive artifact；对需要设计审计的任务是新的阻塞要求
- Authentication/authorization: 不涉及

### Input

```text
task contract
resolved change directory
repository-backed capability decisions
generated design artifact paths
current D0/D1 results
```

候选集合至少覆盖：

```text
requirement-or-clarification
architecture.md
api-contracts.md
table-design.md
plan.md
test-plan.md
```

每项必须分别标记适用性 `required|skipped` 和交付状态 `generated|skipped`，并包含实际路径或 repository-backed skip evidence。`required` 是适用性结论，`generated` 表示已存在且当前评审满足进入下游的要求；不得用 `skipped` 隐藏缺失的必需产物。

### Success result

```text
docs/change/<change>/artifact-review.md
Artifact gate: pass
```

文件至少包含任务与阶段、候选产物矩阵、D0/D1 结果、阻塞问题、证据边界和门禁结论。

### Errors and recovery

| Condition | Result | Retry/idempotency behavior |
|---|---|---|
| `artifact-review.md` 缺失 | 禁止进入行为实现 | 在同一 change 目录生成后重跑 |
| 候选项未列出 | `blocked` | 补齐候选集合后更新同一文件 |
| required 产物不存在、过期或未通过所需评审 | `blocked` | 修复或生成产物并重跑 D0/D1 和 artifact gate |
| skipped 没有仓库证据 | `blocked` | 增加可定位证据或将该项改为 required |
| 实现范围改变导致原判定失效 | 原 `pass` 失效 | 更新同一文件并重新放行 |

### Verification

- Provider: `tests/test_supporting_skill_contracts.py`
- Consumer: `tests/test_workflow_profiles.py`、`tests/test_execution_contract.py`、`tests/test_completion_contract.py`

## design-to-execution-gate-v1

- Change: `changed`
- Provider: Bruce 主入口
- Consumers: `goal-execution-gate` 和后续实现步骤
- Authoritative source: [`skills/bruce/SKILL.md`](../../../skills/bruce/SKILL.md)
- Compatibility: breaking governance change；设计审计适用时不能再仅凭对话或 `execute_record.md` 进入实现
- Authentication/authorization: 不涉及

### Input

```text
artifact-review path
Artifact gate: pass
current task scope
```

### Success result

```text
design phase -> artifact gate pass -> optional Goal execution phase -> behavior implementation
```

`execute_record.md` 可以引用门禁文件路径和结论，但不得复制或替代候选产物决策。

### Errors and recovery

| Condition | Result | Retry/idempotency behavior |
|---|---|---|
| full task 未生成门禁文件 | 不创建执行阶段 Goal，不开始行为实现 | 生成并通过门禁后继续 |
| standard task 生成了下游设计真源但无门禁文件 | 不开始行为实现 | 在同级目录补门禁 |
| Goal 记录包含跳过理由但同级门禁缺失 | 仍然阻塞 | 将决定迁移到 `artifact-review.md` 后继续 |
| completion 发现最终 diff 与门禁判定不一致 | 返回 `issues` | 更新设计产物和门禁，重新执行受影响验证 |

### Verification

- Provider: `tests/test_workflow_profiles.py`
- Consumer: `tests/test_execution_contract.py`、`tests/test_completion_contract.py`
