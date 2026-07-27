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
            "**Design Gate**",
            "**Goal Execution Mode**",
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

    def test_manifest_does_not_route_full_profile_to_goal(self) -> None:
        description = self.manifest["description"]
        long_description = self.manifest["interface"]["longDescription"]
        self.assertIn("optional native Goal persistence", description)
        self.assertIn("optional native Goal persistence", long_description)
        self.assertNotIn("Goal-backed full delivery", description)
        self.assertNotIn("routes full delivery", long_description)


if __name__ == "__main__":
    unittest.main()
