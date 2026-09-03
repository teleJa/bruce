# Implementation plan: Bruce 通用测试验证编排与轨道调度

## Task contract

- Objective: 新增三个项目无关的 Bruce testing skills，使 Agent 能从已确认的 Environment Profile 和 Requirement Verification Profile 锁定共享业务场景，生成或执行 API 编排验证，由主 Agent 使用配置的 Browser Provider 完成真实页面验收，并以统一轨道结果供 Verification Run/Checkpoint 和 Completion Gate 使用。
- Scope: 包含 `test-dispatch`、`api-test-orchestration`、`browser-ui-verification` 三个 Skill，Scenario/Dispatch/Track Result 契约及确定性校验/聚合脚本，Verification Profile/Verification Loop/Completion Gate 对接，agents metadata、README/CONTEXT 和契约测试；排除 Joytime 业务代码和项目硬编码、数据库 schema/migration、Playwright 迁移、浏览器 runtime、子代理浏览器权限、第五类 Functional Agent Profile、`gpt-5.6-sol`、真实生产/远程环境操作、插件刷新、commit 和 push。
- Acceptance:
  - TVO-01: 共享 Scenario v1 能稳定表达 feature area、business flow、actor、environment ref、API/UI 步骤、隔离 namespace、前置条件、断言、持久化、证据和状态，并拒绝缺失 ID/version、API/UI 语义混用及竞争版本。
  - TVO-02: `api-test-orchestration` 能指导 Agent 按真实项目路由和测试约定生成/维护 API 场景，区分 memory-application、real-http、live-acceptance，执行 bounded polling、负例、权限和权威持久化回读，不用 HTTP 200 或 Job created 冒充通过。
  - TVO-03: `browser-ui-verification` 明确只有主 Agent/宿主可操作 `ego-lite|chrome`，API 只能准备/清理/权威核对，子代理 browser access 必须拒绝，Provider 不可用或需要人工接管时保持 blocked/waiting_user。
  - TVO-04: `test-dispatch` 锁定一个共享 Scenario ID/version，选择 api/ui/both，分配互相隔离的数据 namespace 和写入范围，并按 failed > blocked > passed > executed > designed 聚合状态；不同版本或写入冲突必须 blocked。
  - TVO-05: 所有测试 Subagent 都通过 Bruce Functional Agent Profile/resolver 产生 `model_resolution`；新能力不得引用 `gpt-5.6-sol`、不得新增私有 model router，Luna 仍只允许 max，浏览器动作不进入 Subagent Packet。
  - TVO-06: Requirement Verification Profile 能选择三个通用 Skill/能力并把 Acceptance、Environment Profile、账号、场景、轨道和证据边界关联起来，不复制环境全文或写入运行结果。
  - TVO-07: Verification Run/Checkpoint 和 Completion Gate 能消费轨道结果及 evidence revision，保持场景状态与唯一 `Completion` 分离，并在 stale、缺证据、Provider/operation unavailable 时 fail-closed。
  - TVO-08: 新 Skill metadata、链接、模板/脚本、contract tests、plugin validation 和全量回归通过；Joytime 项目文件和当前无关工作区改动保持不变，外部运行时证据单独报告。
- Constraints: 默认使用简体中文说明和英文稳定标识；只实施局部 Skill/contract/test 变更；保持 Codex Host 对浏览器和 Subagent 生命周期的权威；所有数据库破坏性、生产、远程部署和凭证操作维持显式授权；先检查并保留当前 Environment Profile 相关未提交修改，任何冲突必须停止合并而非覆盖。
- Topology: full；变更跨三个新 Skill、公共 Scenario/Result 文件契约、Verification Profile、Browser Provider、Functional Agent 路由和 Completion Gate，并需要冻结任务与多层验证。
- Risk: guarded；共享测试契约或路由错误会导致错误测试模式、浏览器权限越界、证据误聚合或虚假 Completion，但不涉及数据库迁移、生产部署或不可逆业务数据操作。

## Task package

- Path: `tasks/`
- Index: `tasks/index.yaml`
- Contract state: task files are frozen before their task starts
- Status source: `checkpoint.yaml` or the current checkpoint message
- Execution mode: `sequential`
- Omission reason: none

## Task summary

| Task ID | Title | Depends on | Acceptance IDs | Allowed paths | Verification layer |
|---|---|---|---|---|---|
| T-001 | 冻结共享 Scenario 与轨道结果契约 | none | TVO-01, TVO-04, TVO-07 | `skills/test-dispatch/references/**`, `skills/test-dispatch/scripts/**`, dispatch contract tests | unit/contract |
| T-002 | 增加通用 API 编排验证 Skill | T-001 | TVO-01, TVO-02 | `skills/api-test-orchestration/**`, API contract tests | contract/integration design |
| T-003 | 增加主 Agent 页面验收 Skill | T-001 | TVO-01, TVO-03 | `skills/browser-ui-verification/**`, browser UI contract tests | contract/browser-boundary |
| T-004 | 增加测试轨道调度与模型路由约束 | T-001, T-002, T-003 | TVO-04, TVO-05 | `skills/test-dispatch/**`, dispatch/Functional Agent tests | unit/contract |
| T-005 | 接入 Verification Profile、Loop 与 Completion Gate | T-004 | TVO-06, TVO-07 | verification-profile、Bruce references、Completion Gate 及定向 tests | integration/contract |
| T-006 | 更新插件文档、metadata 与全量回归 | T-005 | TVO-08 | README、CONTEXT、plugin metadata、supporting-skill/tests | repository/full |

Detailed frozen contracts live in `tasks/T-ID-short-slug.md`. Do not duplicate their full scope or acceptance here; update a task contract only through an explicit revision or superseding task.

## Repository evidence

- `skills/environment-profile/references/profile-schema.md` — 已有环境、授权、operation 和 preflight 的单一结构化来源。
- `skills/verification-profile/SKILL.md` 与 `references/profile-schema.md` — 已有 `skill_selections`、Acceptance stage 和环境/账号引用位置。
- `skills/bruce/references/browser-provider.md`、`scripts/browser_provider.py` — 已有 `ego-lite|chrome` 选择、visual scope 和统一 browser evidence。
- `skills/bruce/references/model-profiles.yaml`、`scripts/functional_agent_profiles.py` — 已有四 Profile、Luna/Terra 配置、resolver、fallback 和 Packet 校验。
- `skills/bruce/references/verification-loop.md`、`skills/completion-gate/SKILL.md` — 已有 evidence revision、验证层级和唯一 Completion authority。
- Joytime 三个参考 Skill — 已验证共享场景、API 状态编排、页面真实交互和轨道聚合的项目级方法，但包含 Joytime 路径和私有模型路由，不能原样复制。
- `tests/test_supporting_skill_contracts.py`、`tests/test_functional_agent_profiles.py`、`tests/test_browser_provider.py` — 当前可扩展的 Skill、模型和浏览器契约测试入口。

## Dependency and risk notes

- T-001 先冻结机器可校验的 Scenario/Result schema，避免三个 Skill 分别定义同名字段。
- T-002 与 T-003 在概念上独立，但为避免新增目录、公共引用和测试注册产生交叉写入，计划仍按 Bruce 默认 sequential 执行。
- T-004 是唯一 dispatch owner；API/UI Skill 不得直接选择具体模型或聚合整体状态。
- T-003 与 T-004 必须共同保证 `subagent_browser_access=forbidden`；不能通过修改 `verifier` tools 放开 browser。
- T-005 会接触当前已有未提交修改的 `skills/verification-profile/SKILL.md`。执行前必须检查现有 diff，只做兼容增量；若现有修改与本合同冲突，停止并创建新 contract revision，不能覆盖。
- 本变更不改变 `skills/bruce/references/model-profiles.yaml` 中的 Profile 集合和默认模型；任何提出 `gpt-5.6-sol` 或第五 Profile 的实现均越界。
- 真实 Joytime API/UI 执行不是仓库内 Completion 的默认前置；项目适配和真实运行证据必须在后续目标项目任务中单独完成和报告。

## Whole-change verification

- TVO-01 -> Given 合法/非法 Scenario fixtures；When 运行 Scenario validator；Then 合法场景通过，缺 ID/version、混用步骤、namespace 冲突和不同版本失败 -> T-001 -> unit/contract -> 新 validator tests。
- TVO-02 -> Given 三种 API mode 和异步/持久化场景；When 检查 Skill/参考规范和 fixtures；Then 无静默降级、bounded polling、负例和权威回读均被要求 -> T-002 -> contract/integration design -> API Skill contract tests。
- TVO-03 -> Given UI 场景和配置 Provider；When 读取/执行 Skill contract；Then 只有主 Agent 能执行真实页面动作，子代理和 API shortcut 被拒绝 -> T-003 -> contract/browser-boundary -> browser UI contract tests 与 browser-provider regression。
- TVO-04 -> Given api/ui/both track results；When 运行聚合器；Then namespace/版本/写入冲突 fail-closed，状态优先级正确 -> T-004 -> unit/contract -> dispatcher aggregation tests。
- TVO-05 -> Given测试调度请求；When 创建 Functional Agent Task Packet；Then 经过 resolver、有 `model_resolution`、无 Sol/私有 router/browser tool -> T-004 -> unit/contract -> Functional Agent/dispatch tests。
- TVO-06 -> Given Requirement Verification Profile acceptance；When 选择测试 Skill；Then skill/environment/account/scenario/track/evidence 映射完整且静态/动态边界不变 -> T-005 -> integration/contract -> verification-profile tests。
- TVO-07 -> Given passed/failed/blocked/stale 轨道结果；When Verification Loop/Completion Gate 消费；Then 轨道状态不变成平行 Completion，缺证据和 stale fail-closed -> T-005 -> integration/contract -> validation-loop/completion tests。
- TVO-08 -> Given全部变更；When 运行全量 unittest、Functional Agent、plugin validator 和 `git diff --check`；Then仓库内契约通过且外部运行边界如实报告 -> T-006 -> repository/full。

## Delivery boundary

- 仅修改当前 Bruce 工作区中任务合同允许的文件；不修改 Joytime 仓库、不刷新插件、不 commit、不 push、不部署、不执行生产或破坏性操作。
