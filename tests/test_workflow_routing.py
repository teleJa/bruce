from __future__ import annotations

import unittest

from tests._support import ROOT, read


class WorkflowRoutingContractTest(unittest.TestCase):
    def test_main_workflow_has_two_decisions_and_one_optional_mode(self) -> None:
        skill = read("skills/bruce/SKILL.md")
        self.assertIn("Design Gate when needed", skill)
        self.assertIn("Completion Gate", skill)
        self.assertIn("optional Goal execution mode", skill)
        self.assertIn("two decisions and one optional execution mode", skill)
        for name in ("`design-gate`", "`completion-gate`", "`goal-execution`"):
            self.assertIn(name, skill)

    def test_profile_and_risk_remain_independent(self) -> None:
        skill = read("skills/bruce/SKILL.md")
        self.assertIn("`standard`", skill)
        self.assertIn("`full`", skill)
        self.assertIn("Treat execution profile and risk as independent", skill)
        self.assertIn("Size, duration, risk, and uncertainty are insufficient", skill)
        self.assertIn("Never infer `guarded` or `critical` from `full`", skill)
        self.assertIn("use `low` even when", skill)

    def test_active_workflow_does_not_expose_legacy_verdict_protocol(self) -> None:
        paths = (
            "skills/bruce/SKILL.md",
            "skills/bruce/references/verification-loop.md",
            "skills/design-gate/SKILL.md",
            "skills/completion-gate/SKILL.md",
            "skills/goal-execution/SKILL.md",
            "skills/spawn-execute/SKILL.md",
        )
        forbidden = (
            "artifact-review-gate",
            "goal-execution-gate",
            "doc-review-gate",
            "Author check: C0",
            "Document author check: D0",
            "D1 readiness",
            "Verification: V0",
            "Independent review: R1",
        )
        for path in paths:
            body = read(path)
            with self.subTest(path=path):
                for marker in forbidden:
                    self.assertNotIn(marker, body)

    def test_goal_route_is_explicit_and_profile_independent(self) -> None:
        workflow = read("skills/bruce/SKILL.md")
        goal = read("skills/goal-execution/SKILL.md")
        normalized = " ".join(goal.split())
        self.assertIn("Enter only for explicit Goal intent", normalized)
        self.assertIn("resolved task contract requires continuous/cross-turn", normalized)
        self.assertIn("Profile, complexity, duration, risk, or subagent use alone does not", normalized)
        self.assertIn(".goal/<goal-id>/execute_record.md", goal)
        self.assertTrue((ROOT / "skills/goal-execution/SKILL.md").is_file())
        self.assertNotIn("a `full` profile by default", workflow)

    def test_host_authority_remains_owned_by_codex(self) -> None:
        boundary = read("skills/bruce/references/plugin-boundary.md")
        self.assertIn("Codex host approval", boundary)
        self.assertIn("Bruce business decision", boundary)
        self.assertIn("Obey host results directly", boundary)


if __name__ == "__main__":
    unittest.main()
