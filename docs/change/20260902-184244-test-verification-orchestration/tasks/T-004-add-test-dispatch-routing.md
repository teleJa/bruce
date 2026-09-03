# 任务 T-004：增加测试轨道调度与模型路由约束

- 契约修订：1
- 契约状态：执行前冻结
- 状态来源：`../checkpoint.yaml`
- 父计划：`../plan.md`

## 目标

新增 `test-dispatch` Skill，统一锁定共享场景、选择 API/UI 轨道、隔离数据和写入范围、构造 Functional Agent Packet 并聚合结果，不产生第二个模型路由器或 Completion verdict。

## 包含范围

- `skills/test-dispatch/SKILL.md`、`agents/openai.yaml`、references 和 T-001 脚本的必要整合。
- api/ui/both 轨道选择、Scenario version 锁定、namespace/allowed paths 隔离、状态聚合和诊断升级边界。
- `tests/test_test_dispatch_contract.py`、`tests/test_functional_agent_profiles.py` 的路由约束。

## 排除范围

- 不修改四类 Functional Agent registry、resolver 实现或默认模型。
- 不引用 `gpt-5.6-sol`，不新增第五 Profile、Runtime、scheduler 或私有 `model-routing.md`。
- 不直接执行浏览器，不实现 API 子 Skill 的测试代码。

## 依赖关系

- 依赖任务：T-001、T-002、T-003
- 使用：Scenario/Track contract、API/UI Skill、Functional Agent v1 Packet/resolver
- 产出：唯一 Test Dispatch owner、轨道 Task Packet 和聚合结果规范

## 业务不变量与权威状态（按适用性）

- 一致性检查：required
- 业务不变量与权威状态摘要：同一场景版本内每个必需轨道只有一个结果；API/UI 数据 namespace 和写入路径不冲突；轨道 passed 不等于 Completion pass。
- 竞争者/权限视角与冲突后果：API/UI 子任务可能返回不同状态或版本；failed 优先于 blocked，blocked 优先于 passed，冲突版本保持 blocked。
- 关联测试计划矩阵/场景 ID：CONS-001、CONS-S-001、DISPATCH-001、DISPATCH-002、ROUTING-001
- 不适用原因：not_applicable

## 验收标准

- 父级场景 ID：TVO-04、TVO-05
- Given：不同轨道组合、模型可用性、版本/namespace/路径冲突和子代理请求
- When：Test Dispatch 构造 Packet 并聚合结果
- Then：所有 Subagent 先通过 Bruce resolver；无 Sol/私有 router/browser tool；场景和状态按固定规则 fail-closed
- Evidence：dispatcher/aggregator tests、Functional Agent tests 和定向仓库搜索

## 验证

- 必需层级：unit/contract
- 命令/检查：`python3 -m unittest tests.test_test_dispatch_contract tests.test_functional_agent_profiles`
- 环境：不需要真实 Subagent 或浏览器；真实模型生效证据在使用任务中单独报告

## 授权与风险

- 授权：normal
- 风险触发：guarded；错误路由或聚合会扩大工具权限或产生虚假整体状态
- 停止条件：需要修改 resolver/Profile 集合、传入 browser tool、引入 Sol 或创建第二个 verdict 时停止

## 契约变更规则

不得静默扩大本任务范围。如果范围、验收、依赖、授权或所需验证层级发生变化，必须创建新的契约修订或替代任务，并在下一个检查点中记录原因。
