# Browser Provider

Bruce 使用 `verification.browser_provider` 选择执行用户可见 Web 验收的宿主浏览器。Provider 只负责真实页面操作和证据采集；Acceptance Scenario、Design Gate 与 Completion Gate 的职责不变。配置与 scope 归一化由 `scripts/browser_provider.py` 提供确定性解析，底层浏览器 runtime 仍由宿主提供。

## 配置

配置文件固定为 `<shared-direct-parent>/.bruce/config.yaml`。当前支持两个受控值：

```yaml
verification:
  browser_provider: ego-lite | chrome
```

未配置时默认使用 `ego-lite`。Provider 配置不授予登录、扩展、文件上传或敏感数据传输权限。使用 `python3 scripts/browser_provider.py --config .bruce/config.yaml --scope browser-smoke` 可检查解析结果和所需能力。

- `ego-lite`：使用 ego-browser 的隔离 task space；适合自动化、多步骤和重复交互。
- `chrome`：使用 Codex App Chrome capability 的用户当前 Chrome session；适合当前 Tab、Profile、扩展和用户会话相关验证。

非法 Provider 必须作为配置问题报告。Provider 不可用或能力不足时，相关验收保持 `incomplete` 或 `blocked`；不得静默切换另一个 Provider、降低 `visual_scope` 或声称通过。证据 Provider 与配置不一致时，`scripts/browser_provider.py` 必须拒绝该证据。

## Provider capability preflight

每个依赖浏览器的批次只在开始时做一次最小 read-only preflight，并记录：

- `capability`：选定 Provider 和所需能力；
- `target`：实际 URL 或运行目标；
- `check`：真实连接、导航、交互、可见状态和证据采集检查；
- `status=available|unavailable|unknown`；
- `dependent acceptance ids`。

能力要求按 visual scope 计算：

| Scope | Required capabilities |
|---|---|
| `browser-smoke` | navigate、real interaction、visible state、screenshot/artifact |
| `browser-layout` | `browser-smoke` 全部能力，加 viewport、geometry、overflow、before/after evidence |

配置存在、可执行文件存在或计划使用某个工具，不构成能力可用证据。

## 统一证据

Provider 输出必须映射到统一 `browser_evidence`，至少记录：

```yaml
browser_evidence:
  provider: ego-lite | chrome
  provider_version: available provider version or omitted
  target: URL or runtime target
  session: task-space or current-chrome-session metadata
  actions: real actions corresponding to When
  visible_result: observed result
  capture_time: timestamp
  basis_revision: revision
  screenshot_artifact: path or hash
  geometry: required for browser-layout
```

`browser-layout` 还必须记录相关元素几何、overflow 结果和交互前后状态。DOM 文本、静态测试、原型截图或 Provider 自身评分不能替代当前 Provider 的运行时视觉证据。

## Scope 命名与兼容

新任务使用 Provider 中立的：

- `visual_scope=none`
- `visual_scope=browser-smoke`
- `visual_scope=browser-layout`

历史 `chrome-smoke` 和 `chrome-layout` 映射为 `browser-smoke` 和 `browser-layout`，不改变证据强度。新文档不得生成 Chrome 专属 scope 名称。

## Provider 与证据权威

配置选择的是本次任务的实际执行 Provider。Evidence 必须记录同一个 Provider；ego-lite 的成功不能被记录成 Chrome 证据，反之亦然。Provider 是执行能力，不是第二个 verdict owner；最终结果仍只能由 Completion Gate 返回。
