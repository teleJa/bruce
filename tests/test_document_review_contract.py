from __future__ import annotations

import unittest

from tests._support import ROOT, read


DOCUMENT_WRITERS = (
    "grill-with-docs",
    "write-architecture",
    "write-db-design",
    "write-plan",
    "write-prototype",
    "write-tests",
)


class DocumentReviewContractTest(unittest.TestCase):
    def test_design_gate_combines_completeness_and_readiness(self) -> None:
        gate = read("skills/design-gate/SKILL.md")
        self.assertIn("owns both\nartifact completeness and document readiness", gate)
        for check in (
            "factual claims",
            "cross-document references",
            "acceptance coverage",
            "material omissions",
            "unresolved placeholders",
            "broken links",
        ):
            self.assertIn(check, gate)
        self.assertIn("Design: pass|blocked", gate)

    def test_design_review_persists_one_candidate_matrix(self) -> None:
        gate = read("skills/design-gate/SKILL.md")
        template = read("skills/design-gate/templates/design-review.md")
        self.assertIn("exactly one same-directory `design-review.md`", gate)
        self.assertIn("Candidate Matrix", template)
        self.assertIn("Review mode: <main-agent|independent>", template)
        self.assertIn("Behavior implementation: <yes|no>", template)
        self.assertIn("Public/cross-component contract change: <yes|no>", template)
        self.assertIn("Database/persistence design change: <yes|no>", template)
        self.assertIn("Design: <pass|blocked>", template)
        self.assertIn("validate_design_review.py", gate)
        self.assertIn("non-zero result or an unexecuted validator forces", gate)
        self.assertTrue((ROOT / "skills/design-gate/SKILL.md").is_file())

    def test_independence_is_a_mode_not_an_extra_verdict(self) -> None:
        gate = read("skills/design-gate/SKILL.md")
        policy = read("skills/bruce/references/verification-loop.md")
        self.assertIn("review mode\n(`main-agent|independent`)", gate)
        self.assertIn("never a third verdict", policy)
        self.assertIn("without the author's rationale or proposed verdict", gate)

    def test_document_writers_return_local_checks_and_defer_readiness(self) -> None:
        for name in DOCUMENT_WRITERS:
            body = read(f"skills/{name}/SKILL.md")
            with self.subTest(skill=name):
                self.assertIn("Document check: clear|issues", body)
                self.assertNotIn("D0", body)
                self.assertNotIn("D1", body)
        for name in DOCUMENT_WRITERS[1:]:
            body = read(f"skills/{name}/SKILL.md")
            with self.subTest(skill=name):
                self.assertIn("`design-gate` is required", body)

    def test_old_document_gate_is_removed(self) -> None:
        self.assertFalse((ROOT / "skills/doc-review-gate/SKILL.md").exists())
        self.assertFalse((ROOT / "skills/artifact-review-gate/SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
