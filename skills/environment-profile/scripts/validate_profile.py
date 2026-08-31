#!/usr/bin/env python3
"""Validate static Bruce Environment and Requirement Verification Profiles."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ALLOWED_KINDS = {"environment", "requirement-verification"}
ALLOWED_ENV_SOURCE_KINDS = {"repository", "project-document", "user"}
FORBIDDEN_SECRET_KEYS = {
    "api_key",
    "password",
    "passwd",
    "secret",
    "access_token",
    "refresh_token",
    "jwt",
    "cookie",
    "sso_ticket",
    "private_key",
    "secret_value",
}
SECRET_VALUE_PATTERN = re.compile(
    r"(?:bearer\s+eyJ|https?://[^\s/@]+:[^\s/@]+@|-----BEGIN .* PRIVATE KEY-----|sk-[A-Za-z0-9_-]{12,})",
    re.IGNORECASE,
)
DYNAMIC_ENV_KEYS = {
    "run_id",
    "stage_results",
    "preflight_results",
    "evidence_refs",
    "build_id",
    "deployed_commit",
    "deployed_revision",
    "artifact_result",
    "rollout_result",
    "current_availability",
    "runtime_result",
    "selected_account",
}


def _walk(value: Any, path: str = ""):
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            yield from _walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")


def validate_profile(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["profile must be a YAML mapping"]
    if data.get("version") != 1:
        errors.append("version must be 1")
    kind = data.get("profile_kind")
    if kind not in ALLOWED_KINDS:
        errors.append("profile_kind must be environment or requirement-verification")
    if not isinstance(data.get("profile_id"), str) or not data["profile_id"].strip():
        errors.append("profile_id must be a non-empty string")
    revision = data.get("profile_revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        errors.append("profile_revision must be a positive integer")
    confirmation = data.get("confirmation")
    if not isinstance(confirmation, dict):
        errors.append("confirmation must be a mapping")
    else:
        state = confirmation.get("state")
        if state not in {"pending", "confirmed", "rejected"}:
            errors.append("confirmation.state must be pending, confirmed, or rejected")
        if state == "confirmed":
            if data.get("profile_state") != "confirmed":
                errors.append("confirmed profile must have profile_state=confirmed")
            if confirmation.get("confirmed_revision") != revision:
                errors.append("confirmed_revision must match profile_revision")
            if confirmation.get("confirmed_content_hash") != data.get("content_hash"):
                errors.append("confirmed_content_hash must match content_hash")
    for path, value in _walk(data):
        key = path.rsplit(".", 1)[-1].split("[", 1)[0]
        normalized_key = key.replace("-", "_").lower()
        if normalized_key in FORBIDDEN_SECRET_KEYS:
            errors.append(f"secret-bearing field is forbidden: {path}")
        if isinstance(value, str) and SECRET_VALUE_PATTERN.search(value):
            errors.append(f"secret-like value is forbidden: {path}")
    if kind == "environment":
        for path, value in _walk(data.get("facts", []), "facts"):
            if path.endswith(".source.kind") and value not in ALLOWED_ENV_SOURCE_KINDS:
                errors.append(
                    f"static Environment Profile fact source must be repository, project-document, or user: {path}"
                )
        for path, _ in _walk(data):
            key = path.rsplit(".", 1)[-1].split("[", 1)[0]
            if key in DYNAMIC_ENV_KEYS:
                errors.append(f"dynamic runtime field is forbidden in Environment Profile: {path}")
        if "acceptance" in data or "acceptance_ids" in data:
            errors.append("Environment Profile must not contain requirement acceptance mappings")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("profile", type=Path)
    args = parser.parse_args()
    try:
        data = yaml.safe_load(args.profile.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        print(f"Profile validation failed: {error}", file=sys.stderr)
        return 1
    errors = validate_profile(data)
    if errors:
        print("Profile validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Profile validation passed: {args.profile}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
