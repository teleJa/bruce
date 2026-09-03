---
name: browser-ui-verification
description: Execute project-agnostic UI acceptance through Bruce's configured host browser with fail-closed evidence.
---

# Browser UI Verification

使用共享 Scenario v1 为唯一业务语义锚点，由**主 Agent/宿主**通过 Bruce 配置的 Browser Provider 执行真实页面验收。这个 Skill 不实现浏览器 runtime，也不把浏览器控制权委派给子代理。

本 Skill 是项目无关的 UI 轨道规范：它只消费场景、已确认的环境/需求验证 Profile、Provider 配置和宿主能力，不硬编码业务路由、项目路径、账号值、凭证值、模型路由或具体前端框架。

## 硬性边界

- 真实页面动作的唯一执行者是 `main-agent-host`；实际 Provider 必须是适用 `.bruce/config.yaml` 中解析出的 `ego-lite` 或 `chrome`。
- `ego-lite` 使用宿主提供的隔离 task space；`chrome` 使用宿主提供的当前 Chrome session。Skill 不自行创建、替换或模拟 Provider。
- 子代理、`inspector`、`implementer`、`verifier` 和 `reviewer` 均不得获得 browser tool、task space、当前 Tab 或页面动作权限。Verifier 只能做 evidence-only review，不能点击、输入、上传、刷新、导航或接管会话。
- API 只能用于已声明且安全的 `setup`、`cleanup`，以及**页面真实动作之后**的只读 authoritative readback。API 不得完成或模拟场景的 UI `When`，不得用 API shortcut 代替页面动作。
- 不得用 JavaScript state injection、`localStorage` 修改、DOM/状态注入、测试 fixture、静态测试、Toast、单张截图或 Provider 自身评分替代真实页面验收。
- 不新增或运行 Playwright 作为 Bruce Provider；Playwright-only 结果不是有效的 Bruce 页面证据。
- 不选择模型、不创建私有 model router/model selector、不修改 Functional Agent registry；所有必要的子代理 Packet 仍由宿主按 Bruce 既有合同处理，而 UI 真实动作不委派给子代理。
- 不把密码、API Key、Token、Cookie、JWT、SSO ticket、授权头、含凭证 URL 或完整 Provider 响应写入 Profile、Packet、Checkpoint、evidence 或回复。

详细的浏览器执行权和 evidence schema 见 [host-boundary.md](references/host-boundary.md) 与 [browser-evidence.md](references/browser-evidence.md)。上位约束见 [Browser Provider](../bruce/references/browser-provider.md)、[Functional Agent contracts](../bruce/references/functional-agent-contracts.md)、[Verification loop](../bruce/references/verification-loop.md)。

## 输入合同

执行前必须取得以下信息；缺失或不一致时停止受影响 UI 批次，不猜测：

1. 一个已冻结的 Scenario v1，精确读取 `scenario_id`、`scenario_version`、`actor`、`execution.ui_mode=browser-provider`、`data.ui_namespace`、UI `steps`、`assertions`、`forbidden_shortcuts`、`evidence.required` 和 `visual_scope`。
2. 已确认且 revision/hash 匹配的 Environment Profile、Requirement Verification Profile、目标 operation 和账号/权限引用。Profile 只提供可复用的引用和授权范围；本次具体账号绑定、Provider preflight 和证据属于 Verification Run/Checkpoint。
3. 适用的 `.bruce/config.yaml`，以及宿主对所选 Provider 的运行时能力。配置存在、可执行文件存在或计划使用某工具都不等于能力可用。
4. 场景声明的 target、Acceptance IDs、允许的 setup/cleanup/readback 操作和 evidence 目录。Skill 不推断业务 endpoint 或账号。

若场景是 Web 验收却没有显式 `visual_scope`，这是 unresolved contract gap，必须 `blocked`/`incomplete`；不能默认当成 `none`。

## 执行流程

### 1. 锁定场景与命名空间

- 校验 Scenario 的 `scenario_id + scenario_version`，UI 轨道必须是 `execution_mode=browser-provider`。
- 只执行当前场景声明的 UI `When`；API 与 UI 使用各自 namespace，不能复用已完成页面动作的 fixture，也不能让 API/UI 写入路径相互覆盖。
- 在当前 Run/Checkpoint 中保留场景版本、Profile revision/hash、operation refs、账号 alias/ref 和 evidence revision；不要回写可复用 Profile 的动态结果。

### 2. 做一次 Provider capability preflight

每个依赖浏览器的批次开始时做一次最小 read-only preflight：

1. 从适用 `.bruce/config.yaml` 解析 `verification.browser_provider`；使用 `python3 scripts/browser_provider.py --config <config> --scope <visual_scope>` 检查配置与 scope 归一化。
2. 由宿主实际检查选定 Provider 对目标的连接、导航、一次非破坏性交互、可见状态和截图采集能力；`browser-layout` 还要检查 viewport、geometry、overflow 和 before/after 能力。
3. 记录 `capability`、选定 `provider`、精确 `target`、`check`、`status=available|unavailable|unknown` 和 dependent Acceptance IDs。不要以配置、安装状态、环境变量或计划替代运行时证据。

Provider 选择在批次内是确定的。非法配置、Provider unavailable/unknown、目标不可达或所需能力不足时，立即停止相关 UI 验收并标记 `blocked`/`incomplete`；不得静默切换 `ego-lite` 与 `chrome`、降低 `visual_scope`、改用 Playwright 或声称通过。只有相关配置、凭证引用、进程、目标或宿主能力事实发生变化后，才按 Verification Loop 重新 preflight。

### 3. 确认 actor、session 和控制权

- 记录 actor 与实际会话身份的可验证元数据；不得把密码、Cookie、Token 或 SSO ticket 当作 evidence。
- `ego-lite` 必须确认当前 task space 属于本次宿主运行且可由主 Agent控制；`chrome` 必须确认当前 Tab/Profile/session 是目标会话。控制权由用户或宿主持有时，不得强制 takeover。
- 需要登录、Captcha、扩展授权、文件选择或人工 handoff 时，停止页面动作，返回 `waiting_user`，同时把未完成的 UI 轨道保持为 `blocked`/`incomplete`。只说明用户需要完成的动作和恢复条件，不索取或记录秘密，不绕过 Captcha。
- actor 不匹配、session 不明、task space 被其他控制者占用或权限不足时同样停止；恢复后重新观察，不能把旧 session 的截图当作当前证据。

### 4. 仅执行声明的 API setup

在页面动作前，API 只能执行 Scenario/Environment Profile 明确允许的、最小且可清理的 setup，例如准备隔离数据或确认初始状态。setup：

- 不得点击、提交、上传、导航或以其他方式完成 UI `When`；
- 不得把 API 返回的目标结果伪装成页面可见结果；
- 不得跨越确认的 operation、账号、namespace 或权限范围；
- 失败时保留第一失败步骤并停止/报告，不用另一条 API 请求凑成 UI passed。

### 5. 由主 Agent/宿主执行真实页面动作

主 Agent 按 Scenario 的 UI steps 执行真实 `open`、`navigate`、`click`、`input`、`upload`、`select`、`drag`、`refresh`、`confirm` 和 `observe` 等动作，并在关键步骤后重新观察。每个动作必须对应场景中的 `When`，记录逻辑 action ID、目标、动作结果和时间；输入值与上传内容按敏感数据规则脱敏。

任何以下替代都使页面证据无效：API 直接完成 When、JavaScript state injection、localStorage 修改、DOM 文本注入、测试夹具、mock 页面、静态/单元检查、Toast 推断、只读 API 200 或只拍一张截图。无效证据必须丢弃并重新执行真实页面动作；若无法安全重跑，标记 `blocked`/`incomplete`，不能提高为 passed。

### 6. 观察可见结果并采集统一 evidence

真实动作完成后，由同一配置 Provider 观察页面实际可见状态并采集 [browser_evidence](references/browser-evidence.md)。`browser-smoke` 至少需要真实动作、可见结果和截图/等价 artifact；`browser-layout` 还必须有 viewport、相关元素 geometry、overflow 结果和交互前后状态。Evidence 的 Provider 必须与配置完全一致。

### 7. 页面动作后的 authoritative readback

只有页面真实动作已经发生并采集到可见结果后，才可调用场景声明的只读 API/权威适配器核对服务端状态、持久化结果或跨用户权限。Readback 必须记录脱敏的请求/资源引用、状态摘要、actor/namespace 对应关系和 evidence ref；它不能代替页面动作或页面可见结果。

若场景要求后端权威核对而 readback 缺失、失败、版本不匹配、actor 不符或结果未知，UI 轨道不得 `passed`，应保持 `executed` + `unverified_gates` 或 `blocked`。API 200、Job created、Toast 或单张截图均不能单独证明通过。

### 8. 在 evidence 后 cleanup 并生成轨道结果

- 只执行声明的安全 cleanup；不得在 evidence 采集前删除需要证明的状态。
- 输出当前 UI track result 和 evidence refs，不输出 Design/Completion/verdict/approval。轨道状态不是 Bruce 的最终 Completion。
- 失败保留原始场景与 evidence；按 Verification Loop 的 bounded repair 规则重跑未改变的原始场景和相关回归，不用更小的替代检查覆盖失败。

UI track result 至少保留以下字段，并与共享 Track Result v1 对齐：

```yaml
version: 1
scenario_id: FEATURE-AREA-001
scenario_version: 1
profile_id: requirement-verification-profile
profile_revision: 1
profile_content_hash: sha256:<64-hex-profile-hash>
basis_revision: <current-basis-revision>
evidence_revision: <current-evidence-revision>
track: ui
status: passed|executed|failed|blocked|designed
execution_mode: browser-provider
data_namespace: ui-run-<unique-id>
allowed_paths: []
evidence_paths: [docs/test/evidence/ui/summary.yaml]
modified_paths: []
commands: []
browser_actions: [open-page, click-submit, observe-result]
assertions: [visible-result, authoritative-readback]
blockers: []
unverified_gates: []
evidence_records: [{kind: browser, ref: docs/test/evidence/ui/summary.yaml, status: verified}]
persistence_required: true
authoritative_readback: [authoritative-readback]
browser_evidence:
  provider: ego-lite|chrome
  target: <declared-target>
  session: <host-session-reference>
  visual_scope: browser-smoke|browser-layout
  actions: [<real-browser-action>]
  visible_result: <visible-result-after-action>
  capture_time: <iso-8601-timestamp-with-timezone>
  screenshot_path: docs/test/evidence/ui/screenshot.png
operation_refs: []
account_refs: []
```

`status=passed` 的必要条件是：场景版本精确匹配；主 Agent/宿主使用配置 Provider 完成了真实 browser actions；页面结果真实可见；场景要求的 screenshot/等价 artifact 与 `browser-layout` 所需几何均存在；场景要求的 authoritative readback 已成功且与 actor/namespace 对应；没有 blockers 或 `unverified_gates`。任何条件缺失都必须 fail closed。

## Output

返回一个当前 UI track evidence fragment/Track Result 和 supporting evidence refs，至少带有场景 ID/version、`track=ui`、`execution_mode=browser-provider`、namespace、证据路径、真实 browser actions、断言、阻塞项和未验证门禁。`waiting_user` 是宿主控制流状态；写入共享 Track Result 时使用受支持的 `blocked`/`executed` 状态及非空 `blockers`/`unverified_gates`，不得发明平行终态。

这个 Skill 不返回 `Design`、`Completion`、`verdict` 或 `approval`，不把 UI track `passed` 当作 Bruce 的最终完成结论；最终裁决仍由 `completion-gate` 负责。

## Fail-closed 结果表

| 条件 | UI 结果 | 处理 |
|---|---|---|
| Scenario version、Profile revision/hash 或 operation 不匹配 | `blocked` | 停止执行，修正并重新确认，不合并旧 evidence |
| Provider 配置非法、Provider unavailable/unknown 或能力不足 | `blocked`/`incomplete` | 只记录 preflight 证据；不换 Provider、不降 scope |
| actor/session/task space 不匹配或控制权不明确 | `waiting_user` + `blocked`/`incomplete` | 等待宿主/用户恢复控制；不强制接管 |
| 登录、Captcha、人工 handoff 未完成 | `waiting_user` + `blocked`/`incomplete` | 按宿主 handoff/resume 恢复；不绕过敏感步骤 |
| 子代理尝试 browser action 或 Verifier 请求接管 | `blocked` | 拒绝 Packet/停止子任务；改由主 Agent执行 |
| API shortcut、JS/localStorage/fixture 替代 UI When | invalid evidence | 丢弃页面 evidence，重新执行真实动作 |
| 可见结果、截图、几何或权威 readback 缺失 | `executed`/`blocked` | 保留缺口；不得提升为 passed |
| Evidence Provider 与配置 Provider 不一致 | invalid evidence | 拒绝 evidence；用配置 Provider 重新采集 |

## Does not own

本 Skill 不拥有最终 verdict，不修改业务代码、Scenario、Environment/Requirement Profile、Functional Agent registry、`scripts/browser_provider.py` 或宿主权限；不创建 browser runtime、scheduler、model router、账号池、Credential Manager、第二 evidence store、部署流程或真实项目服务。它只规定主 Agent如何消费现有 Provider 和证据边界。
