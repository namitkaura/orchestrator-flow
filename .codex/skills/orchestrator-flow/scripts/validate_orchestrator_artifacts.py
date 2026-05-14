#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path
from typing import Optional

FEATURE_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FEATURE_DIR_RE = re.compile(r"^\.docs/specs/[a-z0-9]+(?:[.-][a-z0-9]+)*$")
REQUIREMENTS_REF_RE = re.compile(r"^\.docs/specs/.+/requirements\.md$")
DESIGN_REF_RE = re.compile(r"^\.docs/specs/.+/design\.md$")
TASKS_REF_RE = re.compile(r"^\.docs/specs/.+/tasks\.md$")
TASK_LOG_REF_RE = re.compile(r"^\.docs/specs/.+/task_log\.json$")
TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
POS_INT_STR_RE = re.compile(r"^[1-9][0-9]*$")

STATUS_ENUM = {
    "spec_in_progress",
    "spec_created",
    "spec_updated",
    "spec_in_review",
    "spec_approved",
    "spec_conditionally_approved",
    "spec_changes_requested",
    "coding_in_progress",
    "coding_complete",
    "blocked",
    "code_in_review",
    "code_approved",
    "code_conditionally_approved",
    "code_changes_requested",
    "implementation_complete",
}

ACTOR_ENUM = {"User", "Planner", "Architect", "Coder", "Reviewer", "Orchestrator"}
REQUESTOR_ENUM = {"User", "Planner", "Architect", "Coder", "Reviewer"}
EVENT_ENUM = {
    "spec-creation-started",
    "spec-revision-started",
    "spec-created",
    "spec-updated",
    "spec-review-started",
    "spec-reviewed",
    "spec-approved-with-justifications",
    "spec-approved-by-user",
    "coding-started",
    "coding-revision-started",
    "coding-complete",
    "code-review-started",
    "code-reviewed",
    "code-approved-with-justifications",
    "code-approved-by-user",
    "user-change-requested",
    "implementation-complete",
    "subagent-error",
}

ACCEPTED_ENUM = {"true", "false", "conditional"}
TEST_STATUS_ENUM = {"pass", "fail", "not_run", "skipped"}


class ValidationError(Exception):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def expect(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def expect_type(value, expected_type, path: str) -> None:
    expect(isinstance(value, expected_type), f"{path}: expected {expected_type.__name__}")


def expect_string(value, path: str, *, non_empty: bool = False, pattern: Optional[re.Pattern] = None) -> None:
    expect_type(value, str, path)
    if non_empty:
        expect(value.strip() != "", f"{path}: must be non-empty")
    if pattern is not None:
        expect(pattern.match(value) is not None, f"{path}: invalid format")


def expect_keys_exact(obj: dict, allowed: set[str], path: str) -> None:
    extra = sorted(set(obj.keys()) - allowed)
    expect(not extra, f"{path}: unknown fields: {', '.join(extra)}")


def validate_issue(value: dict, path: str) -> None:
    expect_type(value, dict, path)
    allowed = {"file", "description", "rationale"}
    expect_keys_exact(value, allowed, path)
    for field in sorted(allowed):
        expect(field in value, f"{path}.{field}: missing")
    expect_string(value["file"], f"{path}.file", non_empty=True)
    expect_string(value["description"], f"{path}.description", non_empty=True)
    expect_string(value["rationale"], f"{path}.rationale", non_empty=True)


def validate_issue_details(value: dict, path: str) -> None:
    expect_type(value, dict, path)
    allowed = {"must_fix", "should_fix", "nit"}
    expect_keys_exact(value, allowed, path)
    for field in ("must_fix", "should_fix", "nit"):
        expect(field in value, f"{path}.{field}: missing")
        entries = value[field]
        expect_type(entries, list, f"{path}.{field}")
        for index, issue in enumerate(entries):
            validate_issue(issue, f"{path}.{field}[{index}]")


def validate_test_result(value: dict, path: str) -> None:
    expect_type(value, dict, path)
    allowed = {"status", "details"}
    expect_keys_exact(value, allowed, path)
    expect("status" in value, f"{path}.status: missing")
    expect("details" in value, f"{path}.details: missing")
    expect_string(value["status"], f"{path}.status", non_empty=True)
    expect(value["status"] in TEST_STATUS_ENUM, f"{path}.status: invalid value")
    expect_string(value["details"], f"{path}.details", non_empty=True)


def validate_test_results(value: dict, path: str) -> None:
    expect_type(value, dict, path)
    allowed = {"unit_tests", "integration_tests"}
    expect_keys_exact(value, allowed, path)
    for field in ("unit_tests", "integration_tests"):
        expect(field in value, f"{path}.{field}: missing")
        validate_test_result(value[field], f"{path}.{field}")


def validate_spec_change_wrapper(wrapper: dict, path: str) -> None:
    expect_type(wrapper, dict, path)
    allowed = {
        "feature",
        "feature_dir",
        "requirements_ref",
        "design_ref",
        "tasks_ref",
        "notes",
        "user_request",
    }
    expect_keys_exact(wrapper, allowed, path)
    for field in sorted(allowed):
        expect(field in wrapper, f"{path}.{field}: missing")

    expect_string(wrapper["feature"], f"{path}.feature", non_empty=True, pattern=FEATURE_RE)
    expect_string(wrapper["feature_dir"], f"{path}.feature_dir", non_empty=True, pattern=FEATURE_DIR_RE)
    expect_string(
        wrapper["requirements_ref"],
        f"{path}.requirements_ref",
        non_empty=True,
        pattern=REQUIREMENTS_REF_RE,
    )
    expect_string(wrapper["design_ref"], f"{path}.design_ref", non_empty=True, pattern=DESIGN_REF_RE)
    expect_string(wrapper["tasks_ref"], f"{path}.tasks_ref", non_empty=True, pattern=TASKS_REF_RE)
    expect_string(wrapper["notes"], f"{path}.notes", non_empty=True)

    user_request = wrapper["user_request"]
    expect_type(user_request, dict, f"{path}.user_request")
    expect_keys_exact(user_request, {"original_request", "additional_context"}, f"{path}.user_request")
    expect("original_request" in user_request, f"{path}.user_request.original_request: missing")
    expect_string(user_request["original_request"], f"{path}.user_request.original_request", non_empty=True)
    if "additional_context" in user_request:
        expect_string(user_request["additional_context"], f"{path}.user_request.additional_context")


def validate_spec_review_wrapper(wrapper: dict, path: str) -> None:
    expect_type(wrapper, dict, path)
    allowed = {"accepted", "issue_details", "notes"}
    expect_keys_exact(wrapper, allowed, path)
    for field in sorted(allowed):
        expect(field in wrapper, f"{path}.{field}: missing")
    expect_string(wrapper["accepted"], f"{path}.accepted", non_empty=True)
    expect(wrapper["accepted"] in ACCEPTED_ENUM, f"{path}.accepted: invalid value")
    validate_issue_details(wrapper["issue_details"], f"{path}.issue_details")
    expect_string(wrapper["notes"], f"{path}.notes", non_empty=True)


def validate_change_wrapper(wrapper: dict, path: str) -> None:
    expect_type(wrapper, dict, path)
    allowed = {
        "changed_files",
        "new_files",
        "deleted_files",
        "cli_runs",
        "test_results",
        "implementation_details",
        "notes",
    }
    expect_keys_exact(wrapper, allowed, path)
    for field in sorted(allowed):
        expect(field in wrapper, f"{path}.{field}: missing")

    for list_field in ("changed_files", "new_files", "deleted_files", "cli_runs"):
        values = wrapper[list_field]
        expect_type(values, list, f"{path}.{list_field}")
        for index, item in enumerate(values):
            expect_string(item, f"{path}.{list_field}[{index}]", non_empty=True)

    validate_test_results(wrapper["test_results"], f"{path}.test_results")
    expect_string(wrapper["implementation_details"], f"{path}.implementation_details", non_empty=True)
    expect_string(wrapper["notes"], f"{path}.notes")


def validate_review_wrapper(wrapper: dict, path: str) -> None:
    expect_type(wrapper, dict, path)
    allowed = {"accepted", "issue_details", "test_results", "notes"}
    expect_keys_exact(wrapper, allowed, path)
    for field in sorted(allowed):
        expect(field in wrapper, f"{path}.{field}: missing")

    expect_string(wrapper["accepted"], f"{path}.accepted", non_empty=True)
    expect(wrapper["accepted"] in ACCEPTED_ENUM, f"{path}.accepted: invalid value")
    validate_issue_details(wrapper["issue_details"], f"{path}.issue_details")
    validate_test_results(wrapper["test_results"], f"{path}.test_results")
    expect_string(wrapper["notes"], f"{path}.notes", non_empty=True)


def validate_task_log(task_log: dict, path: str) -> None:
    expect_type(task_log, dict, path)
    allowed = {
        "feature",
        "feature_dir",
        "requirements_ref",
        "design_ref",
        "tasks_ref",
        "task_log_ref",
        "status",
        "history",
    }
    expect_keys_exact(task_log, allowed, path)
    for field in sorted(allowed):
        expect(field in task_log, f"{path}.{field}: missing")

    expect_string(task_log["feature"], f"{path}.feature", non_empty=True, pattern=FEATURE_RE)
    expect_string(task_log["feature_dir"], f"{path}.feature_dir", non_empty=True, pattern=FEATURE_DIR_RE)
    expect_string(
        task_log["requirements_ref"],
        f"{path}.requirements_ref",
        non_empty=True,
        pattern=REQUIREMENTS_REF_RE,
    )
    expect_string(task_log["design_ref"], f"{path}.design_ref", non_empty=True, pattern=DESIGN_REF_RE)
    expect_string(task_log["tasks_ref"], f"{path}.tasks_ref", non_empty=True, pattern=TASKS_REF_RE)
    expect_string(task_log["task_log_ref"], f"{path}.task_log_ref", non_empty=True, pattern=TASK_LOG_REF_RE)

    expect_string(task_log["status"], f"{path}.status", non_empty=True)
    expect(task_log["status"] in STATUS_ENUM, f"{path}.status: invalid value")

    history = task_log["history"]
    expect_type(history, list, f"{path}.history")
    expected_id = 1

    for index, entry in enumerate(history):
        entry_path = f"{path}.history[{index}]"
        expect_type(entry, dict, entry_path)
        allowed_entry = {
            "timestamp",
            "id",
            "actor",
            "requestor",
            "event",
            "details",
            "spec_change_wrapper",
            "spec_review_wrapper",
            "change_wrapper",
            "review_wrapper",
        }
        expect_keys_exact(entry, allowed_entry, entry_path)

        for required_field in ("timestamp", "id", "actor", "requestor", "event"):
            expect(required_field in entry, f"{entry_path}.{required_field}: missing")

        expect_string(entry["timestamp"], f"{entry_path}.timestamp", non_empty=True, pattern=TIMESTAMP_RE)
        expect_string(entry["id"], f"{entry_path}.id", non_empty=True, pattern=POS_INT_STR_RE)
        parsed_id = int(entry["id"])
        expect(parsed_id == expected_id, f"{entry_path}.id: expected '{expected_id}', found '{entry['id']}'")
        expected_id += 1

        expect_string(entry["actor"], f"{entry_path}.actor", non_empty=True)
        expect(entry["actor"] in ACTOR_ENUM, f"{entry_path}.actor: invalid value")

        expect_string(entry["requestor"], f"{entry_path}.requestor", non_empty=True)
        expect(entry["requestor"] in REQUESTOR_ENUM, f"{entry_path}.requestor: invalid value")

        expect_string(entry["event"], f"{entry_path}.event", non_empty=True)
        expect(entry["event"] in EVENT_ENUM, f"{entry_path}.event: invalid value")

        payload_fields = [
            field
            for field in (
                "details",
                "spec_change_wrapper",
                "spec_review_wrapper",
                "change_wrapper",
                "review_wrapper",
            )
            if field in entry
        ]
        expect(
            len(payload_fields) == 1,
            f"{entry_path}: must contain exactly one payload field, found {len(payload_fields)}",
        )

        if "details" in entry:
            expect_string(entry["details"], f"{entry_path}.details")
        if "spec_change_wrapper" in entry:
            validate_spec_change_wrapper(entry["spec_change_wrapper"], f"{entry_path}.spec_change_wrapper")
        if "spec_review_wrapper" in entry:
            validate_spec_review_wrapper(entry["spec_review_wrapper"], f"{entry_path}.spec_review_wrapper")
        if "change_wrapper" in entry:
            validate_change_wrapper(entry["change_wrapper"], f"{entry_path}.change_wrapper")
        if "review_wrapper" in entry:
            validate_review_wrapper(entry["review_wrapper"], f"{entry_path}.review_wrapper")


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path}: {exc}") from exc


def usage() -> str:
    return (
        "Usage:\n"
        "  validate_orchestrator_artifacts.py task-log <path>\n"
        "  validate_orchestrator_artifacts.py spec-change-wrapper <path>\n"
        "  validate_orchestrator_artifacts.py spec-review-wrapper <path>\n"
        "  validate_orchestrator_artifacts.py change-wrapper <path>\n"
        "  validate_orchestrator_artifacts.py review-wrapper <path>"
    )


def main() -> int:
    if len(sys.argv) != 3:
        print(usage(), file=sys.stderr)
        return 2

    mode = sys.argv[1]
    file_path = Path(sys.argv[2])
    payload = load_json(file_path)

    try:
        if mode == "task-log":
            validate_task_log(payload, mode)
        elif mode == "spec-change-wrapper":
            validate_spec_change_wrapper(payload, mode)
        elif mode == "spec-review-wrapper":
            validate_spec_review_wrapper(payload, mode)
        elif mode == "change-wrapper":
            validate_change_wrapper(payload, mode)
        elif mode == "review-wrapper":
            validate_review_wrapper(payload, mode)
        else:
            print(usage(), file=sys.stderr)
            return 2
    except ValidationError as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1

    print(f"VALID: {mode} -> {file_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
