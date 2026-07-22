from __future__ import annotations

import unittest

from tests._support import read


class CompletionContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = read("skills/verify-completion/SKILL.md")

    def test_verdicts_and_evidence_are_explicit(self) -> None:
        for verdict in ("`pass`", "`issues`", "`blocked`"):
            self.assertIn(verdict, self.skill)
        self.assertIn("acceptance-to-evidence mapping", self.skill)
        self.assertIn("actual change set", self.skill)

    def test_current_evidence_is_required(self) -> None:
        self.assertIn("current, reproducible evidence", self.skill)
        self.assertIn("natural-language evidence as a gap", self.skill)
        self.assertIn("unresolved L2/L3/L4", self.skill)

    def test_behavior_completion_is_scenario_and_layer_specific(self) -> None:
        self.assertIn("concrete Given/When/Then scenarios", self.skill)
        self.assertIn("evidence layer", self.skill)
        self.assertIn("A unit test does not prove", self.skill)
        self.assertIn("scenario-level acceptance-to-evidence mapping", self.skill)

    def test_final_code_review_and_failed_scenario_rerun_are_required(self) -> None:
        self.assertIn("require C0 `pass` after the final code change", self.skill)
        self.assertIn("entered an L1", self.skill)
        self.assertIn("unchanged original scenario", self.skill)
        self.assertIn("related regressions passed", self.skill)
        self.assertIn("Never demand a replay", self.skill)

    def test_web_acceptance_requires_current_chrome_evidence(self) -> None:
        self.assertIn("Codex App Chrome evidence", self.skill)
        self.assertIn("keep the scenario incomplete", self.skill)
        self.assertIn("reject a silent Playwright fallback", self.skill)

    def test_document_review_is_completion_evidence(self) -> None:
        self.assertIn("Current D0 document self-review", self.skill)
        self.assertIn("require a current D0 `pass`", self.skill)
        self.assertIn("D1 `通过`", self.skill)
        self.assertIn("accept `Clean` as `通过`", self.skill)
        self.assertIn("treat `Issues Found` as", self.skill)
        self.assertIn("D1 `不通过` as a completion issue", self.skill)

    def test_review_mode_is_proportional_to_risk(self) -> None:
        self.assertIn("main-agent-second-pass", self.skill)
        self.assertIn("ordinary guarded work", self.skill)
        self.assertIn("broad guarded work", self.skill)
        self.assertIn("multiple components/contracts", self.skill)
        self.assertIn("critical work", self.skill)
        self.assertIn("return `blocked`", self.skill)
        self.assertIn("do not present a main-agent fallback as", self.skill)

    def test_review_does_not_depend_on_legacy_artifacts(self) -> None:
        for forbidden in ("checklist", "progress.md", "completion-review.md", "sha256", "execute-complete"):
            self.assertNotIn(forbidden, self.skill.lower())


if __name__ == "__main__":
    unittest.main()
