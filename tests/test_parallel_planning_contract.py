from __future__ import annotations

import unittest

from tests._support import read


class ParallelPlanningContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = read("skills/write-plan/SKILL.md")

    def test_full_profile_has_evidence_bounded_parallel_path(self) -> None:
        normalized = " ".join(self.plan.split())
        for phrase in (
            "task contract's component boundary and repository evidence",
            "for a `full` profile, also read its named components",
            "Consume synthesized `inspect-parallel` findings when Bruce already produced them",
            "If material planning facts remain missing and at least two scopes can be inspected independently",
            "bounded native read-only subagents",
            "one primary scope per component or concern",
            "public interfaces and consumers",
            "synthesize cross-scope joins before writing tasks",
            "Profile and risk alone are neither necessary nor sufficient for parallel planning inspection",
            "do not invoke another supporting skill automatically",
        ):
            self.assertIn(phrase, normalized)

    def test_parallel_planning_has_direct_fallback(self) -> None:
        normalized = " ".join(self.plan.split())
        self.assertIn("scopes share mutable ownership", normalized)
        self.assertIn("evidence is already sufficient", normalized)
        self.assertIn("parallel capability is unavailable", normalized)
        self.assertIn("inspect the affected scopes directly", normalized)

    def test_planning_does_not_own_subagent_runtime_details(self) -> None:
        normalized = " ".join(self.plan.split())
        self.assertIn("Do not select a model, process, isolation mechanism, or scheduler", normalized)


if __name__ == "__main__":
    unittest.main()
