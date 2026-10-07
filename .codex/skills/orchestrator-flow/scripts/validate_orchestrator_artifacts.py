#!/usr/bin/env python3
"""Validate v2 artifacts and derive a read-only resume action."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from workflow_artifacts import ValidationError, require, validate_shape, validate_wrapper, work_scope
from workflow_protocol import replay, resume_action


def read_json(path):
    return json.loads(sys.stdin.read() if str(path) == "-" else Path(path).read_text(encoding="utf-8-sig"))


def validate_workspace(state, workspace):
    """Inspect content mechanically, returning diagnostics rather than bodies/patches."""
    from checkpoint_state import git, workflow_checkpoints
    from read_spec_body import check_document, check_task_completion, numbered_tasks, progress_basis
    checkpoints = {c["commit"]: c for c in workflow_checkpoints(workspace, state.log)}
    branch = state.log["branch_context"]
    remote = git(workspace, "ls-remote", "--exit-code", branch["remote"], "refs/heads/" + branch["feature_branch"], check=False)
    tip = remote.stdout.split()[0] if remote.returncode == 0 and remote.stdout.strip() else None
    for entry in state.entries.values():
        wrapper = entry.get("spec_change_wrapper", entry.get("change_wrapper"))
        if not wrapper or wrapper["checkpoint_commit"] is None:
            continue
        commit = wrapper["checkpoint_commit"]
        checkpoint = checkpoints.get(commit)
        require(checkpoint and checkpoint["checkpoint_kind"] == "artifacts" and checkpoint["publishing_role"] == entry["actor"],
                "Handoff must identify an actual checkpoint published by its producer")
        if wrapper["artifact_changes"] or wrapper.get("research_updates"):
            require(checkpoint["invocation"]["trigger_event_id"] == wrapper["context"]["trigger_event_id"] and
                    checkpoint["invocation"]["attempt"] == wrapper["context"]["attempt"], "Changed artifacts belong to another invocation")
        require(tip and git(workspace, "merge-base", "--is-ancestor", commit, tip, check=False).returncode == 0,
                "Artifact handoff checkpoint has not been established as published")
        for name, artifact in wrapper["artifacts"].items():
            if artifact:
                content = git(workspace, "show", commit + ":" + artifact["ref"]).stdout
                require(content.splitlines()[1:2] == [f"Content version: {artifact['version']}"], "Artifact checkpoint version differs from handoff")
        if "implementation_phases" in wrapper and wrapper["implementation_phases"]:
            tasks = git(workspace, "show", commit + ":" + state.log["tasks_ref"]).stdout
            planned = [t for p in wrapper["implementation_phases"] for t in p["task_ids"]]
            require(planned == list(numbered_tasks(tasks)), "Phases must partition every actual task in execution order")
        for change in wrapper["artifact_changes"]:
            if change["change_kind"] == "progress":
                producers = [prior["spec_change_wrapper"] for prior in state.entries.values() if
                             int(prior["id"]) < int(entry["id"]) and "spec_change_wrapper" in prior and
                             any(c["artifact"] == "tasks" and c["change_kind"] != "progress" for c in prior["spec_change_wrapper"]["artifact_changes"])]
                producer = producers[-1]
                approved = git(workspace, "show", producer["checkpoint_commit"] + ":" + state.log["tasks_ref"]).stdout
                current = git(workspace, "show", commit + ":" + state.log["tasks_ref"]).stdout
                require(progress_basis(approved) == progress_basis(current), "Progress concealed a task-content or Revision History change")
    for artifact in state.artifacts.values():
        if artifact:
            check_document(workspace / artifact["ref"], artifact["version"])
    # Even between Coder checkpoints/returns, compare the working tasks to the
    # latest Planner content, not to Coder's reported completion ordering.
    if state.artifacts["tasks"]:
        producing = state.entries[state.produced["tasks"]]["spec_change_wrapper"]
        approved = git(workspace, "show", producing["checkpoint_commit"] + ":" + state.log["tasks_ref"]).stdout
        current = (workspace / state.log["tasks_ref"]).read_text(encoding="utf-8-sig")
        require(progress_basis(approved) == progress_basis(current), "Current tasks contain unrecorded content changes")
    for stage, output_id in state.outputs.items():
        if stage == "spec":
            continue
        entry = state.entries[output_id]
        if entry["event"] not in {"coding-complete", "coding-phase-complete"}:
            continue
        wrapper = entry["change_wrapper"]
        scope = work_scope(wrapper)
        task_ids = next(p["task_ids"] for p in state.phases if p["id"] == scope["phase_id"]) if scope["kind"] == "phase" else None
        path = workspace / state.log["tasks_ref"]
        completed = git(workspace, "show", wrapper["checkpoint_commit"] + ":" + state.log["tasks_ref"]).stdout
        check_task_completion(path, wrapper["task_progress"], task_ids, text=completed)
        # Historical completion describes its own published task basis. New
        # drafting/repair work need not be complete before its next handoff.
        at_handoff = state.status in {"coding_complete", "code_in_review", "code_changes_requested",
                                      "code_conditionally_approved", "code_approved", "implementation_complete"}
        at_phase_handoff = state.status == "coding_in_progress" and state.inflight is None
        if (at_handoff or at_phase_handoff) and scope == state.current_scope and wrapper["artifacts"] == state.artifacts:
            check_task_completion(path, wrapper["task_progress"], task_ids)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=("task-log", "repository-config", "spec-change-wrapper", "spec-review-wrapper", "change-wrapper", "review-wrapper", "resume-action"))
    parser.add_argument("path", help="JSON file, or - for the actual JSON return on stdin")
    parser.add_argument("--previous", type=Path, help="Validate append-only history against the preceding log")
    parser.add_argument("--workspace", type=Path, help="Also check current spec versions/history and consolidated task completion")
    parser.add_argument("--observations", help="Read-only delivery/invocation observations; file or - for stdin")
    args = parser.parse_args(argv)
    try:
        require(not (args.path == "-" and args.observations == "-"), "Cannot consume stdin twice")
        require(str(args.previous) != "-", "--previous must identify the authoritative log file")
        value = read_json(args.path)
        if args.kind in {"task-log", "resume-action"}:
            previous = read_json(args.previous) if args.previous else None
            state = replay(value, previous=previous)
            if args.workspace:
                validate_workspace(state, args.workspace)
            if args.kind == "resume-action":
                observations = read_json(args.observations) if args.observations else None
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
