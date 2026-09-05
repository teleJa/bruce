# 测试计划：修复预算配置化

## 验收与前提

- AC-01：按用户要求，本仓库和配置模板的单问题修复预算为 5，Completion 整体预算为 10；二者从适用 `.bruce/config.yaml` 读取。
- AC-02：同一失败允许第 1–5 次完整修复，5 次后仍失败则不允许第 6 次；Completion 第 0 轮不消耗预算，允许第 1–10 次修复，第 11 次被阻止。
- AC-03：显式较小配置仍生效；新问题、批次交接、恢复执行不重置已有失败计数。局部/整体预算哪个先耗尽，哪个先约束相应工作。
- AC-04：L0 瞬态错误重试、Reviewer 等待和独立评审触发阈值不变；不修改历史已确认工件或引入自动执行 Runtime。
- 前置条件：现有 YAML 配置、声明式预算决策表、Python unittest 和插件刷新脚本。
- consistency_check: not_applicable；不涉及业务对象、权限或数据库关系。
- visual_scope: none；本次是工作流规则和配置调整，无产品页面变更。

## 场景：BUDGET-CONFIG-001

- Given: 本仓库/模板配置与当前预算文档、checkpoint 模板。
- When: 运行配置合同及恢复策略回归，并检查所有活跃规则中的旧硬编码。
- Then: 配置默认值、字段名称、范围和读取来源一致；L1 不再固定为 2 次，Completion 不再以 5 为缺省值；显式配置不得被默认值覆盖。
- 验证命令：`python3 -m unittest tests.test_bruce_config_contract tests.test_failure_policy tests.test_workflow_policy_contract`
- Evidence: 当前测试结果及 diff；这些是配置/声明式规则合同检查，不代表真实 Agent 已连续修复十轮。

## 场景：BUDGET-BOUNDARY-001

- Given: 从实际配置读取的两个上限，以及显式更小的配置示例；原始失败计数、当前 Completion 计数和阶段。
- When: 使用原有声明式决策表测试上限前、到达上限、越过上限、未知历史、恢复、批次与新问题。
- Then: 同一失败计数 0–4 可继续修复，5 及以上转 L2；整体计数 0–9 可继续，10 及以上不继续 Completion 修复；批次不消耗全局预算。不同配置的边界按实际值计算。
- 验证命令：同上。
- Evidence: 决策表输入/输出断言及测试退出码；不以测试内构造的决策执行器冒充宿主 Runtime。

## 场景：BUDGET-REGRESSION-001

- Given: 最终局部修改。
- When: 执行完整 unittest、插件校验、diff 检查，再刷新本地插件并核对修改文件的缓存哈希。
- Then: 相关和全量回归通过，L0/Reviewer 边界保持不变；新会话可以加载刷新后的规则。
- 验证命令：`python3 -m unittest discover -s tests -p 'test_*.py'`；`python3 scripts/validate_plugin.py .`；`git diff --check`；`python3 scripts/refresh_local_plugin.py /Users/tele/ai-workspace/bruce`。
- Evidence: 当前命令输出及源码/缓存 SHA-256 对比。

## 限制与回归

- 本文仅记录用户已明确要求的行为和现有检查命令，不引入另一个治理设计或任务包；Design Gate 不适用。
- 未经本轮授权，不提交或推送；不更新用户记忆，不修改评审等待次数。
