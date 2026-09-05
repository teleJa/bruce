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

    def test_resume_uses_one_policy_and_only_expands_when_state_changes(self) -> None:
        workflow = " ".join(read("skills/bruce/SKILL.md").split())
        policy = " ".join(read("skills/bruce/references/failure-recovery.md").split())
        self.assertIn("single authority for recovery", workflow)
        self.assertIn("lightweight consistency check", policy)
        self.assertIn("alone does not require a `Resume checkpoint`", policy)
        for trigger in ("context is missing", "materially changed", "evidence became stale", "unknown result"):
            with self.subTest(trigger=trigger):
                self.assertIn(trigger, policy)
        self.assertIn("Ordinary recovery does not require native Goal state", policy)
        self.assertIn("retry or repair counts or authorizes unmapped inspection", policy)

    def test_legacy_artifacts_are_not_resume_truth(self) -> None:
        policy = read("skills/bruce/references/failure-recovery.md")
        self.assertIn("Do not infer completion from old workflow artifacts", policy)


if __name__ == "__main__":
    unittest.main()
