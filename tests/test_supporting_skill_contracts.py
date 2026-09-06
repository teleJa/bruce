from __future__ import annotations

import unittest

from tests._support import ROOT, frontmatter, markdown_links, read


SUPPORTING_SKILLS = (
    "inspect-parallel",
    "solution-analysis",
    "design-gate",
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
    "verification-profile",
    "environment-profile",
    "environment-operations",
    "test-dispatch",
    "api-test-orchestration",
    "browser-ui-verification",
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
        self.assertIn("independent Test design artifact", normalized)
        self.assertIn("Every behavior change requires", normalized)
        self.assertIn("minimum scenarios", normalized)
        self.assertIn("Complex acceptance: <yes|no>", template)
        self.assertIn("artifact-policy.md", body)
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

    def test_db_design_prohibits_database_foreign_keys(self) -> None:
        skill = " ".join(read("skills/write-db-design/SKILL.md").split())
        template = " ".join(read("skills/write-db-design/templates/table-design.md").split())
        self.assertIn("Do not add database-level foreign keys", skill)
        self.assertIn("`FOREIGN KEY` constraints", skill)
        self.assertIn("`REFERENCES` clauses", skill)
        self.assertIn("Database-level foreign keys are prohibited", template)
        self.assertIn("logical references (no database foreign keys)", template)

    def test_api_contract_artifact_is_mandatory(self) -> None:
        normalized = " ".join(read("skills/write-architecture/SKILL.md").split())
        self.assertIn("must generate or update `api-contracts.md`", normalized)
        self.assertIn("`docs/change/<YYYYMMDD-HHmmss>-<short-slug>/api-contracts.md`", normalized)
        self.assertIn("blocking contract gap", normalized)

    def test_write_tests_template_has_chinese_consistency_contract(self) -> None:
        template = read("skills/write-tests/templates/test-plan.md")
        for phrase in (
            "## 一致性与权威状态矩阵",
            "## 冲突与权限视角场景矩阵",
            "consistency_check",
            "预期 UI 状态",
            "预期 API/结果",
            "持久化不变量",
            "中文请求的自然语言字段全部使用简体中文",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, template)

    def test_task_contract_carries_consistency_fields(self) -> None:
        reference = read("skills/bruce/references/task-contract.md")
        template = read("skills/write-plan/templates/task.md")
        for phrase in (
            "business invariant",
            "authoritative state",
            "competing writers/viewers",
            "conflict semantics",
            "data-preservation guarantee",
            "test-plan.md",
        ):
            self.assertIn(phrase, reference)
        for phrase in (
            "一致性检查",
            "业务不变量与权威状态摘要",
            "竞争者/权限视角与冲突后果",
            "关联测试计划矩阵/场景 ID",
            "不适用原因",
        ):
            self.assertIn(phrase, template)
        self.assertIn("## 业务不变量与权威状态", template)

    def test_verification_profile_is_requirement_scoped_and_unconfirmed(self) -> None:
        body = read("skills/verification-profile/SKILL.md")
        normalized = " ".join(body.split())
        for phrase in (
            "Requirement Verification Profile",
            "exact `requirements.md` path",
            "confirmation.state=pending",
            "confirmed Environment Profiles",
            "waiting_external",
            "waiting_user",
            "blocked",
            "explicit resume",
            "Completion Gate",
            "Missing requirements input",
            "Verification Profile: ready-for-confirmation",
            "Do not generate Environment Profiles",
        ):
            self.assertIn(phrase, normalized)
        self.assertIn("profile-schema.md", body)
        self.assertIn("verification-profile.yaml", body)
        self.assertIn("acceptance_ids", body)

    def test_environment_profile_has_reusable_and_secret_boundaries(self) -> None:
        body = read("skills/environment-profile/SKILL.md")
        normalized = " ".join(body.split())
        for phrase in (
            "reusable **Environment Profile**",
            "user-provided and user-confirmed environment information",
            "confirmation.state: pending",
            "ready_for_confirmation",
            "needs_input",
            "unresolved questions",
            "account pools",
            "credential references",
            "preflight",
            "freshness",
            "ready_for_confirmation",
            "Never report `Design: pass` or `Completion: pass|issues|blocked`",
        ):
            self.assertIn(phrase, normalized)
        self.assertIn("profile-schema.md", body)
        self.assertIn("environment-profile.yaml", body)
        self.assertIn("Completion: pass|issues|blocked", body)

    def test_profile_does_not_trigger_supporting_modes(self) -> None:
        self.assertNotIn("When a `full` task", read("skills/design-gate/SKILL.md"))
        tests = read("skills/write-tests/SKILL.md")
        self.assertIn("profile 本身既不是必要条件，也不是充分条件", tests)


    def test_solution_analysis_is_read_only_and_stops_before_design(self) -> None:
        body = read("skills/solution-analysis/SKILL.md")
        normalized = " ".join(body.split())
        for phrase in (
            "由主 Agent 决定是否委托 Subagent",
            "`inspector` Profile",
            "`task_kind=inspect`",
            "`output=task_evidence_packet`",
            "`allowed_paths=[]`",
            "gpt-5.6-luna",
            "gpt-5.6-terra",
            "Analysis: complete",
            "Awaiting user direction: yes",
        ):
            self.assertIn(phrase, normalized)
        self.assertIn("不得自动调用后续 Skill", body)
        self.assertIn("Do not modify files", body)
        self.assertIn("Do not treat `Analysis: complete` as `Design: pass`", body)

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

    def test_parallel_inspection_requires_pre_dispatch_model_resolution(self) -> None:
        body = read("skills/inspect-parallel/SKILL.md")
        normalized = " ".join(body.split())
        for phrase in (
            "Mandatory pre-dispatch routing gate",
            "before calling the native `spawn_agent` tool",
            "Do not call `spawn_agent` until a `model_resolution` record",
            "Pass `model` only when `resolution_result=resolved`",
            "when `resolution_result=fallback`, intentionally omit `model`",
            "If resolution is `blocked`, the resolver fails",
            "A worker's later `model_resolution` output does not prove",
            "In `Inspection mode: direct`, do not create a native subagent",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, normalized)

    def test_write_plan_does_not_cascade_to_parallel_inspection(self) -> None:
        normalized = " ".join(read("skills/write-plan/SKILL.md").split())
        self.assertIn("when Bruce already produced them", normalized)
        self.assertIn("Do not launch subagents, invoke `inspect-parallel`", normalized)
        self.assertIn("Return `Missing planning evidence`", normalized)
        self.assertIn("smallest bounded scopes Bruce must inspect", normalized)
        self.assertIn("other supporting skills remain predicate-driven", normalized)
        for forbidden in (
            "use bounded native read-only subagents directly",
            "inspect the affected scopes directly",
        ):
            self.assertNotIn(forbidden, normalized)

    def test_capabilities_only_auto_chain_the_mandatory_design_gate_handoff(self) -> None:
        for name in (
            "write-architecture",
            "write-db-design",
            "write-plan",
            "write-prototype",
            "write-tests",
        ):
            body = read(f"skills/{name}/SKILL.md")
            normalized = " ".join(body.split())
            with self.subTest(skill=name):
                self.assertIn("`design-gate` handoff", normalized)
                self.assertRegex(
                    normalized,
                    r"(?i)other supporting skills remain predicate-driven|除强制 Design Gate handoff 外，不要自动调用其他 supporting skill",
                )
        doctor = read("skills/doctor/SKILL.md")
        self.assertIn("does not own the main Bruce workflow", doctor)

    def test_doctor_is_explicit_and_not_a_completion_authority(self) -> None:
        body = read("skills/doctor/SKILL.md")
        normalized = " ".join(body.split())
        self.assertIn("only when the user explicitly asks", normalized)
        self.assertIn("Do not add or use a hook", normalized)
        self.assertIn("Do not emit or change `Design: pass`", body)
        self.assertIn("does not own the main Bruce workflow", body)


if __name__ == "__main__":
    unittest.main()
