# 实施计划：方案落盘后自动衔接 Design Gate

## Task contract

- Objective：消除方案落盘与 Design Gate 之间不必要的用户二次指令。
- Scope：Bruce 核心工作流、五个方案 writer、artifact policy、README/CONTEXT、契约测试和本变更工件。
- Acceptance：AC-01 至 AC-05，证据见 `test-plan.md`。
- Constraints：Design Gate 保持唯一 Design verdict；普通计划不误触发；不扩大实现授权；不修改 Hook 为自动裁决器。
- Profile：standard；单一插件内的多文档契约传播。
- Risk：guarded；共享工作流控制流语义变化，但可通过文本契约测试和插件校验回退。

## 执行顺序

1. 更新契约测试，锁定同轮自动 Gate handoff、无需用户追加指令和非适用边界。
2. 更新 `skills/bruce/SKILL.md` 与 `artifact-policy.md`，定义唯一自动衔接规则和授权边界。
3. 更新五个方案 writer，移除“只提示、等待用户”的旧语义，统一返回 mandatory handoff。
4. 更新 README 与 CONTEXT 的用户可见说明。
5. 执行针对性测试、全量测试、插件/功能型代理校验和 `git diff --check`。
6. 刷新本地 Bruce 插件缓存并核对命令成功；提示必须新建会话。

## 允许修改路径

- `.codex-plugin/plugin.json`
- `skills/bruce/SKILL.md`
- `skills/bruce/references/artifact-policy.md`
- `skills/write-architecture/SKILL.md`
- `skills/write-db-design/SKILL.md`
- `skills/write-plan/SKILL.md`
- `skills/write-prototype/SKILL.md`
- `skills/write-tests/SKILL.md`
- `README.md`
- `CONTEXT.md`
- `tests/test_document_review_contract.py`
- `tests/test_parallel_planning_contract.py`
- `tests/test_prototype_contract.py`
- `tests/test_supporting_skill_contracts.py`
- `tests/test_workflow_policy_contract.py`
- `tests/test_workflow_profiles.py`
- `tests/test_workflow_routing.py`
- `docs/change/20260906-214529-auto-design-gate-handoff/*`

## 排除范围

不修改 Design Gate validator、Completion Gate、Hook、模型路由、配置、依赖、CI、数据库、远程仓库或 Git 历史。
