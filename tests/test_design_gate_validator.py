from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests._support import ROOT


VALIDATOR = ROOT / "skills/design-gate/scripts/validate_design_review.py"
CANDIDATES = (
    ("Requirement or clarification", "requirements.md"),
    ("Architecture", "architecture.md"),
    ("API/file contracts", "api-contracts.md"),
    ("Database/table design", None),
    ("Implementation plan", "plan.md"),
    ("Test design", "test-plan.md"),
    ("UI prototype", None),
)


class DesignGateValidatorTest(unittest.TestCase):
    def make_change(
        self,
        root: Path,
        *,
        verdict: str = "pass",
        behavior: str = "yes",
        missing_candidate: str | None = None,
        test_applicability: str = "required",
        test_delivery: str = "generated",
        blockers: str = "none。当前工件没有阻塞项。",
        facts: str = "pass。字段和状态已对照当前仓库。",
        contract_change: str = "yes",
        persistence_change: str = "no",
        governing_prototype: str = "no",
        validation_result: str = "pass",
    ) -> Path:
        change = root / "docs/change/example"
        change.mkdir(parents=True)
        rows: list[str] = []
        for candidate, artifact in CANDIDATES:
            if candidate == missing_candidate:
                continue
            applicability = "required" if artifact else "skipped"
            delivery = "generated" if artifact else "skipped"
            path = artifact or "none"
            evidence = "当前范围和仓库实现证明该工件需要生成并参与实现。"
            if candidate in {"Database/table design", "UI prototype"}:
                evidence = "当前变更不修改数据库结构且不使用治理型 UI 原型，复用现有实现。"
            if candidate == "Test design":
                applicability = test_applicability
                delivery = test_delivery
                path = "test-plan.md" if delivery == "generated" else "none"
            rows.append(
                f"| {candidate} | {applicability} | {delivery} | `{path}` | {evidence} |"
            )
            if delivery == "generated":
                content = f"# {candidate}\n\n当前工件内容已完成并可验证。\n"
                if candidate == "Implementation plan":
                    content = (
                        "# Implementation plan\n\n## Task package\n\n"
                        "- Omission reason: trivial documentation-only test fixture.\n"
                    )
                (change / path).write_text(content, encoding="utf-8")

        review = "\n".join(
            [
                "# Design Review",
                "",
                "- Objective: 验证工作区知识助手设计。",
                "- Scope: 仅检查当前变更目录中的设计工件。",
                "- Implementation boundary: 这些工件约束后续行为实现。",
                "- Review mode: main-agent",
                f"- Behavior implementation: {behavior}",
                f"- Public/cross-component contract change: {contract_change}",
                f"- Database/persistence design change: {persistence_change}",
                f"- Governing UI prototype: {governing_prototype}",
                "",
                "## Candidate Matrix",
                "",
                "| Candidate | Applicability | Delivery | Path | Repository-backed evidence |",
                "|---|---|---|---|---|",
                *rows,
                "",
                "## Readiness",
                "",
                f"- Facts and consistency: {facts}",
                "- Acceptance and verification coverage: pass。验收均有可执行证据路径。",
                "- Risk and recovery coverage: pass。失败、重试和恢复路径已覆盖。",
                "- Existing-product visual authority and compatibility: clear。复用现有界面规范。",
                "- Deterministic artifact visual assertions: clear。当前范围无新增视觉令牌。",
                f"- Blocking findings: {blockers}",
                "- Evidence boundary: 已检查当前目录工件和对应仓库事实，未执行实现。",
                "- Smallest next action: none。设计通过后进入实现。",
                "",
                "## Validation",
                "",
                "- Command: `python3 validate_design_review.py --change-dir docs/change/example`",
                f"- Result: {validation_result}。由当前验证命令提供证据。",
                "",
                "## Verdict",
                "",
                f"Design: {verdict}",
                "",
            ]
        )
        (change / "design-review.md").write_text(review, encoding="utf-8")
        return change

    def run_validator(self, change: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), "--change-dir", str(change)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_complete_consistent_pass_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_validator(self.make_change(Path(directory)))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("validation passed", result.stdout)

    def test_chinese_task_contract_is_validated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            change = self.make_change(Path(directory))
            (change / "tasks").mkdir()
            (change / "plan.md").write_text(
                "# Plan\n\n## Task package\n\n- Path: `tasks/`\n",
                encoding="utf-8",
            )
            (change / "tasks/index.yaml").write_text(
                """version: 1
execution: sequential
tasks:
  - task_id: T-001
    title: 中文任务
    contract_revision: 1
    path: tasks/T-001-chinese-task.md
    depends_on: []
    acceptance_ids: [AC-01]
    allowed_paths: [src/example.py]
    excluded_paths: [deploy/]
    parallel_safe: false
""",
                encoding="utf-8",
            )
            (change / "tasks/T-001-chinese-task.md").write_text(
                """# 任务 T-001：中文任务

- 契约修订：1

## 目标

完成中文任务。

## 包含范围

- `src/example.py`

## 排除范围

- `deploy/`

## 依赖关系

- 依赖任务：无

## 验收标准

- Given：仓库有效
- When：执行任务
- Then：任务完成
- Evidence：unit-test-01

## 验证

- 必需层级：unit
- 命令/检查：`python -m unittest`
- 环境：无

## 授权与风险

- 授权：normal
- 风险触发：low
- 停止条件：返回任务检查点

## 契约变更规则

范围或验收变化时创建新的契约修订。
""",
                encoding="utf-8",
            )
            result = self.run_validator(change)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_plan_declared_task_package_is_validated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            change = self.make_change(Path(directory))
            (change / "tasks").mkdir()
            (change / "plan.md").write_text(
                "# Plan\n\n## Task package\n\n- Path: `tasks/`\n",
                encoding="utf-8",
            )
            (change / "tasks/index.yaml").write_text(
                """version: 1
execution: sequential
tasks:
  - task_id: T-001
    title: Implement bounded change
    contract_revision: 1
    path: tasks/T-001-bounded-change.md
    depends_on: []
    acceptance_ids: [AC-01]
    allowed_paths: [src/example.py]
    excluded_paths: [deploy/]
    parallel_safe: false
""",
                encoding="utf-8",
            )
            (change / "tasks/T-001-bounded-change.md").write_text(
                """# Task T-001: Implement bounded change

- Contract revision: 1

## Objective

Implement the bounded change.

## Included scope

- `src/example.py`

## Excluded scope

- `deploy/`

## Dependencies

- Depends on: none

## Acceptance

- Parent scenario ids: AC-01
- Given: a valid repository
- When: the task is implemented
- Then: the bounded change works
- Evidence: unit-test-01

## Verification

- Required layer: unit
- Commands/checks: `python -m unittest`
- Environment: none

## Authorization and risks

- Authorization: normal
- Risk trigger: low
- Stop condition: return the task checkpoint

## Contract change rule

Create a new revision when scope or acceptance changes.
""",
                encoding="utf-8",
            )
            result = self.run_validator(change)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_task_package_rejects_wrong_index_field_types(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            change = self.make_change(Path(directory))
            (change / "tasks").mkdir()
            (change / "plan.md").write_text(
                "# Plan\n\n## Task package\n\n- Path: `tasks/`\n",
                encoding="utf-8",
            )
            (change / "tasks/index.yaml").write_text(
                """version: 1
execution: sequential
tasks:
  - task_id: T-001
    title: Bounded change
    contract_revision: 1
    path: tasks/T-001.md
    depends_on: []
    acceptance_ids: AC-01
    allowed_paths: src/
    excluded_paths: deploy/
    parallel_safe: false
""",
                encoding="utf-8",
            )
            (change / "tasks/T-001.md").write_text(
                """# Task T-001: Bounded change

## Objective
Implement the bounded change.

## Included scope
- `src/`

## Excluded scope
- `deploy/`

## Dependencies
- Depends on: none

## Acceptance
- Then: the change works

## Verification
- Required layer: unit

## Authorization and risks
- Authorization: normal

## Contract change rule
Create a new revision when scope changes.
""",
                encoding="utf-8",
            )
            result = self.run_validator(change)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("acceptance_ids must be a list", result.stderr)
        self.assertIn("allowed_paths must be a list", result.stderr)
        self.assertIn("excluded_paths must be a list", result.stderr)

    def test_implementation_plan_requires_task_package_section(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            change = self.make_change(Path(directory))
            (change / "plan.md").write_text(
                "# Plan\n\nA plan without the canonical task package section.\n",
                encoding="utf-8",
            )
            result = self.run_validator(change)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("must include a Task package section", result.stderr)

    def test_task_package_section_requires_declaration_or_omission_reason(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            change = self.make_change(Path(directory))
            (change / "plan.md").write_text(
                "# Plan\n\n## Task package\n\n- Status source: `checkpoint.yaml`\n",
                encoding="utf-8",
            )
            result = self.run_validator(change)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("must declare tasks/", result.stderr)

    def test_plan_declared_task_package_requires_index_and_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            change = self.make_change(Path(directory))
            (change / "plan.md").write_text(
                "# Plan\n\n## Task package\n\n- Path: `tasks/`\n",
                encoding="utf-8",
            )
            result = self.run_validator(change)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("task package declares tasks/", result.stderr)

    def test_missing_candidate_rejects_false_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_validator(
                self.make_change(Path(directory), missing_candidate="Test design")
            )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing candidates: Test design", result.stderr)

    def test_required_missing_test_plan_rejects_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            change = self.make_change(
                Path(directory), test_applicability="required", test_delivery="missing"
            )
            result = self.run_validator(change)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing required artifact: Test design", result.stderr)

    def test_required_plan_cannot_skip_test_design_even_if_behavior_is_no(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_validator(
                self.make_change(
                    Path(directory),
                    behavior="no",
                    test_applicability="skipped",
                    test_delivery="skipped",
                )
            )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("requires Test design", result.stderr)

    def test_contract_change_cannot_skip_api_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            change = self.make_change(Path(directory))
            review = change / "design-review.md"
            review.write_text(
                review.read_text(encoding="utf-8").replace(
                    "| API/file contracts | required | generated | `api-contracts.md` |",
                    "| API/file contracts | skipped | skipped | `none` |",
                ),
                encoding="utf-8",
            )
            result = self.run_validator(change)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("yes requires API/file contracts", result.stderr)

    def test_clear_english_issue_phrasing_does_not_block_a_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_validator(
                self.make_change(
                    Path(directory),
                    facts="pass. no issues found.",
                    blockers="No blocking findings.",
                )
            )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_blocked_review_may_record_missing_required_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_validator(
                self.make_change(
                    Path(directory),
                    verdict="blocked",
                    test_applicability="required",
                    test_delivery="missing",
                    blockers="Test design 缺失，必须补齐后重新评审。",
                    facts="blocked。测试设计尚未生成。",
                )
            )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_blocked_verdict_requires_a_successful_validator_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_validator(
                self.make_change(
                    Path(directory),
                    verdict="blocked",
                    validation_result="blocked",
                    test_applicability="required",
                    test_delivery="missing",
                    blockers="Test design 缺失，必须补齐后重新评审。",
                    facts="blocked。测试设计尚未生成。",
                )
            )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("Validation Result must start with pass", result.stderr)

    def test_validation_fields_outside_validation_section_do_not_count(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            change = self.make_change(Path(directory))
            review = change / "design-review.md"
            text = review.read_text(encoding="utf-8")
            text = text.replace(
                "## Validation\n\n- Command: `python3 validate_design_review.py --change-dir docs/change/example`\n- Result: pass。由当前验证命令提供证据。",
                "## Validation\n\n无命令证据。",
            )
            text = text.replace(
                "- Smallest next action: none。设计通过后进入实现。",
                "- Smallest next action: none。设计通过后进入实现。\n- Command: `python3 validate_design_review.py --change-dir docs/change/example`\n- Result: pass。伪造在 Readiness 中。",
            )
            review.write_text(text, encoding="utf-8")
            result = self.run_validator(change)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("Validation Command must invoke", result.stderr)

    def test_duplicate_candidate_artifact_paths_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            change = self.make_change(Path(directory))
            review = change / "design-review.md"
            review.write_text(
                review.read_text(encoding="utf-8").replace(
                    "| Test design | required | generated | `test-plan.md` |",
                    "| Test design | required | generated | `plan.md` |",
                ),
                encoding="utf-8",
            )
            result = self.run_validator(change)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("generated artifact path duplicates", result.stderr)

    def test_pass_conflicting_with_blocking_findings_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_validator(
                self.make_change(Path(directory), blockers="Test design 尚有阻塞问题。")
            )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("Blocking findings to be none", result.stderr)

    def test_generated_artifact_must_exist(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            change = self.make_change(Path(directory))
            (change / "api-contracts.md").unlink()
            result = self.run_validator(change)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("generated artifact does not exist", result.stderr)

    def test_unresolved_placeholders_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            change = self.make_change(Path(directory))
            review = change / "design-review.md"
            review.write_text(
                review.read_text(encoding="utf-8").replace(
                    "验证工作区知识助手设计。", "<objective>"
                ),
                encoding="utf-8",
            )
            result = self.run_validator(change)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("unresolved placeholders", result.stderr)

    def test_surface_contract_completeness_is_a_design_blocker(self) -> None:
        skill = (ROOT / "skills/design-gate/SKILL.md").read_text(encoding="utf-8")
        for marker in (
            "UI Surface Contract",
            "surface_id",
            "region hierarchy",
            "required states",
            "interaction transitions",
            "observable fields",
            "layout invariants",
            "evidence methods",
            "generic implementation mapping",
            "Design blocker",
            "Do not require React/Vue",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, skill)
        self.assertIn("visual-token", skill)
        self.assertIn("prototype existence", skill)


    def test_chinese_section_headings_are_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            change = self.make_change(Path(directory))
            review = change / "design-review.md"
            text = review.read_text(encoding="utf-8")
            text = text.replace("# Design Review", "# 设计评审")
            text = text.replace("## Candidate Matrix", "## 候选工件矩阵")
            text = text.replace("## Readiness", "## 就绪检查")
            text = text.replace("## Validation", "## 验证")
            text = text.replace("## Verdict", "## 结论")
            review.write_text(text, encoding="utf-8")
            result = self.run_validator(change)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_chinese_candidate_matrix_alias_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            change = self.make_change(Path(directory))
            review = change / "design-review.md"
            text = review.read_text(encoding="utf-8")
            text = text.replace("# Design Review", "# 设计评审")
            text = text.replace("## Candidate Matrix", "## 候选矩阵")
            text = text.replace("## Readiness", "## 就绪度")
            text = text.replace("## Validation", "## 校验")
            text = text.replace("## Verdict", "## 评审结论")
            review.write_text(text, encoding="utf-8")
            result = self.run_validator(change)
        self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
