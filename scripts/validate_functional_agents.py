#!/usr/bin/env python3
"""Validate Bruce Functional Agent Profiles and routing contract."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from functional_agent_profiles import ContractError, PROFILE_IDS, load_builtin_profiles

ROOT = Path(__file__).resolve().parents[1]
ROUTING_FILES = {
    "inspector": ["skills/inspect-parallel/SKILL.md", "skills/solution-analysis/SKILL.md", "skills/write-architecture/SKILL.md"],
    "implementer": ["skills/spawn-execute/SKILL.md", "skills/explore-prototype/SKILL.md"],
    "verifier": ["skills/completion-gate/SKILL.md", "skills/design-gate/SKILL.md"],
    "reviewer": ["skills/completion-gate/SKILL.md", "skills/plan-review/SKILL.md", "skills/design-gate/SKILL.md", "skills/bruce/references/risk-policy.md", "skills/bruce/references/verification-loop.md", "skills/plan-review/references/plan-reviewer-prompt.md"],
}


def validate_registry() -> list[str]:
    errors: list[str] = []
    try:
        profiles = load_builtin_profiles()
    except ContractError as exc:
        return [str(exc)]

    required = {
        "role", "capability", "default_model", "reasoning_effort", "context", "tools",
        "write_scope", "model_capabilities", "fallback", "max_calls", "output", "authority",
    }
    expected_outputs = {
        "inspector": "task_evidence_packet",
        "implementer": "task_evidence_packet",
        "verifier": "verification_packet",
        "reviewer": "review_packet",
    }
    expected_context = {
        "inspector": {"inherit": "task", "clean": False},
        "implementer": {"inherit": "task", "clean": False},
        "verifier": {"inherit": "task", "clean": True},
        "reviewer": {"inherit": "none", "clean": True},
    }
    expected_independence = {
        "inspector": "none",
        "implementer": "none",
        "verifier": "preferred",
        "reviewer": "required",
    }

    for profile_id in PROFILE_IDS:
        profile = profiles[profile_id]
        missing = required - set(profile)
        if missing:
            errors.append(f"{profile_id} missing fields: {sorted(missing)}")
        if profile.get("role") != profile_id:
            errors.append(f"{profile_id} role mismatch")
        if profile.get("output") != expected_outputs[profile_id]:
            errors.append(f"{profile_id} output mismatch")
        if profile.get("context") != expected_context[profile_id]:
            errors.append(f"{profile_id} context mismatch")
        capabilities = profile.get("model_capabilities", {})
        if capabilities.get("independence") != expected_independence[profile_id]:
            errors.append(f"{profile_id} independence mismatch")
        if profile_id == "inspector" and profile.get("write_scope") != "none":
            errors.append("inspector must be read-only")
        if profile_id == "implementer" and profile.get("write_scope") != "task_packet.allowed_paths":
            errors.append("implementer write_scope must be task_packet.allowed_paths")
        if profile_id in {"verifier", "reviewer"} and profile.get("write_scope") != "none":
            errors.append(f"{profile_id} must not write")
        if profile.get("fallback") != "current":
            errors.append(f"{profile_id} fallback must be current")
        if not isinstance(profile.get("max_calls"), int) or profile["max_calls"] < 1:
            errors.append(f"{profile_id} max_calls must be positive")
    return errors


def validate_routing() -> list[str]:
    errors: list[str] = []
    for profile_id, paths in ROUTING_FILES.items():
        for relative in paths:
            text = (ROOT / relative).read_text(encoding="utf-8")
            if f"`{profile_id}`" not in text and f"{profile_id} Profile" not in text:
                errors.append(f"{relative} does not declare {profile_id} Profile")
    for relative in ("skills/completion-gate/SKILL.md", "skills/design-gate/SKILL.md"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        if "verification_packet" not in text:
            errors.append(f"{relative} does not declare verification_packet")
        if "review_packet" not in text:
            errors.append(f"{relative} does not declare review_packet")
        if re.search(r"return\s+(?:Design|Completion)\s+(?:pass|blocked|issues)", text, re.I):
            errors.append(f"{relative} contains agent-like terminal return")
    return errors


def main() -> int:
    errors = validate_registry()
    errors.extend(validate_routing())
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Functional Agent Profiles: pass ({len(PROFILE_IDS)} profiles)")
    print("Routing matrix: pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
