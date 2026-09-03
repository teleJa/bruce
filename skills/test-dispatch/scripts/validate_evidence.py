#!/usr/bin/env python3
"""Validate Track Result evidence against a current Scenario/Profile/run context."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import yaml

from contracts import validate_track_results_for_context


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("track_result", type=Path)
    parser.add_argument("context", type=Path)
    args = parser.parse_args()
    try:
        result = yaml.safe_load(args.track_result.read_text(encoding="utf-8"))
        context = yaml.safe_load(args.context.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        print(f"Evidence validation failed: {error}", file=sys.stderr)
        return 1
    errors = validate_track_results_for_context(result, context)
    if errors:
        print("Evidence validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Evidence validation passed: {args.track_result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
