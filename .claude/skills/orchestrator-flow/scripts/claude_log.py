#!/usr/bin/env python3
"""Record Orchestrator Flow task-log entries in Claude Code.

record-return  Record a role's actual return, read from its subagent transcript by agent ID (or an
               explicit transcript path, or unaltered inline JSON on stdin). Wrappers go through the
               shared record_handoff; --coordination records a Coder coordination report as coding-updated.
append-entry   Record one Orchestrator-authored entry ({actor, requestor, event, details}) from stdin.

Both validate the candidate log with the shared replay before writing, read the written log back,
and print a compact JSON summary. Neither commits, pushes nor dispatches agents.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys

from workflow_artifacts import ValidationError, json_values_equal, require
from workflow_protocol import replay
from validate_orchestrator_artifacts import HandoffError, record_handoff, validate_workspace

WRAPPER_KEYS = ("spec_change_wrapper", "spec_review_wrapper", "change_wrapper", "review_wrapper")
RUN_ORIGINS = {"coordinator", "peer"}
# Notification text is XML-escaped and control tags may be neutralized; such text is not the original return.
ALTERED_INLINE = re.compile(r"\[harness:|&(?:lt|gt|amp|quot);|<\\[A-Za-z]")
AGENT_ID = re.compile(r"[A-Za-z0-9_-]+")


class RecorderError(ValidationError):
    def __init__(self, category, message):
        self.category = category
        super().__init__(f"{category}: {message}")


def config_dir():
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")


def find_transcript(agent_id, session_id=None):
    """Locate agent-<id>.jsonl in this session, else in another session of the same project."""
    require(AGENT_ID.fullmatch(agent_id or ""), "Agent IDs contain only letters, digits, '-' and '_'")
    session = session_id or os.environ.get("CLAUDE_CODE_SESSION_ID")
    if not session:
        raise RecorderError("transcript_unavailable", "CLAUDE_CODE_SESSION_ID is not set; pass --transcript")
    projects = config_dir() / "projects"
    name = f"agent-{agent_id}.jsonl"
    project_dirs = sorted({p.parent for p in projects.glob(f"*/{session}")} | {p.parent for p in projects.glob(f"*/{session}.jsonl")})
    for project in project_dirs:
        direct = project / session / "subagents" / name
        if direct.is_file():
            return direct
    # A resumed session keeps its ID, but an agent can still belong to another session of this project.
    matches = sorted({match for project in project_dirs for match in project.glob(f"*/subagents/{name}")})
    if len(matches) == 1:
        return matches[0]
    if matches:
        raise RecorderError("transcript_unavailable", f"agent {agent_id} appears in several sessions; pass --transcript")
    raise RecorderError("transcript_unavailable", f"no transcript for agent {agent_id} in this project's sessions")


def read_records(path):
    try:
        text = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise RecorderError("transcript_unavailable", str(exc)) from exc
    lines = text.splitlines()
    records = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            if number == len(lines):
                raise RecorderError("no_completed_report", "the transcript's last line is still being written") from exc
            raise RecorderError("transcript_layout_changed", f"transcript line {number} is not JSON") from exc
        if not isinstance(record, dict) or not isinstance(record.get("type"), str):
            raise RecorderError("transcript_layout_changed", f"transcript line {number} has no record type")
        if record["type"] in ("user", "assistant"):
            message = record.get("message")
            if not isinstance(message, dict) or not isinstance(message.get("content"), (str, list)):
                raise RecorderError("transcript_layout_changed", f"transcript line {number} has no message content")
        records.append(record)
    return records


def blocks(record):
    content = record["message"]["content"]
    return [b for b in content if isinstance(b, dict)] if isinstance(content, list) else []


def starts_run(record):
    """A run starts at a user prompt or at a message from the coordinator or a peer; harness prompts do not."""
    if record["type"] != "user":
        return False
    if record.get("isMeta"):
        origin = record.get("origin")
        return isinstance(origin, dict) and origin.get("kind") in RUN_ORIGINS
    return isinstance(record["message"]["content"], str) or not any(b.get("type") == "tool_result" for b in blocks(record))


def delivered(result):
    content = result.get("content")
    text = content if isinstance(content, str) else "".join(b.get("text", "") for b in content or [] if isinstance(b, dict))
    try:
        return json.loads(text).get("success") is True
    except (ValueError, AttributeError):
        return "delivered" in text.lower()


def select_report(records):
    """Return (report text, the assistant record carrying it) for the latest completed run."""
    starts = [index for index, record in enumerate(records) if starts_run(record)]
    if not starts:
        raise RecorderError("transcript_layout_changed", "the transcript has no prompt record")
    run = [record for record in records[starts[-1] + 1:] if record["type"] in ("user", "assistant")]
    for index in range(len(run) - 1, -1, -1):
        handbacks = [b for b in blocks(run[index]) if run[index]["type"] == "assistant"
                     and b.get("type") == "tool_use" and b.get("name") == "SubagentHandback"]
        if not handbacks:
            continue
        handback = handbacks[-1]
        result = next((b for later in run[index + 1:] if later["type"] == "user" for b in blocks(later)
                       if b.get("type") == "tool_result" and b.get("tool_use_id") == handback.get("id")), None)
        if result is None:
            raise RecorderError("no_completed_report", "the latest handback has no result yet")
        if result.get("is_error") or not delivered(result):
            raise RecorderError("report_not_delivered", "Claude Code did not deliver the latest handback")
        report = (handback.get("input") or {}).get("message")
        if not isinstance(report, str):
            raise RecorderError("transcript_layout_changed", "the handback has no message text")
        return report, run[index]
    assistant = [index for index, record in enumerate(run) if record["type"] == "assistant"]
    if not assistant or any(record["type"] == "user" for record in run[assistant[-1] + 1:]):
        raise RecorderError("no_completed_report", "the latest run has not finished")
    message_id = run[assistant[-1]]["message"].get("id")
    final = [run[i] for i in assistant if message_id and run[i]["message"].get("id") == message_id] or [run[assistant[-1]]]
    parts = [b for record in final for b in blocks(record)]
    if any(b.get("type") == "tool_use" for b in parts):
        raise RecorderError("no_completed_report", "the latest run ends with a tool call")
    stop = final[-1]["message"].get("stop_reason")
    if stop not in ("end_turn", "stop_sequence"):
        raise RecorderError("no_completed_report", f"the final message stopped with {stop!r}")
    text = "".join(b.get("text", "") for b in parts if b.get("type") == "text")
    if not text.strip():
        raise RecorderError("no_completed_report", "the final message has no text")
    return text, final[-1]


def parse_report(text):
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RecorderError("report_not_json", f"the report is not JSON ({exc.msg} at character {exc.pos}); ask the same agent "
                                               "to return the wrapper alone") from exc
    if not isinstance(value, dict):
        raise RecorderError("report_not_json", "the report is not a JSON object")
    return value


def read_inline():
    text = sys.stdin.buffer.read().decode("utf-8-sig")
    altered = ALTERED_INLINE.search(text)
    if altered:
        raise RecorderError("inline_text_altered", f"inline text contains {altered.group(0)!r}; record from the transcript "
                                                   "or ask the user")
    return parse_report(text)


def already_recorded(log, value):
    for entry in log["history"]:
        if any(key in entry and json_values_equal(entry[key], value) for key in WRAPPER_KEYS) or \
                (entry["event"] == "coding-updated" and json_values_equal(entry.get("details"), value)):
            return entry["id"]
    return None


def write_verified(path, before, previous, candidate):
    """Write only the authoritative log, then read it back; mirrors record_handoff."""
    encoded = (json.dumps(candidate, ensure_ascii=True, indent=2) + "\n").encode("utf-8")
    try:
        require(path.read_bytes() == before, "Authoritative log changed while preparing the entry")
        path.write_bytes(encoded)
        written = json.loads(path.read_bytes().decode("utf-8-sig"))
        require(json_values_equal(written, candidate), "Written log differs from the validated candidate")
        require(json_values_equal(written["history"][:-1], previous["history"]), "Written historical prefix changed")
    except (ValidationError, ValueError, OSError) as exc:
        raise HandoffError("recording_error", f"Do not publish: {exc}") from exc


def append_entry(path, entry, workspace=None):
    """Derive id, timestamp, status and effective fields for one entry; validate before writing."""
    path = Path(path)
    before = path.read_bytes()
    previous = json.loads(before.decode("utf-8-sig"))
    try:
        require(isinstance(entry, dict) and set(entry) == {"actor", "requestor", "event", "details"},
                "An entry supplies exactly actor, requestor, event and details")
        state = replay(previous)
        derived = {"id": str(len(previous["history"]) + 1), "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "actor": entry["actor"], "requestor": entry["requestor"], "event": entry["event"], "details": deepcopy(entry["details"])}
        state.append(derived, derive_status=True)
        candidate = deepcopy(previous)
        candidate["history"].append(derived)
        candidate["status"] = state.status
        candidate.update(deepcopy(state.config))
        replay(candidate, previous=previous)
        if workspace:
            validate_workspace(replay(candidate), Path(workspace))
    except (ValidationError, ValueError, TypeError, KeyError) as exc:
        raise HandoffError("invalid_entry", str(exc)) from exc
    write_verified(path, before, previous, candidate)
    return candidate


def coordination_entry(log, details):
    state = replay(log)
    if state.status not in {"coding_in_progress", "blocked"} or "Coder" not in state.starts:
        raise HandoffError("recording_error", "No active Coder assignment expects a coordination report")
    trigger = state.entries[state.starts["Coder"]["trigger_event_id"]]
    return {"actor": "Coder", "requestor": trigger["requestor"], "event": "coding-updated", "details": details}


def title(finding):
    first = (finding.get("description") or "").strip().splitlines()[0] if finding.get("description") else ""
    return first if len(first) <= 100 else first[:97] + "..."


def observed_capability(state, entry, record):
    """Report the model and effort the transcript shows, flagging a mismatch with the recorded assignment."""
    if record is None or entry["actor"] not in {"Planner", "Architect", "Coder", "Reviewer"}:
        return {}
    model, effort = record.get("message", {}).get("model"), record.get("effort")
    if not model and not effort:
        return {}
    observed = {key: value for key, value in (("model", model), ("effort", effort)) if value}
    payload = next((entry[key] for key in WRAPPER_KEYS if key in entry), entry.get("details") or {})
    accepted = state.assignment(state.config, entry["actor"], payload.get("context") or payload.get("invocation"))["assignment"] or {}
    notes = []
    if model and accepted.get("model") and accepted["model"] not in model:
        notes.append(f"observed model {model}, recorded {accepted['model']}")
    if effort and accepted.get("reasoning_effort") and effort != accepted["reasoning_effort"]:
        notes.append(f"observed effort {effort}, recorded {accepted['reasoning_effort']}")
    return {"observed": observed, **({"capability_note": "; ".join(notes)} if notes else {})}


def summary(candidate, source, record=None):
    state = replay(candidate)
    entry = candidate["history"][-1]
    out = {"recorded": {"event_id": entry["id"], "event": entry["event"], "actor": entry["actor"]},
           "status": candidate["status"], "workflow_action": state.next_action(), "source": source}
    payload = next((entry[key] for key in WRAPPER_KEYS if key in entry), entry.get("details") or {})
    if "accepted" in payload:
        issues = payload.get("issue_details") or {}
        out["accepted"] = payload["accepted"]
        out["findings"] = [{"id": f["id"], "severity": severity, "title": title(f)}
                           for severity in ("must_fix", "should_fix") for f in issues.get(severity, [])]
        out["nits"] = len(issues.get("nit", []))
    if payload.get("questions"):
        out["questions"] = payload["questions"]
    if payload.get("blockers"):
        out["blockers"] = [{"id": b.get("id"), "reason": b.get("reason")} for b in payload["blockers"]]
    out.update(observed_capability(state, entry, record))
    return out


def record_return(args):
    record = None
    if args.stdin:
        value, source = read_inline(), "stdin"
    else:
        path = Path(args.transcript) if args.transcript else find_transcript(args.agent_id)
        text, record = select_report(read_records(path))
        value, source = parse_report(text), "transcript"
    log_path = Path(args.log)
    log = json.loads(log_path.read_bytes().decode("utf-8-sig"))
    duplicate = already_recorded(log, value)
    if duplicate:
        raise RecorderError("already_recorded", f"this return is already recorded as event {duplicate}; nothing was written")
    if args.coordination:
        candidate = append_entry(log_path, coordination_entry(log, value), args.workspace)
    else:
        candidate = record_handoff(log_path, value, args.workspace)
    return summary(candidate, source, record)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    record = commands.add_parser("record-return", help="Record a role's actual return")
    record.add_argument("--log", required=True, help="Authoritative task_log.json")
    origin = record.add_mutually_exclusive_group(required=True)
    origin.add_argument("--agent-id", help="Read the return from this agent's transcript in the current session")
    origin.add_argument("--transcript", help="Read the return from this transcript file")
    origin.add_argument("--stdin", action="store_true", help="Read unaltered inline JSON from stdin")
    record.add_argument("--coordination", action="store_true", help="Record a Coder coordination report as coding-updated")
    record.add_argument("--workspace", help="Consumer root for workspace checks")
    entry = commands.add_parser("append-entry", help="Record one Orchestrator-authored entry read from stdin")
    entry.add_argument("--log", required=True, help="Authoritative task_log.json")
    entry.add_argument("--workspace", help="Consumer root for workspace checks")
    args = parser.parse_args(argv)
    try:
        if args.command == "record-return":
            result = record_return(args)
        else:
            value = json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))
            result = summary(append_entry(args.log, value, args.workspace), "orchestrator")
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValidationError, ValueError, OSError) as exc:
        print(f"INVALID: {exc}".encode("ascii", "backslashreplace").decode("ascii"), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
