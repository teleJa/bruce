#!/usr/bin/env python3
"""Remind Codex to consider Bruce Design Gate after a planning/design edit.

This plugin hook is intentionally advisory and low-noise. It does not run a
review, block tool execution, or attest completion. Code and ordinary document
edits remain governed by the active Bruce workflow without per-edit reminders.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import PurePosixPath
from typing import Any


EDIT_TOOLS = {
    "Write",
    "Edit",
    "MultiEdit",
    "apply_patch",
    "replace_content",
    "replace_symbol_body",
    "insert_after_symbol",
    "insert_before_symbol",
}

PLANNING_FILENAMES = {
    "prd.md",
    "design.md",
    "implement.md",
    "test-plan.md",
    "plan.md",
    "architecture.md",
    "arch-design.md",
    "api.md",
    "api-contract.md",
    "functional-design.md",
    "acceptance-gate.md",
}
PLANNING_NAME_KEYWORDS = ("方案", "设计", "架构", "需求", "验收", "测试计划", "评审")
DOCUMENT_EXTENSIONS = {".md", ".mdx", ".rst", ".txt"}
CODE_EXTENSIONS = {
    ".go",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".py",
    ".sql",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".sh",
    ".css",
    ".scss",
    ".html",
}

REMINDER = (
    "Bruce Design Gate reminder: a planning/design document was modified. If this document will "
    "govern downstream implementation, run $design-gate before implementation and require "
    "`Design: pass`. The gate checks artifact completeness, factual grounding, consistency, "
    "acceptance coverage, omissions, placeholders, links, and blocking readiness issues together. "
    "This hook is advisory: it makes neither a design-readiness nor completion decision."
)


def main() -> int:
    try:
        payload = _read_payload()
        reminder = _build_reminder(payload)
        if reminder:
            _emit_context(f"<system-reminder>{reminder}</system-reminder>")
    except Exception as exc:  # noqa: BLE001 - an advisory hook must not block tool flow.
        _emit_context(
            "<system-reminder>Bruce PostToolUse review reminder skipped: "
            f"{exc}</system-reminder>"
        )
    return 0


def _read_payload() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    data = json.loads(raw)
    return data if isinstance(data, dict) else {}


def _build_reminder(payload: dict[str, Any]) -> str:
    tool_name = _tool_name(payload)
    if tool_name and tool_name not in EDIT_TOOLS:
        return ""
    if not _tool_succeeded(payload):
        return ""

    categories = _classify_paths(_extract_paths(payload))
    return REMINDER if "planning" in categories else ""


def _tool_name(payload: dict[str, Any]) -> str:
    candidates = [
        payload.get("tool_name"),
        payload.get("toolName"),
        payload.get("name"),
        payload.get("tool"),
    ]
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        candidates.extend([tool_input.get("tool_name"), tool_input.get("toolName")])

    for candidate in candidates:
        if isinstance(candidate, str) and candidate:
            return candidate
    return ""


def _tool_succeeded(payload: dict[str, Any]) -> bool:
    if _bool_value(payload.get("success")) is False:
        return False
    if _bool_value(payload.get("ok")) is False:
        return False
    if payload.get("error") or payload.get("exception"):
        return False

    status = payload.get("status")
    if isinstance(status, str) and status.lower() in {"error", "failed", "failure"}:
        return False

    for key in ("tool_result", "tool_response", "result", "output"):
        result = payload.get(key)
        if not isinstance(result, dict):
            continue
        if _bool_value(result.get("success")) is False:
            return False
        if result.get("error") or result.get("exception"):
            return False
        result_status = result.get("status")
        if isinstance(result_status, str) and result_status.lower() in {
            "error",
            "failed",
            "failure",
        }:
            return False
    return True


def _bool_value(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "yes", "ok", "success"}:
            return True
        if normalized in {"false", "no", "error", "failed", "failure"}:
            return False
    return None


def _extract_paths(payload: dict[str, Any]) -> set[str]:
    paths: set[str] = set()
    _collect_paths(payload, paths)
    for text in _collect_text(payload):
        paths.update(_paths_from_text(text))

    cwd = payload.get("cwd") if isinstance(payload.get("cwd"), str) else ""
    return {
        normalized
        for path in paths
        if _looks_like_path(path)
        for normalized in [_normalize_path(path, cwd)]
        if normalized
    }


def _collect_paths(value: Any, paths: set[str]) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            lowered = str(key).lower()
            if lowered in {
                "path",
                "file",
                "filepath",
                "file_path",
                "filename",
                "relative_path",
            }:
                if isinstance(nested, str):
                    paths.add(nested)
                elif isinstance(nested, list):
                    paths.update(item for item in nested if isinstance(item, str))
            else:
                _collect_paths(nested, paths)
    elif isinstance(value, list):
        for item in value:
            _collect_paths(item, paths)


def _collect_text(value: Any) -> list[str]:
    texts: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key).lower() in {
                "patch",
                "diff",
                "content",
                "command",
                "cmd",
                "input",
            } and isinstance(nested, str):
                texts.append(nested)
            else:
                texts.extend(_collect_text(nested))
    elif isinstance(value, list):
        for item in value:
            texts.extend(_collect_text(item))
    return texts


def _paths_from_text(text: str) -> set[str]:
    patch_paths: set[str] = set()
    for pattern in (
        r"^\*\*\* (?:Add|Update|Delete) File: (.+)$",
        r"^\+\+\+ b/(.+)$",
        r"^--- a/(.+)$",
    ):
        for match in re.finditer(pattern, text, flags=re.MULTILINE):
            patch_paths.add(match.group(1).strip())
    if patch_paths:
        return patch_paths

    paths: set[str] = set()
    pattern = re.compile(
        r"(?P<path>(?:\.?/)?(?:[\w.-]+/)+[\w.@+\- 一-龥]+"
        r"(?:\.[A-Za-z0-9]+|评审结果\.md)|(?:CONTEXT|README|AGENTS)\.md)"
    )
    for match in pattern.finditer(text):
        paths.add(match.group("path").strip())
    return paths


def _looks_like_path(path: str) -> bool:
    normalized = path.strip().strip('"').strip("'").replace("\\", "/")
    if not normalized or "\n" in normalized:
        return False
    if normalized.rsplit("/", 1)[-1] in {"CONTEXT.md", "README.md", "AGENTS.md"}:
        return True
    suffix = PurePosixPath(normalized).suffix.lower()
    return "/" in normalized or suffix in DOCUMENT_EXTENSIONS | CODE_EXTENSIONS


def _normalize_path(path: str, cwd: str) -> str:
    normalized = path.strip().strip('"').strip("'").replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]

    normalized_cwd = cwd.strip().replace("\\", "/").rstrip("/")
    if normalized_cwd and normalized.startswith(f"{normalized_cwd}/"):
        normalized = normalized[len(normalized_cwd) + 1 :]
    return normalized


def _classify_paths(paths: set[str]) -> set[str]:
    categories: set[str] = set()
    for path in paths:
        if _is_planning_design_path(path):
            categories.add("planning")
        elif _is_document_path(path):
            categories.add("docs")
        elif _is_code_path(path):
            categories.add("code")
        else:
            categories.add("unknown")
    return categories


def _is_planning_design_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    pure_path = PurePosixPath(normalized)
    if pure_path.is_absolute() or normalized == ".." or normalized.startswith("../"):
        return False

    name = normalized.rsplit("/", 1)[-1]
    if normalized.startswith(".trellis/tasks/"):
        return name in PLANNING_FILENAMES or name.endswith("评审结果.md")
    if not normalized.startswith("docs/"):
        return False
    return (
        name in PLANNING_FILENAMES
        or name.endswith("评审结果.md")
        or any(keyword in name for keyword in PLANNING_NAME_KEYWORDS)
    )


def _is_document_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    name = normalized.rsplit("/", 1)[-1]
    return (
        normalized.startswith("docs/")
        or name in {"CONTEXT.md", "README.md", "AGENTS.md"}
        or PurePosixPath(normalized).suffix.lower() in DOCUMENT_EXTENSIONS
    )


def _is_code_path(path: str) -> bool:
    return PurePosixPath(path).suffix.lower() in CODE_EXTENSIONS


def _emit_context(context: str) -> None:
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": context,
        }
    }
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    raise SystemExit(main())
