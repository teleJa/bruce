from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.validate_plugin import (
    ValidationError,
    parse_skill_frontmatter,
    validate_agents_metadata,
    validate_hooks,
    validate_legacy_surface,
)
from tests._support import ROOT


class ValidatorRegressionTest(unittest.TestCase):
    def test_bundled_hook_contract_is_valid(self) -> None:
        validate_hooks(ROOT, {"hooks": "./hooks/hooks.json"})

    def test_project_relative_hook_command_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "bruce"
            hooks_dir = root / "hooks"
            hooks_dir.mkdir(parents=True)
            config = json.loads((ROOT / "hooks/hooks.json").read_text(encoding="utf-8"))
            config["hooks"]["PostToolUse"][0]["hooks"][0]["command"] = (
                "python3 .codex/hooks/post_tool_review_reminder.py"
            )
            (hooks_dir / "hooks.json").write_text(
                json.dumps(config),
                encoding="utf-8",
            )
            (hooks_dir / "post_tool_review_reminder.py").write_text(
                "raise SystemExit(0)\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValidationError, "PLUGIN_ROOT"):
                validate_hooks(root, {"hooks": "./hooks/hooks.json"})

    def test_folded_yaml_description_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "SKILL.md"
            path.write_text(
                "---\nname: sample-skill\ndescription: >\n  Use when a folded YAML\n  description is useful.\n---\n\n# Sample\n",
                encoding="utf-8",
            )
            name, description = parse_skill_frontmatter(path)
            self.assertEqual("sample-skill", name)
            self.assertEqual("Use when a folded YAML description is useful.", description)

    def test_negative_legacy_wording_does_not_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "bruce"
            shutil.copytree(ROOT / "skills", root / "skills")
            reference = root / "skills/bruce/references/negative-example.md"
            reference.write_text(
                "# Boundary\n\nDo not use checklist.json, progress.md, or an express lane.\n",
                encoding="utf-8",
            )
            skill = root / "skills/bruce/SKILL.md"
            skill.write_text(
                skill.read_text(encoding="utf-8")
                + "\nRead [negative-example.md](references/negative-example.md).\n",
                encoding="utf-8",
            )
            validate_legacy_surface(root)

    def test_structural_legacy_runtime_still_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "bruce"
            shutil.copytree(ROOT / "skills", root / "skills")
            skill = root / "skills/bruce/SKILL.md"
            skill.write_text(
                skill.read_text(encoding="utf-8") + "\nBruce is a FILE-BASED STATE MACHINE.\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValidationError, "file state machine"):
                validate_legacy_surface(root)

    def test_official_optional_agents_sections_are_supported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skill_dir = Path(directory) / "sample-skill"
            (skill_dir / "agents").mkdir(parents=True)
            (skill_dir / "agents/openai.yaml").write_text(
                "interface:\n"
                '  display_name: "Sample Skill"\n'
                '  short_description: "Handle sample workflows for validation"\n'
                '  default_prompt: "Use $sample-skill to handle this sample."\n'
                "dependencies:\n"
                "  tools: []\n"
                "policy:\n"
                "  allow_implicit_invocation: true\n",
                encoding="utf-8",
            )
            validate_agents_metadata(skill_dir, "sample-skill")


if __name__ == "__main__":
    unittest.main()
