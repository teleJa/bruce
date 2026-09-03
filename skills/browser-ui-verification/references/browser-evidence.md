# Browser evidence contract

页面验收 evidence 必须来自本批次配置的同一个 Browser Provider。它是 Verification Run/Checkpoint 的动态证据引用，不是 Environment Profile 或 Requirement Verification Profile 的长期事实，也不是 Completion verdict。

## Provider-neutral visual scope

| `visual_scope` | 最低运行时证据 |
|---|---|
| `none` | 只有 Scenario 明确声明没有 material rendered outcome 时可用；不产生或声称 browser visual evidence。若场景需要页面证据，缺失/`none` 必须 `blocked`/`incomplete`。 |
| `browser-smoke` | 配置 Provider 的真实连接/导航、至少一个 real page action、动作后的 visible state、screenshot/artifact。 |
| `browser-layout` | `browser-smoke` 全部证据，加 viewport、相关元素 geometry、overflow 检查和交互前后状态。 |

`chrome-smoke`、`chrome-layout` 只能作为旧输入归一化为 Provider-neutral scope；新 evidence 不生成 Chrome 专属 scope 名称。不得为了通过而降低 scope。

## Canonical evidence shape

```yaml
browser_evidence:
  provider: ego-lite
  provider_version: available-provider-version-or-omitted
  target: https://target.example.invalid/path
  session: task-space-or-current-chrome-session-metadata
  visual_scope: browser-smoke
  actions:
    - id: open-page
      action: navigate
      target: declared-scenario-target
      observed: page-loaded
  visible_result: declared-visible-result-after-real-action
  capture_time: 2026-09-03T00:00:00Z
  basis_revision: source-or-working-tree-revision
  screenshot_artifact: docs/test/evidence/ui/final.png
  authoritative_readback:
    status: success
    reference: redacted-resource-reference
    summary: declared-server-state-matches-page-result
  geometry: required-for-browser-layout-only
  viewport: required-for-browser-layout-only
  overflow: required-for-browser-layout-only
  before_after: required-for-browser-layout-only
```

Required common fields are `provider`, `target`, `session`, `actions`, `visible_result`, `capture_time`, `basis_revision` 和 `screenshot_artifact`；`provider_version` 可在宿主不能提供时省略。`browser-layout` 还必须提供 viewport、geometry、overflow 和 before/after evidence。`authoritative_readback` 在 Scenario 要求服务端、持久化或权限后果核对时是必需的。

- `provider` 必须等于配置解析出的 `ego-lite` 或 `chrome`；Provider mismatch 是 invalid evidence。
- `target` 是实际 URL 或运行目标，不能包含凭证；`session` 只记录 task-space/current-tab/profile 的非秘密身份元数据。
- `actions` 记录真实 Scenario `When` 的逻辑动作和观察结果，不记录密码、Token、Cookie、API Key 或完整输入秘密。
- `visible_result` 必须是同一 Provider 运行时观察到的页面状态；DOM 文本、静态测试、原型截图和 Provider 自身评分不构成视觉证据。
- `screenshot_artifact` 使用仓库相对路径或 hash；不得用不存在的占位截图或另一 Provider 的历史截图。
- `authoritative_readback` 只能来自页面真实动作之后的允许 API/权威适配器；它是页面结果的核对，不是页面动作的替代。只记录脱敏摘要和引用。

## Passed gate

UI `status=passed` 必须同时满足：

1. `scenario_id + scenario_version` 与当前 Scenario 精确匹配；
2. 主 Agent/宿主使用配置 Provider 完成了至少一个真实页面动作，且 `actions` 可追溯到 Scenario `When`；
3. `visible_result` 是动作后的实际可见结果；
4. Scenario 要求的 screenshot/artifact 存在且 revision 新鲜；`browser-layout` 的 viewport、geometry、overflow 和 before/after 也存在；
5. Scenario 要求的 `authoritative_readback` 成功、脱敏且与 actor/namespace 对应；
6. 没有 blocker、`unverified_gates`、Provider mismatch、控制权问题、人工 handoff 或未解决的 capability preflight。

API 200、Job created、Toast、单张截图、DOM 文本、静态/单元测试、mock、fixture 或 Provider score 均不能单独证明 UI passed。API shortcut、JavaScript state injection、localStorage 修改和预先写入最终服务端状态会使页面 evidence 失效。

## Evidence failure handling

| 失败 | 结果 |
|---|---|
| Provider unavailable/unknown、目标不可达或 capability 不足 | `blocked`/`incomplete`；不切换 Provider、不降 visual scope |
| 登录、Captcha、task-space/Tab 控制权或 actor 不明 | `waiting_user`，Track Result 保持 `blocked`/`incomplete` |
| API 代替页面动作，或 evidence 来自错误 Provider | `invalid evidence`；丢弃并重做真实页面动作 |
| 页面结果可见但所需 readback、screenshot 或 geometry 缺失 | `executed` + `unverified_gates` 或 `blocked`，不得 passed |
| 代码/场景/Profile/basis revision 变化导致 evidence stale | 旧证据不再支持通过；按当前 revision 重跑 |

Evidence refs 可写入当前 Verification Run/Checkpoint；不要把运行时账号绑定、截图、失败结果或 evidence revision 回写共享 Profile。所有日志和回复都必须脱敏。
