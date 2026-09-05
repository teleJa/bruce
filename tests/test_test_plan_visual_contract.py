from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

from scripts.browser_provider import (
    BrowserProviderConfigError,
    normalize_visual_scope,
    resolve_browser_provider,
    resolve_browser_provider_file,
)
from tests._support import ROOT, read


class TestPlanVisualContractTest(unittest.TestCase):
    """Guard generation guidance; these checks do not prove model or browser execution."""

    templates = (
        "skills/write-tests/templates/test-plan-minimal.md",
        "skills/write-tests/templates/test-plan.md",
    )

    def test_generation_resolves_provider_instead_of_inheriting_chrome(self) -> None:
        skill = read("skills/write-tests/SKILL.md")
        for token in (
            "artifact-placement.md",
            "scripts/browser_provider.py --config",
            "resolve_browser_provider(None)",
            "verification.browser_provider",
            "未配置默认 `ego-lite`",
            "仅显式配置 `chrome`",
            "不继承 Chrome-only",
            "执行前复核配置",
            "不自行改配置",
            "配置非法/不可读",
            "不得静默切换",
        ):
            with self.subTest(token=token):
                self.assertIn(token, skill)

    def test_missing_config_and_legacy_scope_do_not_select_chrome(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "config.yaml"
            self.assertEqual("ego-lite", resolve_browser_provider(None))
            with self.assertRaises(BrowserProviderConfigError):
                resolve_browser_provider_file(config)
            config.write_text("version: 1\nverification: {}\n", encoding="utf-8")
            self.assertEqual("ego-lite", resolve_browser_provider_file(config))
            self.assertEqual("browser-layout", normalize_visual_scope("chrome-layout"))
            self.assertEqual("ego-lite", resolve_browser_provider_file(config))

    def test_both_templates_record_provider_source_and_failure_boundary(self) -> None:
        for path in self.templates:
            with self.subTest(path=path):
                content = read(path)
                for token in (
                    ".bruce/config.yaml",
                    "verification.browser_provider",
                    "解析后的 Provider",
                    "未配置默认 `ego-lite`",
                    "仅显式配置 `chrome`",
                    "不继承历史 Chrome-only",
                    "blocked/incomplete",
                    "执行前复核配置",
                ):
                    self.assertIn(token, content)
                self.assertNotIn("chrome-smoke", content)
                self.assertNotIn("chrome-layout", content)

    def test_both_templates_require_visual_interpretation_not_just_screenshot(self) -> None:
        for path in self.templates:
            with self.subTest(path=path):
                content = read(path)
                for token in (
                    "visual-checks.md",
                    "显示完整性",
                    "溢出与滚动",
                    "遮挡与层级",
                    "布局稳定性",
                    "视口与状态变化",
                    "geometry",
                    "overflow",
                    "before/after",
                    "截图已保存",
                    "incomplete",
                ):
                    self.assertIn(token, content)

    def test_checklist_defines_observable_assertions_and_proportional_scope(self) -> None:
        checklist = read("skills/write-tests/references/visual-checks.md")
        for token in (
            "`none`", "`browser-smoke`", "`browser-layout`",
            "不要求无关区域扫描", "not_applicable", "显示不全",
            "非预期横向溢出", "布局混乱", "真实点击", "有意省略",
            "Given", "When", "Then", "Evidence", "visible_result",
            "不新增必填机器字段", "未查看/未给出判断", "failed", "incomplete",
        ):
            with self.subTest(token=token):
                self.assertIn(token, checklist)

    def test_generation_execution_and_completion_share_checklist(self) -> None:
        consumers = (
            "skills/write-tests/SKILL.md",
            *self.templates,
            "skills/browser-ui-verification/SKILL.md",
            "skills/completion-gate/SKILL.md",
        )
        target = ROOT / "skills/write-tests/references/visual-checks.md"
        for path in consumers:
            with self.subTest(path=path):
                links = re.findall(r"\]\(([^)]+visual-checks\.md)\)", read(path))
                self.assertEqual(1, len(links))
                self.assertEqual(target.resolve(), (ROOT / Path(path).parent / links[0]).resolve())
                self.assertTrue(target.is_file())

    def test_execution_and_gate_reject_uninspected_artifacts(self) -> None:
        execution = read("skills/browser-ui-verification/SKILL.md")
        self.assertIn("只保存截图而未判读保持 `incomplete`", execution)
        self.assertIn("有实际视觉缺陷记为", execution)
        self.assertIn("visible_result", execution)
        completion = read("skills/completion-gate/SKILL.md")
        self.assertIn("An uninspected screenshot leaves the visual row incomplete", completion)
        self.assertIn("a visible defect is a finding", completion)
        self.assertIn("DOM/structure checks pass", completion)


if __name__ == "__main__":
    unittest.main()
