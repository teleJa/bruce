# 测试计划：视觉检查与浏览器配置生成规则

## 验收与前提

- AC-01：测试生成规则及两种模板明确视觉判读；布局风险覆盖显示不全、溢出、遮挡、布局与视口/状态变化，不把截图存在当作检查通过。
- AC-02：生成计划读取适用 Bruce 配置的 `verification.browser_provider`，未配置默认 `ego-lite`；显式 `chrome` 得到保留，非法配置与证据不匹配不降级。
- AC-03：执行与完成检查引用同一视觉清单，不修改运行时 evidence schema，不批量改写历史工件。
- 前提：仓库现有 Python unittest、插件校验与本地刷新脚本；本次只改生成指导、模板和回归测试。
- consistency_check: not_applicable；不涉及业务对象关系、权限或持久化。
- visual_scope: none；本次没有产品页面变更，验证规范内容和现有配置解析行为，不冒充实际网页视觉验收。

## 场景：VISUAL-001

- Given: 当前 write-tests 规则、最小/扩展模板、UI 验证与完成门禁。
- When: 运行文档合同回归并人工检查最终 diff 和相对链接。
- Then: 两种模板均指向可执行视觉清单；有适用性、明确 Then、截图判读和缺证据处理；smoke 不强制完整几何扫描，layout 不得省略布局检查。
- 验证命令：`python3 -m unittest tests.test_test_plan_visual_contract tests.test_browser_ui_verification_contract tests.test_browser_provider`
- Evidence: unittest 结果证明规则回归断言；最终 diff 人工检查证明范围、语义和消费链一致，不证明任意生成模型必然遵守。

## 场景：PROVIDER-001

- Given: 缺失配置/缺失字段、显式 chrome、非法 Provider、历史 scope 与 Provider 不匹配的现有配置解析场景。
- When: 运行同一回归命令及完整 unittest。
- Then: 未配置为 ego-lite，chrome 显式配置保留，旧 scope 不选择 Chrome；非法配置或不匹配拒绝；两种模板记录配置来源和解析值，不硬编码浏览器。
- 验证命令：`python3 -m unittest discover -s tests -p 'test_*.py'`
- Evidence: 当前命令退出码与测试结果；配置解析通过不代表浏览器能力预检通过。

## 场景：PLUGIN-001

- Given: 最终局部改动，无根配置、依赖或历史计划变更。
- When: 执行 `python3 scripts/validate_plugin.py .`、`git diff --check`，再执行 `python3 scripts/refresh_local_plugin.py /Users/tele/ai-workspace/bruce`。
- Then: 插件结构有效，diff 无空白错误；刷新结果可核对，新会话加载新插件。
- Evidence: 实际校验与刷新输出；当前会话不声称已经重新加载新缓存。

## 限制与回归

- 不运行真实网页验收，不修改现有浏览器配置，不修改历史已确认测试计划。
- 本文仅为本次已有检查命令与验收断言的执行清单，不新增架构/公共 schema 或下游设计决策；Design Gate 不适用。
