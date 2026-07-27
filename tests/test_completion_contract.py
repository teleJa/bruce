from __future__ import annotations

import unittest

from tests._support import read


class CompletionContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = read("skills/verify-completion/SKILL.md")

    def test_completion_gate_returns_one_verdict(self) -> None:
        self.assertIn("Bruce's only completion decision", self.skill)
        for verdict in ("Completion: pass", "Completion: issues", "Completion: blocked"):
            self.assertIn(verdict, self.skill)
        self.assertIn("Return exactly one terminal field", self.skill)

    def test_final_author_quality_is_internal(self) -> None:
        for check in (
            "final diff",
            "affected call sites",
            "error paths",
            "security",
            "concurrency",
            "data integrity",
            "regression coverage",
            "cross-document consistency",
        ):
            self.assertIn(check, self.skill)
        self.assertIn("Any later change invalidates", self.skill)

    def test_acceptance_evidence_is_scenario_and_layer_specific(self) -> None:
        self.assertIn("Map every acceptance condition", self.skill)
        self.assertIn("current, reproducible evidence", self.skill)
        self.assertIn("A unit test\ndoes not prove", self.skill)
        self.assertIn("scenario-level\nacceptance evidence", self.skill)

    def test_web_acceptance_requires_current_chrome(self) -> None:
        self.assertIn("current Codex App Chrome evidence", self.skill)
        self.assertIn("keep the scenario incomplete", self.skill)
        self.assertIn("do not silently substitute Playwright", self.skill)

    def test_design_alignment_returns_issue_without_reimplementing_design_gate(self) -> None:
        self.assertIn("compare the final diff and scope with `design-review.md`", self.skill)
        self.assertIn("Do not rerun Design Gate inside completion", self.skill)
        self.assertIn("return the mismatch to Bruce for one explicit rerun", self.skill)

    def test_independence_is_an_internal_review_mode(self) -> None:
        normalized = " ".join(self.skill.split())
        self.assertIn("Use `main-agent` mode", normalized)
        self.assertIn("Use an `independent` clean-context", normalized)
        self.assertIn("Exclude author rationale, confidence, and proposed verdict", normalized)
        self.assertIn("not a second externally combined verdict", normalized)
        self.assertIn("Completion: blocked", normalized)

    def test_repair_and_delivery_boundaries_are_checked(self) -> None:
        self.assertIn("unchanged original failed scenario", self.skill)
        self.assertIn("related regressions", self.skill)
        self.assertIn("L2-L4", self.skill)
        self.assertIn("delivery actions", self.skill)

    def test_legacy_multi_verdict_fields_are_absent(self) -> None:
        for marker in (
            "Verification: V0",
            "Author checks: C0/D0",
            "Independent review: R1",
            "not-run",
        ):
            self.assertNotIn(marker, self.skill)


if __name__ == "__main__":
    unittest.main()
