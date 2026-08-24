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

    def test_goal_records_two_owned_results(self) -> None:
        self.assertIn("Design result when applicable", self.goal)
        self.assertIn("Completion result and evidence summary", self.goal)
        self.assertIn("`Completion: pass`", self.goal)
        self.assertIn("`Completion: issues`", self.goal)
        self.assertIn("`Completion: blocked`", self.goal)
        normalized = " ".join(self.goal.split())
        self.assertIn("checkpoint may be referenced as task-progress evidence", normalized)
        self.assertIn("never overrides native Goal state or either Gate result", normalized)
        self.assertIn("Do not independently inspect artifacts", self.goal)

    def test_goal_resume_records_bounded_resume_checkpoint(self) -> None:
        normalized = " ".join(self.goal.split())
        for phrase in (
            "current workspace basis",
            "before new code inspection",
            "known findings/repair set",
            "allowed paths/direct call sites",
            "deferred concerns",
            "next evidence",
            "stop condition",
        ):
            self.assertIn(phrase, normalized)

    def test_goal_records_preflight_checkpoint_and_interval_rollover(self) -> None:
        normalized = " ".join(self.goal.split())
        for phrase in (
            "capability preflight results",
            "latest batch checkpoint",
            "work-interval counters",
            "At each work-interval boundary",
            "not a Completion result",
        ):
            self.assertIn(phrase, normalized)

    def test_goal_entry_is_explicit_and_profile_independent(self) -> None:
        normalized = " ".join(self.goal.split())
        self.assertIn("Enter only for explicit Goal intent", normalized)
        self.assertIn("resolved task contract requires continuous/cross-turn", normalized)
        self.assertIn("Profile, complexity, duration, risk, or subagent use alone does not", normalized)
        self.assertNotIn("Bruce routes a `full` task", self.goal)

    def test_spawn_execute_returns_task_evidence_not_gate_verdicts(self) -> None:
        self.assertIn("initialized by `goal-execution`", self.spawn)
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
        self.assertIn("one change-level `tasks/` package", plan)
        self.assertIn("tasks/index.yaml", plan)
        for phrase in (
            "## Included scope",
            "## Excluded scope",
            "## Acceptance",
            "## Verification",
            "## Contract change rule",
        ):
            self.assertIn(phrase, template)
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
