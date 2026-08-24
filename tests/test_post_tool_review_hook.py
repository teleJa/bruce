from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests._support import ROOT


HOOK = ROOT / "hooks/post_tool_review_reminder.py"


class PostToolReviewHookTest(unittest.TestCase):
    def run_hook(self, payload: dict[str, object]) -> dict[str, object] | None:
        result = subprocess.run(
            [sys.executable, str(HOOK)],
            cwd=ROOT,
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=True,
        )
        if not result.stdout.strip():
            return None
        return json.loads(result.stdout)

    def additional_context(self, payload: dict[str, object]) -> str:
        output = self.run_hook(payload)
        if output is None:
            return ""
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

    def test_absolute_planning_path_under_payload_cwd_triggers_design_gate(self) -> None:
        reminder = self.additional_context(
            self.patch_payload("/tmp/sample-repo/docs/change/example/plan.md")
        )

        self.assertIn("Bruce Design Gate reminder", reminder)
        self.assertIn("$design-gate", reminder)
        self.assertIn("Design: pass", reminder)
        self.assertIn("advisory", reminder)

    def test_relative_trellis_planning_path_remains_compatible(self) -> None:
        reminder = self.additional_context(
            self.patch_payload(".trellis/tasks/example/test-plan.md")
        )

        self.assertIn("Bruce Design Gate reminder", reminder)

    def test_code_and_regular_document_edits_stay_quiet(self) -> None:
        for path in ("src/app.py", "docs/notes.md", "README.md"):
            with self.subTest(path=path):
                self.assertEqual("", self.additional_context(self.patch_payload(path)))

    def test_failed_edit_stays_quiet(self) -> None:
        self.assertEqual(
            "",
            self.additional_context(
                self.patch_payload("docs/change/example/plan.md", success=False)
            ),
        )

    def test_absolute_path_outside_payload_cwd_stays_quiet(self) -> None:
        self.assertEqual(
            "",
            self.additional_context(
                self.patch_payload(
                    "/tmp/another-repo/docs/change/example/plan.md"
                )
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

        self.assertIn("Bruce Design Gate reminder", self.additional_context(payload))

    def test_read_only_bash_command_stays_quiet(self) -> None:
        payload = {
            "tool_name": "Bash",
            "success": True,
            "cwd": "/tmp/sample-repo",
            "tool_input": {"command": "cat docs/change/example/plan.md"},
        }
        self.assertIsNone(self.run_hook(payload))

    def test_bash_write_to_planning_document_triggers_reminder(self) -> None:
        payload = {
            "tool_name": "Bash",
            "success": True,
            "cwd": "/tmp/sample-repo",
            "tool_input": {
                "command": "cat > docs/change/example/plan.md <<'EOF'\n# Plan\nEOF"
            },
        }
        self.assertIn("Bruce Design Gate reminder", self.additional_context(payload))

    def test_task_contract_edit_triggers_design_gate_reminder(self) -> None:
        reminder = self.additional_context(
            self.patch_payload("docs/change/example/tasks/T-001-bounded-change.md")
        )

        self.assertIn("Bruce Design Gate reminder", reminder)
        self.assertIn("task-contract package completeness", reminder)

    def test_exec_command_workdir_resolves_design_review_location(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "repo"
            change = repo / "docs/change/example"
            change.mkdir(parents=True)
            (change / "design-review.md").write_text(
                "# Design Review\n\n## Verdict\n\nDesign: pass\n",
                encoding="utf-8",
            )
            payload = {
                "tool_name": "exec_command",
                "success": True,
                "cwd": str(root),
                "tool_input": {
                    "cmd": "cat > docs/change/example/design-review.md <<'EOF'\n...\nEOF",
                    "workdir": "repo",
                },
            }
            output = self.run_hook(payload)

        self.assertIsNotNone(output)
        self.assertEqual("block", output["decision"])
        self.assertIn("missing candidates", output["reason"])

    def test_failed_shell_result_with_nonzero_exit_stays_quiet(self) -> None:
        payload = {
            "tool_name": "Bash",
            "cwd": "/tmp/sample-repo",
            "tool_input": {
                "command": "cat > docs/change/example/plan.md <<'EOF'\n# Plan\nEOF"
            },
            "tool_response": {"exit_code": 1},
        }
        self.assertIsNone(self.run_hook(payload))

    def test_non_planning_sibling_edit_does_not_invalidate_review(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            change = root / "docs/change/example"
            change.mkdir(parents=True)
            (change / "design-review.md").write_text(
                "# Design Review\n\n## Verdict\n\nDesign: pass\n",
                encoding="utf-8",
            )
            payload = {
                "tool_name": "apply_patch",
                "success": True,
                "cwd": str(root),
                "tool_input": {
                    "patch": "*** Update File: docs/change/example/notes.md"
                },
            }
            output = self.run_hook(payload)

        self.assertIsNone(output)

    def test_bare_design_review_filename_in_workdir_is_validated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            change = root / "docs/change/example"
            change.mkdir(parents=True)
            (change / "design-review.md").write_text(
                "# Design Review\n\n## Verdict\n\nDesign: pass\n",
                encoding="utf-8",
            )
            payload = {
                "tool_name": "exec_command",
                "success": True,
                "cwd": str(root),
                "tool_input": {
                    "cmd": "cat > design-review.md <<'EOF'\n...\nEOF",
                    "workdir": "docs/change/example",
                },
            }
            output = self.run_hook(payload)

        self.assertIsNotNone(output)
        self.assertEqual("block", output["decision"])
        self.assertIn("missing candidates", output["reason"])

    def test_string_nonzero_shell_result_stays_quiet(self) -> None:
        payload = {
            "tool_name": "Bash",
            "cwd": "/tmp/sample-repo",
            "tool_input": {
                "command": "cat > docs/change/example/plan.md <<'EOF'\n# Plan\nEOF"
            },
            "tool_response": "Process exited with code 2",
        }
        self.assertIsNone(self.run_hook(payload))

    def test_invalid_design_review_written_by_bash_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            change = root / "docs/change/example"
            change.mkdir(parents=True)
            (change / "design-review.md").write_text(
                "# Design Review\n\n## Verdict\n\nDesign: pass\n",
                encoding="utf-8",
            )
            payload = {
                "tool_name": "Bash",
                "success": True,
                "cwd": str(root),
                "tool_input": {
                    "command": "cat > docs/change/example/design-review.md <<'EOF'\n...\nEOF"
                },
            }
            output = self.run_hook(payload)

        self.assertIsNotNone(output)
        self.assertEqual("block", output["decision"])
        self.assertIn("missing candidates", output["reason"])
        self.assertIn("before reporting Design: pass", output["reason"])

    def test_invalid_design_review_outside_docs_is_also_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            change = root / "custom-change/example"
            change.mkdir(parents=True)
            (change / "design-review.md").write_text(
                "# Design Review\n\n## Verdict\n\nDesign: pass\n",
                encoding="utf-8",
            )
            payload = {
                "tool_name": "apply_patch",
                "success": True,
                "cwd": str(root),
                "tool_input": {
                    "patch": "*** Update File: custom-change/example/design-review.md"
                },
            }
            output = self.run_hook(payload)

        self.assertIsNotNone(output)
        self.assertEqual("block", output["decision"])
        self.assertIn("missing candidates", output["reason"])

    def test_task_contract_change_invalidates_parent_review(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            change = root / "docs/change/example"
            (change / "tasks").mkdir(parents=True)
            (change / "design-review.md").write_text(
                "# Design Review\n\n## Verdict\n\nDesign: pass\n",
                encoding="utf-8",
            )
            payload = {
                "tool_name": "apply_patch",
                "success": True,
                "cwd": str(root),
                "tool_input": {
                    "patch": "*** Update File: docs/change/example/tasks/T-001.md"
                },
            }
            output = self.run_hook(payload)

        self.assertIsNotNone(output)
        self.assertEqual("block", output["decision"])
        self.assertIn("same-directory design artifact changed", output["reason"])
        self.assertIn("Rerun $design-gate", output["reason"])

    def test_task_contract_change_from_change_dir_workdir_invalidates_review(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            change = root / "docs/change/example"
            (change / "tasks").mkdir(parents=True)
            (change / "design-review.md").write_text(
                "# Design Review\n\n## Verdict\n\nDesign: pass\n",
                encoding="utf-8",
            )
            payload = {
                "tool_name": "exec_command",
                "success": True,
                "cwd": str(root),
                "tool_input": {
                    "cmd": "touch tasks/T-001.md",
                    "workdir": "docs/change/example",
                },
            }
            output = self.run_hook(payload)

        self.assertIsNotNone(output)
        self.assertEqual("block", output["decision"])
        self.assertIn("same-directory design artifact changed", output["reason"])

    def test_api_contract_change_invalidates_existing_review(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            change = root / "docs/change/example"
            change.mkdir(parents=True)
            (change / "design-review.md").write_text(
                "# Design Review\n\n## Verdict\n\nDesign: pass\n",
                encoding="utf-8",
            )
            payload = {
                "tool_name": "apply_patch",
                "success": True,
                "cwd": str(root),
                "tool_input": {
                    "patch": "*** Update File: docs/change/example/api-contracts.md"
                },
            }
            output = self.run_hook(payload)

        self.assertIsNotNone(output)
        self.assertEqual("block", output["decision"])
        self.assertIn("same-directory design artifact changed", output["reason"])

    def test_custom_change_directory_sibling_invalidates_review(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            change = root / "custom-change/example"
            change.mkdir(parents=True)
            (change / "design-review.md").write_text(
                "# Design Review\n\n## Verdict\n\nDesign: pass\n",
                encoding="utf-8",
            )
            payload = {
                "tool_name": "apply_patch",
                "success": True,
                "cwd": str(root),
                "tool_input": {
                    "patch": "*** Update File: custom-change/example/table-design.md"
                },
            }
            output = self.run_hook(payload)

        self.assertIsNotNone(output)
        self.assertEqual("block", output["decision"])
        self.assertIn("same-directory design artifact changed", output["reason"])

    def test_writing_sibling_design_artifact_revalidates_existing_review(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            change = root / "docs/change/example"
            change.mkdir(parents=True)
            (change / "design-review.md").write_text(
                "# Design Review\n\n## Verdict\n\nDesign: pass\n",
                encoding="utf-8",
            )
            (change / "architecture.md").write_text("# Architecture\n", encoding="utf-8")
            payload = {
                "tool_name": "apply_patch",
                "success": True,
                "cwd": str(root),
                "tool_input": {
                    "patch": "*** Update File: docs/change/example/architecture.md"
                },
            }
            output = self.run_hook(payload)

        self.assertIsNotNone(output)
        self.assertEqual("block", output["decision"])
        self.assertIn("same-directory design artifact changed", output["reason"])
        self.assertIn("Rerun $design-gate", output["reason"])


if __name__ == "__main__":
    unittest.main()
