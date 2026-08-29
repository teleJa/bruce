from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.browser_provider import (
    BrowserProviderConfigError,
    assert_evidence_provider,
    normalize_visual_scope,
    required_capabilities,
    resolve_browser_provider,
    resolve_browser_provider_file,
)


class BrowserProviderTest(unittest.TestCase):
    def test_missing_provider_defaults_to_ego_lite(self) -> None:
        self.assertEqual("ego-lite", resolve_browser_provider({}))
        self.assertEqual("ego-lite", resolve_browser_provider(None))

    def test_explicit_supported_provider_is_preserved(self) -> None:
        self.assertEqual("chrome", resolve_browser_provider({"verification": {"browser_provider": "chrome"}}))

    def test_invalid_provider_fails_closed(self) -> None:
        with self.assertRaises(BrowserProviderConfigError):
            resolve_browser_provider({"verification": {"browser_provider": "playwright"}})

    def test_scope_aliases_preserve_evidence_strength(self) -> None:
        self.assertEqual("browser-smoke", normalize_visual_scope("chrome-smoke"))
        self.assertEqual("browser-layout", normalize_visual_scope("chrome-layout"))
        self.assertEqual(required_capabilities("chrome-layout"), required_capabilities("browser-layout"))

    def test_invalid_scope_fails_closed(self) -> None:
        with self.assertRaises(BrowserProviderConfigError):
            normalize_visual_scope("unknown")

    def test_evidence_provider_mismatch_fails_closed(self) -> None:
        assert_evidence_provider("ego-lite", "ego-lite")
        with self.assertRaises(BrowserProviderConfigError):
            assert_evidence_provider("ego-lite", "chrome")

    def test_yaml_file_resolution_and_cli(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yaml"
            path.write_text(yaml.safe_dump({"verification": {"browser_provider": "chrome"}}), encoding="utf-8")
            self.assertEqual("chrome", resolve_browser_provider_file(path))
            result = subprocess.run(
                [sys.executable, "scripts/browser_provider.py", "--config", str(path), "--scope", "chrome-layout"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, result.returncode)
            self.assertIn("provider=chrome", result.stdout)
            self.assertIn("visual_scope=browser-layout", result.stdout)
            self.assertIn("before_after", result.stdout)


if __name__ == "__main__":
    unittest.main()
