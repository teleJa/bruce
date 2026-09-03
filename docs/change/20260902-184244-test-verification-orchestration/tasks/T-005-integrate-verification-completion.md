# 任务 T-005：接入 Verification Profile、Loop 与 Completion Gate

- 契约修订：1
- 契约状态：执行前冻结
- 状态来源：`../checkpoint.yaml`
- 父计划：`../plan.md`

## 目标

让 Requirement Verification Profile 能选择三个测试 Skill，并让 Verification Loop/Completion Gate 消费场景轨道结果和 evidence revision，同时保持静态 Profile、运行状态和唯一 Completion authority 分离。

## 包含范围

- `skills/verification-profile/SKILL.md`、schema/template 的 Skill/Scenario/Track 映射增量。
- `skills/bruce/references/verification-loop.md` 和 `skills/completion-gate/SKILL.md` 的轨道结果消费规则。
- 对应 Verification Profile、Validation Loop、Completion 契约测试。

## 排除范围

- 不修改 Environment Profile/Operations 当前 schema 或执行器。
- 不改变 Functional Agent registry/resolver、Browser Provider 脚本或 Completion verdict 集合。
- 不覆盖当前工作区已有 Environment/Verification Profile 修改；发生语义冲突时停止并修订合同。

## 依赖关系

- 依赖任务：T-004
- 使用：三个测试 Skill、Scenario/Track Result、现有 `skill_selections`、Verification Run/Checkpoint、Completion review matrix
- 产出：Acceptance 到 environment/account/scenario/track/skill/evidence 的静态映射和运行结果消费规则

## 业务不变量与权威状态（按适用性）

- 一致性检查：required
- 业务不变量与权威状态摘要：Requirement Verification Profile 只描述策略和引用，不保存当前账号实例、运行状态或证据；Checkpoint/Run 保存动态结果；Completion Gate 独占最终判断。
- 竞争者/权限视角与冲突后果：Profile revision、Scenario version、basis/evidence revision 可能不同步；任何 stale 或缺失映射保持 incomplete/blocked，不能合并为 passed。
- 关联测试计划矩阵/场景 ID：CONS-004、CONS-S-004、PROFILE-001、COMPLETION-001
- 不适用原因：not_applicable

## 验收标准

- 父级场景 ID：TVO-06、TVO-07
- Given：已确认 Environment Profile、Requirement Acceptance 和不同状态/新鲜度的轨道结果
- When：生成 Verification Profile 并由 Loop/Gate 消费
- Then：静态映射完整，动态结果不回写 Profile，stale/缺证据/Provider unavailable fail-closed，轨道 status 不生成平行 Completion
- Evidence：定向 contract tests、schema/template 断言和 Completion review matrix 检查

## 验证

- 必需层级：integration/contract
- 命令/检查：`python3 -m unittest tests.test_verification_profile_contract tests.test_validation_loop_contract tests.test_completion_contract`
- 环境：静态仓库检查；真实 Environment/Profile/浏览器运行由后续项目任务验证

## 授权与风险

- 授权：normal
- 风险触发：guarded；触及当前已有未提交 Verification Profile 内容和 Gate evidence semantics
- 停止条件：现有 dirty diff 与新合同冲突、需要重写 Environment Profile schema、或会形成第二个运行状态/Completion 来源时停止

## 契约变更规则

不得静默扩大本任务范围。如果范围、验收、依赖、授权或所需验证层级发生变化，必须创建新的契约修订或替代任务，并在下一个检查点中记录原因。
