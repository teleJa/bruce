from __future__ import annotations

import unittest

from tests._support import read, read_json


class ContextContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.context = read("CONTEXT.md")
        cls.manifest = read_json(".codex-plugin/plugin.json")

    def test_context_names_current_workflow_boundaries(self) -> None:
        for term in (
            "**Task Contract**",
            "**Execution Profile**",
            "`unresolved`",
            "`standard`",
            "`full`",
            "**Business Risk**",
            "**Prototype Design Capability**",
            "**Design Gate**",
            "**Native Goal Adapter**",
            "**Completion Gate**",
            "**Failure Level**",
            "**Codex Host Authority**",
        ):
            with self.subTest(term=term):
                self.assertIn(term, self.context)

    def test_context_excludes_legacy_parallel_runtime(self) -> None:
        for term in (
            "Completion Verification Gate",
            "Closure Evidence Package",
            "Plan Review Agent",
            "Completion Review Agent",
            "Blocking Review Decision",
            "Component-Parallel Execution",
            "Worktree-Isolated Component Execution",
            "Integration Merge Phase",
            "Component Execution Ledger",
            "Parallel Failure Hold",
            "**Execution Mode**",
        ):
            with self.subTest(term=term):
                self.assertNotIn(term, self.context)

    def test_context_keeps_profile_goal_and_review_independent(self) -> None:
        normalized = " ".join(self.context.split())
        self.assertIn("skills/completion-gate/SKILL.md", self.context)
        self.assertNotIn("skills/verify-completion/SKILL.md", self.context)
        self.assertIn("independent of execution profile", normalized)
        self.assertIn("does not decide design readiness or completion", normalized)
        self.assertIn("Independence is risk- or user-triggered", normalized)
        self.assertIn("never adds another externally combined verdict", normalized)

    def test_manifest_describes_goal_independent_delivery(self) -> None:
        for description in (
            self.manifest["description"],
            self.manifest["interface"]["longDescription"],
        ):
            self.assertIn("Goal-independent execution", description)
            self.assertNotIn("optional native Goal persistence", description)
            self.assertNotIn("execute_record.md", description)
            self.assertNotIn("Goal-backed full delivery", description)


if __name__ == "__main__":
    unittest.main()
