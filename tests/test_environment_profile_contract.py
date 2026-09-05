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
            "Agent testing and verification",
            "authorization contract",
            "Candidate discovery",
            "Repository inspection is used only to form candidates",
            "$inspect-parallel",
            "confirmation",
            "state: pending",
            "ready_for_confirmation",
            "needs_input",
            "user-owned data or authorization boundaries",
            "account pools",
            "credential references",
            "never record values",
            "preflight",
            "exact confirmation",
            "does not execute build",
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
            "Repository inspection produces candidates only",
            "An optional `facts` list",
            "empty values only",
            "preflight",
            "never stores passwords",
            "Verification Run/Checkpoint",
            "Completion verdict",
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
            "content_hash": "sha256:" + "a" * 64,
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

    def test_template_declares_compact_agent_test_context(self) -> None:
        template = yaml.safe_load(read("skills/environment-profile/templates/environment-profile.yaml"))
        for key in ("test_context", "operations", "freshness", "security"):
            self.assertIn(key, template)
        context = template["test_context"]
        for key in ("scope", "authorization", "workflow", "services", "data", "authentication", "configuration", "preflight"):
            self.assertIn(key, context)
        self.assertEqual("profile-confirmed", context["authorization"]["mode"])
        self.assertNotIn("operation_manifest", template)
        self.assertNotIn("confirmation_summary", template)
        self.assertNotIn("capabilities", template)
        self.assertNotIn("operations.yaml", read("skills/environment-profile/templates/environment-profile.yaml"))

    def test_profile_contract_uses_one_confirmed_scope_for_routine_operations(self) -> None:
        body = " ".join(read("skills/environment-profile/SKILL.md").split())
        self.assertIn("one confirmation, one test scope", body)
        self.assertIn("must not ask the user to approve every build", body)
        self.assertIn("profile-confirmed", body)

        validator = load_validator()
        profile = {
            "version": 1,
            "profile_kind": "environment",
            "profile_id": "profile-authorized",
            "profile_revision": 1,
            "content_hash": "sha256:abc",
            "profile_state": "draft",
            "confirmation": {"state": "pending"},
            "declaration": {"source": "user", "statement": "user-declared environment"},
            "test_context": {
                "authorization": {"mode": "profile-confirmed", "approved_scopes": ["build"]},
            },
            "operations": [{
                "operation_id": "build", "category": "build", "executor": "local-process",
                "authorization": "profile-confirmed", "risk": "guarded", "argv": ["make", "build"],
            }],
        }
        self.assertEqual([], validator.validate_profile(profile))

    def test_validator_accepts_new_local_env_location_without_legacy_duplicate(self) -> None:
        validator = load_validator()
        profile = {
            "version": 1, "profile_kind": "environment", "profile_id": "new-local",
            "profile_revision": 1, "content_hash": "sha256:pending", "profile_state": "draft",
            "confirmation": {"state": "pending"},
            "declaration": {"source": "user", "statement": "user-declared"},
            "environment": {"kind": "local"},
            "test_context": {"authorization": {"mode": "profile-confirmed", "approved_scopes": []}, "configuration": {"env_file": {
                "path": ".env", "required": False, "required_variables": [],
                "file_mode": "0600", "ignored_by_vcs": "required",
            }}},
            "security": {"persist_secrets": False, "expose_secrets_to_model": False, "credential_values_allowed": False, "credential_refs_only": True},
            "operations": [],
        }
        self.assertEqual([], validator.validate_profile(profile))
        profile["local_env"] = profile["test_context"]["configuration"]["env_file"]
        self.assertTrue(any("must not duplicate .env metadata" in error for error in validator.validate_profile(profile)))

    def test_validator_rejects_unresolved_or_duplicate_operations(self) -> None:
        validator = load_validator()
        profile = {
            "version": 1, "profile_kind": "environment", "profile_id": "refs",
            "profile_revision": 1, "content_hash": "sha256:pending", "profile_state": "draft",
            "confirmation": {"state": "pending"},
            "declaration": {"source": "user", "statement": "user-declared"},
            "test_context": {"workflow": {"test_operation": "missing"}},
            "operations": [
                {"operation_id": "same", "category": "test", "executor": "local-process", "authorization": "explicit-per-invocation", "risk": "guarded", "argv": ["pytest"]},
                {"operation_id": "same", "category": "test", "executor": "local-process", "authorization": "explicit-per-invocation", "risk": "guarded", "argv": ["pytest"]},
            ],
        }
        errors = validator.validate_profile(profile)
        self.assertTrue(any("operation_id must be unique" in error for error in errors))
        self.assertTrue(any("undeclared operation" in error for error in errors))

    def test_validator_requires_real_hash_for_ready_profile(self) -> None:
        validator = load_validator()
        profile = {
            "version": 1, "profile_kind": "environment", "profile_id": "hashed",
            "profile_revision": 1, "content_hash": "sha256:abc", "profile_state": "ready_for_confirmation",
            "confirmation": {"state": "pending"},
            "declaration": {"source": "user", "statement": "user-declared"},
            "operations": [],
        }
        self.assertTrue(any("content_hash must be sha256:<64 lowercase hex characters>" in error for error in validator.validate_profile(profile)))

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
