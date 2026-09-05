from __future__ import annotations

import unittest

from tests._support import read


class ExecutionContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.goal = read("skills/goal-execution/SKILL.md")
        cls.spawn = read("skills/spawn-execute/SKILL.md")

    def test_goal_execution_is_a_mode_not_a_gate(self) -> None:
        self.assertIn("Goal execution is a mode, not a gate", self.goal)
        self.assertIn("does not re-check", self.goal)
        self.assertIn("Do not independently inspect artifacts", self.goal)
        self.assertIn(".goal/<goal-id>/execute_record.md", self.goal)

    def test_goal_consumes_owned_results_without_mandatory_audit(self) -> None:
        normalized = " ".join(self.goal.split())
        for result in ("`Completion: pass`", "`Completion: issues`", "`Completion: blocked`"):
            self.assertIn(result, normalized)
        self.assertIn("Design result when applicable", normalized)
        self.assertIn("Completion result and evidence summary", normalized)
        self.assertIn("Do not create or maintain `execute_record.md` by default", normalized)
        self.assertIn("Only when the user explicitly requests a durable audit record", normalized)
        self.assertIn("never overrides native Goal state or either Gate result", normalized)
        self.assertIn("Do not independently inspect artifacts", normalized)

    def test_goal_resume_reuses_ordinary_recovery_and_honors_host_state(self) -> None:
        normalized = " ".join(self.goal.split())
        self.assertIn("Use the ordinary Bruce resume procedure", normalized)
        self.assertIn("failure-recovery.md", normalized)
        self.assertIn("Do not silently replace a conflicting unfinished Goal", normalized)
        self.assertIn("Honor host pause, cancellation, permissions, and budget limits", normalized)
        self.assertIn("Pass a token budget only when the user explicitly specified one", normalized)

    def test_goal_reuses_existing_progress_and_evidence(self) -> None:
        normalized = " ".join(self.goal.split())
        for phrase in (
            "existing task contract, checkpoint, and verification evidence",
            "capability preflight",
            "event-driven checkpoints",
            "does not reset L0/L1 retry or repair counts",
            "Do not mirror",
        ):
            self.assertIn(phrase, normalized)

    def test_goal_entry_requires_explicit_native_goal_request(self) -> None:
        normalized = " ".join(self.goal.split())
        self.assertIn("Enter only when the user explicitly requests native Goal", normalized)
        self.assertIn("Profile, complexity, duration, risk, subagent use, cross-turn recovery, and audit needs", normalized)
        self.assertIn("do not enable this adapter", normalized)
        for phrase in ("continue nonstop", "继续开发", "持续推进直到完成"):
            self.assertIn(phrase, normalized)
        self.assertNotIn("resolved task contract requires continuous/cross-turn", normalized)

    def test_ordinary_execution_continues_with_bounded_stops(self) -> None:
        workflow = " ".join(read("skills/bruce/SKILL.md").split())
        for phrase in (
            "Continue ordinary implementation within the authorized scope",
            "acceptance is met",
            "user pause",
            "host limit",
            "authorization or scope change",
            "exhausted repair budget",
            "real blocker",
            "A milestone or progress checkpoint alone is not a reason to return control",
            "does not promise background or automatic cross-turn execution",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, workflow)

    def test_progress_continuation_preserves_budgets_without_goal(self) -> None:
        failure = " ".join(read("skills/bruce/references/failure-recovery.md").split())
        self.assertIn("Ordinary authorized implementation continues", failure)
        self.assertIn("never resets L0/L1 retry or repair counts", failure)
        self.assertNotIn("Ordinary work returns control after the checkpoint", failure)
        self.assertNotIn("Explicit Goal or continuous execution may begin", failure)

    def test_spawn_execute_accepts_ordinary_tasks_without_goal_side_effects(self) -> None:
        spawn = " ".join(self.spawn.split())
        self.assertIn("Neither a native Goal nor `execute_record.md` is a prerequisite", spawn)
        self.assertIn("Return task evidence to Bruce for integration", spawn)
        self.assertIn("Do not create or close native Goals", spawn)
        self.assertNotIn("under an active goal-execution mode", spawn)
        self.assertNotIn("Confirm matching native Goal state and audit record exist", spawn)

    def test_discovery_metadata_does_not_reintroduce_goal_or_audit_requirements(self) -> None:
        goal_ui = read("skills/goal-execution/agents/openai.yaml")
        spawn_ui = read("skills/spawn-execute/agents/openai.yaml")
        self.assertIn("explicitly requested native Goal", goal_ui)
        self.assertNotIn("one audit record", goal_ui)
        self.assertNotIn("under $goal-execution", spawn_ui)
        self.assertNotIn("active Goal", spawn_ui)

    def test_spawn_execute_returns_task_evidence_not_gate_verdicts(self) -> None:
        self.assertIn("Neither a native Goal nor `execute_record.md` is a prerequisite", self.spawn)
        self.assertIn("task evidence packet", self.spawn)
        self.assertIn("Do not\nreturn a Design or Completion verdict", self.spawn)
        for field in (
            "task id",
            "changed files",
            "acceptance/scenario",
            "verification layer",
            "L0-L4 classification",
            "remaining work",
        ):
            self.assertIn(field, self.spawn)

    def test_spawn_has_no_custom_runtime(self) -> None:
        for forbidden in ("progress.md", "progress.json", "checklist", "worker pid"):
            self.assertNotIn(forbidden, self.spawn.lower())
        self.assertIn("second ledger", self.spawn)
        self.assertIn("global\nstop-on-first-failure", self.spawn)

    def test_task_contract_package_is_frozen_and_sequential_by_default(self) -> None:
        contract = read("skills/bruce/references/task-contract.md")
        plan = read("skills/write-plan/SKILL.md")
        template = read("skills/write-plan/templates/task.md")
        index = read("skills/write-plan/templates/tasks-index.yaml")
        policy = read("skills/bruce/references/verification-loop.md")
        for phrase in (
            "frozen before execution",
            "include/exclude",
            "contract_revision",
            "checkpoint.yaml",
            "sequential by default",
        ):
            self.assertIn(phrase, contract)
        self.assertIn("does not split, restart, or shorten the task", policy)
        self.assertIn("one change-level `tasks/` package", " ".join(plan.split()))
        self.assertIn("tasks/index.yaml", plan)
        self.assertIn("Only use task-package templates when that package is needed", " ".join(plan.split()))
        self.assertIn("behavior changes still include minimum test design", " ".join(plan.split()))
        for phrase in (
            "# 任务 <task-id>：<title>",
            "## 包含范围",
            "## 排除范围",
            "## 验收标准",
            "## 验证",
            "## 契约变更规则",
        ):
            self.assertIn(phrase, template)
        self.assertIn("Given", template)
        self.assertIn("When", template)
        self.assertIn("Then", template)
        self.assertIn("Evidence", template)
        self.assertIn("execution: sequential", index)

    def test_checkpoint_tracks_task_state_without_becoming_a_second_evidence_store(self) -> None:
        workflow = read("skills/bruce/SKILL.md")
        policy = read("skills/bruce/references/verification-loop.md")
        checkpoint = read("skills/bruce/templates/checkpoint.yaml")
        for body in (policy, checkpoint):
            self.assertIn("Checkpoint: clear|issues|blocked", body)
            self.assertIn("active_task", body)
            self.assertIn("contract_revision", body)
            self.assertIn("evidence_refs", body)
        self.assertIn("pending|in_progress|implemented|verifying|verified|blocked|superseded", policy)
        self.assertIn("environment: {}", checkpoint)
        self.assertIn("matrix: []", checkpoint)
        self.assertIn("not a third decision", policy)
        self.assertIn("second evidence store", policy)
        self.assertIn("long-running task may span multiple checkpoints", workflow)


if __name__ == "__main__":
    unittest.main()
