# 子代理委派语言：测试计划

## 范围

自然语言指令跟随用户当前请求语言，中文默认简体中文；用户明确指定语言优先。
覆盖初次 spawn_agent、send_input、恢复工作者及 clean-context reviewer，不改变 Packet schema、
模型配置、代码注释规则和历史工件。`visual_scope: none`；`consistency_check: not_applicable`
（无界面、跨系统对象状态或持久化数据变化）。

| ID | Given / When / Then | Evidence |
|---|---|---|
| LANG-1 | 中文请求、英文模板；派发任意 Profile；新写的目标、约束、验收、停止条件和结果说明使用简体中文，并明确传入工作者 | 共享规则静态断言、当前 reviewer 实际派发与结果 |
| LANG-2 | 已选择中文；补充、恢复或重试；语言不因工具/模型/模板变化切回英文，用户明确改语言时遵循用户 | follow-up/恢复静态断言；本次未执行的运行场景须保留边界 |
| LANG-3 | 中文任务包含协议键、枚举、命令、路径和原始报错；构造消息；这些保持原样，代码注释英文要求不扩张为任务正文英文 | 静态断言、中文 Packet 兼容性与错误翻译的负例 |
| LANG-4 | 用户明确请求英文；构造任务；英文自然语言可用，不硬性中文化，不增加 language 字段 | 显式语言优先条款与英文 Packet 格式兼容性测试 |

## 验证命令

- `python3 -m unittest tests.test_delegation_language_contract tests.test_document_language_contract tests.test_functional_agent_profiles`
- `python3 scripts/validate_plugin.py`
- `python3 scripts/validate_functional_agents.py`
- `python3 -m unittest discover -s tests`
- `git diff --check`

静态断言只保护规则和入口引用，Packet 示例只验证格式，不构成语言检测器或所有模型遵循规则的
保证。本次实际 reviewer 消息与返回可验证当前路径，不能替代新会话中所有角色、恢复和多语言
场景的运行验证。插件刷新后需新会话加载；不回写历史英文消息。
