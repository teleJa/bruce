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
                (change / path).write_text(
                    f"# {candidate}\n\n当前工件内容已完成并可验证。\n",
                    encoding="utf-8",
                )

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


if __name__ == "__main__":
    unittest.main()
