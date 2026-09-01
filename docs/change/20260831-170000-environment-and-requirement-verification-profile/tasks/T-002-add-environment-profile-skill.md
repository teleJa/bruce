# T-002：新增 environment-profile skill

- Contract revision: 4

## Objective

提供用户环境信息收集、Profile 生成和未确认状态输出能力；不执行仓库扫描来填充 Environment Profile。

## Included scope

- `skills/environment-profile/SKILL.md`；
- `agents/openai.yaml`、schema reference、Profile template、静态 `validate_profile.py`、本地 `.env` metadata checker 和显式授权的 `.env` creator；
- 用户声明与确认边界；禁止 repository/project-document 事实和 `source_of_truth` 进入 Environment Profile；
- 开发/测试环境拓扑：部署、构建、生命周期、依赖/中间件、网络、身份、数据、配置和 preflight；
- 账号池、Credential 引用、构建/部署、服务/数据库/客户端、Skill 和 preflight 字段；
- needs-input、ready-for-confirmation、`.env` 缺失引导、用户授权写入和 confirmation boundary。

## Excluded scope

- 执行构建、部署、数据库写入、客户端测试、浏览器登录和项目 Adapter；
- 实现通用 Secret Manager、远端凭证服务或浏览器 Cookie/SSO 会话迁移。

## Dependencies

- T-001 Profile lifecycle/security contract；
- Bruce artifact placement 和 document language 规则；
- `requirements.md` AC-001、AC-002、AC-006、AC-008。

## Acceptance

- skill 能生成只包含用户提供并确认信息的可复用 Environment Profile；
- 无法确认的用户环境信息形成最小用户问题；
- 不从仓库扫描或推导代码路径、Git revision、测试场景或实现细节；
- 可选生成 Environment Operation Manifest，但只能在 Profile 确认后封装已确认操作；
- Profile 默认未确认；
- API Key 等在 Profile 中只记录安全引用，不记录值；本地环境经用户明确提供并授权后，可写入项目根目录且被 Git 忽略的 `.env`；
- Profile 提供 Skill/capability evidence boundary，但不声称运行时可用；静态 validator 拒绝 secret/dynamic runtime fields。

## Verification

执行 Skill metadata、resource、template、secret boundary 和 lifecycle contract tests。

## Authorization and risks

- Authorization：默认只生成环境描述；本地 `.env` 初始化是独立的、用户明确授权的窄写入动作，不授权外部环境或通用 Credential 访问。
- Risk：用户脑中的环境知识可能过时，必须保留来源并要求运行前 preflight；`.env` 只证明本地变量存在，不证明账号或服务可用。

## Contract change rule

环境 Profile 字段、来源、账号/ Credential policy 或确认语义变化时，必须增加 contract revision。

## Stop conditions

若用户确认的 `.env` 变量缺失或不安全且用户未明确授权本地初始化，进入 `needs_input`；禁止从仓库推导变量清单，禁止回显秘密值，禁止把秘密写入 Profile、日志、Checkpoint、Handoff 或输出。
