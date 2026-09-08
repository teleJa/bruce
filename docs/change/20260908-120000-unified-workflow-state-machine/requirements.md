# 需求：统一 Bruce 工作流状态机

## 目标

为 Bruce 建立一个版本化、可校验、可恢复的任务级统一状态机，收敛当前分散在 Task、Checkpoint、Verification Run、Repair Loop、Design Gate 和 Completion Gate 中的生命周期状态。

统一状态机只治理任务生命周期；验证运行状态、Gate verdict、Failure Level 和交付状态仍保留各自职责，并通过映射关系关联到任务状态。

## 范围

- 定义任务级状态、事件、合法转移和终态。
- 定义统一状态与现有 checkpoint、verification run、Design Gate、Completion Gate、repair loop 的映射。
- 提供 machine-readable 模板、Python 校验器和转移函数。
- 为非法状态、非法转移、终态重启和 Gate/状态不一致增加契约测试。
- 保留 `Design Gate` 和 `Completion Gate` 的唯一裁决权。

## 非范围

- 不创建第二个调度器、Goal ledger、证据库或运行时。
- 不删除 Verification Run 的执行细节状态。
- 不增加数据库、项目 Adapter、CNB、部署或浏览器 runtime。
- 不改变现有 Design/Completion verdict 的命名和所有权。

## 验收标准

### AC-001：统一状态定义

统一状态机定义任务生命周期状态、版本、任务标识、contract/basis revision、运行模式、最后事件以及暂停/阻塞恢复条件，并提供模板。

### AC-002：合法转移

校验器拒绝未知状态、未知事件、非法转移、从完成态继续执行和不一致的 Gate/完成状态；合法事件可以生成新的状态版本。

### AC-003：既有状态映射

Checkpoint 和 Verification Run 明确引用统一任务状态；Verification Run 的 `running/waiting/repairing/re_verifying` 作为执行子状态，不产生第二个任务终态。

### AC-004：Gate 所有权不变

Design Gate 仍只返回 `Design: pass|blocked`；Completion Gate 仍只返回 `Completion: pass|issues|blocked`。状态机不得自行产生这两个 verdict。

### AC-005：回归验证

现有契约测试继续通过，并新增状态机转移、schema、checkpoint/run 映射和终态保护测试。
