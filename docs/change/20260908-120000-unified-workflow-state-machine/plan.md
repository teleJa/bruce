# 实施计划：统一 Bruce 工作流状态机

## T-001：冻结状态机契约

- 新增 `skills/bruce/references/workflow-state.md`、状态模板和事件/转移表。
- 明确任务级状态与 Verification Run、Gate、Failure Policy 的边界。

## T-002：增加校验与转移实现

- 新增 `scripts/workflow_state.py`，提供快照校验、事件校验和纯函数转移。
- 新增 `scripts/validate_workflow_state.py`，支持对 YAML 快照执行静态校验。

## T-003：接入现有 checkpoint/run 文档

- checkpoint 增加统一状态快照。
- Verification Run 增加统一状态引用和映射说明。
- Bruce 主 Skill 与 verification-loop reference 指向统一状态机。

## T-004：契约回归

- 新增状态机单元/契约测试。
- 保留原有 Gate、repair、provider、verification contract 测试。
- 执行全量 pytest、插件校验、状态模板校验和 `git diff --check`。

## 停止条件

- 不实现项目环境、外部 Adapter、部署、数据库或浏览器 runtime。
- 若发现现有状态语义无法无损映射，停止并报告冲突，不静默删除旧状态。
