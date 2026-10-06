#!/usr/bin/env python3
"""Validate v2 artifacts and derive a read-only resume action."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from workflow_artifacts import ValidationError, validate_shape, validate_wrapper
from workflow_protocol import replay, resume_action


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=("task-log", "repository-config", "spec-change-wrapper", "spec-review-wrapper", "change-wrapper", "review-wrapper", "resume-action"))
    parser.add_argument("path", type=Path)
    parser.add_argument("--previous", type=Path, help="Validate append-only history against the preceding log")
    parser.add_argument("--workspace", type=Path, help="Also check current spec versions/history and consolidated task completion")
    parser.add_argument("--observations", type=Path, help="Read-only delivery/invocation observations for resume-action")
    args = parser.parse_args(argv)
    try:
        value = json.loads(args.path.read_text(encoding="utf-8-sig"))
        if args.kind in {"task-log", "resume-action"}:
            previous = json.loads(args.previous.read_text(encoding="utf-8-sig")) if args.previous else None
            state = replay(value, previous=previous)
            if args.workspace:
                from read_spec_body import check_document, check_task_completion
                for artifact in state.artifacts.values():
                    if artifact:
                        check_document(args.workspace / artifact["ref"], artifact["version"])
                if state.status in {"coding_complete", "code_in_review", "code_changes_requested", "code_conditionally_approved", "code_approved", "implementation_complete"}:
                    wrapper = state.entries[state.outputs["code"]]["change_wrapper"]
                    check_task_completion(args.workspace / value["tasks_ref"], wrapper["task_progress"])
            if args.kind == "resume-action":
                observations = json.loads(args.observations.read_text(encoding="utf-8-sig")) if args.observations else None
                print(json.dumps(resume_action(value, observations), indent=2))
                return 0
        elif args.kind == "repository-config":
            validate_shape(args.kind, value)
        else:
            validate_wrapper(args.kind, value)
        print(f"VALID: {args.kind} -> {args.path}")
        return 0
    except (ValidationError, ValueError, OSError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
