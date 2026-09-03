#!/usr/bin/env python3
"""Aggregate a validated Track Result YAML document without executing tests."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import yaml

from contracts import ContractValidationError, aggregate_track_results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        data = yaml.safe_load(args.document.read_text(encoding="utf-8"))
        result = aggregate_track_results(data)
    except (OSError, yaml.YAMLError, ContractValidationError, TypeError) as error:
        print(f"Track result aggregation failed: {error}", file=sys.stderr)
        return 1
    rendered = yaml.safe_dump(result, sort_keys=False, allow_unicode=True)
    if args.output:
        try:
            args.output.write_text(rendered, encoding="utf-8")
        except OSError as error:
            print(f"Track result aggregation failed: {error}", file=sys.stderr)
            return 1
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
