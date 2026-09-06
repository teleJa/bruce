# 测试计划：方案落盘后自动执行 Design Gate

## 验收映射

| Scenario | Acceptance | 层级 |
|---|---|---|
| S-01 | AC-01, AC-04 | 核心工作流契约测试 |
| S-02 | AC-02 | writer handoff 契约测试 |
| S-03 | AC-03 | artifact policy 非适用边界测试 |
| S-04 | AC-05 | 全量插件验证 |

## 场景

### S-01：核心工作流同轮衔接

- Given：用户已选择 design-only 或已授权 implementation scope，方案工件会约束后续实现。
- When：方案工件成功落盘并完成本地文档检查。
- Then：Bruce 在同一轮立即运行 `design-gate`，不等待新的用户指令；design-only 在 Gate 后停止，implementation 仅在 pass 后继续。
- Evidence：`tests/test_workflow_routing.py` 对核心规则的文本契约断言。

### S-02：writer 返回强制 handoff 而不越权裁决

- Given：architecture、database、plan、prototype 或 test writer 产出需要 Gate 的治理型工件。
- When：writer 返回成功结果。
- Then：输出要求调用方立即运行 `design-gate`，明确无需用户追加指令，同时保留 writer 不拥有 Design verdict 的边界。
- Evidence：`tests/test_document_review_contract.py` 与 `tests/test_supporting_skill_contracts.py`。

### S-03：普通文档不误触发

- Given：持久化内容只是执行清单、进度说明、现有命令列表、普通文档编辑，或原型仍未确认且不可治理。
- When：artifact policy 评估 Gate applicability。
- Then：不因文件存在而自动生成 Design Gate；只有治理型设计或下游合同触发 mandatory handoff。
- Evidence：`tests/test_workflow_policy_contract.py`、`tests/test_prototype_contract.py` 与核心 workflow 契约断言。

### S-04：插件整体回归

- Given：共享 Skill 文案与测试已更新。
- When：运行针对性和全量验证。
- Then：所有测试、插件校验、功能型代理校验与 diff 检查通过；刷新脚本成功。
- Evidence：命令退出码和输出。

## 命令

- `python3 -m pytest tests/test_workflow_routing.py tests/test_document_review_contract.py tests/test_supporting_skill_contracts.py -q`
- `python3 -m pytest -q`
- `python3 scripts/validate_plugin.py`
- `python3 scripts/validate_functional_agents.py`
- `git diff --check`
- `python3 scripts/refresh_local_plugin.py /Users/tele/ai-workspace/bruce`

## 限制

文本契约测试证明插件规则已更新，不等同于当前旧会话已经加载新缓存。刷新后仍需新建 Codex 会话验证实际路由；本次不启动额外宿主会话，也不提交或推送。
