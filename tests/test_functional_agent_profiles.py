from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.functional_agent_profiles import (
    ContractError,
    PROFILE_IDS,
    load_builtin_profiles,
    resolve_profile,
    validate_changed_paths,
    validate_output_packet,
    validate_task_packet,
)
from tests._support import ROOT, read


class FunctionalAgentProfileContractTest(unittest.TestCase):
    def test_profile_registry_and_routing_matrix(self) -> None:
        validator = (ROOT / "scripts/validate_functional_agents.py").read_text(encoding="utf-8")
        self.assertEqual({"inspector", "implementer", "verifier", "reviewer"}, set(PROFILE_IDS))
        profiles = load_builtin_profiles()
        self.assertEqual("gpt-5.6-sol", profiles["inspector"]["default_model"])
        self.assertEqual("gpt-5.6-luna", profiles["implementer"]["default_model"])
        self.assertEqual("max", profiles["implementer"]["reasoning_effort"])
        self.assertEqual("gpt-5.6-luna", profiles["verifier"]["default_model"])
        self.assertEqual("max", profiles["verifier"]["reasoning_effort"])
        self.assertEqual("gpt-5.6-terra", profiles["reviewer"]["default_model"])
        self.assertEqual("high", profiles["reviewer"]["reasoning_effort"])
        for profile_id in PROFILE_IDS:
            self.assertIn(profile_id, validator)
        for relative in (
            "skills/inspect-parallel/SKILL.md",
            "skills/spawn-execute/SKILL.md",
            "skills/explore-prototype/SKILL.md",
            "skills/completion-gate/SKILL.md",
            "skills/plan-review/SKILL.md",
            "skills/design-gate/SKILL.md",
        ):
            text = read(relative)
            self.assertTrue("Functional Agent" in text or "Profile" in text, relative)

    def test_task_packet_schema_and_invalid_variants(self) -> None:
        packet = {
            "schema_version": 1,
            "profile_id": "implementer",
            "task_packet": {
                "task_id": "T-1",
                "task_kind": "implement",
                "objective": "修复限定范围内的问题",
                "context": {"inherit": "task", "sources": ["src/example.py"]},
                "tools": {"allow": ["read", "write", "test"], "deny": ["deploy"]},
                "allowed_paths": ["src/**"],
                "model_capabilities": {"required": [], "preferred": [], "independence": "none"},
                "evidence": {"acceptance_ids": ["FA-01"], "required": ["unit-test"]},
                "output": "task_evidence_packet",
                "stop_conditions": ["路径越权时停止"],
            },
        }
        validate_task_packet(packet)
        mutations = [
            {"schema_version": 2},
            {"task_packet": {**packet["task_packet"], "objective": ""}},
            {"profile_id": "reviewer", "task_packet": packet["task_packet"]},
            {"task_packet": {**packet["task_packet"], "task_kind": "review"}},
            {"task_packet": {**packet["task_packet"], "task_kind": []}},
            {"task_packet": {**packet["task_packet"], "output": []}},

            {"task_packet": {**packet["task_packet"], "unexpected": True}},
            {"task_packet": {**packet["task_packet"], "tools": {"allow": ["deploy"], "deny": []}}},
            {"task_packet": {**packet["task_packet"], "stop_conditions": []}},
            {"task_packet": {**packet["task_packet"], "model_override": "/tmp/host-model"}},
            {"task_packet": {**packet["task_packet"], "model_override": "foo/../bar"}},
            {"task_packet": {**packet["task_packet"], "model_override": "sk-secret"}},
            {"task_packet": {**packet["task_packet"], "context": {"inherit": [], "sources": []}}},
        ]
        for mutation in mutations:
            invalid = dict(packet)
            invalid.update(mutation)
            with self.subTest(mutation=mutation), self.assertRaises(ContractError):
                validate_task_packet(invalid)

    def test_profile_specific_packet_constraints(self) -> None:
        def packet_for(profile_id: str, task_kind: str, inherit: str, independence: str, output: str) -> dict:
            return {
                "schema_version": 1,
                "profile_id": profile_id,
                "task_packet": {
                    "task_id": f"{profile_id}-task",
                    "task_kind": task_kind,
                    "objective": "核对角色边界",
                    "context": {"inherit": inherit, "sources": []},
                    "tools": {"allow": ["read", "test", "inspect"], "deny": ["write"]},
                    "allowed_paths": [],
                    "model_capabilities": {"required": [], "preferred": [], "independence": independence},
                    "evidence": {"acceptance_ids": ["FA-01"], "required": ["unit"]},
                    "output": output,
                    "stop_conditions": ["发现越权时停止"],
                },
            }

        reviewer = packet_for("reviewer", "review", "none", "required", "review_packet")
        validate_task_packet(reviewer)
        with self.assertRaises(ContractError):
            validate_task_packet({
                **reviewer,
                "task_packet": {**reviewer["task_packet"], "context": {"inherit": "task", "sources": []}},
            })
        with self.assertRaises(ContractError):
            validate_task_packet({
                **reviewer,
                "task_packet": {**reviewer["task_packet"], "model_capabilities": {"required": [], "preferred": [], "independence": "none"}},
            })

        verifier = packet_for("verifier", "verify", "task", "preferred", "verification_packet")
        validate_task_packet(verifier)
        with self.assertRaises(ContractError):
            validate_task_packet({
                **verifier,
                "task_packet": {**verifier["task_packet"], "context": {"inherit": "none", "sources": []}},
            })

    def test_permissions_and_allowed_paths(self) -> None:
        validate_changed_paths("implementer", ["src/**"], ["src/example.py"])
        with self.assertRaises(ContractError):
            validate_changed_paths("implementer", ["src/**"], ["tests/example.py"])
        with self.assertRaises(ContractError):
            validate_changed_paths("implementer", ["src/**"], ["../outside.py"])
        with self.assertRaises(ContractError):
            validate_changed_paths("inspector", [], ["src/example.py"])

    def test_reviewer_resolution_and_fallback(self) -> None:
        profile, resolution, args = resolve_profile(
            "reviewer", current_model="current-model", available_models={"gpt-5.6-terra"}
        )
        self.assertTrue(profile["context"]["clean"])
        self.assertEqual("resolved", resolution.resolution_result)
        self.assertEqual("gpt-5.6-terra", args["model"])

        _, fallback, fallback_args = resolve_profile(
            "reviewer", current_model="current-model", available_models=None
        )
        self.assertEqual("fallback", fallback.resolution_result)
        self.assertEqual("degraded", fallback.capability_status)
        self.assertTrue(fallback.fallback_used)
        self.assertEqual("current-model", fallback.effective_model)
        self.assertNotIn("model", fallback_args)

        _, blocked, blocked_args = resolve_profile(
            "reviewer", current_model="current-model", available_models={"other-model"}
        )
        self.assertEqual("blocked", blocked.resolution_result)
        self.assertEqual("current_model_unavailable", blocked.fallback_reason)
        self.assertNotIn("model", blocked_args)

    def test_resolution_precedence_and_invalid_override(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project.yaml"
            user = Path(directory) / "user.yaml"
            user.write_text("version: 1\nprofiles:\n  reviewer:\n    default_model: vendor/reviewer-model\n", encoding="utf-8")
            project.write_text("version: 1\nprofiles:\n  reviewer:\n    default_model: project-model\n", encoding="utf-8")
            _, resolution, _ = resolve_profile(
                "reviewer", current_model="current", user_path=user, project_path=project,
                available_models={"task-model"}, task_override={"model": "task-model"}
            )
            self.assertEqual("task-model", resolution.configured_model)
            self.assertEqual("task", resolution.source)
            bad = Path(directory) / "bad.yaml"
            bad.write_text("version: 1\nprofiles:\n  reviewer:\n    tools: [write]\n", encoding="utf-8")
            with self.assertRaises(ContractError):
                resolve_profile("reviewer", current_model="current", user_path=bad)
            invalid_fallback = Path(directory) / "invalid-fallback.yaml"
            invalid_fallback.write_text(
                "version: 1\nprofiles:\n  reviewer:\n    fallback: never\n",
                encoding="utf-8",
            )
            with self.assertRaises(ContractError):
                resolve_profile("reviewer", current_model="current", user_path=invalid_fallback)
            with self.assertRaises(ContractError):
                resolve_profile(
                    "reviewer", current_model="current", task_override={"model": "/tmp/host-model"}
                )

    def test_resolution_failure_matrix(self) -> None:
        _, blocked_model, _ = resolve_profile(
            "reviewer", current_model=None, available_models={"other-model"}
        )
        self.assertEqual("blocked", blocked_model.resolution_result)
        _, blocked_context, _ = resolve_profile(
            "reviewer", current_model="current", available_models={"gpt-5.6-terra"}, clean_context_available=False
        )
        self.assertEqual("blocked", blocked_context.resolution_result)
        _, blocked_tools, _ = resolve_profile(
            "implementer", current_model="current", available_models={"gpt-5.6-luna"}, required_tools={"deploy"}
        )
        self.assertEqual("blocked", blocked_tools.resolution_result)

    def test_evidence_packet_authority_boundary(self) -> None:
        resolution = {
            "requested_profile": "verifier",
            "configured_model": "gpt-5.6-luna",
            "effective_model": "gpt-5.6-luna",
            "fallback_used": False,
            "fallback_reason": None,
            "capability_status": "resolved",
            "resolution_result": "resolved",
            "source": "built-in",
        }
        validate_output_packet(
            {
                "schema_version": 1,
                "status": "completed",
                "output_type": "verification_packet",
                "acceptance_ids": ["FA-04"],
                "scenario_results": [],
                "repro_commands": ["python3 -m unittest"],
                "evidence_revision": "test-revision",
                "model_resolution": resolution,
                "gate_verdict": "absent",
            },
            "verification_packet",
        )
        validate_output_packet(
            {
                "schema_version": 1,
                "status": "completed",
                "output_type": "review_packet",
                "review_subject": "implementation",
                "review_mode": "independent",
                "review_mode_reason": "guarded-multi-component-contract",
                "findings": [],
                "review_matrix": [{"acceptance_id": "FA-04", "path": "x", "required_layer": "unit", "evidence": "test", "result": "pass"}],
                "model_resolution": {**resolution, "requested_profile": "reviewer"},
                "gate_verdict": "absent",
            },
            "review_packet",
        )
        with self.assertRaises(ContractError):
            validate_output_packet(
                {
                    "schema_version": 1,
                    "status": "completed",
                    "output_type": "review_packet",
                    "review_subject": "implementation",
                    "review_mode": "independent",
                    "review_mode_reason": "guarded-multi-component-contract",
                    "findings": [],
                    "review_matrix": [],
                    "model_resolution": {**resolution, "requested_profile": "reviewer"},
                    "gate_verdict": "absent",
                    "unexpected": True,
                },
                "review_packet",
            )
        with self.assertRaises(ContractError):
            validate_output_packet(
                {
                    "schema_version": 1,
                    "status": "completed",
                    "output_type": "review_packet",
                    "findings": [],
                    "model_resolution": {**resolution, "requested_profile": "reviewer"},
                    "gate_verdict": "absent",
                },
                "review_packet",
            )

        malformed_review = {
            "schema_version": 1,
            "status": "completed",
            "output_type": "review_packet",
            "review_subject": "implementation",
            "review_mode": "independent",
            "review_mode_reason": "guarded-multi-component-contract",
            "findings": [{}],
            "review_matrix": [{"acceptance_id": "FA-04", "path": "x", "required_layer": "unit", "evidence": "test", "result": "pass"}],
            "model_resolution": {**resolution, "requested_profile": "reviewer"},
            "gate_verdict": "absent",
        }
        with self.assertRaises(ContractError):
            validate_output_packet(malformed_review, "review_packet")
        malformed_review["findings"] = [{"severity": "high", "path": "x", "evidence": "e", "issue": "i"}]
        malformed_review["review_matrix"][0]["unexpected"] = True
        with self.assertRaises(ContractError):
            validate_output_packet(malformed_review, "review_packet")
        malformed_review["review_matrix"][0].pop("unexpected")
        malformed_review["review_matrix"][0]["result"] = []
        with self.assertRaises(ContractError):
            validate_output_packet(malformed_review, "review_packet")
        malformed_review["review_matrix"][0]["result"] = "pass"
        malformed_review["model_resolution"] = {
            **resolution,
            "requested_profile": "reviewer",
            "capability_status": "resolved",
            "resolution_result": "blocked",
        }
        with self.assertRaises(ContractError):
            validate_output_packet(malformed_review, "review_packet")

    def test_nested_packet_rows_fail_closed(self) -> None:
        implementer_resolution = {
            "requested_profile": "implementer",
            "configured_model": "gpt-5.6-luna",
            "effective_model": "gpt-5.6-luna",
            "fallback_used": False,
            "fallback_reason": None,
            "capability_status": "resolved",
            "resolution_result": "resolved",
            "source": "built-in",
        }
        task_evidence = {
            "schema_version": 1,
            "status": "completed",
            "output_type": "task_evidence_packet",
            "changed_files": [],
            "commands": [{"command": "pytest", "result": "pass", "evidence": "ok"}],
            "evidence": ["ok"],
            "assumptions": [],
            "evidence_gaps": [],
            "model_resolution": implementer_resolution,
            "gate_verdict": "absent",
        }
        validate_output_packet(task_evidence, "task_evidence_packet")
        task_evidence["model_resolution"] = {**implementer_resolution, "requested_profile": "reviewer"}
        with self.assertRaises(ContractError):
            validate_output_packet(task_evidence, "task_evidence_packet")
        task_evidence["model_resolution"] = implementer_resolution
        task_evidence["commands"] = [{}]
        with self.assertRaises(ContractError):
            validate_output_packet(task_evidence, "task_evidence_packet")

        verifier_resolution = {**implementer_resolution, "requested_profile": "verifier"}
        verification = {
            "schema_version": 1,
            "status": "completed",
            "output_type": "verification_packet",
            "acceptance_ids": ["FA-04"],
            "scenario_results": [{"acceptance_id": "FA-04", "result": "pass", "evidence": ["ok"], "gaps": []}],
            "repro_commands": ["pytest"],
            "evidence_revision": "test-revision",
            "model_resolution": verifier_resolution,
            "gate_verdict": "absent",
        }
        validate_output_packet(verification, "verification_packet")
        verification["scenario_results"] = [{}]
        with self.assertRaises(ContractError):
            validate_output_packet(verification, "verification_packet")

    def test_fail_closed_types_and_resolution_consistency(self) -> None:
        with self.assertRaises(ContractError):
            resolve_profile("reviewer", current_model="current", task_override=[])
        with self.assertRaises(ContractError):
            resolve_profile("reviewer", current_model="current", project_path=[])
        with self.assertRaises(ContractError):
            resolve_profile("reviewer", current_model="current", task_override={"model": "foo/../bar"})
        with self.assertRaises(ContractError):
            resolve_profile("reviewer", current_model="current", task_override={"model": "sk-secret"})

        task_packet = {
            "schema_version": 1,
            "profile_id": "implementer",
            "task_packet": {
                "task_id": "T-1",
                "task_kind": "implement",
                "objective": "修复问题",
                "context": {"inherit": "task", "sources": []},
                "tools": {"allow": ["read"], "deny": []},
                "allowed_paths": ["src/**"],
                "model_capabilities": {"required": [], "preferred": [], "independence": "none"},
                "evidence": {"acceptance_ids": ["FA-01"], "required": ["unit"]},
                "output": "task_evidence_packet",
                "stop_conditions": ["停止"],
                "model_override": "packet-model",
            },
        }
        _, packet_resolution, _ = resolve_profile(
            "implementer", current_model="current", available_models={"packet-model"}, task_packet=task_packet
        )
        self.assertEqual("packet-model", packet_resolution.configured_model)
        task_packet["model_resolution"] = []
        with self.assertRaises(ContractError):
            validate_task_packet(task_packet)

        resolution = {
            "requested_profile": "reviewer",
            "configured_model": "configured",
            "effective_model": "other",
            "fallback_used": False,
            "fallback_reason": None,
            "capability_status": "resolved",
            "resolution_result": "resolved",
            "source": "built-in",
        }
        with self.assertRaises(ContractError):
            validate_output_packet(
                {
                    "schema_version": 1,
                    "status": "completed",
                    "output_type": "review_packet",
                    "review_subject": "implementation",
                    "review_mode": "independent",
                    "review_mode_reason": "guarded-multi-component-contract",
                    "findings": [],
                    "review_matrix": [],
                    "model_resolution": resolution,
                    "gate_verdict": "absent",
                },
                "review_packet",
            )

    def test_skills_declare_packet_boundaries(self) -> None:
        completion = read("skills/completion-gate/SKILL.md")
        self.assertIn("verification_packet", completion)
        self.assertIn("review_packet", completion)
        self.assertIn("single `Completion: pass|issues|blocked`", completion)
        self.assertIn("model_resolution", completion)
        self.assertIn("clean context", completion)


if __name__ == "__main__":
    unittest.main()
