from __future__ import annotations

import unittest

import yaml

from tests._support import ROOT


class SkillAgentsMetadataTest(unittest.TestCase):
    def test_every_skill_has_valid_ui_metadata(self) -> None:
        skill_dirs = sorted(path.parent for path in (ROOT / "skills").glob("*/SKILL.md"))
        self.assertEqual(10, len(skill_dirs))
        for skill_dir in skill_dirs:
            path = skill_dir / "agents/openai.yaml"
            with self.subTest(skill=skill_dir.name):
                self.assertTrue(path.is_file())
                metadata = yaml.safe_load(path.read_text(encoding="utf-8"))
                self.assertEqual({"interface"}, set(metadata))
                interface = metadata["interface"]
                self.assertTrue(interface["display_name"])
                self.assertTrue(25 <= len(interface["short_description"]) <= 64)
                self.assertIn(f"${skill_dir.name}", interface["default_prompt"])
                self.assertNotIn("icon_small", interface)
                self.assertNotIn("icon_large", interface)


if __name__ == "__main__":
    unittest.main()
