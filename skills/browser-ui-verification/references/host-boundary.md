# Browser UI execution boundary

这是 `browser-ui-verification` 的权限和执行边界。它补充而不替代 Bruce 的 [Browser Provider](../../bruce/references/browser-provider.md)、[Functional Agent contracts](../../bruce/references/functional-agent-contracts.md) 和 [Verification loop](../../bruce/references/verification-loop.md)。

## Authority map

| Capability | 唯一允许者 | 明确禁止 |
|---|---|---|
| 解析 `verification.browser_provider`、选择本批次 Provider | 主 Agent/宿主，按适用 `.bruce/config.yaml` | Skill 自行配置、静默切换 `ego-lite`/`chrome`、Provider fallback |
| 真实导航、点击、输入、上传、选择、拖拽、刷新、确认和观察 | `main-agent-host` 使用配置的 `ego-lite` 或 `chrome` | 子代理、Verifier、API、JavaScript 注入、localStorage、fixture、Playwright |
| 登录态、Captcha、task space、当前 Tab/Profile 和人工 handoff | 宿主 Provider 与用户 | Skill 强制 takeover、绕过 Captcha、索取/记录秘密 |
| 页面后的服务端权威核对 | 主 Agent/宿主调用场景声明的只读 API/权威适配器 | 用 API 完成 UI When、用 200/Toast 伪造页面通过 |
| evidence 复核 | Verifier 可以只读检查已采集 evidence | Verifier 接管 task space、执行页面动作或改变 evidence |
| 最终完成判断 | Bruce `completion-gate` | UI Skill、Track aggregator、Verifier 返回 Completion/verdict/approval |

## Control contract

UI dispatch/track 输入必须明确：

```yaml
browser_execution:
  owner: main-agent-host
  provider: ego-lite|chrome
  execution_mode: browser-provider
  visual_scope: none|browser-smoke|browser-layout
  scenario_id: FEATURE-AREA-001
  scenario_version: 1
  session: task-space-or-current-chrome-session
  verifier_role: evidence-only-review
  subagent_browser_access: forbidden
```

- `provider` 必须是配置解析出的实际 Provider，不能把 `ego-lite` 证据标成 `chrome`，反之亦然。
- `visual_scope` 必须显式来自 Scenario/dispatch；Web acceptance 缺少 scope 时停止。`none` 只能在场景明确声明没有 material rendered outcome 时使用，不能作为浏览器证据缺失时的降级值。
- `scenario_id + scenario_version` 是 UI 轨道与其他轨道的协调键；不匹配时不执行或不聚合。
- UI 轨道的 `data_namespace` 必须与 API 轨道不同；`allowed_paths` 必须保持互斥。真实页面动作不产生 Skill 代码写入。
- 子代理如需参与，只能按 Bruce v1 Task Packet 执行非浏览器职责；其 `tools.deny` 必须覆盖 browser、task-space、current-tab 和 page-action 能力，且不改变现有 Functional Agent Profile。

## API boundary

API operation 的允许顺序只有：

1. `setup`：页面动作之前的隔离数据/初始状态准备，不得执行场景 UI `When`；
2. `page action`：只能由主 Agent/宿主通过配置 Provider 执行 Scenario UI steps；
3. `authoritative readback`：页面动作之后的只读服务端/持久化核对；
4. `cleanup`：证据采集之后的声明安全清理。

`setup`、`readback` 和 `cleanup` 都不能直接变成 UI evidence。API shortcut、API 完成按钮行为、预先写入最终结果、JS state injection、localStorage 修改或测试 fixture 都是 invalid evidence；必须丢弃并重跑页面动作，无法重跑则 `blocked`/`incomplete`。

## Stop and handoff rules

以下任一情况必须 fail closed：

- Provider 配置非法，或 runtime preflight 为 `unavailable|unknown`；
- 目标不可导航、真实交互、可见状态或 screenshot 能力不足；layout scope 缺 viewport、geometry、overflow 或 before/after 能力；
- actor、账号 alias、session、task space、Chrome Tab/Profile 或数据 namespace 不匹配；
- 用户控制 task space，或宿主不能证明当前主 Agent拥有控制权；
- 需要登录、Captcha、扩展授权、文件选择、敏感确认或人工 handoff；
- 子代理或 Verifier 试图调用 browser tool、接管 session，或通过 API 完成页面动作；
- evidence Provider 不等于配置 Provider，或 evidence revision/basis revision 已过期。

需要用户完成登录/Captcha/接管时，返回 `waiting_user`，说明唯一恢复条件，保留当前真实状态，不猜测、不强制 takeover、不把未完成当作 passed。若无安全恢复路径，Track Result 使用 `blocked` 并填写非空 `blockers`。

## Packet and verdict boundary

UI Skill 输出的是一个当前 UI track evidence fragment/Track Result，至少保留 `scenario_id`、`scenario_version`、`track=ui`、`execution_mode=browser-provider`、`data_namespace`、`evidence_paths`、`browser_actions`、`assertions`、`blockers` 和 `unverified_gates`。它不输出 `Design`、`Completion`、`verdict` 或 `approval`，也不把轨道 `passed` 当作最终完成。
