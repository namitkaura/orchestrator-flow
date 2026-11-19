#!/usr/bin/env python3
"""Validate v2 artifacts, derive resume actions, or explicitly record a verified handoff."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import argparse
import json
from pathlib import Path
import sys

from workflow_artifacts import ValidationError, require, validate_shape, validate_wrapper, work_scope, json_values_equal
from workflow_protocol import replay, resume_action, WRAPPERS


def read_json(path):
    return json.loads((sys.stdin.buffer.read() if str(path) == "-" else Path(path).read_bytes()).decode("utf-8-sig"))


def validate_workspace(state, workspace):
    """Inspect content mechanically, returning diagnostics rather than bodies/patches."""
    from checkpoint_state import git, workflow_checkpoints, artifact_checkpoint_ref as checkpoint_ref
    from read_spec_body import check_document, check_task_completion, numbered_tasks, progress_basis
    locations = {}
    def artifact_checkpoint_ref(repo, log, commit, name):
        key = (commit, name)
        if key not in locations:
            locations[key] = checkpoint_ref(repo, log, commit, name)
        return locations[key]
    checkpoints = {c["commit"]: c for c in workflow_checkpoints(workspace, state.log, allow_pending=True)}
    validate_relocations(state, workspace, checkpoints)
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
        if entry["actor"] == "Coder" or wrapper.get("artifact_changes") or wrapper.get("research_updates"):
            require(checkpoint["invocation"]["trigger_event_id"] == wrapper["context"]["trigger_event_id"] and
                    checkpoint["invocation"]["attempt"] <= wrapper["context"]["attempt"], "Changed artifacts belong to another invocation")
        if checkpoint["invocation"]["trigger_event_id"] == wrapper["context"]["trigger_event_id"]:
            start = state.entries[wrapper["context"]["trigger_event_id"]]
            require(checkpoint["phase_id"] == work_scope(start["details"]).get("phase_id"), "Artifact belongs to another assignment phase")
        require(tip and git(workspace, "merge-base", "--is-ancestor", commit, tip, check=False).returncode == 0,
                "Artifact handoff checkpoint has not been established as published")
        for name, artifact in wrapper["artifacts"].items():
            if artifact:
                content = git(workspace, "show", commit + ":" + artifact_checkpoint_ref(workspace, state.log, commit, name)).stdout
                require(content.splitlines()[1:2] == [f"Content version: {artifact['version']}"], "Artifact checkpoint version differs from handoff")
        if "implementation_phases" in wrapper and wrapper["implementation_phases"]:
            tasks = git(workspace, "show", commit + ":" + artifact_checkpoint_ref(workspace, state.log, commit, "tasks")).stdout
            planned = [t for p in wrapper["implementation_phases"] for t in p["task_ids"]]
            require(planned == list(numbered_tasks(tasks)), "Phases must partition every actual task in execution order")
        for change in wrapper.get("artifact_changes", []):
            if change["change_kind"] == "progress":
                producers = [prior["spec_change_wrapper"] for prior in state.entries.values() if
                             int(prior["id"]) < int(entry["id"]) and "spec_change_wrapper" in prior and
                             any(c["artifact"] == "tasks" and c["change_kind"] != "progress" for c in prior["spec_change_wrapper"].get("artifact_changes", []))]
                producer = producers[-1]
                approved = git(workspace, "show", producer["checkpoint_commit"] + ":" + artifact_checkpoint_ref(workspace, state.log, producer["checkpoint_commit"], "tasks")).stdout
                current = git(workspace, "show", commit + ":" + artifact_checkpoint_ref(workspace, state.log, commit, "tasks")).stdout
                require(progress_basis(approved) == progress_basis(current), "Progress concealed a task-content or Revision History change")
    for artifact in state.artifacts.values():
        if artifact:
            check_document(contained_path(workspace, artifact["ref"]), artifact["version"])
    # Even between Coder checkpoints/returns, compare the working tasks to the
    # latest Planner content, not to Coder's reported completion ordering.
    if state.artifacts["tasks"]:
        producing = state.entries[state.produced["tasks"]]["spec_change_wrapper"]
        approved = git(workspace, "show", producing["checkpoint_commit"] + ":" + artifact_checkpoint_ref(workspace, state.log, producing["checkpoint_commit"], "tasks")).stdout
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
        completed = git(workspace, "show", wrapper["checkpoint_commit"] + ":" + artifact_checkpoint_ref(workspace, state.log, wrapper["checkpoint_commit"], "tasks")).stdout
        check_task_completion(path, wrapper["task_progress"], task_ids, text=completed)
        # Historical completion describes its own published task basis. New
        # drafting/repair work need not be complete before its next handoff.
        at_handoff = state.status in {"coding_complete", "code_in_review", "code_changes_requested",
                                      "code_approved", "implementation_complete"}
        at_phase_handoff = state.status == "coding_in_progress" and state.inflight is None
        if (at_handoff or at_phase_handoff) and scope == state.current_scope and state.same_artifacts(wrapper["artifacts"], state.artifacts):
            check_task_completion(path, wrapper["task_progress"], task_ids)


def contained_path(workspace, ref):
    from workflow_protocol import relative_path
    relative_path(ref)
    path = Path(workspace) / ref
    require(path.resolve().is_relative_to(Path(workspace).resolve()), "Relocation path escapes workspace through a symlink")
    return path


def validate_relocations(state, workspace, checkpoints):
    """Verify each authorized move against immutable Git blobs, including pending work."""
    from checkpoint_state import git
    for entry in state.entries.values():
        if entry["event"] != "feature-relocated":
            continue
        details = entry["details"]
        covering = [c for c in checkpoints.values() if entry["id"] in c["event_ids"]]
        require(len(covering) <= 1, "Relocation has duplicated checkpoints")
        checkpoint = covering[0] if covering else None
        if checkpoint:
            require(checkpoint["first"] == checkpoint["last"] == int(entry["id"]),
                    "Relocation requires its own single-event log checkpoint")
        before = checkpoint["commit"] + "^" if checkpoint else "HEAD"
        after = checkpoint["commit"] if checkpoint else None
        old, new = details["from_dir"], details["to_dir"]
        files = git(workspace, "ls-tree", "-r", "--name-only", before, "--", old).stdout.splitlines()
        require(old + "/task_log.json" in files, "Relocation source has no tracked authoritative log")
        pairs = [(ref, new + ref[len(old):]) for ref in files]
        pairs += [(m["from"], m["to"]) for m in details["input_moves"]]
        require(len({p for pair in pairs for p in pair}) == 2 * len(pairs), "Relocation paths overlap")
        expected_changes = set()
        for source, target in pairs:
            expected_changes.update((source, target))
            for ref in (source, target):
                contained_path(workspace, ref)
            mode = git(workspace, "ls-tree", before, "--", source).stdout.split()
            require(mode and mode[0] in {"100644", "100755"}, "Relocation source must be a tracked regular file")
            require(git(workspace, "cat-file", "-e", before + ":" + target, check=False).returncode != 0,
                    "Relocation destination already exists in its baseline")
            if after:
                require(git(workspace, "cat-file", "-e", after + ":" + source, check=False).returncode != 0,
                        "Relocation left a duplicate source")
                actual = git(workspace, "ls-tree", after, "--", target).stdout.split()
                require(actual and actual[0] == mode[0], "Relocation must preserve regular-file mode")
                digest = actual[2]
            else:
                require(not contained_path(workspace, source).exists(), "Relocation left a duplicate source")
                require(contained_path(workspace, target).is_file(), "Relocation destination is missing")
                digest = git(workspace, "hash-object", "--path=" + source, "--", target).stdout.strip()
            if source != old + "/task_log.json":
                require(digest == mode[2], "Relocation must preserve file bytes without content/version changes")
        if after:
            changed = set(git(workspace, "diff-tree", "--no-renames", "--no-commit-id", "--name-only", "-r", after).stdout.splitlines())
            require(changed == expected_changes, "Relocation checkpoint contains unlisted changes")
        else:
            # A nonempty pre-existing destination must never be silently merged.
            actual_files = {p.relative_to(Path(workspace)).as_posix() for p in contained_path(workspace, new).rglob("*") if p.is_file()}
            require(actual_files == {target for _, target in pairs if target.startswith(new + "/")},
                    "Relocation destination contains unlisted files")


class HandoffError(ValidationError):
    def __init__(self, category, message):
        self.category = category
        super().__init__(f"{category}: {message}")


def prepare_handoff(previous, native_return):
    """Embed one actual return and derive its metadata; never write or dispatch."""
    state = replay(previous)
    role = {"spec_in_progress": "Planner", "spec_in_review": "Architect",
            "coding_in_progress": "Coder", "blocked": "Coder", "code_in_review": "Reviewer"}.get(state.status)
    if role not in state.starts:
        raise HandoffError("recording_error", "No active assignment expects a handoff")
    key = {"Planner": "spec_change_wrapper", "Architect": "spec_review_wrapper",
           "Coder": "change_wrapper", "Reviewer": "review_wrapper"}[role]
    try:
        original = json.loads(native_return) if isinstance(native_return, str) else deepcopy(native_return)
        validate_wrapper(key.replace("_", "-"), original)
        state.context(original["context"], role)
        event = {"Planner": "spec-updated", "Architect": "spec-reviewed",
                 "Coder": "coding-phase-complete" if work_scope(original)["kind"] == "phase" else "coding-complete",
                 "Reviewer": "code-reviewed"}[role]
        trigger = state.entries[state.starts[role]["trigger_event_id"]]
        entry = {"id": str(len(previous["history"]) + 1),
                 "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "actor": role, "requestor": trigger["requestor"], "event": event, key: original}
        state.append(entry, derive_status=True)
        candidate = deepcopy(previous)
        candidate["history"].append(entry)
        candidate["status"] = state.status
        replay(candidate, previous=previous)
    except (ValidationError, ValueError, TypeError, KeyError) as exc:
        raise HandoffError("invalid_native_output", str(exc)) from exc
    return candidate


def record_handoff(path, native_return, workspace=None):
    """Write only the authoritative log after validating the actual return once."""
    path = Path(path)
    before = path.read_bytes()
    previous = json.loads(before.decode("utf-8-sig"))
    candidate = prepare_handoff(previous, native_return)
    if workspace:
        try:
            validate_workspace(replay(candidate), Path(workspace))
        except ValidationError as exc:
            raise HandoffError("invalid_native_output", str(exc)) from exc
    encoded = (json.dumps(candidate, ensure_ascii=True, indent=2) + "\n").encode("utf-8")
    try:
        require(path.read_bytes() == before, "Authoritative log changed while preparing handoff")
        path.write_bytes(encoded)
        written = json.loads(path.read_bytes().decode("utf-8-sig"))
        require(json_values_equal(written, candidate), "Written log differs from the validated candidate")
        require(json_values_equal(written["history"][:-1], previous["history"]), "Written historical prefix changed")
    except (ValidationError, ValueError, OSError) as exc:
        raise HandoffError("recording_error", f"Do not publish: {exc}") from exc
    return candidate


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=("task-log", "repository-config", "spec-change-wrapper", "spec-review-wrapper", "change-wrapper", "review-wrapper", "resume-action", "record-handoff"))
    parser.add_argument("path", help="JSON file, or - for the actual JSON return on stdin")
    parser.add_argument("--previous", type=Path, help="Validate append-only history against the preceding log")
    parser.add_argument("--workspace", type=Path, help="Also check current spec versions/history and consolidated task completion")
    parser.add_argument("--observations", help="Read-only delivery/invocation observations; file or - for stdin")
    parser.add_argument("--log", type=Path, help="Authoritative log to write; record-handoff only")
    args = parser.parse_args(argv)
    try:
        require(not (args.path == "-" and args.observations == "-"), "Cannot consume stdin twice")
        require(str(args.previous) != "-", "--previous must identify the authoritative log file")
        require((args.log is not None) == (args.kind == "record-handoff"), "--log is required only for record-handoff")
        require(args.kind != "record-handoff" or not (args.previous or args.observations), "record-handoff reads its previous log directly")
        value = read_json(args.path)
        if args.kind == "record-handoff":
            record_handoff(args.log, value, args.workspace)
            print("RECORDED: verified native handoff; checkpoint delivery is still required")
            return 0
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
        print(f"INVALID: {exc}".encode("ascii", "backslashreplace").decode("ascii"), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
