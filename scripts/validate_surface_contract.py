#!/usr/bin/env python3
"""Validate a stack-neutral Bruce UI Surface Contract fixture."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


ALLOWED_CLASSIFICATIONS = {"greenfield", "existing-product-extension"}
ALLOWED_LOCATOR_TYPES = {"file", "route", "template", "view", "source-entry"}
REQUIRED_SURFACE_FIELDS = (
    "surface_id",
    "name",
    "purpose",
    "hierarchy",
    "required_states",
    "interactions",
    "observables",
    "layout_invariants",
    "visual_anchors",
    "viewports",
    "evidence",
    "implementation_mappings",
)
PLACEHOLDER_RE = re.compile(
    r"(?i)(?:\b(?:TODO|TBD|FIXME)\b|待补充|待定|<[^>\n]*>|^none$|^n/a$)"
)
FORBIDDEN_TECHNICAL_KEYS = {"framework", "component_tree", "dom_tree", "ast"}


def _is_mapping(value: Any) -> bool:
    return isinstance(value, dict)


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _contains_placeholder(value: Any, path: str = "contract") -> str | None:
    if isinstance(value, str) and PLACEHOLDER_RE.search(value.strip()):
        return path
    if isinstance(value, dict):
        for key, child in value.items():
            found = _contains_placeholder(child, f"{path}.{key}")
            if found:
                return found
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found = _contains_placeholder(child, f"{path}[{index}]")
            if found:
                return found
    return None


def _duplicate_ids(items: Any, id_key: str, scope: str) -> list[str]:
    if not isinstance(items, list):
        return []
    seen: set[str] = set()
    findings: list[str] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        value = item.get(id_key)
        if not _is_non_empty_string(value):
            continue
        if value in seen:
            findings.append(f"duplicate {id_key} in {scope}: {value}")
        seen.add(value)
    return findings


def _validate_region(region: Any, surface_id: str, index: int) -> list[str]:
    findings: list[str] = []
    path = f"surfaces[{surface_id}].hierarchy[{index}]"
    if not _is_mapping(region):
        return [f"{path} must be an object"]
    for field in ("region_id", "name", "purpose", "parent_region_id"):
        if field not in region or (field != "parent_region_id" and not _is_non_empty_string(region[field])):
            findings.append(f"{path}.{field} is required")
    return findings


def _validate_states(states: Any, surface_id: str) -> list[str]:
    findings: list[str] = []
    if not isinstance(states, list) or not states:
        return [f"surface {surface_id} requires non-empty required_states"]
    for index, state in enumerate(states):
        path = f"surface {surface_id} required_states[{index}]"
        if not _is_mapping(state):
            findings.append(f"{path} must be an object")
            continue
        for field in ("state_id", "name", "observable_result"):
            if not _is_non_empty_string(state.get(field)):
                findings.append(f"{path}.{field} is required")
    findings.extend(_duplicate_ids(states, "state_id", f"surface {surface_id}.required_states"))
    return findings


def _validate_interactions(interactions: Any, surface_id: str) -> list[str]:
    findings: list[str] = []
    if not isinstance(interactions, list) or not interactions:
        return [f"surface {surface_id} requires non-empty interactions"]
    required = ("interaction_id", "trigger", "transition", "success", "failure")
    for index, interaction in enumerate(interactions):
        path = f"surface {surface_id} interactions[{index}]"
        if not _is_mapping(interaction):
            findings.append(f"{path} must be an object")
            continue
        for field in required:
            if not _is_non_empty_string(interaction.get(field)):
                findings.append(f"{path}.{field} is required")
    findings.extend(_duplicate_ids(interactions, "interaction_id", f"surface {surface_id}.interactions"))
    return findings


def _validate_observables(observables: Any, surface_id: str) -> list[str]:
    findings: list[str] = []
    if not isinstance(observables, list) or not observables:
        return [f"surface {surface_id} requires non-empty observables"]
    for index, observable in enumerate(observables):
        path = f"surface {surface_id} observables[{index}]"
        if not _is_mapping(observable):
            findings.append(f"{path} must be an object")
            continue
        for field in ("observable_id", "field", "meaning"):
            if not _is_non_empty_string(observable.get(field)):
                findings.append(f"{path}.{field} is required")
    findings.extend(_duplicate_ids(observables, "observable_id", f"surface {surface_id}.observables"))
    return findings


def _validate_layout(layout: Any, surface_id: str) -> list[str]:
    findings: list[str] = []
    if not isinstance(layout, list) or not layout:
        return [f"surface {surface_id} requires non-empty layout_invariants"]
    for index, invariant in enumerate(layout):
        path = f"surface {surface_id} layout_invariants[{index}]"
        if not _is_mapping(invariant):
            findings.append(f"{path} must be an object")
            continue
        for field in ("invariant_id", "rule", "verification"):
            if not _is_non_empty_string(invariant.get(field)):
                findings.append(f"{path}.{field} is required")
    findings.extend(_duplicate_ids(layout, "invariant_id", f"surface {surface_id}.layout_invariants"))
    return findings


def _validate_viewports(viewports: Any, surface_id: str) -> list[str]:
    findings: list[str] = []
    if not isinstance(viewports, list) or not viewports:
        return [f"surface {surface_id} requires non-empty viewports"]
    for index, viewport in enumerate(viewports):
        path = f"surface {surface_id} viewports[{index}]"
        if not _is_mapping(viewport):
            findings.append(f"{path} must be an object")
            continue
        for field in ("name", "width", "height"):
            value = viewport.get(field)
            if field == "name":
                valid = _is_non_empty_string(value)
            else:
                valid = isinstance(value, int) and value > 0
            if not valid:
                findings.append(f"{path}.{field} is required")
    return findings


def _validate_evidence(evidence: Any, surface_id: str) -> list[str]:
    if not isinstance(evidence, dict):
        return [f"surface {surface_id}.evidence is required"]
    findings: list[str] = []
    methods = evidence.get("methods")
    if not isinstance(methods, list) or not methods or not all(_is_non_empty_string(item) for item in methods):
        findings.append(f"surface {surface_id}.evidence.methods must be a non-empty list")
    if not _is_non_empty_string(evidence.get("target")):
        findings.append(f"surface {surface_id}.evidence.target is required")
    if evidence.get("freshness") not in {"current", "planned", "stale", "unavailable"}:
        findings.append(f"surface {surface_id}.evidence.freshness must be current|planned|stale|unavailable")
    return findings


def _validate_mappings(mappings: Any, surface_id: str) -> list[str]:
    if not isinstance(mappings, list) or not mappings:
        return [f"surface {surface_id} requires implementation_mappings"]
    findings: list[str] = []
    for index, mapping in enumerate(mappings):
        path = f"surface {surface_id} implementation_mappings[{index}]"
        if not isinstance(mapping, dict):
            findings.append(f"{path} must be an object")
            continue
        for field in ("mapping_id", "locator_type", "locator"):
            if not _is_non_empty_string(mapping.get(field)):
                findings.append(f"{path}.{field} is required")
        locator_type = mapping.get("locator_type")
        if locator_type not in ALLOWED_LOCATOR_TYPES:
            findings.append(f"{path}.locator_type must be one of {sorted(ALLOWED_LOCATOR_TYPES)}")
        if mapping.get("surface_id") != surface_id:
            findings.append(f"{path}.surface_id must equal {surface_id}")
    findings.extend(_duplicate_ids(mappings, "mapping_id", f"surface {surface_id}.implementation_mappings"))
    return findings


def validate_contract(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return ["contract root must be an object"]
    findings: list[str] = []
    if data.get("schema_version") != 1:
        findings.append("schema_version must be 1")
    if not _is_non_empty_string(data.get("contract_id")):
        findings.append("contract_id is required")
    if data.get("classification") not in ALLOWED_CLASSIFICATIONS:
        findings.append("classification must be greenfield or existing-product-extension")
    for key in FORBIDDEN_TECHNICAL_KEYS:
        if key in data:
            findings.append(f"framework-specific field is not allowed: {key}")
    placeholder = _contains_placeholder(data)
    if placeholder:
        findings.append(f"placeholder value is not allowed: {placeholder}")

    surfaces = data.get("surfaces")
    if not isinstance(surfaces, list) or not surfaces:
        return findings + ["surfaces must be a non-empty list"]
    findings.extend(_duplicate_ids(surfaces, "surface_id", "surfaces"))
    surface_ids = {surface.get("surface_id") for surface in surfaces if isinstance(surface, dict)}
    required_ids = data.get("required_surface_ids", [])
    if required_ids is not None:
        if not isinstance(required_ids, list) or not all(_is_non_empty_string(item) for item in required_ids):
            findings.append("required_surface_ids must be a list of non-empty strings")
        else:
            for required_id in required_ids:
                if required_id not in surface_ids:
                    findings.append(f"missing required surface: {required_id}")

    for index, surface in enumerate(surfaces):
        path = f"surfaces[{index}]"
        if not isinstance(surface, dict):
            findings.append(f"{path} must be an object")
            continue
        surface_id = surface.get("surface_id")
        if not _is_non_empty_string(surface_id):
            findings.append(f"{path}.surface_id is required")
            surface_id = f"index-{index}"
        for field in REQUIRED_SURFACE_FIELDS:
            if field not in surface or surface[field] in (None, "", []):
                findings.append(f"surface {surface_id}.{field} is required")
        hierarchy = surface.get("hierarchy")
        if not isinstance(hierarchy, list) or not hierarchy:
            findings.append(f"surface {surface_id} requires non-empty hierarchy")
        else:
            for region_index, region in enumerate(hierarchy):
                findings.extend(_validate_region(region, surface_id, region_index))
            findings.extend(_duplicate_ids(hierarchy, "region_id", f"surface {surface_id}.hierarchy"))
        findings.extend(_validate_states(surface.get("required_states"), surface_id))
        findings.extend(_validate_interactions(surface.get("interactions"), surface_id))
        findings.extend(_validate_observables(surface.get("observables"), surface_id))
        findings.extend(_validate_layout(surface.get("layout_invariants"), surface_id))
        findings.extend(_validate_viewports(surface.get("viewports"), surface_id))
        findings.extend(_validate_evidence(surface.get("evidence"), surface_id))
        findings.extend(_validate_mappings(surface.get("implementation_mappings"), surface_id))

    return findings


def load_contract(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as stream:
            return yaml.safe_load(stream)
    except (OSError, yaml.YAMLError) as error:
        raise ValueError(str(error)) from error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path, help="YAML surface contract path")
    args = parser.parse_args()
    try:
        data = load_contract(args.contract)
    except ValueError as error:
        print(json.dumps({"valid": False, "findings": [f"cannot load contract: {error}"]}, ensure_ascii=False))
        return 1
    findings = validate_contract(data)
    payload = {"valid": not findings, "findings": findings}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
