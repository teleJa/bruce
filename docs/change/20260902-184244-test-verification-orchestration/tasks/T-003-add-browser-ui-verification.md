# 任务 T-003：增加主 Agent 页面验收 Skill

- 契约修订：1
- 契约状态：执行前冻结
- 状态来源：`../checkpoint.yaml`
- 父计划：`../plan.md`

## 目标

新增 `browser-ui-verification` Skill，使主 Agent 能使用 Bruce 配置的 Browser Provider 执行共享场景中的真实页面动作并保留统一证据，同时明确禁止子代理和 API 绕过页面交互。

## 包含范围

- `skills/browser-ui-verification/SKILL.md`、`agents/openai.yaml` 和本 Skill 自有 references。
- Provider preflight、actor/login/task-space 控制权、真实动作、页面断言、截图/几何、API 准备与权威核对、blocked/waiting_user 和证据格式。
- `tests/test_browser_ui_verification_contract.py`。

## 排除范围

- 不修改或复制 ego-browser runtime，不新增 Playwright，不允许子代理 browser 工具。
- 不修改 `scripts/browser_provider.py` 或 Functional Agent registry。
- 不用 API、JavaScript 状态注入、localStorage 修改或测试夹具替代必须验证的页面动作。

## 依赖关系

- 依赖任务：T-001
- 使用：Scenario v1、`browser-provider.md`、配置的 `ego-lite|chrome` 宿主能力
- 产出：主 Agent 页面验收 Skill、preflight 和 browser evidence 规范

## 业务不变量与权威状态（按适用性）

- 一致性检查：required
- 业务不变量与权威状态摘要：UI passed 必须同时具有真实页面动作、可见结果、所需截图/几何和场景要求的后端权威核对；API 200、Toast 或单张截图不能单独证明通过。
- 竞争者/权限视角与冲突后果：task space 可能由用户控制，actor 可能不匹配；此时必须 waiting_user/blocked，不得强制接管或继续点击。
- 关联测试计划矩阵/场景 ID：CONS-003、CONS-S-003、UI-001、UI-002、UI-003
- 不适用原因：not_applicable

## 验收标准

- 父级场景 ID：TVO-01、TVO-03
- Given：共享 UI 场景、配置 Provider 和可用/不可用控制权状态
- When：主 Agent 执行或子代理尝试执行页面动作
- Then：主 Agent 能按 Provider contract 取证；子代理 browser access/API shortcut/静默 Provider fallback 被明确拒绝；人工登录/Captcha/控制权问题正确阻塞
- Evidence：Skill contract tests、Browser Provider regression 和负向文本/Packet 断言

## 验证

- 必需层级：contract/browser-boundary
- 命令/检查：`python3 -m unittest tests.test_browser_ui_verification_contract tests.test_browser_provider`
- 环境：仓库内契约测试；真实页面 smoke 只在后续目标项目环境由主 Agent执行

## 授权与风险

- 授权：normal；登录、上传、敏感操作和具体页面动作仍由宿主权限及 Environment Profile 决定
- 风险触发：guarded；浏览器控制权、登录态和证据边界错误会造成越权或虚假 UI 通过
- 停止条件：实现提议给子代理 browser 权限、静默切换 Provider、降低 visual scope 或绕过人工 handoff 时停止

## 契约变更规则

不得静默扩大本任务范围。如果范围、验收、依赖、授权或所需验证层级发生变化，必须创建新的契约修订或替代任务，并在下一个检查点中记录原因。
