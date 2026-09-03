# 测试计划：Bruce 通用测试验证编排与轨道调度

## 验收映射

| 验收 ID | 场景 ID | 验证层级 | Evidence |
|---|---|---|---|
| TVO-01 | SCENARIO-001 | unit/contract | Scenario validator fixtures、`tests/test_test_dispatch_contract.py` |
| TVO-02 | API-001、API-002、API-003 | contract/integration-design | `tests/test_api_test_orchestration_contract.py`、Skill/references 链接和 mode 断言 |
| TVO-03 | UI-001、UI-002、UI-003 | contract/browser-boundary | `tests/test_browser_ui_verification_contract.py`、`tests/test_browser_provider.py` |
| TVO-04 | DISPATCH-001、DISPATCH-002 | unit/contract | track aggregator fixtures、namespace/version/path conflict tests |
| TVO-05 | ROUTING-001 | unit/contract | `tests/test_test_dispatch_contract.py`、`tests/test_functional_agent_profiles.py`、定向无 Sol/browser-tool 断言 |
| TVO-06 | PROFILE-001 | integration/contract | `tests/test_verification_profile_contract.py`、schema/template 映射检查 |
| TVO-07 | COMPLETION-001 | integration/contract | `tests/test_validation_loop_contract.py`、`tests/test_completion_contract.py` |
| TVO-08 | REGRESSION-001 | repository/full | 全量 unittest、Functional Agent validator、plugin validator、`git diff --check` |

## 前置条件与真实依赖

- 当前 Bruce 仓库可运行 Python unittest、PyYAML、Functional Agent validator 和 plugin validator。
- 实施前读取当前 `git status` 和涉及文件 diff，保留 Environment Profile/Operations 的既有未提交修改。
- 本次仓库级验证不要求真实业务服务、PostgreSQL、Worker、账号、凭证或浏览器会话。
- 真实 API/UI 运行属于后续目标项目适配任务；必须消费目标项目已确认的 Environment Profile，不能用 Bruce 静态契约测试替代。
- 若后续执行真实页面场景，Browser Provider 由适用 `.bruce/config.yaml` 的 `verification.browser_provider` 决定，并由主 Agent操作。

## 按比例确定视觉验证范围

- 范围：none
- 判断依据：本变更实现 Skill、文件契约、校验脚本和 Gate 集成，不修改产品页面、布局或视觉产物；浏览器 UI Skill 的运行规则通过契约测试校验，真实页面证据只能在后续目标项目任务中由主 Agent使用配置 Provider 采集。
- 对于 `browser-layout`：not_applicable；本变更没有具体目标 URL、页面元素或布局不变量，不能伪造 viewport、截图或几何证据。

## 一致性分类

```yaml
behavior_kinds:
  - shared_resource
  - permission_projection
  - availability_derivation
  - state_transfer
consistency_check: required
reason: Scenario version、API/UI 轨道结果、浏览器控制权、Environment/Profile revision 和 Completion ownership 存在跨对象一致性与权限边界。
```

## 一致性与权威状态矩阵

| ID | 主体 | 关联资源 | 业务不变量 | 当前权威状态源 | 竞争者/权限视角 | 状态时间窗口 | 冲突/错误规则 | 数据后果 | UI/API 重新同步 |
|---|---|---|---|---|---|---|---|---|---|---|
| CONS-001 | 共享 Scenario | API/UI 轨道结果 | 同一聚合只能消费相同 `scenario_id + scenario_version` | Scenario 文件和 validator | API 轨道、UI 轨道、父 Dispatch | 场景锁定到两轨返回之间 | 版本不一致时 overall blocked | 不合并不相干证据 | 父 Agent统一版本并重跑受影响轨道 |
| CONS-002 | API 轨道 | Job/Artifact/持久化资源 | created/2xx 不等于终态或持久化成功 | 公共状态 API 或获准只读数据库回读 | 不同 actor、重复/并发请求 | 请求创建到终态/回读之间 | timeout、failed、unknown、权限冲突分别报告 | 失败不得被后续较小检查覆盖 | 重新读取终态和权威资源，再更新轨道证据 |
| CONS-003 | UI 轨道 | Browser Provider/task space/服务端状态 | passed 必须同时有真实页面动作、可见结果和必要权威核对 | 配置 Provider 的页面证据及权威 API | 主 Agent、用户控制 task space、不同 actor | 登录/点击到异步完成和刷新之间 | 用户控制、actor 不符、Captcha 或 Provider unavailable -> waiting_user/blocked | 不通过 API 补齐页面状态 | 主 Agent恢复控制后重新观察页面并权威回读 |
| CONS-004 | Requirement Verification Profile | Environment/Profile/Scenario/evidence revision | 静态引用与动态运行结果分离，所有 revision 必须匹配 | confirmed Profile、Scenario、Verification Run/Checkpoint | 旧 Profile、旧场景、旧 evidence 与当前 working tree | 设计/代码/环境变化后到重新验证前 | stale 或缺映射保持 incomplete/blocked | 不将旧证据提升为当前通过 | 重新 preflight，重跑失效轨道和相关回归 |
| CONS-005 | Completion Gate | 轨道聚合状态 | `overall_status=passed` 只是场景证据，不是 `Completion: pass` | Completion Gate review matrix | Dispatch、Verifier、Reviewer | 轨道聚合到最终 Gate 之间 | Gate 发现缺口返回 issues/blocked | 不修改轨道历史凑成 pass | 补证据/修复后重新运行 Gate |

## 冲突与权限视角场景矩阵

| 场景 ID | 适用性 | 不适用原因 | 起始状态 | 角色/操作者 | 动作 | 预期 UI 状态 | 预期 API/结果 | 持久化不变量 | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| CONS-S-001 | applicable | 无 | API=version 1、UI=version 2 | 父 Dispatch | 聚合两轨结果 | UI 结果保留但不能形成统一通过 | overall blocked，报告版本冲突 | 证据不被重写或混合 | aggregator conflict fixture |
| CONS-S-002 | applicable | 无 | Job 已创建但未到允许终态 | API actor | 轮询状态并请求结果 | not_applicable；API 场景不验证页面 | executed/failed/blocked 取决于 timeout/终态，不能 passed | 未权威回读前不声明持久化完成 | API Skill polling contract tests |
| CONS-S-003 | applicable | 无 | 正确页面但 task space 由用户控制 | 主 Agent与用户 | 尝试继续页面动作 | waiting_user/blocked，不强制 takeover | 仅可做允许的只读 preflight，不补齐 UI 动作 | 页面失败状态不由 API 修改 | Browser UI Skill negative contract test |
| CONS-S-004 | applicable | 无 | 子代理 Packet 请求 browser tool | Test Dispatch | 校验 Packet | 无页面执行 | invalid dispatch/blocked | 无外部状态变化 | dispatch/Functional Agent tests |
| CONS-S-005 | applicable | 无 | API passed、UI blocked | 父 Dispatch | 聚合必需轨道 | UI 仍为 blocked | overall blocked | API 证据保留，UI 不被标记通过 | status aggregation table tests |
| CONS-S-006 | applicable | 无 | Scenario passed 但 evidence revision 旧于当前 basis | Completion Gate | 构建 review matrix | 页面/API 历史结果不可用于当前完成 | Completion issues/blocked | 旧证据保留但标记 stale | validation-loop/completion tests |

## 状态与意图矩阵

| 起始状态 | 用户/系统意图 | 预期行为 | 数据后果 |
|---|---|---|---|
| 无共享 Scenario | 设计 API/UI 验收 | 创建一个稳定 ID/version，状态 designed | 只写场景契约，不写运行结果 |
| Scenario designed | 执行 API 轨道 | 按声明 mode、namespace 和 operation 运行 | 仅创建当前测试拥有的数据并按策略清理 |
| Scenario designed | 执行 UI 轨道 | 主 Agent用配置 Provider 真实操作页面 | 页面动作不能由 API 预先完成 |
| API/UI 全 passed | 聚合场景 | overall passed，并保留轨道明细 | 不产生 Completion verdict |
| 任一轨道 failed | 聚合场景 | overall failed | 保留第一失败步骤和全部已有证据 |
| 任一必需轨道 blocked | 聚合场景 | overall blocked | 保留解除条件，不静默降级 mode/Provider/model |
| evidence stale | 请求完成判断 | Gate 拒绝旧证据并要求重跑 | 历史证据不删除，当前通过状态失效 |
| 修复完成 | 重新验证 | 重跑原始失败场景及相关回归 | 新 evidence revision 与当前 basis 绑定 |

## 测试场景

### SCENARIO-001：共享 Scenario v1 校验

- 映射到：TVO-01、T-001
- 类型：happy/error/regression
- Given: 合法 Scenario、缺失 ID/version、重复轨道、API/UI 步骤混用和 namespace 冲突 fixtures。
- When: 运行 Scenario validator。
- Then: 合法 fixture 通过；无稳定身份、语义混用、冲突 namespace 或非法状态的 fixture 非零退出并返回可定位错误。
- 预期 UI 状态：not_applicable；验证文件契约。
- 预期 API/结果：validator 返回确定性 pass/fail 和错误路径。
- 持久化不变量：Scenario 文件不包含凭证值或动态运行证据。
- Evidence: `python3 -m unittest tests.test_test_dispatch_contract`。
- 必需验证层级：unit/contract。

### API-001：三种 API mode 边界

- 映射到：TVO-02、T-002
- 类型：integration/contract
- Given: memory-application、real-http、live-acceptance 三种场景及各自前置条件。
- When: 检查 `api-test-orchestration` 的 mode、命令和证据规则。
- Then: 每种 mode 明确能证明和不能证明的边界，缺失真实 HTTP/PostgreSQL/Worker/provider 时不能静默降级或冒充更高层通过。
- 预期 UI 状态：not_applicable；API Skill 禁止浏览器依赖。
- 预期 API/结果：mode、前置条件、命令和 evidence 字段完整。
- 持久化不变量：memory 证据不能描述为 PostgreSQL 持久化证据。
- Evidence: `tests/test_api_test_orchestration_contract.py`。
- 必需验证层级：contract。

### API-002：异步 Job、终态和持久化回读

- 映射到：TVO-02、T-002
- 类型：happy/error/recovery
- Given: API 流程创建 Job，声明 terminal allowlist、timeout、interval 和持久化要求。
- When: 执行 bounded polling 并在成功后权威回读产物。
- Then: succeeded 仅在所需 artifact/readback 也满足时通过；timeout、failed、unknown 和 malformed 分开报告；不使用无界循环或 sleep-only。
- 预期 UI 状态：not_applicable。
- 预期 API/结果：状态迁移和第一失败步骤可追溯。
- 持久化不变量：未完成权威回读时不能声明 durable behavior passed。
- Evidence: API reference contract assertions。
- 必需验证层级：contract/integration-design。

### API-003：权限、重复和脱敏

- 映射到：TVO-02、T-002
- 类型：permission/edge
- Given: owner、非 owner、重复请求和敏感字段响应场景。
- When: 生成或执行 API 测试。
- Then: 权限隔离、重复/幂等结果和敏感字段缺失均有断言；日志不包含 token、cookie、数据库 URL 或模型密钥。
- 预期 UI 状态：not_applicable。
- 预期 API/结果：允许/拒绝/冲突语义可观察。
- 持久化不变量：失败或无权请求不产生未声明状态变化。
- Evidence: API Skill safety/evidence contract tests。
- 必需验证层级：contract。

### UI-001：主 Agent执行真实页面动作

- 映射到：TVO-03、T-003
- 类型：integration/contract
- Given: 共享 UI 场景、配置 Provider、正确 actor 和 Agent 可控制的会话。
- When: 主 Agent执行 open/click/input/upload/refresh 等场景动作并在每个关键步骤后重新观察。
- Then: 证据记录 Provider、target、session、真实 actions、visible result、capture time、basis revision 和 screenshot；layout scope 额外记录 geometry/overflow。
- 预期 UI 状态：场景声明的页面结果真实可见。
- 预期 API/结果：仅做允许的准备、清理和页面动作后的权威核对。
- 持久化不变量：API 不替代页面必须完成的动作。
- Evidence: Browser UI Skill 与 Browser Provider contract tests；真实页面证据留给目标项目任务。
- 必需验证层级：contract/browser-boundary。

### UI-002：子代理浏览器访问被拒绝

- 映射到：TVO-03、TVO-05、T-003、T-004
- 类型：permission/error
- Given: UI 调度提议将 browser 工具、task space 或页面动作交给 Subagent。
- When: 构造或校验 Task Packet。
- Then: 调度被拒绝或改为主 Agent执行；`verifier` 保持 evidence-only，不修改其 browser deny；没有真实页面副作用。
- 预期 UI 状态：无页面操作发生。
- 预期 API/结果：invalid dispatch/blocked 并返回修正边界。
- 持久化不变量：无业务数据变化。
- Evidence: 新 browser UI/dispatch tests 和现有 Functional Agent profile assertions。
- 必需验证层级：unit/contract。

### UI-003：登录、Captcha、控制权和 Provider 不可用

- 映射到：TVO-03、T-003
- 类型：error/recovery
- Given: actor 不匹配、用户控制 task space、需要登录/Captcha 或配置 Provider unavailable。
- When: 执行 UI preflight。
- Then: waiting_user/blocked，记录解除条件；不强制 takeover、不切换 Provider、不降低 visual scope、不用 API 补齐页面状态。
- 预期 UI 状态：保持当前真实状态，不伪造通过。
- 预期 API/结果：只读 preflight 可报告 unavailable/unknown。
- 持久化不变量：无未授权页面或后端变更。
- Evidence: Browser UI preflight contract tests、Browser Provider regression。
- 必需验证层级：unit/contract。

### DISPATCH-001：API/UI 双轨隔离与状态聚合

- 映射到：TVO-04、T-004
- 类型：happy/edge
- Given: 同一版本的 api/ui 轨道使用独立 namespace、互斥写入路径和不同状态组合。
- When: Dispatch 生成任务并运行 aggregator。
- Then: 两轨不共享已完成 UI 动作的 fixture；状态按 failed > blocked > passed > executed > designed 聚合，轨道明细不丢失。
- 预期 UI 状态：UI 状态由其真实证据决定。
- 预期 API/结果：聚合器返回确定性 overall status。
- 持久化不变量：轨道证据和 namespace 不互相覆盖。
- Evidence: dispatcher aggregation table tests。
- 必需验证层级：unit/contract。

### DISPATCH-002：版本或写入冲突 fail-closed

- 映射到：TVO-04、T-004
- 类型：error/recovery
- Given: API/UI 使用不同 Scenario version、相同数据 namespace 或重叠 allowed paths。
- When: Dispatch 尝试派发或聚合。
- Then: blocked，返回冲突字段和解除条件；不得为了得到 passed 合并无关运行。
- 预期 UI 状态：不开始或停止受影响轨道。
- 预期 API/结果：冲突被确定性拒绝。
- 持久化不变量：已有证据保持原始版本。
- Evidence: negative dispatch fixtures。
- 必需验证层级：unit/contract。

### ROUTING-001：Bruce resolver 独占测试模型路由

- 映射到：TVO-05、T-004
- 类型：permission/regression
- Given: API/UI/dispatch 需要 Subagent，目标模型可用、fallback 或 blocked。
- When: 选择 Functional Agent Profile 并解析 Task Packet。
- Then: Packet 带 `model_resolution`；Luna 只用 max；Reviewer 仍用既有 Terra/high；新 Skill/refs 不含 `gpt-5.6-sol`、私有 scheduler/router 或 browser tool。
- 预期 UI 状态：Subagent 不操作页面。
- 预期 API/结果：resolver 返回 resolved/fallback/blocked 且原因完整。
- 持久化不变量：不修改 Profile registry 或新增第五 Profile。
- Evidence: `tests/test_functional_agent_profiles.py`、新 dispatch contract tests 和定向搜索。
- 必需验证层级：unit/contract。

### PROFILE-001：Requirement Verification Profile 选择测试能力

- 映射到：TVO-06、T-005
- 类型：integration/contract
- Given: requirements Acceptance、confirmed Environment Profile、账号要求和共享 Scenario。
- When: 生成 Requirement Verification Profile。
- Then: `skill_selections`/acceptance stage 能引用 dispatch/API/UI 能力、environment/account/scenario/track/evidence；Profile 不复制环境全文、不保存当前结果。
- 预期 UI 状态：not_applicable；只验证静态策略。
- 预期 API/结果：schema/template/Skill contract 一致。
- 持久化不变量：动态 account binding、preflight、stage result 和 evidence 留在 Run/Checkpoint。
- Evidence: `tests/test_verification_profile_contract.py`。
- 必需验证层级：integration/contract。

### COMPLETION-001：轨道状态、证据新鲜度与唯一 Completion

- 映射到：TVO-07、T-005
- 类型：integration/regression
- Given: passed/failed/blocked/stale 轨道结果和当前 basis revision。
- When: Verification Loop/Completion Gate 构建矩阵。
- Then: 轨道聚合状态作为证据输入；stale/缺证据/Provider unavailable 保持 incomplete/issues/blocked；只有 Completion Gate 返回 `Completion`。
- 预期 UI 状态：需要 UI Acceptance 时必须引用匹配 Provider 的当前 browser evidence。
- 预期 API/结果：需要 API/persistence Acceptance 时必须引用相应权威证据。
- 持久化不变量：历史 evidence 不删除、不冒充当前 revision。
- Evidence: `tests/test_validation_loop_contract.py`、`tests/test_completion_contract.py`。
- 必需验证层级：integration/contract。

### REGRESSION-001：插件发现与全量回归

- 映射到：TVO-08、T-006
- 类型：regression
- Given: 三个 Skill 和集成改动已完成，工作区含任务前已有未提交文件。
- When: 运行全量 unittest、Functional Agent validator、plugin validator 和 diff 检查。
- Then: 新 Skill metadata/链接/契约可发现，现有 Profile/Browser/Gate 测试不回退，Joytime 和无关 dirty files 未被修改。
- 预期 UI 状态：not_applicable；不运行具体产品页面。
- 预期 API/结果：所有仓库内命令有独立退出结果。
- 持久化不变量：不提交、不推送、不部署、不刷新插件。
- Evidence: `python3 -m unittest discover -s tests -p 'test_*.py'`、`python3 scripts/validate_functional_agents.py`、`python3 scripts/validate_plugin.py`、`git diff --check`、最终 `git status --short`。
- 必需验证层级：repository/full。

## 回归来源

- Joytime dispatch 的私有模型路由和 Sol 升级路径 -> ROUTING-001，确保泛化后只用 Bruce resolver 且无 Sol。
- Joytime ego-browser 子任务模型路由 -> UI-002，确保浏览器执行权归主 Agent。
- Bruce 现有 Browser Provider fail-closed -> UI-001、UI-003、COMPLETION-001。
- Bruce 现有 Functional Agent 四 Profile/Packet 合同 -> ROUTING-001。
- Environment/Profile 静态与动态边界 -> PROFILE-001、COMPLETION-001。
- API 200、Job created、Toast 或截图被误当通过的历史风险 -> API-002、UI-001、DISPATCH-001。

## 限制与未验证边界

- 本设计阶段和仓库级实现验证不执行 Joytime 或其他项目的真实 API、PostgreSQL、Worker、模型 Provider 或页面场景。
- 静态 Skill/contract tests 只能证明 Bruce 指令和校验规则，不证明目标项目 endpoint、账号、数据、浏览器控制权或服务当前可用。
- 真实项目适配时需要独立确认 Environment Profile、operation ID、场景存储路径、测试命令、账号和证据目录。
- 子代理不允许操作浏览器，因此 UI 轨道不能通过独立 Subagent 并行执行；主 Agent负责编排和真实动作，Verifier 只复核已有证据。
- 本任务不引入 `gpt-5.6-sol`；若未来需要新的模型/Profile，必须作为独立架构变更重新过 Design Gate。

## 自检

- 每个 acceptance item 均映射到稳定 scenario 和证据。
- 每个 behavior scenario 均有具体 Given/When/Then 和匹配层级的 Evidence。
- `consistency_check: required`，已定义 Scenario/version、轨道结果、浏览器控制权、Profile/evidence revision 和 Completion ownership 的权威状态与冲突规则。
- 已覆盖 normal、edge、error、permission、recovery 和 regression 场景。
- API/UI namespace、版本和写入边界均有负向校验。
- 浏览器 Provider 不可用时 fail-closed；不允许子代理浏览器权限和 API shortcut。
- 模型路由由 Bruce resolver 独占，不含 `gpt-5.6-sol` 或第五 Profile。
- 真实运行与静态契约证据分开报告，未用低层证据替代目标项目 API/browser 验收。
- 中文自然语言字段使用简体中文，稳定标识、命令和路径保持原样。
