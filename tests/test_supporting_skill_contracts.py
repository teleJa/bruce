from __future__ import annotations

import unittest

from tests._support import ROOT, frontmatter, markdown_links, read


SUPPORTING_SKILLS = (
    "inspect-parallel",
    "design-gate",
    "goal-execution",
    "grill-with-docs",
    "write-architecture",
    "write-db-design",
    "write-plan",
    "explore-prototype",
    "write-prototype",
    "write-tests",
    "plan-review",
    "spawn-execute",
    "completion-gate",
    "doctor",
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
        self.assertIn(r"generated\|missing\|skipped", template)
        self.assertIn("Behavior implementation: <yes|no>", template)
        self.assertIn("Public/cross-component contract change: <yes|no>", template)
        self.assertIn("required/missing", body)
        self.assertIn("Test design required", normalized)
        self.assertIn("validate_design_review.py", body)

    def test_cross_repository_artifact_placement_is_bounded_and_configurable(self) -> None:
        reference = read("skills/bruce/references/artifact-placement.md")
        normalized = " ".join(reference.split())
        for phrase in (
            "compare their direct parent directories",
            "Do not walk farther up the filesystem",
            "If the direct parent differs, ask the user",
            "<shared-direct-parent>/.bruce/config.yaml",
            "resolved relative to the config file's containing directory",
            "do not silently fall back to a different repository or ancestor",
        ):
            self.assertIn(phrase, normalized)
        self.assertIn("artifacts:", read("skills/bruce/templates/config.yaml"))
        self.assertIn("root: docs/change", read("skills/bruce/templates/config.yaml"))
        self.assertIn("root: docs/change", read(".bruce/config.yaml"))
        for name in (
            "write-architecture",
            "write-plan",
            "write-db-design",
            "write-prototype",
            "write-tests",
            "design-gate",
        ):
            body = read(f"skills/{name}/SKILL.md")
            with self.subTest(skill=name):
                self.assertIn("artifact-placement.md", body)
                self.assertIn("cross-repository", body)

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

    def test_parallel_inspection_is_read_only_and_advisory(self) -> None:
        body = read("skills/inspect-parallel/SKILL.md")
        normalized = " ".join(body.split())
        for phrase in (
            "at least two read-only scopes can be investigated independently",
            "Dispatch no more than five read-only scopes",
            "preserve the working tree",
            "inspect only the missing scope directly",
            "profile-relevant evidence",
            "leave the actual profile and risk decisions to Bruce",
        ):
            self.assertIn(phrase, normalized)
        self.assertIn("Do not modify files", body)
        self.assertIn("Dispatch native subagents as read-only explorers", normalized)
        self.assertIn(
            "Do not select a provider-specific agent name, model, token budget, scheduler, or persistent execution mode",
            normalized,
        )
        self.assertIn("Do not invoke another supporting skill automatically", normalized)
        self.assertNotIn("oh-my-claudecode", body.lower())

    def test_write_plan_does_not_cascade_to_parallel_inspection(self) -> None:
        normalized = " ".join(read("skills/write-plan/SKILL.md").split())
        self.assertIn("when Bruce already produced them", normalized)
        self.assertIn("Do not launch subagents, invoke `inspect-parallel`", normalized)
        self.assertIn("Return `Missing planning evidence`", normalized)
        self.assertIn("smallest bounded scopes Bruce must inspect", normalized)
        self.assertIn("invoke another supporting skill automatically", normalized)
        for forbidden in (
            "use bounded native read-only subagents directly",
            "inspect the affected scopes directly",
        ):
            self.assertNotIn(forbidden, normalized)

    def test_capabilities_do_not_cascade(self) -> None:
        for name in (
            "grill-with-docs",
            "write-architecture",
            "write-db-design",
            "write-plan",
            "write-prototype",
            "write-tests",
            "doctor",
        ):
            body = read(f"skills/{name}/SKILL.md")
            with self.subTest(skill=name):
                self.assertRegex(body, r"(?i)do not invoke it automatically|does not own")

    def test_doctor_is_explicit_and_not_a_completion_authority(self) -> None:
        body = read("skills/doctor/SKILL.md")
        normalized = " ".join(body.split())
        self.assertIn("only when the user explicitly asks", normalized)
        self.assertIn("Do not add or use a hook", normalized)
        self.assertIn("Do not emit or change `Design: pass`", body)
        self.assertIn("does not own the main Bruce workflow", body)


if __name__ == "__main__":
    unittest.main()
