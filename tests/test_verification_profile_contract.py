from __future__ import annotations

import unittest

import yaml

from tests._support import read


class VerificationProfileContractTest(unittest.TestCase):
    def test_skill_requires_requirements_and_confirmed_environment_profiles(self) -> None:
        body = read("skills/verification-profile/SKILL.md")
        normalized = " ".join(body.split())
        for phrase in (
            "exact `requirements.md` path",
            "confirmed Environment Profiles",
            "content hash",
            "acceptance_ids",
            "account requirement",
            "selected Skill/capability",
            "allowed repair scope",
            "waiting_external",
            "waiting_user",
            "blocked",
            "explicit resume",
            "confirmation.state=pending",
            "Missing requirements input",
        ):
            self.assertIn(phrase, normalized)

    def test_template_is_requirement_scoped_and_pending(self) -> None:
        data = yaml.safe_load(read("skills/verification-profile/templates/verification-profile.yaml"))
        self.assertEqual("requirement-verification", data["profile_kind"])
        self.assertEqual("pending", data["confirmation"]["state"])
        self.assertEqual("completion-gate", data["completion"]["owner"])
        self.assertFalse(data["completion"]["profile_may_return_completion"])
        self.assertIsNone(data["requirements"]["path"])

    def test_schema_keeps_acceptance_in_requirement_profile_and_runtime_outside(self) -> None:
        schema = read("skills/verification-profile/references/profile-schema.md")
        normalized = " ".join(schema.split())
        for phrase in (
            "Requirement Verification Profile",
            "requirements",
            "acceptance mapping",
            "Environment Profile",
            "Dynamic boundary",
            "Verification Run/Checkpoint",
            "completion verdict",
            "stale",
        ):
            self.assertIn(phrase, normalized)
        self.assertIn("Do not put these in the static Profile", schema)

    def test_profile_can_bind_shared_scenarios_and_three_test_skills_without_runtime_results(self) -> None:
        skill = " ".join(read("skills/verification-profile/SKILL.md").split())
        schema = " ".join(read("skills/verification-profile/references/profile-schema.md").split())
        template = yaml.safe_load(read("skills/verification-profile/templates/verification-profile.yaml"))
        for phrase in (
            "shared Scenario `scenario_id + scenario_version`",
            "API/UI track mappings",
            "Track Result",
            "`overall_status`",
            "never a parallel Completion decision",
        ):
            self.assertIn(phrase, skill)
        for phrase in (
            "scenario_refs",
            "test-dispatch",
            "api-test-orchestration",
            "browser-ui-verification",
            "scenario_id + scenario_version",
            "overall_status=passed",
            "not a Completion verdict",
        ):
            self.assertIn(phrase, schema)
        self.assertEqual([], template["scenario_refs"])
        self.assertNotIn("track_results", template)
        self.assertNotIn("overall_status", template)
        self.assertNotIn("Completion", template)



if __name__ == "__main__":
    unittest.main()
