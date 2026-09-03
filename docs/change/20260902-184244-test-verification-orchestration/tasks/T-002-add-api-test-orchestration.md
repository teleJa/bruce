# 任务 T-002：增加通用 API 编排验证 Skill

- 契约修订：1
- 契约状态：执行前冻结
- 状态来源：`../checkpoint.yaml`
- 父计划：`../plan.md`

## 目标

新增项目无关的 `api-test-orchestration` Skill，将用户业务流转换为可生成、执行和取证的 API 状态编排测试，同时严格区分三种执行模式和证据边界。

## 包含范围

- `skills/api-test-orchestration/SKILL.md`、`agents/openai.yaml` 和本 Skill 自有 references。
- 路由/服务/仓储/Job/持久化发现规则、场景消费、测试生成、bounded polling、负例/权限/幂等和脱敏证据规范。
- `tests/test_api_test_orchestration_contract.py`。

## 排除范围

- 不操作浏览器，不修改业务代码、shared contract、schema、migration、CI 或环境模板。
- 不猜测项目命令、endpoint、终态或 fixture；只消费项目证据和已确认 Environment operation。
- 不实现通用 HTTP runtime、数据库客户端或自有测试 DSL。

## 依赖关系

- 依赖任务：T-001
- 使用：Scenario v1、Environment Profile operation/authorization、项目现有测试约定
- 产出：可由 Test Dispatch/Verification Profile 选择的 API 验证 Skill 和证据边界

## 业务不变量与权威状态（按适用性）

- 一致性检查：required
- 业务不变量与权威状态摘要：Job created 不是终态；需要持久化的场景必须通过公共 API 或获准的只读数据库查询权威回读；memory-application 证据不得标记为 real-http/live-acceptance。
- 竞争者/权限视角与冲突后果：不同 actor、重复请求和并发/重试可能竞争同一资源；Skill 必须要求权限、幂等或冲突结果，而不是接受任意 2xx。
- 关联测试计划矩阵/场景 ID：CONS-002、CONS-S-002、API-001、API-002、API-003
- 不适用原因：not_applicable

## 验收标准

- 父级场景 ID：TVO-01、TVO-02
- Given：项目存在真实 route/test convention 和声明的执行 mode
- When：Agent 使用 Skill 定义/生成/执行 API 场景
- Then：请求顺序、变量传递、状态转换、bounded polling、负例、权限和权威回读均可追溯；无静默 mode 降级或虚假 passed
- Evidence：Skill contract tests、references 链接检查和三种 mode fixture 断言

## 验证

- 必需层级：contract/integration-design
- 命令/检查：`python3 -m unittest tests.test_api_test_orchestration_contract`
- 环境：仓库内静态测试；真实项目 API/数据库/Worker 在项目适配任务中验证

## 授权与风险

- 授权：normal；实际项目运行仍受 confirmed Environment Profile 约束
- 风险触发：guarded；错误 mode 或证据定义会造成虚假集成通过
- 停止条件：需要破坏性数据操作、生产访问、未声明命令或修改业务代码时停止

## 契约变更规则

不得静默扩大本任务范围。如果范围、验收、依赖、授权或所需验证层级发生变化，必须创建新的契约修订或替代任务，并在下一个检查点中记录原因。
