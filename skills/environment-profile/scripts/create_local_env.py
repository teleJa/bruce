#!/usr/bin/env python3
"""Create or complete a project-local .env without printing submitted values."""

from __future__ import annotations

import argparse
import getpass
import os
import re
import stat
import subprocess
import tempfile
from pathlib import Path

ENV_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _git_check(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False
    )


def _is_git_repository(root: Path) -> bool:
    result = _git_check(root, "rev-parse", "--is-inside-work-tree")
    return result.returncode == 0 and result.stdout.strip() == "true"


def _is_tracked(root: Path) -> bool:
    return _git_check(root, "ls-files", "--error-unmatch", "--", ".env").returncode == 0


def _ensure_ignored(root: Path) -> None:
    gitignore = root / ".gitignore"
    lines = gitignore.read_text(encoding="utf-8").splitlines() if gitignore.exists() else []
    required_entries = [".env", ".bruce-env-*"]
    missing_entries = [entry for entry in required_entries if entry not in lines]
    if missing_entries:
        if lines and lines[-1] != "":
            lines.append("")
        if ".env" not in lines:
            lines.append("# Local credentials for Environment Profiles")
        lines.extend(entry for entry in missing_entries if entry not in lines)
        gitignore.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if _is_git_repository(root) and _git_check(root, "check-ignore", "--quiet", "--", ".env").returncode != 0:
        raise RuntimeError(".env-is-not-ignored")


def _read_existing_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    try:
        opened_stat = os.fstat(fd)
        if not stat.S_ISREG(opened_stat.st_mode):
            raise RuntimeError("non-regular-env-file")
        if stat.S_IMODE(opened_stat.st_mode) & 0o077:
            raise RuntimeError("env-file-permissions-too-open")
        if opened_stat.st_uid != os.getuid():
            raise RuntimeError("env-file-owner-mismatch")
        with os.fdopen(fd, "r", encoding="utf-8") as stream:
            fd = -1
            return stream.read().splitlines(keepends=True)
    finally:
        if fd >= 0:
            os.close(fd)


def _write_values(root: Path, values: dict[str, str]) -> Path:
    root = root.resolve()
    env_path = root / ".env"
    if not root.is_dir():
        raise RuntimeError("project-root-not-found")
    if _is_git_repository(root) and _is_tracked(root):
        raise RuntimeError("tracked-env-file")
    _ensure_ignored(root)

    if os.path.lexists(env_path):
        info = env_path.lstat()
        if stat.S_ISLNK(info.st_mode):
            raise RuntimeError("symlink-env-file")
        if not stat.S_ISREG(info.st_mode):
            raise RuntimeError("non-regular-env-file")

    lines = _read_existing_lines(env_path)
    replacements: dict[str, str] = {}
    seen: set[str] = set()
    for index, raw_line in enumerate(lines):
        line = raw_line.rstrip("\r\n")
        prefix = "export " if line.startswith("export ") else ""
        candidate = line[len(prefix) :]
        if "=" not in candidate:
            continue
        name = candidate.split("=", 1)[0].strip()
        if name in values:
            replacements[name] = f"{prefix}{name}={values[name]}\n"
            seen.add(name)
            lines[index] = replacements[name]
    for name, value in values.items():
        if name not in seen:
            lines.append(f"{name}={value}\n")

    fd, temp_name = tempfile.mkstemp(prefix=".bruce-env-", dir=root, text=True)
    temp_path = Path(temp_name)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.writelines(lines)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, env_path)
        os.chmod(env_path, 0o600)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise
    return env_path


def create_local_env(root: Path, required: list[str], provided: dict[str, str] | None = None) -> Path:
    names = sorted(set(required))
    invalid = [name for name in names if not ENV_NAME_PATTERN.fullmatch(name)]
    if invalid:
        raise ValueError("invalid-required-variable-name")
    values = dict(provided or {})
    for name in names:
        if name not in values:
            values[name] = getpass.getpass(f"Enter value for {name}: ")
        if not values[name].strip():
            raise ValueError(f"empty-value:{name}")
        if any(character in values[name] for character in ("\x00", "\r", "\n")):
            raise ValueError(f"invalid-value:{name}")
    return _write_values(root, values)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create or complete a project-local .env using hidden prompts; never print values."
    )
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--required", action="append", required=True)
    args = parser.parse_args()
    try:
        create_local_env(args.project_root, args.required)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Environment file creation failed: {error}")
        return 1
    print("Environment file created or updated; values were not displayed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
