from __future__ import annotations

import unittest

from tests._support import ROOT, frontmatter, read


class ExplorePrototypeContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = " ".join(read("skills/bruce/SKILL.md").split())
        cls.skill = " ".join(read("skills/explore-prototype/SKILL.md").split())
        cls.logic = " ".join(
            read("skills/explore-prototype/references/logic.md").split()
        )
        cls.ui = " ".join(
            read("skills/explore-prototype/references/ui-variants.md").split()
        )

    def test_skill_is_discoverable_and_routes_two_question_types(self) -> None:
        metadata = frontmatter("skills/explore-prototype/SKILL.md")
        self.assertEqual("explore-prototype", metadata["name"])
        self.assertIn("state model", metadata["description"])
        self.assertIn("structurally different UI", metadata["description"])
        self.assertIn("`logic`", self.skill)
        self.assertIn("`ui-variants`", self.skill)
        self.assertIn("split it into two sequential questions", self.skill)
        self.assertIn("`explore-prototype`", self.workflow)

    def test_logic_mode_is_portable_and_scenario_driven(self) -> None:
        for phrase in (
            "self-contained HTML file",
            "pure reducer",
            "state machine",
            "free-play actions",
            "guided scenarios",
            "illegal or rejected action",
            "must not reference DOM APIs",
        ):
            self.assertIn(phrase, self.logic)

    def test_ui_mode_uses_real_host_and_structural_variants(self) -> None:
        for phrase in (
            "two to five structurally different approaches",
            "Prefer the existing route",
            "`?variant=` URL parameter",
            "cannot render in a production build",
            "Codex App Chrome capability",
            "remove the switcher and losing variants",
        ):
            self.assertIn(phrase, self.ui)

    def test_generation_delegation_is_bounded_and_optional(self) -> None:
        for phrase in (
            "`generation_packet`",
            "exclusive allowed paths",
            "complete scenarios or variant requirements",
            "`prototype_evidence_packet`",
            "changed files",
            "commands or actions actually run",
            "Inspect the actual workspace diff",
            "generate sequentially in the main agent",
            "unavailable delegation alone never blocks",
        ):
            self.assertIn(phrase, self.skill)
        self.assertIn("The main agent retains product decisions", self.workflow)
        self.assertIn("unavailable delegation alone does not block", self.workflow)

    def test_exploration_cannot_bypass_formal_prototype_readiness(self) -> None:
        for phrase in (
            "never an implementation-governing UI prototype by itself",
            "pass the chosen decision and relevant artifact through `write-prototype`",
            "Only that confirmed result may enter Design Gate",
            "Do not generate a formal Open Design artifact",
            "Do not invoke another supporting skill automatically",
        ):
            self.assertIn(phrase, self.skill)

    def test_sources_and_ui_metadata_are_packaged(self) -> None:
        for relative in (
            "skills/explore-prototype/references/logic.md",
            "skills/explore-prototype/references/ui-variants.md",
            "skills/explore-prototype/references/source-attribution.md",
            "skills/explore-prototype/agents/openai.yaml",
        ):
            self.assertTrue((ROOT / relative).is_file())
        attribution = read(
            "skills/explore-prototype/references/source-attribution.md"
        )
        self.assertIn("Matt Pocock", attribution)
        self.assertIn("MIT", attribution)
        self.assertIn("6bcbcb0", attribution)


if __name__ == "__main__":
    unittest.main()
