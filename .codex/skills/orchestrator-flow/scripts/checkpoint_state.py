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


def committed_checkpoint(repo, log):
    checkpoints = event_commits(repo, log["task_log_ref"])
    covered = 0
    latest = None
    for checkpoint in checkpoints:
        require(checkpoint["first"] == covered + 1, "Checkpoint ranges must be contiguous and nonduplicated")
        covered = checkpoint["last"]
        latest = checkpoint
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
    checkpoint = committed_checkpoint(repo, log)
    if checkpoint is None:
        return {"delivery": "uncommitted", "checkpoint": None}
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
    checkpoint = committed_checkpoint(repo, log)
    require(checkpoint is not None, "Commit the update and recovery authorization before attempting delivery")
    require(git(repo, "rev-parse", "HEAD").stdout.strip() == checkpoint["commit"],
            "The attempted HEAD must be the validated checkpoint, without later unrelated commits")
    require(inspect_delivery(repo, log)["delivery"] != "delivered", "Checkpoint already delivered; do not repeat its push")
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
    record = {"record": "started", "attempt_id": str(uuid.uuid4()), "timestamp": utc_now(),
              "attempted_commit": git(repo, "rev-parse", "HEAD").stdout.strip(),
              "event_ids": [str(i) for i in range(checkpoint["first"], checkpoint["last"] + 1)],
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
    parser.add_argument("action", choices=("inspect", "attempt", "failure"))
    parser.add_argument("log", type=Path)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--authorization-event")
    parser.add_argument("--attempt-id")
    parser.add_argument("--exit-code", type=int)
    parser.add_argument("--error-summary", help="Redacted summary; never credentials or raw authenticated URLs")
    args = parser.parse_args()
    log = json.loads(args.log.read_text(encoding="utf-8-sig"))
    from workflow_protocol import replay
    replay(log)
    if args.action == "inspect":
        result = inspect_delivery(args.repo, log)
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
