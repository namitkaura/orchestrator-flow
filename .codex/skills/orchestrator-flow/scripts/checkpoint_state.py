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


def git(repo, *args, check=True, binary=False):
    # Checkpoints and grants name physical Git objects, including their original parents.
    result = subprocess.run(["git", "--no-replace-objects", "-C", str(repo), *args], capture_output=True,
                            encoding=None if binary else "utf-8", env={**os.environ, "GIT_GRAFT_FILE": os.devnull})
    if check and result.returncode:
        error = result.stderr.decode("utf-8", "replace") if binary else result.stderr
        raise ValidationError(error.strip() or f"git {' '.join(args)} failed")
    return result


def journal_path(repo, feature):
    require(re.fullmatch(r"[a-z0-9]+(?:[.-][a-z0-9]+)*", feature), "Invalid feature identity")
    value = git(repo, "rev-parse", "--git-path", f"orchestrator-flow/{feature}/checkpoint-attempts.jsonl").stdout.strip()
    path = Path(value)
    return path if path.is_absolute() else Path(repo) / path


def read_attempts(repo, feature):
    path = journal_path(repo, feature)
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line] if path.exists() else []


def run_attempts(repo, log, checkpoint_commit):
    """This run's journal records: on its feature branch and remote, for the checkpoint or one of its ancestors.

    The journal is keyed by feature, so an earlier run of the same feature can leave records on another
    branch, or on a recreated branch where its commits are unrelated. A commit missing locally (Git exits
    128), for example after an old branch was deleted and collected, is another run's too.
    """
    branch = log["branch_context"]
    return [record for record in read_attempts(repo, log["feature"])
            if record["feature_branch"] == branch["feature_branch"] and record["remote"] == branch["remote"]
            and git(repo, "merge-base", "--is-ancestor", record["attempted_commit"], checkpoint_commit, check=False).returncode == 0]


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
        if any(value in logs for value in ([log_ref] if isinstance(log_ref, str) else log_ref)):
            require(len(logs) == len(ranges) == 1, "Checkpoint must have one log and event range")
            first, last = map(int, ranges[0])
            require(first <= last, "Reversed checkpoint event range")
            checkpoints.append({"commit": commit, "first": first, "last": last, "log_ref": logs[0]})
    return checkpoints


CHECKPOINT_FIELDS = ("Feature", "Checkpoint", "Role", "Invocation", "Phase", "Log", "Events")


def checkpoint_metadata(body):
    """Interpret correspondence only; a commit message never grants authority."""
    fields = {}
    for key in CHECKPOINT_FIELDS:
        values = re.findall(r"^Orchestrator-" + key + r": (.+)$", body, re.M)
        require(len(values) <= 1, f"Repeated Orchestrator-{key} trailer")
        if values:
            fields[key.lower()] = values[0]
    return fields


def checkpoint_log(repo, log, commit):
    """Read the single historical authoritative log at its recorded location."""
    from workflow_protocol import log_locations, feature_directory
    found = []
    for directory in log_locations(log):
        ref = directory + "/task_log.json"
        result = git(repo, "show", commit + ":" + ref, check=False)
        if result.returncode == 0:
            stored = json.loads(result.stdout)
            require(stored["task_log_ref"] == ref and stored["feature"] == log["feature"] and
                    stored["history"] == log["history"][:len(stored["history"])] and
                    stored["feature_dir"] == feature_directory(log, len(stored["history"])),
                    "Historical checkpoint location/history differs from recorded workflow")
            found.append(stored)
    require(len(found) == 1, "Checkpoint must contain exactly one authoritative historical task log")
    return found[0]


def artifact_checkpoint_ref(repo, log, commit, name):
    if not any(e["event"] == "feature-relocated" for e in log["history"]):
        return log[name + "_ref"]
    return checkpoint_log(repo, log, commit)["feature_dir"] + "/" + name + ".md"


def validate_external_commit(repo, commit, parent, log_refs, spec_input_directory=None):
    """Inspect the whole Git inventory; only the legacy spec-input grant requires text blobs."""
    from workflow_protocol import relative_path
    raw = git(repo, "diff-tree", "--raw", "-r", "-z", "--no-renames", "--no-abbrev",
              "--ignore-submodules=none", "--no-commit-id", parent, commit, "--", binary=True).stdout
    fields = raw.split(b"\0")[:-1]
    require(fields and len(fields) % 2 == 0, f"Unaccounted-for commit {commit}: empty or incomplete file inventory")
    for header, name in zip(fields[::2], fields[1::2]):
        old_mode, mode, _, blob, status = header.split()
        try:
            path = relative_path(name.decode("utf-8"))
        except UnicodeDecodeError as exc:
            raise ValidationError(f"Unaccounted-for commit {commit}: invalid UTF-8 path") from exc
        require(path not in log_refs, f"Unaccounted-for commit {commit}: external change to authoritative log {path}")
        if spec_input_directory is None:
            # --no-renames exposes both sides of a move. Inspect the old mode on deletes, too.
            regular_or_absent = {b"100644", b"100755", b"000000"}
            require(status in {b"A", b"M", b"D"} and old_mode[1:] in regular_or_absent and mode in regular_or_absent,
                    f"Unaccounted-for commit {commit}: unsupported external file change at {path}")
            continue
        require(status == b"A" and old_mode == b":000000" and mode in {b"100644", b"100755"},
                f"Unaccounted-for commit {commit}: every change must add a regular specification input")
        filename = path.rsplit("/", 1)[-1]
        require(path.startswith(spec_input_directory + "/") and filename.startswith(("proposal-", "bugreport-")) and filename.endswith(".md"),
                f"Unaccounted-for commit {commit}: {path} is outside the permitted specification inputs")
        content = git(repo, "cat-file", "blob", blob.decode("ascii"), binary=True).stdout
        require(b"\0" not in content, f"Unaccounted-for commit {commit}: NUL byte in {path}")
        try:
            content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValidationError(f"Unaccounted-for commit {commit}: invalid UTF-8 in {path}") from exc


def external_commit_prerequisites(repo, log, inputs, checkpoints, allow_pending):
    """Find acknowledgment commits that need remote proof for producers or withdrawals."""
    from workflow_protocol import feature_directory, log_locations
    decisions = {}
    for entry in log["history"]:
        details = entry.get("details", {})
        if entry["event"] != "user-authorization-recorded" or details["operation"] not in {"accept-spec-input-commit", "accept-external-commit"}:
            continue
        scope = details["scope"]
        require(entry["actor"] == entry["requestor"] == "User" and details["kind"] == "external_operation"
                and details["user_statement"].strip() and details["limits"] == {"max_attempts": None, "additional_cycles": None, "phase": None}
                and not details["failed_attempts"] and not details.get("uncertain_attempts"),
                f"Invalid authority for {details['operation']}")
        require(scope in inputs, f"Unaccounted-for commit: scope must match an exact ordinary commit ID: {scope}")
        decisions.setdefault(scope, []).append(entry)
    missing = inputs.difference(decisions)
    if missing:
        raise ValidationError(f"Unaccounted-for commit {min(missing)}; do not include unrelated commits in checkpoint delivery")
    if not inputs:
        return set(), set()

    branch = log["branch_context"]
    require(git(repo, "branch", "--show-current").stdout.strip() == branch["feature_branch"], "Wrong active feature branch")
    baseline = git(repo, "rev-parse", branch["baseline_commit"] + "^{commit}").stdout.strip()
    chain = [row.split() for row in git(repo, "rev-list", "--first-parent", "--parents", "--reverse",
                                        baseline + "..HEAD").stdout.splitlines()]
    require(chain and chain[0][1:2] == [baseline], "Feature baseline must be on the first-parent history")
    positions = {row[0]: index for index, row in enumerate(chain)}

    def precedes(earlier, later):
        if earlier in positions and later in positions:
            return positions[earlier] < positions[later]
        return earlier != later and git(repo, "merge-base", "--is-ancestor", earlier, later, check=False).returncode == 0

    log_checkpoints = [c for c in checkpoints if c["checkpoint_kind"] == "log"]
    covering = {}
    last = 0
    for checkpoint in log_checkpoints:
        require(checkpoint["first"] == last + 1, "Checkpoint ranges must be contiguous and nonduplicated")
        covering.update(dict.fromkeys(checkpoint["event_ids"], checkpoint["commit"]))
        last = checkpoint["last"]
    producers = [c["commit"] for c in checkpoints if c["publishing_role"] in {"Planner", "Coder"}]
    log_refs = {directory + "/task_log.json" for directory in log_locations(log)}
    for_producers, for_withdrawals = set(), set()
    for commit, entries in decisions.items():
        require(commit in positions and len(chain[positions[commit]]) == 2,
                f"Unaccounted-for commit {commit}: expected a single-parent input on the feature first-parent history")

        # Reduce each checkpoint's decisions at its closing event. None is the
        # append-only candidate suffix and can only bootstrap workspace validation.
        at_boundary = {}
        for entry in entries:
            boundary = covering.get(entry["id"])
            require(boundary is None or boundary in positions and precedes(commit, boundary),
                    f"Unaccounted-for commit {commit}: acknowledgment must follow its input on the feature branch")
            at_boundary[boundary] = entry["details"]
        grants = {boundary: details["operation"] for boundary, details in at_boundary.items()
                  if details["decision"] == "granted"}
        acknowledged = next((boundary for boundary in grants if boundary is not None), None)
        require(acknowledged or allow_pending and None in grants,
                f"Unaccounted-for commit {commit}: missing effective external commit grant")
        # Each effective grant must fit its operation. The narrow policy also satisfies the general one.
        directory = None
        if "accept-spec-input-commit" in grants.values():
            prior = max((c["last"] for c in log_checkpoints if precedes(c["commit"], commit)), default=0)
            directory = feature_directory(log, prior)
        validate_external_commit(repo, commit, chain[positions[commit]][1], log_refs, directory)
        if acknowledged and entries[-1]["details"]["decision"] != "granted":
            for_withdrawals.add(acknowledged)
        for producer in producers:
            if precedes(producer, commit):
                continue
            require(acknowledged and precedes(acknowledged, producer),
                    f"Unaccounted-for commit {commit}: producer work precedes its external commit acknowledgment")
            for_producers.add(acknowledged)
    return for_producers, for_withdrawals


def checkpoint_history(repo, log, allow_pending=False):
    """Account for every commit to be published from the recorded baseline."""
    from workflow_protocol import feature_directory, log_locations
    baseline = log["branch_context"]["baseline_commit"]
    require(git(repo, "merge-base", "--is-ancestor", baseline, "HEAD", check=False).returncode == 0,
            "Feature baseline is not an ancestor of HEAD")
    raw = git(repo, "log", "--topo-order", "--reverse", "--format=%H%x00%B%x00", baseline + "..HEAD").stdout.split("\0")
    checkpoints = []
    inputs = set()
    for offset in range(0, len(raw) - 1, 2):
        commit, body = raw[offset].strip(), raw[offset + 1]
        metadata = checkpoint_metadata(body)
        if not metadata:
            claims = re.findall(r"^Orchestrator-(\w+):", body, re.M)
            require(not any(key in CHECKPOINT_FIELDS for key in claims),
                    f"Unaccounted-for commit {commit}: malformed Flow checkpoint trailer")
            inputs.add(commit)
            continue
        require(metadata.get("feature") == log["feature"] and metadata.get("checkpoint") in {"artifacts", "log"}
                and metadata.get("role") in {"Planner", "Coder", "Orchestrator"},
                f"Unaccounted-for commit {commit}; do not include unrelated commits in checkpoint delivery")
        paths = git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", commit).stdout.splitlines()
        record = {"commit": commit, "checkpoint_kind": metadata["checkpoint"], "publishing_role": metadata["role"],
                  "invocation": None, "phase_id": metadata.get("phase"), "event_ids": []}
        if metadata["checkpoint"] == "log":
            require(metadata["role"] == "Orchestrator" and metadata.get("log") in {d + "/task_log.json" for d in log_locations(log)} and
                    re.fullmatch(r"[1-9]\d*-[1-9]\d*", metadata.get("events", "")), "Log checkpoint needs Orchestrator and its event range")
            require(metadata["log"] in paths, "Log checkpoint must change the authoritative task log")
            first, last = map(int, metadata["events"].split("-"))
            require(metadata["log"] == feature_directory(log, last) + "/task_log.json",
                    "Log trailer disagrees with its historical location")
            stored = checkpoint_log(repo, log, commit)
            require(len(stored["history"]) == last, "Log checkpoint event range differs from its contents")
            require(first <= last, "Reversed checkpoint event range")
            record.update(first=first, last=last, event_ids=[str(i) for i in range(first, last + 1)])
        else:
            require("log" not in metadata and "events" not in metadata and not {d + "/task_log.json" for d in log_locations(log)}.intersection(paths),
                    "Artifact checkpoints do not write the task log or carry event ranges")
            require(paths, "Artifact checkpoint must contain changes; do not create empty handoff commits")
        if metadata["role"] in {"Planner", "Coder"}:
            match = re.fullmatch(r"([1-9]\d*)/(Planner|Coder)/([1-9]\d*)", metadata.get("invocation", ""))
            require(match is not None and match[2] == metadata["role"], "Producer checkpoint needs trigger/role/attempt invocation")
            # Use only history already committed when this artifact was made.
            # Later retries/overrides cannot retroactively authorize its writer.
            recorded = checkpoint_log(repo, log, commit)["history"]
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
    producers, withdrawals = external_commit_prerequisites(repo, log, inputs, checkpoints, allow_pending)
    return checkpoints, producers, withdrawals


def advertised_tip(repo, branch):
    """An empty tip means the branch is absent. None means Git could not inspect it."""
    result = git(repo, "ls-remote", "--exit-code", branch["remote"], "refs/heads/" + branch["feature_branch"], check=False)
    if result.returncode == 2:
        return ""
    return result.stdout.split()[0] if result.returncode == 0 and result.stdout.strip() else None


def acknowledgment_delivery_issue(repo, commits, tip):
    for commit in sorted(commits):
        if not tip or git(repo, "merge-base", "--is-ancestor", commit, tip, check=False).returncode != 0:
            return f"Establish delivery of external commit acknowledgment {commit} on the remote feature branch first"
    return None


def workflow_checkpoints(repo, log, *, allow_pending=False):
    checkpoints, _, withdrawals = checkpoint_history(repo, log, allow_pending)
    if withdrawals:
        issue = acknowledgment_delivery_issue(repo, withdrawals, advertised_tip(repo, log["branch_context"]))
        require(issue is None, issue)
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
    from workflow_protocol import log_locations, feature_directory
    checkpoints = event_commits(repo, [d + "/task_log.json" for d in log_locations(log)])
    covered = 0
    latest = None
    for checkpoint in checkpoints:
        require(checkpoint["first"] == covered + 1, "Checkpoint ranges must be contiguous and nonduplicated")
        require(checkpoint["log_ref"] == feature_directory(log, checkpoint["last"]) + "/task_log.json", "Checkpoint used the wrong historical log path")
        covered = checkpoint["last"]
        latest = checkpoint
        stored = json.loads(git(repo, "show", checkpoint["commit"] + ":" + checkpoint["log_ref"]).stdout)
        require(stored["history"] == log["history"][:covered], "Committed history differs from authoritative append-only history")
    require(covered <= len(log["history"]), "Git contains history absent from the working log")
    if covered != len(log["history"]):
        return None
    if latest:
        stored = json.loads(git(repo, "show", latest["commit"] + ":" + latest["log_ref"]).stdout)
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
    checkpoints, producer_prerequisites, withdrawals = checkpoint_history(repo, log)
    checkpoint = checkpoints[-1]
    branch = log["branch_context"]
    uncertainty = None
    if remote_tip is None:
        remote_tip = advertised_tip(repo, branch)
        if remote_tip is None:
            uncertainty = "Cannot inspect remote delivery"
    # Every later producer contributes its prerequisite, including producers below a log HEAD.
    prerequisite = acknowledgment_delivery_issue(repo, producer_prerequisites | withdrawals, remote_tip)
    if remote_tip:
        present = git(repo, "cat-file", "-e", remote_tip + "^{commit}", check=False).returncode == 0
        if remote_tip == checkpoint["commit"] or present and git(repo, "merge-base", "--is-ancestor", checkpoint["commit"], remote_tip, check=False).returncode == 0:
            return {"delivery": "delivered", "checkpoint": checkpoint}
        if not present:
            uncertainty = "Remote ancestry is unavailable locally"
        elif git(repo, "merge-base", "--is-ancestor", remote_tip, checkpoint["commit"], check=False).returncode != 0:
            return {"delivery": "uncertain", "checkpoint": checkpoint, "reason": "Remote branch diverged; obtain direction without force-pushing"}
    if prerequisite:
        uncertainty = prerequisite
    journal = run_attempts(repo, log, checkpoint["commit"])
    authorizations = [e for e in log["history"] if e["event"] == "user-authorization-recorded"
                      and e["details"]["kind"] == "checkpoint_recovery"]
    latest_auth = authorizations[-1] if authorizations else None
    used = {r.get("authorization_event_id") for r in journal if r["record"] == "started"}
    if not prerequisite and latest_auth and latest_auth["details"]["decision"] == "granted" and latest_auth["id"] not in used:
        if journal and recovery_covers_attempt(latest_auth["details"], journal[-1]):
            return {"delivery": "committed", "checkpoint": checkpoint, "authorization_event_id": latest_auth["id"]}
    if journal:
        # A prior successful push has no receipt. Git ancestry is its evidence,
        # including when a later logical checkpoint now needs its first push.
        attempted = journal[-1]["attempted_commit"]
        if not prerequisite and remote_tip and git(repo, "merge-base", "--is-ancestor", attempted, remote_tip, check=False).returncode == 0:
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
    delivery = inspect_delivery(repo, log)
    checkpoint = delivery["checkpoint"]
    require(checkpoint is not None, "Commit the update and recovery authorization before attempting delivery")
    require(delivery["delivery"] != "delivered", "Checkpoint already delivered; do not repeat its push")
    branch = log["branch_context"]
    require(git(repo, "branch", "--show-current").stdout.strip() == branch["feature_branch"], "Wrong active feature branch")
    journal = run_attempts(repo, log, checkpoint["commit"])
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
            tip = advertised_tip(repo, branch)
            require(tip and git(repo, "merge-base", "--is-ancestor", previous_commit, tip, check=False).returncode == 0,
                    "Previous delivery failed/is uncertain; obtain recovery direction")
    require(delivery["delivery"] == "committed", delivery.get("reason") or "Delivery is failed/uncertain; obtain and commit recovery direction before retry")
    require(git(repo, "rev-parse", "HEAD").stdout.strip() == checkpoint["commit"],
            "The attempted HEAD must be the validated checkpoint, without later unrelated commits")
    record = {"record": "started", "attempt_id": str(uuid.uuid4()), "timestamp": utc_now(),
              "attempted_commit": checkpoint["commit"],
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
