# 任务 T-002：更新测试契约与迁移检查

- 契约修订：1
- 契约状态：执行前冻结
- 状态来源：`../checkpoint.yaml`
- 父计划：`../plan.md`

## 目标

让现有 Bruce 测试锁定 Provider 配置、Provider 中立 visual scope、统一证据和 fail-closed 迁移规则。

## 包含范围

- `tests/test_bruce_config_contract.py`
- `tests/test_validation_loop_contract.py`
- `tests/test_completion_contract.py`
- `tests/test_supporting_skill_contracts.py`
- `tests/test_explore_prototype_contract.py`
- `tests/test_prototype_contract.py`

## 排除范围

- 不修改运行时 Provider。
- 不修改业务代码或外部环境。

## 依赖关系

- 依赖任务：T-001
- 使用：T-001 的配置与文档契约
- 产出：可重复的契约测试和兼容检查

## 业务不变量与权威状态（按适用性）

- 一致性检查：not_applicable
- 业务不变量与权威状态摘要：不涉及业务数据。
- 竞争者/权限视角与冲突后果：不适用。
- 关联测试计划矩阵/场景 ID：none
- 不适用原因：只验证静态配置/流程文本契约。

## 验收标准

- 父级场景 ID：AC-001、AC-002、AC-003、AC-004、AC-005
- Given：T-001 已更新配置和 Bruce 规则。
- When：执行针对性和全量契约测试。
- Then：新 Provider 契约通过，旧 Chrome scope 兼容规则被覆盖，现有无关契约不回归。
- Evidence：`python3 -m unittest discover -s tests -p 'test_*.py'`。

## 验证

- 必需层级：unit/contract
- 命令/检查：`python3 -m unittest discover -s tests -p 'test_*.py'`
- 环境：Python 3、PyYAML。

## 授权与风险

- 授权：normal
- 风险触发：guarded：契约测试是 Completion Gate 规则的回归保护。
- 停止条件：若测试暴露需要修改 runtime 或扩大到业务仓库，停止并返回检查点。

## 契约变更规则

不得静默扩大本任务范围。如果范围、验收、依赖、授权或所需验证层级发生变化，必须创建新的契约修订或替代任务，并在下一个检查点中记录原因。
