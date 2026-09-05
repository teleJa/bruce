from __future__ import annotations

import re
import unittest

import yaml

from tests._support import read


class CompletionContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = read("skills/completion-gate/SKILL.md")

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

    def test_review_batches_complete_findings_before_repair(self) -> None:
        normalized = " ".join(self.skill.split())
        for phrase in (
            "build one review matrix",
            "material early-return/error/empty/null/partial/duplicate/state path",
            "Report all findings from the completed matrix together in one packet",
            "does not invalidate unaffected matrix rows",
            "does not create a per-finding review chain",
            "completed matrix and one consolidated findings packet",
        ):
            self.assertIn(phrase, normalized)

    def test_final_matrix_is_bounded_and_revision_aware(self) -> None:
        normalized = " ".join(self.skill.split())
        for phrase in (
            "direct changed entry point and direct call site",
            "do not expand transitive callers",
            "batch_id",
            "basis_revision",
            "evidence_revision",
            "impact cannot be determined",
        ):
            self.assertIn(phrase, normalized)

    def test_risk_trigger_is_checked(self) -> None:
        normalized = " ".join(self.skill.split())
        self.assertIn("A `low` task records `trigger=none`", normalized)
        self.assertIn("matching risk-policy trigger", normalized)

    def test_acceptance_evidence_is_scenario_and_layer_specific(self) -> None:
        self.assertIn("Map every acceptance condition", self.skill)
        self.assertIn("current, reproducible evidence", self.skill)
        self.assertIn("A unit test\ndoes not prove", self.skill)
        self.assertIn("acceptance-to-evidence references", self.skill)

    def test_cross_object_consistency_requires_authority_and_conflict_evidence(self) -> None:
        normalized = " ".join(self.skill.split())
        for phrase in (
            "consistency_check: required",
            "consistency and authority matrix",
            "authoritative state",
            "competing writer/viewer",
            "stale window",
            "已占用资源",
            "旧快照提交",
            "并发竞争",
            "`hidden`、`denied`、`missing`",
            "仅正常路径成功不能产生",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, normalized)

    def test_task_package_state_is_required_for_completion(self) -> None:
        normalized = " ".join(self.skill.split())
        for phrase in (
            "tasks/index.yaml",
            "frozen task contracts",
            "checkpoint.yaml",
            "Every required task that is not `superseded` must be `verified`",
            "`Completion: issues`",
            "`Completion: blocked`",
            "do not infer Goal state from a checkpoint",
        ):
            self.assertIn(phrase, normalized)

    def test_web_acceptance_requires_configured_provider(self) -> None:
        self.assertIn("Provider\nselected by `verification.browser_provider`", self.skill)
        self.assertIn("keep the scenario incomplete or blocked", self.skill)
        self.assertIn("Do not substitute another Provider", self.skill)
        self.assertIn("browser-layout", self.skill)
        self.assertIn("configured browser Provider", self.skill)

    def test_surface_contract_rows_require_mapping_and_fresh_runtime_evidence(self) -> None:
        for marker in (
            "Surface review matrix",
            "review-matrix row per required `surface_id`",
            "implementation locator",
            "runtime evidence",
            "layout evidence",
            "evidence revision/freshness",
            "Missing mappings, stale",
            "static Surface validator",
            "never create a second UI verdict",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.skill)
        self.assertIn("browser-layout", self.skill)
        self.assertIn("geometry/overflow", self.skill)

    def test_visual_scope_is_risk_proportional_and_fresh(self) -> None:
        normalized = " ".join(self.skill.split())
        for scope in ("`none`", "`browser-smoke`", "`browser-layout`"):
            self.assertIn(scope, normalized)
        for phrase in (
            "Do not turn every frontend or UI-file diff into a full visual run",
            "DOM snapshot or text assertion cannot substitute",
            "basis revision",
            "reopen the affected acceptance rows",
            "declared scope is missing",
        ):
            self.assertIn(phrase, normalized)

    def test_design_alignment_returns_issue_without_reimplementing_design_gate(self) -> None:
        self.assertIn("compare the final diff and scope with `design-review.md`", self.skill)
        self.assertIn("Do not rerun Design Gate inside completion", self.skill)
        self.assertIn("return the mismatch to Bruce for one explicit rerun", self.skill)

    def test_independence_is_an_internal_review_mode(self) -> None:
        normalized = " ".join(self.skill.split())
        self.assertIn("Mandatory review-mode selection", self.skill)
        self.assertIn("Before author-quality checks or review-matrix construction", normalized)
        self.assertIn("record exactly one `review_mode` plus one stable `review_mode_reason`", normalized)
        reasons = (
            "`explicit-independent-request`: the user explicitly requested independent review",
            "`critical-risk`: risk is `critical`",
            "`guarded-multi-component-contract`: risk is `guarded` and the final state spans multiple components or propagated contracts",
            "`guarded-migration-rollout`: risk is `guarded` and the task combines migration and rollout",
            "`guarded-semantic-ambiguity`: risk is `guarded` and material semantic ambiguity remains",
            "`guarded-weak-evidence`: risk is `guarded` and the result relies mainly on weak executable evidence",
            "`guarded-repeated-repair`: risk is `guarded` and the current task completed two or more L1 repair rounds",
            "`guarded-broad-security-data-impact`: risk is `guarded` and the final state has broad security or data impact",
            "`none`: no independent trigger remains",
        )
        self.assertIn("Select the first matching reason in this precedence order", normalized)
        section = self.skill.split("## Mandatory review-mode selection", 1)[1].split(
            "## Internal checks", 1
        )[0]
        actual_reasons = re.findall(r"^\d+\. (`[^`]+`):", section, flags=re.MULTILINE)
        normalized_section = " ".join(section.split())
        for reason in reasons:
            self.assertIn(reason, normalized_section)
        expected_reasons = [reason.split(":", 1)[0] for reason in reasons]
        self.assertEqual(expected_reasons, actual_reasons)
        self.assertIn(
            "Reasons 1-8 require `review_mode: independent`; reason 9 requires `review_mode: main-agent`",
            normalized,
        )
        self.assertIn("Do not silently downgrade", normalized)
        self.assertIn("Exclude author rationale, confidence, and proposed verdict", normalized)
        self.assertIn("not a second externally combined verdict", normalized)
        self.assertIn(
            "if a clean-context native reviewer is unavailable, return `Completion: blocked`",
            normalized,
        )
        self.assertIn("`review_mode_reason`", self.skill)

    def test_repair_and_delivery_boundaries_are_checked(self) -> None:
        self.assertIn("unchanged original failed scenario", self.skill)
        self.assertIn("related regressions", self.skill)
        self.assertIn("L2-L4", self.skill)
        self.assertIn("delivery actions", self.skill)

    def test_output_example_uses_one_stable_completion_protocol(self) -> None:
        self.assertIn("### Output format example", self.skill)
        output_section = self.skill.split("### Output format example", 1)[1].split(
            "## Does not own", 1
        )[0]
        self.assertIn("`Completion` is the only terminal verdict", output_section)
        self.assertIn("Do not use aliases such as `completion_verdict`", output_section)
        self.assertNotIn("completion_verdict:", output_section)
        match = re.search(r"```yaml\n(.*?)\n```", output_section, flags=re.DOTALL)
        self.assertIsNotNone(match)
        example_text = match.group(1)
        example = yaml.safe_load(example_text)
        expected_fields = [
            "Completion",
            "review_mode",
            "review_mode_reason",
            "review_matrix",
            "findings",
            "acceptance_evidence",
            "design_alignment",
            "scope_findings",
            "repair_loop_results",
            "residual_risks",
            "next_action",
        ]
        self.assertEqual(expected_fields, list(example))
        self.assertEqual("pass", example["Completion"])
        self.assertEqual("independent", example["review_mode"])
        self.assertEqual("guarded-multi-component-contract", example["review_mode_reason"])
        self.assertEqual(1, len(re.findall(r"^Completion:", example_text, flags=re.MULTILINE)))
        for field in (
            "findings",
            "scope_findings",
            "repair_loop_results",
            "residual_risks",
        ):
            self.assertEqual([], example[field])

    def test_compact_output_has_one_verdict_and_real_evidence_slot(self) -> None:
        section = self.skill.split("### Compact output example", 1)[1].split("### Output format example", 1)[0]
        match = re.search(r"```yaml\n(.*?)\n```", section, flags=re.DOTALL)
        self.assertIsNotNone(match)
        example = yaml.safe_load(match.group(1))
        self.assertEqual("pass", example["Completion"])
        self.assertTrue(example["changes"])
        self.assertTrue(example["acceptance_evidence"])
        self.assertTrue(example["acceptance_evidence"][0]["evidence"])
        self.assertIn("residual_risks", example)
        self.assertIn("next_action", example)
        self.assertNotIn("review_matrix", example)
        self.assertNotIn("batch_id", example)
        self.assertEqual(1, len(re.findall(r"^Completion:", match.group(1), re.MULTILINE)))

    def test_output_mode_and_reason_pairing_is_explicit(self) -> None:
        normalized = " ".join(self.skill.split())
        self.assertIn(
            "`review_mode: main-agent` requires `review_mode_reason: none`",
            normalized,
        )
        self.assertIn(
            "`review_mode: independent` requires one of reasons 1-8",
            normalized,
        )

    def test_legacy_multi_verdict_fields_are_absent(self) -> None:
        for marker in (
            "Verification: V0",
            "Author checks: C0/D0",
            "Independent review: R1",
            "not-run",
        ):
            self.assertNotIn(marker, self.skill)

    def test_completion_consumes_track_results_and_keeps_single_completion_authority(self) -> None:
        normalized = " ".join(self.skill.split())
        for phrase in (
            "Scenario and Track Result evidence",
            "one exact `scenario_id + scenario_version`",
            "distinct namespaces and non-overlapping `allowed_paths`",
            "`overall_status=passed` is only the Test Dispatch aggregation state",
            "not `Completion: pass`",
            "do not modify aggregation rules to manufacture a pass",
        ):
            self.assertIn(phrase, normalized)



if __name__ == "__main__":
    unittest.main()
