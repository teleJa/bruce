from __future__ import annotations

import unittest
from pathlib import Path

from tests._support import ROOT, frontmatter, markdown_links, read


SUPPORTING_SKILLS = (
    "grill-with-docs",
    "write-architecture",
    "write-db-design",
    "write-plan",
    "write-tests",
    "plan-review",
)

LEGACY_MARKERS = (
    "checklist.json",
    "checklist_gate.py",
    "docs/flow",
    "express lane",
    "status: approved",
    "progress.md",
    "completion-review.md",
    "oh-my-claudecode",
    "sonnet",
    "haiku",
)


class SupportingSkillContractTest(unittest.TestCase):
    def test_skill_frontmatter_and_boundaries(self) -> None:
        for name in SUPPORTING_SKILLS:
            path = f"skills/{name}/SKILL.md"
            metadata = frontmatter(path)
            body = read(path)
            with self.subTest(skill=name):
                self.assertEqual(name, metadata["name"])
                self.assertTrue(metadata["description"])
                self.assertIn("## Inputs", body)
                self.assertIn("## Output", body)
                self.assertIn("## Does not own", body)

    def test_reachable_local_resources_exist_and_stay_inside_skill(self) -> None:
        for name in SUPPORTING_SKILLS:
            skill_file = ROOT / "skills" / name / "SKILL.md"
            for link in markdown_links(f"skills/{name}/SKILL.md"):
                if "://" in link or link.startswith("#"):
                    continue
                target = (skill_file.parent / link).resolve()
                with self.subTest(skill=name, link=link):
                    self.assertTrue(target.is_relative_to(skill_file.parent.resolve()))
                    self.assertTrue(target.is_file())

    def test_active_skill_and_reachable_resources_have_no_legacy_runtime(self) -> None:
        for name in SUPPORTING_SKILLS:
            skill_file = ROOT / "skills" / name / "SKILL.md"
            paths = [skill_file]
            for link in markdown_links(f"skills/{name}/SKILL.md"):
                if "://" not in link and not link.startswith("#"):
                    paths.append((skill_file.parent / link).resolve())
            for path in paths:
                text = path.read_text(encoding="utf-8").lower()
                for marker in LEGACY_MARKERS:
                    with self.subTest(skill=name, path=path.name, marker=marker):
                        self.assertNotIn(marker.lower(), text)

    def test_database_contract_uses_repository_conventions(self) -> None:
        combined = read("skills/write-db-design/SKILL.md") + read(
            "skills/write-db-design/templates/table-design.md"
        )
        self.assertIn("repository conventions", combined.lower())
        self.assertNotIn("never use foreign", combined.lower())
        self.assertNotIn("references;", combined.lower())

    def test_api_contract_artifact_is_mandatory_and_has_a_default_location(self) -> None:
        body = read("skills/write-architecture/SKILL.md")
        normalized = " ".join(body.split())
        self.assertIn("must generate or update `api-contracts.md`", normalized)
        self.assertIn("repository's documented convention", normalized)
        self.assertIn("existing change directory", normalized)
        self.assertIn(
            "`docs/change/<YYYYMMDD-HHmmss>-<short-slug>/api-contracts.md`",
            normalized,
        )
        self.assertIn("blocking contract gap", normalized)

    def test_capabilities_do_not_require_cascade(self) -> None:
        for name in SUPPORTING_SKILLS:
            body = read(f"skills/{name}/SKILL.md")
            with self.subTest(skill=name):
                self.assertRegex(body, r"(?i)do not .*automatically|does not own")

    def test_grilling_is_not_used_for_one_isolated_question(self) -> None:
        body = read("skills/grill-with-docs/SKILL.md")
        self.assertIn("multiple dependent decisions", body)
        self.assertIn("one isolated blocking ambiguity", body)
        self.assertIn("return control to Bruce", body)


if __name__ == "__main__":
    unittest.main()
