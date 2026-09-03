#!/usr/bin/env python3
"""Validation and aggregation helpers for Bruce test-dispatch contracts.

The module is deliberately project-agnostic.  It validates the shared Scenario v1,
Dispatch v1, and Track Result v1 shapes without executing any project command,
network request, browser action, or database operation.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import importlib.util
import math
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any, Iterable


SCHEMA_VERSION = 1
API_MODES = {"memory-application", "real-http", "live-acceptance"}
UI_MODES = {"browser-provider"}
ALL_API_UI_MODES = API_MODES | UI_MODES
SCENARIO_STATUSES = {"designed", "executed", "passed", "failed", "blocked"}
TRACKS = {"api", "ui"}
API_ACTIONS = {"request", "poll", "assert", "cleanup"}
UI_ACTIONS = {
    "open",
    "observe",
    "click",
    "input",
    "upload",
    "select",
    "drag",
    "refresh",
    "navigate",
    "confirm",
    "assert",
}
OWNERSHIPS = {"test-run", "dedicated-test-database", "read-only-existing-data"}
VISUAL_SCOPES = {"none", "browser-smoke", "browser-layout"}
BROWSER_PROVIDERS = {"ego-lite", "chrome"}
ROUTING_PROFILES = {"inspector", "implementer", "verifier", "reviewer"}
RESOLUTION_RESULTS = {"resolved", "fallback", "blocked"}
EVIDENCE_KINDS = {"command", "browser", "screenshot", "state-trace", "readback", "assertion", "log", "artifact"}
EVIDENCE_STATUSES = {"captured", "verified", "redacted", "missing"}
AGGREGATION_STATUSES = ("failed", "blocked", "passed", "executed", "designed")


SCENARIO_KEYS = {
    "version",
    "scenario_id",
    "scenario_version",
    "feature_area",
    "business_flow",
    "actor",
    "visual_scope",
    "execution",
    "data",
    "preconditions",
    "api",
    "ui",
    "failure_cases",
    "evidence",
    "status",
}
EXECUTION_KEYS = {"environment_profile", "api_mode", "ui_mode"}
DATA_KEYS = {"api_namespace", "ui_namespace", "ownership", "cleanup"}
API_KEYS = {"steps", "assertions", "persistence"}
UI_KEYS = {"steps", "assertions", "forbidden_shortcuts"}
PERSISTENCE_KEYS = {"required", "readback"}
EVIDENCE_KEYS = {"required", "directory"}
STEP_KEYS = {"id", "action", "request", "until", "target", "value", "assertion"}
POLL_KEYS = {"terminal_statuses", "success_statuses", "timeout_seconds", "interval_seconds"}
EVIDENCE_RECORD_KEYS = {"kind", "ref", "status"}
BROWSER_EVIDENCE_KEYS = {
    "provider", "target", "session", "visual_scope", "actions", "visible_result",
    "capture_time", "screenshot_path", "viewport", "geometry", "overflow",
}
VIEWPORT_KEYS = {"width", "height"}
PROFILE_HASH_PATTERN = re.compile(r"^sha256:[0-9a-fA-F]{64}$")
NAMESPACE_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
DISALLOWED_TEST_MODEL = "gpt-5.6-" + "sol"

DISPATCH_KEYS = {
    "version",
    "scenario_id",
    "scenario_version",
    "feature_area",
    "business_flow",
    "actor",
    "tracks",
    "routing",
}
DISPATCH_TRACK_KEYS = {"track", "execution_mode", "data_namespace", "allowed_paths", "required_evidence"}
ROUTING_KEYS = {
    "required_capabilities",
    "functional_agent_profile",
    "resolver",
    "model_resolution",
    "functional_packet",
    "subagent_browser_access",
    "visual_scope",
}

TRACK_RESULT_KEYS = {
    "scenario_id",
    "scenario_version",
    "status",
    "execution_mode",
    "data_namespace",
    "allowed_paths",
    "evidence_paths",
    "modified_paths",
    "commands",
    "browser_actions",
    "assertions",
    "blockers",
    "unverified_gates",
    "track",
    "basis_revision",
    "evidence_revision",
    "profile_revision",
    "operation_refs",
    "account_refs",
    "evidence_records",
    "persistence_required",
    "authoritative_readback",
    "browser_evidence",
}
TRACK_RESULT_ROOT_KEYS = {
    "version",
    "scenario_id",
    "scenario_version",
    "required_tracks",
    "tracks",
    "overall_status",
    "profile_id",
    "profile_revision",
    "profile_content_hash",
    "basis_revision",
    "evidence_revision",
}

# Contract inputs must never become a secret store.  These are field names, not
# values such as the safe Environment Profile reference ``AUTH_CENTER_TEST_KEY``.
SECRET_KEY_PARTS = {
    "password",
    "passwd",
    "token",
    "access_token",
    "refresh_token",
    "id_token",
    "cookie",
    "cookies",
    "api_key",
    "apikey",
    "secret",
    "secrets",
    "authorization",
    "auth_header",
    "database_url",
    "db_url",
    "connection_string",
    "sso_ticket",
    "jwt",
}
DYNAMIC_KEYS = {
    "run_id",
    "checkpoint",
    "source_revision",
    "build_id",
    "artifact_id",
    "deployment_revision",
    "actual_account",
    "account_binding",
    "stage_results",
    "preflight_results",
    "evidence_revision",
    "current_round",
    "completion",
    "verdict",
}
RAW_SECRET_PATTERNS = (
    re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{8,}"),
    re.compile(r"(?i)\bbasic\s+[A-Za-z0-9+/=]{8,}"),
    re.compile(r"(?i)\b(?:sk|rk)-[A-Za-z0-9_-]{12,}"),
    re.compile(r"(?i)https?://[^/\s:@]+:[^/\s@]+@"),
    re.compile(r"(?i)(?:[?&](?:token|access_token|refresh_token|id_token|api_key|apikey|password|passwd|secret|cookie|jwt)=)"),
    re.compile(r"(?i)\b(?:token|access_token|refresh_token|api_key|apikey|password|passwd|secret|cookie|jwt|database_url)\s*=\s*[^\s{<][^\s]*"),
)
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
ENV_NAME_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]{1,127}$")


class ContractValidationError(ValueError):
    """Raised by aggregation when its input is not a valid Track Result document."""

    def __init__(self, errors: Iterable[str]):
        self.errors = sorted(set(errors))
        super().__init__("; ".join(self.errors))


def _is_mapping(value: Any) -> bool:
    return isinstance(value, dict)


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _is_positive_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
        and value > 0
    )


def _is_safe_namespace(value: Any) -> bool:
    return isinstance(value, str) and bool(NAMESPACE_PATTERN.fullmatch(value.strip()))


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and all(_is_nonempty_string(item) for item in value)


def _unique_string_list(value: Any) -> bool:
    return _string_list(value) and len(value) == len(set(value))


def _unknown_keys(value: dict[str, Any], allowed: set[str], label: str) -> list[str]:
    return [f"{label} field is not allowed: {key}" for key in sorted(set(value) - allowed)]


def _normalise_path(value: str) -> str:
    return value.strip().rstrip("/") or "."


def _safe_relative_path(value: Any) -> bool:
    if not _is_nonempty_string(value):
        return False
    candidate = value.strip().replace("\\", "/")
    if candidate.startswith(("/", "~")) or re.match(r"^[A-Za-z]:", candidate):
        return False
    path = PurePosixPath(candidate)
    if path.is_absolute() or any(part in {"", ".."} for part in path.parts):
        return False
    return True


def _path_list(value: Any, label: str, *, allow_empty: bool = True) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, list):
        return [f"{label} must be a list"]
    if not allow_empty and not value:
        errors.append(f"{label} must not be empty")
    seen: set[str] = set()
    for index, item in enumerate(value):
        if not _safe_relative_path(item):
            errors.append(f"{label}[{index}] must be a safe repository-relative path")
            continue
        normalised = _normalise_path(item)
        if normalised in seen:
            errors.append(f"{label} contains duplicate path: {item}")
        seen.add(normalised)
    return errors


def _paths_overlap(left: str, right: str) -> bool:
    a = _normalise_path(left)
    b = _normalise_path(right)
    if a == "." or b == ".":
        return True
    return a == b or a.startswith(f"{b}/") or b.startswith(f"{a}/")


def _path_is_within(path: str, parent: str) -> bool:
    child = _normalise_path(path)
    container = _normalise_path(parent)
    if container == ".":
        return True
    return child == container or child.startswith(f"{container}/")


def _paths_within(paths: list[str], parent_paths: list[str]) -> bool:
    return all(any(_path_is_within(path, parent) for parent in parent_paths) for path in paths)


def _scan_sensitive_values(value: Any, path: str = "root") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            normalised = key_text.lower().replace("-", "_")
            if normalised in SECRET_KEY_PARTS or any(
                part in normalised.split("_") for part in SECRET_KEY_PARTS if "_" not in part
            ):
                errors.append(f"secret-bearing field is forbidden: {path}.{key_text}")
            errors.extend(_scan_sensitive_values(child, f"{path}.{key_text}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_scan_sensitive_values(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        for pattern in RAW_SECRET_PATTERNS:
            if pattern.search(value):
                errors.append(f"secret-like value is forbidden: {path}")
                break
    return errors


def _scan_dynamic_keys(value: Any, path: str = "root") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            normalised = str(key).lower().replace("-", "_")
            if normalised in DYNAMIC_KEYS:
                errors.append(f"dynamic runtime field is forbidden: {path}.{key}")
            errors.extend(_scan_dynamic_keys(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_scan_dynamic_keys(child, f"{path}[{index}]"))
    return errors


def _validate_identity(data: dict[str, Any], label: str) -> list[str]:
    errors: list[str] = []
    if data.get("version") != SCHEMA_VERSION:
        errors.append(f"{label}.version must be {SCHEMA_VERSION}")
    for key in ("scenario_id", "feature_area", "business_flow", "actor"):
        value = data.get(key)
        if not _is_nonempty_string(value) or (key == "scenario_id" and not ID_PATTERN.fullmatch(value.strip())):
            errors.append(f"{label}.{key} must be a non-empty stable string")
    if not _is_positive_int(data.get("scenario_version")):
        errors.append(f"{label}.scenario_version must be a positive integer")
    return errors


def _validate_namespace_pair(data: dict[str, Any], api_enabled: bool, ui_enabled: bool, label: str) -> list[str]:
    errors: list[str] = []
    api_namespace = data.get("api_namespace")
    ui_namespace = data.get("ui_namespace")
    if api_enabled and not _is_safe_namespace(api_namespace):
        errors.append(f"{label}.api_namespace must be a safe lowercase namespace")
    if ui_enabled and not _is_safe_namespace(ui_namespace):
        errors.append(f"{label}.ui_namespace must be a safe lowercase namespace")
    if not api_enabled and api_namespace not in (None, ""):
        errors.append(f"{label}.api_namespace must be null when API track is disabled")
    if not ui_enabled and ui_namespace not in (None, ""):
        errors.append(f"{label}.ui_namespace must be null when UI track is disabled")
    if api_enabled and ui_enabled and isinstance(api_namespace, str) and isinstance(ui_namespace, str) and api_namespace == ui_namespace:
        errors.append(f"{label} API and UI namespaces must be distinct")
    return errors


def _validate_api_steps(api: dict[str, Any], enabled: bool) -> list[str]:
    errors: list[str] = []
    steps = api.get("steps", [])
    if not isinstance(steps, list):
        return ["api.steps must be a list"]
    if enabled and not steps:
        errors.append("enabled API track requires at least one api step")
    seen: set[str] = set()
    for index, step in enumerate(steps):
        label = f"api.steps[{index}]"
        if not _is_mapping(step):
            errors.append(f"{label} must be a mapping")
            continue
        errors.extend(_unknown_keys(step, STEP_KEYS, label))
        step_id = step.get("id")
        if not _is_nonempty_string(step_id) or step_id in seen:
            errors.append(f"{label}.id must be unique and non-empty")
        else:
            seen.add(step_id)
        action = step.get("action")
        if not isinstance(action, str) or action not in API_ACTIONS:
            errors.append(f"{label}.action must be one of {sorted(API_ACTIONS)}")
        if isinstance(action, str) and action in UI_ACTIONS - {"assert"}:
            errors.append(f"{label} contains a UI action in the API track")
        if "target" in step:
            errors.append(f"{label}.target is a UI-only field")
        if action in {"request", "poll"}:
            request = step.get("request")
            if not _is_mapping(request):
                errors.append(f"{label}.request must be a mapping for {action}")
            else:
                if not _is_nonempty_string(request.get("method")):
                    errors.append(f"{label}.request.method must be a non-empty string")
                if not _is_nonempty_string(request.get("path")):
                    errors.append(f"{label}.request.path must be a non-empty string")
            if action == "poll":
                until = step.get("until")
                if not _is_mapping(until):
                    errors.append(f"{label}.until must be a mapping for poll")
                else:
                    errors.extend(_unknown_keys(until, POLL_KEYS, f"{label}.until"))
                    terminal = until.get("terminal_statuses")
                    success = until.get("success_statuses")
                    if not _unique_string_list(terminal):
                        errors.append(f"{label}.until.terminal_statuses must be a unique string list")
                    if not _unique_string_list(success):
                        errors.append(f"{label}.until.success_statuses must be a unique string list")
                    if _unique_string_list(terminal) and _unique_string_list(success) and not set(success).issubset(terminal):
                        errors.append(f"{label}.until.success_statuses must be a subset of terminal_statuses")
                    for key in ("timeout_seconds", "interval_seconds"):
                        if not _is_positive_number(until.get(key)):
                            errors.append(f"{label}.until.{key} must be positive")
        elif "request" in step or "until" in step:
            errors.append(f"{label}.request/until are only valid for request or poll actions")
    return errors


def _validate_ui_steps(ui: dict[str, Any], enabled: bool) -> list[str]:
    errors: list[str] = []
    steps = ui.get("steps", [])
    if not isinstance(steps, list):
        return ["ui.steps must be a list"]
    if enabled and not steps:
        errors.append("enabled UI track requires at least one ui step")
    seen: set[str] = set()
    for index, step in enumerate(steps):
        label = f"ui.steps[{index}]"
        if not _is_mapping(step):
            errors.append(f"{label} must be a mapping")
            continue
        errors.extend(_unknown_keys(step, STEP_KEYS, label))
        step_id = step.get("id")
        if not _is_nonempty_string(step_id) or step_id in seen:
            errors.append(f"{label}.id must be unique and non-empty")
        else:
            seen.add(step_id)
        action = step.get("action")
        if not isinstance(action, str) or action not in UI_ACTIONS:
            errors.append(f"{label}.action must be one of {sorted(UI_ACTIONS)}")
        if isinstance(action, str) and action in API_ACTIONS - {"assert"}:
            errors.append(f"{label} contains an API action in the UI track")
        for key in ("request", "until"):
            if key in step:
                errors.append(f"{label}.{key} is forbidden in the UI track; use setup/cleanup/readback outside page actions")
        if action not in {"assert", "observe"} and not _is_nonempty_string(step.get("target")):
            errors.append(f"{label}.target is required for {action}")
    return errors


def validate_scenario(data: Any) -> list[str]:
    """Return deterministic validation errors for a Shared Scenario v1 document."""

    if not _is_mapping(data):
        return ["Scenario must be a mapping"]
    errors = _unknown_keys(data, SCENARIO_KEYS, "Scenario")
    errors.extend(_validate_identity(data, "Scenario"))
    execution = data.get("execution")
    if not _is_mapping(execution):
        errors.append("Scenario.execution must be a mapping")
        execution = {}
    else:
        errors.extend(_unknown_keys(execution, EXECUTION_KEYS, "Scenario.execution"))
    api_mode = execution.get("api_mode")
    ui_mode = execution.get("ui_mode")
    if api_mode is not None and (not isinstance(api_mode, str) or api_mode not in API_MODES):
        errors.append(f"Scenario.execution.api_mode must be one of {sorted(API_MODES)} or null")
    if ui_mode is not None and (not isinstance(ui_mode, str) or ui_mode not in UI_MODES):
        errors.append(f"Scenario.execution.ui_mode must be one of {sorted(UI_MODES)} or null")
    if not _is_nonempty_string(execution.get("environment_profile")):
        errors.append("Scenario.execution.environment_profile must be a non-empty string")
    visual_scope = data.get("visual_scope")
    if visual_scope is not None and (not isinstance(visual_scope, str) or visual_scope not in VISUAL_SCOPES):
        errors.append("Scenario.visual_scope must be none, browser-smoke, or browser-layout")
    if ui_mode is not None and visual_scope not in {"browser-smoke", "browser-layout"}:
        errors.append("enabled UI track requires an explicit browser visual_scope")
    if api_mode is None and ui_mode is None:
        errors.append("Scenario must enable at least one API or UI track")

    data_section = data.get("data")
    if not _is_mapping(data_section):
        errors.append("Scenario.data must be a mapping")
        data_section = {}
    else:
        errors.extend(_unknown_keys(data_section, DATA_KEYS, "Scenario.data"))
    if not isinstance(data_section.get("ownership"), str) or data_section.get("ownership") not in OWNERSHIPS:
        errors.append(f"Scenario.data.ownership must be one of {sorted(OWNERSHIPS)}")
    if not _is_nonempty_string(data_section.get("cleanup")):
        errors.append("Scenario.data.cleanup must be a non-empty declared strategy")
    errors.extend(_validate_namespace_pair(data_section, api_mode is not None, ui_mode is not None, "Scenario.data"))

    for key in ("preconditions", "failure_cases"):
        value = data.get(key, [])
        if not _string_list(value):
            errors.append(f"Scenario.{key} must be a list of non-empty strings")
    if "preconditions" not in data:
        errors.append("Scenario.preconditions must be declared")

    api = data.get("api")
    if not _is_mapping(api):
        errors.append("Scenario.api must be a mapping")
        api = {}
    else:
        errors.extend(_unknown_keys(api, API_KEYS, "Scenario.api"))
    errors.extend(_validate_api_steps(api, api_mode is not None))
    if not _string_list(api.get("assertions", [])):
        errors.append("Scenario.api.assertions must be a list of non-empty strings")
    persistence = api.get("persistence")
    if not _is_mapping(persistence):
        errors.append("Scenario.api.persistence must be a mapping")
        persistence = {}
    else:
        errors.extend(_unknown_keys(persistence, PERSISTENCE_KEYS, "Scenario.api.persistence"))
    if not isinstance(persistence.get("required"), bool):
        errors.append("Scenario.api.persistence.required must be boolean")
    if not _string_list(persistence.get("readback", [])):
        errors.append("Scenario.api.persistence.readback must be a list of non-empty strings")
    if persistence.get("required") is True and not persistence.get("readback"):
        errors.append("required API persistence must declare at least one readback")
    if api_mode is None and (api.get("steps") or api.get("assertions") or persistence.get("required")):
        errors.append("disabled API track must not declare executable API steps/assertions/persistence")

    ui = data.get("ui")
    if not _is_mapping(ui):
        errors.append("Scenario.ui must be a mapping")
        ui = {}
    else:
        errors.extend(_unknown_keys(ui, UI_KEYS, "Scenario.ui"))
    errors.extend(_validate_ui_steps(ui, ui_mode is not None))
    for key in ("assertions", "forbidden_shortcuts"):
        if not _string_list(ui.get(key, [])):
            errors.append(f"Scenario.ui.{key} must be a list of non-empty strings")
    if ui_mode is None and (ui.get("steps") or ui.get("assertions")):
        errors.append("disabled UI track must not declare executable UI steps/assertions")

    evidence = data.get("evidence")
    if not _is_mapping(evidence):
        errors.append("Scenario.evidence must be a mapping")
    else:
        errors.extend(_unknown_keys(evidence, EVIDENCE_KEYS, "Scenario.evidence"))
        if not _unique_string_list(evidence.get("required", [])) or not evidence.get("required"):
            errors.append("Scenario.evidence.required must be a non-empty unique string list")
        if not _safe_relative_path(evidence.get("directory")):
            errors.append("Scenario.evidence.directory must be a safe repository-relative path")

    if not isinstance(data.get("status"), str) or data.get("status") not in SCENARIO_STATUSES:
        errors.append(f"Scenario.status must be one of {sorted(SCENARIO_STATUSES)}")
    errors.extend(_scan_sensitive_values(data))
    errors.extend(_scan_dynamic_keys(data))
    return sorted(set(errors))


def _validate_track_declarations(tracks: Any, label: str = "Dispatch.tracks") -> tuple[list[str], dict[str, dict[str, Any]]]:
    errors: list[str] = []
    by_track: dict[str, dict[str, Any]] = {}
    if not isinstance(tracks, list) or not tracks:
        return [f"{label} must be a non-empty list"], by_track
    for index, item in enumerate(tracks):
        item_label = f"{label}[{index}]"
        if not _is_mapping(item):
            errors.append(f"{item_label} must be a mapping")
            continue
        errors.extend(_unknown_keys(item, DISPATCH_TRACK_KEYS, item_label))
        track = item.get("track")
        if not isinstance(track, str) or track not in TRACKS:
            errors.append(f"{item_label}.track must be api or ui")
            continue
        if track in by_track:
            errors.append(f"duplicate track declaration: {track}")
        else:
            by_track[track] = item
        mode = item.get("execution_mode")
        allowed_modes = API_MODES if track == "api" else UI_MODES
        if not isinstance(mode, str) or mode not in allowed_modes:
            errors.append(f"{item_label}.execution_mode is invalid for {track}")
        if not _is_safe_namespace(item.get("data_namespace")):
            errors.append(f"{item_label}.data_namespace must be a safe lowercase namespace")
        errors.extend(_path_list(item.get("allowed_paths", []), f"{item_label}.allowed_paths"))
        if not _unique_string_list(item.get("required_evidence", [])):
            errors.append(f"{item_label}.required_evidence must be a unique string list")
    namespaces = {
        item.get("data_namespace"): track
        for track, item in by_track.items()
        if _is_nonempty_string(item.get("data_namespace"))
    }
    valid_namespaces = [
        item.get("data_namespace")
        for item in by_track.values()
        if _is_nonempty_string(item.get("data_namespace"))
    ]
    if len(valid_namespaces) != len(set(valid_namespaces)):
        errors.append("API and UI data namespaces must be distinct")
    paths = {track: item.get("allowed_paths", []) for track, item in by_track.items()}
    if set(paths) == TRACKS:
        api_paths = [path for path in paths["api"] if isinstance(path, str)]
        ui_paths = [path for path in paths["ui"] if isinstance(path, str)]
        for left in api_paths:
            for right in ui_paths:
                if _paths_overlap(left, right):
                    errors.append(f"API/UI allowed_paths overlap: {left} vs {right}")
    return errors, by_track


def validate_dispatch_against_scenario(dispatch: Any, scenario: Any) -> list[str]:
    """Validate that a dispatch locks the same Scenario identity and enabled track modes."""

    errors = validate_dispatch(dispatch)
    errors.extend(validate_scenario(scenario))
    if not _is_mapping(dispatch) or not _is_mapping(scenario):
        return sorted(set(errors))
    for key in ("scenario_id", "scenario_version", "feature_area", "business_flow", "actor"):
        if dispatch.get(key) != scenario.get(key):
            errors.append(f"Dispatch.{key} must match Scenario.{key}")
    execution = scenario.get("execution") if _is_mapping(scenario.get("execution")) else {}
    declarations = dispatch.get("tracks") if isinstance(dispatch.get("tracks"), list) else []
    routing = dispatch.get("routing") if _is_mapping(dispatch.get("routing")) else {}
    for declaration in declarations:
        if not _is_mapping(declaration):
            continue
        track = declaration.get("track")
        expected_mode = execution.get("api_mode" if track == "api" else "ui_mode")
        if expected_mode is None:
            errors.append(f"Dispatch selects disabled Scenario track: {track}")
        elif declaration.get("execution_mode") != expected_mode:
            errors.append(f"Dispatch.{track}.execution_mode must match Scenario.execution")
    if any(_is_mapping(item) and item.get("track") == "ui" for item in declarations):
        if routing.get("visual_scope") != scenario.get("visual_scope"):
            errors.append("Dispatch.routing.visual_scope must match Scenario.visual_scope")
    return sorted(set(errors))


def _validate_model_resolution(value: Any, *, expected_profile: str | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["routing.model_resolution must be the full Bruce resolver record"]
    fields = {
        "requested_profile", "configured_model", "effective_model", "fallback_used",
        "fallback_reason", "capability_status", "resolution_result", "source",
    }
    errors.extend(_unknown_keys(value, fields, "routing.model_resolution"))
    if not isinstance(value.get("requested_profile"), str) or value.get("requested_profile") not in ROUTING_PROFILES:
        errors.append("routing.model_resolution.requested_profile is invalid")
    elif expected_profile and value.get("requested_profile") != expected_profile:
        errors.append("routing.model_resolution.requested_profile must match functional_agent_profile")
    for key in ("configured_model", "effective_model"):
        model = value.get(key)
        if model is not None and not _is_nonempty_string(model):
            errors.append(f"routing.model_resolution.{key} must be a non-empty string or null")
        if isinstance(model, str) and (DISALLOWED_TEST_MODEL in model or not model.strip()):
            errors.append(f"routing.model_resolution.{key} uses a disallowed model")
    if not isinstance(value.get("fallback_used"), bool):
        errors.append("routing.model_resolution.fallback_used must be boolean")
    if value.get("fallback_reason") is not None and not _is_nonempty_string(value.get("fallback_reason")):
        errors.append("routing.model_resolution.fallback_reason must be a non-empty string or null")
    if value.get("capability_status") not in {"resolved", "degraded", "blocked"}:
        errors.append("routing.model_resolution.capability_status is invalid")
    if value.get("resolution_result") not in RESOLUTION_RESULTS:
        errors.append("routing.model_resolution.resolution_result is invalid")
    if value.get("source") not in {"task", "project", "user", "built-in", "current"}:
        errors.append("routing.model_resolution.source is invalid")
    result = value.get("resolution_result")
    if result == "resolved" and (
        value.get("capability_status") != "resolved"
        or value.get("fallback_used") is not False
        or not _is_nonempty_string(value.get("configured_model"))
        or value.get("effective_model") != value.get("configured_model")
        or value.get("fallback_reason") is not None
    ):
        errors.append("resolved model_resolution is inconsistent")
    elif result == "fallback" and (
        value.get("capability_status") != "degraded"
        or value.get("fallback_used") is not True
        or not _is_nonempty_string(value.get("configured_model"))
        or not _is_nonempty_string(value.get("effective_model"))
        or not _is_nonempty_string(value.get("fallback_reason"))
    ):
        errors.append("fallback model_resolution is inconsistent")
    elif result == "blocked" and (
        value.get("capability_status") != "blocked"
        or value.get("fallback_used") is not False
        or value.get("effective_model") is not None
        or not _is_nonempty_string(value.get("fallback_reason"))
    ):
        errors.append("blocked model_resolution is inconsistent")
    return errors


def _load_functional_agent_contract():
    path = Path(__file__).resolve().parents[3] / "scripts/functional_agent_profiles.py"
    if not path.is_file():
        return None, [f"missing Bruce Functional Agent resolver: {path}"]
    spec = importlib.util.spec_from_file_location("bruce_functional_agent_profiles", path)
    if spec is None or spec.loader is None:
        return None, ["cannot load Bruce Functional Agent resolver"]
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as error:  # pragma: no cover - defensive fail-closed boundary
        return None, [f"cannot load Bruce Functional Agent resolver: {error}"]
    return module, []


def _validate_functional_packet(packet: Any, profile_id: str, model_resolution: dict[str, Any]) -> list[str]:
    if not isinstance(packet, dict):
        return ["routing.functional_packet must be a Bruce v1 Task Packet mapping"]
    module, errors = _load_functional_agent_contract()
    if module is None:
        return errors
    try:
        module.validate_task_packet(packet, profile_id=profile_id)
    except Exception as error:
        errors.append(f"routing.functional_packet violates Bruce Task Packet contract: {error}")
    if packet.get("model_resolution") != model_resolution:
        errors.append("routing.functional_packet.model_resolution must equal routing.model_resolution")
    return errors


def validate_dispatch(data: Any) -> list[str]:
    """Return deterministic validation errors for a Test Dispatch v1 request."""

    if not _is_mapping(data):
        return ["Dispatch must be a mapping"]
    errors = _unknown_keys(data, DISPATCH_KEYS, "Dispatch")
    errors.extend(_validate_identity(data, "Dispatch"))
    for key in ("feature_area", "business_flow", "actor"):
        if not _is_nonempty_string(data.get(key)):
            errors.append(f"Dispatch.{key} must be a non-empty string")
    declaration_errors, declarations = _validate_track_declarations(data.get("tracks"))
    errors.extend(declaration_errors)
    routing = data.get("routing")
    if not _is_mapping(routing):
        errors.append("Dispatch.routing must be a mapping")
    else:
        errors.extend(_unknown_keys(routing, ROUTING_KEYS, "Dispatch.routing"))
        if routing.get("resolver") != "bruce-functional-agent-resolver":
            errors.append("Dispatch.routing.resolver must be bruce-functional-agent-resolver")
        if not _unique_string_list(routing.get("required_capabilities", [])):
            errors.append("Dispatch.routing.required_capabilities must be a unique string list")
        if not isinstance(routing.get("functional_agent_profile"), str) or routing.get("functional_agent_profile") not in ROUTING_PROFILES:
            errors.append("Dispatch.routing.functional_agent_profile must be an existing Bruce Functional Agent Profile")
        profile_id = routing.get("functional_agent_profile") if isinstance(routing.get("functional_agent_profile"), str) else None
        errors.extend(_validate_model_resolution(routing.get("model_resolution"), expected_profile=profile_id))
        if isinstance(routing.get("model_resolution"), dict):
            errors.extend(_validate_functional_packet(routing.get("functional_packet"), profile_id or "", routing["model_resolution"]))
        else:
            errors.append("Dispatch.routing.functional_packet cannot be checked without model_resolution")
        access = routing.get("subagent_browser_access")
        if access is not None and access != "forbidden":
            errors.append("Dispatch.routing.subagent_browser_access must be forbidden")
        visual_scope = routing.get("visual_scope")
        if visual_scope is not None and (not isinstance(visual_scope, str) or visual_scope not in VISUAL_SCOPES):
            errors.append("Dispatch.routing.visual_scope is invalid")
        selected_ui = isinstance(data.get("tracks"), list) and any(
            isinstance(item, dict) and item.get("track") == "ui" for item in data["tracks"]
        )
        if selected_ui and access != "forbidden":
            errors.append("UI dispatch requires routing.subagent_browser_access=forbidden")
        if selected_ui and visual_scope not in {"browser-smoke", "browser-layout"}:
            errors.append("UI dispatch requires an explicit browser visual_scope")
    if DISALLOWED_TEST_MODEL in repr(data):
        errors.append("disallowed model is not allowed in test-dispatch")
    if isinstance(routing, dict) and any(key in routing for key in ("model_router", "model_selector", "private_router")):
        errors.append("Dispatch must use Bruce resolver; private model routing is forbidden")
    errors.extend(_scan_sensitive_values(data))
    return sorted(set(errors))


def _validate_string_fields(result: dict[str, Any], track_label: str) -> list[str]:
    errors: list[str] = []
    for key in ("commands", "browser_actions", "assertions", "blockers", "unverified_gates", "operation_refs", "account_refs"):
        if key in result and not _string_list(result[key]):
            errors.append(f"{track_label}.{key} must be a list of non-empty strings")
    return errors


def _validate_evidence_records(value: Any, label: str, *, required: bool) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, list):
        return [f"{label} must be a list"]
    if required and not value:
        errors.append(f"{label} is required for passed results")
    for index, record in enumerate(value):
        record_label = f"{label}[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{record_label} must be a mapping")
            continue
        errors.extend(_unknown_keys(record, EVIDENCE_RECORD_KEYS, record_label))
        if not isinstance(record.get("kind"), str) or record.get("kind") not in EVIDENCE_KINDS:
            errors.append(f"{record_label}.kind is invalid")
        if not _is_nonempty_string(record.get("ref")):
            errors.append(f"{record_label}.ref must be a non-empty redacted reference")
        if not isinstance(record.get("status"), str) or record.get("status") not in EVIDENCE_STATUSES:
            errors.append(f"{record_label}.status is invalid")
    if required and any(
        isinstance(record, dict) and record.get("status") == "missing" for record in value
    ):
        errors.append(f"{label} must not contain missing evidence for passed results")
    return errors


def _validate_capture_time(value: Any, label: str) -> bool:
    if not _is_nonempty_string(value):
        return False
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _validate_browser_evidence(
    value: Any,
    label: str,
    evidence_paths: list[str],
    *,
    required: bool,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return [f"{label} must be a mapping"] if required or value is not None else []
    errors.extend(_unknown_keys(value, BROWSER_EVIDENCE_KEYS, label))
    if not isinstance(value.get("provider"), str) or value.get("provider") not in BROWSER_PROVIDERS:
        errors.append(f"{label}.provider must be ego-lite or chrome")
    for key in ("target", "session", "visible_result"):
        if not _is_nonempty_string(value.get(key)):
            errors.append(f"{label}.{key} must be a non-empty string")
    scope = value.get("visual_scope")
    if not isinstance(scope, str) or scope not in {"browser-smoke", "browser-layout"}:
        errors.append(f"{label}.visual_scope must be browser-smoke or browser-layout")
    if not _unique_string_list(value.get("actions")):
        errors.append(f"{label}.actions must be a unique non-empty string list")
    if not _validate_capture_time(value.get("capture_time"), f"{label}.capture_time"):
        errors.append(f"{label}.capture_time must be an ISO-8601 timestamp with timezone")
    screenshot_path = value.get("screenshot_path")
    if not _safe_relative_path(screenshot_path):
        errors.append(f"{label}.screenshot_path must be a safe repository-relative path")
    elif evidence_paths and _normalise_path(screenshot_path) not in {
        _normalise_path(path) for path in evidence_paths if isinstance(path, str)
    }:
        errors.append(f"{label}.screenshot_path must be listed in evidence_paths")
    if scope == "browser-layout":
        viewport = value.get("viewport")
        if not isinstance(viewport, dict):
            errors.append(f"{label}.viewport is required for browser-layout")
        else:
            errors.extend(_unknown_keys(viewport, VIEWPORT_KEYS, f"{label}.viewport"))
            for key in ("width", "height"):
                if not _is_positive_int(viewport.get(key)):
                    errors.append(f"{label}.viewport.{key} must be a positive integer")
        if not value.get("geometry"):
            errors.append(f"{label}.geometry is required for browser-layout")
        if not value.get("overflow"):
            errors.append(f"{label}.overflow is required for browser-layout")
    return errors


def _validate_result_revisions(data: dict[str, Any], statuses: list[str]) -> list[str]:
    if "passed" not in statuses:
        return []
    errors: list[str] = []
    if not _is_nonempty_string(data.get("profile_id")):
        errors.append("passed Track Result requires profile_id")
    if not _is_positive_int(data.get("profile_revision")):
        errors.append("passed Track Result requires positive profile_revision")
    if not _is_nonempty_string(data.get("basis_revision")):
        errors.append("passed Track Result requires basis_revision")
    if not _is_nonempty_string(data.get("evidence_revision")):
        errors.append("passed Track Result requires evidence_revision")
    if not isinstance(data.get("profile_content_hash"), str) or not PROFILE_HASH_PATTERN.fullmatch(
        data.get("profile_content_hash", "")
    ):
        errors.append("passed Track Result requires a sha256 profile_content_hash")
    return errors


def _validate_track_result(track: str, result: Any, scenario_id: Any, scenario_version: Any) -> list[str]:
    label = f"tracks.{track}"
    errors: list[str] = []
    if not _is_mapping(result):
        return [f"{label} must be a mapping"]
    errors.extend(_unknown_keys(result, TRACK_RESULT_KEYS, label))
    if result.get("scenario_id") != scenario_id:
        errors.append(f"{label}.scenario_id must match top-level scenario_id")
    if result.get("scenario_version") != scenario_version:
        errors.append(f"{label}.scenario_version must match top-level scenario_version")
    if result.get("track") is not None and result.get("track") != track:
        errors.append(f"{label}.track must match its track key")
    status = result.get("status")
    if not isinstance(status, str) or status not in SCENARIO_STATUSES:
        errors.append(f"{label}.status is invalid")
    mode = result.get("execution_mode")
    allowed_modes = API_MODES if track == "api" else UI_MODES
    if not isinstance(mode, str) or mode not in allowed_modes:
        errors.append(f"{label}.execution_mode is invalid for {track}")
    if not _is_safe_namespace(result.get("data_namespace")):
        errors.append(f"{label}.data_namespace must be a safe lowercase namespace")
    for key in ("allowed_paths", "evidence_paths", "modified_paths"):
        errors.extend(_path_list(result.get(key, []), f"{label}.{key}"))
    errors.extend(_validate_string_fields(result, label))
    for key in ("commands", "browser_actions", "assertions", "blockers", "unverified_gates"):
        if key not in result:
            errors.append(f"{label}.{key} must be declared")
    if not isinstance(result.get("persistence_required"), bool):
        errors.append(f"{label}.persistence_required must be boolean")
    if "authoritative_readback" not in result or not _string_list(result.get("authoritative_readback")):
        errors.append(f"{label}.authoritative_readback must be a list of non-empty strings")
    errors.extend(_validate_evidence_records(result.get("evidence_records"), f"{label}.evidence_records", required=status == "passed"))
    if track == "ui" and status == "passed" and "browser_evidence" not in result:
        errors.append("UI passed Track Result must declare browser_evidence")
    if "browser_evidence" in result:
        errors.extend(_validate_browser_evidence(result.get("browser_evidence"), f"{label}.browser_evidence", result.get("evidence_paths", []), required=track == "ui" and status == "passed"))
    if track == "api" and result.get("browser_actions"):
        errors.append("API track must not contain browser_actions")
    if result.get("modified_paths") and not result.get("allowed_paths"):
        errors.append(f"{label}.modified_paths require declared allowed_paths")
    elif result.get("modified_paths") and (
        not isinstance(result.get("modified_paths"), list)
        or not isinstance(result.get("allowed_paths"), list)
        or not _paths_within(result["modified_paths"], result["allowed_paths"])
    ):
        errors.append(f"{label}.modified_paths must remain within allowed_paths")
    if status == "passed":
        if not result.get("evidence_paths"):
            errors.append(f"{label}.passed requires evidence_paths")
        elif any(isinstance(path, str) and ("<" in path or ">" in path) for path in result.get("evidence_paths", [])):
            errors.append(f"{label}.passed evidence_paths must not contain placeholders")
        if not result.get("assertions"):
            errors.append(f"{label}.passed requires assertions")
        if result.get("blockers"):
            errors.append(f"{label}.passed must not contain blockers")
        if result.get("unverified_gates"):
            errors.append(f"{label}.passed must not contain unverified_gates")
        if track == "ui" and not result.get("browser_actions"):
            errors.append("UI passed requires real browser_actions")
        if track == "api" and not result.get("commands"):
            errors.append("API passed requires an actual command or test invocation")
        if result.get("persistence_required") is True and not result.get("authoritative_readback"):
            errors.append(f"{label}.passed requires authoritative_readback when persistence_required=true")
    elif status == "failed":
        if not result.get("evidence_paths") and not result.get("assertions"):
            errors.append(f"{label}.failed requires evidence_paths or assertions")
    elif status == "blocked" and not result.get("blockers"):
        errors.append(f"{label}.blocked requires at least one blocker")
    return errors


def validate_track_results(data: Any, *, allow_overall_status: bool = True) -> list[str]:
    """Return deterministic validation errors for a Track Result v1 document."""

    if not _is_mapping(data):
        return ["Track Result document must be a mapping"]
    errors = _unknown_keys(data, TRACK_RESULT_ROOT_KEYS, "Track Result")
    if data.get("version") != SCHEMA_VERSION:
        errors.append(f"Track Result.version must be {SCHEMA_VERSION}")
    scenario_id = data.get("scenario_id")
    if not _is_nonempty_string(scenario_id) or not ID_PATTERN.fullmatch(scenario_id.strip()):
        errors.append("Track Result.scenario_id must be a non-empty stable string")
    scenario_version = data.get("scenario_version")
    if not _is_positive_int(scenario_version):
        errors.append("Track Result.scenario_version must be a positive integer")
    required = data.get("required_tracks")
    if not isinstance(required, list) or not required:
        errors.append("Track Result.required_tracks must be a non-empty list")
        required = []
    elif not all(isinstance(track, str) and track in TRACKS for track in required):
        errors.append("Track Result.required_tracks may contain only api and ui")
    if isinstance(required, list) and all(isinstance(track, str) for track in required) and len(required) != len(set(required)):
        errors.append("Track Result.required_tracks must be unique")
    tracks = data.get("tracks")
    if not _is_mapping(tracks):
        errors.append("Track Result.tracks must be a mapping")
        tracks = {}
    else:
        declared_tracks = {track for track in required if isinstance(track, str)}
        extra = set(tracks) - declared_tracks
        if extra:
            errors.append(f"Track Result.tracks contains undeclared tracks: {sorted(extra)}")
        for track in required:
            if not isinstance(track, str):
                continue
            if track not in tracks:
                errors.append(f"Track Result.tracks is missing required track: {track}")
            else:
                errors.extend(_validate_track_result(track, tracks[track], scenario_id, scenario_version))
    status_values = []
    if isinstance(tracks, dict):
        for track in required:
            if isinstance(track, str) and isinstance(tracks.get(track), dict) and isinstance(tracks[track].get("status"), str):
                status_values.append(tracks[track]["status"])
    errors.extend(_validate_result_revisions(data, status_values))

    if "overall_status" in data:
        if not allow_overall_status:
            errors.append("overall_status is derived and must not be supplied as input")
        elif not isinstance(data.get("overall_status"), str) or data.get("overall_status") not in SCENARIO_STATUSES:
            errors.append("Track Result.overall_status is invalid")
        elif len(status_values) == len(required) and status_values:
            expected_overall = _aggregate_statuses(status_values)
            if data.get("overall_status") != expected_overall:
                errors.append(f"Track Result.overall_status must equal derived status {expected_overall}")

    namespaces: dict[str, str] = {}
    paths: dict[str, list[str]] = {}
    if isinstance(tracks, dict):
        for track in required:
            if not isinstance(track, str):
                continue
            result = tracks.get(track)
            if not isinstance(result, dict):
                continue
            namespace = result.get("data_namespace")
            if _is_nonempty_string(namespace) and namespace in namespaces:
                errors.append(f"API/UI data namespaces must be distinct: {namespace}")
            elif _is_nonempty_string(namespace):
                namespaces[namespace] = track
            paths[track] = result.get("allowed_paths", [])
    if "api" in paths and "ui" in paths:
        api_paths = [path for path in paths["api"] if isinstance(path, str)]
        ui_paths = [path for path in paths["ui"] if isinstance(path, str)]
        for left in api_paths:
            for right in ui_paths:
                if _paths_overlap(left, right):
                    errors.append(f"API/UI allowed_paths overlap: {left} vs {right}")
    errors.extend(_scan_sensitive_values(data))
    return sorted(set(errors))


def validate_track_results_for_context(data: Any, context: Any) -> list[str]:
    """Validate Track Results against the current Scenario/Profile/evidence run basis."""

    errors = validate_track_results(data)
    if not isinstance(context, dict):
        return sorted(set(errors + ["Track Result context must be a mapping"]))
    if not isinstance(data, dict):
        return sorted(set(errors))
    for key in ("scenario_id", "scenario_version", "profile_id", "profile_revision", "basis_revision", "evidence_revision"):
        if key in context and data.get(key) != context.get(key):
            errors.append(f"Track Result.{key} does not match current context")
    if "profile_content_hash" in context and data.get("profile_content_hash") != context.get("profile_content_hash"):
        errors.append("Track Result.profile_content_hash does not match current context")
    if "required_tracks" in context and data.get("required_tracks") != context.get("required_tracks"):
        errors.append("Track Result.required_tracks does not match current context")
    expected_provider = context.get("browser_provider")
    expected_scope = context.get("visual_scope")
    ui = data.get("tracks", {}).get("ui") if isinstance(data.get("tracks"), dict) else None
    if isinstance(ui, dict) and isinstance(ui.get("browser_evidence"), dict):
        if expected_provider is not None and ui["browser_evidence"].get("provider") != expected_provider:
            errors.append("UI browser evidence provider does not match current context")
        if expected_scope is not None and ui["browser_evidence"].get("visual_scope") != expected_scope:
            errors.append("UI browser evidence visual_scope does not match current context")
    return sorted(set(errors))


def _aggregate_statuses(statuses: list[str]) -> str:
    if "failed" in statuses:
        return "failed"
    if "blocked" in statuses:
        return "blocked"
    if statuses and all(status == "passed" for status in statuses):
        return "passed"
    if "executed" in statuses:
        return "executed"
    return "designed"


def aggregate_track_results(data: dict[str, Any]) -> dict[str, Any]:
    """Validate and aggregate required track statuses, preserving track evidence."""

    errors = validate_track_results(data, allow_overall_status=False)
    if errors:
        raise ContractValidationError(errors)
    result = deepcopy(data)
    statuses = [result["tracks"][track]["status"] for track in result["required_tracks"]]
    overall = _aggregate_statuses(statuses)
    result["overall_status"] = overall
    return result
