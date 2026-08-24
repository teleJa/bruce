# Architecture: Bruce 功能型 Agent 与 Model Profile 路由

## Objective and scope

- Objective: 将 Bruce 的原生 Subagent 委派统一收敛到可验证的 Functional Agent Profile 与 Packet 合同，并保留 Codex 宿主对生命周期、工具和最终 Gate 的权威。
- Included: 四类 P0 Profile、三层 Profile 覆盖解析、Task/Verification/Review Packet、模型解析审计、Inspector/Implementer/Verifier/Reviewer 调用 Skill 的合同接入、静态校验与契约测试。
- Excluded: 自建调度器、Worker Registry、常驻 Runtime、模型服务、权限代理、数据库/业务 schema、生产部署、插件安装刷新、commit/push。

## Repository evidence

- `skills/bruce/SKILL.md` — Bruce 已明确由 Codex 管理工具、文件、命令、原生 Goal 与 Subagent 生命周期，Bruce 不创建第二运行时。
- `skills/inspect-parallel/SKILL.md` — 当前 Explorer 只读、主 Agent 保留综合与决策，适合作为 `inspector` Profile 的消费方。
- `skills/spawn-execute/SKILL.md` — 当前 bounded executor 只返回 task evidence，不决定 Gate，适合作为 `implementer` Profile 的消费方。
- `skills/completion-gate/SKILL.md` 与 `skills/plan-review/SKILL.md` — 已存在 clean-context 独立审查边界，分别承载 `reviewer`；验证证据继续由主 Agent/Gate 消费。
- `tests/test_completion_contract.py`、`tests/test_execution_contract.py`、`tests/test_supporting_skill_contracts.py` — 现有静态合同测试可扩展，不需要引入新测试运行时。

## Components and ownership

| Component | Existing stack/deliverable | Owns | Does not own |
|---|---|---|---|
| Profile Registry | `skills/bruce/references/model-profiles.yaml` | 内置 Profile、能力、默认模型、推理强度、工具/权限和 fallback | 实际启动模型、宿主能力探测 |
| Contract Resolver | `scripts/functional_agent_profiles.py` | 合并覆盖层、校验 Profile/Packet、生成 `model_resolution` 和宿主调用参数 | 调度器、模型服务、权限代理 |
| Routing Skills | `skills/inspect-parallel`、`spawn-execute`、`explore-prototype`、`completion-gate`、`plan-review`、`design-gate` | 声明 Profile ID、输入 Packet、输出 Packet、上下文/权限边界 | 选择最终业务方案、Design/Completion terminal verdict |
| Gate and Evidence | 现有 Design/Completion Gate 与 `verification-loop.md` | 验收、证据综合、最终 `Design`/`Completion` 决定 | Verifier/Reviewer 平行 verdict、第二证据账本 |
| Contract Tests | `scripts/validate_functional_agents.py`、`tests/test_functional_agent_profiles.py` | 静态 registry、schema、路由映射、降级语义验证 | 真实模型可用性证明、插件安装/外部交付 |

## Data and control flow

1. Skill 根据任务类型选择 `profile_id`，构造 `task_packet`，声明当前模型和可用宿主能力。
2. Contract Resolver 依次合并 task > project > user > built-in；当目标模型未被宿主确认可用时，若允许 `fallback=current`，省略 `model` 参数并继承当前模型。
3. Resolver 返回 `model_resolution`（请求 Profile、配置模型、有效模型、是否降级、原因、状态）和安全的 `spawn_agent` 参数映射。
4. Codex 宿主负责创建/运行原生 Subagent；Agent 只能在 Packet 声明的上下文、工具和路径边界内工作。
5. Agent 返回对应 Packet：Inspector/Implementer 使用 `task_evidence_packet`，Verifier 使用 `verification_packet`，Reviewer 使用 `review_packet`。
6. 主 Agent 综合依赖、冲突、业务决策和证据，Design Gate/Completion Gate 仍分别输出唯一 terminal verdict。

## Decisions

### D-01：Profile 是内部版本化合同，而不是第五套 Skill 或 Runtime

- Chosen: Profile ID、Packet schema 和解析器作为 `skills/bruce/references/` 与 `scripts/` 的内部公共合同。
- Rationale: 当前插件只有 Skills + hooks；新增可发现 Skill 会错误地把内部角色暴露给用户，新增 Runtime 又越过 Codex Host Authority。
- Rejected: Worker Registry、provider-specific selector、常驻 dispatcher；它们扩大权限与状态边界且不满足计划排除项。
- Reversibility: 可通过删除路由片段和 registry 条目回退；Packet v1 保留向后兼容字段策略。

### D-02：Profile 覆盖采用文件层级合并，模型解析与实际生效分离

- Chosen: built-in `skills/bruce/references/model-profiles.yaml`，user `~/.codex/bruce/model-profiles.yaml`，project `project/.bruce/model-profiles.yaml`，task 显式 override；优先级 task > project > user > built-in > current fallback。
- Rationale: 用户和项目覆盖可版本化/隔离，且不污染既有 `.bruce/config.yaml`；解析器不能把配置文件当成模型已生效证据。
- Rejected: 将个人模型写进项目配置或在每个 Skill 内重复 selector。
- Reversibility: 覆盖文件删除即可回到内置 Profile。

### D-03：模型 fallback 必须显式降级

- Chosen: Profile 模型不可用时，若 `fallback=current` 则省略 `model` 以继承 current model，输出 `fallback_used=true`、`capability_status=degraded`、`resolution_result=fallback`；同模型不宣称异构。
- Rationale: 宿主是实际模型生效的唯一证据源；不可用模型不能阻断允许 fallback 的低风险委派，也不能伪装独立性。
- Rejected: 从 YAML 推断模型成功，或自建 provider runtime 绕过宿主。
- Reversibility: 关闭 fallback 或提供 host capability 即可切换回 resolved/blocked。

### D-04：Verifier/Reviewer 只返回证据 Packet，不返回 Gate verdict

- Chosen: `verification_packet` 复现验收证据，`review_packet` 记录独立审查发现；terminal verdict 只由 Design/Completion Gate 生成。
- Rationale: 保持现有两 Gate 权威数量，避免“多 Agent 多结论”造成不可综合的第二账本。
- Rejected: Reviewer approval、Verifier pass、每个 finding 一个 review chain。
- Reversibility: Packet 是输入合同，不改变既有 Gate 输出。

## Cross-cutting behavior

- Compatibility/versioning: 所有 Profile/Packet 使用 `schema_version: 1`；旧 Skill 文本继续保留主 Agent 和 Gate 权威语义，迁移仅添加明确 Profile/Packet 约束。
- Authentication/authorization: 不新增权限代理；Inspector `write_scope=none`，Implementer 仅允许 `Task Packet.allowed_paths`，Resolver 拒绝越权路径、未知字段和禁止工具。
- Failure and recovery: `invalid`/`blocked` fail closed；目标模型、clean context 或工具不可用时按能力要求决定 fallback/degraded/blocked，并记录 L0-L4 所需原因，不重放未知外部副作用。
- Observability: 每次委派的 `model_resolution` 和 Packet evidence 记录 requested/configured/effective model、fallback、能力状态、变更路径、命令结果和 evidence gaps。
- Rollout/rollback: 先启用静态校验与路由合同，再逐点迁移 Skill；任一合同不合法时阻断调用并回退到主 Agent 直接执行，删除覆盖文件可回到 built-in Profile；本轮不安装插件、不发布。

## Verification impact

- FA-01/FA-02: Profile validator、registry/fixture/schema 契约测试与全部 native-subagent 文本调用点矩阵。
- FA-03/FA-06: resolver 单元测试覆盖 task/project/user/built-in/fallback、目标模型 unavailable、当前模型 unavailable、clean context/tool unavailable。
- FA-04: 静态测试拒绝 `Design`/`Completion` terminal field 出现在 Verifier/Reviewer Packet。
- FA-05: 路径权限与 Inspector 只读测试、受控 smoke packet；主 Agent复核工作区。
- FA-07: `python3 -m unittest discover -s tests -p 'test_*.py'`、`python3 scripts/validate_plugin.py`、`python3 scripts/validate_functional_agents.py`、`git diff --check`。

## Open decisions

- None. 目标模型的实际可用性仍由当前 Codex 宿主在运行时提供证据；本仓库只定义解析与记录合同，不伪造 smoke 结果。
