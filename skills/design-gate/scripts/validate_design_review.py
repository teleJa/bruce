#!/usr/bin/env python3
"""Validate one Bruce design-review.md against its current change directory."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml


CANDIDATES = (
    "Requirement or clarification",
    "Architecture",
    "API/file contracts",
    "Database/table design",
    "Implementation plan",
    "Test design",
    "UI prototype",
)

READINESS_FIELDS = (
    "Facts and consistency",
    "Acceptance and verification coverage",
    "Risk and recovery coverage",
    "Existing-product visual authority and compatibility",
    "Deterministic artifact visual assertions",
    "Blocking findings",
    "Evidence boundary",
    "Smallest next action",
)

NONE_PATHS = {"none", "n/a", "not-applicable", "not applicable", "无"}
WEAK_EVIDENCE = {"none", "n/a", "not-applicable", "not applicable", "无", "无需", "不适用"}
PLACEHOLDER = re.compile(
    r"(?im)(?:\b(?:TODO|TBD|FIXME)\b|待补充|待定|"
    r"<[^>\n]*(?:objective|scope|path|evidence|pass|blocked|required|skipped|action|none)[^>\n]*>)"
)
ROW_SPLIT = re.compile(r"(?<!\\)\|")


@dataclass(frozen=True)
class CandidateRow:
    name: str
    applicability: str
    delivery: str
    path: str
    evidence: str


def _field(text: str, label: str) -> str | None:
    match = re.search(rf"(?m)^- {re.escape(label)}:\s*(.+?)\s*$", text)
    return match.group(1).strip() if match else None


def _section(text: str, title: str) -> str:
    match = re.search(
        rf"(?ms)^## {re.escape(title)}\s*$\n(.*?)(?=^## |\Z)",
        text,
    )
    return match.group(1) if match else ""


def _clean_cell(value: str) -> str:
    return value.strip().replace(r"\|", "|")


def _parse_candidate_rows(text: str) -> tuple[dict[str, CandidateRow], list[str]]:
    errors: list[str] = []
    rows: dict[str, CandidateRow] = {}
    in_matrix = False

    for raw_line in text.splitlines():
        if raw_line.strip() == "## Candidate Matrix":
            in_matrix = True
            continue
        if in_matrix and raw_line.startswith("## "):
            break
        if not in_matrix or not raw_line.lstrip().startswith("|"):
            continue

        cells = [_clean_cell(cell) for cell in ROW_SPLIT.split(raw_line.strip().strip("|"))]
        if not cells or cells[0] in {"Candidate", "---"} or set(cells[0]) == {"-"}:
            continue
        if len(cells) != 5:
            errors.append(f"candidate row must contain exactly 5 columns: {raw_line.strip()}")
            continue

        name, applicability, delivery, path, evidence = cells
        if name not in CANDIDATES:
            errors.append(f"unknown candidate: {name}")
            continue
        if name in rows:
            errors.append(f"duplicate candidate: {name}")
            continue
        rows[name] = CandidateRow(name, applicability, delivery, path, evidence)

    missing = [candidate for candidate in CANDIDATES if candidate not in rows]
    if missing:
        errors.append("missing candidates: " + ", ".join(missing))
    return rows, errors


def _is_none_path(value: str) -> bool:
    normalized = value.strip().strip("`").strip().lower()
    return normalized in NONE_PATHS


def _has_real_evidence(value: str) -> bool:
    normalized = value.strip().strip("`").strip()
    return len(normalized) >= 8 and normalized.lower() not in WEAK_EVIDENCE


def _resolve_artifact(change_dir: Path, raw_path: str) -> Path | None:
    value = raw_path.strip().strip("`").strip()
    if not value or _is_none_path(value):
        return None
    relative = Path(value)
    if relative.is_absolute():
        return None
    target = (change_dir / relative).resolve()
    try:
        target.relative_to(change_dir.resolve())
    except ValueError:
        return None
    return target


def _contains_blocked(value: str) -> bool:
    normalized = value.lower()
    normalized = re.sub(
        r"\b(?:no|without)\s+(?:blocking\s+)?(?:issues?|findings?)\b|"
        r"无(?:阻塞项|阻塞问题|阻塞发现|问题)",
        "",
        normalized,
    )
    return bool(re.search(r"\bblocked\b|\bissues?\b|阻塞|未通过|不通过", normalized))


def _blocking_findings_clear(value: str) -> bool:
    normalized = value.strip().strip("`").lower()
    if re.search(r"\b(?:except|however)\b|但是|但仍|除外", normalized):
        return False
    return bool(
        re.match(
            r"^(?:none|no\s+(?:blocking\s+)?(?:findings?|issues?)|无(?:阻塞项|阻塞问题|阻塞发现|问题))"
            r"(?:\s|[。.;；，,]|$)",
            normalized,
        )
    )


def _validate_task_package(change_dir: Path, plan_artifact: Path) -> list[str]:
    plan_text = plan_artifact.read_text(encoding="utf-8")
    declares_tasks = re.search(r"(?m)^- Path: `tasks/`\s*$", plan_text)
    has_task_section = re.search(r"(?m)^## Task package\s*$", plan_text)
    if not declares_tasks:
        if not has_task_section:
            return [
                "generated implementation plan must include a Task package section and declare "
                "tasks/ or record a concrete trivial documentation-only omission reason"
            ]
        omission_reason = _field(plan_text, "Omission reason") or ""
        if (
            not omission_reason
            or PLACEHOLDER.search(omission_reason)
            or not re.search(r"trivial|documentation-only|文档|简单", omission_reason, re.IGNORECASE)
        ):
            return [
                "implementation plan must declare tasks/ or record a concrete "
                "trivial documentation-only omission reason"
            ]
        return []

    errors: list[str] = []
    tasks_dir = change_dir / "tasks"
    index_path = tasks_dir / "index.yaml"
    if not tasks_dir.is_dir():
        return ["task package declares tasks/ but the directory is missing"]
    if not index_path.is_file():
        return ["task package declares tasks/ but tasks/index.yaml is missing"]

    try:
        index = yaml.safe_load(index_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        return [f"task package index is invalid YAML: {error}"]
    if not isinstance(index, dict):
        return ["task package index must be a YAML object"]
    if index.get("version") != 1:
        errors.append("task package index version must be 1")
    if index.get("execution") != "sequential":
        errors.append("task package execution must be sequential")

    entries = index.get("tasks")
    if not isinstance(entries, list) or not entries:
        return errors + ["task package index must contain a non-empty tasks list"]

    required_fields = (
        "task_id",
        "title",
        "contract_revision",
        "path",
        "depends_on",
        "acceptance_ids",
        "allowed_paths",
        "excluded_paths",
        "parallel_safe",
    )
    ids: set[str] = set()
    paths: set[str] = set()
    indexed_contract_paths: set[Path] = set()
    dependencies: dict[str, list[str]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("task package index entries must be objects")
            continue
        missing = [field for field in required_fields if field not in entry]
        if missing:
            errors.append("task package entry is missing: " + ", ".join(missing))
            continue

        raw_task_id = entry["task_id"]
        task_id = str(raw_task_id)
        if not isinstance(raw_task_id, str):
            errors.append(f"task id must be a string: {task_id}")
        if not re.fullmatch(r"T-[A-Za-z0-9][A-Za-z0-9_-]*", task_id):
            errors.append(f"invalid task id: {task_id}")
        if task_id in ids:
            errors.append(f"duplicate task id: {task_id}")
        ids.add(task_id)

        title = entry["title"]
        if not isinstance(title, str) or not title.strip():
            errors.append(f"task title must be a non-empty string: {task_id}")
        contract_revision = entry["contract_revision"]
        if (
            not isinstance(contract_revision, int)
            or isinstance(contract_revision, bool)
            or contract_revision < 1
        ):
            errors.append(f"contract_revision must be a positive integer: {task_id}")
        for field in ("acceptance_ids", "allowed_paths", "excluded_paths"):
            if not isinstance(entry[field], list):
                errors.append(f"{field} must be a list: {task_id}")
        if not isinstance(entry["parallel_safe"], bool):
            errors.append(f"parallel_safe must be a boolean: {task_id}")

        raw_path = entry["path"]
        if not isinstance(raw_path, str):
            errors.append(f"task path must be a string: {task_id}")
            continue
        path = Path(raw_path)
        resolved = (change_dir / path).resolve()
        try:
            resolved.relative_to(tasks_dir.resolve())
        except ValueError:
            errors.append(f"task path must stay under tasks/: {raw_path}")
            continue
        if path.as_posix() in paths:
            errors.append(f"duplicate task path: {raw_path}")
        paths.add(path.as_posix())
        if not resolved.is_file():
            errors.append(f"task contract does not exist: {raw_path}")
        else:
            indexed_contract_paths.add(resolved)
            task_text = resolved.read_text(encoding="utf-8")
            if not task_text.strip():
                errors.append(f"task contract is empty: {raw_path}")
            elif PLACEHOLDER.search(task_text):
                errors.append(f"task contract contains unresolved placeholders: {raw_path}")
            revision_match = re.search(
                r"(?m)^- Contract revision:\s*(\d+)\s*$", task_text
            )
            if revision_match is None:
                errors.append(f"task contract is missing Contract revision: {raw_path}")
            elif isinstance(contract_revision, int) and not isinstance(contract_revision, bool):
                if int(revision_match.group(1)) != contract_revision:
                    errors.append(f"task contract revision does not match index: {raw_path}")
            for heading in (
                "## Objective",
                "## Included scope",
                "## Excluded scope",
                "## Dependencies",
                "## Acceptance",
                "## Verification",
                "## Authorization and risks",
                "## Contract change rule",
            ):
                if heading not in task_text:
                    errors.append(f"task contract is missing {heading}: {raw_path}")

        depends_on = entry["depends_on"]
        if not isinstance(depends_on, list):
            errors.append(f"depends_on must be a list: {task_id}")
            dependencies[task_id] = []
        else:
            dependencies[task_id] = [str(value) for value in depends_on]

    for task_file in tasks_dir.rglob("T-*.md"):
        if task_file.resolve() not in indexed_contract_paths:
            relative = task_file.resolve().relative_to(tasks_dir.resolve())
            errors.append(f"task contract is not indexed: tasks/{relative.as_posix()}")

    for task_id, depends_on in dependencies.items():
        for dependency in depends_on:
            if dependency not in ids:
                errors.append(f"task {task_id} depends on unknown task: {dependency}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            errors.append(f"task dependency cycle includes: {task_id}")
            return
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in dependencies.get(task_id, []):
            if dependency in ids:
                visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in ids:
        visit(task_id)
    return errors


def validate_change_dir(change_dir: Path) -> list[str]:
    change_dir = change_dir.resolve()
    review_path = change_dir / "design-review.md"
    if not review_path.is_file():
        return [f"missing design review: {review_path}"]

    text = review_path.read_text(encoding="utf-8")
    errors: list[str] = []
    if not text.strip():
        return [f"empty design review: {review_path}"]
    if PLACEHOLDER.search(text):
        errors.append("design-review.md contains unresolved placeholders")

    section_names = ("Candidate Matrix", "Readiness", "Validation", "Verdict")
    for section_name in section_names:
        count = len(re.findall(rf"(?m)^## {re.escape(section_name)}\s*$", text))
        if count != 1:
            errors.append(f"design-review.md must contain exactly one ## {section_name} section")
    header_positions = [text.find(f"## {name}") for name in section_names]
    if all(position >= 0 for position in header_positions) and header_positions != sorted(header_positions):
        errors.append("Design Review sections must appear in Candidate Matrix, Readiness, Validation, Verdict order")

    preamble = text.split("## Candidate Matrix", 1)[0]
    readiness_text = _section(text, "Readiness")
    validation_text = _section(text, "Validation")
    verdict_text = _section(text, "Verdict")

    decision_fields = (
        "Behavior implementation",
        "Public/cross-component contract change",
        "Database/persistence design change",
        "Governing UI prototype",
    )
    for label in ("Objective", "Scope", "Implementation boundary", "Review mode", *decision_fields):
        if not _field(preamble, label):
            errors.append(f"missing review field: {label}")

    review_mode = (_field(preamble, "Review mode") or "").lower()
    if review_mode not in {"main-agent", "independent"}:
        errors.append("Review mode must be main-agent or independent")

    decisions: dict[str, str] = {}
    for label in decision_fields:
        value = (_field(preamble, label) or "").lower()
        decisions[label] = value
        if value not in {"yes", "no"}:
            errors.append(f"{label} must be yes or no")

    rows, row_errors = _parse_candidate_rows(text)
    errors.extend(row_errors)

    for candidate in CANDIDATES:
        row = rows.get(candidate)
        if row is None:
            continue
        applicability = row.applicability.lower()
        delivery = row.delivery.lower()
        if applicability not in {"required", "skipped"}:
            errors.append(f"{candidate}: applicability must be required or skipped")
            continue
        if delivery not in {"generated", "missing", "skipped"}:
            errors.append(f"{candidate}: delivery must be generated, missing, or skipped")
            continue
        if not _has_real_evidence(row.evidence):
            errors.append(f"{candidate}: repository-backed evidence is missing or too weak")

        valid_pair = (applicability, delivery) in {
            ("required", "generated"),
            ("required", "missing"),
            ("skipped", "skipped"),
        }
        if not valid_pair:
            errors.append(f"{candidate}: invalid applicability/delivery pair {applicability}/{delivery}")

        if delivery == "generated":
            artifact = _resolve_artifact(change_dir, row.path)
            if artifact is None:
                errors.append(f"{candidate}: generated path must be a contained relative path")
            elif not artifact.is_file():
                errors.append(f"{candidate}: generated artifact does not exist: {row.path}")
            else:
                artifact_text = artifact.read_text(encoding="utf-8")
                if not artifact_text.strip():
                    errors.append(f"{candidate}: generated artifact is empty: {row.path}")
                elif PLACEHOLDER.search(artifact_text):
                    errors.append(f"{candidate}: generated artifact contains unresolved placeholders: {row.path}")
        elif not _is_none_path(row.path):
            errors.append(f"{candidate}: {delivery} delivery must use path none")

    generated_paths: dict[str, str] = {}
    for row in rows.values():
        if row.delivery.lower() != "generated":
            continue
        normalized_path = row.path.strip().strip("`").strip()
        if normalized_path == "design-review.md":
            errors.append(f"{row.name}: generated artifact cannot be design-review.md itself")
        previous = generated_paths.get(normalized_path)
        if previous is not None:
            errors.append(f"{row.name}: generated artifact path duplicates {previous}: {normalized_path}")
        else:
            generated_paths[normalized_path] = row.name

    plan = rows.get("Implementation plan")
    tests = rows.get("Test design")
    if plan and plan.applicability.lower() == "required":
        if not tests or tests.applicability.lower() != "required":
            errors.append("a required persisted Implementation plan requires Test design")
        elif plan.delivery.lower() == "generated":
            plan_artifact = _resolve_artifact(change_dir, plan.path)
            if plan_artifact is not None and plan_artifact.is_file():
                errors.extend(_validate_task_package(change_dir, plan_artifact))

    decision_requirements = {
        "Public/cross-component contract change": "API/file contracts",
        "Database/persistence design change": "Database/table design",
        "Governing UI prototype": "UI prototype",
    }
    for decision, candidate in decision_requirements.items():
        if decisions.get(decision) != "yes":
            continue
        row = rows.get(candidate)
        if not row or row.applicability.lower() != "required":
            errors.append(f"{decision}: yes requires {candidate}")

    readiness: dict[str, str] = {}
    for label in READINESS_FIELDS:
        value = _field(readiness_text, label)
        if not value:
            errors.append(f"missing readiness field: {label}")
        else:
            readiness[label] = value
            if PLACEHOLDER.search(value):
                errors.append(f"readiness field contains a placeholder: {label}")

    validation_command = _field(validation_text, "Command")
    validation_result = (_field(validation_text, "Result") or "").lower()
    if not validation_command or "validate_design_review.py" not in validation_command or "--change-dir" not in validation_command:
        errors.append("Validation Command must invoke validate_design_review.py with --change-dir")
    if not validation_result or not re.match(r"^pass(?:\s|[。.;；，,]|$)", validation_result):
        errors.append("Validation Result must start with pass")

    verdicts = re.findall(r"(?m)^Design:\s*(pass|blocked)\s*$", verdict_text, flags=re.IGNORECASE)
    if len(verdicts) != 1:
        errors.append("design-review.md must contain exactly one Design: pass|blocked verdict")
        verdict = ""
    else:
        verdict = verdicts[0].lower()

    if verdict == "pass":
        for row in rows.values():
            if row.applicability.lower() == "required" and row.delivery.lower() != "generated":
                errors.append(f"Design: pass cannot retain a missing required artifact: {row.name}")
        for label, value in readiness.items():
            if label != "Blocking findings" and _contains_blocked(value):
                errors.append(f"Design: pass conflicts with blocked readiness: {label}")
        blockers = readiness.get("Blocking findings", "")
        if blockers and not _blocking_findings_clear(blockers):
            errors.append("Design: pass requires Blocking findings to be none")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Bruce design-review.md")
    parser.add_argument("--change-dir", required=True, type=Path)
    args = parser.parse_args()

    errors = validate_change_dir(args.change_dir)
    if errors:
        print("Bruce Design Review validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Bruce Design Review validation passed: {args.change_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
