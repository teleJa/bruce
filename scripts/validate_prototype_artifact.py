#!/usr/bin/env python3
"""Validate deterministic visual assertions against a bounded prototype artifact.

The checker is intentionally product-agnostic. Product-specific values live in a
change-scoped ``visual-assertions.json`` sidecar, while provider status is only
reported as context and never overrides a failed visual assertion.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


class ValidationError(ValueError):
    pass


_TEXT_EXTENSIONS = {".html", ".htm", ".css", ".scss", ".less", ".jsx", ".tsx", ".vue", ".svelte"}
_COLOR_RE = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b")
_RGB_RE = re.compile(r"rgba?\([^)]*\)", re.I)
_DECL_RE = re.compile(r"(?P<property>[\w-]+)\s*:\s*(?P<value>[^;{}]+)")
_RULE_RE = re.compile(r"(?P<selectors>[^{}]+)\{(?P<body>[^{}]*)\}", re.S)
_STYLE_RE = re.compile(r"<style\b[^>]*>(?P<body>.*?)</style>", re.I | re.S)


def _normalise_color(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("rgb"):
        numbers = re.findall(r"\d+(?:\.\d+)?", value)
        if len(numbers) >= 3:
            return "#%02x%02x%02x" % tuple(int(float(n)) for n in numbers[:3])
    if value.startswith("#"):
        value = value.split("(", 1)[0]
        if len(value) == 4:
            return "#" + "".join(ch * 2 for ch in value[1:])
        return value[:9]
    return value


def _as_list(contract: dict[str, Any], key: str) -> list[dict[str, Any]]:
    raw = contract.get(key, [])
    if not isinstance(raw, list):
        raise ValidationError(f"{key} must be a list")
    result: list[dict[str, Any]] = []
    for item in raw:
        if isinstance(item, str):
            result.append({"value": item})
        elif isinstance(item, dict) and isinstance(item.get("value"), (str, int, float)):
            result.append(item)
        else:
            raise ValidationError(f"{key} contains an invalid assertion")
    return result


def load_contract(path: str | Path) -> dict[str, Any]:
    contract_path = Path(path)
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read contract: {exc}") from exc
    if not isinstance(contract, dict) or contract.get("schema_version") != 1:
        raise ValidationError("schema_version must be 1")
    for key in ("exact_colors", "exact_dimensions", "required_brand_text", "forbidden_tokens"):
        _as_list(contract, key)
    return contract


class _VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stack: list[tuple[dict[str, str], list[str]]] = []
        self.elements: list[tuple[dict[str, str], str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.stack.append(({"tag": tag, **{k: v or "" for k, v in attrs}}, []))

    def handle_data(self, data: str) -> None:
        if any(attrs.get("tag") in {"script", "style"} for attrs, _ in self.stack):
            return
        for _, chunks in self.stack:
            chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            attrs, chunks = self.stack[index]
            if attrs.get("tag") == tag:
                del self.stack[index:]
                self.elements.append((attrs, "".join(chunks).strip()))
                break


def _matches_selector(attrs: dict[str, str], selector: str) -> bool:
    selector = selector.strip().split()[-1]
    if ":" in selector:
        selector = selector.split(":", 1)[0]
    tag = re.match(r"^[a-zA-Z][\w-]*", selector)
    if tag and attrs.get("tag") != tag.group(0).lower():
        return False
    id_match = re.search(r"#([\w-]+)", selector)
    if id_match and attrs.get("id") != id_match.group(1):
        return False
    classes = set(attrs.get("class", "").split())
    return all(cls in classes for cls in re.findall(r"\.([\w-]+)", selector))


def _files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValidationError(f"artifact does not exist: {path}")
    return sorted(p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in _TEXT_EXTENSIONS)


def validate_artifact(contract_path: str | Path, artifact_path: str | Path,
                      provider_status: str | None = None) -> dict[str, Any]:
    contract = load_contract(contract_path)
    paths = _files(Path(artifact_path))
    if not paths:
        raise ValidationError("artifact has no supported text files")
    texts: dict[Path, str] = {}
    for path in paths:
        try:
            texts[path] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise ValidationError(f"artifact is not UTF-8 text: {path}") from exc
    combined = "\n".join(texts.values())
    findings: list[str] = []
    parser = _VisibleText()
    html = "\n".join(text for path, text in texts.items() if path.suffix.lower() in {".html", ".htm", ".vue", ".svelte"})
    if html:
        parser.feed(html)
    rules: list[tuple[str, dict[str, str]]] = []
    css_sources = [
        text
        for path, text in texts.items()
        if path.suffix.lower() in {".css", ".scss", ".less"}
    ]
    css_sources.extend(match.group("body") for match in _STYLE_RE.finditer(html))
    for match in _RULE_RE.finditer("\n".join(css_sources)):
        declarations = {m.group("property").lower(): m.group("value").strip() for m in _DECL_RE.finditer(match.group("body"))}
        for selector in match.group("selectors").split(","):
            rules.append((selector.strip(), declarations))

    def values_for(selector: str, prop: str) -> list[str]:
        found: list[str] = []
        for rule_selector, declarations in rules:
            if rule_selector == selector and prop in declarations and declarations[prop] not in found:
                found.append(declarations[prop])
        for attrs, _ in parser.elements:
            if _matches_selector(attrs, selector) and attrs.get("style"):
                inline = {
                    match.group("property").lower(): match.group("value").strip()
                    for match in _DECL_RE.finditer(attrs["style"])
                }
                if prop in inline and inline[prop] not in found:
                    found.append(inline[prop])
        return found

    def colors_in(value: str) -> list[str]:
        return [_normalise_color(color) for color in (*_COLOR_RE.findall(value), *_RGB_RE.findall(value))]

    def selector_content(selector: str) -> str:
        css = " ".join(
            " ".join(declarations.values())
            for rule_selector, declarations in rules
            if rule_selector == selector
        )
        html_text = " ".join(text for attrs, text in parser.elements if _matches_selector(attrs, selector))
        inline = " ".join(attrs.get("style", "") for attrs, _ in parser.elements if _matches_selector(attrs, selector))
        return " ".join((css, html_text, inline))

    for item in _as_list(contract, "exact_colors"):
        expected = _normalise_color(str(item["value"]))
        selector = item.get("selector")
        if selector:
            candidates = colors_in(selector_content(str(selector)))
        else:
            candidates = colors_in(combined)
        if expected not in candidates:
            findings.append(f"color mismatch: {selector or '*'} expected {expected}")

    for item in _as_list(contract, "exact_dimensions"):
        selector, prop, expected = item.get("selector"), str(item.get("property", "width")), str(item["value"])
        if isinstance(item["value"], (int, float)):
            expected += str(item.get("unit", "px"))
        candidates = values_for(str(selector), prop) if selector else [m.group("value").strip() for m in _DECL_RE.finditer(combined) if m.group("property").lower() == prop.lower()]
        if expected not in candidates:
            findings.append(f"dimension mismatch: {selector or '*'} {prop} expected {expected}")

    for item in _as_list(contract, "required_brand_text"):
        expected, selector = str(item["value"]), item.get("selector")
        matches = [text for attrs, text in parser.elements if (not selector or _matches_selector(attrs, str(selector))) and expected in text]
        if not matches:
            findings.append(f"brand text missing: {expected}")

    for item in _as_list(contract, "forbidden_tokens"):
        token, selector = str(item["value"]), item.get("selector")
        searchable = selector_content(str(selector)) if selector else combined
        if token in searchable:
            findings.append(f"forbidden token present: {token}")

    status = "blocked" if findings else "clear"
    return {
        "provider_status": provider_status or "not-supplied",
        "visual_check": "blocked" if findings else "automated-clear",
        "exact_token_assertions": status,
        "findings": findings,
        "files_checked": [str(path) for path in paths],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--provider-status")
    args = parser.parse_args(argv)
    try:
        result = validate_artifact(args.contract, args.artifact, args.provider_status)
    except ValidationError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["visual_check"] == "blocked" else 0


if __name__ == "__main__":
    sys.exit(main())
