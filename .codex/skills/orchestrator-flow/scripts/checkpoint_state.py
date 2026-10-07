"""Checkpoint inspection and local attempt evidence; never commits, pushes, or retries."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import uuid

from workflow_artifacts import ValidationError, require


def git(repo, *args, check=True):
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8")
    if check and result.returncode:
        raise ValidationError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result


def journal_path(repo, feature):
    require(re.fullmatch(r"[a-z0-9]+(?:[.-][a-z0-9]+)*", feature), "Invalid feature identity")
    value = git(repo, "rev-parse", "--git-path", f"orchestrator-flow/{feature}/checkpoint-attempts.jsonl").stdout.strip()
    path = Path(value)
    return path if path.is_absolute() else Path(repo) / path


def read_attempts(repo, feature):
    path = journal_path(repo, feature)
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line] if path.exists() else []


def append_attempt(repo, feature, record):
    path = journal_path(repo, feature)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as output:
        output.write(json.dumps(record) + "\n")
        output.flush()
        os.fsync(output.fileno())


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def event_commits(repo, log_ref):
    """Return checkpoint ranges, oldest first. Correspondence lives in commit trailers."""
    raw = git(repo, "log", "--reverse", "--format=%H%x00%B%x00").stdout.split("\0")
    checkpoints = []
    for offset in range(0, len(raw) - 1, 2):
        commit, body = raw[offset].strip(), raw[offset + 1]
        logs = re.findall(r"^Orchestrator-Log: (.+)$", body, re.M)
        ranges = re.findall(r"^Orchestrator-Events: ([1-9]\d*)-([1-9]\d*)$", body, re.M)
        if log_ref in logs:
            require(len(logs) == len(ranges) == 1, "Checkpoint must have one log and event range")
            first, last = map(int, ranges[0])
            require(first <= last, "Reversed checkpoint event range")
            checkpoints.append({"commit": commit, "first": first, "last": last})
    return checkpoints


def checkpoint_metadata(body):
    """Interpret correspondence only; a commit message never grants authority."""
    fields = {}
    for key in ("Feature", "Checkpoint", "Role", "Invocation", "Phase", "Log", "Events"):
        values = re.findall(r"^Orchestrator-" + key + r": (.+)$", body, re.M)
        require(len(values) <= 1, f"Repeated Orchestrator-{key} trailer")
        if values:
            fields[key.lower()] = values[0]
    return fields


def workflow_checkpoints(repo, log):
    """Account for every commit to be published from the recorded baseline."""
    baseline = log["branch_context"]["baseline_commit"]
    require(git(repo, "merge-base", "--is-ancestor", baseline, "HEAD", check=False).returncode == 0,
            "Feature baseline is not an ancestor of HEAD")
    raw = git(repo, "log", "--reverse", "--format=%H%x00%B%x00", baseline + "..HEAD").stdout.split("\0")
    checkpoints = []
    for offset in range(0, len(raw) - 1, 2):
        commit, body = raw[offset].strip(), raw[offset + 1]
        metadata = checkpoint_metadata(body)
        require(metadata.get("feature") == log["feature"] and metadata.get("checkpoint") in {"artifacts", "log"}
                and metadata.get("role") in {"Planner", "Coder", "Orchestrator"},
                f"Unaccounted-for commit {commit}; do not include unrelated commits in checkpoint delivery")
        paths = git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", commit).stdout.splitlines()
        record = {"commit": commit, "checkpoint_kind": metadata["checkpoint"], "publishing_role": metadata["role"],
                  "invocation": None, "phase_id": metadata.get("phase"), "event_ids": []}
        if metadata["checkpoint"] == "log":
            require(metadata["role"] == "Orchestrator" and metadata.get("log") == log["task_log_ref"] and
                    re.fullmatch(r"[1-9]\d*-[1-9]\d*", metadata.get("events", "")), "Log checkpoint needs Orchestrator and its event range")
            require(log["task_log_ref"] in paths, "Log checkpoint must change the authoritative task log")
            first, last = map(int, metadata["events"].split("-"))
            require(first <= last, "Reversed checkpoint event range")
            record.update(first=first, last=last, event_ids=[str(i) for i in range(first, last + 1)])
        else:
            require("log" not in metadata and "events" not in metadata and log["task_log_ref"] not in paths,
                    "Artifact checkpoints do not write the task log or carry event ranges")
            require(paths, "Artifact checkpoint must contain changes; do not create empty handoff commits")
        if metadata["role"] in {"Planner", "Coder"}:
            match = re.fullmatch(r"([1-9]\d*)/(Planner|Coder)/([1-9]\d*)", metadata.get("invocation", ""))
            require(match is not None and match[2] == metadata["role"], "Producer checkpoint needs trigger/role/attempt invocation")
            # Use only history already committed when this artifact was made.
            # Later retries/overrides cannot retroactively authorize its writer.
            recorded = json.loads(git(repo, "show", commit + ":" + log["task_log_ref"]).stdout)["history"]
            require(recorded == log["history"][:len(recorded)], "Artifact checkpoint contains a different workflow history")
            entry = next((e for e in recorded if e["id"] == match[1]), None)
            require(entry and entry["actor"] == match[2] and entry["event"] in {"spec-creation-started", "spec-revision-started", "coding-started", "coding-revision-started"}, "Checkpoint invocation is not a producer start")
            context = {"trigger_event_id": match[1], "role": match[2], "attempt": int(match[3])}
            failures = [e for e in recorded if e["event"] == "subagent-error" and e["details"]["invocation"]["trigger_event_id"] == match[1]]
            require(context["attempt"] <= len(failures) + 1, "Checkpoint uses an unrecorded attempt")
            record["invocation"] = context
            scope = entry["details"].get("work_scope", {"kind": "feature"})
            require(record["phase_id"] == scope.get("phase_id"), "Checkpoint phase disagrees with its publishing invocation")
        else:
            require("invocation" not in metadata and "phase" not in metadata, "Orchestrator does not invent delegated invocation trailers")
        checkpoints.append(record)
    return checkpoints


def recent_history(repo, log, cursor=None, limit=20):
    """Return bounded metadata and file statuses, never patches or file bodies."""
    require(1 <= limit <= 100, "History batch must contain 1 through 100 commits")
    head = git(repo, "rev-parse", "HEAD").stdout.strip()
    offset = 0
    if cursor:
        match = re.fullmatch(r"([0-9a-f]{40,64}):(\d+)", cursor)
        require(match is not None and match[1] == head, "History cursor is invalid or HEAD changed; reconcile from the beginning")
        offset = int(match[2])
    baseline = log["branch_context"]["baseline_commit"]
    commits = git(repo, "rev-list", "--first-parent", f"--skip={offset}", f"--max-count={limit + 1}", baseline + ".." + head).stdout.splitlines()
    items = []
    for commit in commits[:limit]:
        body = git(repo, "show", "-s", "--format=%B", commit).stdout.strip()
        names = git(repo, "diff-tree", "--no-renames", "--no-commit-id", "--name-status", "-r", "-z", commit).stdout.split("\0")
        changed = [{"status": names[i], "path": names[i + 1]} for i in range(0, len(names) - 1, 2)]
        items.append({"commit": commit, "message": body, "checkpoint": checkpoint_metadata(body), "changed_files": changed})
    dirty = git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all").stdout.split("\0")
    return {"head": head, "commits": items, "working_tree": [s for s in dirty if s],
            "next_cursor": f"{head}:{offset + limit}" if len(commits) > limit else None}


def select_feature_branch(repo, feature, explicit=None):
    """Resolve once; callers separately handle existing-branch/baseline conflicts."""
    branch = explicit if explicit is not None else feature
    require(git(repo, "check-ref-format", "--branch", branch, check=False).returncode == 0,
            "Invalid intended feature branch; obtain direction rather than inventing another name")
    return branch


def committed_checkpoint(repo, log):
    checkpoints = event_commits(repo, log["task_log_ref"])
    covered = 0
    latest = None
    for checkpoint in checkpoints:
        require(checkpoint["first"] == covered + 1, "Checkpoint ranges must be contiguous and nonduplicated")
        covered = checkpoint["last"]
        latest = checkpoint
        stored = json.loads(git(repo, "show", checkpoint["commit"] + ":" + log["task_log_ref"]).stdout)
        require(stored["history"] == log["history"][:covered], "Committed history differs from authoritative append-only history")
    require(covered <= len(log["history"]), "Git contains history absent from the working log")
    if covered != len(log["history"]):
        return None
    if latest:
        stored = json.loads(git(repo, "show", latest["commit"] + ":" + log["task_log_ref"]).stdout)
        require(stored == log, "Committed log does not match current checkpoint contents")
    return latest


def recovery_covers_attempt(details, attempt):
    """Bind a recovery decision to the actual latest local attempt and outcome."""
    contexts = details["failed_attempts"] if attempt["record"] == "failed" else details.get("uncertain_attempts", [])
    recorded = {k: v for k, v in attempt.items() if k != "record"}
    return any(all(context.get(k) == v for k, v in recorded.items()) for context in contexts)


def inspect_delivery(repo, log, remote_tip=None):
    log_checkpoint = committed_checkpoint(repo, log)
    if log_checkpoint is None:
        return {"delivery": "uncommitted", "checkpoint": None}
    checkpoints = workflow_checkpoints(repo, log)
    checkpoint = checkpoints[-1]
    branch = log["branch_context"]
    uncertainty = None
    if remote_tip is None:
        result = git(repo, "ls-remote", "--exit-code", branch["remote"], "refs/heads/" + branch["feature_branch"], check=False)
        if result.returncode not in {0, 2}:
            uncertainty = "Cannot inspect remote delivery"
        remote_tip = result.stdout.split()[0] if not uncertainty and result.stdout.strip() else ""
    if remote_tip:
        present = git(repo, "cat-file", "-e", remote_tip + "^{commit}", check=False).returncode == 0
        if remote_tip == checkpoint["commit"] or present and git(repo, "merge-base", "--is-ancestor", checkpoint["commit"], remote_tip, check=False).returncode == 0:
            return {"delivery": "delivered", "checkpoint": checkpoint}
        if not present:
            uncertainty = "Remote ancestry is unavailable locally"
        elif git(repo, "merge-base", "--is-ancestor", remote_tip, checkpoint["commit"], check=False).returncode != 0:
            return {"delivery": "uncertain", "checkpoint": checkpoint, "reason": "Remote branch diverged; obtain direction without force-pushing"}
    journal = read_attempts(repo, log["feature"])
    authorizations = [e for e in log["history"] if e["event"] == "user-authorization-recorded"
                      and e["details"]["kind"] == "checkpoint_recovery"]
    latest_auth = authorizations[-1] if authorizations else None
    used = {r.get("authorization_event_id") for r in journal if r["record"] == "started"}
    if latest_auth and latest_auth["details"]["decision"] == "granted" and latest_auth["id"] not in used:
        if journal and recovery_covers_attempt(latest_auth["details"], journal[-1]):
            return {"delivery": "committed", "checkpoint": checkpoint, "authorization_event_id": latest_auth["id"]}
    if journal:
        # A prior successful push has no receipt. Git ancestry is its evidence,
        # including when a later logical checkpoint now needs its first push.
        attempted = journal[-1]["attempted_commit"]
        if remote_tip and git(repo, "merge-base", "--is-ancestor", attempted, remote_tip, check=False).returncode == 0:
            return {"delivery": "committed", "checkpoint": checkpoint, "authorization_event_id": None}
        observed = {"delivery": "failed" if journal[-1]["record"] == "failed" and not uncertainty else "uncertain", "checkpoint": checkpoint}
        if uncertainty:
            observed["reason"] = uncertainty
        if journal[-1]["record"] == "started":
            observed["uncertain_attempt"] = {k: v for k, v in journal[-1].items() if k != "record"}
            observed["uncertain_attempt"]["observation"] = "No result was recorded for this attempt. " + (
                uncertainty + "." if uncertainty else "Remote inspection does not establish delivery of its commit.")
        return observed
    if uncertainty:
        return {"delivery": "uncertain", "checkpoint": checkpoint, "reason": uncertainty}
    return {"delivery": "committed", "checkpoint": checkpoint, "authorization_event_id": None}


def record_push_attempt(repo, log, authorization_event_id=None):
    from workflow_protocol import replay
    replay(log)
    require(committed_checkpoint(repo, log) is not None, "Commit the update and recovery authorization before attempting delivery")
    checkpoint = workflow_checkpoints(repo, log)[-1]
    require(git(repo, "rev-parse", "HEAD").stdout.strip() == checkpoint["commit"],
            "The attempted HEAD must be the validated checkpoint, without later unrelated commits")
    delivery = inspect_delivery(repo, log)
    require(delivery["delivery"] != "delivered", "Checkpoint already delivered; do not repeat its push")
    branch = log["branch_context"]
    require(git(repo, "branch", "--show-current").stdout.strip() == branch["feature_branch"], "Wrong active feature branch")
    journal = read_attempts(repo, log["feature"])
    if authorization_event_id:
        auth = next((e for e in log["history"] if e["id"] == authorization_event_id), None)
        require(auth and auth["event"] == "user-authorization-recorded" and auth["details"]["kind"] == "checkpoint_recovery"
                and auth["details"]["decision"] == "granted", "Missing checkpoint retry authorization")
        require(not any(r["record"] == "started" and r.get("authorization_event_id") == authorization_event_id for r in journal), "Retry authorization already consumed")
        require(not any(e["event"] == "user-authorization-recorded" and e["details"]["kind"] == "checkpoint_recovery"
                        for e in log["history"][int(authorization_event_id):]), "A later recovery decision supersedes this authorization")
        require(journal and recovery_covers_attempt(auth["details"], journal[-1]), "Retry authorization omits or misstates latest local attempt")
    else:
        # A new logical checkpoint is allowed only after earlier attempts were delivered.
        if journal:
            previous_commit = journal[-1]["attempted_commit"]
            remote = git(repo, "ls-remote", "--exit-code", branch["remote"], "refs/heads/" + branch["feature_branch"], check=False)
            tip = remote.stdout.split()[0] if remote.returncode == 0 and remote.stdout.strip() else ""
            require(tip and git(repo, "merge-base", "--is-ancestor", previous_commit, tip, check=False).returncode == 0,
                    "Previous delivery failed/is uncertain; obtain recovery direction")
    require(delivery["delivery"] == "committed", "Delivery is failed/uncertain; obtain and commit recovery direction before retry")
    record = {"record": "started", "attempt_id": str(uuid.uuid4()), "timestamp": utc_now(),
              "attempted_commit": git(repo, "rev-parse", "HEAD").stdout.strip(),
              "event_ids": checkpoint["event_ids"], "checkpoint_kind": checkpoint["checkpoint_kind"],
              "publishing_role": checkpoint["publishing_role"], "invocation": checkpoint["invocation"], "phase_id": checkpoint["phase_id"],
              "remote": branch["remote"], "feature_branch": branch["feature_branch"],
              "authorization_event_id": authorization_event_id}
    append_attempt(repo, log["feature"], record)
    return record


def record_push_failure(repo, feature, attempt_id, exit_code, error_summary):
    require(exit_code != 0, "Do not create success receipts")
    require(error_summary.strip(), "Failure needs a redacted error summary")
    records = read_attempts(repo, feature)
    require(records and records[-1]["record"] == "started" and records[-1]["attempt_id"] == attempt_id,
            "Failure must complete the latest started attempt once")
    record = {**records[-1], "record": "failed", "timestamp": utc_now(), "exit_code": exit_code, "error_summary": error_summary}
    append_attempt(repo, feature, record)
    return {k: v for k, v in record.items() if k != "record"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("inspect", "recent", "attempt", "failure"))
    parser.add_argument("log", type=Path)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--authorization-event")
    parser.add_argument("--cursor")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--attempt-id")
    parser.add_argument("--exit-code", type=int)
    parser.add_argument("--error-summary", help="Redacted summary; never credentials or raw authenticated URLs")
    args = parser.parse_args()
    log = json.loads(args.log.read_text(encoding="utf-8-sig"))
    from workflow_protocol import replay
    replay(log)
    if args.action == "inspect":
        result = inspect_delivery(args.repo, log)
    elif args.action == "recent":
        result = recent_history(args.repo, log, args.cursor, args.limit)
    elif args.action == "attempt":
        result = record_push_attempt(args.repo, log, args.authorization_event)
    else:
        require(args.attempt_id and args.exit_code is not None and args.error_summary, "Failure requires attempt, exit code, and redacted summary")
        result = record_push_failure(args.repo, log["feature"], args.attempt_id, args.exit_code, args.error_summary)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValidationError, OSError, ValueError) as exc:
        raise SystemExit(f"INVALID: {exc}")
