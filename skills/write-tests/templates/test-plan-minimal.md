# 测试计划：<变更名称>

## 验收与前提

- 验收 ID：<AC-id 与可观察结果>
- 前置条件：<真实依赖、fixture、权限；无则说明>
- consistency_check: not_applicable；原因：<不涉及跨对象状态/权限/关系的依据；适用则改用扩展模板>
- visual_scope: <none|browser-smoke|browser-layout>；理由：<无可见变化或适用的真实证据层级>

## 场景：<scenario-id>

- Given: <具体初始状态>
- When: <用户或系统动作>
- Then: <可观察断言>
- 验证命令：<仓库真实存在的测试或复现命令>
- Evidence: <该命令/操作如何证明 Then；区分预期证据和实际执行结果>

## 限制与回归

- <已知回归来源、未验证边界；不适用时一句说明，不生成空矩阵>
