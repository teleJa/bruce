# 文件与命令合同

## 现有边界

提供方为 Bruce Skill 和 `scripts/workflow_behavior_fixture.py`；消费者为主 Agent、checkpoint 使用者、
`tests/test_workflow_behavior.py` 与显式运行 fixture 的评估者。仍采用现有宿主命令和人工语义评估，
不新增调度器、Gate、模型调用或权限代理。

## 测试设计与预算

`artifact-policy.md` 是测试计划适用性的唯一来源：行为变更必需，简单用最小模板，复杂按适用性展开。
原 `templates/test-plan.md` 路径保持兼容，增加 `test-plan-minimal.md`。生成文件仍叫 `test-plan.md`。
`failure-recovery.md` 是预算权威：L1 按稳定 failure_id 记录最多两次完整修复，复现同一错误不得改 ID。
`workflow.repair_loop.max_rounds` 保持 1..5、默认 5，仅限制一次 Completion Gate 的全局修复轮次。
批次仅受本地 L1/已声明较小预算限制；Completion 修复同时消耗本地和全局预算，先耗尽者优先停止。
现有 checkpoint 的 `findings` 行可增量携带 `failure_id`、`l1_repair_rounds` 和证据引用；
不增加顶层台账。旧 checkpoint 无计数时是未知，应先根据原证据恢复，不能默认为零。

## Fixture prepare/check

保持 v1 manifest 与现有 prepare/check CLI、退出码及 `needs_manual_review` 边界。
增加可选 `created` 相对文件白名单（旧 manifest 缺省为空），只允许场景明确声明的非空普通文件；
不允许绝对路径、父级越权或符号链接。修复场景允许并要求独立 `test-plan.md`，其语义由主 Agent 复核。
增加 `unknown_external_result`（只读，检查器不重放操作）和 `dirty_worktree`（冻结用户草稿）场景。
创建目录与清理仍由调用者掌控；冻结原测试和所有未授权文件/模式保持不变，执行前后均检查。

## 可选 summarize CLI

`summarize <input.json>` 读取显式指定的测量文件及内置场景表并输出 JSON；无递归发现、会话读取、网络、执行或写入。
输入是 `{version: 1, trials: [...]}`。每项包含唯一 `trial_id`、`workflow_revision`、`fixture_revision`、
已知 `scenario`、`source: native_actor|fixture_test`、`automated_checks_passed` 布尔值、
`manual_status: passed|failed|pending`、`evidence_refs` 字符串列表以及 `metrics` 对象。
人工完成复核必须有引用；引用由调用者提供，不冒充自动认证。
指标：elapsed_seconds、first_verification_seconds、planning_seconds、inspection_seconds、implementation_seconds、
verification_seconds 为非负有限数；tool_calls、repair_rounds、redundant_checks、user_interventions、
false_completion_claims、tokens 为非负整数；缺失或 null 表示未知，不能补零。
首次验证时间不得大于总耗时；阶段耗时使用互不重叠区间，总和不得大于总耗时。
时长比较仅允许相对 1e-12、绝对 0 的浮点舍入容差；零总耗时下任何正耗时仍拒绝。
按 workflow_revision、fixture_revision、scenario、source 分组，返回样本数、各指标观测数/均值、
人工复核覆盖数；只有 native_actor 的已复核记录计算 reviewed_pass_rate，pending 不作为通过。
空样本返回空分组。拒绝重复 ID、未知字段、非法类型/非有限数；合法汇总退出 0，输入错误退出 2。
自动检查通过不能变成 actor 成功、环境可用或 Completion verdict；fixture_test 永不计为真实 actor 成功。

## 恢复与验证

变更为本地可回退修改，无持久化迁移。回退代码/文档及刷新插件即可；旧 manifest 可继续检查。
参数化路由/预算合同测试、fixture 故障注入与 CLI 输入校验覆盖兼容性；详见 test-plan.md。
