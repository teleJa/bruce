from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

import yaml

from scripts.functional_agent_profiles import resolve_profile, validate_task_packet
from tests._support import ROOT, frontmatter, markdown_links, read

CONTRACTS = ROOT / "skills/test-dispatch/scripts/contracts.py"
VALIDATOR = ROOT / "skills/test-dispatch/scripts/validate_contract.py"
AGGREGATOR = ROOT / "skills/test-dispatch/scripts/aggregate_track_results.py"
EVIDENCE_VALIDATOR = ROOT / "skills/test-dispatch/scripts/validate_evidence.py"


def load_contracts():
    spec = importlib.util.spec_from_file_location("test_dispatch_contracts", CONTRACTS)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load test-dispatch contracts")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def scenario() -> dict:
    return {
        "version": 1,
        "scenario_id": "CONTENT-CREATION-001",
        "scenario_version": 1,
        "feature_area": "content-creation",
        "business_flow": "select-topic -> generate-artifact -> reload-recovery",
        "actor": "regular-user",
        "visual_scope": "browser-smoke",
        "execution": {
            "environment_profile": "project-local",
            "api_mode": "real-http",
            "ui_mode": "browser-provider",
        },
        "data": {
            "api_namespace": "api-run-20260903-001",
            "ui_namespace": "ui-run-20260903-001",
            "ownership": "test-run",
            "cleanup": "delete-created-resources",
        },
        "preconditions": ["backend-health", "frontend-ready", "worker-ready"],
        "api": {
            "steps": [
                {
                    "id": "create-job",
                    "action": "request",
                    "request": {"method": "POST", "path": "/api/jobs"},
                },
                {
                    "id": "wait-job",
                    "action": "poll",
                    "request": {"method": "GET", "path": "/api/jobs/{job_id}"},
                    "until": {
                        "terminal_statuses": ["succeeded", "failed", "canceled"],
                        "success_statuses": ["succeeded"],
                        "timeout_seconds": 180,
                        "interval_seconds": 2,
                    },
                },
            ],
            "assertions": ["job-reaches-succeeded"],
            "persistence": {
                "required": True,
                "readback": ["artifact-readable-through-public-api"],
            },
        },
        "ui": {
            "steps": [
                {"id": "open-page", "action": "open", "target": "/writing"},
                {"id": "submit", "action": "click", "target": "submit-button"},
                {"id": "observe-result", "action": "observe", "target": "generated-artifact"},
            ],
            "assertions": ["artifact-visible-after-reload"],
            "forbidden_shortcuts": ["submit-via-api"],
        },
        "failure_cases": ["worker-failure", "cross-user-access"],
        "evidence": {
            "required": ["redacted-request-summary", "state-trace", "visible-state", "screenshot"],
            "directory": "docs/test/evidence/content-creation-001",
        },
        "status": "designed",
    }


def dispatch() -> dict:
    return {
        "version": 1,
        "scenario_id": "CONTENT-CREATION-001",
        "scenario_version": 1,
        "feature_area": "content-creation",
        "business_flow": "select-topic -> generate-artifact -> reload-recovery",
        "actor": "regular-user",
        "tracks": [
            {
                "track": "api",
                "execution_mode": "real-http",
                "data_namespace": "api-run-20260903-001",
                "allowed_paths": ["docs/test/api"],
                "required_evidence": ["request-summary", "state-trace"],
            },
            {
                "track": "ui",
                "execution_mode": "browser-provider",
                "data_namespace": "ui-run-20260903-001",
                "allowed_paths": ["docs/test/evidence/ui"],
                "required_evidence": ["final-url", "visible-state", "screenshot"],
            },
        ],
        "routing": {
            "required_capabilities": ["reproducible-verification"],
            "functional_agent_profile": "verifier",
            "resolver": "bruce-functional-agent-resolver",
            "model_resolution": {
                "requested_profile": "verifier",
                "configured_model": "gpt-5.6-luna",
                "effective_model": "gpt-5.6-luna",
                "fallback_used": False,
                "fallback_reason": None,
                "capability_status": "resolved",
                "resolution_result": "resolved",
                "source": "built-in",
            },
            "functional_packet": {
                "schema_version": 1,
                "profile_id": "verifier",
                "task_packet": {
                    "task_id": "dispatch-evidence-review",
                    "task_kind": "verify",
                    "objective": "Review the selected track evidence without changing the project.",
                    "context": {"inherit": "task", "sources": ["shared-scenario-v1", "track-result-v1"]},
                    "tools": {"allow": ["read", "test"], "deny": []},
                    "allowed_paths": [],
                    "model_capabilities": {
                        "required": ["reproducible-verification"],
                        "preferred": ["test-analysis"],
                        "independence": "preferred",
                    },
                    "evidence": {"acceptance_ids": ["TVO-04"], "required": ["track-result"]},
                    "output": "verification_packet",
                    "stop_conditions": ["browser action requested", "evidence revision mismatch"],
                },
                "model_resolution": {
                    "requested_profile": "verifier",
                    "configured_model": "gpt-5.6-luna",
                    "effective_model": "gpt-5.6-luna",
                    "fallback_used": False,
                    "fallback_reason": None,
                    "capability_status": "resolved",
                    "resolution_result": "resolved",
                    "source": "built-in",
                },
            },
            "subagent_browser_access": "forbidden",
            "visual_scope": "browser-smoke",
        },
    }


def track_result(*, api_status="passed", ui_status="passed", api_version=1, ui_version=1) -> dict:
    return {
        "version": 1,
        "scenario_id": "CONTENT-CREATION-001",
        "scenario_version": 1,
        "required_tracks": ["api", "ui"],
        "profile_id": "verification-profile",
        "profile_revision": 1,
        "profile_content_hash": "sha256:" + "a" * 64,
        "basis_revision": "working-tree-2026-09-03",
        "evidence_revision": "evidence-20260903-001",
        "tracks": {
            "api": {
                "scenario_id": "CONTENT-CREATION-001",
                "scenario_version": api_version,
                "status": api_status,
                "execution_mode": "real-http",
                "data_namespace": "api-run-20260903-001",
                "allowed_paths": ["docs/test/api"],
                "evidence_paths": ["docs/test/evidence/api/summary.yaml"],
                "modified_paths": [],
                "commands": ["node --test docs/test/api/content-creation.api.test.mjs"],
                "browser_actions": [],
                "assertions": ["job-succeeded", "artifact-readback"],
                "blockers": ["missing-api"] if api_status == "blocked" else [],
                "unverified_gates": [],
                "evidence_records": [
                    {"kind": "command", "ref": "docs/test/evidence/api/summary.yaml", "status": "verified"},
                    {"kind": "readback", "ref": "docs/test/evidence/api/summary.yaml", "status": "verified"},
                ],
                "persistence_required": True,
                "authoritative_readback": ["artifact-readback"],
            },
            "ui": {
                "scenario_id": "CONTENT-CREATION-001",
                "scenario_version": ui_version,
                "status": ui_status,
                "execution_mode": "browser-provider",
                "data_namespace": "ui-run-20260903-001",
                "allowed_paths": ["docs/test/evidence/ui"],
                "evidence_paths": ["docs/test/evidence/ui/summary.yaml", "docs/test/evidence/ui/final.png"],
                "modified_paths": [],
                "commands": [],
                "browser_actions": ["open-page", "click-submit", "observe-result"],
                "assertions": ["visible-result", "authoritative-readback"],
                "blockers": ["provider-unavailable"] if ui_status == "blocked" else [],
                "unverified_gates": [],
                "evidence_records": [
                    {"kind": "browser", "ref": "docs/test/evidence/ui/summary.yaml", "status": "verified"},
                    {"kind": "screenshot", "ref": "docs/test/evidence/ui/final.png", "status": "verified"},
                    {"kind": "readback", "ref": "docs/test/evidence/ui/summary.yaml", "status": "verified"},
                ],
                "persistence_required": True,
                "authoritative_readback": ["authoritative-readback"],
                "browser_evidence": {
                    "provider": "ego-lite",
                    "target": "declared-test-target",
                    "session": "declared-test-session",
                    "visual_scope": "browser-smoke",
                    "actions": ["open-page", "click-submit", "observe-result"],
                    "visible_result": "declared-visible-result",
                    "capture_time": "2026-09-03T00:00:00Z",
                    "screenshot_path": "docs/test/evidence/ui/final.png",
                },
            },
        },
    }


class TestDispatchContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contracts = load_contracts()

    def test_reference_documents_define_shared_versioned_contracts(self) -> None:
        scenario_ref = read("skills/test-dispatch/references/scenario-schema.md")
        result_ref = read("skills/test-dispatch/references/track-result-schema.md")
        evidence_ref = read("skills/test-dispatch/references/evidence-status.md")
        for body, phrases in (
            (scenario_ref, ("Scenario v1", "scenario_id", "scenario_version", "API/UI", "forbidden")),
            (result_ref, ("Track result", "required_tracks", "overall_status", "failed", "blocked")),
            (evidence_ref, ("designed", "executed", "passed", "failed", "blocked", "Completion Gate")),
        ):
            normalized = " ".join(body.split())
            for phrase in phrases:
                self.assertIn(phrase, normalized)


    def test_dispatch_skill_owns_routing_without_creating_runtime_or_second_verdict(self) -> None:
        metadata = frontmatter("skills/test-dispatch/SKILL.md")
        self.assertEqual("test-dispatch", metadata["name"])
        body = read("skills/test-dispatch/SKILL.md")
        normalized = " ".join(body.split())
        for phrase in (
            "select `api`, `ui`, or `both`",
            "selects a single `scenario_id + scenario_version`",
            "Functional Agent",
            "model_resolution",
            "configured Bruce Browser Provider",
            "failed > blocked > passed > executed > designed",
            "never emits `Completion`, `verdict`, or `approval`",
            "## Output",
            "## Does not own",
        ):
            self.assertIn(phrase, normalized)
        self.assertNotIn("gpt-5.6-" + "sol", normalized)
        self.assertNotIn("private model router", normalized)
        for link in markdown_links("skills/test-dispatch/SKILL.md"):
            if "://" not in link and not link.startswith("#"):
                self.assertTrue((ROOT / "skills/test-dispatch" / link).is_file())

    def test_dispatch_schema_and_track_result_reject_parallel_authority_fields(self) -> None:
        dispatch_ref = read("skills/test-dispatch/references/dispatch-schema.md")
        result_ref = read("skills/test-dispatch/references/track-result-schema.md")
        combined = " ".join((dispatch_ref + "\n" + result_ref).split()).lower()
        for phrase in (
            "private router",
            "subagent_browser_access",
            "api/ui `allowed_paths`",
            "only adds derived `overall_status`",
            "never emits `completion`",
        ):
            self.assertIn(phrase, combined)

    def test_change_contract_matches_shared_schema_and_marks_examples_non_executable(self) -> None:
        api_contract = read("docs/change/20260902-184244-test-verification-orchestration/api-contracts.md")
        scenario_ref = read("skills/test-dispatch/references/scenario-schema.md")
        result_ref = read("skills/test-dispatch/references/track-result-schema.md")
        self.assertNotRegex(api_contract, r"<[^>]+>")
        for phrase in ("visual_scope", "profile_content_hash", "evidence_records", "browser_evidence"):
            self.assertIn(phrase, api_contract)
        self.assertIn("non-executable placeholders", scenario_ref)
        self.assertIn("non-executable placeholders", result_ref)
        self.assertIn("only adds derived `overall_status`", result_ref)

    def test_valid_scenario_passes(self) -> None:
        self.assertEqual([], self.contracts.validate_scenario(scenario()))

    def test_scenario_requires_stable_identity_and_enabled_track(self) -> None:
        invalid = scenario()
        invalid.pop("scenario_id")
        invalid["scenario_version"] = 0
        invalid["execution"]["api_mode"] = None
        invalid["execution"]["ui_mode"] = None
        invalid["visual_scope"] = "none"
        errors = self.contracts.validate_scenario(invalid)
        self.assertTrue(any("scenario_id" in error for error in errors))
        self.assertTrue(any("scenario_version" in error for error in errors))
        self.assertTrue(any("at least one" in error for error in errors))

    def test_ui_scenario_requires_explicit_visual_scope(self) -> None:
        invalid = scenario()
        invalid.pop("visual_scope")
        errors = self.contracts.validate_scenario(invalid)
        self.assertTrue(any("explicit browser visual_scope" in error for error in errors))

    def test_scenario_rejects_api_ui_action_mixing(self) -> None:
        invalid = scenario()
        invalid["api"]["steps"][0] = {"id": "bad", "action": "click", "target": "submit"}
        invalid["ui"]["steps"][0] = {"id": "bad-ui", "action": "request", "request": {"method": "GET", "path": "/"}}
        errors = self.contracts.validate_scenario(invalid)
        self.assertTrue(any("UI action in the API track" in error for error in errors))
        self.assertTrue(any("API action in the UI track" in error for error in errors))
        self.assertTrue(any("forbidden in the UI track" in error for error in errors))

    def test_scenario_rejects_namespace_collision_and_runtime_or_secret_fields(self) -> None:
        invalid = scenario()
        invalid["data"]["ui_namespace"] = invalid["data"]["api_namespace"]
        invalid["run_id"] = "VR-1"
        invalid["api"]["steps"][0]["token"] = "real-secret"
        errors = self.contracts.validate_scenario(invalid)
        self.assertTrue(any("namespaces must be distinct" in error for error in errors))
        self.assertTrue(any("dynamic runtime field" in error for error in errors))
        self.assertTrue(any("secret-bearing field" in error for error in errors))

    def test_scenario_requires_bounded_poll_and_authoritative_readback(self) -> None:
        invalid = scenario()
        invalid["api"]["steps"][1]["until"]["success_statuses"] = ["unknown"]
        invalid["api"]["steps"][1]["until"]["timeout_seconds"] = 0
        invalid["api"]["persistence"]["readback"] = []
        errors = self.contracts.validate_scenario(invalid)
        self.assertTrue(any("success_statuses must be a subset" in error for error in errors))
        self.assertTrue(any("timeout_seconds must be positive" in error for error in errors))
        self.assertTrue(any("required API persistence" in error for error in errors))

    def test_valid_dispatch_passes_and_duplicate_track_fails(self) -> None:
        self.assertEqual([], self.contracts.validate_dispatch(dispatch()))
        invalid = dispatch()
        invalid["tracks"].append(deepcopy(invalid["tracks"][0]))
        errors = self.contracts.validate_dispatch(invalid)
        self.assertTrue(any("duplicate track" in error for error in errors))

    def test_ui_dispatch_requires_browser_scope_and_forbidden_subagent_access(self) -> None:
        invalid = dispatch()
        invalid["routing"].pop("visual_scope")
        invalid["routing"]["subagent_browser_access"] = "allowed"
        errors = self.contracts.validate_dispatch(invalid)
        self.assertTrue(any("explicit browser visual_scope" in error for error in errors))
        self.assertTrue(any("subagent_browser_access=forbidden" in error for error in errors))

    def test_dispatch_rejects_packet_tool_escape_and_resolution_mismatch(self) -> None:
        invalid = dispatch()
        invalid["routing"]["functional_packet"]["task_packet"]["tools"]["allow"].append("browser")
        errors = self.contracts.validate_dispatch(invalid)
        self.assertTrue(any("outside profile allow" in error for error in errors))

        invalid = dispatch()
        invalid["routing"]["functional_packet"]["model_resolution"]["effective_model"] = "gpt-5.6-luna"
        invalid["routing"]["model_resolution"]["effective_model"] = "gpt-5.6-terra"
        errors = self.contracts.validate_dispatch(invalid)
        self.assertTrue(any("must equal routing.model_resolution" in error for error in errors))

    def test_dispatch_requires_resolver_record_and_functional_packet(self) -> None:
        invalid = dispatch()
        invalid["routing"].pop("resolver")
        invalid["routing"].pop("functional_packet")
        invalid["routing"]["model_resolution"] = "resolved"
        errors = self.contracts.validate_dispatch(invalid)
        self.assertTrue(any("routing.resolver" in error for error in errors))
        self.assertTrue(any("full Bruce resolver record" in error for error in errors))
        self.assertTrue(any("functional_packet" in error for error in errors))

    def test_dispatch_rejects_version_namespace_path_and_router_conflicts(self) -> None:
        invalid = dispatch()
        invalid["scenario_version"] = 2
        invalid["tracks"][1]["data_namespace"] = invalid["tracks"][0]["data_namespace"]
        invalid["tracks"][1]["allowed_paths"] = ["docs/test"]
        invalid["routing"]["model_router"] = "private-router"
        invalid["routing"]["model_resolution"] = {"resolution_result": "resolved", "effective_model": "gpt-5.6-" + "sol"}
        errors = self.contracts.validate_dispatch(invalid)
        self.assertTrue(any("namespaces" in error for error in errors))
        self.assertTrue(any("allowed_paths overlap" in error for error in errors))
        self.assertTrue(any("private model routing" in error for error in errors))
        self.assertTrue(any("disallowed model" in error for error in errors))


    def test_delegated_packet_uses_bruce_resolver_and_keeps_ui_browser_denied(self) -> None:
        profile, resolution, spawn_args = resolve_profile(
            "verifier",
            current_model="gpt-5.6-luna",
            available_models={"gpt-5.6-luna"},
        )
        self.assertEqual("resolved", resolution.resolution_result)
        self.assertEqual("gpt-5.6-luna", spawn_args["model"])
        packet = {
            "schema_version": 1,
            "profile_id": "verifier",
            "task_packet": {
                "task_id": "dispatch-ui-evidence-review",
                "task_kind": "verify",
                "objective": "Review captured UI evidence without operating the browser.",
                "context": {"inherit": "task", "sources": ["shared-scenario-v1", "ui-track-result"]},
                "tools": {"allow": ["read", "test"], "deny": []},
                "allowed_paths": [],
                "model_capabilities": profile["model_capabilities"],
                "evidence": {"acceptance_ids": ["TVO-05"], "required": ["ui-track-result"]},
                "output": "verification_packet",
                "stop_conditions": ["browser action requested", "evidence revision mismatch"],
            },
            "model_resolution": spawn_args["model_resolution"],
        }
        validate_task_packet(packet, profile_id="verifier")
        self.assertNotIn("browser", packet["task_packet"]["tools"]["allow"])
        self.assertEqual("verifier", packet["model_resolution"]["requested_profile"])
        self.assertNotIn("gpt-5.6-" + "sol", repr(packet))


    def test_dispatch_locks_the_scenario_identity_and_declared_modes(self) -> None:
        self.assertEqual([], self.contracts.validate_dispatch_against_scenario(dispatch(), scenario()))
        invalid = dispatch()
        invalid["scenario_version"] = 2
        invalid["tracks"][0]["execution_mode"] = "memory-application"
        invalid["actor"] = "admin"
        invalid["routing"]["visual_scope"] = "browser-layout"
        errors = self.contracts.validate_dispatch_against_scenario(invalid, scenario())
        self.assertTrue(any("scenario_version must match" in error for error in errors))
        self.assertTrue(any("execution_mode must match" in error for error in errors))
        self.assertTrue(any("visual_scope must match" in error for error in errors))
        self.assertTrue(any("actor must match" in error for error in errors))

    def test_valid_track_results_pass(self) -> None:
        self.assertEqual([], self.contracts.validate_track_results(track_result()))

    def test_track_result_rejects_mismatched_version_and_write_overlap(self) -> None:
        invalid = track_result(api_version=1, ui_version=2)
        invalid["tracks"]["ui"]["allowed_paths"] = ["docs/test"]
        errors = self.contracts.validate_track_results(invalid)
        self.assertTrue(any("scenario_version must match" in error for error in errors))
        self.assertTrue(any("allowed_paths overlap" in error for error in errors))

    def test_malformed_track_lists_return_errors_instead_of_crashing(self) -> None:
        invalid = track_result()
        invalid["required_tracks"] = [{"api": True}]
        errors = self.contracts.validate_track_results(invalid)
        self.assertTrue(any("required_tracks may contain only" in error for error in errors))

    def test_passed_track_requires_current_typed_evidence_and_revisions(self) -> None:
        invalid = track_result()
        for key in ("profile_id", "profile_revision", "profile_content_hash", "basis_revision", "evidence_revision"):
            invalid.pop(key)
        invalid["tracks"]["ui"].pop("browser_evidence")
        errors = self.contracts.validate_track_results(invalid)
        self.assertTrue(any("passed Track Result requires profile_id" in error for error in errors))
        self.assertTrue(any("passed Track Result requires a sha256" in error for error in errors))
        self.assertTrue(any("UI passed Track Result must declare browser_evidence" in error for error in errors))

    def test_finite_poll_namespace_and_credential_query_boundaries(self) -> None:
        invalid = scenario()
        invalid["api"]["steps"][1]["until"]["timeout_seconds"] = float("inf")
        invalid["api"]["steps"][0]["request"]["path"] = "/api/jobs?token=rawsecret"
        invalid["data"]["api_namespace"] = "../shared"
        errors = self.contracts.validate_scenario(invalid)
        self.assertTrue(any("timeout_seconds must be positive" in error for error in errors))
        self.assertTrue(any("secret-like value" in error for error in errors))
        self.assertTrue(any("safe lowercase namespace" in error for error in errors))

    def test_track_result_status_guards_are_fail_closed(self) -> None:
        invalid = track_result(ui_status="passed")
        invalid["tracks"]["ui"]["browser_actions"] = []
        invalid["tracks"]["ui"]["unverified_gates"] = ["provider-capability"]
        invalid["tracks"]["api"]["status"] = "blocked"
        invalid["tracks"]["api"]["blockers"] = []
        errors = self.contracts.validate_track_results(invalid)
        self.assertTrue(any("UI passed requires real browser_actions" in error for error in errors))
        self.assertTrue(any("passed must not contain unverified_gates" in error for error in errors))
        self.assertTrue(any("blocked requires" in error for error in errors))

    def test_context_consumer_rejects_stale_profile_or_evidence_revision(self) -> None:
        document = track_result()
        context = {
            "scenario_id": document["scenario_id"],
            "scenario_version": document["scenario_version"],
            "required_tracks": document["required_tracks"],
            "profile_id": document["profile_id"],
            "profile_revision": document["profile_revision"],
            "profile_content_hash": document["profile_content_hash"],
            "basis_revision": document["basis_revision"],
            "evidence_revision": document["evidence_revision"],
            "browser_provider": "ego-lite",
            "visual_scope": "browser-smoke",
        }
        self.assertEqual([], self.contracts.validate_track_results_for_context(document, context))
        stale = dict(context, evidence_revision="evidence-20260903-old")
        errors = self.contracts.validate_track_results_for_context(document, stale)
        self.assertIn("Track Result.evidence_revision does not match current context", errors)

    def test_track_result_validator_rejects_forged_overall_status(self) -> None:
        invalid = track_result(api_status="failed")
        invalid["tracks"]["api"]["blockers"] = []
        # Keep the track result itself structurally valid as a reached failure.
        invalid["tracks"]["api"]["blockers"] = ["assertion-failed"]
        invalid["overall_status"] = "passed"
        errors = self.contracts.validate_track_results(invalid)
        self.assertTrue(any("overall_status must equal derived status failed" in error for error in errors))

    def test_aggregation_priority_and_track_preservation(self) -> None:
        for statuses, expected in (
            (("failed", "blocked"), "failed"),
            (("passed", "blocked"), "blocked"),
            (("passed", "passed"), "passed"),
            (("executed", "passed"), "executed"),
            (("designed", "designed"), "designed"),
        ):
            document = track_result(api_status=statuses[0], ui_status=statuses[1])
            result = self.contracts.aggregate_track_results(document)
            self.assertEqual(expected, result["overall_status"])
            self.assertEqual(document["tracks"], result["tracks"])
            self.assertNotIn("Completion", result)
            self.assertNotIn("verdict", result)

    def test_cli_validator_and_aggregator(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document = root / "track-result.yaml"
            document.write_text(yaml.safe_dump(track_result(), sort_keys=False), encoding="utf-8")
            validated = subprocess.run(
                [sys.executable, str(VALIDATOR), "track-result", str(document)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, validated.returncode, validated.stderr)
            aggregated = subprocess.run(
                [sys.executable, str(AGGREGATOR), str(document)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, aggregated.returncode, aggregated.stderr)
            self.assertEqual("passed", yaml.safe_load(aggregated.stdout)["overall_status"])

    def test_cli_evidence_validator_checks_current_context(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result_file = root / "track-result.yaml"
            context_file = root / "context.yaml"
            document = track_result()
            result_file.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
            context = {
                "scenario_id": document["scenario_id"],
                "scenario_version": document["scenario_version"],
                "required_tracks": document["required_tracks"],
                "profile_id": document["profile_id"],
                "profile_revision": document["profile_revision"],
                "profile_content_hash": document["profile_content_hash"],
                "basis_revision": document["basis_revision"],
                "evidence_revision": document["evidence_revision"],
                "browser_provider": "ego-lite",
                "visual_scope": "browser-smoke",
            }
            context_file.write_text(yaml.safe_dump(context, sort_keys=False), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(EVIDENCE_VALIDATOR), str(result_file), str(context_file)],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            context["evidence_revision"] = "stale-evidence"
            context_file.write_text(yaml.safe_dump(context, sort_keys=False), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(EVIDENCE_VALIDATOR), str(result_file), str(context_file)],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("Evidence validation failed", result.stderr)

    def test_cli_rejects_invalid_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            document = Path(directory) / "scenario.yaml"
            invalid = scenario()
            invalid["ui"]["steps"][0]["action"] = "request"
            document.write_text(yaml.safe_dump(invalid, sort_keys=False), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(VALIDATOR), "scenario", str(document)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("Contract validation failed", result.stderr)


if __name__ == "__main__":
    unittest.main()
