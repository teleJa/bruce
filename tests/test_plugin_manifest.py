from __future__ import annotations

import re
import unittest

from tests._support import ROOT, read_json


class PluginManifestTest(unittest.TestCase):
    def test_manifest_bundles_skills_and_review_hook(self) -> None:
        manifest = read_json(".codex-plugin/plugin.json")
        self.assertEqual("bruce", manifest["name"])
        self.assertRegex(
            manifest["version"],
            r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$",
        )
        self.assertEqual("./skills/", manifest["skills"])
        self.assertEqual("teleJa", manifest["author"]["name"])
        self.assertEqual("Bruce", manifest["interface"]["displayName"])
        self.assertEqual("#4F46E5", manifest["interface"]["brandColor"])
        self.assertEqual("./hooks/hooks.json", manifest["hooks"])
        for key in ("composerIcon", "logo"):
            path = manifest["interface"][key]
            self.assertTrue(path.startswith("./assets/"))
            self.assertTrue((ROOT / path).is_file())
            self.assertEqual(".png", (ROOT / path).suffix)
        for forbidden in ("mcpServers", "apps", "cli"):
            self.assertNotIn(forbidden, manifest)
        self.assertTrue((ROOT / manifest["skills"]).is_dir())
        self.assertTrue((ROOT / "skills/bruce/SKILL.md").is_file())
        self.assertTrue((ROOT / "skills/design-gate/SKILL.md").is_file())
        self.assertTrue((ROOT / "skills/goal-execution/SKILL.md").is_file())
        self.assertTrue((ROOT / "skills/completion-gate/SKILL.md").is_file())
        self.assertTrue((ROOT / "skills/doctor/SKILL.md").is_file())
        self.assertTrue((ROOT / "skills/explore-prototype/SKILL.md").is_file())
        self.assertTrue((ROOT / "skills/write-prototype/SKILL.md").is_file())
        self.assertFalse((ROOT / "skills/verify-completion/SKILL.md").exists())
        hooks = read_json("hooks/hooks.json")
        self.assertNotIn("doctor", str(hooks).lower())
        command = hooks["hooks"]["PostToolUse"][0]["hooks"][0]["command"]
        self.assertIn("$PLUGIN_ROOT/hooks/post_tool_review_reminder.py", command)
        self.assertNotIn(".codex/hooks", command)

    def test_marketplace_points_at_this_plugin_root(self) -> None:
        marketplace = read_json(".agents/plugins/marketplace.json")
        self.assertEqual("bruce", marketplace["name"])
        self.assertEqual(1, len(marketplace["plugins"]))
        entry = marketplace["plugins"][0]
        self.assertEqual("bruce", entry["name"])
        self.assertEqual({"source": "local", "path": "."}, entry["source"])
        self.assertEqual("AVAILABLE", entry["policy"]["installation"])
        self.assertEqual("ON_INSTALL", entry["policy"]["authentication"])
        self.assertEqual("Developer Tools", entry["category"])

    def test_manifest_paths_are_relative_and_contained(self) -> None:
        manifest = read_json(".codex-plugin/plugin.json")
        for key in ("skills", "hooks"):
            path = manifest[key]
            self.assertTrue(path.startswith("./"))
            self.assertNotIn("..", path.split("/"))
            self.assertFalse(re.match(r"^[A-Za-z]:|^/", path))


if __name__ == "__main__":
    unittest.main()
