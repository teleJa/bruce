from __future__ import annotations

import importlib.util
import re
import unittest
from pathlib import Path

import yaml

from tests._support import ROOT, frontmatter, markdown_links, read


SKILL_DIR = ROOT / "skills" / "api-test-orchestration"
CONTRACTS = ROOT / "skills" / "test-dispatch" / "scripts" / "contracts.py"


def load_contracts():
    spec = importlib.util.spec_from_file_location("test_dispatch_contracts", CONTRACTS)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {CONTRACTS}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def api_scenario(mode: str) -> dict:
    return {
        "version": 1,
        "scenario_id": "API-ORCHESTRATION-001",
        "scenario_version": 1,
        "feature_area": "api-verification",
        "business_flow": "submit -> observe-job -> readback",
        "actor": "declared-test-actor",
        "execution": {
            "environment_profile": "confirmed-test-environment",
            "api_mode": mode,
            "ui_mode": None,
        },
        "data": {
            "api_namespace": "api-run-20260903-001",
            "ui_namespace": None,
            "ownership": "test-run",
            "cleanup": "declared-project-cleanup-or-read-only",
        },
        "preconditions": ["declared-backend-health", "declared-worker-ready"],
        "api": {
            "steps": [
                {
                    "id": "submit",
                    "action": "request",
                    "request": {
                        "method": "<evidence-backed-method>",
                        "path": "<evidence-backed-submit-route>",
                    },
                },
                {
                    "id": "wait-job",
                    "action": "poll",
                    "request": {
                        "method": "<evidence-backed-poll-method>",
                        "path": "<evidence-backed-status-route>/{job_id}",
                    },
                    "until": {
                        "terminal_statuses": ["succeeded", "failed", "canceled"],
                        "success_statuses": ["succeeded"],
                        "timeout_seconds": 60,
                        "interval_seconds": 1,
                    },
                },
                {
                    "id": "readback",
                    "action": "assert",
                    "assertion": "authoritative-public-readback",
                },
            ],
            "assertions": [
                "terminal-success",
                "authoritative-readback",
                "actor-ownership",
                "idempotency-invariant",
            ],
            "persistence": {
                "required": True,
                "readback": ["public-authoritative-readback"],
            },
        },
        "ui": {
            "steps": [],
            "assertions": [],
            "forbidden_shortcuts": ["submit-via-browser-track"],
        },
        "failure_cases": [
            "documented-validation-error",
            "permission-denied",
            "duplicate-request",
            "worker-failure",
        ],
        "evidence": {
            "required": [
                "redacted-request-summary",
                "variable-lineage",
                "bounded-state-trace",
                "authoritative-readback",
            ],
            "directory": "docs/test/evidence/api-orchestration-001",
        },
        "status": "designed",
    }


def api_track_result(mode: str, *, status: str = "passed") -> dict:
    return {
        "version": 1,
        "scenario_id": "API-ORCHESTRATION-001",
        "scenario_version": 1,
        "required_tracks": ["api"],
        "profile_id": "verification-profile",
        "profile_revision": 1,
        "profile_content_hash": "sha256:" + "b" * 64,
        "basis_revision": "working-tree-2026-09-03",
        "evidence_revision": "evidence-api-20260903-001",
        "tracks": {
            "api": {
                "scenario_id": "API-ORCHESTRATION-001",
                "scenario_version": 1,
                "status": status,
                "execution_mode": mode,
                "data_namespace": "api-run-20260903-001",
                "allowed_paths": ["docs/test/api"],
                "evidence_paths": ["docs/test/evidence/api/summary.yaml"],
                "modified_paths": [],
                "commands": ["declared-project-api-test-command"],
                "browser_actions": [],
                "assertions": ["terminal-success", "authoritative-readback"],
                "blockers": [],
                "unverified_gates": [],
                "evidence_records": [
                    {"kind": "command", "ref": "docs/test/evidence/api/summary.yaml", "status": "verified"},
                    {"kind": "readback", "ref": "docs/test/evidence/api/summary.yaml", "status": "verified"},
                ],
                "persistence_required": True,
                "authoritative_readback": ["public-authoritative-readback"],
            },
        },
    }


class ApiTestOrchestrationContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = read("skills/api-test-orchestration/SKILL.md")
        cls.references = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted((SKILL_DIR / "references").glob("*.md"))
        }
        cls.contracts = load_contracts()

    def test_skill_and_metadata_exist_with_supporting_skill_shape(self) -> None:
        self.assertTrue((SKILL_DIR / "SKILL.md").is_file())
        self.assertTrue((SKILL_DIR / "agents/openai.yaml").is_file())
        metadata = frontmatter("skills/api-test-orchestration/SKILL.md")
        self.assertEqual("api-test-orchestration", metadata["name"])
        self.assertTrue(metadata["description"])
        self.assertIn("## Output", self.skill)
        self.assertIn("## Does not own", self.skill)

        agent_metadata = yaml.safe_load(
            (SKILL_DIR / "agents/openai.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual({"interface"}, set(agent_metadata))
        interface = agent_metadata["interface"]
        self.assertTrue(25 <= len(interface["short_description"]) <= 64)
        self.assertIn("$api-test-orchestration", interface["default_prompt"])

    def test_all_skill_links_resolve_to_repository_resources(self) -> None:
        for link in markdown_links("skills/api-test-orchestration/SKILL.md"):
            if "://" in link or link.startswith("#"):
                continue
            target = (SKILL_DIR / link).resolve()
            with self.subTest(link=link):
                self.assertTrue(target.is_relative_to(ROOT / "skills"))
                self.assertTrue(target.is_file())

    def test_skill_explicitly_covers_modes_boundaries_and_fail_closed_rules(self) -> None:
        normalized = " ".join(self.skill.lower().split())
        required_phrases = (
            "memory-application",
            "real-http",
            "live-acceptance",
            "do not silently",
            "route",
            "service",
            "repository",
            "job",
            "persistence",
            "variable lineage",
            "bounded poll",
            "terminal_statuses",
            "success_statuses",
            "negative",
            "permission",
            "idempotency",
            "authoritative readback",
            "redact",
            "browser_actions",
            "business code",
            "generic http runtime",
            "functional agent profile/resolver",
        )
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, normalized)

        self.assertIn("do not silently downgrade", normalized)
        self.assertIn("browser_actions: []", normalized)
        self.assertIn("modified_paths: []", normalized)
        self.assertNotIn("gpt-5.6-sol", normalized)
        self.assertNotIn("model_router", normalized)

    def test_reference_documents_cover_each_contract_surface(self) -> None:
        self.assertEqual(
            {"api-modes.md", "discovery-boundaries.md", "evidence-contract.md"},
            set(self.references),
        )
        combined = " ".join(self.references.values()).lower()
        for phrase in (
            "memory-application",
            "real-http",
            "live-acceptance",
            "route/controller/router",
            "service/use-case",
            "repository/data access",
            "job/worker",
            "persistence authority",
            "variable lineage",
            "terminal_statuses",
            "success_statuses",
            "negative",
            "permission",
            "idempotency",
            "authoritative readback",
            "redacted evidence",
            "browser_actions",
            "business-code changes",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, combined)

    def test_shared_scenario_accepts_all_three_declared_api_modes(self) -> None:
        for mode in ("memory-application", "real-http", "live-acceptance"):
            with self.subTest(mode=mode):
                self.assertEqual([], self.contracts.validate_scenario(api_scenario(mode)))

    def test_scenario_rejects_browser_actions_unbounded_poll_and_missing_readback(self) -> None:
        invalid = api_scenario("real-http")
        invalid["api"]["steps"][0] = {
            "id": "browser-shortcut",
            "action": "click",
            "target": "submit-button",
        }
        invalid["api"]["steps"][1]["until"]["success_statuses"] = ["unknown"]
        invalid["api"]["steps"][1]["until"]["timeout_seconds"] = 0
        invalid["api"]["persistence"]["readback"] = []
        errors = self.contracts.validate_scenario(invalid)
        self.assertTrue(any("UI action in the API track" in error for error in errors))
        self.assertTrue(any("success_statuses must be a subset" in error for error in errors))
        self.assertTrue(any("timeout_seconds must be positive" in error for error in errors))
        self.assertTrue(any("required API persistence" in error for error in errors))

    def test_track_result_preserves_mode_and_forbids_browser_actions_for_api(self) -> None:
        for mode in ("memory-application", "real-http", "live-acceptance"):
            with self.subTest(mode=mode):
                result = api_track_result(mode)
                self.assertEqual([], self.contracts.validate_track_results(result))
                self.assertEqual(mode, result["tracks"]["api"]["execution_mode"])
                self.assertEqual([], result["tracks"]["api"]["browser_actions"])

        invalid = api_track_result("real-http")
        invalid["tracks"]["api"]["browser_actions"] = ["click-submit"]
        errors = self.contracts.validate_track_results(invalid)
        self.assertIn("API track must not contain browser_actions", errors)

    def test_status_and_secret_guards_remain_fail_closed(self) -> None:
        blocked = api_track_result("real-http", status="blocked")
        blocked["tracks"]["api"]["blockers"] = ["operation-unavailable"]
        self.assertEqual([], self.contracts.validate_track_results(blocked))

        invalid = api_scenario("real-http")
        invalid["api"]["steps"][0]["authorization"] = "raw-secret"
        invalid["run_id"] = "runtime-1"
        errors = self.contracts.validate_scenario(invalid)
        self.assertTrue(any("secret-bearing field" in error for error in errors))
        self.assertTrue(any("dynamic runtime field" in error for error in errors))

    def test_no_project_specific_endpoint_command_or_generic_runtime_is_added(self) -> None:
        all_text = self.skill + "\n" + "\n".join(self.references.values())
        self.assertNotRegex(all_text, re.compile(r"https?://|localhost|127\\.0\\.0\\.1", re.I))
        self.assertNotRegex(
            all_text,
            re.compile(r"(?:^|[\\s`])(curl|wget|pytest|npm|pnpm|make|go test|cargo test)(?:[\\s`]|$)", re.I | re.M),
        )
        self.assertFalse(any(SKILL_DIR.rglob("*.py")))
        self.assertFalse((SKILL_DIR / "scripts").exists())
        self.assertFalse((SKILL_DIR / "templates").exists())

    def test_fixture_keeps_variable_flow_and_evidence_mode_separate(self) -> None:
        scenario = api_scenario("memory-application")
        poll_path = scenario["api"]["steps"][1]["request"]["path"]
        self.assertIn("{job_id}", poll_path)
        self.assertEqual("memory-application", scenario["execution"]["api_mode"])
        self.assertNotEqual("real-http", scenario["execution"]["api_mode"])
        self.assertEqual("public-authoritative-readback", scenario["api"]["persistence"]["readback"][0])


if __name__ == "__main__":
    unittest.main()
