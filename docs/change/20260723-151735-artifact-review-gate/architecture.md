# Architecture: Bruce 设计产物完整性门禁

## Objective and scope

- Objective: 在行为实现前生成与设计文档同级的 `artifact-review.md`，完整记录候选设计产物的生成或跳过结论，并阻止缺失、无证据或未通过评审的设计进入实现。
- Included: Bruce 主路由、独立 artifact review gate、Goal 入口边界、完成复核、插件版本元数据和契约测试。
- Excluded: 业务仓库数据库 schema、Codex 原生 Goal 状态、执行日志格式、历史 change 目录批量补写和本机插件安装。

## Repository evidence

- [`skills/bruce/SKILL.md`](../../../skills/bruce/SKILL.md) — 当前只对 `api-contracts.md` 和 full test-design 做专项判断，没有统一候选产物清单。
- [`skills/write-db-design/SKILL.md`](../../../skills/write-db-design/SKILL.md) — 数据库设计不需要时只返回 `not needed`，不会在 change 目录留下跳过证据。
- [`skills/goal-execution-gate/SKILL.md`](../../../skills/goal-execution-gate/SKILL.md) — `execute_record.md` 是执行阶段的人类审计记录，不是设计产物放行凭证。
- [`tests/test_supporting_skill_contracts.py`](../../../tests/test_supporting_skill_contracts.py) — 当前只有 API 契约的必需产物测试，没有通用 artifact gate 契约。

## Components and ownership

| Component | Existing stack/deliverable | Owns | Does not own |
|---|---|---|---|
| Bruce 主入口 | `skills/bruce/SKILL.md` | 选择设计能力、要求门禁通过、控制进入实现 | 代替各设计技能生成内容 |
| Artifact Review Gate | 新增 `skills/artifact-review-gate/` | 候选产物清单、required/generated/skipped 判定、同级落盘和阻塞结论 | 修改被检查设计文档、执行代码 |
| Goal Execution Gate | `skills/goal-execution-gate/SKILL.md` | 门禁通过后的执行持久化与证据记录 | 保存设计产物取舍或替代 `artifact-review.md` |
| Completion Review | `skills/verify-completion/SKILL.md` | 对照最终 diff 复查门禁是否仍然完整、当前 | 在完成阶段补造设计证据 |

## Data and control flow

1. Bruce 根据任务和仓库事实选择必要的设计能力。
2. 各设计能力生成所需文档，或把 `not needed` 及证据返回 Bruce。
3. `artifact-review-gate` 在同一 change 目录生成或更新 `artifact-review.md`，逐项检查需求/澄清、架构、API 契约、表设计、开发计划和测试计划。
4. 只有 `Artifact gate: pass` 才允许创建/接续执行阶段 Goal 并开始行为实现。
5. 实现范围变化时更新同一 `artifact-review.md` 并重新放行；完成复核再按最终 diff 检查其完整性和时效性。

## Decisions

### 使用独立同级门禁产物

- Chosen: 固定使用 change 目录同级的 `artifact-review.md`。
- Rationale: 审计者无需读取会话或执行记录即可知道哪些产物应生成、哪些被跳过及其证据。
- Rejected: 将判断仅写入对话、task contract 或 `.goal/.../execute_record.md`；这些位置不能作为设计阶段的持久放行凭证。
- Reversibility: 删除新 skill 和路由即可恢复旧行为，但旧任务重新失去完整性审计。

### 内容评审与完整性门禁分责

- Chosen: D0/D1 判断单份文档内容是否就绪；artifact gate 判断候选集合是否完整并汇总当前评审结论。
- Rationale: 避免 artifact gate 重复专业文档评审，也避免 D1 因未收到候选集合而漏掉缺失文档。
- Rejected: 仅依赖 `doc-review-gate` 对已存在文档逐份评审；它无法自动证明缺失产物是否合理。
- Reversibility: 可扩充候选集合，但不得降低 required/skipped 的证据要求。

### Goal 只消费门禁结果

- Chosen: Goal gate 只接收 `artifact-review.md` 路径和 `pass` 结论。
- Rationale: 保持设计阶段和执行阶段职责清晰。
- Rejected: 在 `execute_record.md` 复制 test-design 或 table-design 跳过原因。
- Reversibility: 执行记录仍可保留门禁路径，恢复和追踪能力不受影响。

## Contracts

- [`api-contracts.md`](api-contracts.md#artifact-review-file-v1)
- [`api-contracts.md`](api-contracts.md#design-to-execution-gate-v1)

## Cross-cutting behavior

- Compatibility/versioning: 新增治理契约；需要设计审计的旧调用路径若未生成门禁文件将被阻断。
- Authentication/authorization: 不涉及。
- Failure and recovery: 缺少门禁文件、必需产物、跳过证据或当前 D0/D1 结论时返回 blocked；补齐后更新同一文件并重跑。
- Observability: `artifact-review.md` 包含候选矩阵、证据、评审结果和最终门禁结论。
- Rollout/rollback: 先加入 skill/模板和契约测试，再切换 Bruce、Goal 与 completion 路由；不迁移历史任务。

## Verification impact

- 候选产物与阻塞规则 -> `tests/test_supporting_skill_contracts.py`。
- full 路由和 test-design 记录位置 -> `tests/test_workflow_profiles.py`。
- Goal 不再承载设计决策 -> `tests/test_execution_contract.py`。
- 最终 diff 导致门禁失效 -> `tests/test_completion_contract.py`。
- 打包和 skill 元数据 -> 完整测试集及 `scripts/validate_plugin.py`。

## Open decisions

- None。
