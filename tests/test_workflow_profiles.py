from __future__ import annotations

import unittest

from tests._support import read


class WorkflowProfileContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = read("skills/bruce/SKILL.md")
        cls.risk = read("skills/bruce/references/risk-policy.md")

    def test_standard_low_is_direct(self) -> None:
        self.assertIn("`standard`", self.workflow)
        self.assertIn("`low`", self.risk)
        self.assertIn("Implement and verify directly", self.risk)
        self.assertIn("does not create a Goal by default", self.workflow)

    def test_full_low_uses_goal_without_business_gate(self) -> None:
        self.assertIn("full + low", self.workflow)
        self.assertIn("By default, every `full` task", self.workflow)
        self.assertIn("goal-execution-gate", self.workflow)
        self.assertNotIn("full requires approval", self.workflow.lower())

    def test_guarded_authority_and_review_are_separate(self) -> None:
        self.assertIn("already authorizes the exact change", self.risk)
        self.assertIn("always run completion review", self.risk)

    def test_critical_requires_impact_recovery_confirmation(self) -> None:
        self.assertIn("state target, impact, and recovery", self.risk)
        self.assertIn("obtain explicit confirmation", self.risk)


if __name__ == "__main__":
    unittest.main()
