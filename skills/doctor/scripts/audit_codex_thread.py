#!/usr/bin/env python3
"""Build a compact, evidence-linked audit view of a Codex rollout JSONL file.

The source file is opened read-only and processed one line at a time. Generated
artifacts never contain an unredacted copy of extracted message or tool text.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


SECRET_PATTERNS = (
    re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)([A-Za-z0-9._~+/=-]+)"),
    re.compile(
        r"(?i)([\"'](?:api[_-]?key|token|secret|password|passwd)[\"']\s*:\s*[\"'])([^\"']+)([\"'])"
    ),
    re.compile(
        r"(?i)\b(api[_-]?key|token|secret|password|passwd)\b(\s*[:=]\s*)([\"']?)([^\s,;\"'}]+)"
    ),
    re.compile(r"\b(sk-[A-Za-z0-9_-]{12,})\b"),
)


def redact(text: str) -> tuple[str, int]:
    count = 0

    def bearer(match: re.Match[str]) -> str:
        nonlocal count
        count += 1
        return f"{match.group(1)}<REDACTED>"

    def quoted(match: re.Match[str]) -> str:
        nonlocal count
        count += 1
        return f"{match.group(1)}<REDACTED>{match.group(3)}"

    def assigned(match: re.Match[str]) -> str:
        nonlocal count
        count += 1
        quote = match.group(3)
        suffix = quote if quote else ""
        return f"{match.group(1)}{match.group(2)}{quote}<REDACTED>{suffix}"

    def sk_key(_: re.Match[str]) -> str:
        nonlocal count
        count += 1
        return "<REDACTED_KEY>"

    text = SECRET_PATTERNS[0].sub(bearer, text)
    text = SECRET_PATTERNS[1].sub(quoted, text)
    text = SECRET_PATTERNS[2].sub(assigned, text)
    text = SECRET_PATTERNS[3].sub(sk_key, text)
    return text, count


def parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def text_from_blocks(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = [text_from_blocks(item) for item in value]
        return "\n".join(part for part in parts if part)
    if isinstance(value, dict):
        for key in ("text", "output_text", "input_text"):
            if isinstance(value.get(key), str):
                return value[key]
        return compact_json(value)
    if value is None:
        return ""
    return str(value)


def clean_objective(text: str) -> str:
    """Remove host-injected wrappers from the short timeline objective only."""
    text = re.sub(r"(?is)<(?:app-context|environment_context)>.*?</(?:app-context|environment_context)>", "", text)
    text = re.sub(r"(?is)<image[^>]*>.*?</image>", "", text)
    text = re.sub(r"(?is)(?:data:image/[^;]+;base64,)[A-Za-z0-9+/=]{100,}", "<IMAGE_DATA>", text)
    text = re.sub(r"[A-Za-z0-9+/=]{240,}", "<OPAQUE_BLOB>", text)
    return " ".join(text.split())


def get_turn_id(payload: dict[str, Any], current_turn: str | None) -> str | None:
    direct = payload.get("turn_id")
    if isinstance(direct, str):
        return direct
    metadata = payload.get("internal_chat_message_metadata_passthrough")
    if isinstance(metadata, dict) and isinstance(metadata.get("turn_id"), str):
        return metadata["turn_id"]
    return current_turn


def describe_event(
    record: dict[str, Any], current_turn: str | None
) -> tuple[dict[str, Any] | None, str]:
    source_type = str(record.get("type") or "unknown")
    payload = record.get("payload")
    if not isinstance(payload, dict):
        payload = {}
    subtype = payload.get("type")
    event_type = str(subtype) if subtype else source_type
    turn_id = get_turn_id(payload, current_turn)
    base: dict[str, Any] = {
        "timestamp": record.get("timestamp"),
        "turn_id": turn_id,
        "source_type": source_type,
        "event_type": event_type,
        "category": None,
        "role": None,
        "tool_name": None,
        "call_id": payload.get("call_id"),
        "status": payload.get("status"),
        "success": payload.get("success"),
        "duration_ms": payload.get("duration_ms"),
        "text": "",
    }

    if source_type in {"session_meta", "world_state"}:
        return None, source_type

    if source_type == "turn_context":
        base["category"] = "turn_context"
        selected = {
            key: payload.get(key)
            for key in ("cwd", "workspace_roots", "model", "effort", "approval_policy")
            if key in payload
        }
        base["text"] = compact_json(selected)
        return base, ""

    if source_type == "compacted":
        base["category"] = "compaction"
        base["text"] = str(payload.get("message") or "")
        return base, ""

    if source_type == "response_item":
        if subtype == "message":
            role = str(payload.get("role") or "unknown")
            if role in {"developer", "system"}:
                return None, f"message:{role}"
            base["category"] = f"{role}_message"
            base["role"] = role
            base["text"] = text_from_blocks(payload.get("content"))
            return base, ""
        if subtype in {"custom_tool_call", "function_call"}:
            base["category"] = "tool_call"
            base["tool_name"] = payload.get("name")
            base["text"] = text_from_blocks(payload.get("input") or payload.get("arguments"))
            return base, ""
        if subtype in {"custom_tool_call_output", "function_call_output"}:
            base["category"] = "tool_output"
            base["text"] = text_from_blocks(payload.get("output"))
            return base, ""
        return None, f"response_item:{event_type}"

    if source_type == "event_msg":
        if subtype in {"user_message", "agent_message"}:
            role = "user" if subtype == "user_message" else "assistant"
            message = str(payload.get("message") or "")
            if subtype == "user_message" and message.lstrip().startswith("<subagent_notification>"):
                base["category"] = "notification"
                base["role"] = "system"
                base["text"] = message
                return base, ""
            base["category"] = f"{role}_message"
            base["role"] = role
            base["text"] = message
            return base, ""
        if subtype in CHECKPOINT_TRIGGERS:
            base["category"] = "lifecycle"
            base["text"] = str(payload.get("message") or "")
            return base, ""
        if subtype in {"task_started", "task_complete"}:
            base["category"] = "lifecycle"
            if subtype == "task_complete":
                base["text"] = str(payload.get("last_agent_message") or "")
            return base, ""
        if subtype == "patch_apply_end":
            base["category"] = "patch"
            changes = payload.get("changes")
            paths = sorted(changes) if isinstance(changes, dict) else []
            base["text"] = "\n".join(
                part
                for part in (
                    str(payload.get("stdout") or ""),
                    str(payload.get("stderr") or ""),
                    "changed_paths:\n" + "\n".join(paths) if paths else "",
                )
                if part
            )
            return base, ""
        if subtype == "mcp_tool_call_end":
            invocation = payload.get("invocation")
            if isinstance(invocation, dict):
                server = invocation.get("server")
                tool = invocation.get("tool")
                base["tool_name"] = ".".join(str(x) for x in (server, tool) if x)
            base["category"] = "tool_output"
            base["text"] = compact_json(
                {"invocation": invocation, "result": payload.get("result")}
            )
            return base, ""
        if subtype == "context_compacted":
            base["category"] = "compaction"
            return base, ""
        lowered = str(subtype or "").lower()
        if any(marker in lowered for marker in ("error", "failed", "aborted")):
            base["category"] = "error"
            base["text"] = compact_json(payload)
            return base, ""
        return None, f"event_msg:{event_type}"

    return None, source_type


def preview_text(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    head = max(1, limit // 2)
    tail = max(1, limit - head)
    return f"{text[:head]}\n…<TRUNCATED {len(text) - limit} CHARS>…\n{text[-tail:]}"


CHECKPOINT_STATUS = re.compile(r"(?im)^\s*Checkpoint:\s*(clear|issues|blocked)\s*$")
CHECKPOINT_FIELDS = (
    "batch_id",
    "basis_revision",
    "acceptance",
    "findings",
    "repair_sets",
    "next_action",
)
VERIFY_COMMAND = re.compile(
    r"(?i)(?:\bgo\s+test\b|\b(?:pnpm|npm|yarn|bun)\b[^\n]*\b(?:test|vitest|jest|tsc|typecheck|eslint)\b|\bpytest\b|\bvitest\b|\bpython(?:3)?\s+-m\s+unittest\b|\bmake\s+test\b)"
)
EDIT_COMMAND = re.compile(
    r"(?i)(?:\bapply_patch\b|\bcat\s+>\s*[^\n]+|\btee\s+[^\n]+|\b(?:python|python3|perl)\b[^\n]*(?:write_text|replace\(|unlink\(|rename\())"
)


# Only these explicit declarations are audited; tool names and prose are not
# evidence that a material change or side-effect boundary occurred.
CHECKPOINT_TRIGGERS = (
    "material_task_change",
    "material_scope_change",
    "material_environment_change",
    "material_evidence_change",
    "side_effect_boundary",
)
CHECKPOINT_TRIGGER = re.compile(
    r"(?im)^\s*Checkpoint trigger:\s*(" + "|".join(CHECKPOINT_TRIGGERS) + r")\s*$"
)


def checkpoint_triggers(event: dict[str, Any]) -> list[str]:
    if event.get("category") not in {"assistant_message", "user_message", "lifecycle"}:
        return []
    triggers = CHECKPOINT_TRIGGER.findall(str(event.get("text") or ""))
    if event.get("category") == "lifecycle" and event.get("event_type") in CHECKPOINT_TRIGGERS:
        triggers.append(event["event_type"])
    return list(dict.fromkeys(trigger.lower() for trigger in triggers))


def checkpoint_from_text(text: str) -> dict[str, Any] | None:
    match = CHECKPOINT_STATUS.search(text)
    if match is None:
        return None
    missing = [
        field
        for field in CHECKPOINT_FIELDS
        if re.search(rf"(?im)^\s*{re.escape(field)}\s*:", text) is None
    ]
    return {"status": match.group(1), "missing_fields": missing}


def tool_action_kind(event: dict[str, Any]) -> str | None:
    if event.get("category") != "tool_call":
        return None
    if event.get("tool_name") != "exec_command":
        return None
    text = str(event.get("text") or "")
    if VERIFY_COMMAND.search(text):
        return "verify"
    if EDIT_COMMAND.search(text):
        return "edit"
    return None


def interval_snapshot(interval: dict[str, Any], end_timestamp: str | None, end_line: int) -> dict[str, Any]:
    start = parse_timestamp(interval.get("started_at"))
    end = parse_timestamp(end_timestamp)
    elapsed_seconds = (end - start).total_seconds() if start and end and end >= start else None
    return {
        "start_line": interval["start_line"],
        "end_line": end_line,
        "tool_calls": interval["tool_calls"],
        "elapsed_seconds": elapsed_seconds,
    }


def analyze_checkpoint_protocol(normalized_path: Path) -> dict[str, Any]:
    """Audit explicit event-triggered checkpoints; time/count limits are advisory.

    Only explicit checkpoint-shaped assistant/lifecycle messages are checkpoints.
    Missing-checkpoint evidence requires an explicit trigger, never a user turn,
    profile, elapsed time, tool count, or guessed tool side effect. Brief progress
    messages are not incomplete checkpoints. Update-plan and churn stay suspected.
    """
    valid: list[dict[str, Any]] = []
    incomplete: list[dict[str, Any]] = []
    overruns: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    substitutions: list[dict[str, Any]] = []
    churn_cycles: list[dict[str, Any]] = []
    interval: dict[str, Any] | None = None
    last_timestamp: str | None = None
    last_line = 0
    seen_checkpoint_text: set[tuple[str | None, str]] = set()
    pending_triggers: list[dict[str, Any]] = []

    def start_interval(timestamp: str | None, line_no: int) -> dict[str, Any]:
        return {
            "started_at": timestamp,
            "start_line": line_no,
            "tool_calls": 0,
            "last_action": None,
            "last_verify_line": None,
            "churn_cycle_count": 0,
            "substitution_lines": set(),
        }

    def exceeds(snapshot: dict[str, Any]) -> bool:
        return snapshot["tool_calls"] > 40 or (
            isinstance(snapshot["elapsed_seconds"], (int, float))
            and snapshot["elapsed_seconds"] > 45 * 60
        )

    def record_churn(current: dict[str, Any]) -> None:
        if current["churn_cycle_count"] >= 2:
            churn_cycles.append(
                {
                    "start_line": current["start_line"],
                    "last_verify_line": current["last_verify_line"],
                    "cycles": current["churn_cycle_count"],
                }
            )

    for raw in normalized_path.open(encoding="utf-8"):
        event = json.loads(raw)
        timestamp = event.get("timestamp") if isinstance(event.get("timestamp"), str) else None
        line_no = int(event.get("line_no") or 0)
        last_timestamp = timestamp or last_timestamp
        last_line = line_no or last_line
        category = event.get("category")
        event_type = event.get("event_type")

        if category == "lifecycle" and event_type == "task_started":
            if interval is not None:
                record_churn(interval)
            interval = start_interval(timestamp, line_no)
            continue

        text = str(event.get("text") or "")
        text_hash = str(event.get("text_sha256") or hashlib.sha256(text.encode()).hexdigest())
        checkpoint_key = (event.get("turn_id"), text_hash)
        # task_complete can mirror the last assistant checkpoint; its text is
        # not a new boundary declaration.
        mirrored_checkpoint = event_type == "task_complete" and checkpoint_key in seen_checkpoint_text
        if not mirrored_checkpoint:
            for trigger in checkpoint_triggers(event):
                pending_triggers.append({"line_no": line_no, "trigger": trigger})
                if interval is None:
                    interval = start_interval(timestamp, line_no)

        if interval is None and category == "tool_call":
            interval = start_interval(timestamp, line_no)

        if interval is not None and category == "tool_call":
            interval["tool_calls"] += 1
            if event.get("tool_name") == "update_plan":
                snapshot = interval_snapshot(interval, timestamp, line_no)
                if pending_triggers and line_no not in interval["substitution_lines"]:
                    substitutions.append(
                        {
                            "line_no": line_no,
                            "start_line": interval["start_line"],
                            "tool_calls": snapshot["tool_calls"],
                            "elapsed_seconds": snapshot["elapsed_seconds"],
                        }
                    )
                    interval["substitution_lines"].add(line_no)
            action = tool_action_kind(event)
            if action == "edit":
                if interval["last_action"] == "verify":
                    interval["churn_cycle_count"] += 1
                interval["last_action"] = "edit"
            elif action == "verify":
                interval["last_action"] = "verify"
                interval["last_verify_line"] = line_no

        if category in {"assistant_message", "lifecycle"}:
            checkpoint = checkpoint_from_text(text)
            if checkpoint is not None and checkpoint_key not in seen_checkpoint_text:
                seen_checkpoint_text.add(checkpoint_key)
                if interval is None:
                    interval = start_interval(timestamp, line_no)
                snapshot = interval_snapshot(interval, timestamp, line_no)
                record = {
                    "line_no": line_no,
                    "status": checkpoint["status"],
                    "tool_calls": snapshot["tool_calls"],
                    "elapsed_seconds": snapshot["elapsed_seconds"],
                }
                if checkpoint["missing_fields"]:
                    incomplete.append({**record, "missing_fields": checkpoint["missing_fields"]})
                else:
                    valid.append(record)
                    pending_triggers.clear()
                    if exceeds(snapshot):
                        overruns.append({**snapshot, "checkpoint_line": line_no})
                    record_churn(interval)
                    interval = start_interval(timestamp, line_no)

        if interval is not None and category == "lifecycle" and event_type in {"task_complete", "turn_aborted"}:
            snapshot = interval_snapshot(interval, timestamp, line_no)
            if pending_triggers:
                missing.append({**snapshot, "reason": event_type, "triggers": list(pending_triggers)})
                pending_triggers.clear()
            record_churn(interval)
            interval = None

    if interval is not None:
        snapshot = interval_snapshot(interval, last_timestamp, last_line)
        if pending_triggers:
            missing.append({**snapshot, "reason": "source_ended", "triggers": list(pending_triggers)})
        record_churn(interval)

    return {
        "limits": {"max_tool_calls": 40, "max_elapsed_seconds": 45 * 60},
        "limits_advisory": True,
        "trigger_policy": "explicit_event_evidence",
        "supported_triggers": list(CHECKPOINT_TRIGGERS),
        "valid_checkpoints": len(valid),
        "incomplete_checkpoints": len(incomplete),
        "interval_overruns": len(overruns),
        "missing_checkpoints": len(missing),
        "suspected_update_plan_substitutions": len(substitutions),
        "suspected_single_finding_churn_cycles": sum(item["cycles"] for item in churn_cycles),
        "evidence": {
            "valid_checkpoints": valid,
            "incomplete_checkpoints": incomplete,
            "interval_overruns": overruns,
            "missing_checkpoints": missing,
            "suspected_update_plan_substitutions": substitutions,
            "suspected_single_finding_churn": churn_cycles,
        },
    }


def union_duration_seconds(intervals: Iterable[tuple[datetime, datetime]]) -> float:
    ordered = sorted((start, end) for start, end in intervals if end >= start)
    if not ordered:
        return 0.0
    merged: list[tuple[datetime, datetime]] = []
    for start, end in ordered:
        if not merged or start > merged[-1][1]:
            merged.append((start, end))
        elif end > merged[-1][1]:
            merged[-1] = (merged[-1][0], end)
    return sum((end - start).total_seconds() for start, end in merged)


def ensure_output_dir(output_dir: Path, force: bool) -> None:
    if output_dir.exists() and any(output_dir.iterdir()) and not force:
        raise FileExistsError(
            f"output directory is not empty: {output_dir} (use --force to replace generated files)"
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "large-outputs").mkdir(exist_ok=True)
    if force:
        for name in (
            "inventory.json",
            "events.normalized.jsonl",
            "timeline.md",
            "evidence-index.json",
            "parse-errors.jsonl",
        ):
            path = output_dir / name
            if path.exists():
                path.unlink()
        for path in (output_dir / "large-outputs").glob("*.txt"):
            path.unlink()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def clean_thread(
    source: Path,
    output_dir: Path,
    *,
    large_threshold: int = 32_768,
    preview_limit: int = 4_000,
    force: bool = False,
    until_timestamp: str | None = None,
) -> dict[str, Any]:
    if not source.is_file():
        raise FileNotFoundError(source)
    if source.resolve().is_relative_to(output_dir.resolve()):
        raise ValueError("output directory must not contain the source log")
    if until_timestamp is not None and parse_timestamp(until_timestamp) is None:
        raise ValueError(f"invalid --until timestamp: {until_timestamp}")
    ensure_output_dir(output_dir, force)

    source_hasher = hashlib.sha256()
    until_dt = parse_timestamp(until_timestamp)
    top_types: Counter[str] = Counter()
    subtypes: Counter[str] = Counter()
    categories: Counter[str] = Counter()
    excluded: Counter[str] = Counter()
    tools: Counter[str] = Counter()
    tool_call_names: dict[str, str] = {}
    parse_errors: list[dict[str, Any]] = []
    evidence_index: list[dict[str, Any]] = []
    turns: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "started": None,
            "completed": None,
            "duration_ms": None,
            "objective": "",
            "tool_calls": 0,
            "patches": 0,
            "errors": 0,
            "task_complete": False,
        }
    )
    message_seen: set[tuple[str | None, str | None, str]] = set()
    current_turn: str | None = None
    first_timestamp: str | None = None
    last_timestamp: str | None = None
    session_meta: dict[str, Any] = {}
    line_count = 0
    processed_bytes = 0
    redaction_count = 0
    normalized_count = 0

    normalized_path = output_dir / "events.normalized.jsonl"
    errors_path = output_dir / "parse-errors.jsonl"
    with source.open("rb") as raw_file, normalized_path.open(
        "w", encoding="utf-8"
    ) as normalized_file, errors_path.open("w", encoding="utf-8") as errors_file:
        for line_no, raw_line in enumerate(raw_file, 1):
            line_count = line_no
            if until_dt is not None:
                try:
                    probe = json.loads(raw_line.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    probe = None
                probe_timestamp = parse_timestamp(probe.get("timestamp")) if isinstance(probe, dict) else None
                if probe_timestamp is not None and probe_timestamp > until_dt:
                    line_count = line_no - 1
                    break
            source_hasher.update(raw_line)
            processed_bytes += len(raw_line)
            raw_sha = hashlib.sha256(raw_line).hexdigest()
            try:
                record = json.loads(raw_line.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                item = {
                    "line_no": line_no,
                    "raw_line_sha256": raw_sha,
                    "error": f"{type(exc).__name__}: {exc}",
                }
                parse_errors.append(item)
                errors_file.write(json.dumps(item, ensure_ascii=False) + "\n")
                continue
            if not isinstance(record, dict):
                excluded["non_object"] += 1
                continue

            source_type = str(record.get("type") or "unknown")
            payload = record.get("payload") if isinstance(record.get("payload"), dict) else {}
            event_type = str(payload.get("type") or source_type)
            top_types[source_type] += 1
            subtypes[f"{source_type}/{event_type}"] += 1
            timestamp = record.get("timestamp")
            if isinstance(timestamp, str):
                first_timestamp = first_timestamp or timestamp
                last_timestamp = timestamp

            if source_type == "session_meta" and not session_meta:
                session_meta = {
                    key: payload.get(key)
                    for key in ("id", "session_id", "cwd", "originator", "cli_version", "source")
                    if key in payload
                }

            if source_type == "event_msg" and event_type == "task_started":
                possible_turn = payload.get("turn_id")
                if isinstance(possible_turn, str):
                    current_turn = possible_turn
                    turns[current_turn]["started"] = timestamp

            event, reason = describe_event(record, current_turn)
            if event is None:
                excluded[reason or "unselected"] += 1
                continue

            turn_id = event.get("turn_id")
            category = str(event["category"])
            original_text = str(event.pop("text", ""))
            original_text_sha = hashlib.sha256(original_text.encode("utf-8")).hexdigest()
            role = event.get("role")
            if category in {"user_message", "assistant_message"}:
                dedupe_key = (turn_id, role, original_text_sha)
                if dedupe_key in message_seen:
                    excluded["duplicate_message"] += 1
                    continue
                message_seen.add(dedupe_key)

            redacted_text, event_redactions = redact(original_text)
            redaction_count += event_redactions
            text_bytes = len(original_text.encode("utf-8"))
            evidence_file: str | None = None
            if text_bytes > large_threshold:
                evidence_name = f"line-{line_no:06d}-{category}-{original_text_sha[:12]}.txt"
                evidence_path = output_dir / "large-outputs" / evidence_name
                evidence_path.write_text(redacted_text, encoding="utf-8")
                evidence_file = str(evidence_path.relative_to(output_dir))
                evidence_index.append(
                    {
                        "source_line": line_no,
                        "turn_id": turn_id,
                        "category": category,
                        "tool_name": event.get("tool_name"),
                        "text_bytes": text_bytes,
                        "text_sha256": original_text_sha,
                        "redaction_count": event_redactions,
                        "file": evidence_file,
                    }
                )

            event.update(
                {
                    "line_no": line_no,
                    "raw_line_bytes": len(raw_line),
                    "raw_line_sha256": raw_sha,
                    "text_bytes": text_bytes,
                    "text_sha256": original_text_sha,
                    "redaction_count": event_redactions,
                    "truncated": len(redacted_text) > preview_limit,
                    "evidence_file": evidence_file,
                    "text": preview_text(redacted_text, preview_limit),
                }
            )

            call_id = event.get("call_id")
            tool_name = event.get("tool_name")
            if category == "tool_call":
                if isinstance(tool_name, str) and tool_name:
                    tools[tool_name] += 1
                    if isinstance(call_id, str):
                        tool_call_names[call_id] = tool_name
                if isinstance(turn_id, str):
                    turns[turn_id]["tool_calls"] += 1
            elif category == "tool_output" and not tool_name and isinstance(call_id, str):
                resolved_name = tool_call_names.get(call_id)
                if resolved_name:
                    event["tool_name"] = resolved_name
            if isinstance(turn_id, str):
                turn = turns[turn_id]
                if category == "user_message":
                    objective = clean_objective(redacted_text.strip())
                    # Host-injected AGENTS/context records can arrive before the real
                    # user message. Prefer the short explicit request when available.
                    if event.get("source_type") == "event_msg" or (
                        not turn["objective"]
                        and len(objective) <= 1_000
                        and not objective.startswith("# AGENTS.md instructions")
                    ):
                        turn["objective"] = preview_text(objective, 240)
                if category == "patch":
                    turn["patches"] += 1
                if category == "error" or (
                    category == "tool_output"
                    and re.search(r"(?im)^(script failed|error:|fatal:)", redacted_text)
                ):
                    turn["errors"] += 1
                if source_type == "event_msg" and event_type == "task_complete":
                    turn["completed"] = timestamp
                    turn["duration_ms"] = payload.get("duration_ms")
                    turn["task_complete"] = True

            categories[category] += 1
            normalized_count += 1
            normalized_file.write(json.dumps(event, ensure_ascii=False) + "\n")

    if not parse_errors:
        errors_path.unlink()

    checkpoint_protocol = analyze_checkpoint_protocol(normalized_path)

    intervals: list[tuple[datetime, datetime]] = []
    reported_duration_ms = 0
    for turn in turns.values():
        start = parse_timestamp(turn["started"])
        end = parse_timestamp(turn["completed"])
        if start and end:
            intervals.append((start, end))
        if isinstance(turn["duration_ms"], (int, float)):
            reported_duration_ms += int(turn["duration_ms"])

    first_dt = parse_timestamp(first_timestamp)
    last_dt = parse_timestamp(last_timestamp)
    wall_seconds = (last_dt - first_dt).total_seconds() if first_dt and last_dt else None
    active_union_seconds = union_duration_seconds(intervals)
    inventory = {
        "source": {
            "path": str(source.resolve()),
            "size_bytes": source.stat().st_size,
            "processed_bytes": processed_bytes,
            "sha256": source_hasher.hexdigest(),
            "line_count": line_count,
            "first_timestamp": first_timestamp,
            "last_timestamp": last_timestamp,
            "wall_duration_seconds": wall_seconds,
            "prefix_until_timestamp": until_timestamp,
        },
        "session": session_meta,
        "counts": {
            "top_level_types": dict(top_types.most_common()),
            "event_types": dict(subtypes.most_common()),
            "normalized_categories": dict(categories.most_common()),
            "excluded": dict(excluded.most_common()),
            "tools": dict(tools.most_common()),
            "turns": len(turns),
            "task_started_turns": sum(bool(turn["started"]) for turn in turns.values()),
            "orphan_turns": sum(not bool(turn["started"]) for turn in turns.values()),
            "completed_turns": sum(bool(turn["task_complete"]) for turn in turns.values()),
            "normalized_events": normalized_count,
            "large_outputs": len(evidence_index),
            "parse_errors": len(parse_errors),
            "redactions": redaction_count,
        },
        "time": {
            "completed_turn_interval_union_seconds": active_union_seconds,
            "reported_completed_turn_duration_sum_ms": reported_duration_ms,
            "note": "Active time is an interval estimate, not model compute time; overlapping turns are merged.",
        },
        "checkpoint_protocol": checkpoint_protocol,
        "generation": {
            "large_threshold_bytes": large_threshold,
            "preview_limit_characters": preview_limit,
            "source_opened_read_only": True,
            "generated_text_redacted": True,
        },
    }
    write_json(output_dir / "inventory.json", inventory)
    write_json(output_dir / "evidence-index.json", evidence_index)
    write_timeline(output_dir / "timeline.md", source, inventory, turns)
    return inventory


def markdown_cell(value: Any) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")


def write_timeline(
    path: Path,
    source: Path,
    inventory: dict[str, Any],
    turns: dict[str, dict[str, Any]],
) -> None:
    source_info = inventory["source"]
    counts = inventory["counts"]
    time_info = inventory["time"]
    checkpoint_protocol = inventory["checkpoint_protocol"]
    lines = [
        "# Codex thread audit timeline",
        "",
        f"- Source: `{source.resolve()}`",
        f"- SHA-256: `{source_info['sha256']}`",
        f"- Lines: {source_info['line_count']}",
        f"- Wall duration: {source_info['wall_duration_seconds']} seconds",
        f"- Completed-turn interval union: {time_info['completed_turn_interval_union_seconds']} seconds",
        f"- Tracked turns: {counts['turns']} ({counts['task_started_turns']} task-started, "
        f"{counts['orphan_turns']} orphan, {counts['completed_turns']} completed)",
        f"- Normalized events: {counts['normalized_events']}",
        f"- Large outputs: {counts['large_outputs']}",
        f"- Redactions: {counts['redactions']}",
        f"- Checkpoints: {checkpoint_protocol['valid_checkpoints']} valid, "
        f"{checkpoint_protocol['incomplete_checkpoints']} incomplete, "
        f"{checkpoint_protocol['missing_checkpoints']} missing",
        f"- Advisory work-interval measurements: {checkpoint_protocol['interval_overruns']} checkpointed overrun, "
        f"{checkpoint_protocol['suspected_update_plan_substitutions']} suspected update-plan substitution, "
        f"{checkpoint_protocol['suspected_single_finding_churn_cycles']} suspected single-finding churn cycles",
        "",
        "Checkpoint deviations are protocol evidence where explicit; missing checkpoints require an evidenced event trigger. "
        "The 40-call/45-minute measurements are advisory, not mandatory checkpoint limits; "
        "update-plan substitution and churn are suspected heuristic signals, not proven violations.",
        "Active time is an interval estimate derived from task lifecycle events; it is not model compute time.",
        "",
        "| Turn | Started | Completed | Duration ms | Tools | Patches | Errors | Objective |",
        "|---|---|---|---:|---:|---:|---:|---|",
    ]
    ordered = sorted(
        turns.items(), key=lambda item: (item[1]["started"] or "", item[0])
    )
    for turn_id, turn in ordered:
        lines.append(
            "| "
            + " | ".join(
                markdown_cell(value)
                for value in (
                    turn_id,
                    turn["started"],
                    turn["completed"],
                    turn["duration_ms"],
                    turn["tool_calls"],
                    turn["patches"],
                    turn["errors"],
                    turn["objective"],
                )
            )
            + " |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="source Codex rollout JSONL")
    parser.add_argument("--out", required=True, type=Path, help="generated artifact directory")
    parser.add_argument(
        "--large-threshold",
        type=int,
        default=32_768,
        help="spill extracted text larger than this byte count (default: 32768)",
    )
    parser.add_argument(
        "--preview-limit",
        type=int,
        default=4_000,
        help="maximum characters retained inline per normalized event (default: 4000)",
    )
    parser.add_argument("--force", action="store_true", help="replace prior generated artifacts")
    parser.add_argument(
        "--until",
        dest="until_timestamp",
        help="process only records up to this ISO-8601 timestamp; useful for a live-growing log",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.large_threshold < 1 or args.preview_limit < 80:
        print("threshold must be positive and preview limit must be at least 80", file=sys.stderr)
        return 2
    try:
        inventory = clean_thread(
            args.input,
            args.out,
            large_threshold=args.large_threshold,
            preview_limit=args.preview_limit,
            force=args.force,
            until_timestamp=args.until_timestamp,
        )
    except (FileNotFoundError, FileExistsError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    counts = inventory["counts"]
    print(
        f"processed {inventory['source']['line_count']} lines; "
        f"normalized {counts['normalized_events']} events across {counts['turns']} turns; "
        f"artifacts: {args.out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
