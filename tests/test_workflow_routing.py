from __future__ import annotations

import unittest

from tests._support import ROOT, read


class WorkflowRoutingContractTest(unittest.TestCase):
    def test_main_workflow_has_one_default_path(self) -> None:
        skill = read("skills/bruce/SKILL.md")
        self.assertIn(
            "inspect -> task contract -> design when needed -> artifact gate when required -> "
            "implement -> verify -> summary",
            skill,
        )
        self.assertNotIn("express", skill.lower())
        for reference in ("risk-policy.md", "failure-recovery.md"):
            self.assertIn(reference, skill)
        self.assertNotIn("workflow-contract.md", skill)

    def test_execution_profile_is_independent_from_risk(self) -> None:
        contract = read("skills/bruce/SKILL.md")
        self.assertIn("`standard`", contract)
        self.assertIn("`full`", contract)
        self.assertIn("execution profile and risk as independent dimensions", contract)
        self.assertIn("standard + guarded", contract)
        self.assertIn("full + low", contract)

    def test_capabilities_are_defined_once_in_main_workflow(self) -> None:
        skill = read("skills/bruce/SKILL.md")
        self.assertIn("Select only necessary capabilities", skill)
        self.assertFalse((ROOT / "skills/bruce/references/workflow-contract.md").exists())

    def test_public_contract_change_requires_persisted_api_contract(self) -> None:
        skill = read("skills/bruce/SKILL.md")
        normalized = " ".join(skill.split())
        self.assertIn("public or cross-component API, event, or file-contract change", normalized)
        self.assertIn("must invoke `write-architecture`", normalized)
        self.assertIn("before behavior implementation begins", normalized)
        self.assertIn("`api-contracts.md`", normalized)

    def test_risk_policy_avoids_duplicate_guarded_confirmation(self) -> None:
        policy = read("skills/bruce/references/risk-policy.md")
        self.assertIn("already authorizes the exact change", policy)
        self.assertIn("Lower risk when the original trigger is disproved", policy)
        self.assertIn("Never lower risk merely to bypass", policy)

    def test_host_authority_is_not_business_risk(self) -> None:
        boundary = read("skills/bruce/references/plugin-boundary.md")
        self.assertIn("Codex host approval", boundary)
        self.assertIn("Bruce business decision", boundary)
        self.assertIn("does not prove or replace", boundary)

    def test_full_and_explicit_standard_goal_route_through_bundled_gate(self) -> None:
        skill = read("skills/bruce/SKILL.md")
        self.assertIn("Use native subagents directly for incidental delegation", skill)
        self.assertIn("goal-execution-gate", skill)
        self.assertIn(".goal/<goal-id>/execute_record.md", skill)
        self.assertIn("By default, every `full` task", skill)
        self.assertIn("A `standard` task enters Goal", skill)
        self.assertIn("explicit user instruction to skip Goal", skill)
        self.assertNotIn("Until `goal-execution-gate` is bundled", skill)
        self.assertTrue((ROOT / "skills/goal-execution-gate/SKILL.md").is_file())

        boundary = read("skills/bruce/references/plugin-boundary.md")
        self.assertIn("native Goal status", boundary)
        self.assertIn("human audit source only", boundary)
        self.assertIn("never\ncreates a second ledger", boundary)


if __name__ == "__main__":
    unittest.main()
