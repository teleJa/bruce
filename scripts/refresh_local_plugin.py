#!/usr/bin/env python3
"""Refresh the local Bruce Codex plugin without breaking a running session.

Codex keeps an installed hook's absolute PLUGIN_ROOT for the lifetime of the
current session. When a cachebuster update removes the old cache directory,
that session can briefly call a path that no longer exists. This wrapper keeps
old cache roots usable by adding a symlink or hook-file compatibility alias
after installing the new cache.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_CODEX_HOME = Path.home() / ".codex"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "plugin_path",
        nargs="?",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Bruce plugin root (defaults to this repository)",
    )
    parser.add_argument(
        "--cachebuster",
        help="Optional cachebuster token passed to update_plugin_cachebuster.py",
    )
    return parser.parse_args()


def run(command: list[str], *, cwd: Path | None = None) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = result.stdout.strip()
    if output:
        print(output)
    return output


def version_from_manifest(plugin_root: Path) -> str:
    manifest = json.loads(
        (plugin_root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    version = manifest.get("version")
    if not isinstance(version, str) or not version:
        raise ValueError("plugin manifest version must be a non-empty string")
    return version


def cache_entries(cache_root: Path) -> dict[str, Path]:
    if not cache_root.is_dir():
        return {}
    return {
        entry.name: entry
        for entry in cache_root.iterdir()
        if entry.name != ".DS_Store" and (entry.is_dir() or entry.is_symlink())
    }


def ensure_compatibility_aliases(
    previous: dict[str, Path],
    cache_root: Path,
    new_cache: Path,
) -> list[str]:
    repaired: list[str] = []
    for version, old_cache in previous.items():
        if version == new_cache.name:
            continue

        hook = old_cache / "hooks" / "post_tool_review_reminder.py"
        if hook.is_file():
            continue

        if not os.path.lexists(old_cache):
            old_cache.symlink_to(new_cache, target_is_directory=True)
            repaired.append(f"cache alias: {old_cache} -> {new_cache}")
            continue

        hooks_dir = old_cache / "hooks"
        if hooks_dir.is_dir() and not os.path.lexists(hook):
            hook.symlink_to(new_cache / "hooks" / "post_tool_review_reminder.py")
            repaired.append(f"hook alias: {hook} -> {new_cache / 'hooks' / 'post_tool_review_reminder.py'}")

    return repaired


def main() -> int:
    args = parse_args()
    plugin_root = args.plugin_path.expanduser().resolve()
    codex_home = Path(os.environ.get("CODEX_HOME", DEFAULT_CODEX_HOME)).expanduser()
    cache_root = codex_home / "plugins" / "cache" / "bruce" / "bruce"
    helper = codex_home / "skills" / ".system" / "plugin-creator" / "scripts" / "update_plugin_cachebuster.py"
    codex = shutil.which("codex")

    if not helper.is_file():
        raise FileNotFoundError(f"cachebuster helper not found: {helper}")
    if not codex:
        raise FileNotFoundError("codex executable not found on PATH")

    previous = cache_entries(cache_root)
    command = [sys.executable, str(helper), str(plugin_root)]
    if args.cachebuster:
        command.extend(["--cachebuster", args.cachebuster])
    run(command)

    run([codex, "plugin", "marketplace", "add", str(plugin_root)])
    run([codex, "plugin", "add", "bruce@bruce", "--json"])

    version = version_from_manifest(plugin_root)
    new_cache = cache_root / version
    if not new_cache.is_dir():
        raise FileNotFoundError(f"new Bruce cache not found: {new_cache}")

    for message in ensure_compatibility_aliases(previous, cache_root, new_cache):
        print(message)
    print(f"Bruce local plugin refreshed: {version}")
    print("Open a new Codex session to load the new plugin version.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(exc.stdout or str(exc), file=sys.stderr)
        raise SystemExit(exc.returncode) from exc
