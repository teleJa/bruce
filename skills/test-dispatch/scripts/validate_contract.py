#!/usr/bin/env python3
"""CLI validator for Bruce Scenario, Dispatch, and Track Result YAML contracts."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import yaml

from contracts import validate_dispatch, validate_scenario, validate_track_results


VALIDATORS = {
    "scenario": validate_scenario,
    "dispatch": validate_dispatch,
    "track-result": validate_track_results,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=sorted(VALIDATORS))
    parser.add_argument("document", type=Path)
    args = parser.parse_args()
    try:
        data = yaml.safe_load(args.document.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        print(f"Contract validation failed: {error}", file=sys.stderr)
        return 1
    errors = VALIDATORS[args.kind](data)
    if errors:
        print("Contract validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Contract validation passed: {args.document}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
