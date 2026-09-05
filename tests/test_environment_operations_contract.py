from __future__ import annotations

import importlib.util
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from tests._support import ROOT, read

SKILL = ROOT / "skills/environment-operations/SKILL.md"
GENERATOR = ROOT / "skills/environment-operations/scripts/generate_operation_skill.py"


def load_generator():
    spec = importlib.util.spec_from_file_location("operation_skill_generator", GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load operation Skill generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def confirmed_profile(root: Path, *, command: list[str]) -> Path:
    profile = {
        "version": 1,
        "profile_kind": "environment",
        "profile_id": "local-profile",
        "profile_revision": 1,
        "content_hash": "sha256:" + "a" * 64,
        "profile_state": "confirmed",
        "environment": {"kind": "local"},
        "declaration": {"source": "user", "statement": "user-declared"},
        "confirmation": {"state": "confirmed", "confirmed_revision": 1, "confirmed_content_hash": "sha256:" + "a" * 64},
        "test_context": {"authorization": {"mode": "per-invocation", "approved_scopes": []}, "configuration": {"env_file": {"path": ".env", "required": False, "ignored_by_vcs": "required", "file_mode": "0600", "required_variables": []}}},
        "security": {"persist_secrets": False, "expose_secrets_to_model": False, "credential_values_allowed": False, "credential_refs_only": True},
        "operations": [
            {"operation_id": "local-build", "category": "build", "purpose": "build", "executor": "local-operator", "working_directory_ref": "project-root", "argv": command, "authorization": "explicit-per-invocation", "risk": "guarded", "mutates": True, "required_evidence": ["command-exit-status"]},
            {"operation_id": "local-service-start", "category": "start", "purpose": "start", "executor": "local-operator", "working_directory_ref": "project-root", "argv": command, "authorization": "explicit-per-invocation", "risk": "guarded", "mutates": True, "ownership": "profile-owned", "required_evidence": ["process-observation"]},
            {"operation_id": "local-service-stop", "category": "stop", "purpose": "stop", "executor": "local-operator", "working_directory_ref": "project-root", "argv": command, "authorization": "explicit-per-invocation", "risk": "guarded", "mutates": True, "ownership": "profile-owned", "required_evidence": ["process-observation"]},
        ],
    }
    path = root / ".bruce/environments/local-profile.profile.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(profile, sort_keys=False), encoding="utf-8")
    return path


class EnvironmentOperationsContractTest(unittest.TestCase):
    def test_skill_generates_executable_project_artifacts_not_manifest(self) -> None:
        body = " ".join(read("skills/environment-operations/SKILL.md").split())
        for phrase in (
            "executable project-local Skill",
            "bounded runner script",
            "does **not** generate `operations.yaml`",
            "existing Skill check",
            "Never overwrite an existing non-Bruce-owned Skill",
            "Makefile target",
            "run_operation.py",
            "--confirm",
            "Verification Run/Checkpoint",
        ):
            self.assertIn(phrase, body)
        self.assertFalse((ROOT / "skills/environment-operations/templates/operation-manifest.yaml").exists())
        self.assertFalse((ROOT / "skills/environment-operations/scripts/validate_operation_manifest.py").exists())

    def test_generator_creates_skill_and_runner_from_confirmed_profile(self) -> None:
        generator = load_generator()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profile = confirmed_profile(root, command=[sys.executable, "-c", "print('ok')"])
            skill_root = root / ".codex/skills"
            output = generator.generate(profile, root, skill_root, None, False)
            skill = output / "SKILL.md"
            runner = output / "scripts/run_operation.py"
            metadata = output / "agents/openai.yaml"
            self.assertEqual((root / ".codex/skills/local-profile-operations").resolve(), output)
            self.assertTrue(skill.is_file())
            self.assertTrue(runner.is_file())
            self.assertTrue(metadata.is_file())
            self.assertEqual(0o755, stat.S_IMODE(runner.stat().st_mode))
            generated = skill.read_text(encoding="utf-8")
            self.assertIn("local-service-start", generated)
            self.assertIn("local-service-stop", generated)
            self.assertIn("local-build", generated)
            self.assertIn("EXPECTED_CONTENT_HASH", runner.read_text(encoding="utf-8"))

            blocked = subprocess.run([sys.executable, str(runner), "--operation", "local-build"], cwd=root, capture_output=True, text=True)
            self.assertEqual(2, blocked.returncode)
            self.assertIn("requires --confirm", blocked.stderr)
            executed = subprocess.run([sys.executable, str(runner), "--operation", "local-build", "--confirm"], cwd=root, capture_output=True, text=True)
            self.assertEqual(0, executed.returncode, executed.stderr)
            self.assertIn('"exit_code": 0', executed.stdout)
            profile.write_text(profile.read_text(encoding="utf-8") + "# changed after generation\n", encoding="utf-8")
            stale = subprocess.run([sys.executable, str(runner), "--operation", "local-build", "--confirm"], cwd=root, capture_output=True, text=True)
            self.assertEqual(2, stale.returncode)
            self.assertIn("Profile file changed", stale.stderr)

    def test_generator_rejects_unconfirmed_profile_and_unowned_existing_skill(self) -> None:
        generator = load_generator()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profile = confirmed_profile(root, command=[sys.executable, "-c", "print('ok')"])
            data = yaml.safe_load(profile.read_text(encoding="utf-8"))
            data["profile_state"] = "draft"
            data["confirmation"]["state"] = "pending"
            profile.write_text(yaml.safe_dump(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must be confirmed"):
                generator.generate(profile, root, root / ".codex/skills", None, False)

            profile = confirmed_profile(root, command=[sys.executable, "-c", "print('ok')"])
            target = root / ".codex/skills/local-profile-operations"
            target.mkdir(parents=True)
            (target / "SKILL.md").write_text("---\nname: hand-written\n---\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unowned"):
                generator.generate(profile, root, root / ".codex/skills", None, False)

    def test_profile_confirmed_operations_do_not_prompt_again(self) -> None:
        generator = load_generator()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profile = confirmed_profile(root, command=[sys.executable, "-c", "print('ok')"])
            data = yaml.safe_load(profile.read_text(encoding="utf-8"))
            data["test_context"] = {
                "authorization": {
                    "mode": "profile-confirmed",
                    "approved_scopes": ["build"],
                    "escalation_required_for": ["database-drop"],
                },
                "configuration": {
                    "env_file": {"path": ".env", "required": False, "required_variables": [], "file_mode": "0600", "ignored_by_vcs": "required"},
                },
            }
            data["operations"][0]["authorization"] = "profile-confirmed"
            profile.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
            output = generator.generate(profile, root, root / ".codex/skills", None, False)
            result = subprocess.run([sys.executable, str(output / "scripts/run_operation.py"), "--operation", "local-build"], cwd=root, capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn('"exit_code": 0', result.stdout)

    def test_profile_escalation_overrides_routine_profile_authorization(self) -> None:
        generator = load_generator()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profile = confirmed_profile(root, command=[sys.executable, "-c", "print('ok')"])
            data = yaml.safe_load(profile.read_text(encoding="utf-8"))
            data["test_context"] = {
                "authorization": {
                    "mode": "profile-confirmed",
                    "approved_scopes": ["build"],
                    "escalation_required_for": ["build"],
                },
                "configuration": {
                    "env_file": {"path": ".env", "required": False, "required_variables": [], "file_mode": "0600", "ignored_by_vcs": "required"},
                },
            }
            data["operations"][0]["authorization"] = "profile-confirmed"
            profile.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
            output = generator.generate(profile, root, root / ".codex/skills", None, False)
            blocked = subprocess.run([sys.executable, str(output / "scripts/run_operation.py"), "--operation", "local-build"], cwd=root, capture_output=True, text=True)
            self.assertEqual(2, blocked.returncode)
            self.assertIn("requires --confirm", blocked.stderr)
            executed = subprocess.run([sys.executable, str(output / "scripts/run_operation.py"), "--operation", "local-build", "--confirm"], cwd=root, capture_output=True, text=True)
            self.assertEqual(0, executed.returncode, executed.stderr)

    def test_generated_runner_loads_dotenv_without_printing_values(self) -> None:
        generator = load_generator()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profile = confirmed_profile(root, command=[sys.executable, "-c", "import os; print(os.environ['LOCAL_TOKEN'])"])
            data = yaml.safe_load(profile.read_text(encoding="utf-8"))
            data["test_context"]["configuration"]["env_file"]["required"] = True
            data["test_context"]["configuration"]["env_file"]["required_variables"] = ["LOCAL_TOKEN"]
            profile.write_text(yaml.safe_dump(data), encoding="utf-8")
            env = root / ".env"
            env.write_text("LOCAL_TOKEN=not-for-output\n", encoding="utf-8")
            os.chmod(env, 0o600)
            output = generator.generate(profile, root, root / ".codex/skills", None, False)
            result = subprocess.run([sys.executable, str(output / "scripts/run_operation.py"), "--operation", "local-build", "--confirm"], cwd=root, capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertNotIn("not-for-output", result.stdout)
            self.assertIn("<redacted>", result.stdout)


if __name__ == "__main__":
    unittest.main()
