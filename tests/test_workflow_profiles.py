from __future__ import annotations

import unittest

from tests._support import read


class WorkflowProfileContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = read("skills/bruce/SKILL.md")
        cls.risk = read("skills/bruce/references/risk-policy.md")
        cls.test_design = read("skills/write-tests/SKILL.md")
        cls.design_gate = read("skills/design-gate/SKILL.md")

    def test_unresolved_profile_is_read_only_and_side_effect_free(self) -> None:
        normalized = " ".join(self.workflow.split())
        self.assertIn("`unresolved`", normalized)
        self.assertIn("bounded read-only inspection", normalized)
        self.assertIn("does not create a Goal, design review, test design, or change directory", normalized)
        self.assertIn("Do not begin behavior implementation while the profile is `unresolved`", normalized)

    def test_bruce_exposes_analysis_and_design_only_boundaries(self) -> None:
        normalized = " ".join(self.workflow.split())
        for phrase in (
            "user-directed design and implementation capability",
            "`solution-analysis` is the normal pre-design entry",
            "does not invoke it automatically",
            "`design-only` scope",
            "it must not implement behavior",
            "it is not permission to implement",
        ):
            self.assertIn(phrase, normalized)

    def test_unresolved_inspection_can_use_bounded_parallel_exploration(self) -> None:
        normalized = " ".join(self.workflow.split())
        for phrase in (
            "Use `inspect-parallel` when unresolved facts can be divided",
            "at least two independent read-only scopes",
            "the task spans multiple components/directories, a cross-cutting concern, or repository-wide patterns",
            "Repository size, expected `full` profile, or a desire to use subagents is not sufficient",
            "The main agent owns synthesis",
            "If native subagents are unavailable or one shard fails",
            "inspect only the missing scope directly",
            "unavailable parallelism alone does not block contract formation",
        ):
            self.assertIn(phrase, normalized)

    def test_full_requires_structural_evidence(self) -> None:
        normalized = " ".join(self.workflow.split())
        self.assertIn("multiple independently delivered components", normalized)
        self.assertIn("cross-component contract propagation", normalized)
        for evidence in ("`named components`", "`propagated contract`", "repository `evidence`"):
            with self.subTest(evidence=evidence):
                self.assertIn(evidence, normalized)
        self.assertIn("Size, duration, risk, and uncertainty are insufficient", normalized)

    def test_cross_component_full_or_critical_requires_closed_batches(self) -> None:
        normalized = " ".join(self.workflow.split())
        for phrase in (
            "required before implementation for a `full` or `critical` task",
            "two or more independently delivered components or a propagated cross-component contract",
            "Each batch is a closed, verifiable delivery boundary",
            "not a remaining-work bucket",
            "owned components and allowed paths",
            "excluded work",
            "repair budget",
            "missing, open-ended, or overlapping batches also leave the task contract unresolved",
        ):
            self.assertIn(phrase, normalized)

    def test_full_batch_contract_requires_executable_stop_boundary(self) -> None:
        normalized = " ".join(self.workflow.split())
        for phrase in (
            "direct call sites",
            "stop condition",
            "stop opening new inspection",
            "current acceptance id",
            "known failing matrix row",
            "declared direct call site",
        ):
            self.assertIn(phrase, normalized)

    def test_test_design_route_is_profile_independent(self) -> None:
        normalized = " ".join(self.test_design.split())
        for trigger in (
            "跨越多个组件、API、服务、数据库或其他合同边界",
            "需要验证 state、repeat use、retry、concurrency、partial failure、recovery、permission、rollback",
            "需要真实 integration、deployment、runtime、database、browser 证据或多个验证层级",
            "共享行为场景或回归来源跨越多个任务",
            "修改有重复进入、可变数据或生命周期语义的 stateful UI",
        ):
            with self.subTest(trigger=trigger):
                self.assertIn(trigger, normalized)
        self.assertIn("profile 本身既不是必要条件，也不是充分条件", normalized)
        self.assertIn("对任何 resolved Bruce profile 都执行判断", normalized)
        self.assertNotIn("For a `full` Bruce task", self.test_design)

    def test_ui_changes_route_to_test_design_by_lifecycle_risk(self) -> None:
        normalized = " ".join(self.test_design.split())
        for trigger in (
            "可以关闭后再次进入",
            "可能在 surface 关闭期间或两次进入之间变化",
            "cache、refresh、reset、re-fetch、prefill 或 selection-retention",
            "stale state、duplicate interaction、reopening 或 recovery",
        ):
            self.assertIn(trigger, normalized)
        self.assertIn("不要为纯 copy、icon、color 或没有状态、数据、交互和验证边界的 layout-only 变更调用本 Skill", self.test_design)
        self.assertIn("first entry、close and reopen", normalized)
        self.assertIn("fresh observable result", normalized)

    def test_resource_and_permission_state_consistency_is_mandatory_when_applicable(self) -> None:
        normalized = " ".join(self.test_design.split())
        for phrase in (
            "跨对象一致性触发条件",
            "一致性与权威状态矩阵",
            "consistency_check",
            "业务不变量",
            "权威状态源",
            "竞争 actor/viewer",
            "stale window",
            "不要把“对象对当前用户不可见”推导为“对象离线”",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.test_design)
        for phrase in (
            "权限过滤",
            "关联对象受到独立的权限过滤",
            "权限投影/可用性推导",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, normalized)

    def test_chinese_request_requires_chinese_test_plan_natural_language(self) -> None:
        for phrase in (
            "中文请求时",
            "全部使用简体中文",
            "Given",
            "When",
            "Then",
            "Evidence",
            "稳定 machine-facing tokens",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.test_design)

    def test_design_gate_depends_on_downstream_design(self) -> None:
        normalized = " ".join(self.workflow.split())
        self.assertIn("will govern downstream implementation", normalized)
        self.assertIn("A resolved profile does not itself invoke Goal, Design Gate", normalized)
        self.assertIn("Design: pass|blocked", self.design_gate)
        self.assertNotIn("When a `full` task", self.design_gate)

    def test_later_facts_recheck_only_affected_predicates(self) -> None:
        normalized = " ".join(self.workflow.split())
        self.assertIn("re-evaluate only the affected capability predicates", normalized)
        self.assertIn("before continuing affected behavior implementation", normalized)
        self.assertIn("Do not ask for approval unless", normalized)

    def test_risk_changes_review_mode_not_verdict_count(self) -> None:
        self.assertIn("Risk changes its review mode, not the number of", self.risk)
        self.assertIn("main-agent review mode", self.risk)
        self.assertIn("independent mode", self.risk)
        self.assertIn("Completion: blocked", self.risk)

    def test_critical_requires_impact_recovery_confirmation(self) -> None:
        self.assertIn("state target, impact, and recovery", self.risk)
        self.assertIn("obtain explicit confirmation", self.risk)


if __name__ == "__main__":
    unittest.main()
