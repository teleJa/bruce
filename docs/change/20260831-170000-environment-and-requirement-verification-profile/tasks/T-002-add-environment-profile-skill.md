# T-002：新增 environment-profile skill

- Contract revision: 1

## Objective

提供项目环境事实扫描、用户信息补充、Profile 生成和未确认状态输出能力。

## Included scope

- `skills/environment-profile/SKILL.md`；
- `agents/openai.yaml`、schema reference、Profile template 和静态 `validate_profile.py`；
- 仓库事实与用户事实的来源标记；
- 账号池、Credential 引用、构建/部署、服务/数据库/客户端、Skill 和 preflight 字段；
- needs-input、ready-for-confirmation 和 confirmation boundary。

## Excluded scope

- 执行构建、部署、数据库写入、客户端测试、浏览器登录和项目 Adapter。

## Dependencies

- T-001 Profile lifecycle/security contract；
- Bruce artifact placement 和 document language 规则；
- `requirements.md` AC-001、AC-002、AC-006、AC-008。

## Acceptance

- skill 能生成可复用 Environment Profile；
- 无法确认的环境事实形成最小用户问题；
- Profile 默认未确认；
- API Key 等只记录安全引用，不记录值；
- Profile 提供 Skill/capability evidence boundary，但不声称运行时可用；静态 validator 拒绝 secret/dynamic runtime fields。

## Verification

执行 Skill metadata、resource、template、secret boundary 和 lifecycle contract tests。

## Authorization and risks

- Authorization：只生成环境描述，不授权访问真实 Credential 或外部环境。
- Risk：用户脑中的环境知识可能过时，必须保留来源并要求运行前 preflight。

## Contract change rule

环境 Profile 字段、来源、账号/ Credential policy 或确认语义变化时，必须增加 contract revision。

## Stop conditions

若生成过程需要用户粘贴秘密值，或无法区分用户声明与运行时证据，停止并返回 issues。
