from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_prototype_artifact import validate_artifact


class PrototypeArtifactTest(unittest.TestCase):
    def _case(self, artifact: str, contract: dict) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text(artifact, encoding="utf-8")
            contract_path = root / "visual-assertions.json"
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            return validate_artifact(contract_path, root / "index.html", "succeeded")

    def test_clear_artifact_passes_exact_tokens_and_brand(self) -> None:
        result = self._case(
            '<div class="sidebar">乐享时光</div><style>.sidebar { background: #df6f57; width: 184px; }</style>',
            {
                "schema_version": 1,
                "exact_colors": [{"selector": ".sidebar", "value": "#df6f57"}],
                "exact_dimensions": [{"selector": ".sidebar", "property": "width", "value": "184px"}],
                "required_brand_text": [{"selector": ".sidebar", "value": "乐享时光"}],
                "forbidden_tokens": ["#d32029", "248px", "Joytime Studio", "JT"],
            },
        )
        self.assertEqual("automated-clear", result["visual_check"])
        self.assertEqual("clear", result["exact_token_assertions"])
        self.assertEqual("succeeded", result["provider_status"])

    def test_provider_success_does_not_override_drift(self) -> None:
        result = self._case(
            '<div class="sidebar">JT</div><style>.sidebar { background: #d32029; width: 248px; }</style>',
            {
                "schema_version": 1,
                "exact_colors": [{"selector": ".sidebar", "value": "#df6f57"}],
                "exact_dimensions": [{"selector": ".sidebar", "property": "width", "value": "184px"}],
                "required_brand_text": [{"selector": ".sidebar", "value": "乐享时光"}],
                "forbidden_tokens": ["#d32029", "248px", "JT"],
            },
        )
        self.assertEqual("succeeded", result["provider_status"])
        self.assertEqual("blocked", result["visual_check"])
        self.assertEqual("blocked", result["exact_token_assertions"])
        self.assertGreaterEqual(len(result["findings"]), 4)

    def test_manual_only_is_not_part_of_checker_clearance(self) -> None:
        result = self._case(
            '<div class="sidebar">乐享时光</div><style>.sidebar { background: #df6f57; width: 184px; }</style>',
            {
                "schema_version": 1,
                "exact_colors": [{"selector": ".sidebar", "value": "#df6f57"}],
                "exact_dimensions": [{"selector": ".sidebar", "property": "width", "value": "184px"}],
                "required_brand_text": [{"selector": ".sidebar", "value": "乐享时光"}],
                "forbidden_tokens": [],
            },
        )
        self.assertEqual("automated-clear", result["visual_check"])


if __name__ == "__main__":
    unittest.main()
