# Task T-004: 完成回归与范围收口

- Contract revision: 1
- Contract state: frozen before execution
- Status source: `../checkpoint.yaml`
- Parent plan: `../plan.md`

## Objective

完成 Bruce 全量静态与契约回归，确认技术无关 Surface Contract 没有破坏现有 prototype、Design Gate、Completion Gate、plugin 和文档语言边界，并收口本次变更范围。

## Included scope

- `README.md`
- `CONTEXT.md`
- 必要的 `tests/**` 回归断言
- 当前变更目录中的计划和验证记录

## Excluded scope

- 不批量改写历史 change artifact。
- 不修改 Joytime 现有 spec 或页面实现。
- 不执行 commit、push、发布、插件安装或外部交付。

## Dependencies

- Depends on: T-003
- Consumes: validator 和两类 Gate 的最终合同、radar regression findings
- Produces: 范围收口记录和全量验证记录

## Acceptance

- Parent scenario ids: UI-SURFACE-07
- Given: Bruce 源码和新增 Surface Contract/Gate 规则
- When: 执行 targeted/full checks
- Then: prototype、Design Gate、Completion Gate、plugin、document-language 和 diff contracts 均通过，且计划内外路径边界清晰
- Evidence: `python3 -m unittest discover -s tests -p 'test_*.py'`、`python3 scripts/validate_plugin.py`、`git diff --check`、范围收口记录

## Verification

- Required layer: repository/full
- Commands/checks: `python3 -m unittest discover -s tests -p 'test_*.py'`; `python3 scripts/validate_plugin.py`; `git diff --check`
- Environment: none for static checks

## Authorization and risks

- Authorization: normal
- Risk trigger: guarded；全量合同回归和变更范围收口
- Stop condition: 任一全量检查失败则返回 issues，并保留失败输出与未验证边界，不执行外部交付

## Contract change rule

Do not silently widen this task. If scope, acceptance, dependency, authorization, or required verification changes, create a new contract revision or a superseding task and record the reason in the next checkpoint.
