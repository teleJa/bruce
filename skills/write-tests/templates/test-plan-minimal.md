# 测试计划：<变更名称>

## 验收与前提

- 验收 ID：<AC-id 与可观察结果>
- 前置条件：<真实依赖、fixture、权限；无则说明>
- consistency_check: not_applicable；原因：<不涉及跨对象状态/权限/关系的依据；适用则改用扩展模板>
- visual_scope: <none|browser-smoke|browser-layout>；理由：<无可见变化或适用的真实证据层级>
- 视觉适用性：<非 Web/none 写 not_applicable；smoke/layout 仅引用 visual-checks.md，展开到场景时补 Provider 证据要求>。
- Provider 来源（仅适用视觉验收）：<`.bruce/config.yaml`、`verification.browser_provider`、解析后的 Provider；未配置默认 `ego-lite`，仅显式配置 `chrome`；配置非法/不可读或 Provider 不可用时 `blocked/incomplete`，执行前复核配置，不继承历史 Chrome-only>。

## 场景：<scenario-id>

- Given: <具体初始状态>
- When: <用户或系统动作>
- Then: <可观察断言>
- 验证命令：<仓库真实存在的测试或复现命令>
- Evidence: <预期证据如何证明 Then；只写预期证据，不填实际通过结果>
- 实际证据：<由后续验证轨道填写；生成计划时留空>
- 视觉检查（仅 `browser-smoke|browser-layout`）：<按 [视觉检查清单](../references/visual-checks.md) 展开具体 Then 与预期证据，生成时不复制模板内部链接；smoke 检查显示完整性、明显遮挡和布局异常；layout 明确显示完整性、溢出与滚动、遮挡与层级、布局稳定性、视口与状态变化的适用性/理由，并补齐 viewport、geometry、overflow、before/after>
- 视觉判读（仅 Web）：<实际查看截图，记录受影响区域/状态、所见和结论；DOM 结构/文本或“截图已保存”不等于通过，未判读为 incomplete；此处只写预期检查，不预填通过>

## 限制与回归

- <已知回归来源、未验证边界；不适用时一句说明，不生成空矩阵>
