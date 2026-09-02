#!/usr/bin/env python3
"""Generate an executable project-local environment operations Skill from a confirmed Profile."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import stat
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
PROFILE_VALIDATOR = ROOT / "skills/environment-profile/scripts/validate_profile.py"
SECRET_ASSIGNMENT = re.compile(r"(?i)^(?:[A-Z0-9_]*(?:PASSWORD|PASSWD|TOKEN|API_KEY|SECRET)[A-Z0-9_]*)=")
SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")
CRITICAL_CATEGORIES = {
    "migrate", "seed", "reset", "drop", "destroy", "publish", "deploy-remote",
    "production-access", "credential-rotation",
}
STOP_CATEGORIES = {"stop", "down", "cleanup"}


def _load_validator():
    import importlib.util

    spec = importlib.util.spec_from_file_location("environment_profile_validator", PROFILE_VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Environment Profile validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _normalise_id(value: str) -> str:
    candidate = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not SAFE_ID.fullmatch(candidate):
        raise ValueError("skill-id-must-use-lowercase-digits-and-hyphens")
    return candidate


def _project_root(profile_path: Path, explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit.resolve()
    resolved = profile_path.resolve()
    # The standard location is <project>/.bruce/environments/<id>.profile.yaml.
    if resolved.parent.name == "environments" and resolved.parent.parent.name == ".bruce":
        return resolved.parent.parent.parent
    raise ValueError("project-root-required-for-nonstandard-profile-path")


def _safe_relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError("generated-skill-path-must-be-inside-project-root") from exc


def _choose_skill_root(project_root: Path, explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit.resolve()
    for relative in (".codex/skills", ".agents/skills", "skills"):
        candidate = project_root / relative
        if candidate.is_dir():
            return candidate
    return project_root / ".codex/skills"


def _assert_confirmed_profile(data: dict[str, Any]) -> None:
    errors = _load_validator().validate_profile(data)
    if errors:
        raise ValueError("invalid-profile: " + "; ".join(errors))
    confirmation = data["confirmation"]
    if data.get("profile_state") != "confirmed" or confirmation.get("state") != "confirmed":
        raise ValueError("Environment Profile must be confirmed before generating an executable Skill")
    if confirmation.get("confirmed_revision") != data.get("profile_revision"):
        raise ValueError("confirmed profile revision does not match")
    if confirmation.get("confirmed_content_hash") != data.get("content_hash"):
        raise ValueError("confirmed profile content hash does not match")


def _operations(data: dict[str, Any]) -> list[dict[str, Any]]:
    raw = data.get("operations", [])
    if not isinstance(raw, list) or not raw:
        raise ValueError("confirmed Environment Profile must declare at least one operation")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, operation in enumerate(raw):
        if not isinstance(operation, dict):
            raise ValueError(f"operations[{index}] must be a mapping")
        operation_id = operation.get("operation_id")
        argv = operation.get("argv")
        if not isinstance(operation_id, str) or not operation_id.strip() or operation_id in seen:
            raise ValueError(f"operations[{index}] has invalid or duplicate operation_id")
        if not isinstance(argv, list) or not argv or not all(isinstance(arg, str) and arg for arg in argv):
            raise ValueError(f"operations[{index}].argv must be a non-empty string list")
        if any(SECRET_ASSIGNMENT.match(arg) for arg in argv):
            raise ValueError(f"operations[{index}].argv contains a secret assignment")
        seen.add(operation_id)
        result.append(operation)
    return result




def _existing_skill_owners(project_root: Path, selected_root: Path, output_dir: Path, operations: list[dict[str, Any]]) -> list[Path]:
    owners: list[Path] = []
    operation_markers = [operation["operation_id"].lower() for operation in operations]
    command_markers = [" ".join(operation["argv"]).lower() for operation in operations]
    roots = [project_root / relative for relative in (".codex/skills", ".agents/skills", "skills")]
    roots.append(selected_root)
    seen: set[Path] = set()
    for root in roots:
        if not root.is_dir():
            continue
        for skill_path in root.glob("*/SKILL.md"):
            resolved = skill_path.resolve()
            if resolved in seen or resolved.is_relative_to(output_dir):
                continue
            seen.add(resolved)
            try:
                body = skill_path.read_text(encoding="utf-8").lower()
            except (OSError, UnicodeError):
                continue
            if any(marker in body for marker in operation_markers + command_markers):
                owners.append(resolved)
    return owners

def _render_skill(
    *,
    profile: dict[str, Any],
    profile_relative: str,
    skill_id: str,
    runner_relative: str,
    operations: list[dict[str, Any]],
) -> str:
    rows = []
    for operation in operations:
        operation_id = operation["operation_id"]
        category = operation.get("category", "operation")
        risk = operation.get("risk", "guarded")
        purpose = str(operation.get("purpose", "按确认的环境操作执行。"))
        rows.append(f"| `{operation_id}` | `{category}` | `{risk}` | {purpose} |")
    table = "\n".join(rows)
    command = f"python3 {runner_relative} --operation <operation-id>"
    return f'''---
name: {skill_id}
description: Execute the confirmed {profile["profile_id"]} environment operations through the generated bounded runner.
---

# {profile["profile_id"]} Environment Operations

<!-- Generated by Bruce environment-operations. Regenerate after the source Profile changes. -->

This project-local Skill is an executable delivery artifact. It uses the generated runner and the
commands declared in the confirmed Environment Profile; it does not infer commands at runtime.

- Source Profile: `{profile_relative}`
- Profile revision: `{profile["profile_revision"]}`
- Profile content hash: `{profile["content_hash"]}`
- Runner: `{runner_relative}`

## Operations

| operation_id | category | risk | purpose |
|---|---|---|---|
{table}

## Usage

Run from the project root:

```bash
{command}
```

The runner performs a binding and local configuration preflight before execution. For `guarded`
operations such as build/start/stop, pass explicit per-invocation confirmation:

```bash
{runner_relative} --operation <operation-id> --confirm
```

`critical` operations additionally require `--authorize-critical` and are never implied by this
Skill. Use `--dry-run` to inspect the selected operation without executing it. The runner loads local
`.env` values as child-process environment input when the confirmed Profile declares `.env`; values
are never printed or stored in this Skill.

## Boundaries

- Only the listed operations and their Profile-declared `argv` may run.
- Start/stop commands are limited by the Profile's ownership declaration; unrelated processes,
  containers, databases, or networks must not be stopped.
- Missing, stale, or hash-mismatched Profile confirmation fails closed.
- Operation output is redacted before it is returned. Runtime evidence belongs in the caller's
  Verification Run/Checkpoint, not in this Skill.
- This Skill does not grant production, remote deployment, database-write, or credential access.
'''


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _render_agent_metadata(skill_id: str) -> str:
    return (
        "interface:\n"
        f"  display_name: \"{skill_id} Operations\"\n"
        "  short_description: \"Run confirmed project environment operations\"\n"
        f"  default_prompt: \"Use ${skill_id} to run a confirmed project environment operation through its bounded runner.\"\n"
    )


def _render_runner(
    *,
    profile_relative: str,
    profile_id: str,
    revision: int,
    content_hash: str,
    profile_file_sha256: str,
) -> str:
    return f'''#!/usr/bin/env python3
"""Generated bounded runner for the {profile_id} Environment Profile."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

PROFILE_RELATIVE = {profile_relative!r}


def find_project_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / PROFILE_RELATIVE).is_file():
            return candidate
    raise ValueError("cannot locate bound Environment Profile from generated runner")


PROJECT_ROOT = find_project_root()
EXPECTED_PROFILE_ID = {profile_id!r}
EXPECTED_REVISION = {revision!r}
EXPECTED_CONTENT_HASH = {content_hash!r}
EXPECTED_PROFILE_FILE_SHA256 = {profile_file_sha256!r}
SECRET_ASSIGNMENT = re.compile(r"(?i)^(?:[A-Z0-9_]*(?:PASSWORD|PASSWD|TOKEN|API_KEY|SECRET)[A-Z0-9_]*)=")
CRITICAL_CATEGORIES = {sorted(CRITICAL_CATEGORIES)!r}


def fail(message: str) -> int:
    print(f"environment operation blocked: {{message}}", file=sys.stderr)
    return 2


def load_profile() -> dict[str, Any]:
    path = PROJECT_ROOT / PROFILE_RELATIVE
    actual_file_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual_file_sha256 != EXPECTED_PROFILE_FILE_SHA256:
        raise ValueError("bound Environment Profile file changed; regenerate this Skill")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("profile is not a mapping")
    confirmation = data.get("confirmation", {{}})
    if (data.get("profile_id"), data.get("profile_revision"), data.get("content_hash")) != (EXPECTED_PROFILE_ID, EXPECTED_REVISION, EXPECTED_CONTENT_HASH):
        raise ValueError("Profile identity, revision, or content hash changed; regenerate this Skill")
    if (data.get("profile_state"), confirmation.get("state"), confirmation.get("confirmed_revision"), confirmation.get("confirmed_content_hash")) != ("confirmed", "confirmed", EXPECTED_REVISION, EXPECTED_CONTENT_HASH):
        raise ValueError("Profile is no longer exactly confirmed")
    return data


def read_dotenv(path: Path, required: list[str]) -> dict[str, str]:
    if not path.exists():
        if required:
            raise ValueError(f"local .env is missing; add values for: {{', '.join(required)}}")
        return {{}}
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise ValueError("local .env must be a regular non-symlink file")
    if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
        raise ValueError("local .env must be owner-only (0600)")
    values: dict[str, str] = {{}}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        if name and value.strip():
            values[name] = value.strip().strip('"').strip("'")
    missing = [name for name in required if name not in values]
    if missing:
        raise ValueError(f"local .env has missing values for: {{', '.join(missing)}}")
    return values


def redact(text: str, env_values: dict[str, str]) -> str:
    result = text
    for value in sorted((v for v in env_values.values() if v), key=len, reverse=True):
        result = result.replace(value, "<redacted>")
    result = re.sub(r"(?i)(bearer\\s+)[^\\s]+", r"\\1<redacted>", result)
    result = re.sub(r"(?i)(password|passwd|token|api[_-]?key|secret)(\\s*[=:]\\s*)[^\\s]+", r"\\1\\2<redacted>", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one confirmed project environment operation")
    parser.add_argument("--operation", required=True)
    parser.add_argument("--confirm", action="store_true")
    parser.add_argument("--authorize-critical", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        profile = load_profile()
        operations = {{item.get("operation_id"): item for item in profile.get("operations", []) if isinstance(item, dict)}}
        operation = operations.get(args.operation)
        if not operation:
            return fail("operation is not declared by the confirmed Profile")
        argv = operation.get("argv")
        if not isinstance(argv, list) or not argv or not all(isinstance(value, str) and value for value in argv):
            return fail("operation argv is invalid")
        if any(SECRET_ASSIGNMENT.match(value) for value in argv):
            return fail("secret assignments in argv are forbidden")
        executor = operation.get("executor", "local-operator")
        if executor not in {"local-operator", "local-process", "local-shell"}:
            return fail("operation executor is not a supported local executor")
        risk = operation.get("risk", "guarded")
        category = operation.get("category", "")
        if risk in {{"guarded", "critical"}} and not args.confirm:
            return fail("guarded or critical operation requires --confirm")
        if risk == "critical" or category in CRITICAL_CATEGORIES:
            if not args.authorize_critical:
                return fail("critical operation requires --authorize-critical")
        env_config = profile.get("local_env", {{}})
        env_values: dict[str, str] = {{}}
        if isinstance(env_config, dict) and env_config.get("path") == ".env":
            env_values = read_dotenv(PROJECT_ROOT / ".env", env_config.get("required_variables", []))
        cwd = PROJECT_ROOT
        working_directory_ref = operation.get("working_directory_ref", "project-root")
        if isinstance(working_directory_ref, str) and working_directory_ref not in {{"", "project-root"}}:
            candidate = (PROJECT_ROOT / working_directory_ref).resolve()
            candidate.relative_to(PROJECT_ROOT.resolve())
            cwd = candidate
        if args.dry_run:
            print(json.dumps({{"operation_id": args.operation, "risk": risk, "category": category, "argv": argv, "cwd": str(cwd)}}, ensure_ascii=False))
            return 0
        result = subprocess.run(argv, cwd=cwd, env={{**os.environ, **env_values}}, capture_output=True, text=True, check=False)
        output = redact((result.stdout or "") + (result.stderr or ""), env_values)
        print(json.dumps({{"operation_id": args.operation, "risk": risk, "exit_code": result.returncode, "output": output}}, ensure_ascii=False))
        return result.returncode
    except (OSError, UnicodeError, ValueError, KeyError) as error:
        return fail(str(error))


if __name__ == "__main__":
    raise SystemExit(main())
'''


def generate(profile_path: Path, project_root: Path | None, skill_root: Path | None, skill_id: str | None, update: bool) -> Path:
    profile_path = profile_path.resolve()
    data = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("profile must be a YAML mapping")
    _assert_confirmed_profile(data)
    root = _project_root(profile_path, project_root)
    if not root.is_dir():
        raise ValueError("project root does not exist")
    operations = _operations(data)
    chosen_root = _choose_skill_root(root, skill_root)
    selected_id = _normalise_id(skill_id or f"{data['profile_id']}-operations")
    output_dir = (chosen_root / selected_id).resolve()
    _safe_relative(output_dir, root)
    owners = _existing_skill_owners(root, chosen_root, output_dir, operations)
    if owners and not update:
        rendered = ", ".join(_safe_relative(path, root) for path in owners)
        raise ValueError(f"existing Skill may already own confirmed operations: {rendered}; review/reuse it or pass --update")
    skill_path = output_dir / "SKILL.md"
    runner_path = output_dir / "scripts/run_operation.py"
    agent_metadata_path = output_dir / "agents/openai.yaml"
    if skill_path.exists() and "Generated by Bruce environment-operations" not in skill_path.read_text(encoding="utf-8"):
        raise ValueError("refusing to overwrite an unowned existing SKILL.md")
    if output_dir.exists() and not update:
        raise ValueError("generated Skill already exists; pass --update only for a Bruce-generated Skill")
    output_dir.mkdir(parents=True, exist_ok=True)
    runner_path.parent.mkdir(parents=True, exist_ok=True)
    agent_metadata_path.parent.mkdir(parents=True, exist_ok=True)
    profile_relative = _safe_relative(profile_path, root)
    runner_relative = _safe_relative(runner_path, root)
    skill_path.write_text(_render_skill(profile=data, profile_relative=profile_relative, skill_id=selected_id, runner_relative=runner_relative, operations=operations), encoding="utf-8")
    runner_path.write_text(_render_runner(profile_relative=profile_relative, profile_id=data["profile_id"], revision=data["profile_revision"], content_hash=data["content_hash"], profile_file_sha256=_file_sha256(profile_path)), encoding="utf-8")
    agent_metadata_path.write_text(_render_agent_metadata(selected_id), encoding="utf-8")
    os.chmod(runner_path, 0o755)
    return output_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an executable project Skill from a confirmed Environment Profile")
    parser.add_argument("profile", type=Path)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--skill-root", type=Path)
    parser.add_argument("--skill-id")
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args()
    try:
        output = generate(args.profile, args.project_root, args.skill_root, args.skill_id, args.update)
    except (OSError, UnicodeError, ValueError, yaml.YAMLError) as error:
        print(f"Environment operation Skill generation failed: {error}", file=sys.stderr)
        return 1
    print(f"Executable environment operation Skill generated: {output}")
    print("No operation was executed. Use the generated SKILL.md for explicit per-invocation execution.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
