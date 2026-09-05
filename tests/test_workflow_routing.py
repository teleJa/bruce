from __future__ import annotations

import unittest

from tests._support import read


class WorkflowRoutingContractTest(unittest.TestCase):
    def test_main_workflow_has_two_decisions_without_goal_dependency(self) -> None:
        skill = read("skills/bruce/SKILL.md")
        self.assertIn("design-only:", skill)
        self.assertIn("implementation:", skill)
        self.assertIn("Bruce has two decisions; ordinary execution does not require Goal", skill)
        self.assertNotIn("two decisions and one optional execution mode", skill)
        for name in ("`design-gate`", "`completion-gate`"):
            self.assertIn(name, skill)

    def test_bruce_is_user_directed_and_consumes_confirmed_handoffs(self) -> None:
        skill = read("skills/bruce/SKILL.md")
        normalized = " ".join(skill.split())
        self.assertIn("user-directed design and implementation capability", normalized)
        self.assertIn("The user decides when to move from analysis to design", normalized)
        self.assertIn("`solution-analysis` is the normal pre-design entry", normalized)
        self.assertIn("does not invoke it automatically", normalized)
        self.assertIn("user-confirmed analysis", normalized)

    def test_design_only_handoff_stops_before_completion(self) -> None:
        skill = read("skills/bruce/SKILL.md")
        normalized = " ".join(skill.split())
        self.assertIn("A `design-only` scope is the normal Bruce handoff", normalized)
        self.assertIn("stop after the design artifacts and Design Gate result", normalized)
        self.assertIn("must not implement behavior, invoke `completion-gate`", normalized)
        self.assertIn("Do not invoke `completion-gate`", normalized)

    def test_profile_and_risk_remain_independent(self) -> None:
        skill = read("skills/bruce/SKILL.md")
        self.assertIn("`standard`", skill)
        self.assertIn("`full`", skill)
        self.assertIn("Treat execution profile and risk as independent", skill)
        self.assertIn("Size, duration, risk, and uncertainty are insufficient", skill)
        self.assertIn("Never infer `guarded` or `critical` from `full`", skill)
        self.assertIn("use `low` even when", skill)

    def test_environment_operations_remains_explicit_and_does_not_chain(self) -> None:
        workflow = read("skills/bruce/SKILL.md")
        self.assertIn("`environment-operations`", workflow)
        self.assertIn("Executable environment Skill generation remains an explicit user-selected capability", workflow)
        lifecycle = read("skills/bruce/references/profile-lifecycle.md")
        self.assertIn("Executable environment Skill lifecycle", lifecycle)
        self.assertIn("not a third Profile type", lifecycle)

    def test_active_workflow_does_not_expose_legacy_verdict_protocol(self) -> None:
        paths = (
            "skills/bruce/SKILL.md",
            "skills/bruce/references/verification-loop.md",
            "skills/design-gate/SKILL.md",
            "skills/completion-gate/SKILL.md",
            "skills/spawn-execute/SKILL.md",
        )
        forbidden = (
            "artifact-review-gate",
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


    def test_host_authority_remains_owned_by_codex(self) -> None:
        boundary = read("skills/bruce/references/plugin-boundary.md")
        self.assertIn("Codex host approval", boundary)
        self.assertIn("Bruce business decision", boundary)
        self.assertIn("Obey host results directly", boundary)


if __name__ == "__main__":
    unittest.main()
