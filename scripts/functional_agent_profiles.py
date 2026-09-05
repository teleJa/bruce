#!/usr/bin/env python3
"""Functional Agent Profile and Packet contracts for Bruce."""
from __future__ import annotations

import copy
import fnmatch
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

ROOT = Path(__file__).resolve().parents[1]
BUILTIN_PROFILE_PATH = ROOT / "skills/bruce/references/model-profiles.yaml"
SCHEMA_VERSION = 1
PROFILE_IDS = ("inspector", "implementer", "prototype-generator", "verifier", "reviewer")
PACKET_OUTPUTS = {"task_evidence_packet", "verification_packet", "review_packet"}
TERMINAL_FIELDS = {"Design", "Completion", "verdict", "approval"}


class ContractError(ValueError):
    """Raised when a Profile or Packet violates the v1 contract."""


@dataclass(frozen=True)
class ModelResolution:
    requested_profile: str
    configured_model: str | None
    effective_model: str | None
    fallback_used: bool
    fallback_reason: str | None
    capability_status: str
    resolution_result: str
    source: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "requested_profile": self.requested_profile,
            "configured_model": self.configured_model,
            "effective_model": self.effective_model,
            "fallback_used": self.fallback_used,
            "fallback_reason": self.fallback_reason,
            "capability_status": self.capability_status,
            "resolution_result": self.resolution_result,
            "source": self.source,
        }


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ContractError(f"missing profile file: {path}")
    except yaml.YAMLError as exc:
        raise ContractError(f"invalid YAML: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"profile file must be a mapping: {path}")
    return value


def _merge(base: dict[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(result.get(key), Mapping):
            result[key] = _merge(dict(result[key]), value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def load_builtin_profiles(path: Path = BUILTIN_PROFILE_PATH) -> dict[str, dict[str, Any]]:
    document = _load_yaml(path)
    if document.get("version") != SCHEMA_VERSION:
        raise ContractError("profile registry version must be 1")
    profiles = document.get("profiles")
    if not isinstance(profiles, dict):
        raise ContractError("profile registry must contain profiles mapping")
    if set(profiles) != set(PROFILE_IDS):
        raise ContractError("profile registry must contain exactly the five built-in profiles")
    return {profile_id: dict(profile) for profile_id, profile in profiles.items()}


def _validate_model_name(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{label} must be a non-empty model name")
    if value.startswith(("/", "~")) or "\\" in value or ".." in Path(value).parts:
        raise ContractError(f"{label} contains an unsafe path")
    if re.search(r"(?:^sk-|token|secret|api[_-]?key)", value, re.IGNORECASE):
        raise ContractError(f"{label} contains a credential-like value")
    return value


def _load_override(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None or not path.is_file():
        return {}

    document = _load_yaml(path)
    if document.get("version") != SCHEMA_VERSION:
        raise ContractError(f"override version must be 1: {path}")

    profiles = document.get("profiles", {})
    if not isinstance(profiles, dict) or not set(profiles).issubset(PROFILE_IDS):
        raise ContractError(f"override contains unknown profile: {path}")

    allowed_fields = {"default_model", "reasoning_effort", "fallback"}
    reasoning_values = {"low", "medium", "high", "max"}
    for profile_id, values in profiles.items():
        if not isinstance(values, dict):
            raise ContractError(f"override profile must be a mapping: {profile_id}")
        forbidden = set(values) - allowed_fields
        if forbidden:
            raise ContractError(f"override changes structural fields: {sorted(forbidden)}")
        if "default_model" in values:
            _validate_model_name(values["default_model"], f"override {profile_id}.default_model")
        if "reasoning_effort" in values and (
            not isinstance(values["reasoning_effort"], str)
            or values["reasoning_effort"] not in reasoning_values
        ):
            raise ContractError(f"override reasoning_effort is invalid for {profile_id}")
        if "fallback" in values:
            expected_fallback = "blocked" if profile_id == "prototype-generator" else "current"
            if values["fallback"] != expected_fallback:
                raise ContractError(
                    f"override fallback must be {expected_fallback} for {profile_id}"
                )

    return {profile_id: dict(values) for profile_id, values in profiles.items()}


def resolve_profile(
    profile_id: str,
    *,
    current_model: str | None,
    task_override: Mapping[str, Any] | None = None,
    task_packet: Mapping[str, Any] | None = None,
    project_path: Path | None = None,
    user_path: Path | None = None,
    available_models: set[str] | None = None,
    clean_context_available: bool = True,
    required_tools: set[str] | None = None,
    fallback_allowed: bool = True,
) -> tuple[dict[str, Any], ModelResolution, dict[str, Any]]:
    profiles = load_builtin_profiles()
    if not isinstance(profile_id, str) or profile_id not in profiles:
        raise ContractError(f"unknown profile: {profile_id}")
    if task_override is not None and not isinstance(task_override, Mapping):
        raise ContractError("task_override must be a mapping or null")
    if task_packet is not None:
        if not isinstance(task_packet, Mapping):
            raise ContractError("task_packet must be a mapping or null")
        validate_task_packet(task_packet, profile_id=profile_id)
    for path, label in ((user_path, "user"), (project_path, "project")):
        if path is not None and not isinstance(path, Path):
            raise ContractError(f"{label}_path must be a Path or null")

    profile = profiles[profile_id]
    source = "built-in"
    for path, label in ((user_path, "user"), (project_path, "project")):
        override = _load_override(path)
        if profile_id not in override:
            continue
        profile = _merge(profile, override[profile_id])
        source = label

    task_values = dict(task_override or {})
    packet_model = None
    if task_packet is not None:
        packet_model = task_packet["task_packet"].get("model_override")
    if profile_id == "prototype-generator" and (
        packet_model is not None or "model" in task_values
    ):
        raise ContractError(
            "prototype-generator model must come from its resolved Profile configuration"
        )
    if packet_model is not None and "model" not in task_values:
        task_values["model"] = packet_model
    unknown = set(task_values) - {"model", "reasoning_effort", "fallback"}
    if unknown:
        raise ContractError(f"unknown task override fields: {sorted(unknown)}")
    if "model" in task_values:
        profile["default_model"] = _validate_model_name(task_values["model"], "task model override")
        source = "task"
    for field in ("reasoning_effort", "fallback"):
        if field in task_values:
            profile[field] = task_values[field]
    if profile.get("fallback") not in {"current", "blocked"}:
        raise ContractError("profile fallback must be current or blocked")
    if not isinstance(profile.get("reasoning_effort"), str) or profile.get("reasoning_effort") not in {"low", "medium", "high", "max"}:
        raise ContractError("profile reasoning_effort is invalid")

    configured = _validate_model_name(profile.get("default_model"), f"profile {profile_id}.default_model")
    capabilities = profile.get("model_capabilities", {})
    independence = capabilities.get("independence")
    if profile["context"].get("clean") and not clean_context_available and independence == "required":
        resolution = ModelResolution(
            profile_id, configured, None, False, "clean_context_unavailable",
            "blocked", "blocked", source,
        )
    elif required_tools and not required_tools.issubset(set(profile["tools"].get("allow", []))):
        resolution = ModelResolution(
            profile_id, configured, None, False, "required_tool_unavailable",
            "blocked", "blocked", source,
        )
    elif available_models is not None and configured in available_models:
        resolution = ModelResolution(
            profile_id, configured, configured, False, None,
            "resolved", "resolved", source,
        )
    elif fallback_allowed and current_model and profile.get("fallback") == "current":
        current_available = available_models is None or current_model in available_models
        if current_available:
            reason = "host_model_unconfirmed" if available_models is None else "configured_model_unavailable"
            resolution = ModelResolution(
                profile_id, configured, current_model, True, reason,
                "degraded", "fallback", source,
            )
        else:
            resolution = ModelResolution(
                profile_id, configured, None, False, "current_model_unavailable",
                "blocked", "blocked", source,
            )
    else:
        reason = "current_model_unavailable" if current_model is None else "configured_model_unavailable"
        resolution = ModelResolution(
            profile_id, configured, None, False, reason,
            "blocked", "blocked", source,
        )

    spawn_args: dict[str, Any] = {
        "reasoning_effort": profile.get("reasoning_effort"),
        "model_resolution": resolution.as_dict(),
    }
    if resolution.resolution_result == "resolved":
        spawn_args["model"] = resolution.effective_model
    return profile, resolution, spawn_args


def _assert_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be a mapping")
    return value


def validate_task_packet(packet: Mapping[str, Any], profile_id: str | None = None) -> None:
    packet = _assert_mapping(packet, "task packet")
    allowed_top_level = {"schema_version", "profile_id", "task_packet", "model_resolution"}
    if packet.get("schema_version") != SCHEMA_VERSION:
        raise ContractError("packet schema_version must be 1")
    if set(packet) - allowed_top_level:
        raise ContractError("task packet has unknown top-level fields")
    if "model_resolution" in packet:
        _validate_model_resolution(packet["model_resolution"], expected_profile=packet.get("profile_id"))

    actual_profile = packet.get("profile_id")
    if not isinstance(actual_profile, str) or actual_profile not in PROFILE_IDS or (profile_id and actual_profile != profile_id):
        raise ContractError("packet profile_id is invalid or mismatched")
    profile = load_builtin_profiles()[actual_profile]

    task = _assert_mapping(packet.get("task_packet"), "task_packet")
    task_fields = {
        "task_id", "task_kind", "objective", "context", "tools", "allowed_paths",
        "model_capabilities", "evidence", "output", "stop_conditions", "model_override",
    }
    required_fields = task_fields - {"model_override"}
    missing = required_fields - set(task)
    if missing:
        raise ContractError(f"task_packet missing fields: {sorted(missing)}")
    if set(task) - task_fields:
        raise ContractError("task_packet has unknown fields")
    if not isinstance(task["task_id"], str) or not task["task_id"].strip():
        raise ContractError("task_packet task_id must be non-empty")
    if not isinstance(task["objective"], str) or not task["objective"].strip():
        raise ContractError("task_packet objective must be non-empty")

    task_kinds = {
        "inspector": {"inspect"},
        "implementer": {"implement", "throwaway_prototype"},
        "prototype-generator": {"prototype_generate"},
        "verifier": {"verify"},
        "reviewer": {"review"},
    }
    if not isinstance(task["task_kind"], str) or task["task_kind"] not in task_kinds[actual_profile]:
        raise ContractError("task_packet task_kind does not match profile")
    if not isinstance(task["output"], str) or task["output"] != profile["output"]:
        raise ContractError("task packet output does not match profile")

    context = _assert_mapping(task["context"], "context")
    if set(context) - {"inherit", "sources"}:
        raise ContractError("context has unknown fields")
    if not isinstance(context.get("inherit"), str) or context.get("inherit") not in {"none", "task", "author"}:
        raise ContractError("context inherit is invalid")
    expected_inherit = profile.get("context", {}).get("inherit")
    if context["inherit"] != expected_inherit:
        raise ContractError(f"{actual_profile} context inherit does not match profile")
    _validate_string_list(context.get("sources"), "context sources")

    tools = _assert_mapping(task["tools"], "tools")
    if set(tools) - {"allow", "deny"}:
        raise ContractError("tools has unknown fields")
    _validate_string_list(tools.get("allow"), "tools allow")
    _validate_string_list(tools.get("deny"), "tools deny")
    profile_tools = profile["tools"]
    if not set(tools["allow"]).issubset(set(profile_tools["allow"])):
        raise ContractError("task packet requests a tool outside profile allow")
    if set(tools["allow"]) & set(profile_tools["deny"]):
        raise ContractError("task packet requests a profile-denied tool")

    paths = task["allowed_paths"]
    if not isinstance(paths, list) or not all(isinstance(path, str) for path in paths):
        raise ContractError("allowed_paths must be a list of strings")
    for path in paths:
        if Path(path).is_absolute() or ".." in Path(path).parts:
            raise ContractError(f"allowed path must be repository-relative: {path}")
    if actual_profile in {"inspector", "prototype-generator", "verifier", "reviewer"} and paths:
        raise ContractError(f"{actual_profile} must have empty allowed_paths")

    capabilities = _assert_mapping(task["model_capabilities"], "model_capabilities")
    if set(capabilities) - {"required", "preferred", "independence"}:
        raise ContractError("model_capabilities has unknown fields")
    _validate_string_list(capabilities.get("required"), "model_capabilities required")
    _validate_string_list(capabilities.get("preferred"), "model_capabilities preferred")
    if not isinstance(capabilities.get("independence"), str) or capabilities.get("independence") not in {"required", "preferred", "none"}:
        raise ContractError("model_capabilities independence is invalid")
    expected_independence = profile.get("model_capabilities", {}).get("independence")
    if capabilities["independence"] != expected_independence:
        raise ContractError(f"{actual_profile} independence does not match profile")

    evidence = _assert_mapping(task["evidence"], "evidence")
    if set(evidence) - {"acceptance_ids", "required"}:
        raise ContractError("evidence has unknown fields")
    _validate_string_list(evidence.get("acceptance_ids"), "evidence acceptance_ids", allow_empty=False)
    _validate_string_list(evidence.get("required"), "evidence required", allow_empty=False)
    _validate_string_list(task["stop_conditions"], "stop_conditions", allow_empty=False)

    if "model_override" in task and task["model_override"] is not None:
        _validate_model_name(task["model_override"], "task_packet model_override")


def _validate_string_list(value: Any, label: str, *, allow_empty: bool = True) -> None:
    if not isinstance(value, list) or (not allow_empty and not value) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ContractError(f"{label} must be a {'' if allow_empty else 'non-empty '}string list")


def _validate_model_resolution(
    resolution: Mapping[str, Any],
    *,
    expected_profile: str | None = None,
) -> None:
    resolution = _assert_mapping(resolution, "model_resolution")
    resolution_fields = {
        "requested_profile", "configured_model", "effective_model", "fallback_used",
        "fallback_reason", "capability_status", "resolution_result", "source",
    }
    if set(resolution) != resolution_fields:
        raise ContractError("model_resolution fields are incomplete or unknown")
    if not isinstance(resolution["requested_profile"], str) or resolution["requested_profile"] not in PROFILE_IDS:
        raise ContractError("model_resolution requested_profile is invalid")
    if expected_profile is not None and resolution["requested_profile"] != expected_profile:
        raise ContractError("model_resolution profile does not match packet profile")
    if resolution["configured_model"] is not None:
        _validate_model_name(resolution["configured_model"], "model_resolution configured_model")
    if resolution["effective_model"] is not None:
        _validate_model_name(resolution["effective_model"], "model_resolution effective_model")
    if not isinstance(resolution["fallback_used"], bool):
        raise ContractError("model_resolution fallback_used must be boolean")
    if resolution["fallback_reason"] is not None and not isinstance(resolution["fallback_reason"], str):
        raise ContractError("model_resolution fallback_reason must be a string or null")
    if not isinstance(resolution["capability_status"], str) or resolution["capability_status"] not in {"resolved", "degraded", "blocked"}:
        raise ContractError("model_resolution capability_status is invalid")
    if not isinstance(resolution["resolution_result"], str) or resolution["resolution_result"] not in {"resolved", "fallback", "blocked"}:
        raise ContractError("model_resolution resolution_result is invalid")
    if not isinstance(resolution["source"], str) or resolution["source"] not in {"task", "project", "user", "built-in", "current"}:
        raise ContractError("model_resolution source is invalid")

    result = resolution["resolution_result"]
    if result == "resolved":
        if (
            resolution["capability_status"] != "resolved"
            or resolution["fallback_used"]
            or not resolution["configured_model"]
            or resolution["effective_model"] != resolution["configured_model"]
            or resolution["fallback_reason"] is not None
        ):
            raise ContractError("resolved model_resolution is inconsistent")
    elif result == "fallback":
        if (
            resolution["capability_status"] != "degraded"
            or not resolution["fallback_used"]
            or not resolution["configured_model"]
            or not resolution["effective_model"]
            or not resolution["fallback_reason"]
        ):
            raise ContractError("fallback model_resolution is inconsistent")
    elif (
        resolution["capability_status"] != "blocked"
        or resolution["effective_model"] is not None
        or resolution["fallback_used"]
        or not resolution["fallback_reason"]
    ):
        raise ContractError("blocked model_resolution is inconsistent")


def validate_output_packet(packet: Mapping[str, Any], output_type: str) -> None:
    packet = _assert_mapping(packet, "output packet")
    common = {"schema_version", "status", "output_type", "model_resolution", "gate_verdict"}
    if packet.get("schema_version") != SCHEMA_VERSION or packet.get("output_type") != output_type:
        raise ContractError("output packet schema or output_type is invalid")
    status = packet.get("status")
    if not isinstance(status, str) or status not in {"completed", "blocked", "failed"}:
        raise ContractError("output packet status is invalid")
    if set(packet) & TERMINAL_FIELDS:
        raise ContractError("agent packet cannot contain Design/Completion/verdict/approval")
    if packet.get("gate_verdict") != "absent":
        raise ContractError("agent packet gate_verdict must be absent")
    expected_profile = {"verification_packet": "verifier", "review_packet": "reviewer"}.get(output_type)
    _validate_model_resolution(packet.get("model_resolution"), expected_profile=expected_profile)
    if output_type == "task_evidence_packet" and packet["model_resolution"]["requested_profile"] not in {"inspector", "implementer", "prototype-generator"}:
        raise ContractError("task_evidence_packet must come from inspector, implementer, or prototype-generator")

    packet_fields = {
        "task_evidence_packet": common | {"changed_files", "commands", "evidence", "assumptions", "evidence_gaps"},
        "verification_packet": common | {"acceptance_ids", "scenario_results", "repro_commands", "evidence_revision"},
        "review_packet": common | {"review_subject", "review_mode", "review_mode_reason", "findings", "review_matrix"},
    }
    if not isinstance(output_type, str) or output_type not in packet_fields:
        raise ContractError("unknown output packet type")
    if set(packet) != packet_fields[output_type]:
        raise ContractError("output packet fields are incomplete or unknown")

    if output_type == "task_evidence_packet":
        _validate_string_list(packet["changed_files"], "changed_files")
        _validate_string_list(packet["evidence"], "evidence")
        _validate_string_list(packet["assumptions"], "assumptions")
        _validate_string_list(packet["evidence_gaps"], "evidence_gaps")
        if not isinstance(packet["commands"], list) or not all(isinstance(item, Mapping) for item in packet["commands"]):
            raise ContractError("commands must be a list of mappings")
        for command in packet["commands"]:
            if set(command) != {"command", "result", "evidence"}:
                raise ContractError("command evidence fields are incomplete or unknown")
            if not isinstance(command["command"], str) or not command["command"].strip() or not isinstance(command["evidence"], str) or not command["evidence"].strip():
                raise ContractError("command and evidence must be non-empty")
            if not isinstance(command["result"], str) or command["result"] not in {"pass", "fail", "blocked"}:
                raise ContractError("command result is invalid")
    elif output_type == "verification_packet":
        _validate_string_list(packet["acceptance_ids"], "acceptance_ids", allow_empty=False)
        _validate_string_list(packet["repro_commands"], "repro_commands", allow_empty=False)
        if not isinstance(packet["scenario_results"], list) or not all(isinstance(item, Mapping) for item in packet["scenario_results"]):
            raise ContractError("scenario_results must be a list of mappings")
        for scenario in packet["scenario_results"]:
            if set(scenario) != {"acceptance_id", "result", "evidence", "gaps"}:
                raise ContractError("scenario result fields are incomplete or unknown")
            if not isinstance(scenario["acceptance_id"], str) or not scenario["acceptance_id"].strip():
                raise ContractError("scenario acceptance_id must be non-empty")
            if not isinstance(scenario["result"], str) or scenario["result"] not in {"pass", "fail", "blocked"}:
                raise ContractError("scenario result is invalid")
            _validate_string_list(scenario["evidence"], "scenario evidence")
            _validate_string_list(scenario["gaps"], "scenario gaps")
        if not isinstance(packet["evidence_revision"], str) or not packet["evidence_revision"].strip():
            raise ContractError("verification_packet evidence_revision must be non-empty")
    else:
        review_mode = packet["review_mode"]
        review_reason = packet["review_mode_reason"]
        reasons = {
            "none", "explicit-independent-request", "critical-risk",
            "guarded-multi-component-contract", "guarded-migration-rollout",
            "guarded-semantic-ambiguity", "guarded-weak-evidence",
            "guarded-repeated-repair", "guarded-broad-security-data-impact",
        }
        if not isinstance(review_mode, str) or review_mode not in {"main-agent", "independent"}:
            raise ContractError("review_packet review_mode is invalid")
        if not isinstance(review_reason, str) or review_reason not in reasons:
            raise ContractError("review_packet review_mode_reason is invalid")
        review_subject = packet["review_subject"]
        if not isinstance(review_subject, str) or review_subject not in {"implementation", "plan", "design"}:
            raise ContractError("review_packet review_subject is invalid")
        if not isinstance(packet["findings"], list) or not all(isinstance(item, Mapping) for item in packet["findings"]):
            raise ContractError("findings must be a list of mappings")
        for finding in packet["findings"]:
            if set(finding) != {"severity", "path", "evidence", "issue"}:
                raise ContractError("review finding fields are incomplete or unknown")
            if not isinstance(finding["severity"], str) or finding["severity"] not in {"critical", "high", "medium", "low"}:
                raise ContractError("review finding severity is invalid")
            for field in ("path", "evidence", "issue"):
                if not isinstance(finding[field], str) or not finding[field].strip():
                    raise ContractError(f"review finding {field} must be non-empty")
        if not isinstance(packet["review_matrix"], list) or not all(isinstance(item, Mapping) for item in packet["review_matrix"]):
            raise ContractError("review_matrix must be a list of mappings")
        for row in packet["review_matrix"]:
            if set(row) != {"acceptance_id", "path", "required_layer", "evidence", "result"}:
                raise ContractError("review matrix fields are incomplete or unknown")
            if not all(isinstance(row[field], str) and row[field].strip() for field in ("acceptance_id", "path", "required_layer", "evidence")):
                raise ContractError("review matrix identity/evidence fields must be non-empty")
            if not isinstance(row["result"], str) or row["result"] not in {"pass", "finding", "incomplete"}:
                raise ContractError("review matrix result is invalid")


def validate_changed_paths(profile_id: str, allowed_paths: list[str], changed_paths: list[str]) -> None:
    if profile_id == "inspector" and changed_paths:
        raise ContractError("inspector is read-only")
    for changed in changed_paths:
        if Path(changed).is_absolute() or ".." in Path(changed).parts:
            raise ContractError(f"changed path is unsafe: {changed}")
        if not any(fnmatch.fnmatch(changed, allowed) or changed == allowed for allowed in allowed_paths):
            raise ContractError(f"changed path is outside allowed_paths: {changed}")
