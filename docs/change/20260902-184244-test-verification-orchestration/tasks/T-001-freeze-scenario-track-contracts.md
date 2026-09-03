# 任务 T-001：冻结共享 Scenario 与轨道结果契约

- 契约修订：1
- 契约状态：执行前冻结
- 状态来源：`../checkpoint.yaml`
- 父计划：`../plan.md`

## 目标

建立机器可校验的 Scenario v1、轨道输入/结果和状态聚合契约，使 API/UI Skill 与 Completion 集成使用同一字段、版本和失败语义。

## 包含范围

- `skills/test-dispatch/references/**` 中的 Scenario、Dispatch 和 Track Result 规范。
- `skills/test-dispatch/scripts/**` 中的有界场景校验和结果聚合脚本。
- `tests/test_test_dispatch_contract.py` 的 schema、冲突和聚合测试。

## 排除范围

- 不创建 `test-dispatch/SKILL.md`；不实现 API/UI 子 Skill。
- 不修改 Environment Profile、Functional Agent registry、Browser Provider 或 Completion Gate。
- 不引入项目路径、业务 endpoint、凭证、数据库 reset 或真实外部执行。

## 依赖关系

- 依赖任务：无
- 使用：`architecture.md`、`api-contracts.md`、现有 Verification Loop 状态词汇
- 产出：三个测试 Skill 共同消费的 Scenario/Track v1 文件契约和确定性校验入口

## 业务不变量与权威状态（按适用性）

- 一致性检查：required
- 业务不变量与权威状态摘要：同一业务验收的 API/UI 证据必须引用相同 `scenario_id + scenario_version`；不同版本、重复轨道、namespace 冲突或无完整证据的结果不能聚合为 passed。
- 竞争者/权限视角与冲突后果：API/UI 轨道是同一场景的独立证据生产者；任何一方不得覆盖另一方状态，失败/阻塞必须按固定优先级保留。
- 关联测试计划矩阵/场景 ID：CONS-001、CONS-S-001、SCENARIO-001、DISPATCH-001
- 不适用原因：not_applicable

## 验收标准

- 父级场景 ID：TVO-01、TVO-04、TVO-07
- Given：存在合法和非法 Scenario/Track Result fixtures
- When：运行 validator 和 aggregator
- Then：合法 v1 数据稳定通过；缺失 ID/version、API/UI 混用、namespace/版本冲突和不完整 passed fail-closed；状态优先级符合合同
- Evidence：`tests/test_test_dispatch_contract.py`、脚本退出码和 fixture 断言

## 验证

- 必需层级：unit/contract
- 命令/检查：`python3 -m unittest tests.test_test_dispatch_contract`
- 环境：仅 Python 与 PyYAML；不需要数据库、服务或浏览器

## 授权与风险

- 授权：normal
- 风险触发：guarded；公共 Scenario/Result 合同被多个 Skill 和 Gate 消费
- 停止条件：字段来源产生两套权威、需要改变 Completion ownership、或 schema 要求环境/凭证值时停止并修订架构

## 契约变更规则

不得静默扩大本任务范围。如果范围、验收、依赖、授权或所需验证层级发生变化，必须创建新的契约修订或替代任务，并在下一个检查点中记录原因。
