from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from tests._support import ROOT


HOOK = ROOT / "hooks/post_tool_review_reminder.py"


class PostToolReviewHookTest(unittest.TestCase):
    def run_hook(self, payload: dict[str, object]) -> str:
        result = subprocess.run(
            [sys.executable, str(HOOK)],
            cwd=ROOT,
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=True,
        )
        if not result.stdout.strip():
            return ""
        output = json.loads(result.stdout)
        return output["hookSpecificOutput"]["additionalContext"]

    def patch_payload(
        self,
        path: str,
        *,
        cwd: str = "/tmp/sample-repo",
        success: bool = True,
    ) -> dict[str, object]:
        return {
            "tool_name": "apply_patch",
            "success": success,
            "cwd": cwd,
            "tool_input": {"patch": f"*** Update File: {path}"},
        }

    def test_absolute_planning_path_under_payload_cwd_triggers_d0(self) -> None:
        reminder = self.run_hook(
            self.patch_payload("/tmp/sample-repo/docs/change/example/plan.md")
        )

        self.assertIn("Bruce D0 review reminder", reminder)
        self.assertIn("advisory", reminder)

    def test_relative_trellis_planning_path_remains_compatible(self) -> None:
        reminder = self.run_hook(
            self.patch_payload(".trellis/tasks/example/test-plan.md")
        )

        self.assertIn("Bruce D0 review reminder", reminder)

    def test_code_and_regular_document_edits_stay_quiet(self) -> None:
        for path in ("src/app.py", "docs/notes.md", "README.md"):
            with self.subTest(path=path):
                self.assertEqual("", self.run_hook(self.patch_payload(path)))

    def test_failed_edit_stays_quiet(self) -> None:
        self.assertEqual(
            "",
            self.run_hook(self.patch_payload("docs/change/example/plan.md", success=False)),
        )

    def test_absolute_path_outside_payload_cwd_stays_quiet(self) -> None:
        self.assertEqual(
            "",
            self.run_hook(
                self.patch_payload("/tmp/another-repo/docs/change/example/plan.md")
            ),
        )

    def test_multi_file_patch_triggers_when_any_path_is_planning(self) -> None:
        payload = {
            "tool_name": "apply_patch",
            "success": True,
            "cwd": "/tmp/sample-repo",
            "tool_input": {
                "patch": "\n".join(
                    [
                        "*** Update File: src/app.py",
                        "*** Update File: docs/change/example/architecture.md",
                    ]
                )
            },
        }

        self.assertIn("Bruce D0 review reminder", self.run_hook(payload))


if __name__ == "__main__":
    unittest.main()
