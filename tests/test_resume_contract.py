from __future__ import annotations

import unittest

from tests._support import read


class ResumeContractTest(unittest.TestCase):
    def test_resume_uses_codex_and_workspace_facts(self) -> None:
        policy = read("skills/bruce/references/failure-recovery.md")
        for source in ("current conversation", "native plan", "tool results"):
            self.assertIn(source, policy)
        self.assertRegex(policy, r"actual\s+workspace")

    def test_handoff_is_optional_snapshot(self) -> None:
        skill = read("skills/bruce/SKILL.md")
        template = read("skills/bruce/templates/handoff.md")
        self.assertIn("only when the user explicitly requests", skill)
        self.assertIn("Optional human-readable snapshot", template)
        self.assertIn("Reinspect", template)

    def test_unfinished_full_cross_turn_resume_requires_goal_and_resume_checkpoint(self) -> None:
        workflow = read("skills/bruce/SKILL.md")
        failure = read("skills/bruce/references/failure-recovery.md")
        goal = read("skills/goal-execution/SKILL.md")
        for source in (workflow, failure, goal):
            normalized = " ".join(source.split())
            self.assertIn("unfinished `full` task", normalized)
            self.assertIn("user-turn boundary", normalized)
            self.assertIn("Resume checkpoint", normalized)
        self.assertIn("enter or resume `goal-execution`", workflow)
        self.assertIn("does not reset interval counters", goal)
        self.assertIn("does not authorize\nunmapped inspection", goal)

    def test_legacy_artifacts_are_not_resume_truth(self) -> None:
        policy = read("skills/bruce/references/failure-recovery.md")
        self.assertIn("Do not infer completion from old workflow artifacts", policy)


if __name__ == "__main__":
    unittest.main()
