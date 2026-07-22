from __future__ import annotations

import unittest

from tests._support import read


class ValidationLoopContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = read("skills/bruce/SKILL.md")
        cls.policy = read("skills/bruce/references/verification-loop.md")
        cls.write_plan = read("skills/write-plan/SKILL.md") + read(
            "skills/write-plan/templates/plan.md"
        )
        cls.write_tests = read("skills/write-tests/SKILL.md") + read(
            "skills/write-tests/templates/test-plan.md"
        )

    def test_behavior_acceptance_has_gwt_and_evidence_contract(self) -> None:
        for field in ("`Given`", "`When`", "`Then`", "`Evidence`"):
            self.assertIn(field, self.policy)
        self.assertIn("stable id", self.policy)
        self.assertIn("actual use", self.policy)
        self.assertIn("Given/When/Then/Evidence", self.write_tests)
        self.assertIn("scenario ids with Given/When/Then", self.write_plan)

    def test_material_then_requires_feasible_evidence_before_implementation(self) -> None:
        self.assertIn("Do not start behavior implementation", self.policy)
        self.assertIn("material `Then` has no feasible evidence path", self.policy)
        self.assertIn("explicitly accepts that boundary", self.policy)
        self.assertIn("Do not begin a behavior implementation", self.workflow)

    def test_tdd_reproduction_and_characterization_have_proportional_boundaries(self) -> None:
        self.assertIn("smallest failing automated test or reproducible scenario", self.policy)
        self.assertIn("reproduce the\nfailure before fixing it", self.policy)
        self.assertIn("characterization baseline", self.policy)
        self.assertIn("genuinely impractical", self.policy)
        self.assertIn("Do not impose TDD on documentation-only", self.policy)

    def test_c0_is_required_and_invalidated_by_later_code_changes(self) -> None:
        self.assertIn("## C0 code self-review", self.policy)
        self.assertIn("Code review: self-review", self.policy)
        self.assertIn("Verdict: pass|issues", self.policy)
        self.assertIn("Any later code change invalidates", self.policy)
        self.assertIn("Required C0 code self-review is `pass`", self.workflow)

    def test_verification_layers_cannot_substitute_for_each_other(self) -> None:
        for layer in ("Unit/component", "Integration/API/database", "Real-use"):
            self.assertIn(layer, self.policy)
        self.assertIn("do not let a lower layer stand in", self.policy)
        self.assertIn("mocked-only evidence", self.policy)

    def test_web_e2e_uses_current_chrome_and_real_service_without_silent_fallback(self) -> None:
        self.assertIn("Codex App Chrome capability", self.policy)
        self.assertIn("current\nChrome session, login state, and extensions", self.policy)
        self.assertIn("real\nlocalhost or target service", self.policy)
        self.assertIn("do not claim that acceptance passed", self.policy)
        self.assertIn("Do not silently substitute Playwright", self.policy)
        self.assertIn("established repository SOP or an explicit user request", self.policy)

    def test_failed_scenario_closes_fix_review_rerun_and_regression_loop(self) -> None:
        for requirement in (
            "Preserve the original failing scenario",
            "Classify the failure with L0-L4",
            "Only for L1",
            "Rerun C0 after code changes",
            "Rerun the original failed scenario unchanged",
            "related regression set",
            "acceptance-to-evidence mapping",
        ):
            self.assertIn(requirement.lower(), self.policy.lower())

    def test_two_unsuccessful_complete_l1_rounds_escalate_to_l2(self) -> None:
        self.assertIn("An L1 repair round counts only", self.policy)
        self.assertIn("After two unsuccessful L1 rounds, move", self.policy)
        self.assertIn("to L2", self.policy)

    def test_failure_classification_prevents_unsafe_replay(self) -> None:
        self.assertIn("L0: retry only an idempotent operation", self.policy)
        self.assertIn("L2: replan the affected dependency boundary", self.policy)
        self.assertIn("L3: pause the affected work", self.policy)
        self.assertIn("L4: freeze writes and retries", self.policy)
        self.assertIn("never replay the original scenario", self.policy)
        self.assertIn("Only L1 enters the repair loop", self.workflow)
        self.assertIn("never replays unknown external side effects", self.workflow)

    def test_completion_reports_scenario_level_current_evidence(self) -> None:
        self.assertIn("For each acceptance id report its scenario", self.policy)
        self.assertIn("verification layer, current evidence, and result", self.policy)
        self.assertIn("keeps that acceptance incomplete", self.policy)


if __name__ == "__main__":
    unittest.main()
