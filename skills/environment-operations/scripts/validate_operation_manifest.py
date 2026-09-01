#!/usr/bin/env python3
"""Validate a static Environment Operation Manifest without executing it."""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path
from typing import Any

import yaml

SECRET_PATTERN = re.compile(
    r"(?:bearer\s+eyJ|https?://[^\s/@]+:[^\s/@]+@|-----BEGIN .* PRIVATE KEY-----|sk-[A-Za-z0-9_-]{12,})",
    re.IGNORECASE,
)
FORBIDDEN_KEYS = {
    "password", "passwd", "api_key", "secret", "secret_value", "token", "access_token",
    "refresh_token", "jwt", "cookie", "private_key", "raw_value", "source_of_truth",
    "repository_revision", "git_revision", "branch", "implementation_path", "source_code_path",
    "test_scenarios", "run_id", "result", "results", "status_result", "runtime_result",
}
RISK_LEVELS = {"read-only", "guarded", "critical"}
CRITICAL_CATEGORIES = {"migrate", "seed", "reset", "drop", "destroy", "publish", "deploy-remote", "production-access", "credential-rotation"}


def _walk(value: Any, path: str = ""):
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            yield from _walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")


def _load_profile(profile_path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        profile_data = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        return None, [f"source Profile cannot be read: {error.__class__.__name__}"]
    if not isinstance(profile_data, dict):
        return None, ["source Profile must be a YAML mapping"]
    validator_path = Path(__file__).resolve().parents[2] / "environment-profile" / "scripts" / "validate_profile.py"
    try:
        spec = importlib.util.spec_from_file_location("environment_profile_validator", validator_path)
        if spec is None or spec.loader is None:
            return None, ["source Environment Profile validator cannot be loaded"]
        validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator)
        profile_errors = validator.validate_profile(profile_data)
    except (OSError, ImportError, AttributeError):
        return None, ["source Environment Profile validator cannot be loaded"]
    if profile_errors:
        return None, ["source Environment Profile is invalid"]
    return profile_data, []


def _validate_profile_binding(data: dict[str, Any], errors: list[str], base_dir: Path | None = None) -> None:
    profile_ref = data.get("profile_ref")
    if not isinstance(profile_ref, dict):
        return
    profile_path_value = profile_ref.get("path")
    if not isinstance(profile_path_value, str) or not profile_path_value.strip():
        return
    profile_path = Path(profile_path_value)
    if not profile_path.is_absolute():
        profile_path = (base_dir or Path.cwd()) / profile_path
    profile, profile_errors = _load_profile(profile_path)
    errors.extend(profile_errors)
    if profile is None:
        return
    if profile.get("profile_kind") != "environment":
        errors.append("profile_ref.path must point to an Environment Profile")
    if profile.get("profile_state") != "confirmed":
        errors.append("source Environment Profile must be confirmed")
    confirmation = profile.get("confirmation")
    if not isinstance(confirmation, dict) or confirmation.get("state") != "confirmed":
        errors.append("source Environment Profile confirmation.state must be confirmed")
    else:
        if confirmation.get("confirmed_revision") != profile.get("profile_revision"):
            errors.append("source Environment Profile confirmed_revision must match profile_revision")
        if confirmation.get("confirmed_content_hash") != profile.get("content_hash"):
            errors.append("source Environment Profile confirmed_content_hash must match content_hash")
    if profile_ref.get("profile_id") not in (None, profile.get("profile_id")):
        errors.append("profile_ref.profile_id must match source Environment Profile")
    if profile_ref.get("profile_revision") != profile.get("profile_revision"):
        errors.append("profile_ref.profile_revision must match source Environment Profile")
    if profile_ref.get("profile_content_hash") != profile.get("content_hash"):
        errors.append("profile_ref.profile_content_hash must match source Environment Profile")
    declared = profile.get("operations", [])
    declared_ids = {item.get("operation_id") for item in declared if isinstance(item, dict)}
    for index, operation_id in enumerate(data.get("operations", [])):
        if isinstance(operation_id, str) and operation_id not in declared_ids:
            errors.append(f"operations[{index}] is not declared by source Environment Profile")


def validate_manifest(data: Any, *, base_dir: Path | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["manifest must be a YAML mapping"]
    if data.get("version") != 1:
        errors.append("version must be 1")
    if data.get("manifest_kind") != "environment-operation":
        errors.append("manifest_kind must be environment-operation")
    if not isinstance(data.get("manifest_id"), str) or not data["manifest_id"].strip():
        errors.append("manifest_id must be a non-empty string")

    profile_ref = data.get("profile_ref")
    if not isinstance(profile_ref, dict):
        errors.append("profile_ref must be a mapping")
    else:
        for key in ("path", "profile_revision", "profile_content_hash"):
            if profile_ref.get(key) in (None, ""):
                errors.append(f"profile_ref.{key} is required")
        if profile_ref.get("profile_id") in (None, ""):
            errors.append("profile_ref.profile_id is required")
        elif isinstance(profile_ref.get("profile_id"), str) and profile_ref["profile_id"].strip() == "self":
            errors.append("profile_ref.profile_id must identify the source Environment Profile")
        _validate_profile_binding(data, errors, base_dir)

    declaration = data.get("declaration")
    if not isinstance(declaration, dict) or declaration.get("source") != "environment-profile":
        errors.append("declaration.source must be environment-profile")
    elif declaration.get("confirmed") is not True:
        errors.append("declaration.confirmed must be true")

    security = data.get("security")
    if not isinstance(security, dict):
        errors.append("security must be a mapping")
    else:
        if security.get("secret_values_allowed") is not False:
            errors.append("security.secret_values_allowed must be false")
        if security.get("expose_secrets_to_model") is not False:
            errors.append("security.expose_secrets_to_model must be false")
        if security.get("redact_logs") is not True:
            errors.append("security.redact_logs must be true")

    runtime = data.get("runtime")
    if not isinstance(runtime, dict) or runtime.get("preflight_required") is not True:
        errors.append("runtime.preflight_required must be true")

    operations = data.get("operations")
    if not isinstance(operations, list):
        errors.append("operations must be a list")
    elif not all(isinstance(operation_id, str) and operation_id.strip() for operation_id in operations):
        errors.append("operations must be a list of declared operation IDs")


    for path, value in _walk(data):
        key = path.rsplit(".", 1)[-1].split("[", 1)[0].replace("-", "_").lower()
        if key in FORBIDDEN_KEYS:
            errors.append(f"forbidden manifest field: {path}")
        if isinstance(value, str) and SECRET_PATTERN.search(value):
            errors.append(f"secret-like value is forbidden: {path}")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        data = yaml.safe_load(args.manifest.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        print(f"Manifest validation failed: {error}", file=sys.stderr)
        return 1
    errors = validate_manifest(data, base_dir=args.manifest.parent.resolve())
    if errors:
        print("Manifest validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Manifest validation passed: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
