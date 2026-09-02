from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import stat
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from tests._support import ROOT, read


VALIDATOR = ROOT / "skills/environment-profile/scripts/validate_profile.py"
ENV_CHECKER = ROOT / "skills/environment-profile/scripts/check_local_env.py"
CREATE_ENV = ROOT / "skills/environment-profile/scripts/create_local_env.py"


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
            "user-provided and user-confirmed environment information",
            "user-confirmed environment declaration",
            "Repository-assisted candidate discovery",
            "candidates only",
            "$inspect-parallel",
            "confirmation",
            "state: pending",
            "ready_for_confirmation",
            "needs_input",
            "unresolved questions",
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
            "Repository and project-document sources are not valid Environment Profile fact sources",
            "accepted after Bruce presents repository-derived candidates",
            "empty values for safe candidate variable names",
            "runtime preflight",
            "secret value",
            "Verification Run/Checkpoint",
            "completion verdict",
            "profile_state",
        ):
            self.assertIn(phrase, normalized)
        self.assertIn("must not contain", normalized.lower())

    def test_local_env_template_creates_empty_owner_only_ignored_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            result = subprocess.run(
                [sys.executable, str(CREATE_ENV), str(root), "--template", "--required", "LOCAL_TOKEN", "--required", "DB_HOST"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            env_path = root / ".env"
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue(env_path.is_file())
            self.assertEqual(0o600, stat.S_IMODE(env_path.stat().st_mode))
            self.assertEqual(
                "# Local Environment Profile values. Fill locally; do not commit.\nDB_HOST=\nLOCAL_TOKEN=\n",
                env_path.read_text(encoding="utf-8"),
            )
            self.assertIn(".env", (root / ".gitignore").read_text(encoding="utf-8"))
            self.assertIn(".bruce-env-*", (root / ".gitignore").read_text(encoding="utf-8"))
            self.assertEqual(0, subprocess.run(["git", "check-ignore", "--quiet", ".env"], cwd=root, check=False).returncode)

    def test_local_env_template_allows_no_candidate_names(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = subprocess.run(
                [sys.executable, str(CREATE_ENV), str(root), "--template"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(
                "# Local Environment Profile values. Fill locally; do not commit.\n",
                (root / ".env").read_text(encoding="utf-8"),
            )

    def test_local_env_template_refuses_to_overwrite_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            existing = root / ".env"
            existing.write_text("UNCHANGED=1\n", encoding="utf-8")
            os.chmod(existing, 0o600)
            result = subprocess.run(
                [sys.executable, str(CREATE_ENV), str(root), "--template", "--required", "LOCAL_TOKEN"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(1, result.returncode)
            self.assertIn("env-file-already-exists", result.stdout)
            self.assertEqual("UNCHANGED=1\n", existing.read_text(encoding="utf-8"))

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
            "declaration": {"source": "user", "statement": "user-declared test environment"},
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
        self.assertTrue(any("Environment Profile fact source must be user" in error for error in errors))
        self.assertTrue(any("secret-bearing field" in error or "secret-like value" in error for error in errors))

    def test_template_declares_environment_topology_and_operation_declarations(self) -> None:
        template = yaml.safe_load(read("skills/environment-profile/templates/environment-profile.yaml"))
        for key in ("deployment", "build", "lifecycle", "dependencies", "network", "identities", "data_policy", "configuration", "operations"):
            self.assertIn(key, template)
        self.assertNotIn("operation_manifest", template)
        self.assertNotIn("operations.yaml", read("skills/environment-profile/templates/environment-profile.yaml"))

    def test_validator_rejects_unsafe_profile_operations(self) -> None:
        validator = load_validator()
        profile = {
            "version": 1,
            "profile_kind": "environment",
            "profile_id": "unsafe-operations",
            "profile_revision": 1,
            "content_hash": "sha256:abc",
            "profile_state": "draft",
            "confirmation": {"state": "pending"},
            "declaration": {"source": "user", "statement": "user-declared environment"},
            "operations": [{
                "operation_id": "reset", "category": "reset", "executor": "local-process",
                "authorization": "none", "risk": "critical", "argv": ["TOKEN=not-for-output"],
            }, {
                "operation_id": "build", "category": "build", "executor": "local-process",
                "authorization": "none", "risk": "read-only",
            }],
        }
        errors = validator.validate_profile(profile)
        self.assertTrue(any("category requires at least guarded risk" in error for error in errors))
        self.assertTrue(any("critical operation requires explicit authorization" in error for error in errors))
        self.assertTrue(any("critical operation requires target" in error for error in errors))
        self.assertTrue(any("argv must not contain secret assignments" in error for error in errors))



if __name__ == "__main__":
    unittest.main()
