from __future__ import annotations

import unittest

from tests._support import read


class ExecutionContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = read("skills/spawn-execute/SKILL.md")

    def test_delegation_uses_native_subagents_or_sequential_fallback(self) -> None:
        self.assertIn("bounded Codex-native delegation", self.skill)
        self.assertRegex(self.skill, r"Otherwise execute the same\s+task sequentially")
        self.assertIn("main agent responsible", self.skill)

    def test_execution_is_goal_backed_and_auditable(self) -> None:
        self.assertIn("goal-execution-gate", self.skill)
        self.assertIn("active native Goal", self.skill)
        self.assertIn(".goal/<goal-id>/execute_record.md", self.skill)
        self.assertIn("audit evidence packet", self.skill)
        self.assertIn("do not use for incidental delegation", self.skill)

    def test_bundled_goal_gate_owns_native_goal_lifecycle(self) -> None:
        gate = read("skills/goal-execution-gate/SKILL.md")
        self.assertIn("Bruce routes a `full` task", gate)
        self.assertIn("Native Goal", gate)
        self.assertIn("execute_record.md", gate)
        self.assertNotIn("progress.json", gate)

    def test_delegation_brief_has_scope_and_acceptance(self) -> None:
        for field in ("objective", "allowed/excluded files", "dependencies", "acceptance", "verification"):
            self.assertIn(field, self.skill.lower())

    def test_audit_packet_has_execution_evidence(self) -> None:
        for field in (
            "task_id",
            "changed files",
            "verification",
            "L0-L4 classification",
            "dependent impact",
            "remaining work",
        ):
            self.assertIn(field.lower(), self.skill.lower())
        for field in (
            "acceptance/scenario ids",
            "Given/When/Then",
            "required verification layer",
            "C0 verdict",
            "repair-round number",
            "original-scenario rerun",
            "related regression",
        ):
            self.assertIn(field.lower(), self.skill.lower())
        self.assertIn("D0/D1 document-review mode and verdict", self.skill)

    def test_subagent_failure_is_classified_not_globalized(self) -> None:
        self.assertIn("failure-recovery.md", self.skill)
        self.assertIn("affected dependency", self.skill)
        self.assertIn("global stop-on-first-failure", self.skill)

    def test_no_custom_runtime_contract(self) -> None:
        for forbidden in (
            "progress.md",
            "progress.json",
            "sonnet",
            "checklist",
            "worker pid",
            "worktree_isolation",
        ):
            self.assertNotIn(forbidden, self.skill.lower())
        self.assertIn("as runtime state", self.skill)
        self.assertIn("Do not own native Goal", self.skill)


if __name__ == "__main__":
    unittest.main()
