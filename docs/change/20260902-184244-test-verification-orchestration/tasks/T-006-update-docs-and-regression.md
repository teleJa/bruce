# 任务 T-006：更新插件文档、metadata 与全量回归

- 契约修订：1
- 契约状态：执行前冻结
- 状态来源：`../checkpoint.yaml`
- 父计划：`../plan.md`

## 目标

注册三个新 Skill 的插件元数据和文档入口，执行全量仓库验证并如实区分静态契约、宿主能力、项目 API/UI 运行和外部交付边界。

## 包含范围

- `README.md`、`CONTEXT.md`、`.codex-plugin/plugin.json` 的能力说明。
- supporting Skill/agents/package contract tests 的注册与回归。
- 全量 unittest、Functional Agent validator、plugin validator 和 diff 检查。

## 排除范围

- 不刷新本地插件缓存，不修改 hook、marketplace、用户配置或 Joytime 仓库。
- 不 commit、push、部署、运行生产测试或声明真实项目 API/UI 已通过。
- 不顺带整理当前无关 Environment Profile 脏文件。

## 依赖关系

- 依赖任务：T-005
- 使用：已实现并验证的三个 Skill 与集成契约
- 产出：可发现的插件能力、文档边界和完整仓库验证证据

## 业务不变量与权威状态（按适用性）

- 一致性检查：not_applicable
- 业务不变量与权威状态摘要：本任务只更新插件文档/metadata 和验证入口，不创建业务资源关系或权限投影。
- 竞争者/权限视角与冲突后果：不适用；只需保持已有脏文件和未跟踪文件不被覆盖。
- 关联测试计划矩阵/场景 ID：REGRESSION-001
- 不适用原因：不涉及业务对象绑定、归属、共享、状态转移或持久化写入。

## 验收标准

- 父级场景 ID：TVO-08
- Given：三个新 Skill 及集成改动已完成
- When：运行 metadata、package、contract 和全量仓库验证
- Then：所有仓库内检查通过；Joytime、插件刷新、真实浏览器/API/数据库和远程交付明确标记未执行或另行验证
- Evidence：unittest、`validate_functional_agents.py`、`validate_plugin.py`、`git diff --check` 和最终 status/diff

## 验证

- 必需层级：repository/full
- 命令/检查：`python3 -m unittest discover -s tests -p 'test_*.py'`; `python3 scripts/validate_functional_agents.py`; `python3 scripts/validate_plugin.py`; `git diff --check`
- 环境：本地 Bruce 仓库；不需要外部服务

## 授权与风险

- 授权：normal
- 风险触发：guarded；插件发现和跨 Skill 文档必须与实现一致
- 停止条件：任一全量检查失败、diff 包含 Joytime/未授权文件、或需要刷新/commit/push 时停止并报告

## 契约变更规则

不得静默扩大本任务范围。如果范围、验收、依赖、授权或所需验证层级发生变化，必须创建新的契约修订或替代任务，并在下一个检查点中记录原因。
