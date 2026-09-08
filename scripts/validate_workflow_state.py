#!/usr/bin/env python3
"""Validate a Bruce unified workflow-state YAML snapshot."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import yaml

from workflow_state import WorkflowStateError, validate_document, validate_verification_run


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--verification-run", type=Path, default=None)
    args = parser.parse_args()
    try:
        data = yaml.safe_load(args.snapshot.read_text(encoding="utf-8"))
        state = validate_document(data)
        if args.verification_run is not None:
            run = yaml.safe_load(args.verification_run.read_text(encoding="utf-8"))
            checkpoint_id = data.get("checkpoint_id") if isinstance(data, dict) else None
            validate_verification_run(run, state, checkpoint_id=checkpoint_id)
    except (OSError, yaml.YAMLError, WorkflowStateError) as exc:
        print(f"Workflow state validation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Workflow state validation passed: {args.snapshot}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
