#!/usr/bin/env python3
"""Remind on planning edits and validate written Bruce design reviews.

Ordinary planning reminders remain advisory. A successfully written
``design-review.md`` is checked deterministically and an invalid review blocks
normal PostToolUse processing until the files are repaired.
"""

from __future__ import annotations

import json
import re
import shlex
import subprocess
import sys
from pathlib import Path, PurePosixPath
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
SHELL_TOOLS = {"Bash", "exec_command"}

PLANNING_FILENAMES = {
    "prd.md",
    "requirements.md",
    "design.md",
    "implement.md",
    "test-plan.md",
    "plan.md",
    "architecture.md",
    "arch-design.md",
    "api.md",
    "api-contract.md",
    "api-contracts.md",
    "table-design.md",
    "functional-design.md",
    "prototype-manifest.md",
    "acceptance-gate.md",
    "design-review.md",
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
    "acceptance coverage, task-contract package completeness, omissions, placeholders, links, and "
    "blocking readiness issues together. "
    "This hook is advisory: it makes neither a design-readiness nor completion decision."
)


def main() -> int:
    payload: dict[str, Any] = {}
    try:
        payload = _read_payload()
        output = _build_output(payload)
        if output:
            print(json.dumps(output, ensure_ascii=False))
    except Exception as exc:  # noqa: BLE001 - fail closed only for a review write.
        reason = f"Bruce PostToolUse Design Review validation failed unexpectedly: {exc}"
        if _payload_mentions_design_review(payload):
            print(json.dumps(_block_output(reason), ensure_ascii=False))
        else:
            _emit_context(f"<system-reminder>{reason}</system-reminder>")
    return 0


def _read_payload() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    data = json.loads(raw)
    return data if isinstance(data, dict) else {}


def _build_output(payload: dict[str, Any]) -> dict[str, Any] | None:
    tool_name = _tool_name(payload)
    if tool_name and tool_name not in EDIT_TOOLS | SHELL_TOOLS:
        return None
    if not _tool_succeeded(payload):
        return None

    written_paths = _extract_written_paths(tool_name, payload)
    if written_paths:
        design_reviews = _design_reviews_to_validate(payload, written_paths)
        if design_reviews:
            written_reviews = {
                path for path in written_paths if _is_design_review_path(path)
            }
            stale_reviews = [path for path in design_reviews if path not in written_reviews]
            if stale_reviews:
                joined = ", ".join(stale_reviews)
                return _block_output(
                    "Bruce Design Gate invalidated an existing review because a same-directory "
                    "design artifact changed without updating design-review.md in the same tool "
                    f"call: {joined}. Rerun $design-gate and the validator before implementation."
                )
            return _validate_design_reviews(payload, design_reviews)

    categories = _classify_paths(written_paths)
    if "planning" in categories:
        return _context_output(f"<system-reminder>{REMINDER}</system-reminder>")
    return None


def _extract_written_paths(tool_name: str, payload: dict[str, Any]) -> set[str]:
    raw_paths: set[str] = set()
    tool_input = payload.get("tool_input")

    if tool_name in EDIT_TOOLS:
        if isinstance(tool_input, dict):
            _collect_paths(tool_input, raw_paths)
            for key in ("patch", "diff"):
                value = tool_input.get(key)
                if isinstance(value, str):
                    raw_paths.update(_patch_paths_from_text(value))
    elif tool_name in SHELL_TOOLS:
        raw_paths.update(_shell_write_paths(_shell_command(payload)))

    return _normalize_paths(payload, raw_paths)


def _shell_write_paths(command: str) -> set[str]:
    if not command:
        return set()

    paths: set[str] = set()
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars="<>|&;")
        lexer.commenters = ""
        tokens = list(lexer)
    except ValueError:
        tokens = []
    for index, token in enumerate(tokens[:-1]):
        if token not in {">", ">>", "&>", "&>>"}:
            continue
        target = tokens[index + 1]
        if _is_real_file_target(target):
            paths.add(target)

    command_pattern = re.compile(
        r"(?:^|[;&|]\s*)(?:sudo\s+)?"
        r"(?P<command>tee|touch|cp|mv|install|sed|perl)\b"
        r"(?P<arguments>[^\n;&|]*)",
        flags=re.IGNORECASE | re.MULTILINE,
    )
    for match in command_pattern.finditer(command):
        try:
            arguments = shlex.split(match.group("arguments"))
        except ValueError:
            continue
        name = match.group("command").lower()
        if name == "sed" and not any(value.startswith("-i") for value in arguments):
            continue
        if name == "perl" and not any(
            value.startswith("-") and "i" in value[1:] for value in arguments
        ):
            continue
        operands = [value for value in arguments if not value.startswith("-")]
        candidates = operands if name in {"tee", "touch"} else operands[-1:]
        paths.update(target for target in candidates if _is_real_file_target(target))

    direct_path_write = re.compile(
        r'''Path\(\s*["'](?P<path>[^"']+)["']\s*\)\s*
            \.\s*write_(?:text|bytes)\s*\(''',
        flags=re.VERBOSE,
    )
    joined_path_write = re.compile(
        r'''(?:\(\s*)?Path\(\s*["'](?P<parent>[^"']+)["']\s*\)\s*
            /\s*["'](?P<name>[^"']+)["']\s*(?:\))?\s*
            \.\s*write_(?:text|bytes)\s*\(''',
        flags=re.VERBOSE,
    )
    paths.update(match.group("path") for match in direct_path_write.finditer(command))
    paths.update(
        (PurePosixPath(match.group("parent")) / match.group("name")).as_posix()
        for match in joined_path_write.finditer(command)
    )
    path_assignments = {
        match.group("variable"): match.group("path")
        for match in re.finditer(
            r'''\b(?P<variable>[A-Za-z_]\w*)\s*=\s*
                Path\(\s*["'](?P<path>[^"']+)["']\s*\)''',
            command,
            flags=re.VERBOSE,
        )
    }
    variable_path_write = re.compile(
        r'''(?:\(\s*)?(?P<variable>[A-Za-z_]\w*)\s*
            /\s*["'](?P<name>[^"']+)["']\s*(?:\))?\s*
            \.\s*write_(?:text|bytes)\s*\(''',
        flags=re.VERBOSE,
    )
    paths.update(
        (PurePosixPath(path_assignments[match.group("variable")]) / match.group("name")).as_posix()
        for match in variable_path_write.finditer(command)
        if match.group("variable") in path_assignments
    )
    return paths


def _is_real_file_target(target: str) -> bool:
    normalized = target.strip().strip('"').strip("'")
    return bool(normalized) and normalized not in {
        "&1",
        "&2",
        "/dev/null",
        "/dev/stdout",
        "/dev/stderr",
    }


def _shell_command(payload: dict[str, Any]) -> str:
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return ""
    for key in ("command", "cmd"):
        value = tool_input.get(key)
        if isinstance(value, str):
            return value
    return ""


def _is_design_review_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    pure_path = PurePosixPath(normalized)
    return (
        not pure_path.is_absolute()
        and normalized != ".."
        and not normalized.startswith("../")
        and pure_path.name == "design-review.md"
    )


def _parent_design_review_path(path: str, cwd: Path) -> str | None:
    candidate = PurePosixPath(path)
    current = candidate.parent
    while True:
        review_relative = (current / "design-review.md").as_posix()
        if (cwd / review_relative).is_file():
            return review_relative
        if current == PurePosixPath(".") or current in {
            PurePosixPath("docs"),
            PurePosixPath(".trellis"),
        }:
            break
        current = current.parent
    return None

def _design_reviews_to_validate(
    payload: dict[str, Any], paths: set[str]
) -> list[str]:
    cwd = _effective_cwd(payload)
    if cwd is None:
        return sorted(path for path in paths if _is_design_review_path(path))

    reviews: set[str] = set()
    for path in paths:
        normalized = path.replace("\\", "/")
        candidate = PurePosixPath(normalized)
        if candidate.is_absolute() or normalized == ".." or normalized.startswith("../"):
            continue
        if _is_design_review_path(normalized):
            reviews.add(normalized)
        elif _is_task_contract_path(normalized):
            review_relative = _parent_design_review_path(normalized, cwd)
            if review_relative is not None:
                reviews.add(review_relative)
        elif _is_gate_artifact_path(normalized):
            review_relative = (candidate.parent / "design-review.md").as_posix()
            if (cwd / review_relative).is_file():
                reviews.add(review_relative)
    return sorted(reviews)


def _validate_design_reviews(
    payload: dict[str, Any], paths: list[str]
) -> dict[str, Any] | None:
    cwd = _effective_cwd(payload)
    if cwd is None:
        return _block_output("Cannot validate design-review.md because the hook payload has no cwd.")
    validator = (Path(__file__).resolve().parents[1] / "skills/design-gate/scripts/validate_design_review.py")
    failures: list[str] = []
    validated: list[str] = []

    for relative in paths:
        review = (cwd / relative).resolve()
        try:
            review.relative_to(cwd)
        except ValueError:
            continue
        if not review.is_file():
            failures.append(f"{relative}: design-review.md was referenced by a write but does not exist")
            continue
        if not validator.is_file():
            failures.append(f"{relative}: Design Review validator is missing: {validator}")
            continue
        try:
            result = subprocess.run(
                [sys.executable, str(validator), "--change-dir", str(review.parent)],
                cwd=cwd,
                text=True,
                capture_output=True,
                check=False,
                timeout=15,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            failures.append(f"{relative}: Design Review validator could not run: {exc}")
            continue
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            failures.append(f"{relative}: {detail}")
        else:
            validated.append(relative)

    if failures:
        detail = "\n".join(failures)
        return _block_output(
            "Bruce Design Gate rejected the written design review. Repair the current files and "
            f"rerun the validator before reporting Design: pass.\n{detail[:6000]}"
        )
    if validated:
        joined = ", ".join(validated)
        return _context_output(
            "<system-reminder>Bruce Design Review validator passed for "
            f"{joined}. Use the current validator result as gate evidence; file presence or prose "
            "alone is not a pass.</system-reminder>"
        )
    return None


def _context_output(context: str) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": context,
        }
    }


def _block_output(reason: str) -> dict[str, Any]:
    return {
        "decision": "block",
        "reason": reason,
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": reason,
        },
    }


def _payload_mentions_design_review(payload: dict[str, Any]) -> bool:
    try:
        return "design-review.md" in json.dumps(payload, ensure_ascii=False)
    except (TypeError, ValueError):
        return False


def _effective_cwd(payload: dict[str, Any]) -> Path | None:
    cwd_value = payload.get("cwd")
    base = Path(cwd_value).resolve() if isinstance(cwd_value, str) and cwd_value else None
    tool_input = payload.get("tool_input")
    workdir = tool_input.get("workdir") if isinstance(tool_input, dict) else None
    if not isinstance(workdir, str) or not workdir:
        return base
    candidate = Path(workdir).expanduser()
    if candidate.is_absolute():
        return candidate.resolve()
    return (base / candidate).resolve() if base is not None else candidate.resolve()


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
        if isinstance(result, str) and re.search(
            r"(?:Process exited with code|exit_code[=:]|returncode[=:])\s*[1-9]\d*",
            result,
            flags=re.IGNORECASE,
        ):
            return False
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
        for exit_key in ("exit_code", "exitCode", "returncode", "return_code"):
            exit_code = result.get(exit_key)
            if isinstance(exit_code, int) and exit_code != 0:
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


def _normalize_paths(payload: dict[str, Any], paths: set[str]) -> set[str]:
    effective_cwd = _effective_cwd(payload)
    raw_cwd = payload.get("cwd") if isinstance(payload.get("cwd"), str) else ""
    cwd_candidates = {raw_cwd.rstrip("/")} if raw_cwd else set()
    if effective_cwd is not None:
        cwd_candidates.add(str(effective_cwd).rstrip("/"))
    return {
        normalized
        for path in paths
        if _looks_like_path(path)
        for normalized in [_normalize_path(path, cwd_candidates)]
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


def _patch_paths_from_text(text: str) -> set[str]:
    paths: set[str] = set()
    for pattern in (
        r"^\*\*\* (?:Add|Update|Delete) File: (.+)$",
        r"^\+\+\+ b/(.+)$",
        r"^--- a/(.+)$",
    ):
        for match in re.finditer(pattern, text, flags=re.MULTILINE):
            paths.add(match.group(1).strip())
    return paths


def _looks_like_path(path: str) -> bool:
    normalized = path.strip().strip('"').strip("'").replace("\\", "/")
    if not normalized or "\n" in normalized:
        return False
    if normalized.rsplit("/", 1)[-1] in {"CONTEXT.md", "README.md", "AGENTS.md"}:
        return True
    suffix = PurePosixPath(normalized).suffix.lower()
    return "/" in normalized or suffix in DOCUMENT_EXTENSIONS | CODE_EXTENSIONS


def _normalize_path(path: str, cwd_candidates: set[str]) -> str:
    normalized = path.strip().strip('"').strip("'").replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]

    for cwd in sorted(cwd_candidates, key=len, reverse=True):
        normalized_cwd = cwd.strip().replace("\\", "/").rstrip("/")
        if normalized_cwd and normalized.startswith(f"{normalized_cwd}/"):
            return normalized[len(normalized_cwd) + 1 :]
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


def _is_task_contract_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    pure_path = PurePosixPath(normalized)
    if pure_path.is_absolute() or normalized == ".." or normalized.startswith("../"):
        return False
    if "/tasks/" not in f"/{normalized}/":
        return False
    return pure_path.suffix.lower() in {".md", ".yaml", ".yml"}


def _is_gate_artifact_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    pure_path = PurePosixPath(normalized)
    if pure_path.is_absolute() or normalized == ".." or normalized.startswith("../"):
        return False
    name = pure_path.name
    return (
        _is_task_contract_path(normalized)
        or name in PLANNING_FILENAMES
        or name.endswith("评审结果.md")
        or any(keyword in name for keyword in PLANNING_NAME_KEYWORDS)
    )


def _is_planning_design_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    pure_path = PurePosixPath(normalized)
    if pure_path.is_absolute() or normalized == ".." or normalized.startswith("../"):
        return False

    name = normalized.rsplit("/", 1)[-1]
    if normalized.startswith(".trellis/tasks/"):
        return name in PLANNING_FILENAMES or name.endswith("评审结果.md") or _is_task_contract_path(normalized)
    if not normalized.startswith("docs/"):
        return False
    return (
        _is_task_contract_path(normalized)
        or name in PLANNING_FILENAMES
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
    print(json.dumps(_context_output(context), ensure_ascii=False))


if __name__ == "__main__":
    raise SystemExit(main())
