"""Static delegation-language regressions, not a model-compliance or language detector."""
from __future__ import annotations

import copy
import unittest

from scripts.functional_agent_profiles import ContractError, validate_task_packet
from tests._support import read


POLICY = "skills/bruce/references/delegation-contract.md"


def packet(objective: str) -> dict:
    return {
        "schema_version": 1,
        "profile_id": "implementer",
        "task_packet": {
            "task_id": "language-check",
            "task_kind": "implement",
            "objective": objective,
            "context": {"inherit": "task", "sources": ["src/example.py"]},
            "tools": {"allow": ["read", "edit", "test"], "deny": ["push"]},
            "allowed_paths": ["src/example.py"],
            "model_capabilities": {"required": [], "preferred": [], "independence": "none"},
            "evidence": {"acceptance_ids": ["AC-1"], "required": ["python3 -m unittest"]},
            "output": "task_evidence_packet",
            "stop_conditions": ["发现范围冲突时停止；保留原始报错 `Not Found`"],
        },
    }


class DelegationLanguageContractTest(unittest.TestCase):
    def test_creation_and_followups_use_request_language(self) -> None:
        text = " ".join(read(POLICY).split())
        for clause in (
            "## Delegation language",
            "all Profiles",
            "spawn_agent",
            "send_input",
            "resumed workers",
            "explicit user language instruction takes precedence",
            "current user's request language",
            "Simplified Chinese",
            "Do not infer the language from an English template",
            "Before dispatch or send_input",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, text)

    def test_natural_language_fields_and_independent_context_are_covered(self) -> None:
        text = " ".join(read(POLICY).split())
        for clause in (
            "objective",
            "constraints",
            "acceptance",
            "stop_conditions",
            "follow-up corrections",
            "reply prose",
            "including clean-context reviewers",
            "No new Packet field",
            "does not require translating historical messages",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, text)

    def test_machine_tokens_quotes_and_code_rules_are_preserved(self) -> None:
        text = " ".join(read(POLICY).split())
        for clause in (
            "Keep schema keys, enum/status values",
            "code identifiers, paths, commands",
            "quoted source text and tool output",
            "Code-comment language rules apply to code comments",
            "not the delegation prose",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, text)

    def test_bruce_and_packet_contract_route_to_message_language_rule(self) -> None:
        for path in (
            "skills/bruce/SKILL.md",
            "skills/bruce/references/functional-agent-contracts.md",
        ):
            with self.subTest(path=path):
                self.assertIn("delegation-contract.md", read(path))

    def test_chinese_prose_uses_unchanged_v1_schema(self) -> None:
        original = packet("请修复限定范围内的问题；使用简体中文说明结果，代码标识符保持英文。")
        before = copy.deepcopy(original)
        validate_task_packet(original, "implementer")
        self.assertEqual(before, original)
        for label, target, key, translated in (
            ("schema key", "task_packet", "objective", "目标"),
            ("enum", "root", "profile_id", "实现者"),
        ):
            invalid = copy.deepcopy(original)
            if target == "task_packet":
                invalid[target][translated] = invalid[target].pop(key)
            else:
                invalid[key] = translated
            with self.subTest(label=label), self.assertRaises(ContractError):
                validate_task_packet(invalid)

    def test_explicit_english_request_remains_schema_compatible(self) -> None:
        # The caller selects language; the v1 validator does not guess it from characters.
        value = packet("Please fix the scoped issue and report in English as explicitly requested.")
        value["task_packet"]["stop_conditions"] = ["Stop on a scope conflict; preserve `Not Found`."]
        validate_task_packet(value, "implementer")


if __name__ == "__main__":
    unittest.main()
