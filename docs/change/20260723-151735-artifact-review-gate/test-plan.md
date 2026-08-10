# Test plan: Bruce 设计产物完整性门禁

## Acceptance mapping

| Acceptance | Scenario | Verification layer | Evidence |
|---|---|---|---|
| AR-01 | artifact-review-required | component | `python -m unittest tests.test_workflow_profiles tests.test_supporting_skill_contracts -v` |
| AR-02 | missing-or-unjustified-artifact-blocks | component | `python -m unittest tests.test_supporting_skill_contracts -v` |
| AR-03 | execute-record-is-not-design-gate | component | `python -m unittest tests.test_execution_contract -v` |
| AR-04 | stale-gate-fails-completion | component | `python -m unittest tests.test_completion_contract -v` |

## Preconditions and real dependencies

- Python 标准库 `unittest`。
- 仓库内 skill Markdown、模板、manifest 和 validator。
- 不需要数据库、网络、浏览器或外部服务。

## State and intent matrix

| Pre-state | User/system intent | Expected behavior | Data consequence |
|---|---|---|---|
| full task，设计未检查 | 进入实现 | 缺少 `artifact-review.md` 时阻塞 | 不创建执行阶段状态 |
| required 产物存在并通过评审 | 进入实现 | artifact gate pass | 生成/更新同级门禁文件 |
| candidate 被跳过但无证据 | 进入实现 | artifact gate blocked | 门禁文件记录具体缺口 |
| Goal-backed 且门禁已通过 | 开始执行 | Goal 只消费门禁路径和结论 | `execute_record.md` 不复制设计决策 |
| 最终 diff 扩大 schema/contract 范围 | 报告完成 | completion 返回 issues | 更新原门禁文件后重跑 |

## Scenarios

### artifact-review-required

- Maps to: AR-01、artifact-gate-1、artifact-gate-2
- Type: happy/regression
- Given: full 任务或 standard 任务已生成下游设计真源。
- When: Bruce 准备开始行为实现。
- Then: 当前 change 目录存在 `artifact-review.md`，完整列出候选集合且结论为 pass。
- Evidence: workflow 与 supporting skill contract assertions。
- Required layer: component

### missing-or-unjustified-artifact-blocks

- Maps to: AR-02、artifact-gate-1
- Type: error
- Given: required 产物缺失、候选项遗漏，或 skipped 没有 repository-backed evidence。
- When: artifact review gate 判定。
- Then: 返回 blocked，禁止进入 Goal/行为实现。
- Evidence: `tests/test_supporting_skill_contracts.py`。
- Required layer: component

### execute-record-is-not-design-gate

- Maps to: AR-03、artifact-gate-3
- Type: regression
- Given: full 任务已经通过 artifact gate。
- When: Goal execution gate 创建执行记录。
- Then: 只引用 `artifact-review.md` 路径和 pass，不写入 test/table design 跳过理由。
- Evidence: `tests/test_execution_contract.py`。
- Required layer: component

### stale-gate-fails-completion

- Maps to: AR-04、artifact-gate-3
- Type: error/regression
- Given: 实现 diff 引入原 artifact review 未覆盖的公共契约或 persistence schema 影响。
- When: verify-completion 复核。
- Then: 返回 issues，不允许以旧 pass 完成。
- Evidence: `tests/test_completion_contract.py`。
- Required layer: component

## Regression sources

- `system-namespace` 任务仅在 `execute_record.md` 声称 D1 通过，同级目录没有 table-design 跳过证据 -> artifact-review-required。
- full test-design 修复曾把 skip decision 写入 `execute_record.md` -> execute-record-is-not-design-gate。
- 当前测试只强制 API contract artifact -> missing-or-unjustified-artifact-blocks。

## Limits

- 静态 contract tests 验证 Bruce 指令和打包契约，不证明外部业务仓库已自动补写历史门禁文件。
- 本次不刷新本机插件缓存，因此安装态 smoke 不在完成边界。

## Self-check

- AR-01 至 AR-04 均映射到可执行证据。
- 错误场景覆盖缺文件、缺候选、无跳过证据和实现后门禁过期。
- Goal 与设计阶段职责有独立回归。
- 命令和文件均存在于当前仓库。
