from __future__ import annotations

import unittest

from tests._support import read


class ValidationLoopContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = read("skills/bruce/SKILL.md")
        cls.policy = read("skills/bruce/references/verification-loop.md")
        cls.failure = read("skills/bruce/references/failure-recovery.md")
        cls.write_plan = read("skills/write-plan/SKILL.md") + read("skills/write-plan/templates/plan.md")
        cls.write_tests = read("skills/write-tests/SKILL.md") + read("skills/write-tests/templates/test-plan.md")

    def test_behavior_acceptance_has_gwt_and_evidence(self) -> None:
        for field in ("`Given`", "`When`", "`Then`", "`Evidence`"):
            self.assertIn(field, self.policy)
        self.assertIn("stable id", self.policy)
        self.assertIn("Given/When/Then/Evidence", self.write_tests)
        self.assertIn("scenario ids with Given/When/Then", self.write_plan)

    def test_material_outcome_requires_evidence_before_implementation(self) -> None:
        self.assertIn("Do not start behavior implementation", self.policy)
        self.assertIn("no feasible evidence path", self.policy)
        self.assertIn("explicitly accepts an exploratory", self.policy)

    def test_visual_scope_is_proportional_not_frontend_path_based(self) -> None:
        normalized = " ".join(self.policy.split())
        for scope in ("visual_scope=none", "visual_scope=browser-smoke", "visual_scope=browser-layout"):
            self.assertIn(scope, normalized)
        self.assertIn("Do not infer `browser-layout` from any frontend diff alone", normalized)
        self.assertIn("DOM text presence alone is not visual evidence", normalized)
        self.assertIn("basis revision", normalized)
        self.assertIn("absent `visual_scope` remains an unresolved contract gap", normalized)
        test_normalized = " ".join(self.write_tests.split())
        self.assertIn("proportional `visual_scope`", test_normalized)
        self.assertIn("layout invariant and interaction evidence", test_normalized)

    def test_runtime_dependencies_require_one_read_only_preflight(self) -> None:
        normalized = " ".join(self.policy.split())
        for phrase in (
            "perform one minimal read-only preflight",
            "status=available|unavailable|unknown",
            "dependent acceptance ids",
            "pause only their batch",
            "Do not repeat the same preflight",
        ):
            self.assertIn(phrase, normalized)

    def test_feedback_is_not_another_gate(self) -> None:
        self.assertIn("Continuous author feedback", self.policy)
        self.assertIn("not separately named gates", self.policy)
        self.assertIn("final state once", self.policy)
        self.assertNotIn("C0", self.policy)
        self.assertNotIn("D0", self.policy)

    def test_independence_is_internal_to_an_owning_gate(self) -> None:
        self.assertIn("Independence is a review mode inside", self.policy)
        self.assertIn("never a third verdict", self.policy)
        self.assertIn("fresh native subagent", self.policy)
        self.assertIn("Exclude author rationale, confidence, and proposed conclusion", self.policy)

    def test_verification_layers_cannot_substitute(self) -> None:
        for layer in ("Unit/component", "Integration/API/database", "Real-use"):
            self.assertIn(layer, self.policy)
        self.assertIn("never substitute a lower layer", self.policy)
        self.assertIn("mocked-only evidence", self.policy)

    def test_web_uses_configured_provider_without_silent_fallback(self) -> None:
        self.assertIn("verification.browser_provider", self.policy)
        self.assertIn("default is `ego-lite`", self.policy)
        self.assertIn("supported values are `ego-lite` and `chrome`", self.policy)
        self.assertIn("do not silently switch Provider", self.policy)
        self.assertIn("browser-provider.md", self.policy)
        self.assertIn("selected Provider", self.policy)
        self.assertIn("Provider capability requirements", self.workflow)

    def test_failed_scenario_closes_repair_and_regression_loop(self) -> None:
        self.assertIn("preserve the original scenario and evidence", self.policy.lower())
        self.assertIn("rerun\nthe original failed scenario unchanged", self.policy)
        self.assertIn("related regressions", self.policy)
        self.assertIn("`repair_round` counts only", self.failure)
        self.assertIn("Move exhausted L0/L1 work to L2", self.failure)

    def test_completion_evidence_is_passed_once(self) -> None:
        self.assertIn("For each acceptance id", self.policy)
        self.assertIn("required verification layer", self.policy)
        self.assertIn("Pass this evidence once", self.policy)
        self.assertIn("do not create parallel verdicts", self.policy)

    def test_completion_repairs_converge_without_per_finding_reviews(self) -> None:
        normalized = " ".join(self.policy.split())
        self.assertIn("one matrix across acceptance ids", normalized)
        self.assertIn("returns all current findings together", normalized)
        self.assertIn("does not create a per-finding review chain", normalized)

    def test_batch_checkpoint_is_early_feedback_not_a_second_verdict(self) -> None:
        normalized = " ".join(self.workflow.split())
        for phrase in (
            "batch checkpoint",
            "returns `Checkpoint: clear|issues|blocked`",
            "never returns `Completion`",
            "Use the final `completion-gate` once all batches are complete",
        ):
            self.assertIn(phrase, normalized)

    def test_cross_component_batch_change_map_stops_single_finding_expansion(self) -> None:
        normalized = " ".join(self.policy.split())
        for phrase in (
            "use the first failing scenario only to establish the batch boundary",
            "build a batch change map",
            "owned entry points, direct call sites, allowed paths, material state/error paths, and planned evidence",
            "do not follow each downstream failure into an undeclared component",
            "After the second non-blocking finding in the same batch",
            "stop single-finding repair",
            "Only a failure that prevents safe evidence collection",
        ):
            self.assertIn(phrase, normalized)

    def test_checkpoint_schema_is_machine_readable_and_complete(self) -> None:
        for phrase in (
            "Every checkpoint uses this machine-readable summary",
            "Checkpoint: clear|issues|blocked",
            "batch_id: B1-example",
            "basis_revision",
            "acceptance:",
            "repair_sets: []",
            "next_action:",
        ):
            self.assertIn(phrase, self.policy)

    def test_checkpoint_batches_non_blocking_findings_before_repair(self) -> None:
        normalized = " ".join(self.policy.split())
        for phrase in (
            "Before repairing a non-blocking batch failure, complete the current batch matrix",
            "all currently observable failures in one batch findings packet",
            "`blocking`",
            "`compatible`",
            "`deferred`",
            "group these findings into one bounded repair set",
            "Do not repair each newly observed non-blocking finding while the batch matrix remains incomplete",
            "do not use an `update_plan` progress update as a substitute",
            "repair compatible findings together",
        ):
            self.assertIn(phrase, normalized)

    def test_workflow_requires_batch_packet_before_non_blocking_repair(self) -> None:
        normalized = " ".join(self.workflow.split())
        for phrase in (
            "Complete the batch matrix and return one batch findings packet before repairing non-blocking failures",
            "repair compatible findings together in one bounded repair set",
            "An `update_plan` progress update never substitutes for this checkpoint",
        ):
            self.assertIn(phrase, normalized)

    def test_checkpoint_matrix_is_bounded_and_stale_aware(self) -> None:
        normalized = " ".join(self.policy.split())
        for phrase in (
            "Build the matrix for the current batch only",
            "direct changed entry points and direct call sites",
            "evidence_revision",
            "impact cannot be determined",
            "related regressions",
        ):
            self.assertIn(phrase, normalized)

    def test_loop_consumes_versioned_track_results_without_becoming_completion(self) -> None:
        normalized = " ".join(self.policy.split())
        for phrase in (
            "Shared Scenario and Track Result consumption",
            "exact `scenario_id + scenario_version`",
            "API/UI namespaces and write paths are distinct",
            "`overall_status=passed` is only a scenario/track evidence state",
            "not `Completion: pass`",
            "Dynamic results remain in Verification Run/Checkpoint",
        ):
            self.assertIn(phrase, normalized)



if __name__ == "__main__":
    unittest.main()
