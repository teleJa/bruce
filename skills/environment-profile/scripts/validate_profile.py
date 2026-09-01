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
ALLOWED_ENV_SOURCE_KINDS = {"user"}
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
FORBIDDEN_ENV_METADATA_KEYS = {
    "source_of_truth",
    "repository_revision",
    "branch",
    "working_tree_basis",
    "git_revision",
    "git_branch",
    "test_scenarios",
    "implementation_path",
    "source_code_path",
    "source_file",
    "source_files",
    "code_path",
}
DECLARATION_KEYS = {"source", "statement", "provided_at"}
FACT_KEYS = {"fact_id", "value", "source", "confirmation_required", "runtime_preflight_required"}
FACT_SOURCE_KEYS = {"kind", "statement", "provided_at"}
LOCAL_ENV_KEYS = {"path", "required", "ignored_by_vcs", "file_mode", "required_variables"}
CREDENTIAL_KEYS = {
    "credential_id", "kind", "source_ref", "owner", "scope", "preflight_method",
    "secret_value_persisted", "expose_to_model", "redact_logs",
}
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
        declaration = data.get("declaration")
        if not isinstance(declaration, dict):
            errors.append("Environment Profile requires declaration mapping")
        else:
            if declaration.get("source") != "user":
                errors.append("Environment Profile declaration.source must be user")
            if not isinstance(declaration.get("statement"), str) or not declaration["statement"].strip():
                errors.append("Environment Profile declaration.statement must be non-empty")
            for key in set(declaration) - DECLARATION_KEYS:
                errors.append(f"Environment Profile declaration field is not allowed: {key}")
        for key in FORBIDDEN_ENV_METADATA_KEYS:
            if key in data:
                errors.append(f"Environment Profile must not contain repository metadata: {key}")
        environment = data.get("environment")
        environment_kind = environment.get("kind") if isinstance(environment, dict) else None
        security = data.get("security")
        if environment_kind == "local" and not isinstance(security, dict):
            errors.append("local Environment Profile requires security mapping")
        if isinstance(security, dict):
            if security.get("persist_secrets") is not False:
                errors.append("security.persist_secrets must be false")
            if security.get("expose_secrets_to_model") is not False:
                errors.append("security.expose_secrets_to_model must be false")
            if security.get("credential_values_allowed") is not False:
                errors.append("security.credential_values_allowed must be false")
            if security.get("credential_refs_only") is not True:
                errors.append("security.credential_refs_only must be true")
        credentials = data.get("credentials", [])
        if isinstance(credentials, list):
            for index, credential in enumerate(credentials):
                if not isinstance(credential, dict):
                    errors.append(f"credentials[{index}] must be a mapping")
                    continue
                for key in set(credential) - CREDENTIAL_KEYS:
                    errors.append(f"credentials[{index}] field is not allowed: {key}")
                if credential.get("secret_value_persisted") is not False:
                    errors.append(f"credentials[{index}].secret_value_persisted must be false")
                if credential.get("expose_to_model") is not False:
                    errors.append(f"credentials[{index}].expose_to_model must be false")
                if credential.get("redact_logs") is not True:
                    errors.append(f"credentials[{index}].redact_logs must be true")
        local_env = data.get("local_env")
        if environment_kind == "local" and not isinstance(local_env, dict):
            errors.append("local Environment Profile requires local_env mapping")
        if isinstance(local_env, dict):
            for key in set(local_env) - LOCAL_ENV_KEYS:
                errors.append(f"local_env field is not allowed: {key}")
            if local_env.get("path") != ".env":
                errors.append("local_env.path must be .env")
            if local_env.get("ignored_by_vcs") != "required":
                errors.append("local_env.ignored_by_vcs must be required")
            if local_env.get("file_mode") != "0600":
                errors.append("local_env.file_mode must be 0600")
            if not isinstance(local_env.get("required"), bool):
                errors.append("local_env.required must be boolean")
            required_variables = local_env.get("required_variables", [])
            if not isinstance(required_variables, list):
                errors.append("local_env.required_variables must be a list")
            else:
                for index, name in enumerate(required_variables):
                    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                        errors.append(f"local_env.required_variables[{index}] must be a valid environment variable name")
        facts = data.get("facts", [])
        if not isinstance(facts, list):
            errors.append("Environment Profile facts must be a list")
        else:
            for index, fact in enumerate(facts):
                if not isinstance(fact, dict):
                    errors.append(f"facts[{index}] must be a mapping")
                    continue
                for key in set(fact) - FACT_KEYS:
                    errors.append(f"facts[{index}] field is not allowed: {key}")
                source = fact.get("source")
                if not isinstance(source, dict):
                    errors.append(f"facts[{index}].source must be a mapping with kind=user")
                else:
                    if source.get("kind") not in ALLOWED_ENV_SOURCE_KINDS:
                        errors.append(f"Environment Profile fact source must be user: facts[{index}].source.kind")
                    for key in set(source) - FACT_SOURCE_KEYS:
                        errors.append(f"Environment Profile facts must not contain repository source metadata: facts[{index}].source.{key}")
        for path, _ in _walk(data):
            key = path.rsplit(".", 1)[-1].split("[", 1)[0]
            if key in FORBIDDEN_ENV_METADATA_KEYS:
                errors.append(f"Environment Profile must not contain repository or implementation metadata: {path}")
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
