#!/usr/bin/env python3
"""Check a project-local .env without exposing any stored values."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path
from typing import Iterable

ENV_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _git_check(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def _is_git_repository(root: Path) -> bool:
    result = _git_check(root, "rev-parse", "--is-inside-work-tree")
    return result.returncode == 0 and result.stdout.strip() == "true"


def _is_tracked(root: Path) -> bool:
    return _git_check(root, "ls-files", "--error-unmatch", "--", ".env").returncode == 0


def _is_ignored(root: Path) -> bool:
    return _git_check(root, "check-ignore", "--quiet", "--", ".env").returncode == 0


def _read_present_names(lines: Iterable[str]) -> set[str]:
    present: set[str] = set()
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        if ENV_NAME_PATTERN.fullmatch(name) and value.strip():
            present.add(name)
    return present


def inspect_local_env(root: Path, required: list[str]) -> tuple[dict[str, object], int]:
    root = root.resolve()
    env_path = root / ".env"
    invalid_required = sorted({name for name in required if not ENV_NAME_PATTERN.fullmatch(name)})
    if invalid_required:
        return {
            "project_root": str(root),
            "env_path": str(env_path),
            "usable": False,
            "error": "invalid-required-variable-name",
            "invalid_required": invalid_required,
        }, 4

    git_repository = _is_git_repository(root)
    env_lstat = os.lstat(env_path) if os.path.lexists(env_path) else None
    exists = env_lstat is not None
    symlink = stat.S_ISLNK(env_lstat.st_mode) if env_lstat is not None else False
    env_mode = env_lstat.st_mode if env_lstat is not None else None
    regular_file = env_mode is not None and stat.S_ISREG(env_mode) and not symlink
    tracked = _is_tracked(root) if git_repository else False
    ignored = _is_ignored(root) if git_repository else None
    permissions = None
    owner_only = False
    owner_is_current_user = False
    present: set[str] = set()
    read_error = None

    if regular_file:
        fd = -1
        try:
            flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
            fd = os.open(env_path, flags)
            opened_stat = os.fstat(fd)
            if not stat.S_ISREG(opened_stat.st_mode):
                read_error = "non-regular-env-file"
            else:
                permissions = stat.S_IMODE(opened_stat.st_mode)
                owner_only = permissions & 0o077 == 0
                owner_is_current_user = opened_stat.st_uid == os.getuid()
                with os.fdopen(fd, "r", encoding="utf-8") as stream:
                    fd = -1
                    present = _read_present_names(stream)
            if fd >= 0:
                os.close(fd)
        except (OSError, UnicodeError):
            if fd >= 0:
                os.close(fd)
            read_error = "unsafe-or-unreadable-env-file"

    missing_required = sorted(set(required) - present)
    safe_vcs_state = not tracked and (ignored is True if git_repository else True)
    usable = (
        exists
        and regular_file
        and read_error is None
        and owner_only
        and owner_is_current_user
        and safe_vcs_state
        and not missing_required
    )

    result: dict[str, object] = {
        "project_root": str(root),
        "env_path": str(env_path),
        "exists": exists,
        "regular_file": regular_file,
        "symlink": symlink,
        "git_repository": git_repository,
        "tracked": tracked,
        "ignored": ignored,
        "owner_only_permissions": owner_only,
        "owner_is_current_user": owner_is_current_user,
        "permissions": f"{permissions:04o}" if permissions is not None else None,
        "required_names": sorted(set(required)),
        "missing_required_names": missing_required,
        "usable": usable,
    }
    if symlink:
        result["error"] = "symlink-env-file"
    elif read_error:
        result["error"] = read_error

    if usable:
        return result, 0
    if not exists:
        return result, 2
    if symlink or not regular_file or read_error or tracked or not safe_vcs_state or not owner_only or not owner_is_current_user:
        return result, 3
    if missing_required:
        return result, 2
    return result, 3


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check a project-local .env and report metadata only; never print values."
    )
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--required", action="append", default=[])
    args = parser.parse_args()

    if not args.project_root.is_dir():
        print(json.dumps({"usable": False, "error": "project-root-not-found"}, sort_keys=True))
        return 4

    result, exit_code = inspect_local_env(args.project_root, args.required)
    print(json.dumps(result, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
