from __future__ import annotations

import unittest

from tests._support import read


CORE_OPEN_DESIGN_CAPABILITIES = (
    "create_project",
    "write_file",
    "start_run",
    "get_run",
    "cancel_run",
    "get_artifact",
)

CONDITIONAL_DISCOVERY_CAPABILITIES = (
    "list_projects",
    "list_skills",
    "list_plugins",
    "list_agents",
)


class PrototypeContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = read("skills/bruce/SKILL.md")
        cls.skill = read("skills/write-prototype/SKILL.md")
        cls.brief = read("skills/write-prototype/templates/prototype-brief.md")
        cls.generation_input = read(
            "skills/write-prototype/templates/generation-input.md"
        )
        cls.ui_contract = read(
            "skills/write-prototype/templates/repository-ui-contract.md"
        )
        cls.surface_contract = read(
            "skills/write-prototype/references/ui-surface-contract.md"
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
        for capability in CORE_OPEN_DESIGN_CAPABILITIES:
            with self.subTest(capability=capability):
                self.assertIn(f"`{capability}`", self.skill)
        for capability in CONDITIONAL_DISCOVERY_CAPABILITIES:
            with self.subTest(capability=capability):
                self.assertIn(f"`{capability}`", self.skill)
        self.assertIn("Conditional discovery capabilities", self.skill)
        self.assertIn("selected conditional discovery capability", self.skill)
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
        self.assertIn("otherwise use `get_run`", normalized)
        self.assertIn("explicit user request", normalized)
        self.assertIn("terminal `succeeded` result has no artifact", normalized)
        self.assertIn("provider's agent message", normalized)
        self.assertIn("no generated snapshot", normalized)

    def test_preflight_discovery_is_selective_when_inputs_are_explicit(self) -> None:
        normalized = " ".join(self.skill.split())
        for marker in (
            "selection matrix",
            "do not enumerate",
            "plugin=none",
            "design-system=none",
            "Never rely on a provider default Agent route",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker.lower(), normalized.lower())
        self.assertIn("discovery_mode", self.manifest)

    def test_repository_visual_authority_skips_direction_discovery(self) -> None:
        normalized = " ".join(self.skill.split())
        for marker in (
            "direction_selection=skip",
            "repository/runtime visual authority",
            "prohibit Direction library probing",
            "unknown subcommand",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker.lower(), normalized.lower())
        self.assertIn("direction_selection", self.brief)
        self.assertIn("direction_selection", self.manifest)

    def test_generation_uses_compact_context_and_incremental_hashes(self) -> None:
        normalized = " ".join(self.skill.split())
        for marker in (
            "generation-input.md",
            "context_hash",
            "context_files",
            "sync_mode=full",
            "synchronize only the changed",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker.lower(), normalized.lower())
        for field in ("context_hash", "sync_mode", "source_evidence"):
            self.assertIn(field, self.generation_input)
            self.assertIn(field, self.manifest)

    def test_generation_skill_readiness_does_not_mislabel_a_wrapper_as_a_template(self) -> None:
        normalized = " ".join(self.skill.split())
        for marker in (
            "generation_skill_readiness",
            "wrapper-only generation skill",
            "generate from scratch",
            "ready-made prototype template",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker.lower(), normalized.lower())
        self.assertIn("generation_skill_readiness", self.brief)
        self.assertIn("generation_skill_readiness", self.manifest)

    def test_run_observation_is_incremental_and_specific(self) -> None:
        normalized = " ".join(self.skill.split())
        for marker in (
            "45–60 second interval",
            "wait_run",
            "get_run_events",
            "get_run_summary",
            "reconnecting",
            "stalled_candidate",
            "last_event_id",
            "last_progress_at",
            "without nested long sleeps",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker.lower(), normalized.lower())
        for field in ("provider_state", "observation_mode", "last_event_id"):
            self.assertIn(field, self.manifest)

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

    def test_surface_contract_reference_is_stack_neutral_and_separate(self) -> None:
        for marker in (
            "Surface Contract",
            "surface_id",
            "region hierarchy",
            "required states",
            "interaction transitions",
            "observable fields",
            "layout invariants",
            "viewports",
            "evidence methods",
            "implementation mappings",
            "file",
            "route",
            "template",
            "view",
            "source-entry",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.surface_contract)
        self.assertIn("must not require a React/Vue component tree", self.surface_contract)
        self.assertIn("visual-assertions.json", self.surface_contract)
        self.assertIn("surface_contract_path", self.manifest)
        self.assertIn("Surface Contract", self.ui_contract)

    def test_surface_contract_fields_are_present_in_existing_product_templates(self) -> None:
        normalized_brief = " ".join(self.brief.split()).lower()
        normalized_contract = " ".join(self.ui_contract.split()).lower()
        for marker in (
            "surface id",
            "regions and hierarchy",
            "required states",
            "interaction transitions",
            "observable fields",
            "layout invariants",
            "visual anchors",
            "required viewports",
            "evidence methods",
            "implementation mapping",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, normalized_brief)
                self.assertIn(marker, normalized_contract)
        for forbidden in ("must require a react", "must require a vue", "framework ast as a required"):
            self.assertNotIn(forbidden, normalized_brief)
            self.assertNotIn(forbidden, normalized_contract)

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

    def test_existing_product_visual_authority_is_strict_and_provider_defaults_are_limited(self) -> None:
        normalized = " ".join(self.skill.split())
        for marker in (
            "visual authority contract",
            "repository theme/source governs",
            "provider/framework defaults only for uncovered gaps",
            "confirmed requirements > current runtime screenshot/dom",
            "do not allow a provider default to replace",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker.lower(), normalized.lower())
        self.assertIn("Unchanged-surface protection", self.brief)
        self.assertIn("Visual authority and plugin compatibility", self.ui_contract)

    def test_generation_skill_and_visual_plugin_are_audited_separately(self) -> None:
        normalized = " ".join(self.skill.split())
        for field in (
            "selected_generation_skill",
            "selected_visual_plugin",
            "selected_design_system",
            "selection_basis",
            "compatibility_check",
            "effective_plugin",
            "effective_design_system",
            "run_input_summary",
        ):
            with self.subTest(field=field):
                self.assertIn(field, self.manifest)
                self.assertIn(field, self.brief)
        self.assertIn("generation capability and visual policy as separate selections", normalized)
        self.assertIn("blocked-before-generation", normalized)
        self.assertIn("do not silently default to `design-system-ant`", normalized)

    def test_deterministic_visual_assertions_are_required_before_manual_only(self) -> None:
        normalized = " ".join(self.skill.split())
        self.assertIn("visual-assertions.json", normalized)
        self.assertIn("validate_prototype_artifact.py", normalized)
        for field in (
            "exact_colors",
            "exact_dimensions",
            "required_brand_text",
            "forbidden_tokens",
        ):
            self.assertIn(field, self.ui_contract)
        self.assertIn("exact_token_assertions", self.manifest)
        self.assertIn("artifact_visual_checker", self.manifest)
        self.assertIn("failed exact assertion", normalized)
        self.assertIn("manual-only", normalized)
        self.assertIn("cannot override it", normalized)

    def test_refinement_context_sync_fails_closed_before_start_run(self) -> None:
        normalized = " ".join(self.skill.split())
        self.assertIn("validate the complete local brief/assertion patch before project mutation", normalized)
        self.assertIn("verify provider-side readability", normalized)
        self.assertIn("Any step failure stops before `start_run`", normalized)

    def test_design_gate_requires_compatibility_and_clear_deterministic_assertions(self) -> None:
        normalized = " ".join(self.design_gate.split())
        for marker in (
            "selected/effective generation skill and visual plugin/design-system",
            "compatibility evidence",
            "run input summary",
            "exact_token_assertions = blocked",
            "deterministic assertions must be `clear` first",
        ):
            self.assertIn(marker, normalized)

    def test_completion_gate_keeps_provider_success_and_manual_only_fail_closed(self) -> None:
        normalized = " ".join(self.completion_gate.split())
        for marker in (
            "selected/effective generation skill and visual plugin/design-system",
            "artifact checker's result",
            "blocked exact token assertion",
            "provider succeeded",
            "manual-only confirmation",
        ):
            self.assertIn(marker, normalized)

    def test_high_fidelity_requires_filled_visual_grounding(self) -> None:
        normalized_skill = " ".join(self.skill.split())
        normalized_gate = " ".join(self.design_gate.split())
        for body in (normalized_skill, normalized_gate):
            self.assertIn("placeholders", body)
            self.assertIn("empty evidence/verification", body)
            for dimension in ("shell/layout", "palette", "typography", "brand", "geometry"):
                self.assertIn(dimension, body)
        self.assertIn("A template heading alone is not grounded evidence", normalized_skill)

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
