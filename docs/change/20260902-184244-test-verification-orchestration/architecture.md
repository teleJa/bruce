# 架构：Bruce 通用测试验证编排与轨道调度

## 目标与范围

- Objective：在 Bruce 已确认的 Environment Profile、Requirement Verification Profile、浏览器 Provider 和 Completion Gate 体系上，增加可复用的 API 编排验证、真实页面验收和测试轨道调度能力。
- Included：通用业务场景契约、API/UI 轨道边界、轨道结果聚合、测试 Skill 选择、Verification Run/Checkpoint 对接、证据和授权边界。
- Excluded：生产业务代码、数据库 schema/migration、通用测试执行引擎、Bruce 自有浏览器 runtime、子代理直接操作浏览器、Playwright 资产迁移、`gpt-5.6-sol` 路由、生产访问和未声明的环境操作。

本设计整合 Joytime 侧三个 Skill 的可复用方法，但不复制 Joytime 的项目路径、业务模块、浏览器驱动或私有模型路由。Joytime 仓库只是本设计的参考来源，不是本变更的写入目标。

## 冻结的用户决策

1. **子代理不允许操作浏览器。** 真实页面交互由主 Agent 通过 Bruce 选择的宿主 Browser Provider 执行；Verifier 只能复核场景和已采集的浏览器证据，不能接管 task space、点击、输入、上传、刷新或导航。
2. **测试场景不引入 `gpt-5.6-sol`。** 测试调度不建立私有模型选择器；所有 Subagent 仍通过 Bruce 的四类 Functional Agent Profile 和共享 resolver 路由。当前测试场景最多复用 `gpt-5.6-luna + max` 与 `gpt-5.6-terra + high` 的现有配置。

## 仓库证据

- `skills/environment-profile/SKILL.md:8-43,70-159` — Environment Profile 已声明环境、服务、数据、账号、操作、授权和 preflight，并区分静态 Profile 与运行结果。
- `skills/environment-profile/references/profile-schema.md:66-180` — `test_context` 是测试执行上下文的结构化归属，`operations` 是唯一可执行操作目录，Profile 确认是声明范围内的授权而不是运行成功。
- `skills/verification-profile/SKILL.md:32-78` — Requirement Verification Profile 绑定已确认环境、账号、Skill/capability、Acceptance、证据和修复边界。
- `skills/verification-profile/references/profile-schema.md:119-156` — `skill_selections`、Acceptance 映射、阻塞和恢复规则已经为测试 Skill 选择提供位置。
- `skills/bruce/references/browser-provider.md:1-72` — Bruce 已有 `ego-lite|chrome` Provider、`browser-smoke|browser-layout` scope、能力 preflight 和统一 `browser_evidence`。
- `skills/bruce/references/functional-agent-contracts.md:35-119` — Subagent 角色、Packet、模型解析和 Gate ownership 已有统一合同；Skill 不得私自创建模型 Runtime 或调度器。
- `skills/bruce/references/verification-loop.md:7-18,58-75,96-115` — Acceptance、外部能力 preflight、验证层级和浏览器证据边界已经存在。
- `skills/completion-gate/SKILL.md:51-53,65-73,237-258` — Verifier/Reviewer 只返回证据 Packet，Completion Gate 是唯一终态裁决者。
- `/Users/tele/xjjk/joytime-studio/.codex/skills/joytime-api-orchestration/SKILL.md:10-18,30-40,62-141` — Joytime API Skill 已形成状态化请求、异步 Job、持久化回读、失败分类和执行边界。
- `/Users/tele/xjjk/joytime-studio/.codex/skills/joytime-test-dispatch/SKILL.md:16-57,69-99` — Joytime dispatch 已形成用户功能域场景、共享 Scenario ID/version、API/UI 轨道隔离和状态聚合规则。
- `/Users/tele/xjjk/joytime-studio/.codex/skills/joytime-ego-browser/SKILL.md:10-40,42-60` — Joytime 页面 Skill 已形成真实页面动作、API 仅作准备/权威核对、页面证据优先和 blocked 边界。

## 组件与责任

| 组件 | 现有或计划交付物 | 负责 | 不负责 |
|---|---|---|---|
| Environment Profile | `environment-profile`、`environment-operations` | 环境拓扑、服务/依赖、账号引用、数据隔离、可执行 operation、授权和 preflight 声明 | 业务场景、Acceptance 断言、运行结果、Completion |
| Requirement Verification Profile | `verification-profile` | 将需求 Acceptance 映射到环境、账号、测试 Skill、场景、证据和修复边界 | 执行命令、浏览器操作、运行时状态 |
| Shared Scenario Contract | 新增通用场景规范，项目可保存于自身测试目录 | 一个用户可验收功能域的业务流、actor、轨道步骤、断言、状态、持久化和证据要求 | 运行时结果、模型选择、最终 Gate |
| Test Dispatch | 新增通用调度 Skill/规范 | 锁定唯一场景 ID/version，选择 API/UI 轨道，生成受限 Packet，分配隔离命名空间，聚合轨道状态 | 浏览器操作、API 测试实现细节、模型私有路由、Completion |
| API Verification Track | 新增通用 API 编排 Skill/规范 | HTTP/应用测试模式、认证、变量传递、状态转换、bounded polling、持久化回读、脱敏证据 | 浏览器、生产代码、schema/migration、未声明命令 |
| Browser UI Verification Track | 新增通用页面验收 Skill/规范 | 使用选定 Provider 执行真实页面动作、页面可见断言、截图、页面后 API 权威核对 | 子代理浏览器操作、Playwright 替代、API 替代用户动作、Provider fallback |
| Bruce Functional Agent Profiles | `inspector`、`implementer`、`verifier`、`reviewer` | 统一 Subagent 职责、Packet、模型解析和证据输出 | 为测试新增 `sol` Profile 或由 Skill 直接选择模型 |
| Browser Provider | `scripts/browser_provider.py` 与宿主 capability | 选择和校验 `ego-lite|chrome`，提供运行时页面能力和统一证据元数据 | 业务场景、测试结论、子代理权限 |
| Verification Run/Checkpoint | 现有 checkpoint/verification-loop 约定 | 记录当前 revision、轨道运行状态、证据引用、阻塞、恢复和修复轮次 | 静态环境事实、第二套结果库、最终 Completion |
| Completion Gate | `completion-gate` | 根据全部 Acceptance、轨道证据和复核矩阵返回唯一 `Completion` | 执行浏览器、选择模型、替代轨道状态聚合 |

## 数据与控制流

1. 用户提供需求和验收边界；Bruce 读取已确认的 Environment Profile 和 Requirement Verification Profile。
2. Test Dispatch 将面向用户的 `feature_area + business_flow + actor` 锁定为一个 `scenario_id + scenario_version`，不得按代码包拆成竞争场景。
3. Dispatch 根据需求选择 `api`、`ui` 或 `both` 轨道，并为每条轨道生成独立数据命名空间和明确的操作/证据范围。
4. API 轨道消费 Environment Profile 中已声明的 operation 和场景中的 API 步骤，执行请求、状态转换、Job polling 和权威回读。
5. UI 轨道由主 Agent 通过已配置的 Browser Provider 执行场景中的真实 `When` 动作；API 只用于前置数据准备、清理和页面动作后的只读权威核对。
6. 每条轨道返回结构化结果和证据引用。子代理若参与，只能使用 Bruce 合同允许的角色；浏览器动作不委派给子代理。
7. Dispatch 按轨道状态规则聚合为场景级 `designed|executed|passed|failed|blocked`，并保留每条轨道的命令、动作、证据、阻塞和未验证门禁。
8. Verification Run/Checkpoint 记录运行时状态和 evidence revision；代码、需求、环境或场景契约变化会使受影响证据失效。
9. Completion Gate 消费场景结果和当前证据，执行自己的复核矩阵并返回唯一 `Completion: pass|issues|blocked`。

## 决策

### 决策一：以共享用户场景作为 API/UI 的唯一协调锚点

- Chosen：场景按用户功能域和业务流程定义，API/UI 轨道共享 `scenario_id` 和 `scenario_version`。
- Rationale：避免把跨模块业务流拆成互不一致的代码包测试；保留 Joytime 已验证的场景协调方式，并与 Bruce 的 Given/When/Then/Evidence 对齐。
- Rejected：每个后端包或前端页面各自创建独立场景，因为会丢失跨轨道一致性和统一 Acceptance 映射。
- Reversibility：中；可通过新增场景版本修订步骤或断言，不修改历史运行证据。

### 决策二：Environment Profile 与 Scenario/Verification Profile 分层

- Chosen：Environment Profile 只保存环境、操作、授权和依赖；Scenario 保存业务步骤；Requirement Verification Profile 保存 Acceptance 到 Skill/场景/证据的映射。
- Rationale：维持 Bruce 已建立的静态环境与动态运行边界，避免把业务断言和运行结果写入可复用环境档案。
- Rejected：把 API/UI 步骤直接放入 Environment Profile，因为同一环境可服务多个需求和多个场景。
- Reversibility：高；场景和 Verification Profile 均可在不改变环境档案的情况下演进。

### 决策三：浏览器执行权归主 Agent/宿主，Verifier 只读复核

- Chosen：主 Agent 使用 `verification.browser_provider` 对真实页面执行操作；Verifier 如被调用，只检查复现命令、页面证据、权威核对和 Acceptance 覆盖，不获得 browser 工具。
- Rationale：保持 Codex Host 对浏览器、task space、登录态、Captcha 和人工 handoff 的控制；不扩展当前 `verifier` 的 browser deny 边界。
- Rejected：让 UI 子代理直接调用 ego-browser，因为会引入 task space 所有权转移、敏感操作 handoff、证据归属和工具授权的新合同。
- Reversibility：中；未来若需要子代理浏览器能力，必须单独进行架构设计和安全/契约评审，不由本设计隐式开启。

### 决策四：模型路由复用 Bruce resolver，不引入 `gpt-5.6-sol`

- Chosen：测试 Skill 只声明轨道、复杂度和所需能力；Subagent 仍映射到现有 `inspector`、`implementer`、`verifier`、`reviewer` Profile，并由共享 resolver 解析模型。第一版允许使用现有 Luna/Max 和 Terra/High 配置，不新增 Sol。
- Rationale：避免 Joytime 私有 `model-routing.md` 与 Bruce Functional Agent Registry 产生第二个权威；满足用户明确排除 `gpt-5.6-sol` 的边界。
- Rejected：在 Test Dispatch 内直接按场景选择具体模型，或增加第五个测试专用 Profile，因为会绕过 Bruce 的 fallback、Packet 和模型可用性契约。
- Reversibility：高；未来可以扩展 Bruce 的统一 Profile Registry，但必须作为独立变更，不改变本设计中的 Skill ownership。

### 决策五：API/UI 轨道状态聚合不是 Completion Gate

- Chosen：Dispatch 只聚合场景和轨道级状态；Completion Gate 仍是唯一最终完成判断。
- Rationale：复用 Joytime 的轨道状态优先级，同时遵守 Bruce 的单一终态 authority。
- Rejected：让 Test Dispatch 直接返回或代替 `Completion`，因为会形成第二个 Gate。
- Reversibility：高；轨道状态字段可扩展，但不得改变唯一 Completion ownership。

## 契约

- `api-contracts.md#shared-scenario-contract` — 共享场景文件契约。
- `api-contracts.md#track-dispatch-contract` — API/UI 轨道调度输入、权限和 Packet 边界。
- `api-contracts.md#track-result-and-status-aggregation` — 轨道结果、证据和状态聚合契约。
- `api-contracts.md#browser-execution-ownership` — 浏览器执行权、证据来源和子代理禁止项。
- `api-contracts.md#model-routing-ownership` — 测试场景与 Bruce resolver 的模型路由边界。

## 横切行为

- Compatibility/versioning：Scenario、Dispatch Packet 和轨道结果均带 `version`；对已有项目场景采用增量字段和显式 `scenario_version`，不覆盖历史运行证据。Joytime 原有场景可通过项目适配层映射，不要求立即迁移。
- Authentication/authorization：账号和凭证只引用已确认 Environment Profile 的 alias/pool/ref；测试轨道不得记录密码、Token、Cookie、API Key、数据库 URL 或模型密钥。浏览器登录、Captcha 和用户控制 task space 仍按 Provider handoff 规则处理。
- Failure and recovery：缺失环境 operation、服务、Worker、Provider、账号或权限时为 `blocked`；API 失败为 `failed`；证据不完整为 `executed`/`issues`，不得静默降级测试模式、换 Provider、换模型或降低 visual scope。修复后重跑原始失败场景和相关回归。
- Observability：API 记录脱敏请求/响应、状态转换、polling、持久化回读和实际命令；UI 记录 Provider、target、session、真实动作、可见结果、截图和必要几何；聚合记录每条轨道的 evidence refs、revision、namespace 和未验证门禁。
- Rollout/rollback：先落地规范、Profile 映射和契约测试，再为项目增加适配 Skill/场景；不修改业务代码或数据库。若适配不兼容，移除项目 Skill 选择即可回退到已有验证路径，不改变 Environment Profile 的历史确认记录。
- Security：默认只允许 Profile 已声明的 operation；数据库 reset/drop、migration、生产、远程部署和凭证轮换保持显式授权。UI 轨道不得通过 API 补齐页面失败状态。

## 验证影响

- Shared Scenario Contract -> 契约校验必须覆盖唯一 ID/version、API/UI 步骤隔离、数据 namespace、状态和 evidence 字段。
- Track Dispatch Contract -> 测试必须覆盖 `api`、`ui`、`both`、不同 execution mode、缺少前置条件、不同场景版本和写入路径冲突。
- API Verification Track -> 至少覆盖请求链、保存变量、负例、bounded polling、终态 allowlist、持久化回读、脱敏和 memory/real-http/live-acceptance 边界。
- Browser UI Verification Track -> 由主 Agent/Provider 进行真实交互测试；契约测试只验证 Provider/证据边界，不能用静态测试伪造浏览器通过。
- Model Routing -> 契约测试必须验证测试 Skill 不引入 `gpt-5.6-sol`，且所有 Subagent 路由经过 Bruce resolver 和 `model_resolution`。
- Completion integration -> Completion Gate 复核场景和轨道证据，必须区分轨道 `passed` 与最终 `Completion`。

## 开放决策

- 无。用户已冻结本阶段的浏览器执行权和模型范围；后续实现时仍需由 Bruce 根据具体项目确认场景存储路径、测试命令和 Environment Profile operation ID，这些不应在通用核心中硬编码。
