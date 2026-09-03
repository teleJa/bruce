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
    "test_scenarios",
    "runtime_status",
}
DECLARATION_KEYS = {"source", "statement", "provided_at"}
FACT_KEYS = {"fact_id", "value", "source", "confirmation_required", "runtime_preflight_required"}
FACT_SOURCE_KEYS = {"kind", "statement", "provided_at"}
LOCAL_ENV_KEYS = {"path", "required", "ignored_by_vcs", "file_mode", "required_variables"}
TEST_CONTEXT_KEYS = {"scope", "authorization", "workflow", "services", "data", "authentication", "configuration", "preflight"}
TEST_AUTHORIZATION_KEYS = {"mode", "approved_scopes", "escalation_required_for"}
TEST_WORKFLOW_KEYS = {"build_operation", "deploy_operation", "test_data", "authenticate_operation", "test_operation"}
TEST_DATA_KEYS = {"prepare_operation", "cleanup_operation", "isolation", "strategy"}
TEST_SERVICES_KEYS = {"application", "dependencies", "endpoints"}
TEST_CONFIGURATION_KEYS = {"env_file", "references"}
TEST_ENV_FILE_KEYS = {"path", "required", "required_variables", "file_mode", "ignored_by_vcs"}
TEST_DATA_POLICY_KEYS = {"allowed_mutations", "prohibited_mutations"}
OPERATION_AUTHORIZATIONS = {"none", "profile-confirmed", "explicit-per-invocation"}
BUILD_KEYS = {"strategy", "operation_id", "artifact_expectations"}
CREDENTIAL_KEYS = {
    "credential_id", "kind", "source_ref", "owner", "scope", "preflight_method",
    "secret_value_persisted", "expose_to_model", "redact_logs",
}
PROFILE_OPERATION_KEYS = {
    "operation_id", "category", "purpose", "executor", "working_directory_ref", "argv",
    "authorization", "risk", "mutates", "ownership", "target", "impact", "rollback",
    "cleanup", "required_evidence",
}
OPERATION_RISKS = {"read-only", "guarded", "critical"}
OPERATION_CRITICAL_CATEGORIES = {"migrate", "seed", "reset", "drop", "destroy", "publish", "deploy-remote", "production-access", "credential-rotation"}
SECRET_ASSIGNMENT_PATTERN = re.compile(r"(?i)^(?:[A-Z0-9_]*(?:PASSWORD|PASSWD|TOKEN|API_KEY|SECRET)[A-Z0-9_]*)=")
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
        test_context = data.get("test_context")
        profile_authorization_mode = None
        approved_scopes: set[str] = set()
        if test_context is not None:
            if not isinstance(test_context, dict):
                errors.append("Environment Profile test_context must be a mapping")
            else:
                for key in set(test_context) - TEST_CONTEXT_KEYS:
                    errors.append(f"test_context field is not allowed: {key}")
                authorization = test_context.get("authorization", {})
                if not isinstance(authorization, dict):
                    errors.append("test_context.authorization must be a mapping")
                else:
                    for key in set(authorization) - TEST_AUTHORIZATION_KEYS:
                        errors.append(f"test_context.authorization field is not allowed: {key}")
                    profile_authorization_mode = authorization.get("mode")
                    if profile_authorization_mode not in {"profile-confirmed", "per-invocation"}:
                        errors.append("test_context.authorization.mode must be profile-confirmed or per-invocation")
                    for key in ("approved_scopes", "escalation_required_for"):
                        value = authorization.get(key, [])
                        if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
                            errors.append(f"test_context.authorization.{key} must be a list of non-empty strings")
                    approved_scopes = set(authorization.get("approved_scopes", [])) if isinstance(authorization.get("approved_scopes", []), list) else set()
                workflow = test_context.get("workflow", {})
                if not isinstance(workflow, dict):
                    errors.append("test_context.workflow must be a mapping")
                else:
                    for key in set(workflow) - TEST_WORKFLOW_KEYS:
                        errors.append(f"test_context.workflow field is not allowed: {key}")
                    for key in ("build_operation", "deploy_operation", "authenticate_operation", "test_operation"):
                        value = workflow.get(key)
                        if value is not None and (not isinstance(value, str) or not value.strip()):
                            errors.append(f"test_context.workflow.{key} must be a non-empty operation ID when provided")
                    test_data = workflow.get("test_data", {})
                    if not isinstance(test_data, dict):
                        errors.append("test_context.workflow.test_data must be a mapping")
                    else:
                        for key in set(test_data) - TEST_DATA_KEYS:
                            errors.append(f"test_context.workflow.test_data field is not allowed: {key}")
                        for key in ("prepare_operation", "cleanup_operation"):
                            value = test_data.get(key)
                            if value is not None and (not isinstance(value, str) or not value.strip()):
                                errors.append(f"test_context.workflow.test_data.{key} must be a non-empty operation ID when provided")
                services = test_context.get("services", {})
                if services is not None and not isinstance(services, dict):
                    errors.append("test_context.services must be a mapping")
                elif isinstance(services, dict):
                    for key in set(services) - TEST_SERVICES_KEYS:
                        errors.append(f"test_context.services field is not allowed: {key}")
                configuration = test_context.get("configuration", {})
                if configuration is not None and not isinstance(configuration, dict):
                    errors.append("test_context.configuration must be a mapping")
                elif isinstance(configuration, dict):
                    for key in set(configuration) - TEST_CONFIGURATION_KEYS:
                        errors.append(f"test_context.configuration field is not allowed: {key}")
                    env_file = configuration.get("env_file")
                    if env_file is not None:
                        if not isinstance(env_file, dict):
                            errors.append("test_context.configuration.env_file must be a mapping")
                        else:
                            for key in set(env_file) - TEST_ENV_FILE_KEYS:
                                errors.append(f"test_context.configuration.env_file field is not allowed: {key}")
                            if env_file.get("path") != ".env":
                                errors.append("test_context.configuration.env_file.path must be .env")
                data_policy = test_context.get("data")
                if data_policy is not None:
                    if not isinstance(data_policy, dict):
                        errors.append("test_context.data must be a mapping")
                    else:
                        for key in set(data_policy) - TEST_DATA_POLICY_KEYS:
                            errors.append(f"test_context.data field is not allowed: {key}")
                preflight = test_context.get("preflight")
                if preflight is not None and not isinstance(preflight, list):
                    errors.append("test_context.preflight must be a list")
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
        build = data.get("build")
        if isinstance(build, dict):
            for key in set(build) - BUILD_KEYS:
                errors.append(f"build field is not allowed: {key}")
            operation_id = build.get("operation_id")
            if operation_id is not None and (not isinstance(operation_id, str) or not operation_id.strip()):
                errors.append("build.operation_id must be a non-empty string when provided")
            artifact_expectations = build.get("artifact_expectations", [])
            if not isinstance(artifact_expectations, list) or not all(isinstance(item, str) and item.strip() for item in artifact_expectations):
                errors.append("build.artifact_expectations must be a list of non-empty strings")
        elif build is not None:
            errors.append("Environment Profile build must be a mapping")
        lifecycle = data.get("lifecycle")
        if isinstance(lifecycle, dict):
            lifecycle_keys = {"prepare", "start", "stop", "status", "logs"}
            for key in set(lifecycle) - lifecycle_keys:
                errors.append(f"lifecycle field is not allowed: {key}")
            for phase in lifecycle_keys:
                value = lifecycle.get(phase, [])
                if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
                    errors.append(f"lifecycle.{phase} must be a list of non-empty operation IDs")
        elif lifecycle is not None:
            errors.append("Environment Profile lifecycle must be a mapping")
        if "confirmation_summary" in data:
            errors.append("Environment Profile must not persist confirmation_summary; generate it for display")
        operations = data.get("operations", [])
        if not isinstance(operations, list):
            errors.append("Environment Profile operations must be a list")
        else:
            for index, operation in enumerate(operations):
                if not isinstance(operation, dict):
                    errors.append(f"operations[{index}] must be a mapping")
                    continue
                for key in set(operation) - PROFILE_OPERATION_KEYS:
                    errors.append(f"operations[{index}] field is not allowed: {key}")
                for key in ("operation_id", "category", "executor", "authorization", "risk"):
                    if not isinstance(operation.get(key), str) or not operation[key].strip():
                        errors.append(f"operations[{index}].{key} is required")
                risk = operation.get("risk")
                if risk not in OPERATION_RISKS:
                    errors.append(f"operations[{index}].risk must be read-only, guarded, or critical")
                argv = operation.get("argv")
                if argv is not None:
                    if not isinstance(argv, list) or not all(isinstance(item, str) and item for item in argv):
                        errors.append(f"operations[{index}].argv must be a non-empty string list")
                    elif any(SECRET_ASSIGNMENT_PATTERN.search(item) for item in argv):
                        errors.append(f"operations[{index}].argv must not contain secret assignments")
                category = operation.get("category")
                minimum_risk = "read-only" if category in {"status", "health-check", "inspect-declared-resources", "logs", "preflight"} else "guarded"
                if risk == "read-only" and minimum_risk != "read-only":
                    errors.append(f"operations[{index}] category requires at least guarded risk")
                authorization_mode = operation.get("authorization")
                if authorization_mode not in OPERATION_AUTHORIZATIONS:
                    errors.append(f"operations[{index}].authorization must be none, profile-confirmed, or explicit-per-invocation")
                if risk == "guarded" and authorization_mode == "none":
                    errors.append(f"operations[{index}] guarded operation requires profile-confirmed or explicit-per-invocation authorization")
                if authorization_mode == "profile-confirmed":
                    if profile_authorization_mode != "profile-confirmed":
                        errors.append(f"operations[{index}] profile-confirmed authorization requires test_context.authorization.mode=profile-confirmed")
                    if category not in approved_scopes and operation.get("operation_id") not in approved_scopes:
                        errors.append(f"operations[{index}] is not covered by test_context.authorization.approved_scopes")
                if category in OPERATION_CRITICAL_CATEGORIES:
                    if authorization_mode != "explicit-per-invocation":
                        errors.append(f"operations[{index}] critical operation requires explicit authorization")
                    if risk != "critical":
                        errors.append(f"operations[{index}] critical operation risk must be critical")
                    for key in ("target", "impact", "rollback"):
                        if not isinstance(operation.get(key), str) or not operation[key].strip():
                            errors.append(f"operations[{index}] critical operation requires {key}")
                if category in {"stop", "down", "cleanup"} and not operation.get("ownership"):
                    errors.append(f"operations[{index}] stop-like operation requires ownership")
        # Backward-compatible read-only validation for profiles created before executable
        # operation Skills replaced the old manifest artifact. New profiles do not emit this field.
        operation_manifest = data.get("operation_manifest")
        if operation_manifest is not None:
            if not isinstance(operation_manifest, dict):
                errors.append("legacy operation_manifest must be a mapping")
            else:
                allowed_legacy_manifest_keys = {
                    "requested", "manifest_id", "output_path", "source_profile", "generation",
                    "included_operations", "excluded_operations",
                }
                for key in set(operation_manifest) - allowed_legacy_manifest_keys:
                    errors.append(f"legacy operation_manifest field is not allowed: {key}")
                if not isinstance(operation_manifest.get("requested"), bool):
                    errors.append("legacy operation_manifest.requested must be boolean")
                for key in ("included_operations", "excluded_operations"):
                    value = operation_manifest.get(key, [])
                    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                        errors.append(f"legacy operation_manifest.{key} must be a list of strings")

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
