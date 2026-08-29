#!/usr/bin/env python3
"""Resolve Bruce's configured browser provider and normalize browser evidence scope."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Mapping

import yaml

SUPPORTED_PROVIDERS = ("ego-lite", "chrome")
SUPPORTED_SCOPES = ("none", "browser-smoke", "browser-layout")
LEGACY_SCOPE_ALIASES = {
    "chrome-smoke": "browser-smoke",
    "chrome-layout": "browser-layout",
}
CAPABILITIES = {
    "none": (),
    "browser-smoke": ("navigate", "real_interaction", "visible_state", "screenshot"),
    "browser-layout": (
        "navigate",
        "real_interaction",
        "visible_state",
        "screenshot",
        "viewport",
        "geometry",
        "overflow",
        "before_after",
    ),
}


class BrowserProviderConfigError(ValueError):
    """Raised when a browser provider or visual scope is invalid."""


def resolve_browser_provider(config: Mapping[str, Any] | None) -> str:
    """Return the configured provider, defaulting to ego-lite without fallback."""
    if config is None:
        return "ego-lite"
    verification = config.get("verification") or {}
    if not isinstance(verification, Mapping):
        raise BrowserProviderConfigError("verification must be a mapping")
    provider = verification.get("browser_provider", "ego-lite")
    if provider not in SUPPORTED_PROVIDERS:
        supported = ", ".join(SUPPORTED_PROVIDERS)
        raise BrowserProviderConfigError(
            f"verification.browser_provider must be one of: {supported}"
        )
    return provider


def resolve_browser_provider_file(path: str | Path) -> str:
    """Load a Bruce YAML config and resolve its browser provider."""
    config_path = Path(path)
    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise BrowserProviderConfigError(f"unable to read config: {config_path}") from error
    if config is not None and not isinstance(config, Mapping):
        raise BrowserProviderConfigError("config must be a YAML mapping")
    return resolve_browser_provider(config)


def normalize_visual_scope(scope: str) -> str:
    """Normalize legacy Chrome-specific scopes to the provider-neutral names."""
    normalized = LEGACY_SCOPE_ALIASES.get(scope, scope)
    if normalized not in SUPPORTED_SCOPES:
        supported = ", ".join(SUPPORTED_SCOPES)
        raise BrowserProviderConfigError(f"visual_scope must be one of: {supported}")
    return normalized


def required_capabilities(scope: str) -> tuple[str, ...]:
    """Return the capabilities required by a normalized or legacy visual scope."""
    return CAPABILITIES[normalize_visual_scope(scope)]


def assert_evidence_provider(configured_provider: str, evidence_provider: str) -> None:
    """Reject evidence collected by a provider different from the configured provider."""
    if configured_provider not in SUPPORTED_PROVIDERS:
        raise BrowserProviderConfigError(f"unsupported configured provider: {configured_provider}")
    if evidence_provider != configured_provider:
        raise BrowserProviderConfigError(
            f"browser evidence provider mismatch: configured={configured_provider}, "
            f"evidence={evidence_provider}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=".bruce/config.yaml")
    parser.add_argument("--scope", default="none")
    args = parser.parse_args()

    provider = resolve_browser_provider_file(args.config)
    scope = normalize_visual_scope(args.scope)
    capabilities = ",".join(required_capabilities(scope)) or "none"
    print(f"provider={provider}")
    print(f"visual_scope={scope}")
    print(f"capabilities={capabilities}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
