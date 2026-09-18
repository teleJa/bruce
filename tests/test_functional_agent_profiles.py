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
    validate_review_for_basis,
    validate_task_packet,
)
from tests._support import ROOT, read


class FunctionalAgentProfileContractTest(unittest.TestCase):
    def test_profile_registry_and_routing_matrix(self) -> None:
        validator = (ROOT / "scripts/validate_functional_agents.py").read_text(encoding="utf-8")
        self.assertEqual(
            {"inspector", "implementer", "exploration-prototype-generator", "prototype-generator", "verifier", "reviewer"},
            set(PROFILE_IDS),
        )
        profiles = load_builtin_profiles()
        self.assertEqual("gpt-5.6-luna", profiles["inspector"]["default_model"])
        self.assertEqual("max", profiles["inspector"]["reasoning_effort"])
        self.assertEqual("gpt-5.6-luna", profiles["implementer"]["default_model"])
        self.assertEqual("max", profiles["implementer"]["reasoning_effort"])
        self.assertEqual("gemini-3.8-flash", profiles["prototype-generator"]["default_model"])
        self.assertEqual("high", profiles["prototype-generator"]["reasoning_effort"])
        self.assertEqual("blocked", profiles["prototype-generator"]["fallback"])
        self.assertEqual("gpt-5.6-luna", profiles["verifier"]["default_model"])
        self.assertEqual("max", profiles["verifier"]["reasoning_effort"])
        self.assertEqual("deepseek-flash", profiles["reviewer"]["default_model"])
        self.assertEqual("high", profiles["reviewer"]["reasoning_effort"])
        for profile_id in PROFILE_IDS:
            self.assertIn(profile_id, validator)
        for relative in (
            "skills/inspect-parallel/SKILL.md",
            "skills/solution-analysis/SKILL.md",
            "skills/spawn-execute/SKILL.md",
            "skills/explore-prototype/SKILL.md",
            "skills/write-prototype/SKILL.md",
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

    def test_reviewer_resolution_never_falls_back(self) -> None:
        profile, resolution, args = resolve_profile(
            "reviewer", current_model="current-model", available_models={"deepseek-flash"}
        )
        self.assertTrue(profile["context"]["clean"])
        self.assertEqual("none", profile["context"]["inherit"])
        self.assertEqual("blocked", profile["fallback"])
        self.assertEqual("resolved", resolution.resolution_result)
        self.assertEqual("deepseek-flash", args["model"])
        for available in (None, set(), {"current-model"}, {"other-model"}):
            with self.subTest(available=available):
                _, blocked, blocked_args = resolve_profile(
                    "reviewer", current_model="current-model", available_models=available
                )
                self.assertEqual("blocked", blocked.resolution_result)
                self.assertFalse(blocked.fallback_used)
                self.assertIsNone(blocked.effective_model)
                self.assertNotIn("model", blocked_args)
                reason = "host_model_unconfirmed" if available is None else "configured_model_unavailable"
                self.assertEqual(reason, blocked.fallback_reason)

    def test_reviewer_requires_explicit_available_replacement(self) -> None:
        _, blocked, _ = resolve_profile(
            "reviewer", current_model="replacement", available_models={"replacement"}
        )
        self.assertEqual("blocked", blocked.resolution_result)
        for level in ("task", "project", "user"):
            with self.subTest(level=level), tempfile.TemporaryDirectory() as directory:
                kwargs = {}
                if level == "task":
                    kwargs["task_override"] = {"model": "replacement"}
                else:
                    path = Path(directory) / "override.yaml"
                    path.write_text("version: 1\nprofiles:\n  reviewer:\n    default_model: replacement\n")
                    kwargs[f"{level}_path"] = path
                _, resolved, args = resolve_profile(
                    "reviewer", current_model="current-model", available_models={"replacement"}, **kwargs
                )
                self.assertEqual("resolved", resolved.resolution_result)
                self.assertEqual(level, resolved.source)
                self.assertEqual("replacement", args["model"])
                for capability in ({"clean_context_available": False}, {"required_tools": {"deploy"}}):
                    _, blocked, blocked_args = resolve_profile(
                        "reviewer", current_model="current-model", available_models={"replacement"},
                        **kwargs, **capability
                    )
                    self.assertEqual("blocked", blocked.resolution_result)
                    self.assertNotIn("model", blocked_args)

    def test_reviewer_override_cannot_enable_current_fallback(self) -> None:
        with self.assertRaisesRegex(ContractError, "fallback"):
            resolve_profile("reviewer", current_model="current", task_override={"fallback": "current"})
        for level in ("project", "user"):
            with self.subTest(level=level), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "override.yaml"
                path.write_text("version: 1\nprofiles:\n  reviewer:\n    fallback: current\n")
                with self.assertRaisesRegex(ContractError, "fallback"):
                    resolve_profile("reviewer", current_model="current", **{f"{level}_path": path})

    def test_non_reviewer_fallback_policy_is_unchanged(self) -> None:
        for role in ("inspector", "implementer", "verifier"):
            with self.subTest(role=role):
                _, resolution, args = resolve_profile(role, current_model="current", available_models={"current"})
                self.assertEqual("fallback", resolution.resolution_result)
                self.assertTrue(resolution.fallback_used)
                self.assertNotIn("model", args)

    def test_review_packet_rejects_self_review_and_unexecuted_claims(self) -> None:
        _, resolution, _ = resolve_profile("reviewer", current_model="current", available_models={"deepseek-flash"})
        packet = {
            "schema_version": 1, "status": "completed", "output_type": "review_packet",
            "review_basis": {"task_id": "T-1", "dispatch_id": "reviewer-run-1", "basis_revision": "sha256:" + "a" * 64},
                "review_subject": "implementation", "review_mode": "independent",
            "review_mode_reason": "mandatory-independent-review", "findings": [],
            "review_matrix": [{"acceptance_id": "AC-1", "path": "src/example.py",
                               "required_layer": "unit", "evidence": "current-evidence", "result": "pass"}],
            "model_resolution": resolution.as_dict(), "gate_verdict": "absent",
        }
        for subject in ("plan", "implementation", "design"):
            validate_output_packet({**packet, "review_subject": subject}, "review_packet")
        _, blocked, _ = resolve_profile("reviewer", current_model="current", available_models={"current"})
        _, fallback, _ = resolve_profile("inspector", current_model="current", available_models={"current"})
        invalid_variants = (
            {"review_mode": "main-agent"}, {"review_mode_reason": "none"},
            {"review_matrix": []}, {"model_resolution": blocked.as_dict()},
            {"model_resolution": {**fallback.as_dict(), "requested_profile": "reviewer"}},
            {"model_resolution": {**resolution.as_dict(), "source": "current"}},
        )
        for variant in invalid_variants:
            with self.subTest(variant=variant), self.assertRaises(ContractError):
                validate_output_packet({**packet, **variant}, "review_packet")
        validate_output_packet({**packet, "status": "blocked", "review_matrix": [],
                                "model_resolution": blocked.as_dict()}, "review_packet")

    def test_review_consumption_binds_current_basis_and_native_dispatch(self) -> None:
        _, resolution, _ = resolve_profile("reviewer", current_model=None, available_models={"deepseek-flash"})
        context = {"task_id": "T-1", "dispatch_id": "reviewer-run-1", "basis_revision": "sha256:" + "a" * 64,
                   "model_resolution": resolution.as_dict(), "review_subject": "implementation"}
        packet = {"schema_version": 1, "status": "completed", "output_type": "review_packet",
                  "review_subject": "implementation", "review_mode": "independent",
                  "review_mode_reason": "mandatory-independent-review",
                  "review_basis": {key: context[key] for key in ("task_id", "dispatch_id", "basis_revision")},
                  "findings": [], "review_matrix": [{"acceptance_id": "AC-1", "path": "src/example.py",
                  "required_layer": "unit", "evidence": "current-evidence", "result": "pass"}],
                  "model_resolution": resolution.as_dict(), "gate_verdict": "absent"}
        validate_review_for_basis(packet, **context)
        _, replacement, _ = resolve_profile("reviewer", current_model=None, available_models={"user-model"},
                                            task_override={"model": "user-model"})
        for update in ({"task_id": "T-2"}, {"dispatch_id": "another-native-run"},
                       {"basis_revision": "sha256:" + "b" * 64}, {"review_subject": "plan"},
                       {"model_resolution": replacement.as_dict()}):
            with self.subTest(update=update), self.assertRaises(ContractError):
                validate_review_for_basis(packet, **{**context, **update})
        with self.assertRaises(ContractError):
            validate_review_for_basis({**packet, "status": "blocked"}, **context)
        for invalid_basis in ({}, {"task_id": "", "dispatch_id": "run", "basis_revision": "sha256:" + "a" * 64},
                              {**packet["review_basis"], "basis_revision": "HEAD"}):
            with self.subTest(basis=invalid_basis), self.assertRaises(ContractError):
                validate_output_packet({**packet, "review_basis": invalid_basis}, "review_packet")
        # After a repair, the old packet stays invalid; the same independent reviewer can recheck.
        repaired_context = {**context, "basis_revision": "sha256:" + "b" * 64}
        repaired_packet = {**packet, "review_basis": {**packet["review_basis"], "basis_revision": repaired_context["basis_revision"]}}
        validate_review_for_basis(repaired_packet, **repaired_context)

    def test_prototype_generator_is_model_pinned(self) -> None:
        profile, resolution, args = resolve_profile(
            "prototype-generator",
            current_model="current-model",
            available_models={"gemini-3.8-flash"},
        )
        self.assertEqual("prototype-generator", profile["role"])
        self.assertEqual("resolved", resolution.resolution_result)
        self.assertEqual("gemini-3.8-flash", args["model"])
        self.assertEqual("high", args["reasoning_effort"])

        packet = {
            "schema_version": 1,
            "profile_id": "prototype-generator",
            "task_packet": {
                "task_id": "prototype-run",
                "task_kind": "prototype_generate",
                "objective": "在 Open Design 中生成已冻结的原型",
                "context": {"inherit": "task", "sources": ["prototype-brief.md"]},
                "tools": {"allow": ["open-design"], "deny": ["write"]},
                "allowed_paths": [],
                "model_capabilities": {
                    "required": ["prototype-generation"],
                    "preferred": [],
                    "independence": "none",
                },
                "evidence": {
                    "acceptance_ids": ["PG-01"],
                    "required": ["Open Design model availability"],
                },
                "output": "task_evidence_packet",
                "stop_conditions": ["配置模型不可用时停止"],
            },
        }
        validate_task_packet(packet)

        _, blocked, blocked_args = resolve_profile(
            "prototype-generator",
            current_model="current-model",
            available_models={"current-model"},
        )
        self.assertEqual("blocked", blocked.resolution_result)
        self.assertEqual("configured_model_unavailable", blocked.fallback_reason)
        self.assertFalse(blocked.fallback_used)
        self.assertNotIn("model", blocked_args)
        with self.assertRaises(ContractError):
            resolve_profile(
                "prototype-generator",
                current_model="current-model",
                available_models={"gemini-3.8-flash"},
                task_override={"model": "other-model"},
            )

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
            "reviewer", current_model="current", available_models={"deepseek-flash"}, clean_context_available=False
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
                "review_basis": {"task_id": "T-1", "dispatch_id": "reviewer-run-1", "basis_revision": "sha256:" + "a" * 64},
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
                    "review_basis": {"task_id": "T-1", "dispatch_id": "reviewer-run-1", "basis_revision": "sha256:" + "a" * 64},
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
            "review_basis": {"task_id": "T-1", "dispatch_id": "reviewer-run-1", "basis_revision": "sha256:" + "a" * 64},
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
                    "review_basis": {"task_id": "T-1", "dispatch_id": "reviewer-run-1", "basis_revision": "sha256:" + "a" * 64},
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
