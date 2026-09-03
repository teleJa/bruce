from __future__ import annotations

import importlib.util
import re
import unittest
from copy import deepcopy
from pathlib import Path

import yaml

from tests._support import ROOT


SKILL_DIR = ROOT / "skills" / "browser-ui-verification"
SKILL_PATH = SKILL_DIR / "SKILL.md"
METADATA_PATH = SKILL_DIR / "agents" / "openai.yaml"
REFERENCE_PATHS = (
    SKILL_DIR / "references" / "host-boundary.md",
    SKILL_DIR / "references" / "browser-evidence.md",
)



CONTRACTS_PATH = ROOT / "skills/test-dispatch/scripts/contracts.py"


def load_dispatch_contracts():
    spec = importlib.util.spec_from_file_location("test_dispatch_contracts", CONTRACTS_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load test-dispatch contracts")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valid_ui_dispatch() -> dict:
    return {
        "version": 1,
        "scenario_id": "EXAMPLE-UI-001",
        "scenario_version": 1,
        "feature_area": "example-feature",
        "business_flow": "open -> act -> observe",
        "actor": "regular-user",
        "tracks": [
            {
                "track": "ui",
                "execution_mode": "browser-provider",
                "data_namespace": "ui-run-example-001",
                "allowed_paths": [],
                "required_evidence": ["visible-state", "screenshot"],
            }
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
                    "task_id": "ui-evidence-review",
                    "task_kind": "verify",
                    "objective": "Review UI evidence without browser actions.",
                    "context": {"inherit": "task", "sources": ["scenario-v1", "ui-result"]},
                    "tools": {"allow": ["read", "test"], "deny": []},
                    "allowed_paths": [],
                    "model_capabilities": {
                        "required": ["reproducible-verification"],
                        "preferred": ["test-analysis"],
                        "independence": "preferred",
                    },
                    "evidence": {"acceptance_ids": ["TVO-03"], "required": ["ui-evidence"]},
                    "output": "verification_packet",
                    "stop_conditions": ["browser action requested"],
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


def passed_ui_track_without_actions() -> dict:
    return {
        "version": 1,
        "scenario_id": "EXAMPLE-UI-001",
        "scenario_version": 1,
        "required_tracks": ["ui"],
        "tracks": {
            "ui": {
                "scenario_id": "EXAMPLE-UI-001",
                "scenario_version": 1,
                "track": "ui",
                "status": "passed",
                "execution_mode": "browser-provider",
                "data_namespace": "ui-run-example-001",
                "allowed_paths": [],
                "evidence_paths": ["docs/test/evidence/ui/summary.yaml"],
                "modified_paths": [],
                "commands": [],
                "browser_actions": [],
                "assertions": ["visible-state"],
                "blockers": [],
                "unverified_gates": [],
            }
        },
    }

class BrowserUiVerificationContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = SKILL_PATH.read_text(encoding="utf-8")
        cls.corpus = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(SKILL_DIR.rglob("*"))
            if path.is_file()
        )

    def test_skill_metadata_and_project_agnostic_references(self) -> None:
        self.assertTrue(SKILL_PATH.is_file())
        self.assertTrue(self.skill.startswith("---\n"))
        frontmatter_text = self.skill.split("---\n", 2)[1]
        frontmatter = yaml.safe_load(frontmatter_text)
        self.assertEqual("browser-ui-verification", frontmatter["name"])
        self.assertTrue(frontmatter["description"])
        for path in REFERENCE_PATHS:
            self.assertTrue(path.is_file(), path)
        self.assertIn("references/host-boundary.md", self.skill)
        self.assertIn("references/browser-evidence.md", self.skill)
        self.assertNotIn("Joytime", self.corpus)
        self.assertNotRegex(self.corpus, r"/Users/[^\s`]+")

    def test_openai_metadata_is_skill_only(self) -> None:
        metadata = yaml.safe_load(METADATA_PATH.read_text(encoding="utf-8"))
        self.assertEqual({"interface"}, set(metadata))
        interface = metadata["interface"]
        self.assertEqual("Browser UI Verification", interface["display_name"])
        self.assertTrue(25 <= len(interface["short_description"]) <= 64)
        self.assertIn("$browser-ui-verification", interface["default_prompt"])
        self.assertNotIn("model", interface["default_prompt"].lower())

    def test_provider_scope_and_runtime_preflight_are_fail_closed(self) -> None:
        for token in (
            "verification.browser_provider",
            "ego-lite",
            "chrome",
            "visual_scope",
            "browser-smoke",
            "browser-layout",
            "capability preflight",
            "available|unavailable|unknown",
            "不得静默切换",
            "降低 `visual_scope`",
        ):
            self.assertIn(token, self.corpus)
        self.assertIn("Provider mismatch", self.corpus)
        self.assertIn("blocked`/`incomplete", self.corpus)

    def test_only_main_agent_host_can_act_and_verifier_is_read_only(self) -> None:
        for token in (
            "main-agent-host",
            "主 Agent/宿主",
            "subagent_browser_access: forbidden",
            "evidence-only-review",
            "Verifier 只能",
            "子代理",
            "task space",
            "不强制 takeover",
        ):
            self.assertIn(token, self.corpus)
        self.assertIn("browser tool", self.corpus)
        self.assertIn("拒绝 Packet", self.corpus)

    def test_api_boundary_is_setup_readback_cleanup_only(self) -> None:
        for token in (
            "`setup`",
            "`cleanup`",
            "authoritative readback",
            "页面动作之后",
            "API shortcut",
            "JavaScript state injection",
            "localStorage",
            "测试 fixture",
            "API 不得完成或模拟",
        ):
            self.assertIn(token, self.corpus)
        self.assertIn("page action", self.corpus)
        self.assertIn("invalid evidence", self.corpus)

    def test_evidence_contract_has_required_fields_and_layout_expansion(self) -> None:
        reference = (SKILL_DIR / "references" / "browser-evidence.md").read_text(encoding="utf-8")
        match = re.search(r"```yaml\n(browser_evidence:\n.*?\n)```", reference, re.DOTALL)
        self.assertIsNotNone(match)
        evidence = yaml.safe_load(match.group(1))
        self.assertIn("browser_evidence", evidence)
        payload = evidence["browser_evidence"]
        for field in (
            "provider",
            "target",
            "session",
            "actions",
            "visible_result",
            "capture_time",
            "basis_revision",
            "screenshot_artifact",
        ):
            self.assertIn(field, payload)
        for field in ("geometry", "viewport", "overflow", "before_after"):
            self.assertIn(field, payload)
        for token in (
            "real page action",
            "visible_result",
            "screenshot/artifact",
            "viewport",
            "geometry",
            "overflow",
            "before/after",
            "authoritative_readback",
            "capture_time",
            "basis_revision",
        ):
            self.assertIn(token, self.corpus)

    def test_pass_is_gated_by_real_action_visible_state_evidence_and_readback(self) -> None:
        for token in (
            "status=passed",
            "真实 browser actions",
            "页面结果真实可见",
            "screenshot/等价 artifact",
            "authoritative readback",
            "没有 blockers",
            "unverified_gates",
            "API 200",
            "Toast",
            "单张截图",
        ):
            self.assertIn(token, self.corpus)
        self.assertIn("不能单独证明通过", self.corpus)
        self.assertIn("任何条件缺失都必须 fail closed", self.corpus)

    def test_login_captcha_handoff_control_and_provider_fail_closed(self) -> None:
        for token in (
            "waiting_user",
            "blocked",
            "incomplete",
            "登录",
            "Captcha",
            "人工 handoff",
            "控制权",
            "actor",
            "Provider unavailable",
            "不绕过 Captcha",
            "不强制 takeover",
        ):
            self.assertIn(token, self.corpus)
        self.assertIn("不把未完成当作 passed", self.corpus)

    def test_track_packet_is_evidence_only_and_has_shared_v1_fields(self) -> None:
        for token in (
            "track: ui",
            "execution_mode: browser-provider",
            "scenario_id",
            "scenario_version",
            "data_namespace",
            "evidence_paths",
            "browser_actions",
            "assertions",
            "blockers",
            "unverified_gates",
            "Track Result v1",
            "不输出 Design/Completion/verdict/approval",
        ):
            self.assertIn(token, self.corpus)
        self.assertNotIn("Completion: pass", self.corpus)
        self.assertNotIn("verdict: pass", self.corpus)

    def test_negative_packets_fail_closed_at_shared_contract_boundary(self) -> None:
        contracts = load_dispatch_contracts()
        packet = valid_ui_dispatch()
        self.assertEqual([], contracts.validate_dispatch(packet))

        child_browser_packet = deepcopy(packet)
        child_browser_packet["routing"]["subagent_browser_access"] = "allowed"
        errors = contracts.validate_dispatch(child_browser_packet)
        self.assertTrue(any("subagent_browser_access must be forbidden" in error for error in errors))

        missing_real_action = passed_ui_track_without_actions()
        errors = contracts.validate_track_results(missing_real_action)
        self.assertIn("UI passed requires real browser_actions", errors)

    def test_forbidden_runtime_and_private_model_route_are_not_introduced(self) -> None:
        # Keep the forbidden model name assembled so this test remains a negative assertion,
        # not an invitation to copy that route into the Skill.
        disallowed_model = "gpt-5.6-" + "sol"
        self.assertNotIn(disallowed_model, self.corpus)
        self.assertNotIn("model_router:", self.corpus)
        self.assertNotIn("model_selector:", self.corpus)
        self.assertNotIn("import playwright", self.corpus.lower())
        self.assertNotIn("from playwright", self.corpus.lower())
        self.assertIn("Playwright-only", self.corpus)
        self.assertIn("不创建 browser runtime", self.corpus)
        self.assertIn("不创建 browser runtime", self.skill)


if __name__ == "__main__":
    unittest.main()
