# Test plan: Bruce 功能型 Agent 与 Model Profile 路由

## Scope

验证 Profile registry、Packet schema、覆盖优先级、模型 fallback、路径/工具权限和 Skill 路由合同；不把真实模型 smoke、插件安装、Chrome、部署或 commit/push 的未执行状态伪装成自动化通过。

## Scenarios

| ID | Given | When | Then | Evidence |
|---|---|---|---|---|
| FA-01 | 委派任务有明确目标和边界 | 构造 Task Packet 并选择 Profile | 完整字段通过校验，缺字段/未知字段/非法版本 fail closed | `test_task_packet_schema_and_invalid_variants` |
| FA-02 | registry 与 Skills 已迁移 | 扫描 P0 Profile 与 native-subagent 路由 | 四类 Profile 存在且每个调用方恰好映射一个 ID | `test_profile_registry_and_routing_matrix` |
| FA-03 | Reviewer 需要独立审查 | 目标模型可用或不可用 | 可用时传 override；不可用时省略 model、标记 degraded/fallback，不宣称异构 | `test_reviewer_resolution_and_fallback` |
| FA-04 | Verifier/Reviewer 返回结果 | 校验输出 Packet | 只允许 verification/review packet，禁止 Design/Completion terminal field | `test_evidence_packet_authority_boundary` |
| FA-05 | Agent 试图越权写入 | 校验变更路径和 Inspector 工具 | 越权 fail closed，Inspector write_scope=none | `test_permissions_and_allowed_paths` |
| FA-06 | 宿主能力不足或配置非法 | 解析 profile | 按 resolved/fallback/degraded/blocked 记录原因和 effective_model | `test_resolution_failure_matrix` |
| FA-07 | 全部改造完成 | 运行回归与插件校验 | 回归、插件、Profile validator 和 diff check 有独立结果；真实 smoke 另行标注 | 全量命令输出 |

## Commands

- `python3 -m unittest discover -s tests -p 'test_*.py'`
- `python3 scripts/validate_plugin.py`
- `python3 scripts/validate_functional_agents.py`
- `git diff --check`
