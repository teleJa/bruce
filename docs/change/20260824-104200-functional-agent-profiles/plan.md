# Implementation plan: Bruce 功能型 Agent 与 Model Profile 路由

## Task contract

- Objective: 将 Bruce 现有的临时通用 Subagent 调用收敛为可验证的功能型 Agent 合同，并由 Bruce 维护可版本化的 Model Profile（能力描述、默认模型名称、推理强度和 fallback 策略），使 Inspector、Implementer、Verifier、Reviewer 具备稳定的上下文、权限、模型、证据和输出边界；用户可覆盖具体模型名称，目标模型不可用时默认回退到当前模型并显式记录降级。
- Scope:
  - Included: 功能型 Agent 公共合同与四类 Profile；`skills/bruce/references/model-profiles.yaml` 内置注册表；`~/.codex/bruce/model-profiles.yaml` 用户覆盖与 `project/.bruce/model-profiles.yaml` 项目覆盖边界；Task/Verification/Review Packet schema；现有原生 Subagent 调用点的 Profile 路由接入；显式 model override、当前模型 fallback 和解析结果记录；静态校验、契约测试、宿主运行 smoke、README 和插件元数据更新。
  - Excluded: 自建调度器、Worker Registry、常驻进程、模型服务、权限代理、第二套状态/证据账本；数据库、业务 schema、生产部署；改变 Design Gate、Completion Gate、Goal 和 Checkpoint 的权威数量；把人格 Prompt 当作功能合同；未经确认安装/刷新本机 Bruce 插件、提交、推送或发布。
- Acceptance:
  - FA-01: Given Bruce 需要委派一个边界清晰的任务；When 创建原生 Subagent；Then 调用方必须选择一个 Functional Agent Profile，并传入满足 schema 的 Task Packet，明确目标、上下文继承、允许/禁止工具、写入范围、模型能力、证据、输出和停止条件；Evidence: Profile validator、契约测试和调用点静态检查。
  - FA-02: Given P0 功能 Agent 集合；When 检查 Profile；Then Inspector、Implementer、Verifier、Reviewer 四类合同均存在，职责互斥部分明确，所有当前 Subagent 调用点均映射到一个 Profile 或记录有证据的延期理由；Evidence: Profile 清单、调用点矩阵和契约测试。
  - FA-03: Given Completion Gate 命中独立审查条件；When 启动 Reviewer；Then Reviewer 加载 `reviewer` Model Profile，使用不继承作者对话的干净上下文，并优先通过显式 model override 使用 Profile 模型；Profile 模型不可用时按 `fallback=current` 回退到当前模型，记录 `fallback_used`、`effective_model` 和 `capability_status=degraded`，不得把同模型执行描述为已完成模型异构；只有当前模型也不可用或任务/风险明确禁止 fallback 时才 blocked；Evidence: review-mode 测试、模型解析测试和宿主 smoke 记录。
  - FA-04: Given 实现已产生候选结果；When 进入验证和审查；Then Verifier 只生产可复现的 `verification_packet`，Reviewer 只生产独立的 `review_packet`，两者都不能返回平行的 Design 或 Completion verdict；最终仍只有 `Design: pass|blocked` 和 `Completion: pass|issues|blocked`；Evidence: Completion/Design/Execution 契约测试。
  - FA-05: Given Inspector 或 Implementer 执行；When Agent 返回；Then Inspector 保持只读并引用仓库事实，Implementer 只能修改 Task Packet 允许的路径并返回实际变更与验证证据，主 Agent 继续负责综合、依赖顺序、冲突、业务决策、集成和最终 Gate；Evidence: 权限/路径/输出 schema 测试及受控运行 smoke。
  - FA-06: Given 当前宿主不支持 Profile 目标模型、干净上下文或所需工具；When 路由失败；Then 先按用户覆盖、Bruce 默认 Profile、当前模型 fallback 的优先级解析；允许 fallback 时省略 model override 以继承当前模型，并记录 `resolved|fallback|degraded|blocked`、原因和有效模型；不得静默丢失降级信息，也不自建 Runtime 绕过宿主能力；Evidence: 失败策略测试和降级 fixture。
  - FA-07: Given 功能型 Agent 改造完成；When 执行静态与运行验证；Then 现有 Bruce 回归测试、插件校验和 diff 检查通过，并分别报告 Profile/Packet 合同验证、实际 model override、当前模型 fallback、真实 Subagent smoke、插件安装/Chrome/外部交付中已执行与未执行的层级；Evidence: 命令输出、`model_resolution` packet、smoke packet 和 Completion Gate 矩阵。
- Constraints:
  - 默认使用 Codex 原生 Subagent 生命周期和当前宿主工具面，不增加 provider-specific Runtime。
  - 功能差异首先来自合同、上下文、权限、证据和权威边界；不同模型是可配置增强，不能替代干净上下文与证据验证。
  - Bruce 内置 Model Profile 同时维护能力描述和默认具体模型名称；Skill 只引用 Profile ID，不直接绑定模型名。
  - 用户可在明确的覆盖层修改 Profile 模型名称；覆盖优先级为任务级显式覆盖 > 用户/项目覆盖 > Bruce 默认 Profile > 当前模型 fallback。
  - 当前模型 fallback 是默认可用策略；fallback 必须记录实际模型和 `degraded` 状态。`required|preferred|none` 控制能力/独立性声明和 Gate 充分性，不得把 fallback 结果标记为 `resolved` 或异构完成。
  - 所有新增自然语言文档使用简体中文，稳定字段、状态、路径和 schema token 使用英文。
  - 保留当前未跟踪的 `.serena/` 和 现有未跟踪的待办文件，不纳入本变更。
- Topology: `full`。该改造横跨 Bruce 主路由、Inspection、Goal Delegation、Verification、Completion Review、Plan Review、Prototype Generation、失败恢复、插件校验和测试；并引入由多个调用方消费的 Functional Agent/Profile/Packet 公共合同。
- Risk: `guarded`。它改变 Bruce 的公共工作流、独立审查可信度、模型成本与降级语义，但不涉及数据库、生产基础设施或不可逆外部写入。

## Task package

- Path: `tasks/`
- Index: `tasks/index.yaml`
- Contract state: task files are frozen before execution
- Status source: `checkpoint.yaml`
- Execution mode: `sequential`
- Omission reason: none; this is a full, cross-component contract change.

## Task summary

| Task ID | Title | Depends on | Acceptance IDs | Allowed paths | Verification layer |
|---|---|---|---|---|---|
| T-001 | 冻结 Functional Agent 与 Model Profile 公共合同 | none | FA-01、FA-02、FA-03、FA-04、FA-06 | change package、Profile refs | document + Design Gate |
| T-002 | 增加 Profile、Packet schema 与静态校验 | T-001 | FA-01、FA-02、FA-04、FA-06 | scripts、references、tests | unit/contract + validator |
| T-003 | 接入 Inspector 与 Implementer 路由 | T-002 | FA-02、FA-05、FA-06 | inspect/spawn/explore skills | unit/contract + smoke |
| T-004 | 分离 Verifier 与 Reviewer 证据边界 | T-002 | FA-02、FA-03、FA-04、FA-06 | gate/review skills | unit/contract + smoke |
| T-005 | 接入 Model Profile 覆盖、显式 override 与当前模型 fallback | T-002、T-003、T-004 | FA-03、FA-06、FA-07 | resolver、references、skills、tests | resolver/fallback |
| T-006 | 更新插件文档、元数据与全量回归 | T-003、T-004、T-005 | FA-07 | README、CONTEXT、plugin、tests | full regression |

详细冻结合同位于 `tasks/T-id-short-slug.md`，状态只由 `checkpoint.yaml` 或当前 checkpoint 提供。

## Repository evidence

- `skills/bruce/SKILL.md` — Codex 管理 Subagent 生命周期，主 Agent 负责综合、Profile、任务合同、集成与最终 Gate。
- `skills/inspect-parallel/SKILL.md` — 只读 Explorer，不选择 provider-specific agent/model/token budget。
- `skills/spawn-execute/SKILL.md` — bounded executor 返回 task evidence packet，不实现 model selector。
- `skills/completion-gate/SKILL.md` — clean-context independent review 与唯一 Completion verdict。
- `skills/plan-review/SKILL.md` — clean-context plan reviewer 的现有边界。
- `skills/explore-prototype/SKILL.md` — generation worker 复用 Implementer，不增加第五种 Agent。
- `tests/test_completion_contract.py`、`tests/test_execution_contract.py`、`tests/test_supporting_skill_contracts.py`、`tests/test_workflow_profiles.py` — 可扩展的静态契约测试。
- `.codex-plugin/plugin.json` — Bruce 是 skills + hooks 插件，没有 CLI、MCP Server 或 Agent Runtime。
- `.bruce/config.yaml` — 仅配置 artifact root；个人模型配置不写入该文件。

## Model Profile storage and resolution

- Built-in registry: `skills/bruce/references/model-profiles.yaml`。
- User override: `~/.codex/bruce/model-profiles.yaml`，不进入项目仓库。
- Project override: `project/.bruce/model-profiles.yaml`，仅允许项目约定，不包含个人凭证或本机路径。
- Task override: 当前 Task Packet 的显式 `model` 或 Profile override，仅当前任务生效。
- Precedence: `task override > project override > user override > built-in Profile > current model fallback`。
- Resolution: 目标模型经宿主确认可用才传 `model`；不可用且允许 fallback 时省略 `model` 并继承当前模型。
- Audit: 每次委派产出 `model_resolution`，至少记录 `requested_profile`、`configured_model`、`effective_model`、`fallback_used`、`fallback_reason`、`capability_status` 和 `resolution_result`。

## Whole-change verification

- FA-01 -> T-001/T-002 -> `test_task_packet_schema_and_invalid_variants` + Profile validator。
- FA-02 -> T-002/T-003/T-004 -> registry 与 Skill 路由矩阵测试，覆盖全部 native-subagent 调用点。
- FA-03 -> T-004/T-005 -> reviewer clean context、显式 override、目标模型 unavailable fallback 测试；真实宿主模型证据另列。
- FA-04 -> T-001/T-004 -> output schema 禁止 Gate terminal field，Completion/Design 仍唯一权威。
- FA-05 -> T-003 -> Inspector 只读、Implementer 路径包含校验和受控 smoke。
- FA-06 -> T-002/T-005 -> user/project/task precedence、invalid config、model/context/tool unavailable 的 failure matrix。
- FA-07 -> T-006 -> `python3 -m unittest discover -s tests -p 'test_*.py'`、`python3 scripts/validate_plugin.py`、`python3 scripts/validate_functional_agents.py`、`git diff --check`。

## Delivery boundary

- 本轮允许在当前工作区完成设计产物、Profile/Packet 合同、Skill/脚本/测试/文档改造和静态验证。
- 不执行真实模型 Subagent smoke、插件安装/刷新、Chrome、部署、commit 或 push；这些证据单独报告为未执行。
