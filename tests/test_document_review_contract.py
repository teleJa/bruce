from __future__ import annotations

import unittest

from tests._support import read


DOCUMENT_WRITERS = (
    "artifact-review-gate",
    "grill-with-docs",
    "write-architecture",
    "write-db-design",
    "write-plan",
    "write-tests",
)


class DocumentReviewContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = read("skills/bruce/SKILL.md")

    def test_every_document_change_requires_explicit_d0_verdict(self) -> None:
        self.assertIn("If any documentation changed", self.workflow)
        self.assertIn("separated D0 document self-review", self.workflow)
        self.assertIn("Document review: self-review", self.workflow)
        self.assertIn("Verdict: pass|issues", self.workflow)
        self.assertIn("do not report completion while issues remain", self.workflow)

    def test_d0_checks_facts_consistency_completeness_and_links(self) -> None:
        for check in (
            "factual claims",
            "cross-document references",
            "acceptance coverage",
            "material omissions",
            "unresolved placeholders",
            "broken links",
        ):
            self.assertIn(check, self.workflow)

    def test_d1_is_conditional_and_not_duplicated_for_plans(self) -> None:
        self.assertIn("doc-review-gate", self.workflow)
        self.assertIn("multiple related documents", self.workflow)
        self.assertIn("downstream source of truth", self.workflow)
        self.assertIn("Use\n`plan-review` instead", self.workflow)
        self.assertIn("Do not run both mechanically", self.workflow)
        for verdict in ("`通过|有条件通过|不通过`", "explicitly authorized and recorded"):
            self.assertIn(verdict, self.workflow)
        self.assertIn("`Clean` is equivalent to `通过`", self.workflow)
        self.assertIn("`Issues Found` is equivalent to `不通过`", self.workflow)

    def test_document_writers_report_self_review_when_they_persist_files(self) -> None:
        for name in DOCUMENT_WRITERS:
            body = read(f"skills/{name}/SKILL.md")
            with self.subTest(skill=name):
                self.assertIn("Document self-review: pass|issues", body)
                self.assertRegex(body, r"(?i)diff")
                self.assertRegex(body, r"(?i)placeholders")

    def test_review_results_use_stage_appropriate_audit_locations(self) -> None:
        self.assertIn(
            "Keep implementation/completion D0/D1 results in the current task by default",
            self.workflow,
        )
        self.assertIn("Design-phase candidate decisions", self.workflow)
        self.assertIn("belong in `artifact-review.md`, never `execute_record.md`", self.workflow)
        self.assertIn("existing `execute_record.md`", self.workflow)


if __name__ == "__main__":
    unittest.main()
