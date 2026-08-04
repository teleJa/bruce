from __future__ import annotations

import unittest

from tests._support import read


REQUIRED_OPEN_DESIGN_CAPABILITIES = (
    "list_projects",
    "create_project",
    "write_file",
    "list_skills",
    "list_plugins",
    "list_agents",
    "start_run",
    "get_run",
    "cancel_run",
    "get_artifact",
)


class PrototypeContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = read("skills/bruce/SKILL.md")
        cls.skill = read("skills/write-prototype/SKILL.md")
        cls.brief = read("skills/write-prototype/templates/prototype-brief.md")
        cls.ui_contract = read(
            "skills/write-prototype/templates/repository-ui-contract.md"
        )
        cls.manifest = read("skills/write-prototype/templates/prototype-manifest.md")
        cls.design_gate = read("skills/design-gate/SKILL.md")
        cls.design_review = read("skills/design-gate/templates/design-review.md")
        cls.completion_gate = read("skills/completion-gate/SKILL.md")

    def test_prototype_capability_is_optional_and_predicate_driven(self) -> None:
        normalized = " ".join(self.skill.split())
        self.assertIn("`write-prototype`", self.workflow)
        self.assertIn("explicitly requests a prototype", normalized)
        self.assertIn("confirmed prototype must govern", normalized)
        self.assertIn("does not trigger this skill", normalized)
        self.assertIn("Do not invoke another supporting skill automatically", self.skill)

    def test_open_design_requires_the_complete_host_capability_set(self) -> None:
        for capability in REQUIRED_OPEN_DESIGN_CAPABILITIES:
            with self.subTest(capability=capability):
                self.assertIn(f"`{capability}`", self.skill)
        self.assertIn("fixed MCP server prefix", self.skill)
        self.assertIn("Block before creating or changing an Open Design project", self.skill)
        self.assertIn("Do not install", self.skill)
        self.assertIn("do not silently substitute", self.skill.lower())

    def test_generation_input_is_grounded_and_stops_on_material_unknowns(self) -> None:
        for status in ("confirmed", "inferred", "unresolved"):
            self.assertIn(status, self.skill)
            self.assertIn(status, self.brief)
        for evidence in ("design system", "theme token", "component", "source evidence"):
            self.assertIn(evidence, self.skill.lower())
        self.assertIn("Material unresolved facts", self.skill)
        self.assertIn("must not contain credentials", self.brief)

    def test_project_and_run_lifecycle_is_deterministic(self) -> None:
        normalized = " ".join(self.skill.split())
        self.assertIn("<repository>-<change>-<surface>", self.skill)
        self.assertIn("100 characters", self.skill)
        self.assertIn("Pass the project id explicitly", self.skill)
        self.assertIn("halt without resubmitting", normalized)
        self.assertIn("poll `get_run`", normalized)
        self.assertIn("explicit user request", normalized)
        self.assertIn("terminal `succeeded` result has no artifact", normalized)
        self.assertIn("provider's agent message", normalized)
        self.assertIn("no generated snapshot", normalized)

    def test_generated_and_confirmed_artifacts_remain_distinct_and_safe(self) -> None:
        normalized = " ".join(self.skill.split())
        for marker in (
            "generated_snapshot",
            "confirmed_snapshot",
            "sha256",
            "safety_check",
            "confirmation",
            "known_gaps",
        ):
            self.assertIn(marker, self.manifest)
        self.assertIn("pending, running, succeeded, failed, or canceled", self.manifest)
        self.assertIn("untrusted", self.skill)
        self.assertIn("remote resources", self.skill.lower())
        self.assertIn("real backend", self.skill)
        self.assertIn("Only a confirmed snapshot", normalized)
        self.assertIn("prototype/versions/<run-id>/generated", self.skill)
        self.assertIn("prototype/versions/<run-id>/confirmed", self.skill)

    def test_existing_gates_own_prototype_readiness_and_alignment(self) -> None:
        for body in (self.design_gate, self.design_review):
            self.assertIn("UI prototype", body)
        self.assertIn("`prototype-manifest.md`", self.design_gate)
        self.assertIn("confirmed", self.design_gate)
        self.assertIn("prototype", self.completion_gate.lower())
        self.assertIn("current Codex App Chrome evidence", self.completion_gate)
        self.assertNotIn("prototype-gate", self.workflow)

    def test_existing_product_extension_requires_grounding_bundle(self) -> None:
        normalized = " ".join(self.skill.split())
        self.assertIn("`greenfield` or `existing-product-extension`", normalized)
        self.assertIn("`prototype-context/repository-ui-contract.md`", self.skill)
        for field in (
            "Host surface",
            "Exact entry",
            "Destination surface",
            "Layout invariants",
            "Reuse anchors",
            "Visual anchors",
            "Baseline artifacts",
            "Evidence gaps",
        ):
            with self.subTest(field=field):
                self.assertIn(field, self.ui_contract)
        self.assertIn("source-grounded wireframe", normalized)

    def test_changed_and_unchanged_evidence_authority_is_explicit(self) -> None:
        for rule in (
            "Confirmed requirements govern changed behavior",
            "runtime screenshot or DOM evidence governs unchanged visible state",
            "confirmed prototype governs the refinement baseline",
            "Provider and framework defaults may fill only uncovered gaps",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, self.skill)
        self.assertIn("Source revision and drift", self.ui_contract)

    def test_preflight_records_explicit_agent_cli_inputs_and_visual_capability(self) -> None:
        normalized = " ".join(self.skill.split())
        for field in (
            "selected_agent",
            "agent_readiness",
            "cli_compatibility",
            "input_readability",
            "visual_capability",
            "preflight_status",
        ):
            with self.subTest(field=field):
                self.assertIn(field, self.manifest)
        self.assertIn("`blocked-before-generation`", normalized)
        self.assertIn("`partial`", normalized)
        self.assertIn("Do not claim preflight passed", self.skill)

    def test_effective_output_rejects_no_artifact_and_unchanged_refinement(self) -> None:
        normalized = " ".join(self.skill.split())
        self.assertIn("`artifactCount == 0`", normalized)
        self.assertIn("`no_artifact`", normalized)
        self.assertIn("unchanged refinement target SHA-256", normalized)
        self.assertIn("`no_effect`", normalized)
        self.assertIn("Neither state creates", normalized)
        self.assertIn("effective_output_state", self.manifest)
        self.assertIn("artifact_count", self.manifest)

    def test_first_noop_refinement_switches_to_deterministic_fresh_lineage(self) -> None:
        normalized = " ".join(self.skill.split())
        self.assertIn("first explicit refinement no-op", normalized)
        self.assertIn("`<base-project-id>-r<sequence>`", self.skill)
        for field in (
            "parent_project_id",
            "parent_run_id",
            "baseline_sha256",
        ):
            with self.subTest(field=field):
                self.assertIn(field, self.manifest)

    def test_acceptance_dimensions_cannot_substitute_for_each_other(self) -> None:
        normalized = " ".join(self.skill.split())
        for check in (
            "Functional",
            "Visual",
            "Safety",
            "Provenance",
        ):
            with self.subTest(check=check):
                self.assertIn(check, self.skill)
                self.assertIn(f"{check.lower()}_check", self.manifest)
        self.assertIn("must not substitute", normalized)
        self.assertIn("provider score", normalized)
        self.assertIn("region-specific", normalized)

    def test_manual_visual_confirmation_never_claims_automated_pass(self) -> None:
        normalized = " ".join(self.skill.split())
        self.assertIn("`visual_evidence = manual-only`", self.skill)
        self.assertIn("explicit user inspection", normalized)
        self.assertIn("does not mean automated Visual pass", normalized)
        self.assertIn("automated, manual-only, or unavailable", self.manifest)

    def test_governing_visual_state_and_evidence_pairs_fail_closed(self) -> None:
        normalized_skill = " ".join(self.skill.split())
        normalized_gate = " ".join(self.design_gate.split())
        for body in (normalized_skill, normalized_gate):
            with self.subTest(body=body[:40]):
                self.assertIn("`automated-clear + automated`", body)
                self.assertIn("`manual-confirmed + manual-only`", body)
                lower_body = body.lower()
                self.assertIn("pending", lower_body)
                self.assertIn("blocked", lower_body)
                self.assertIn("unavailable", lower_body)
                self.assertIn("cannot govern", lower_body)
        self.assertIn("inspected exact snapshot", normalized_skill)

    def test_effective_output_and_confirmation_lifecycle_are_separate(self) -> None:
        output_line = next(
            line
            for line in self.manifest.splitlines()
            if line.startswith("- effective_output_state:")
        )
        for state in (
            "blocked-before-generation",
            "failed",
            "canceled",
            "no_artifact",
            "no_effect",
            "generated",
        ):
            with self.subTest(state=state):
                self.assertIn(state, output_line)
        self.assertNotIn("confirmed", output_line)
        self.assertIn("confirmation_state", self.manifest)
        normalized = " ".join(self.skill.split())
        self.assertIn("never overwrite", normalized)
        self.assertIn("`effective_output_state = generated`", normalized)

    def test_feedback_becomes_positive_and_negative_regression_assertions(self) -> None:
        normalized = " ".join(self.skill.split())
        self.assertIn("Positive assertions", self.brief)
        self.assertIn("Negative assertions", self.brief)
        self.assertIn("positive and one negative", normalized)
        self.assertIn("Do not start refinement", normalized)

    def test_manifest_history_survives_snapshot_cleanup(self) -> None:
        normalized = " ".join(self.skill.split())
        self.assertIn("Run history", self.manifest)
        for field in (
            "Project / run",
            "Output state",
            "Artifact count",
            "Hash summary",
            "Snapshot retention",
        ):
            with self.subTest(field=field):
                self.assertIn(field, self.manifest)
        self.assertIn("Deleting an old local snapshot", normalized)
        self.assertIn("must not delete", normalized)


if __name__ == "__main__":
    unittest.main()
