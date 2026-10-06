"""Codex artifact validation using local schemas and the skill's VERSION symlink."""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
BUNDLE = Path(__file__).resolve().parent.parent

try:
    from jsonschema import Draft202012Validator, FormatChecker
    from jsonschema.exceptions import best_match
    from referencing import Registry, Resource
except ImportError as exc:
    raise SystemExit("Install validation dependencies: python -m pip install -r <workflow>/scripts/requirements.txt") from exc

SCHEMAS = {
    "common": "common.schema.json",
    "task-log": "task_log_schema.json",
    "repository-config": "repository_config.schema.json",
    **{name: f"wrappers/{name.replace('-', '_')}.schema.json" for name in (
        "spec-change-wrapper", "spec-review-wrapper", "change-wrapper", "review-wrapper")},
}


class ValidationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def workflow_version(bundle=BUNDLE):
    version = Path(bundle) / "VERSION"
    require(version.is_symlink() and not version.readlink().is_absolute() and version.is_file(),
            f"Workflow setup: repair the real relative VERSION symlink in {bundle}")
    return version.read_text(encoding="utf-8").strip()


def version_tuple(value):
    require(isinstance(value, str) and re.fullmatch(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", value),
            "Missing or invalid workflow_version; pre-2.0 logs require separately directed work")
    return tuple(map(int, value.split(".")))


def check_compatibility(writer, reader=None):
    written, current = version_tuple(writer), version_tuple(reader or workflow_version())
    require((2, 0, 0) <= written <= current and written[0] == current[0] == 2,
            f"Unsupported workflow version {writer!r} for reader {reader or workflow_version()}; stop before mutation")


@lru_cache(maxsize=4)
def load_schemas(bundle=BUNDLE):
    schemas = {name: json.loads((Path(bundle) / "references" / filename).read_text(encoding="utf-8"))
               for name, filename in SCHEMAS.items()}
    for value in schemas.values():
        Draft202012Validator.check_schema(value)
    registry = Registry().with_resources((value["$id"], Resource.from_contents(value)) for value in schemas.values())
    return schemas, registry


def validate_shape(kind, value, bundle=BUNDLE):
    schemas, registry = load_schemas(bundle)
    validator = Draft202012Validator(schemas[kind], registry=registry, format_checker=FormatChecker())
    error = best_match(validator.iter_errors(value))
    if error is not None:
        location = ".".join(map(str, error.absolute_path)) or "$"
        raise ValidationError(f"{kind} {location}: {error.message}")


def validate_capability(config):
    capability = config["capability"]
    special = any(assignment["model"] == "platform_default" or
                  assignment["reasoning_effort"] in {"platform_default", "not_supported"}
                  for assignment in capability["roles"].values())
    require(not special or capability["acknowledged_limitations"],
            "Native defaults/unsupported effort require acknowledged_limitations in feature configuration")
    require(all(a["model"] != "not_supported" for a in capability["roles"].values()),
            "Use platform_default for an acknowledged native model default, not not_supported")


def all_findings(wrapper):
    return {finding["id"]: {**finding, "severity": severity}
            for severity, findings in wrapper["issue_details"].items() for finding in findings}


def validate_wrapper(kind, value):
    validate_shape(kind, value)
    artifacts = value.get("artifacts", value.get("reviewed_artifacts"))
    if "output_kind" in value and value["output_kind"] == "consolidated" or "reviewed_artifacts" in value:
        require(all(artifacts.values()), "Consolidated/review output requires all three artifacts")
    if kind == "spec-change-wrapper":
        for name, artifact in artifacts.items():
            require(value[name + "_ref"] == (artifact["ref"] if artifact else None), f"{name}_ref disagrees with artifact snapshot")
    changes = value.get("artifact_changes", [])
    require(len({c["artifact"] for c in changes}) == len(changes), "Duplicate artifact change")
    for change in changes:
        old = change["previous_version"] or 0
        require(change["current_version"] == old + 1, "Content versions increase once per logical update")
        require(artifacts[change["artifact"]] and artifacts[change["artifact"]]["version"] == old + 1,
                "Artifact snapshot disagrees with version change")
    if kind == "change-wrapper":
        progress = {task["task_id"]: task for task in value["task_progress"]}
        require(len(progress) == len(value["task_progress"]), "Duplicate task progress identity")
        blocked = {task_id for blocker in value["blockers"] for task_id in blocker["task_ids"]}
        independent = {task_id for blocker in value["blockers"] for task_id in blocker["independent_task_ids"]}
        require((blocked | independent).issubset(progress), "Blocker reports must include progress for referenced tasks")
        require(not blocked.intersection(independent), "A blocked task cannot also be independent work")
        require(all(progress[task_id]["status"] in {"pending", "in_progress"} for task_id in independent),
                "Independent work must still be pending or in progress")
    if "issue_details" in value:
        findings = all_findings(value)
        require(len(findings) == sum(map(len, value["issue_details"].values())), "Duplicate finding ID")
        if value["context"] is not None or value["review_kind"] == "initial":
            require((value["review_kind"] == "initial") == (value["prior_review_ref"] is None), "Review kind/prior reference mismatch")
        if value["review_kind"] == "initial" or value["assurance_level"] == "maximum":
            require(value["review_scope"] == "full", "Initial and Maximum reviews require complete coverage")
        if value["review_kind"] == "follow_up":
            require(value["repair_class"] is not None, "Follow-up requires repair class")
            if value["repair_class"] == "architectural_systemic":
                require(value["review_scope"] == "full", "Architectural/systemic changes require full review")
            if value["assurance_level"] == "standard" and value["repair_class"] == "bounded_correctness":
                require(value["review_scope"] in {"affected", "full"}, "Standard correctness repair includes neighboring contracts")
        for report in value["evidence"]:
            if value["assurance_level"] == "maximum":
                require(report["freshness"] in {"new", "revalidated", "incomplete"}, "Maximum cannot merely reuse decision-critical evidence")
        if value["context"] is None:
            # Standalone user decisions are supplied directly. Embedding the same
            # result in a log later requires real historical authority in replay.
            responses = {d["finding_id"]: d for d in value["dispositions"]}
            require(len(responses) == len(value["dispositions"]) and set(responses).issubset(findings),
                    "Standalone dispositions must identify current unique findings")
            unresolved = []
            for fid, finding in findings.items():
                response = responses.get(fid, {})
                settled = response.get("decision") in {"defer", "accept_limitation", "reject"}
                permitted = response.get("authority") == "user" or (finding["severity"] != "must_fix"
                    and value["assurance_level"] != "maximum" and response.get("decision") in {"defer", "accept_limitation"})
                if not settled or not permitted:
                    unresolved.append(finding)
            expected = "false" if any(f["severity"] == "must_fix" for f in unresolved) else "conditional" if unresolved else "true"
            require(value["accepted"] == expected, f"Standalone acceptance must be {expected} under supplied decisions")
    return value
