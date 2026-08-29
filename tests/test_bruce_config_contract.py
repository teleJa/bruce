from __future__ import annotations

import unittest

import yaml

from tests._support import read


class BruceConfigContractTest(unittest.TestCase):
    def test_workspace_and_template_configure_bounded_repair_loop(self) -> None:
        workspace = yaml.safe_load(read(".bruce/config.yaml"))
        template = yaml.safe_load(read("skills/bruce/templates/config.yaml"))
        for config in (workspace, template):
            with self.subTest(config=config):
                self.assertEqual(1, config["version"])
                self.assertEqual("docs/change", config["artifacts"]["root"])
                self.assertEqual("ego-lite", config["verification"]["browser_provider"])
                self.assertEqual(5, config["workflow"]["repair_loop"]["max_rounds"])
                self.assertEqual(60, config["workflow"]["review"]["max_wait_seconds"])
                self.assertEqual(2, config["workflow"]["review"]["max_no_progress_polls"])

    def test_browser_provider_contract_is_documented_and_provider_neutral(self) -> None:
        reference = read("skills/bruce/references/browser-provider.md")
        for phrase in (
            "verification.browser_provider",
            "未配置时默认使用 `ego-lite`",
            "browser_provider: ego-lite | chrome",
            "不得静默切换",
            "browser-smoke",
            "browser-layout",
            "browser_evidence",
        ):
            self.assertIn(phrase, reference)

    def test_config_documentation_defines_safe_bounds_and_defaults(self) -> None:
        reference = " ".join(read("skills/bruce/references/artifact-placement.md").split())
        for phrase in (
            "initial review scan is round 0",
            "integer from 1 through 5",
            "max_wait_seconds` is 1 through 60",
            "max_no_progress_polls` is 1 through 2",
            "defaults (`5`, `60`, and `2`)",
            "browser_provider=ego-lite",
            "ego-lite` or `chrome",
            "Invalid values must be reported",
        ):
            self.assertIn(phrase, reference)

    def test_completion_progress_states_are_not_terminal_verdicts(self) -> None:
        workflow = read("skills/bruce/SKILL.md")
        gate = read("skills/completion-gate/SKILL.md")
        checkpoint = read("skills/bruce/templates/checkpoint.yaml")
        self.assertIn("`completion.state` may be `not_started`, `reviewing`, `repairing`, `ready`, or `decided`", workflow)
        self.assertIn("Only `Completion: pass|issues|blocked` is terminal", gate)
        self.assertIn("state: not_started|reviewing|repairing|ready|decided", checkpoint)
        self.assertIn("result: null|pass|issues|blocked", checkpoint)

    def test_checkpoint_tracks_repair_round_and_completion_state(self) -> None:
        checkpoint = read("skills/bruce/templates/checkpoint.yaml")
        self.assertIn("repair_loop:", checkpoint)
        self.assertIn("max_rounds: 5", checkpoint)
        self.assertIn("current_round: 0", checkpoint)
        self.assertIn("status: not_started|scanning|repairing|verifying|exhausted|complete", checkpoint)
        self.assertIn("completion:", checkpoint)


if __name__ == "__main__":
    unittest.main()
