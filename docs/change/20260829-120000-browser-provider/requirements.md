# 需求：可配置浏览器验证提供者

## 目标

Bruce 的用户可见 Web 验收不再在流程语义上固定绑定 Chrome。任务从 `.bruce/config.yaml` 读取 `verification.browser_provider`，由选定的浏览器提供者执行页面交互、可见状态观察、截图以及布局证据采集；默认提供者为 `ego-lite`。

## 范围

- 在现有 `.bruce/config.yaml` 和配置模板中增加 `verification.browser_provider`。
- 支持 `ego-lite` 与 `chrome` 两个受控 Provider 标识。
- 将 `visual_scope` 的验收语义改为 Provider 中立的 `browser-smoke` 与 `browser-layout`。
- 让 verification loop、prototype 相关规则和 Completion Gate 按配置的 Provider 要求和记录证据。
- Provider 不可用、配置非法或能力不足时保持 `incomplete`/`blocked`，不得静默切换。

## 非范围

- 不实现 ego-lite 或 Chrome 的底层运行时。
- 不修改业务 UI、后端 API、数据库或持久化结构。
- 不实现自动 fallback、Provider 排序或任意命令注入。
- 不改变 Design Gate、Completion Gate 的唯一裁决权。
- 不把静态 DOM、原型截图或 Provider 质量评分提升为运行时视觉证据。

## 验收场景

### AC-001 配置默认值

- Given：工作区存在 `.bruce/config.yaml`，未显式配置浏览器提供者。
- When：Bruce 解析验证配置。
- Then：有效默认值为 `ego-lite`，配置模板和现有工作区配置保持一致。
- Evidence：`python3 -m unittest tests.test_bruce_config_contract tests.test_browser_provider` 读取并解析 `.bruce/config.yaml` 与 `skills/bruce/templates/config.yaml`。

### AC-002 Provider 选择

- Given：任务声明 `visual_scope=browser-smoke` 或 `browser-layout`，配置选择 `ego-lite` 或 `chrome`。
- When：执行浏览器验证前置检查和验证流程。
- Then：流程使用且记录配置的 Provider；不把未配置的 Provider 当作实际证据来源。
- Evidence：`tests/test_browser_provider.py`、验证循环契约测试、Completion Gate 契约测试和 Provider 证据格式检查。

### AC-003 Provider 中立的视觉范围

- Given：用户可见 Web 改动分别属于无布局影响和布局敏感影响。
- When：Bruce 解析任务合同并执行 Completion Gate。
- Then：分别使用 `browser-smoke` 和 `browser-layout`；`browser-layout` 要求截图、viewport、几何/overflow 与交互前后证据。
- Evidence：verification-loop、Completion Gate 和测试计划模板契约测试。

### AC-004 Fail-closed

- Given：Provider 标识非法、配置缺失且无默认可用值、Provider 前置检查不可用或缺少所需能力。
- When：Bruce 开始依赖浏览器的批次或 Completion Gate。
- Then：报告配置/能力问题，相关验收保持 `incomplete` 或 `blocked`，不得静默使用其他 Provider，也不得返回通过。
- Evidence：验证规则文本和失败策略测试。

### AC-005 兼容迁移

- Given：历史任务使用 `chrome-smoke` 或 `chrome-layout`。
- When：读取历史任务或更新模板。
- Then：旧名称仅作为兼容别名映射到 Provider 中立语义；新文档和模板使用 `browser-smoke`/`browser-layout`。
- Evidence：`tests/test_browser_provider.py` 的 scope 归一化测试和文档搜索检查。
