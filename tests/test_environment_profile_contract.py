from __future__ import annotations

import importlib.util
import json
import os
import subprocess
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
            "user environment declaration",
            "not a repository scan",
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
            "Repository and project-document sources are not valid Environment Profile fact sources",
            "user-provided and user-confirmed",
            "runtime preflight",
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

    def test_agent_prompt_describes_user_declared_profile(self) -> None:
        metadata = read("skills/environment-profile/agents/openai.yaml")
        self.assertIn("user-provided", metadata)
        self.assertIn("without scanning repository implementation files", metadata)
        self.assertNotIn("repository-grounded", metadata)

    def test_template_is_user_declared_and_has_no_source_of_truth(self) -> None:
        template = yaml.safe_load(read("skills/environment-profile/templates/environment-profile.yaml"))
        self.assertEqual("user", template["declaration"]["source"])
        self.assertNotIn("source_of_truth", template)
        self.assertEqual("user-declaration-and-selected-reference-revisions", template["freshness"]["basis"])

    def test_validator_rejects_repository_facts_and_repository_metadata(self) -> None:
        validator = load_validator()
        profile = {
            "version": 1,
            "profile_kind": "environment",
            "profile_id": "repository-backed",
            "profile_revision": 1,
            "content_hash": "sha256:abc",
            "profile_state": "draft",
            "confirmation": {"state": "pending"},
            "source_of_truth": [{"path": "backend/cmd/server/main.go"}],
            "facts": [{"fact_id": "implementation", "source": {"kind": "repository", "path": "backend/cmd/server/main.go", "revision": "current"}}],
        }
        errors = validator.validate_profile(profile)
        self.assertIn("Environment Profile must not contain repository metadata: source_of_truth", errors)
        self.assertTrue(any("fact source must be user" in error for error in errors))
        self.assertTrue(any("must not contain repository source metadata" in error for error in errors))

        user_profile = {**profile}
        user_profile.pop("source_of_truth")
        user_profile["declaration"] = {"source": "user", "statement": "user-declared environment"}
        user_profile["facts"] = [{"fact_id": "declared", "source": {"kind": "user"}}]
        self.assertEqual([], validator.validate_profile(user_profile))

        bypass = {
            **user_profile,
            "facts": [{"fact_id": "declared", "source": {"kind": "user"}, "implementation_path": "backend/main.go"}],
            "test_scenarios": [{"name": "scenario"}],
            "local_env": {"path": ".env", "required": True, "ignored_by_vcs": "required", "file_mode": "0600", "required_variables": [], "values": {"TOKEN": "hidden"}},
            "credentials": [{"secret_value_persisted": False, "expose_to_model": False, "redact_logs": True, "raw_value": "hidden"}],
        }
        bypass_errors = validator.validate_profile(bypass)
        self.assertTrue(any("implementation_path" in error for error in bypass_errors))
        self.assertTrue(any("test_scenarios" in error for error in bypass_errors))
        self.assertTrue(any("local_env field is not allowed: values" in error for error in bypass_errors))
        self.assertTrue(any("credentials[0] field is not allowed: raw_value" in error for error in bypass_errors))

    def test_validator_rejects_facts_without_user_source(self) -> None:
        validator = load_validator()
        profile = {
            "version": 1,
            "profile_kind": "environment",
            "profile_id": "missing-source",
            "profile_revision": 1,
            "content_hash": "sha256:abc",
            "profile_state": "draft",
            "confirmation": {"state": "pending"},
            "declaration": {"source": "user", "statement": "user-declared environment"},
            "facts": [{"fact_id": "missing-source"}],
        }
        errors = validator.validate_profile(profile)
        self.assertIn("facts[0].source must be a mapping with kind=user", errors)

    def test_validator_enforces_local_env_and_credential_security_flags(self) -> None:
        validator = load_validator()
        profile = {
            "version": 1,
            "profile_kind": "environment",
            "profile_id": "unsafe-local-env",
            "profile_revision": 1,
            "content_hash": "sha256:abc",
            "profile_state": "draft",
            "confirmation": {"state": "pending"},
            "security": {
                "persist_secrets": True,
                "expose_secrets_to_model": True,
                "credential_values_allowed": True,
                "credential_refs_only": False,
            },
            "local_env": {"path": "other.env", "ignored_by_vcs": "optional", "required_variables": ["bad-name"]},
            "credentials": [{"secret_value_persisted": True, "expose_to_model": True, "redact_logs": False}],
        }
        errors = validator.validate_profile(profile)
        for expected in (
            "security.persist_secrets must be false",
            "security.expose_secrets_to_model must be false",
            "security.credential_values_allowed must be false",
            "security.credential_refs_only must be true",
            "local_env.path must be .env",
            "local_env.ignored_by_vcs must be required",
            "local_env.required_variables[0] must be a valid environment variable name",
            "credentials[0].secret_value_persisted must be false",
            "credentials[0].expose_to_model must be false",
            "credentials[0].redact_logs must be true",
        ):
            self.assertIn(expected, errors)

    def test_validator_requires_local_profile_security_fields(self) -> None:
        validator = load_validator()
        profile = {
            "version": 1,
            "profile_kind": "environment",
            "profile_id": "local-profile",
            "profile_revision": 1,
            "content_hash": "sha256:abc",
            "profile_state": "draft",
            "confirmation": {"state": "pending"},
            "declaration": {"source": "user", "statement": "user-declared local environment"},
            "environment": {"kind": "local"},
        }
        errors = validator.validate_profile(profile)
        self.assertIn("local Environment Profile requires security mapping", errors)
        self.assertIn("local Environment Profile requires local_env mapping", errors)

        profile["security"] = {
            "persist_secrets": False,
            "expose_secrets_to_model": False,
            "credential_values_allowed": False,
            "credential_refs_only": True,
        }
        profile["local_env"] = {
            "path": ".env",
            "required": True,
            "ignored_by_vcs": "required",
            "file_mode": "0644",
            "required_variables": [],
        }
        errors = validator.validate_profile(profile)
        self.assertIn("local_env.file_mode must be 0600", errors)

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
            "declaration": {"source": "user", "statement": "user-declared environment"},
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


    def test_skill_requires_local_env_bootstrap_without_model_exposure(self) -> None:
        body = read("skills/environment-profile/SKILL.md")
        normalized = " ".join(body.split())
        for phrase in (
            "Local `.env` bootstrap",
            "project-root `.env`",
            "check_local_env.py",
            "missing variable names",
            "ensure the project `.gitignore` contains the exact `.env` entry",
            "owner-only permissions",
            "create_local_env.py",
            "hidden prompts",
            "ordinary chat",
            "do not echo the submitted values",
            "A successful `.env` check proves only local configuration presence",
        ):
            self.assertIn(phrase, normalized)

    def test_template_declares_local_env_safety_contract(self) -> None:
        template = yaml.safe_load(read("skills/environment-profile/templates/environment-profile.yaml"))
        self.assertEqual(".env", template["local_env"]["path"])
        self.assertEqual("required", template["local_env"]["ignored_by_vcs"])
        self.assertEqual("0600", template["local_env"]["file_mode"])
        self.assertEqual([], template["local_env"]["required_variables"])
        ignored_lines = read(".gitignore").splitlines()
        self.assertIn(".env", ignored_lines)
        self.assertIn(".bruce-env-*", ignored_lines)

    def test_local_env_checker_reports_missing_names_without_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = subprocess.run(
                [sys.executable, str(ENV_CHECKER), str(root), "--required", "BRUCE_TEST_PASSWORD"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(2, result.returncode, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(["BRUCE_TEST_PASSWORD"], report["missing_required_names"])
        self.assertNotIn("value", report)
        self.assertNotIn("password", report)

    def test_local_env_checker_accepts_ignored_owner_only_complete_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            (root / ".gitignore").write_text(".env\n", encoding="utf-8")
            env_path = root / ".env"
            env_path.write_text("BRUCE_TEST_PASSWORD=not-for-output\n", encoding="utf-8")
            os.chmod(env_path, 0o600)
            result = subprocess.run(
                [sys.executable, str(ENV_CHECKER), str(root), "--required", "BRUCE_TEST_PASSWORD"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(0, result.returncode, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["usable"])
        self.assertTrue(report["ignored"])
        self.assertFalse(report["tracked"])
        self.assertTrue(report["owner_is_current_user"])
        self.assertNotIn("not-for-output", result.stdout)

    def test_local_env_creator_preserves_entries_and_writes_owner_only_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            (root / ".gitignore").write_text(".env\n", encoding="utf-8")
            env_path = root / ".env"
            env_path.write_text("EXISTING=value\n", encoding="utf-8")
            os.chmod(env_path, 0o600)
            result = subprocess.run(
                [sys.executable, str(CREATE_ENV), str(root), "--required", "BRUCE_TEST_TOKEN"],
                input="created-secret\n",
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(0o600, os.stat(env_path).st_mode & 0o777)
            contents = env_path.read_text(encoding="utf-8")
            self.assertIn("EXISTING=value", contents)
            self.assertIn("BRUCE_TEST_TOKEN=created-secret", contents)
            self.assertNotIn("created-secret", result.stdout)
            self.assertNotIn("created-secret", result.stderr)

    def test_local_env_creator_refuses_insecure_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            (root / ".gitignore").write_text(".env\n", encoding="utf-8")
            env_path = root / ".env"
            env_path.write_text("EXISTING=value\n", encoding="utf-8")
            os.chmod(env_path, 0o644)
            result = subprocess.run(
                [sys.executable, str(CREATE_ENV), str(root), "--required", "BRUCE_TEST_TOKEN"],
                input="created-secret\n",
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(1, result.returncode)
        self.assertIn("permissions-too-open", result.stdout)
        self.assertNotIn("created-secret", result.stdout)
        self.assertNotIn("created-secret", result.stderr)

    def test_local_env_checker_reports_existing_incomplete_env(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            (root / ".gitignore").write_text(".env\n", encoding="utf-8")
            env_path = root / ".env"
            env_path.write_text("OTHER=value\n", encoding="utf-8")
            os.chmod(env_path, 0o600)
            result = subprocess.run(
                [sys.executable, str(ENV_CHECKER), str(root), "--required", "BRUCE_TEST_TOKEN"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(2, result.returncode)
        report = json.loads(result.stdout)
        self.assertEqual(["BRUCE_TEST_TOKEN"], report["missing_required_names"])
        self.assertFalse(report["usable"])
        self.assertNotIn("value", result.stdout)

    def test_local_env_checker_rejects_unignored_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            env_path = root / ".env"
            env_path.write_text("BRUCE_TEST_TOKEN=not-for-output\n", encoding="utf-8")
            os.chmod(env_path, 0o600)
            result = subprocess.run(
                [sys.executable, str(ENV_CHECKER), str(root), "--required", "BRUCE_TEST_TOKEN"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(3, result.returncode)
        report = json.loads(result.stdout)
        self.assertFalse(report["usable"])
        self.assertFalse(report["ignored"])
        self.assertFalse(report["tracked"])
        self.assertNotIn("not-for-output", result.stdout)

    def test_local_env_checker_rejects_symlinked_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            (root / ".gitignore").write_text(".env\n", encoding="utf-8")
            outside = root / "outside.env"
            outside.write_text("BRUCE_TEST_TOKEN=not-for-output\n", encoding="utf-8")
            (root / ".env").symlink_to(outside)
            result = subprocess.run(
                [sys.executable, str(ENV_CHECKER), str(root), "--required", "BRUCE_TEST_TOKEN"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(3, result.returncode, result.stderr)
        report = json.loads(result.stdout)
        self.assertFalse(report["usable"])
        self.assertTrue(report["symlink"])
        self.assertNotIn("not-for-output", result.stdout)

    def test_local_env_checker_rejects_tracked_or_world_readable_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            env_path = root / ".env"
            env_path.write_text("BRUCE_TEST_TOKEN=not-for-output\n", encoding="utf-8")
            os.chmod(env_path, 0o644)
            subprocess.run(["git", "add", ".env"], cwd=root, check=True)
            result = subprocess.run(
                [sys.executable, str(ENV_CHECKER), str(root), "--required", "BRUCE_TEST_TOKEN"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(3, result.returncode, result.stderr)
        report = json.loads(result.stdout)
        self.assertFalse(report["usable"])
        self.assertTrue(report["tracked"])
        self.assertFalse(report["owner_only_permissions"])
        self.assertNotIn("not-for-output", result.stdout)


if __name__ == "__main__":
    unittest.main()
