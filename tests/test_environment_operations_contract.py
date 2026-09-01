from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from tests._support import ROOT, read

SKILL = ROOT / "skills/environment-operations/SKILL.md"
TEMPLATE = ROOT / "skills/environment-operations/templates/operation-manifest.yaml"
VALIDATOR = ROOT / "skills/environment-operations/scripts/validate_operation_manifest.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("operation_manifest_validator", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load operation manifest validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EnvironmentOperationsContractTest(unittest.TestCase):
    def test_skill_requires_confirmed_profile_and_keeps_operations_bounded(self) -> None:
        body = " ".join(read("skills/environment-operations/SKILL.md").split())
        for phrase in (
            "confirmed Environment Profile",
            "Environment Operation Manifest",
            "does not dynamically register a project-level",
            "Do not infer commands",
            "critical",
            "Verification Run/Checkpoint",
        ):
            self.assertIn(phrase, body)

    def test_manifest_template_is_unconfirmed_and_secret_safe(self) -> None:
        data = yaml.safe_load(TEMPLATE.read_text(encoding="utf-8"))
        self.assertEqual("environment-operation", data["manifest_kind"])
        self.assertFalse(data["declaration"]["confirmed"])
        self.assertFalse(data["security"]["secret_values_allowed"])
        self.assertTrue(data["runtime"]["preflight_required"])

    def test_validator_accepts_bounded_read_only_operation(self) -> None:
        validator = load_validator()
        manifest = yaml.safe_load(TEMPLATE.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profile = {
                "version": 1,
                "profile_kind": "environment",
                "profile_id": "local-profile",
                "profile_revision": 1,
                "content_hash": "sha256:abc",
                "profile_state": "confirmed",
                "declaration": {"source": "user", "statement": "user-declared"},
                "confirmation": {
                    "state": "confirmed",
                    "confirmed_revision": 1,
                    "confirmed_content_hash": "sha256:abc",
                },
                "operations": [{"operation_id": "status", "category": "status", "executor": "local-read-only", "authorization": "none", "risk": "read-only"}],
            }
            profile_path = root / "profile.yaml"
            profile_path.write_text(yaml.safe_dump(profile), encoding="utf-8")
            manifest.update({
                "manifest_id": "local-ops",
                "profile_ref": {
                    "path": str(profile_path),
                    "profile_id": "local-profile",
                    "profile_revision": 1,
                    "profile_content_hash": "sha256:abc",
                },
                "declaration": {"source": "environment-profile", "confirmed": True},
                "operations": ["status"],
            })
            self.assertEqual([], validator.validate_manifest(manifest))

    def test_validator_rejects_unsafe_or_underdeclared_operations(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profile = {
                "version": 1, "profile_kind": "environment", "profile_id": "local-profile",
                "profile_revision": 1, "content_hash": "sha256:abc", "profile_state": "confirmed",
                "declaration": {"source": "user", "statement": "user-declared"},
                "confirmation": {"state": "confirmed", "confirmed_revision": 1, "confirmed_content_hash": "sha256:abc"},
                "operations": [{"operation_id": "status", "category": "status", "executor": "local-read-only", "authorization": "none", "risk": "read-only"}],
            }
            profile_path = root / "profile.yaml"
            profile_path.write_text(yaml.safe_dump(profile), encoding="utf-8")
            manifest = yaml.safe_load(TEMPLATE.read_text(encoding="utf-8"))
            manifest.update({
                "manifest_id": "unsafe-ops",
                "profile_ref": {"path": str(profile_path), "profile_id": "local-profile", "profile_revision": 1, "profile_content_hash": "sha256:abc"},
                "declaration": {"source": "environment-profile", "confirmed": True},
                "operations": ["reset"],
                "raw_value": "not-for-output",
            })
            errors = validator.validate_manifest(manifest)
        self.assertTrue(any("operations[0] is not declared by source Environment Profile" in error for error in errors))
        self.assertTrue(any("forbidden manifest field: raw_value" in error for error in errors))

    def test_validator_rejects_unconfirmed_mismatched_or_downgraded_source_operations(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profile = {
                "version": 1,
                "profile_kind": "environment",
                "profile_id": "local-profile",
                "profile_revision": 1,
                "content_hash": "sha256:abc",
                "profile_state": "confirmed",
                "declaration": {"source": "user", "statement": "user-declared"},
                "confirmation": {
                    "state": "confirmed",
                    "confirmed_revision": 1,
                    "confirmed_content_hash": "sha256:abc",
                },
                "operations": [{
                    "operation_id": "build",
                    "category": "build",
                    "executor": "local-process",
                    "authorization": "per-invocation",
                    "risk": "guarded",
                }],
            }
            profile_path = root / "profile.yaml"
            profile_path.write_text(yaml.safe_dump(profile), encoding="utf-8")
            manifest = yaml.safe_load(TEMPLATE.read_text(encoding="utf-8"))
            manifest.update({
                "manifest_id": "local-ops",
                "profile_ref": {"path": str(profile_path), "profile_id": "local-profile", "profile_revision": 1, "profile_content_hash": "sha256:wrong"},
                "declaration": {"source": "environment-profile", "confirmed": True},
                "operations": ["build"],
            })
            errors = validator.validate_manifest(manifest)
            self.assertIn("profile_ref.profile_content_hash must match source Environment Profile", errors)
            self.assertIn("profile_ref.profile_content_hash must match source Environment Profile", errors)

            profile["profile_state"] = "needs_input"
            profile["confirmation"]["state"] = "pending"
            profile_path.write_text(yaml.safe_dump(profile), encoding="utf-8")
            errors = validator.validate_manifest(manifest)
        self.assertIn("source Environment Profile must be confirmed", errors)
        self.assertIn("source Environment Profile confirmation.state must be confirmed", errors)

    def test_validator_cli_does_not_execute_manifest(self) -> None:
        manifest = yaml.safe_load(TEMPLATE.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profile = {
                "version": 1,
                "profile_kind": "environment",
                "profile_id": "cli-profile",
                "profile_revision": 1,
                "content_hash": "sha256:abc",
                "profile_state": "confirmed",
                "declaration": {"source": "user", "statement": "user-declared"},
                "confirmation": {
                    "state": "confirmed",
                    "confirmed_revision": 1,
                    "confirmed_content_hash": "sha256:abc",
                },
                "operations": [],
            }
            profile_path = root / "profile.yaml"
            profile_path.write_text(yaml.safe_dump(profile), encoding="utf-8")
            manifest.update({
                "manifest_id": "cli-ops",
                "profile_ref": {
                    "path": "profile.yaml",
                    "profile_id": "cli-profile",
                    "profile_revision": 1,
                    "profile_content_hash": "sha256:abc",
                },
                "declaration": {"source": "environment-profile", "confirmed": True},
            })
            path = root / "manifest.yaml"
            path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
            result = subprocess.run([sys.executable, str(VALIDATOR), str(path)], cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Manifest validation passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
