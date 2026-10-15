#!/usr/bin/env python3
"""Record Orchestrator Flow task-log entries in Claude Code.

record-return  Record a role's actual return, read from its subagent transcript by agent ID (or an
               explicit transcript path, or unaltered inline JSON on stdin). Wrappers go through the
               shared record_handoff; a Coder coordination report is recorded as coding-updated.
append-entry   Record one Orchestrator-authored entry ({actor, requestor, event, details}) from stdin.
find-agent     Find a lead's agent ID from the feature and invocation lines its start prompt carries.

The writers validate the candidate log with the shared replay before writing, read the written log
back, and print a compact JSON summary. find-agent is read-only. None commits, pushes nor dispatches agents.
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
RETURN_EVENTS = {"Planner": {"spec-updated"}, "Architect": {"spec-reviewed"}, "Reviewer": {"code-reviewed"},
                 "Coder": {"coding-complete", "coding-phase-complete", "coding-updated"}}
RUN_ORIGINS = {"coordinator", "peer"}
# Notification text is XML-escaped and control tags may be neutralized; such text is not the original return.
ALTERED_INLINE = re.compile(r"\[harness:|&(?:lt|gt|amp|quot);|<\\[A-Za-z]")
AGENT_ID = re.compile(r"[A-Za-z0-9_-]+")
FEATURE = re.compile(r"[a-z0-9][a-z0-9.-]*")
INVOCATION = re.compile(r"[1-9][0-9]*/(Planner|Architect|Coder|Reviewer)/[1-9][0-9]*")


class RecorderError(ValidationError):
    def __init__(self, category, message):
        self.category = category
        super().__init__(f"{category}: {message}")


def config_dir():
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")


def project_dirs(session_id=None):
    """Return this session's ID and the project folders that hold it."""
    session = session_id or os.environ.get("CLAUDE_CODE_SESSION_ID")
    if not session:
        raise RecorderError("transcript_unavailable", "CLAUDE_CODE_SESSION_ID is not set; pass --transcript")
    projects = config_dir() / "projects"
    return session, sorted({p.parent for p in projects.glob(f"*/{session}")} | {p.parent for p in projects.glob(f"*/{session}.jsonl")})


def find_transcript(agent_id, session_id=None):
    """Locate agent-<id>.jsonl in this session, else in another session of the same project."""
    require(AGENT_ID.fullmatch(agent_id or ""), "Agent IDs contain only letters, digits, '-' and '_'")
    session, projects = project_dirs(session_id)
    name = f"agent-{agent_id}.jsonl"
    for project in projects:
        direct = project / session / "subagents" / name
        if direct.is_file():
            return direct
    # A resumed session keeps its ID, but an agent can still belong to another session of this project.
    matches = sorted({match for project in projects for match in project.glob(f"*/subagents/{name}")})
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


def prompt_text(record):
    content = record["message"]["content"]
    return content if isinstance(content, str) else "\n".join(b.get("text", "") for b in blocks(record) if b.get("type") == "text")


def starts_run(record):
    """A run starts at a user prompt or at a message from the coordinator or a peer; harness prompts do not."""
    if record["type"] != "user":
        return False
    if record.get("isMeta"):
        origin = record.get("origin")
        return isinstance(origin, dict) and origin.get("kind") in RUN_ORIGINS
    return isinstance(record["message"]["content"], str) or not any(b.get("type") == "tool_result" for b in blocks(record))


def harness_prompt(record):
    return record["type"] == "user" and record.get("isMeta") and not isinstance(record.get("origin"), dict)


def delivered(result):
    content = result.get("content")
    text = content if isinstance(content, str) else "".join(b.get("text", "") for b in content or [] if isinstance(b, dict))
    try:
        return json.loads(text).get("success") is True
    except (ValueError, AttributeError):
        return "delivered" in text.lower()


def continues_after_limit(run, start):
    """True when the final message continues text that stopped at the output limit."""
    for record in reversed(run[:start]):
        if harness_prompt(record):
            continue
        if record["type"] == "user" or any(b.get("type") == "tool_use" for b in blocks(record)):
            return False
        if record["message"].get("stop_reason") == "max_tokens":
            return True
    return False


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
            raise RecorderError("report_not_delivered", "Claude Code did not deliver the latest handback; ask the same agent to deliver it again")
        report = (handback.get("input") or {}).get("message")
        if not isinstance(report, str):
            raise RecorderError("transcript_layout_changed", "the handback has no message text")
        return report, run[index]
    assistant = [index for index, record in enumerate(run) if record["type"] == "assistant"]
    if not assistant or any(record["type"] == "user" for record in run[assistant[-1] + 1:]):
        raise RecorderError("no_completed_report", "the latest run has not finished")
    message_id = run[assistant[-1]]["message"].get("id")
    group = [i for i in assistant if message_id and run[i]["message"].get("id") == message_id] or [assistant[-1]]
    final = [run[i] for i in group]
    parts = [b for record in final for b in blocks(record)]
    if any(b.get("type") == "tool_use" for b in parts):
        raise RecorderError("no_completed_report", "the latest run ends with a tool call")
    stop = final[-1]["message"].get("stop_reason")
    if stop == "max_tokens" or continues_after_limit(run, group[0]):
        raise RecorderError("report_truncated", "the report reached the output limit; ask the same agent to return the complete "
                                                "wrapper in one message")
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
        raise RecorderError("inline_text_altered", f"inline text contains {altered.group(0)!r}, which completion notices introduce "
                                                   "when they escape or neutralize text (a literal one in the wrapper is refused "
                                                   "too); record from the transcript or ask the user")
    return parse_report(text)


def payload(entry):
    return next((entry[key] for key in WRAPPER_KEYS if key in entry), entry.get("details"))


def already_recorded(log, value):
    """Compare a return only with its lead's latest recorded return, so a later identical report still records."""
    invocation = value.get("context") or value.get("invocation")
    role = invocation.get("role") if isinstance(invocation, dict) else None
    latest = next((entry for entry in reversed(log["history"]) if entry["actor"] == role
                   and entry["event"] in RETURN_EVENTS.get(role, ())), None)
    return latest["id"] if latest and json_values_equal(payload(latest), value) else None


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
    if record is None or entry["actor"] not in RETURN_EVENTS:
        return {}
    model, effort = record.get("message", {}).get("model"), record.get("effort")
    if not model and not effort:
        return {}
    observed = {key: value for key, value in (("model", model), ("effort", effort)) if value}
    returned = payload(entry) or {}
    accepted = state.assignment(state.config, entry["actor"], returned.get("context") or returned.get("invocation"))["assignment"] or {}
    notes = []
    if model and accepted.get("model") and accepted["model"] not in model:
        notes.append(f"observed model {model}, recorded {accepted['model']}")
    if effort and accepted.get("reasoning_effort") and effort != accepted["reasoning_effort"]:
        notes.append(f"observed effort {effort}, recorded {accepted['reasoning_effort']}")
    return {"observed": observed, **({"capability_note": "; ".join(notes)} if notes else {})}


def summary(candidate, source, record=None, agent_id=None):
    state = replay(candidate)
    entry = candidate["history"][-1]
    out = {"recorded": {"event_id": entry["id"], "event": entry["event"], "actor": entry["actor"]},
           "status": candidate["status"], "workflow_action": state.next_action(), "source": source}
    if agent_id:
        out["agent_id"] = agent_id
    returned = payload(entry) or {}
    if "accepted" in returned:
        issues = returned.get("issue_details") or {}
        out["accepted"] = returned["accepted"]
        out["findings"] = [{"id": f["id"], "severity": severity, "title": title(f)}
                           for severity in ("must_fix", "should_fix") for f in issues.get(severity, [])]
        out["nits"] = len(issues.get("nit", []))
    if returned.get("questions"):
        out["questions"] = returned["questions"]
    if returned.get("blockers"):
        out["blockers"] = [{"id": b.get("id"), "reason": b.get("reason")} for b in returned["blockers"]]
    out.update(observed_capability(state, entry, record))
    return out


def record_return(args):
    record, agent_id = None, args.agent_id
    if args.stdin:
        value, source = read_inline(), "stdin"
    else:
        path = Path(args.transcript) if args.transcript else find_transcript(args.agent_id)
        text, record = select_report(read_records(path))
        value, source = parse_report(text), "transcript"
        agent_id = agent_id or record.get("agentId")
    log_path = Path(args.log)
    log = json.loads(log_path.read_bytes().decode("utf-8-sig"))
    duplicate = already_recorded(log, value)
    if duplicate:
        raise RecorderError("already_recorded", f"this return is already recorded as event {duplicate}; nothing was written")
    if "invocation" in value and "context" not in value:
        candidate = append_entry(log_path, coordination_entry(log, value), args.workspace)
    else:
        candidate = record_handoff(log_path, value, args.workspace)
    return summary(candidate, source, record, agent_id)


def first_prompt(path):
    """Return the first prompt record of a transcript without reading the rest of the file."""
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                return None
            if isinstance(record, dict) and record.get("type") == "user" and not record.get("isMeta") \
                    and isinstance(record.get("message"), dict) and isinstance(record["message"].get("content"), (str, list)):
                return record
    return None


def find_agents(feature, invocation, session_id=None):
    """Lead agents whose start prompt carries this feature and invocation, newest first."""
    require(FEATURE.fullmatch(feature or ""), "Feature names are lowercase identifiers separated by hyphens or dots")
    require(INVOCATION.fullmatch(invocation or ""), "Invocations look like <trigger>/<Role>/<attempt>, for example 12/Coder/1")
    agent_type = "flow-" + invocation.split("/")[1].lower()
    markers = {f"Orchestrator-Feature: {feature}", f"Orchestrator-Invocation: {invocation}"}
    session, projects = project_dirs(session_id)
    paths = [p for project in projects for p in sorted((project / session / "subagents").glob("agent-*.jsonl"))]
    paths += [p for project in projects for p in sorted(project.glob("*/subagents/agent-*.jsonl")) if p not in paths]
    matches = []
    for path in paths:
        meta = path.with_name(path.name[:-len(".jsonl")] + ".meta.json")
        try:
            declared = json.loads(meta.read_text(encoding="utf-8")).get("agentType") if meta.is_file() else None
        except (OSError, ValueError):
            declared = None
        if declared and declared != agent_type:
            continue
        prompt = first_prompt(path)
        if prompt and markers <= {line.strip() for line in prompt_text(prompt).splitlines()}:
            matches.append({"agent_id": path.name[len("agent-"):-len(".jsonl")], "session_id": path.parent.parent.name,
                            "started": prompt.get("timestamp"), "agent_type": declared or agent_type})
    return sorted(matches, key=lambda match: match["started"] or "", reverse=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    record = commands.add_parser("record-return", help="Record a role's actual return")
    record.add_argument("--log", required=True, help="Authoritative task_log.json")
    origin = record.add_mutually_exclusive_group(required=True)
    origin.add_argument("--agent-id", help="Read the return from this agent's transcript in the current session")
    origin.add_argument("--transcript", help="Read the return from this transcript file")
    origin.add_argument("--stdin", action="store_true", help="Read unaltered inline JSON from stdin")
    record.add_argument("--workspace", help="Consumer root for workspace checks")
    entry = commands.add_parser("append-entry", help="Record one Orchestrator-authored entry read from stdin")
    entry.add_argument("--log", required=True, help="Authoritative task_log.json")
    entry.add_argument("--workspace", help="Consumer root for workspace checks")
    find = commands.add_parser("find-agent", help="Find a lead's agent ID from its start prompt (read-only)")
    find.add_argument("--feature", required=True, help="Feature name, as in Orchestrator-Feature")
    find.add_argument("--invocation", required=True, help="<trigger>/<Role>/<attempt>, as in Orchestrator-Invocation")
    args = parser.parse_args(argv)
    try:
        if args.command == "record-return":
            result = record_return(args)
        elif args.command == "append-entry":
            value = json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))
            result = summary(append_entry(args.log, value, args.workspace), "orchestrator")
        else:
            result = {"matches": find_agents(args.feature, args.invocation)}
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValidationError, ValueError, OSError) as exc:
        print(f"INVALID: {exc}".encode("ascii", "backslashreplace").decode("ascii"), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
