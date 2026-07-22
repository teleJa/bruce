from __future__ import annotations

import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def read_json(relative_path: str) -> dict:
    return json.loads(read(relative_path))


def frontmatter(relative_path: str) -> dict[str, str]:
    text = read(relative_path)
    if not text.startswith("---\n"):
        raise AssertionError(f"{relative_path} has no YAML frontmatter")
    _, raw, _ = text.split("---", 2)
    result = yaml.safe_load(raw)
    if not isinstance(result, dict):
        raise AssertionError(f"{relative_path} frontmatter is not a YAML object")
    return result


def markdown_links(relative_path: str) -> list[str]:
    return re.findall(r"\[[^\]]+\]\(([^)]+)\)", read(relative_path))


def skill_markdown_files() -> list[Path]:
    return sorted((ROOT / "skills").glob("**/*.md"))
