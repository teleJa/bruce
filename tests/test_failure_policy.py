from __future__ import annotations

import unittest

from tests._support import read


class FailurePolicyContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = read("skills/bruce/references/failure-recovery.md")

    def test_all_levels_have_distinct_responses(self) -> None:
        for level, response in (
            ("L0", "Retry"),
            ("L1", "Make an actual"),
            ("L2", "Replan"),
            ("L3", "Ask one precise question"),
            ("L4", "Freeze writes"),
        ):
            self.assertIn(level, self.policy)
            self.assertIn(response, self.policy)

    def test_retry_and_repair_budgets_are_bounded(self) -> None:
        self.assertIn("`retry_count < 2`", self.policy)
        self.assertIn("two complete repair-and-reverify rounds", self.policy)
        self.assertIn("Move exhausted L0/L1 work to L2", self.policy)

    def test_repair_round_requires_original_scenario_and_regression(self) -> None:
        self.assertIn("required C0", self.policy)
        self.assertIn("unchanged original\n  failed scenario", self.policy)
        self.assertIn("related regressions", self.policy)
        self.assertIn("Do not weaken acceptance", self.policy)

    def test_unknown_side_effect_is_never_replayed(self) -> None:
        self.assertIn("unknown external side-effect state", self.policy)
        self.assertIn("L4", self.policy)
        self.assertIn("never elevate privileges or replay", self.policy)
        loop = read("skills/bruce/references/verification-loop.md")
        self.assertIn("L4: freeze writes and retries", loop)
        self.assertIn("never replay the original scenario", loop)

    def test_failure_propagation_is_local_except_incident_boundary(self) -> None:
        self.assertIn("Proven-independent work continues", self.policy)
        self.assertIn("incident boundary", self.policy)
        self.assertIn("Only read-only diagnosis and proven-isolated work may continue", self.policy)


if __name__ == "__main__":
    unittest.main()
