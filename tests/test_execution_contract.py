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


if __name__ == "__main__":
    unittest.main()
