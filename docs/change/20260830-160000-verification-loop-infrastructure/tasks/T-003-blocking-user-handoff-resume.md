# T-003：接入阻塞通知、用户交接与恢复语义

- Contract revision: 1

## Objective

让用户手测和阻塞处理成为验证循环的正式节点：阻塞时停下通知用户，用户处理并显式恢复后，从原 batch 安全继续。

## Included scope

- User Verification Handoff；
- Blocking Notification；
- Resume Event；
- 用户反馈 pass/fail/blocked/unclear 到 failure classification 的映射；
- 原始失败场景、相关回归和证据 stale 规则。

## Excluded scope

- 自动替用户操作 Desktop、浏览器或外部系统；
- 自动推断用户未提供的测试结果。

## Dependencies

- T-001 的 blocked/resume 事件协议；
- T-002 的外部与用户 Adapter 边界；
- `requirements.md` AC-003、AC-004、AC-005、AC-006。

## Acceptance

- 用户 handoff 绑定 artifact/client/deployment identity；
- 用户未反馈时保持 `waiting_user`；
- 阻塞未恢复前禁止修复和重试；
- 恢复后只重跑受影响验证和相关回归；
- `unclear` 不直接进入代码修复。

## Authorization and risks

- Authorization：仅定义交接和恢复契约，不授权自动控制用户设备或外部系统。
- Risk：缺少版本和证据绑定时可能修复错误版本，或误判用户反馈。

## Contract change rule

阻塞通知、恢复条件、用户反馈字段或失败分类发生变化时，必须增加 contract revision；不得删除原始阻塞和失败证据。

## Verification

使用 handoff/resume/failure fixtures 验证状态冻结、显式恢复、证据失效和预算保留。

## Stop conditions

无法确认用户测试版本、目标或实际观察结果时，暂停并要求最小补充事实，不猜测修复。
