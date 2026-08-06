from __future__ import annotations

import unittest

from tests._support import read


DOCUMENT_WRITERS = (
    "grill-with-docs",
    "write-architecture",
    "write-db-design",
    "write-plan",
    "write-prototype",
    "write-tests",
    "design-gate",
)


class DocumentLanguageContractTest(unittest.TestCase):
    def test_bruce_defines_document_language_rule(self) -> None:
        body = " ".join(read("skills/bruce/SKILL.md").split())
        self.assertIn("document-language.md", body)
        self.assertIn("user's language", body)

    def test_document_writers_reference_language_rule(self) -> None:
        for name in DOCUMENT_WRITERS:
            with self.subTest(skill=name):
                body = read(f"skills/{name}/SKILL.md")
                self.assertIn("document-language.md", body)
                self.assertIn("Simplified Chinese", body)

    def test_language_rule_preserves_machine_tokens_and_history(self) -> None:
        policy = read("skills/bruce/references/document-language.md")
        for token in ("Given", "When", "Then", "Evidence", "historical artifacts"):
            self.assertIn(token, policy)


if __name__ == "__main__":
    unittest.main()
