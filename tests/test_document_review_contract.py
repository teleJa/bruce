from __future__ import annotations

import unittest

from tests._support import ROOT, read


DOCUMENT_WRITERS = (
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
        self.assertTrue("Candidate Matrix" in template or "候选工件矩阵" in template or "候选矩阵" in template)
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

    def test_plan_review_requires_independent_packet_without_automatic_invocation(self) -> None:
        plan = read("skills/plan-review/SKILL.md")
        prompt = read("skills/plan-review/references/plan-reviewer-prompt.md")
        interface = read("skills/plan-review/agents/openai.yaml")
        self.assertIn("optional standalone entry", plan)
        self.assertIn("Once invoked, independent review is mandatory", plan)
        self.assertNotIn("Use `main-agent` review mode by default", plan)
        for body in (plan, prompt):
            with self.subTest(document=body.splitlines()[0]):
                for token in (
                    'fork_turns="none"',
                    "review_packet",
                    "mandatory-independent-review",
                    "fallback: blocked",
                    "original",
                    "new snapshot",
                ):
                    self.assertIn(token, body)
        self.assertIn("Only the caller interprets a valid independent packet", plan)
        self.assertIn("not executed / blocked", plan)
        self.assertIn("never invent a `pass` result", plan)
        self.assertIn("Do not ignore blocking findings", plan)
        self.assertNotIn("Status: Clean | Issues Found", prompt)
        self.assertIn("Do not return Clean, Issues Found, Design, Completion, verdict, or approval", prompt)
        self.assertIn("valid independent review_packet", interface)

    def test_design_quality_review_is_mandatory_but_completeness_can_be_deterministic(self) -> None:
        gate = read("skills/design-gate/SKILL.md")
        normalized = " ".join(gate.split())
        template = read("skills/design-gate/templates/design-review.md")
        self.assertIn("purely deterministic completeness checks", gate)
        self.assertIn("Any design-quality or critical-semantic assessment requires an independent", gate)
        for trigger in (
            "public/cross-component contracts",
            "persistence or migration",
            "permissions or security",
            "asynchronous/concurrent/idempotent behavior",
            "cross-repository design",
            "governing prototypes",
            "semantic disputes",
            "explicit user request",
        ):
            self.assertIn(trigger, normalized)
        self.assertIn("mandatory-independent-review", gate)
        self.assertIn("fallback: blocked", gate)
        self.assertIn("ask the user to explicitly name an available replacement", normalized)
        self.assertIn("never use `main-agent` mode as a substitute", normalized)
        self.assertIn("original independent reviewer must re-review the new snapshot", normalized)
        self.assertIn("Design Gate remains the only owner of `Design: pass|blocked`", gate)
        self.assertIn("main-agent is deterministic completeness only", template)
        self.assertIn("mode alone does not prove execution", template)
        self.assertIn("author confirmation is insufficient", template)

    def test_document_writers_return_local_checks_and_mandatory_gate_handoff(self) -> None:
        for name in DOCUMENT_WRITERS:
            body = read(f"skills/{name}/SKILL.md")
            normalized = " ".join(body.split())
            with self.subTest(skill=name):
                self.assertIn("Document check: clear|issues", body)
                self.assertNotIn("D0", body)
                self.assertNotIn("D1", body)
                self.assertIn("`design-gate` handoff", normalized)
                if name == "write-tests":
                    self.assertIn("同一轮", normalized)
                    self.assertIn("无需用户追加指令", normalized)
                    self.assertIn("不拥有 Design verdict", normalized)
                else:
                    self.assertIn("same turn", normalized)
                    self.assertIn("without another user instruction", normalized)
                    self.assertIn("does not own the Design verdict", normalized)

    def test_old_document_gate_is_removed(self) -> None:
        self.assertFalse((ROOT / "skills/doc-review-gate/SKILL.md").exists())
        self.assertFalse((ROOT / "skills/artifact-review-gate/SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
