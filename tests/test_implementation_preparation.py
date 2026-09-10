"""Static instruction regressions; these do not simulate agent execution or measure latency."""
from __future__ import annotations

import re
import unittest

import yaml

from scripts.functional_agent_profiles import validate_task_packet
from tests._support import ROOT, read


REFERENCE = "skills/bruce/references/implementation-preparation.md"


class ImplementationPreparationTest(unittest.TestCase):
    def test_all_entrypoints_link_shared_stop_rule(self) -> None:
        for relative in (
            "skills/bruce/SKILL.md",
            "skills/spawn-execute/SKILL.md",
            "skills/inspect-parallel/SKILL.md",
            "skills/bruce/references/delegation-contract.md",
        ):
            with self.subTest(path=relative):
                links = re.findall(r"\]\(([^)]+implementation-preparation\.md|implementation-preparation\.md)\)", read(relative))
                self.assertTrue(links)
                for link in links:
                    self.assertEqual((ROOT / REFERENCE).resolve(), (ROOT / relative).parent.joinpath(link).resolve())

    def test_preparation_has_readiness_budget_and_safety_exit(self) -> None:
        text = read(REFERENCE)
        for clause in (
            "Start that slice immediately",
            "at most two focused evidence rounds",
            "one additional bounded round",
            "cannot\nreset already consumed investigation",
            "never permits unsafe edits",
            "shared contract or dependency",
            "Analysis-only\nand design-only",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, text)

    def test_reuse_is_bounded_and_keeps_current_source_authoritative(self) -> None:
        text = read(REFERENCE)
        for clause in (
            "same-model workers",
            "HEAD alone does not cover dirty or untracked sources",
            "Executor-only gaps",
            "First edit/test target",
            "do not restart the top-level Bruce discovery workflow",
            "Never trust a handoff summary over current source or mandatory rules",
            "Independent reviewers retain clean context",
            "not a timer, runtime, new Gate, or Packet schema",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, text)

    def test_durable_handoff_preserves_consumed_budget(self) -> None:
        text = " ".join(read("skills/write-plan/templates/execution-handoff.md").split())
        for clause in (
            "Focused evidence rounds: at most `2`",
            "Consumed rounds (parent + executors)",
            "Remaining rounds",
            "Extension already used",
            "Gap ID",
            "same shared round budget, not separate per-gap allowances",
            "Calls, reads, and output caps are additional ceilings",
            "no conversion from calls to rounds",
            "Missing consumption data is unknown, not zero",
            "must not reset on delegation",
            "report the affected boundary",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, text)

    def test_dispatch_entrypoints_require_handoff_content(self) -> None:
        # Protect the actual dispatch instructions, not just their reference links.
        for relative in (
            "skills/spawn-execute/SKILL.md",
            "skills/bruce/references/delegation-contract.md",
        ):
            text = " ".join(read(relative).split())
            for clause in (
                "verified facts",
                "source basis",
                "executor-only gaps",
                "first edit/test target",
                "consumed/remaining focused evidence rounds",
                "before dispatch",
                "current instructions",
                "dirty worktree",
                "stale or inaccessible evidence",
                "only affected facts",
            ):
                with self.subTest(path=relative, clause=clause):
                    self.assertIn(clause, text)

    def test_unknown_history_does_not_block_a_ready_safe_slice(self) -> None:
        for relative in (
            REFERENCE,
            "skills/spawn-execute/SKILL.md",
            "skills/bruce/references/delegation-contract.md",
            "skills/write-plan/templates/execution-handoff.md",
        ):
            text = " ".join(read(relative).split()).lower()
            for clause in (
                "if no investigation gaps remain and safety prerequisites are confirmed",
                "keep missing consumption unknown",
                "proceed directly to editing or verification",
                "no additional investigation or extension allowance",
                "budget bookkeeping must not block a ready safe slice",
                "or skip current-source safety checks",
            ):
                with self.subTest(path=relative, clause=clause):
                    self.assertIn(clause, text)

    def test_handoff_example_uses_existing_v1_packet(self) -> None:
        examples = re.findall(r"```yaml\n(.*?)\n```", read(REFERENCE), re.S)
        self.assertEqual(1, len(examples))
        packet = yaml.safe_load(examples[0])
        validate_task_packet(packet, "implementer")
        task = packet["task_packet"]
        for label in ("范围：", "已核实：", "依据：", "待查：", "首步：", "预算："):
            self.assertIn(label, task["objective"])
        self.assertTrue(task["context"]["sources"])
        self.assertTrue(task["evidence"]["required"])
        self.assertTrue(task["stop_conditions"])


if __name__ == "__main__":
    unittest.main()
