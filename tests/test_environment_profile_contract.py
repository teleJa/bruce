from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from tests._support import ROOT, read


VALIDATOR = ROOT / "skills/environment-profile/scripts/validate_profile.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("environment_profile_validator", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load profile validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EnvironmentProfileContractTest(unittest.TestCase):
    def test_skill_requires_reusable_environment_facts_and_user_confirmation(self) -> None:
        body = read("skills/environment-profile/SKILL.md")
        normalized = " ".join(body.split())
        for phrase in (
            "reusable **Environment Profile**",
            "user-provided environment knowledge",
            "confirmation",
            "state: pending",
            "ready_for_confirmation",
            "needs_input",
            "unresolved_fact",
            "account pools",
            "credential references",
            "secret values",
            "runtime preflight",
            "stale",
            "does not execute the environment",
        ):
            self.assertIn(phrase, normalized)

    def test_template_is_unconfirmed_and_does_not_store_secrets(self) -> None:
        template = read("skills/environment-profile/templates/environment-profile.yaml")
        data = yaml.safe_load(template)
        self.assertEqual(1, data["version"])
        self.assertEqual("environment", data["profile_kind"])
        self.assertEqual("pending", data["confirmation"]["state"])
        self.assertFalse(data["security"]["persist_secrets"])
        self.assertFalse(data["security"]["expose_secrets_to_model"])
        self.assertNotIn("api_key", template.lower())
        self.assertNotIn("password", template.lower())
        self.assertNotIn("jwt", template.lower())

    def test_schema_separates_static_profile_from_runtime_and_completion(self) -> None:
        schema = read("skills/environment-profile/references/profile-schema.md")
        normalized = " ".join(schema.split())
        for phrase in (
            "confirmation",
            "state: pending",
            "repository",
            "project-document",
            "user",
            "runtime-preflight",
            "secret value",
            "Verification Run/Checkpoint",
            "completion verdict",
            "profile_state",
        ):
            self.assertIn(phrase, normalized)
        self.assertIn("must not contain", normalized.lower())

    def test_validator_accepts_static_profile_and_rejects_dynamic_or_secret_content(self) -> None:
        validator = load_validator()
        valid = {
            "version": 1,
            "profile_kind": "environment",
            "profile_id": "multica-test",
            "profile_revision": 1,
            "content_hash": "sha256:abc",
            "profile_state": "ready_for_confirmation",
            "confirmation": {"state": "pending"},
            "facts": [
                {"fact_id": "target", "value": "test", "source": {"kind": "user"}},
            ],
        }
        self.assertEqual([], validator.validate_profile(valid))

        invalid = {
            **valid,
            "facts": [
                {
                    "fact_id": "runtime",
                    "value": "deployed",
                    "source": {"kind": "runtime-preflight"},
                }
            ],
            "credentials": [{"source_ref": "https://user:password@example.test"}],
            "build_id": "build-123",
        }
        errors = validator.validate_profile(invalid)
        self.assertTrue(any("dynamic runtime field" in error for error in errors))
        self.assertTrue(any("static Environment Profile fact source" in error for error in errors))
        self.assertTrue(any("secret-bearing field" in error or "secret-like value" in error for error in errors))

    def test_validator_requires_matching_confirmation_hash(self) -> None:
        validator = load_validator()
        profile = {
            "version": 1,
            "profile_kind": "environment",
            "profile_id": "confirmed-test",
            "profile_revision": 2,
            "content_hash": "sha256:new",
            "profile_state": "confirmed",
            "confirmation": {
                "state": "confirmed",
                "confirmed_revision": 2,
                "confirmed_content_hash": "sha256:old",
            },
        }
        errors = validator.validate_profile(profile)
        self.assertIn("confirmed_content_hash must match content_hash", errors)

    def test_validator_cli_validates_a_profile_file(self) -> None:
        profile = {
            "version": 1,
            "profile_kind": "environment",
            "profile_id": "cli-test",
            "profile_revision": 1,
            "content_hash": "sha256:abc",
            "profile_state": "draft",
            "confirmation": {"state": "pending"},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "environment.profile.yaml"
            path.write_text(yaml.safe_dump(profile, sort_keys=False), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(VALIDATOR), str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Profile validation passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
