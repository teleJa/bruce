from __future__ import annotations

import unittest

from tests._support import ROOT, frontmatter, markdown_links, read


SUPPORTING_SKILLS = (
    "design-gate",
    "goal-execution",
    "grill-with-docs",
    "write-architecture",
    "write-db-design",
    "write-plan",
    "write-prototype",
    "write-tests",
    "plan-review",
    "spawn-execute",
    "completion-gate",
)

LEGACY_MARKERS = (
    "checklist.json",
    "checklist_gate.py",
    "express lane",
    "progress.md",
    "completion-review.md",
    "oh-my-claudecode",
    "sonnet",
    "haiku",
    "verify-completion",
)


class SupportingSkillContractTest(unittest.TestCase):
    def test_skill_frontmatter_and_boundaries(self) -> None:
        for name in SUPPORTING_SKILLS:
            metadata = frontmatter(f"skills/{name}/SKILL.md")
            body = read(f"skills/{name}/SKILL.md")
            with self.subTest(skill=name):
                self.assertEqual(name, metadata["name"])
                self.assertTrue(metadata["description"])
                self.assertIn("## Output", body)
                self.assertIn("## Does not own", body)

    def test_reachable_resources_exist_and_stay_inside_skill(self) -> None:
        for name in SUPPORTING_SKILLS:
            skill_file = ROOT / "skills" / name / "SKILL.md"
            for link in markdown_links(f"skills/{name}/SKILL.md"):
                if "://" in link or link.startswith("#"):
                    continue
                target = (skill_file.parent / link).resolve()
                with self.subTest(skill=name, link=link):
                    self.assertTrue(target.is_relative_to((ROOT / "skills").resolve()))
                    self.assertTrue(target.is_file())

    def test_active_resources_have_no_legacy_runtime(self) -> None:
        for name in SUPPORTING_SKILLS:
            skill_file = ROOT / "skills" / name / "SKILL.md"
            paths = [skill_file]
            paths.extend(
                (skill_file.parent / link).resolve()
                for link in markdown_links(f"skills/{name}/SKILL.md")
                if "://" not in link and not link.startswith("#")
            )
            for path in paths:
                text = path.read_text(encoding="utf-8").lower()
                for marker in LEGACY_MARKERS:
                    with self.subTest(skill=name, path=path.name, marker=marker):
                        self.assertNotIn(marker, text)

    def test_design_gate_has_complete_candidate_matrix_and_one_verdict(self) -> None:
        body = read("skills/design-gate/SKILL.md")
        template = read("skills/design-gate/templates/design-review.md")
        normalized = " ".join(body.split())
        for candidate in (
            "requirement or clarification",
            "`architecture.md`",
            "`api-contracts.md`",
            "`table-design.md`",
            "`plan.md`",
            "`test-plan.md`",
            "UI prototype",
        ):
            self.assertIn(candidate, normalized)
        self.assertIn("repository-backed evidence", normalized)
        self.assertIn("Design: pass|blocked", body)
        self.assertIn(r"required\|skipped", template)
        self.assertIn(r"generated\|skipped", template)

    def test_api_contract_artifact_is_mandatory(self) -> None:
        normalized = " ".join(read("skills/write-architecture/SKILL.md").split())
        self.assertIn("must generate or update `api-contracts.md`", normalized)
        self.assertIn("`docs/change/<YYYYMMDD-HHmmss>-<short-slug>/api-contracts.md`", normalized)
        self.assertIn("blocking contract gap", normalized)

    def test_profile_does_not_trigger_supporting_modes(self) -> None:
        self.assertNotIn("Bruce routes a `full` task", read("skills/goal-execution/SKILL.md"))
        self.assertNotIn("When a `full` task", read("skills/design-gate/SKILL.md"))
        tests = read("skills/write-tests/SKILL.md")
        self.assertIn("profile alone is neither necessary nor sufficient", tests)

    def test_capabilities_do_not_cascade(self) -> None:
        for name in (
            "grill-with-docs",
            "write-architecture",
            "write-db-design",
            "write-plan",
            "write-prototype",
            "write-tests",
        ):
            body = read(f"skills/{name}/SKILL.md")
            with self.subTest(skill=name):
                self.assertRegex(body, r"(?i)do not invoke it automatically|does not own")


if __name__ == "__main__":
    unittest.main()
