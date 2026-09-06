from __future__ import annotations

import unittest

from tests._support import read


class ParallelPlanningContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = read("skills/write-plan/SKILL.md")

    def test_write_plan_consumes_bruce_inspection_evidence(self) -> None:
        normalized = " ".join(self.plan.split())
        for phrase in (
            "task contract and repository evidence already provided by Bruce",
            "For a `full` profile, require named components",
            "Consume synthesized `inspect-parallel` findings when Bruce already produced them",
            "Do not plan against invented paths or APIs",
        ):
            self.assertIn(phrase, normalized)

    def test_write_plan_does_not_own_parallel_exploration(self) -> None:
        normalized = " ".join(self.plan.split())
        for phrase in (
            "Do not launch subagents, invoke `inspect-parallel`, or own parallel repository inspection",
            "Do not choose Bruce risk/profile, launch subagents, or own repository exploration",
            "other supporting skills remain predicate-driven",
        ):
            self.assertIn(phrase, normalized)
        for forbidden in (
            "use bounded native read-only subagents directly",
            "inspect the affected scopes directly",
        ):
            self.assertNotIn(forbidden, normalized)

    def test_missing_evidence_returns_to_bruce_without_persisting_plan(self) -> None:
        normalized = " ".join(self.plan.split())
        for phrase in (
            "If material facts about files, interfaces and consumers, verification commands, dependencies, ownership, or dirty-worktree boundaries remain missing",
            "do not persist a plan",
            "Return `Missing planning evidence`",
            "unresolved questions and smallest bounded scopes Bruce must inspect",
            "before invoking `write-plan` again",
            "Return exactly one outcome",
            "`Missing planning evidence`: do not create or update `plan.md`",
            "smallest bounded inspection scopes to Bruce",
        ):
            self.assertIn(phrase, normalized)

    def test_ready_output_is_distinct_from_missing_evidence(self) -> None:
        normalized = " ".join(self.plan.split())
        self.assertIn("`Plan: ready`: persist one minimal executable plan", normalized)
        self.assertIn("`Document check: clear|issues`", normalized)
        missing_outcome = self.plan.split("- `Missing planning evidence`:", 1)[1].split(
            "## Does not own", 1
        )[0]
        normalized_missing = " ".join(missing_outcome.split())
        self.assertIn("do not create or update `plan.md`", normalized_missing)
        self.assertNotIn("persist one minimal executable plan", normalized_missing)
        self.assertNotIn("`Plan: ready`", normalized_missing)


if __name__ == "__main__":
    unittest.main()
