from __future__ import annotations

import subprocess
import sys
import unittest

from tests._support import ROOT, read


LEGACY_PATHS = (
    "SKILL.md",
    "config.default.yaml",
    "scripts/checklist_gate.py",
    "skills/bruce/config.default.yaml",
    "skills/bruce/scripts/checklist_gate.py",
    "skills/bruce/templates/checklist.json",
    "skills/spawn-execute/templates/progress.md",
    "skills/verify-completion/SKILL.md",
)


class PackageTest(unittest.TestCase):
    def test_legacy_entry_points_are_removed(self) -> None:
        for relative in LEGACY_PATHS:
            with self.subTest(path=relative):
                self.assertFalse((ROOT / relative).exists())

    def test_readme_separates_static_validation_and_install(self) -> None:
        readme = read("README.md")
        self.assertIn("Static checks do not install the plugin", readme)
        self.assertIn("codex plugin marketplace add", readme)
        self.assertIn("source is `.`", readme)
        self.assertIn("skills/bruce/SKILL.md", readme)

    def test_repository_validator_passes_without_side_effects(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/validate_plugin.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Bruce plugin validation passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
