from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_surface_contract.py"


def contract(*, surface_id: str = "SURFACE-TEST-BOARD", required_id: str | None = None) -> dict[str, object]:
    required = required_id or surface_id
    return {
        "schema_version": 1,
        "contract_id": "test-surface-contract",
        "classification": "existing-product-extension",
        "required_surface_ids": [required],
        "surfaces": [
            {
                "surface_id": surface_id,
                "name": "测试榜单",
                "purpose": "展示榜单条目",
                "hierarchy": [
                    {
                        "region_id": "REGION-TEST-BOARD",
                        "name": "榜单区域",
                        "purpose": "呈现榜单列表",
                        "parent_region_id": None,
                    }
                ],
                "required_states": [
                    {
                        "state_id": "STATE-TEST-DEFAULT",
                        "name": "默认",
                        "observable_result": "榜单可见",
                    }
                ],
                "interactions": [
                    {
                        "interaction_id": "INT-TEST-REFRESH",
                        "trigger": "用户刷新",
                        "transition": "更新榜单内容",
                        "success": "显示最新榜单",
                        "failure": "显示可恢复错误",
                    }
                ],
                "observables": [
                    {
                        "observable_id": "OBS-TEST-RANK",
                        "field": "rank",
                        "meaning": "榜单排名",
                    }
                ],
                "layout_invariants": [
                    {
                        "invariant_id": "LAYOUT-TEST-LIST",
                        "rule": "榜单行垂直排列",
                        "verification": "screenshot and geometry",
                    }
                ],
                "visual_anchors": [
                    {
                        "anchor_id": "ANCHOR-TEST-BOARD",
                        "rule": "保留榜单层级和间距",
                        "evidence": "repository source",
                    }
                ],
                "viewports": [{"name": "desktop", "width": 1440, "height": 900}],
                "evidence": {
                    "methods": ["contract"],
                    "target": "current test surface",
                    "freshness": "current",
                },
                "implementation_mappings": [
                    {
                        "mapping_id": "MAP-TEST-BOARD",
                        "surface_id": surface_id,
                        "locator_type": "source-entry",
                        "locator": "test/surface-entry",
                    }
                ],
            }
        ],
    }


class SurfaceContractTest(unittest.TestCase):
    def run_contract(self, value: dict[str, object]) -> tuple[int, dict[str, object]]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "contract.yaml"
            path.write_text(yaml.safe_dump(value, allow_unicode=True, sort_keys=False), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(VALIDATOR), str(path)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        return result.returncode, json.loads(result.stdout)

    def test_valid_surface_contract_passes(self) -> None:
        returncode, payload = self.run_contract(contract())
        self.assertEqual(0, returncode)
        self.assertEqual([], payload["findings"])

    def test_missing_required_surface_is_reported(self) -> None:
        returncode, payload = self.run_contract(contract(required_id="SURFACE-MISSING"))
        self.assertNotEqual(0, returncode)
        self.assertIn("missing required surface: SURFACE-MISSING", payload["findings"])

    def test_duplicate_and_placeholder_contracts_fail_closed(self) -> None:
        duplicate = contract()
        duplicate["surfaces"].append(duplicate["surfaces"][0])
        returncode, payload = self.run_contract(duplicate)
        self.assertNotEqual(0, returncode)
        self.assertTrue(any("duplicate surface_id" in item for item in payload["findings"]))

        placeholder = contract()
        placeholder["surfaces"][0]["observables"][0]["meaning"] = "TODO fill field"
        returncode, payload = self.run_contract(placeholder)
        self.assertNotEqual(0, returncode)
        self.assertTrue(any("placeholder value" in item for item in payload["findings"]))


if __name__ == "__main__":
    unittest.main()
