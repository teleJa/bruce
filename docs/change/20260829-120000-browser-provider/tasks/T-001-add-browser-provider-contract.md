# 任务 T-001：增加 Provider 配置与统一契约

- 契约修订：1
- 契约状态：执行前冻结
- 状态来源：`../checkpoint.yaml`
- 父计划：`../plan.md`

## 目标

将 Bruce 的浏览器验收从 Chrome 专属规则改为配置驱动的 `ego-lite`/`chrome` Provider 规则，默认 `ego-lite`，并定义统一证据和 fail-closed 语义。

## 包含范围

- `.bruce/config.yaml` 与配置模板。
- Bruce、verification loop、Completion Gate、prototype 和 test-plan 规则。
- `browser-smoke`/`browser-layout` 命名及历史 `chrome-*` 兼容映射。

## 排除范围

- 不实现浏览器 runtime、host API 或安装流程。
- 不修改业务 UI、API、数据库、部署和插件缓存。
- 不实现自动 fallback。

## 依赖关系

- 依赖任务：无
- 使用：`requirements.md`、`architecture.md`、`api-contracts.md`
- 产出：更新后的配置和 Bruce 验收契约

## 业务不变量与权威状态（按适用性）

- 一致性检查：not_applicable
- 业务不变量与权威状态摘要：不涉及业务持久化或跨对象状态。
- 竞争者/权限视角与冲突后果：不适用。
- 关联测试计划矩阵/场景 ID：none
- 不适用原因：只改变验证 Provider 和证据契约。

## 验收标准

- 父级场景 ID：AC-001、AC-002、AC-003、AC-004、AC-005
- Given：Bruce 当前配置和 Web 验收规则仍使用 YAML 与 Chrome 专属术语。
- When：增加 `verification.browser_provider`，将 scope 和证据规则 Provider 中立化。
- Then：默认 `ego-lite`，支持显式 `chrome`，按 Provider 执行并记录证据，非法/不可用时不 fallback，旧 scope 可解释。
- Evidence：`python3 -m unittest` 契约测试和定向文本检查。

## 验证

- 必需层级：unit/contract
- 命令/检查：`python3 -m unittest tests.test_bruce_config_contract tests.test_validation_loop_contract tests.test_completion_contract`
- 环境：Python 3、PyYAML；无需真实浏览器。

## 授权与风险

- 授权：normal
- 风险触发：guarded：改变正式 Web 验收环境与证据解释。
- 停止条件：若发现 Provider runtime 或外部宿主 API 需要新增实现，停止并返回检查点，不扩展本任务。

## 契约变更规则

不得静默扩大本任务范围。如果范围、验收、依赖、授权或所需验证层级发生变化，必须创建新的契约修订或替代任务，并在下一个检查点中记录原因。
