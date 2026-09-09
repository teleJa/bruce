---
name: solution-analysis
description: Analyze a concrete solution decision from repository evidence and continue the discussion incrementally. Use inspect-parallel for bounded fact-finding when delegation helps; keep tradeoffs and recommendations with the main Agent. Read-only, without automatically persisting design or starting implementation.
---

# Solution Analysis

围绕用户当前要决定的问题开展只读分析。主 Agent 负责确定证据缺口、综合事实和判断取舍；
调查子代理负责带回有界、可核对的证据。不把分析讨论自动转成正式设计或执行计划。

## 1. 明确当前决策与证据缺口

从用户问题和已有上下文中明确：要决定什么、已经确认什么、哪些未知事实会改变结论。
复用仍然有效的仓库证据和已确认决策，不从零重做现状调查。遵守当前仓库的 `AGENTS.md`、
用户范围及只读约束；不要为填写报告而调查无关目录或领域。

仅在范围、验收或业务后果存在无法从证据解决的关键歧义时，提出一个关键问题。
普通实现细节不触发访谈；可以带着明确标注的假设继续分析，但不能把假设当成已确认事实。

## 2. 组织有界调查

由主 Agent 决定需要哪些事实，通过 [inspect-parallel](../inspect-parallel/SKILL.md) 判断 direct 或 parallel。
当读取多个实现范围、追踪调用链或收集项目约定适合独立分工时，优先考虑委派，以控制主 Agent
的上下文占用和调查成本；不要先把整个范围读完再交给子代理重复调查。

- 多个证据缺口可独立调查时，交给 `inspect-parallel` 拆分有界任务并汇总结果。调查范围和问题
  必须服务于当前决策，子代理不代替主 Agent 作最终业务判断。
- 已有充分证据无需新增调查；只需读取一处已知定义或缺口紧密耦合时，按该 Skill 的 direct
  路径直接核对，不为了并行而制造多个任务。`inspect-parallel` 不可用时，报告限制并有界 direct 补查。
- 委派使用共享 `inspector` Profile。Task Packet、模型配置、reasoning effort、解析记录及
  fallback/blocked 均由 `inspect-parallel` 和
  [Functional Agent 合同](../bruce/references/functional-agent-contracts.md) 负责；本 Skill 不复制模型名单、
  选择器或 Packet schema，也不另设路由。direct 调查不为满足流程运行模型解析。
- 需要独立挑战关键假设时，才按共享合同使用 `reviewer` Profile；不把独立审查变成每次分析的必经步骤。
  主 Agent 直接补查不能替代必需的 clean-context 审查，不能绕过授权或缺失的必需能力。

给调查方的核心问题是“需要什么事实来区分这些选择”，而不是全领域检查清单。当前实现、生命周期、
权限、数据、接口、测试或发布等领域，只检查会影响当前判断的部分。每个缺口应有有限的证据范围：
证据足以支持判断即可结束；有界调查仍无法确认时，返回具体缺口，不无限扩展到相邻问题。

## 3. 综合证据与形成判断

消费子代理返回的事实、来源和未知项，而不是复制完整调查记录。主 Agent 重点复核决定方案的关键
事实、相互矛盾的结论和证据不足的部分；对来源清楚、范围匹配且未失效的普通证据直接复用，
不把子代理读过的文件全部重读。工具不可用或某个调查失败时，保留已有结果，只处理受影响的缺口。

区分事实、推断、建议和未知，不编造 API、路径、表、命令执行或测试结果。没有证据支撑时可以给出
有条件的建议，但须说明缺口如何影响结论，以及下一步最小取证动作。

只比较有实际竞争力的方案，说明推荐理由、关键取舍、适用前提及会使结论改变的条件；
现有约束已经排除其他路径时，说明排除依据，不为填对比表制造候选。技术、架构、数据迁移、权限、
测试或回滚按当前问题的适用性讨论，不要求逐项评级或生成空章节。

## Output — 增量讨论与输出

默认直接回答当前问题，按需要附关键证据、取舍和未决事项；不强制章节、候选数量、对比表或状态字段。
使用用户的语言，保留稳定代码标识符。委派或证据缺口影响可信度时，简要说明实际调查范围、
复核情况及限制，不在普通回答中展开完整模型路由记录；共享协议要求的记录仍随委派保留。

用户追问或加入新条件时，先识别哪些结论和证据受影响，只补查新增或失效的范围，说明改变了什么、
哪些结论仍然成立；不重复完整调查和报告，也不重新确认未改变的决策。是否需要新增调查仍按第 2 节判断。

完成当前问题的回答后，等待用户继续讨论或明确选择下一阶段；不因一次回答结束就宣称整个方案已定稿。
若使用 `Analysis: complete`，它仅表示当前问题已回答，不是批准设计或进入实现的授权。

## Does not own — 只读与阶段边界

不得修改源代码、测试、配置或文档；不执行会写入文件、变更数据或服务状态的测试、构建、索引或命令。
不得创建 `docs/change`、Goal、checkpoint 或 review 状态，不得 commit、push、部署或执行其他外部副作用。

不得自动调用后续 Skill：`write-architecture`、`write-db-design`、`write-plan`、`write-tests`、
`design-gate`、`completion-gate` 或 `test-dispatch`。分析可以指出需要什么实验或验证证据，但本 Skill
不执行它们；需要执行时，报告最小验证范围并等待对应授权，再由调用方进入相应执行能力。
调查委派不扩大上述只读边界。

用户明确要求落盘设计、制定执行计划或实现时，才由 Bruce/调用方在对应授权范围内进入下一阶段；
方案讨论、推荐结论或普通“继续”不自动授予写入权限。

Do not modify files or execute delivery actions. Do not treat `Analysis: complete` as `Design: pass`
or as permission to start implementation. The main Agent retains the final analysis responsibility.
