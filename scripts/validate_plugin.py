#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml


SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

REQUIRED_INTERFACE_FIELDS = (
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
    "capabilities",
    "defaultPrompt",
)

FORBIDDEN_MANIFEST_FIELDS = ("apps", "mcpServers", "cli")

LEGACY_FILES = (
    "SKILL.md",
    "PIPELINE-REDESIGN.md",
    "config.default.yaml",
    "scripts/checklist_gate.py",
    "skills/bruce/PIPELINE-REDESIGN.md",
    "skills/bruce/config.default.yaml",
    "skills/bruce/scripts/checklist_gate.py",
    "skills/bruce/templates/checklist.json",
    "skills/bruce/templates/clarification.md",
    "skills/bruce/templates/plan-review.md",
    "skills/bruce/templates/completion-review.md",
    "templates/checklist.json",
    "templates/clarification.md",
    "templates/plan-review.md",
    "templates/completion-review.md",
    "skills/spawn-execute/REDESIGN.md",
    "skills/spawn-execute/templates/progress.md",
    "skills/verify-completion/SKILL.md",
    "skills/write-db-design/DESIGN.md",
)

ALLOWED_SKILL_FRONTMATTER = {
    "name",
    "description",
    "license",
    "allowed-tools",
    "metadata",
}

LEGACY_RUNTIME_PATTERNS = (
    ("file state machine", re.compile(r"\bfile-based state machine\b", re.IGNORECASE)),
    ("checklist transition command", re.compile(r"checklist_gate\.py\s+--run-dir", re.IGNORECASE)),
    ("lane-backed runtime state", re.compile(r"\btriage\.lane\b", re.IGNORECASE)),
    ("progress ledger as truth", re.compile(r"progress\.md\s+is\s+the\s+single\s+source\s+of\s+truth", re.IGNORECASE)),
    ("numbered fixed stage", re.compile(r"\bSTAGE\s*[①②③④]", re.IGNORECASE)),
)


class ValidationError(Exception):
    pass


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValidationError(f"missing required file: {path}") from error
    except json.JSONDecodeError as error:
        raise ValidationError(f"invalid JSON in {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValidationError(f"expected JSON object: {path}")
    return value


def load_yaml(path: Path, label: str) -> dict:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValidationError(f"missing {label}: {path}") from error
    except yaml.YAMLError as error:
        raise ValidationError(f"invalid YAML in {label} {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValidationError(f"expected YAML object in {label}: {path}")
    return value


def contained_path(root: Path, raw: str, label: str) -> Path:
    if not raw.startswith("./"):
        raise ValidationError(f"{label} must start with './': {raw}")
    target = (root / raw).resolve()
    try:
        target.relative_to(root)
    except ValueError as error:
        raise ValidationError(f"{label} escapes plugin root: {raw}") from error
    return target


def validate_manifest(root: Path) -> dict:
    manifest = load_json(root / ".codex-plugin/plugin.json")
    for key in ("name", "version", "description", "author", "skills", "interface"):
        if not manifest.get(key):
            raise ValidationError(f"manifest missing required field: {key}")
    if manifest["name"] != root.name:
        raise ValidationError("manifest name must match plugin root directory")
    if not SEMVER.fullmatch(manifest["version"]):
        raise ValidationError("manifest version must be strict semver")
    if not isinstance(manifest["author"], dict) or not manifest["author"].get("name"):
        raise ValidationError("manifest author.name is required")
    for field in FORBIDDEN_MANIFEST_FIELDS:
        if field in manifest:
            raise ValidationError(f"skills-only Bruce plugin must not declare {field}")
    if manifest["skills"] != "./skills/":
        raise ValidationError("manifest skills must be exactly './skills/'")
    if not contained_path(root, manifest["skills"], "manifest skills path").is_dir():
        raise ValidationError("manifest skills path does not exist")
    if manifest.get("hooks") != "./hooks/hooks.json":
        raise ValidationError("manifest hooks must be exactly './hooks/hooks.json'")
    if not contained_path(root, manifest["hooks"], "manifest hooks path").is_file():
        raise ValidationError("manifest hooks path does not exist")

    interface = manifest["interface"]
    if not isinstance(interface, dict):
        raise ValidationError("manifest interface must be an object")
    for key in REQUIRED_INTERFACE_FIELDS:
        if not interface.get(key):
            raise ValidationError(f"manifest interface missing required field: {key}")
    prompts = interface["defaultPrompt"]
    if not isinstance(prompts, list) or len(prompts) > 3:
        raise ValidationError("interface.defaultPrompt must contain at most 3 prompts")
    if any(not isinstance(item, str) or len(item) > 128 for item in prompts):
        raise ValidationError("default prompts must be strings of at most 128 characters")
    for key in ("homepage", "repository"):
        if key in manifest and not str(manifest[key]).startswith("https://"):
            raise ValidationError(f"manifest {key} must be an absolute https URL")
    for key in ("websiteURL", "privacyPolicyURL", "termsOfServiceURL"):
        if key in interface and not str(interface[key]).startswith("https://"):
            raise ValidationError(f"interface {key} must be an absolute https URL")
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", str(interface.get("brandColor", ""))):
        raise ValidationError("interface.brandColor must be a six-digit hex color")
    for key in ("composerIcon", "logo"):
        raw_path = interface.get(key)
        if not isinstance(raw_path, str):
            raise ValidationError(f"interface.{key} must be a relative path")
        path = contained_path(root, raw_path, f"interface.{key}")
        if not path.is_file() or path.suffix.lower() != ".png":
            raise ValidationError(f"interface.{key} must point to an existing PNG file")
    return manifest


def validate_hooks(root: Path, manifest: dict) -> None:
    root = root.resolve()
    hooks_path = contained_path(root, manifest["hooks"], "manifest hooks path")
    config = load_json(hooks_path)
    if set(config) - {"description", "hooks"}:
        raise ValidationError("hooks config contains unsupported top-level fields")
    hooks = config.get("hooks")
    if not isinstance(hooks, dict) or set(hooks) != {"PostToolUse"}:
        raise ValidationError("Bruce hooks config must contain only PostToolUse")
    entries = hooks["PostToolUse"]
    if not isinstance(entries, list) or len(entries) != 1:
        raise ValidationError("PostToolUse must contain one matcher entry")
    entry = entries[0]
    if not isinstance(entry, dict) or not isinstance(entry.get("matcher"), str):
        raise ValidationError("PostToolUse matcher entry is invalid")
    matcher = entry["matcher"]
    for required_tool in ("Bash", "apply_patch"):
        if required_tool not in matcher:
            raise ValidationError(f"PostToolUse matcher must cover {required_tool}")
    commands = entry.get("hooks")
    if not isinstance(commands, list) or len(commands) != 1:
        raise ValidationError("PostToolUse must contain one command hook")
    command = commands[0]
    if not isinstance(command, dict) or command.get("type") != "command":
        raise ValidationError("PostToolUse hook must be a command")
    command_text = command.get("command")
    expected = "$PLUGIN_ROOT/hooks/post_tool_review_reminder.py"
    if not isinstance(command_text, str) or expected not in command_text:
        raise ValidationError("PostToolUse command must resolve through $PLUGIN_ROOT")
    if ".codex/hooks" in command_text:
        raise ValidationError("plugin hook command must not use a project-relative .codex path")
    timeout = command.get("timeout")
    if not isinstance(timeout, int) or not 1 <= timeout <= 30:
        raise ValidationError("PostToolUse command timeout must be between 1 and 30 seconds")
    if not (root / "hooks/post_tool_review_reminder.py").is_file():
        raise ValidationError("missing PostToolUse reminder script")
    if not (root / "skills/design-gate/scripts/validate_design_review.py").is_file():
        raise ValidationError("missing Design Review validator script")


def validate_marketplace(root: Path, manifest: dict) -> None:
    marketplace = load_json(root / ".agents/plugins/marketplace.json")
    entries = marketplace.get("plugins")
    if marketplace.get("name") != "bruce" or not isinstance(entries, list) or len(entries) != 1:
        raise ValidationError("marketplace must contain one Bruce entry")
    entry = entries[0]
    if entry.get("name") != manifest["name"]:
        raise ValidationError("marketplace entry name must match manifest")
    if entry.get("source") != {"source": "local", "path": "."}:
        raise ValidationError("repo-root marketplace source must be local path '.'")
    policy = entry.get("policy")
    if not isinstance(policy, dict):
        raise ValidationError("marketplace policy is required")
    if policy.get("installation") not in {"NOT_AVAILABLE", "AVAILABLE", "INSTALLED_BY_DEFAULT"}:
        raise ValidationError("invalid marketplace installation policy")
    if policy.get("authentication") not in {"ON_INSTALL", "ON_USE"}:
        raise ValidationError("invalid marketplace authentication policy")
    if entry.get("category") != manifest["interface"]["category"]:
        raise ValidationError("marketplace and manifest category must match")
    if not (root / ".codex-plugin/plugin.json").is_file():
        raise ValidationError("marketplace source does not resolve to a plugin root")


def parse_skill_frontmatter(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValidationError(f"skill missing YAML frontmatter: {path}")
    try:
        _, raw, _ = text.split("---", 2)
    except ValueError as error:
        raise ValidationError(f"skill frontmatter is not closed: {path}") from error
    try:
        values = yaml.safe_load(raw)
    except yaml.YAMLError as error:
        raise ValidationError(f"invalid skill frontmatter YAML: {path}: {error}") from error
    if not isinstance(values, dict):
        raise ValidationError(f"skill frontmatter must be an object: {path}")
    name = values.get("name", "")
    description = values.get("description", "")
    if not isinstance(name, str) or not name.strip():
        raise ValidationError(f"skill name must be a non-empty string: {path}")
    if not isinstance(description, str) or not description.strip():
        raise ValidationError(f"skill requires name and description: {path}")
    unexpected = set(values) - ALLOWED_SKILL_FRONTMATTER
    if unexpected:
        raise ValidationError(f"unsupported skill frontmatter fields {sorted(unexpected)}: {path}")
    return name.strip(), description.strip()


def validate_agents_metadata(skill_dir: Path, skill_name: str) -> None:
    path = skill_dir / "agents/openai.yaml"
    metadata = load_yaml(path, "skill UI metadata")
    unexpected = set(metadata) - {"interface", "dependencies", "policy"}
    if unexpected:
        raise ValidationError(f"unsupported skill UI metadata fields {sorted(unexpected)}: {path}")
    if not isinstance(metadata.get("interface"), dict):
        raise ValidationError(f"skill UI metadata requires an interface object: {path}")
    interface = metadata["interface"]
    required = ("display_name", "short_description", "default_prompt")
    for key in required:
        if not isinstance(interface.get(key), str) or not interface[key].strip():
            raise ValidationError(f"skill UI metadata missing {key}: {path}")
    length = len(interface["short_description"])
    if not 25 <= length <= 64:
        raise ValidationError(f"skill short_description must be 25-64 characters: {path}")
    if f"${skill_name}" not in interface["default_prompt"]:
        raise ValidationError(f"skill default_prompt must mention ${skill_name}: {path}")
    if "dependencies" in metadata and not isinstance(metadata["dependencies"], dict):
        raise ValidationError(f"skill UI metadata dependencies must be an object: {path}")
    if "policy" in metadata and not isinstance(metadata["policy"], dict):
        raise ValidationError(f"skill UI metadata policy must be an object: {path}")


def validate_skills(root: Path) -> None:
    skill_files = sorted((root / "skills").glob("*/SKILL.md"))
    if not skill_files or not (root / "skills/bruce/SKILL.md").is_file():
        raise ValidationError("skills/bruce/SKILL.md is required")
    for path in skill_files:
        name, _ = parse_skill_frontmatter(path)
        if name != path.parent.name or not SKILL_NAME.fullmatch(name):
            raise ValidationError(f"skill name must match folder and use kebab-case: {path}")
        validate_agents_metadata(path.parent, name)
        text = path.read_text(encoding="utf-8")
        for raw_link in MARKDOWN_LINK.findall(text):
            if "://" in raw_link or raw_link.startswith("#"):
                continue
            target = (path.parent / raw_link).resolve()
            try:
                target.relative_to(root)
            except ValueError as error:
                raise ValidationError(f"skill reference escapes plugin root: {path} -> {raw_link}") from error
            if not target.is_file():
                raise ValidationError(f"missing skill reference: {path} -> {raw_link}")


def active_skill_resources(root: Path) -> set[Path]:
    root = root.resolve()
    resources: set[Path] = set()
    for path in sorted((root / "skills").glob("*/SKILL.md")):
        resources.add(path.resolve())
        text = path.read_text(encoding="utf-8")
        for raw_link in MARKDOWN_LINK.findall(text):
            if "://" in raw_link or raw_link.startswith("#"):
                continue
            target = (path.parent / raw_link).resolve()
            if target.is_file():
                resources.add(target)
    return resources


def validate_legacy_surface(root: Path) -> None:
    root = root.resolve()
    for relative in LEGACY_FILES:
        if (root / relative).exists():
            raise ValidationError(f"legacy active surface remains: {relative}")
    for path in sorted(active_skill_resources(root)):
        text = path.read_text(encoding="utf-8")
        for label, pattern in LEGACY_RUNTIME_PATTERNS:
            if pattern.search(text):
                raise ValidationError(f"legacy runtime semantics '{label}' remain in {path.relative_to(root)}")


def validate(root: Path) -> None:
    root = root.resolve()
    manifest = validate_manifest(root)
    validate_hooks(root, manifest)
    validate_marketplace(root, manifest)
    validate_skills(root)
    validate_legacy_surface(root)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Bruce Codex workflow plugin")
    parser.add_argument("plugin_path", nargs="?", default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        validate(Path(args.plugin_path))
    except ValidationError as error:
        print(f"Bruce plugin validation failed: {error}", file=sys.stderr)
        return 1
    print(f"Bruce plugin validation passed: {Path(args.plugin_path).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
