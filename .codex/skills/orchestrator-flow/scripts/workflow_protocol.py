"""Pure v2 history validation/replay; never dispatches agents or changes files/Git."""
from __future__ import annotations

from copy import deepcopy
import re

from workflow_artifacts import (ValidationError, all_findings, check_compatibility,
                                require, validate_capability, validate_shape, validate_wrapper)

ARTIFACTS = ("requirements", "design", "tasks")
LEVELS = {"basic": 0, "standard": 1, "maximum": 2}
SETTLED = {"defer", "accept_limitation", "reject"}
WRAPPERS = {"spec-created": "spec_change_wrapper", "spec-updated": "spec_change_wrapper",
            "spec-reviewed": "spec_review_wrapper", "coding-updated": "change_wrapper",
            "coding-complete": "change_wrapper", "code-reviewed": "review_wrapper"}
REFERENCE_EVENTS = {
    "spec_review": {"spec-reviewed"}, "code_review": {"code-reviewed"},
    "approval": {"spec-artifact-approved"}, "authorization": {"user-authorization-recorded"},
    "override": {"user-override"},
}


def check_reference(reference, entries):
    target = entries.get(reference["event_id"])
    require(target is not None, f"Unknown/forward history reference {reference['event_id']}")
    kind = reference["kind"]
    if kind in REFERENCE_EVENTS:
        require(target["event"] in REFERENCE_EVENTS[kind], f"History {target['id']} is not {kind}")
    elif kind.endswith("_wrapper"):
        require(kind in target, f"History {target['id']} does not contain {kind}")
    return target


def check_references(value, entries):
    if isinstance(value, dict):
        if set(value) == {"event_id", "kind"}:
            check_reference(value, entries)
        else:
            for child in value.values():
                check_references(child, entries)
    elif isinstance(value, list):
        for child in value:
            check_references(child, entries)
    elif isinstance(value, str):
        # Supported text: [wrapper from] history entry/entries 1, 2 and 3;
        # spec/code review event/events 4, 5. Ordinary numbers are not references.
        pattern = (r"(?:(spec_change_wrapper|spec_review_wrapper|change_wrapper|review_wrapper)\s+(?:from\s+)?)?"
                   r"(?:(history\s+entr(?:y|ies))|((?:spec|code)\s+review\s+events?))\s+"
                   r"([#\"']?\d+[\"']?(?:(?:\s*,\s*|\s+and\s+)[#\"']?\d+[\"']?)*)")
        for match in re.finditer(pattern, value, re.I):
            kind = match[1].lower() if match[1] else (match[3].split()[0].lower() + "_review" if match[3] else "event")
            for number in re.findall(r"\d+", match[4]):
                check_reference({"event_id": number, "kind": kind}, entries)


class Replay:
    def __init__(self, log):
        self.log = log
        self.entries = {}
        self.status = None
        self.config = None
        self.config_ref = None
        self.configurations = {}
        self.artifacts = dict.fromkeys(ARTIFACTS)
        self.produced = {}
        self.approvals = {}
        self.starts = {}
        self.errors = {}
        self.inflight = None
        self.outputs = {}
        self.reviews = {}
        self.findings = {}
        self.dispositions = {}
        self.review_decisions = {}
        self.authorizations = {}
        self.cycles = {"spec": 0, "code": 0}
        self.extra_cycles = {"spec": 0, "code": 0}
        self.repair_pending = {"spec": False, "code": False}
        self.review_runs = {"spec": [], "code": []}
        self.assurance_gaps = set()
        self.scope_epoch = 0
        self.coding_authorization = None
        self.earliest_artifact = "requirements"
        self.spec_handed_off = False
        self.last_error = None
        self.feedback_ref = None
        self.user_revision_pending = False
        self.review_returns = {}

    def pair(self, entry, actor, requestor):
        require(entry["actor"] == actor and entry["requestor"] == requestor,
                f"{entry['event']}: expected actor/requestor {actor}/{requestor}")

    def config_snapshot(self, context):
        require(context is not None, "Embedded output requires orchestration context")
        require(context["configuration_ref"] in self.configurations, "Unknown configuration basis")
        return self.configurations[context["configuration_ref"]]

    def role_recovery_gate(self, context):
        failures = self.errors.get(context["trigger_event_id"], [])
        if not failures:
            return None
        attempt = len(failures) + 1
        decisions = [a for a in self.authorizations.values() if a["kind"] == "external_operation"
                     and a["operation"] == "continue-role" and a["scope"] == context["trigger_event_id"]]
        latest = decisions[-1] if decisions else None
        if latest and latest["decision"] != "granted":
            return "obtain_role_failure_direction"
        directed = latest and attempt <= latest["attempt_ceiling"]
        if latest and not directed:
            return "obtain_role_failure_direction"
        last = failures[-1]
        category = (last.get("helper") or {}).get("category", last["category"])
        if category in {"model_unavailable", "usage_limit"}:
            assigned_role = "helpers" if last.get("helper") else context["role"].lower()
            old = self.configurations[last["invocation"]["configuration_ref"]]["capability"]
            current = self.config["capability"]
            changed = old["platform"] != current["platform"] or old["roles"][assigned_role] != current["roles"][assigned_role]
            if not changed and not directed:
                return "obtain_model_direction"
        if attempt > 3 and not directed:
            return "obtain_role_failure_direction"
        return None

    def context(self, context, role, starting=False, entry=None):
        self.config_snapshot(context)
        require(context["role"] == role, "Invocation role mismatch")
        if starting:
            require(context["trigger_event_id"] == entry["id"] and context["attempt"] == 1,
                    "A new logical invocation uses its start event and attempt 1")
            require(context["configuration_ref"] == self.config_ref, "Invocation must use effective feature configuration")
            self.starts[role] = deepcopy(context)
            self.inflight = role
        else:
            require(role in self.starts, f"No start event for {role}")
            start = self.starts[role]
            require(context["trigger_event_id"] == start["trigger_event_id"], "Output belongs to a different invocation")
            failures = self.errors.get(start["trigger_event_id"], [])
            allowed_attempt = len(failures) + 1
            require(context["attempt"] == allowed_attempt, "Invocation attempt is duplicated or skips recovery")
            if failures:
                require(context["configuration_ref"] == self.config_ref, "Retried work must use effective configuration")
                require(self.role_recovery_gate(context) is None, f"Role retry gate: {self.role_recovery_gate(context)}")
        return context

    def all_approved(self):
        return all(self.artifacts[name] and name in self.approvals for name in ARTIFACTS)

    def apply_artifacts(self, wrapper, entry, coder=False):
        changes = {c["artifact"]: c for c in wrapper["artifact_changes"]}
        for name in ARTIFACTS:
            old, new = self.artifacts[name], wrapper["artifacts"][name]
            change = changes.get(name)
            expected_ref = self.log[name + "_ref"]
            require(new is None or new["ref"] == expected_ref, f"Wrong {name} path")
            if change is None:
                require(new == old, f"Unrecorded change to {name}")
                continue
            require(change["previous_version"] == (old["version"] if old else None), "Stale previous content version")
            if coder:
                require(name == "tasks" and change["change_kind"] == "progress", "Coder may only change task progress")
            else:
                for upstream in ARTIFACTS[:ARTIFACTS.index(name)]:
                    require(upstream in self.approvals, f"Approve {upstream} before changing dependent {name}")
            if change["change_kind"] == "material":
                self.approvals.pop(name, None)
                self.scope_epoch += 1
            elif name in self.approvals:
                require(change["approval_basis_ref"] == {"event_id": self.approvals[name]["event_id"], "kind": "approval"},
                        "Nonmaterial update must cite its preserved approval basis")
            self.artifacts[name] = deepcopy(new)
            self.produced[name] = entry["id"]

    def disposition_allowed(self, finding_id, disposition):
        if disposition["decision"] not in SETTLED:
            return False
        finding = self.findings[finding_id]
        if disposition["authority"] == "user":
            return bool(disposition.get("recorded_user_event"))
        return (finding["severity"] != "must_fix" and self.config["assurance_level"] != "maximum"
                and disposition["decision"] in {"defer", "accept_limitation"})

    def apply_dispositions(self, values, entry, user=False):
        require(len({d["finding_id"] for d in values}) == len(values), "Duplicate disposition")
        for raw in values:
            disposition = deepcopy(raw)
            finding_id = disposition["finding_id"]
            require(finding_id in self.findings, f"Unknown finding {finding_id}")
            old = self.dispositions.get(finding_id)
            if old and self.disposition_allowed(finding_id, old) and disposition["decision"] != old["decision"]:
                require(disposition["decision"] == "reconsider", "Settled disposition requires explicit reconsideration")
            if user:
                require(disposition["authority"] == "user" and disposition["authority_ref"] is None,
                        "A user decision records its own authority, not another person's decision")
                disposition["recorded_user_event"] = entry["id"]
            elif disposition["authority"] == "user":
                reference = disposition["authority_ref"]
                require(reference is not None, "User authority requires its historical decision")
                authority = check_reference(reference, self.entries)
                require(authority["actor"] == "User", "Disposition authority is not a user decision")
                decisions = authority.get("details", {}).get("decisions", [])
                require(any(d["finding_id"] == finding_id and d["decision"] == disposition["decision"] for d in decisions),
                        "Cited user decision does not grant this disposition")
                disposition["recorded_user_event"] = authority["id"]
            else:
                if entry["actor"] in {"Architect", "Reviewer"}:
                    require(old and old["decision"] == disposition["decision"] and old["authority"] == "policy",
                            "Review may confirm a producer disposition, not invent one")
                if old and old["authority"] == "user" and disposition["decision"] in SETTLED:
                    require(disposition["decision"] == old["decision"], "Policy cannot replace the user's selected finding response")
            self.dispositions[finding_id] = disposition

    def open_findings(self, phase):
        return {fid: f for fid, f in self.findings.items() if f["phase"] == phase and not f.get("resolved")
                and not self.disposition_allowed(fid, self.dispositions.get(fid, {"decision": "fix"}))}

    def result(self, phase):
        findings = self.open_findings(phase)
        if any(f["severity"] == "must_fix" for f in findings.values()):
            return "false"
        return "conditional" if findings else "true"

    def result_status(self, phase, accepted):
        return phase + {"false": "_changes_requested", "conditional": "_conditionally_approved", "true": "_approved"}[accepted]

    def stuck(self, phase):
        runs = self.review_runs[phase]
        if len(runs) >= 2 and runs[-1]["must_fix"] and runs[-1]["must_fix"] == runs[-2]["must_fix"] and not runs[-1]["meaningful_change"]:
            return True
        return len(runs) >= 5 and len({r["accepted"] for r in runs[-5:]}) == 1

    def repair_gate(self, phase):
        review_id = self.reviews.get(phase)
        current_decisions = [a for a in self.authorizations.values() if a["kind"] == "repair_cycle"
                             and a["limits"]["phase"] == phase and any(r["event_id"] == review_id for r in a["references"])]
        if current_decisions and current_decisions[-1]["decision"] != "granted":
            return "obtain_repair_cycle_authorization"
        policy = self.config["review_disposition_policy"]
        needs_user = policy == "all_user" or (phase == "spec" and policy == "spec_user_code_auto")
        unresolved = set(self.open_findings(phase))
        if needs_user and not unresolved.issubset(self.review_decisions.get(review_id, set())):
            return "obtain_findings_disposition"
        limits = {"basic": 1, "standard": 2, "maximum": None}
        limit = limits[self.config["assurance_level"]]
        if limit is not None and self.cycles[phase] >= limit + self.extra_cycles[phase]:
            return "obtain_repair_cycle_authorization"
        if self.stuck(phase) and not any(a["kind"] == "repair_cycle" and a["decision"] == "granted"
                                       and any(r["event_id"] == review_id for r in a["references"])
                                       for a in self.authorizations.values()):
            return "obtain_stalled_loop_direction"
        return None

    def check_checks(self, checks):
        for check in checks:
            if check["required"] and check["status"] != "pass":
                reference = check["disposition_ref"]
                require(reference is not None, f"Required check {check['name']} has not passed")
                auth = self.authorizations.get(reference["event_id"], {})
                require(auth.get("decision") == "granted" and auth.get("kind") == "external_operation"
                        and auth.get("operation") == "accept-check-result" and auth.get("scope") == check["name"]
                        and auth.get("scope_epoch") == self.scope_epoch,
                        "Check exception needs explicit authorization for this exact check")

    def append(self, entry):
        event, entry_id, previous = entry["event"], entry["id"], self.status
        require(entry_id == str(len(self.entries) + 1), "History IDs must be contiguous strings starting at 1")
        details = entry.get("details", {})
        check_references(details if details else entry[WRAPPERS[event]], self.entries)
        if not self.entries:
            require(event in {"spec-creation-started", "spec-revision-started"}, "First event must initialize a Planner cycle")
            require("initial_configuration" in details, "Initial event requires accepted configuration")
            self.config = deepcopy(details["initial_configuration"])
            validate_capability(self.config)
            self.config_ref = entry_id
            self.configurations[entry_id] = deepcopy(self.config)
            require(details["branch_context"] == self.log["branch_context"], "Branch context disagrees with initialization")
            require(self.log["branch_context"]["feature_branch"] != self.log["branch_context"]["integration_branch"], "Feature branch must differ from integration target")
        elif "initial_configuration" in details:
            raise ValidationError("Configuration initialization is only valid in the first event")
        if previous == "implementation_complete":
            require(event == "user-authorization-recorded" and details["kind"] == "checkpoint_recovery",
                    "Completed work permits only checkpoint recovery authorization")
        target = previous

        if event in {"spec-creation-started", "spec-revision-started"}:
            if self.entries:
                require(event == "spec-revision-started", "Only one creation-start event is permitted")
                require(previous in {"spec_changes_requested", "spec_conditionally_approved"}, "No spec revision is ready")
                if entry["requestor"] == "Architect":
                    require({"event_id": self.reviews["spec"], "kind": "spec_review"} in details["references"],
                            "Planner repair must cite the triggering Architect review")
                    require(self.repair_gate("spec") is None, f"Spec repair gate: {self.repair_gate('spec')}")
                    self.repair_pending["spec"] = True
                else:
                    require(entry["requestor"] == "User" and self.user_revision_pending, "Revision must follow user change or review disposition")
            self.pair(entry, "Planner", entry["requestor"])
            require(entry["requestor"] in {"User", "Architect"}, "Invalid Planner requestor")
            self.earliest_artifact = details["earliest_artifact"]
            self.context(details["invocation"], "Planner", True, entry)
            self.user_revision_pending = False
            target = "spec_in_progress"

        elif event == "user-change-requested":
            self.pair(entry, "Orchestrator", "User")
            self.earliest_artifact = details["earliest_artifact"]
            self.feedback_ref = entry_id
            # Feedback during either initial drafting or an active revision belongs
            # to that Planner cycle, even after an earlier completed handoff.
            self.user_revision_pending = previous != "spec_in_progress"
            self.inflight = None
            target = "spec_changes_requested" if self.user_revision_pending else "spec_in_progress"

        elif event in {"spec-created", "spec-updated"}:
            require(previous == "spec_in_progress", "Planner output requires a drafting cycle")
            start = self.entries[self.starts["Planner"]["trigger_event_id"]]
            self.pair(entry, "Planner", start["requestor"])
            wrapper = entry["spec_change_wrapper"]
            validate_wrapper("spec-change-wrapper", wrapper)
            self.context(wrapper["context"], "Planner")
            require(wrapper["feature"] == self.log["feature"] and wrapper["feature_dir"] == self.log["feature_dir"], "Planner feature identity mismatch")
            self.apply_artifacts(wrapper, entry)
            if self.feedback_ref:
                require({"event_id": self.feedback_ref, "kind": "event"} in wrapper["causes"], "Planner output must carry the recorded user feedback")
                self.feedback_ref = None
            self.apply_dispositions(wrapper["dispositions"], entry)
            self.outputs["spec"] = entry_id
            self.inflight = None
            self.last_error = None
            if wrapper["output_kind"] == "consolidated":
                require(self.all_approved() and not wrapper["questions"], "Consolidation requires approvals and resolved questions")
                require(event == ("spec-updated" if self.spec_handed_off else "spec-created"), "Wrong consolidated event for this cycle")
                self.spec_handed_off = True
                target = "spec_updated" if event == "spec-updated" else "spec_created"
            else:
                require(event == "spec-updated", "Interim drafts use spec-updated")

        elif event == "spec-artifact-approved":
            self.pair(entry, "User", "Planner")
            require(previous == "spec_in_progress", "Artifact approval outside drafting")
            name = details["artifact"]
            require(self.artifacts[name] and details["version"] == self.artifacts[name]["version"], "Approval is for a stale/absent version")
            require(details["output_ref"] == {"event_id": self.produced[name], "kind": "spec_change_wrapper"}, "Approval must cite the actual producing Planner output")
            require(name not in self.approvals, "Do not invent renewed approval for an unchanged approval basis")
            require(all(n in self.approvals for n in ARTIFACTS[:ARTIFACTS.index(name)]), "Approve upstream artifacts first")
            self.approvals[name] = {"event_id": entry_id, "version": details["version"], "output_ref": details["output_ref"]}

        elif event in {"spec-review-started", "code-review-started"}:
            phase = event.split("-")[0]
            role, requestor = ("Architect", "Planner") if phase == "spec" else ("Reviewer", "Coder")
            self.pair(entry, role, requestor)
            allowed = {"spec_created", "spec_updated"} if phase == "spec" else {"coding_complete"}
            reconsidering = self.reviews.get(phase) and any(d["decision"] in {"reconsider", "clarify"} for fid, d in self.dispositions.items() if self.findings[fid]["phase"] == phase)
            catchup = phase in self.assurance_gaps and previous not in allowed
            require(previous in allowed or catchup or reconsidering, "Review has no completed handoff or reconsideration")
            require(self.inflight is None, "Recover/suspend existing role work before another review invocation")
            if catchup:
                self.review_returns[phase] = previous
            source_kind = "spec_change_wrapper" if phase == "spec" else "change_wrapper"
            require(details["source_ref"] == {"event_id": self.outputs[phase], "kind": source_kind}, "Review must use latest consolidated output")
            source = self.entries[self.outputs[phase]][source_kind]
            require(source["output_kind"] == "consolidated", "Review cannot start from an interim output")
            prior = self.reviews.get(phase)
            require(details["prior_review_ref"] == ({"event_id": prior, "kind": phase + "_review"} if prior else None), "Review must carry latest prior review")
            require(details["review_kind"] == ("follow_up" if prior else "initial"), "Incorrect review kind")
            self.context(details["invocation"], role, True, entry)
            target = phase + "_in_review"

        elif event in {"spec-reviewed", "code-reviewed"}:
            phase = event.split("-")[0]
            role, requestor = ("Architect", "Planner") if phase == "spec" else ("Reviewer", "Coder")
            self.pair(entry, role, requestor)
            require(previous == phase + "_in_review", "Review output without review start")
            wrapper = entry[WRAPPERS[event]]
            validate_wrapper(WRAPPERS[event].replace("_", "-"), wrapper)
            context = self.context(wrapper["context"], role)
            basis = self.config_snapshot(context)
            for key in ("assurance_level", "review_disposition_policy"):
                require(wrapper[key] == basis[key], "Review configuration basis mismatch")
            start = self.entries[context["trigger_event_id"]]["details"]
            require(wrapper["reviewed_output_ref"] == start["source_ref"] and wrapper["prior_review_ref"] == start["prior_review_ref"] and wrapper["review_kind"] == start["review_kind"], "Review output disagrees with invocation scope")
            require(wrapper["reviewed_artifacts"] == self.artifacts, "Review uses stale document versions")
            new_findings = all_findings(wrapper)
            for fid, finding in new_findings.items():
                old = self.findings.get(fid)
                if old is None:
                    require(fid.startswith(("S" if phase == "spec" else "C") + "-" + context["trigger_event_id"] + "-"), "New finding identity must use its first review-start event")
                else:
                    require(old["phase"] == phase, "Finding belongs to the other review loop")
                    if old["severity"] != finding["severity"] or old.get("resolved"):
                        require(finding["reconsideration_reason"], "Changed classification/reopened finding requires grounds")
                    if finding["reconsideration_reason"]:
                        self.dispositions.pop(fid, None)
                self.findings[fid] = {**finding, "phase": phase, "resolved": False}
            for fid in wrapper["resolved_findings"]:
                require(fid in self.findings and self.findings[fid]["phase"] == phase and fid not in new_findings, "Invalid resolved finding")
                self.findings[fid]["resolved"] = True
            require(set(self.open_findings(phase)).issubset(new_findings), "Review silently dropped an unresolved finding")
            self.apply_dispositions(wrapper["dispositions"], entry)
            expected = self.result(phase)
            require(wrapper["accepted"] == expected, f"Acceptance must be {expected} under the recorded dispositions")
            if phase == "code" and expected == "true":
                self.check_checks(wrapper["checks"])
            if self.repair_pending[phase]:
                self.cycles[phase] += 1
                self.repair_pending[phase] = False
            self.reviews[phase] = entry_id
            self.review_runs[phase].append({"accepted": expected, "must_fix": sorted(fid for fid, f in self.open_findings(phase).items() if f["severity"] == "must_fix"), "meaningful_change": wrapper["meaningful_change"]})
            if LEVELS[wrapper["assurance_level"]] >= LEVELS[self.config["assurance_level"]]:
                self.assurance_gaps.discard(phase)
            else:
                # A first review may have been running when assurance increased.
                # Its original invocation basis remains valid evidence, but cannot
                # satisfy the feature's now-higher requirement.
                self.assurance_gaps.add(phase)
            self.inflight = None
            self.last_error = None
            return_phase = self.review_returns.pop(phase, None)
            target = return_phase if return_phase and expected == "true" else self.result_status(phase, expected)

        elif event == "review-findings-dispositioned" or event.endswith("-approved-by-user"):
            reference = details["review_ref"]
            phase = "spec" if reference["kind"] == "spec_review" else "code"
            require(reference["kind"] in {"spec_review", "code_review"} and self.reviews.get(phase) == reference["event_id"], "Disposition must identify the latest review")
            requestors = {"Planner", "Architect"} if phase == "spec" else {"Coder", "Reviewer"}
            if event.endswith("-approved-by-user"):
                require(event.startswith(phase + "-"), "Approval event belongs to the other review loop")
                requestors = {"Planner" if phase == "spec" else "Coder"}
            require(entry["actor"] == "User" and entry["requestor"] in requestors, "Invalid user disposition actor/requestor")
            require(previous in {phase + "_changes_requested", phase + "_conditionally_approved", phase + "_approved"}, "Disposition outside findings state")
            require(all(self.findings.get(d["finding_id"], {}).get("phase") == phase for d in details["decisions"]), "Cross-phase finding disposition")
            self.apply_dispositions(details["decisions"], entry, user=True)
            self.review_decisions.setdefault(reference["event_id"], set()).update(d["finding_id"] for d in details["decisions"])
            if phase == "code" and self.result(phase) == "true":
                self.check_checks(self.entries[self.reviews[phase]]["review_wrapper"]["checks"])
            target = self.result_status(phase, self.result(phase))

        elif event.endswith("-approved-with-justifications"):
            phase = event.split("-")[0]
            self.pair(entry, "Orchestrator", "Planner" if phase == "spec" else "Coder")
            require(previous in {phase + "_changes_requested", phase + "_conditionally_approved"}, "Justifications must concern reviewed work")
            require(details["review_ref"] == {"event_id": self.reviews[phase], "kind": phase + "_review"}, "Stale deferral review")
            require(self.result(phase) != "false", "Unresolved must-fix findings cannot be conditionally approved")
            require(all(d["finding_id"] in self.findings and self.findings[d["finding_id"]]["phase"] == phase
                        and self.findings[d["finding_id"]]["severity"] != "must_fix" for d in details["dispositions"]),
                    "Justifications must concern this loop's non-must-fix findings")
            target = phase + "_conditionally_approved"

        elif event == "user-authorization-recorded":
            self.pair(entry, "User", "User")
            kind = details["kind"]
            auth = deepcopy(details)
            auth.setdefault("uncertain_attempts", [])
            auth["scope_epoch"] = self.scope_epoch
            if kind == "coding":
                require(previous == "spec_approved", "Coding decision must concern an accepted specification")
                self.coding_authorization = entry_id
            if kind == "coding" and details["decision"] == "granted":
                require(previous == "spec_approved" and not self.assurance_gaps.intersection({"spec"}), "Coding authorization requires accepted spec at current assurance")
                require(any(r == {"event_id": self.reviews["spec"], "kind": "spec_review"} for r in details["references"]), "Coding authorization must cite current spec review")
                self.coding_authorization = entry_id
            elif kind == "repair_cycle":
                phase = details["limits"]["phase"]
                require(phase in {"spec", "code"} and self.reviews.get(phase), "Repair authorization needs phase/review")
                require({"event_id": self.reviews[phase], "kind": phase + "_review"} in details["references"], "Repair authorization must cite current review")
                require(details["limits"]["additional_cycles"] is not None, "Specify extra repair allowance (one for generic continue)")
                if details["decision"] == "granted":
                    self.extra_cycles[phase] += details["limits"]["additional_cycles"]
            elif kind == "checkpoint_recovery":
                attempts = details["failed_attempts"] + auth["uncertain_attempts"]
                require(attempts, "Recovery authorization needs failed or uncertain push-attempt context")
                require(details["limits"]["max_attempts"] == 1, "Checkpoint retry authorizes exactly one push")
                require(len({a["attempt_id"] for a in attempts}) == len(attempts), "Recovery context repeats an attempt identity")
                for attempt in attempts:
                    require(all(i in self.entries for i in attempt["event_ids"]), "Push attempt refers to unrecorded events")
                    require(attempt["remote"] == self.log["branch_context"]["remote"] and attempt["feature_branch"] == self.log["branch_context"]["feature_branch"], "Push attempt target disagrees with feature branch")
            elif kind == "external_operation" and details["operation"] == "continue-role":
                require(details["scope"] in self.errors,
                        "Further role attempts must identify the original invocation start")
                require(details["limits"]["max_attempts"] is not None, "Further role attempts need an explicit bounded allowance")
                auth["attempt_ceiling"] = len(self.errors[details["scope"]]) + details["limits"]["max_attempts"]
            if kind != "checkpoint_recovery":
                require(not details["failed_attempts"] and not auth["uncertain_attempts"], "Push-attempt context belongs to checkpoint recovery")
            self.authorizations[entry_id] = auth

        elif event in {"coding-started", "coding-revision-started"}:
            revision = event == "coding-revision-started"
            self.pair(entry, "Coder", "Reviewer" if revision else "Planner")
            require(self.all_approved() and "spec" not in self.assurance_gaps, "Coding requires valid artifact approvals and sufficient spec assurance")
            if revision:
                require(previous in {"code_changes_requested", "code_conditionally_approved"}, "No code repair is ready")
                require(self.repair_gate("code") is None, f"Code repair gate: {self.repair_gate('code')}")
                require(details["source_ref"] == {"event_id": self.reviews["code"], "kind": "code_review"}, "Code repair requires latest review")
                self.repair_pending["code"] = True
            else:
                require(previous == "spec_approved", "Initial/in-scope coding follows spec acceptance")
                require(details["source_ref"] == {"event_id": self.outputs["spec"], "kind": "spec_change_wrapper"}, "Coding requires latest spec handoff")
            auth = self.authorizations.get(details["authorization_ref"]["event_id"], {})
            require(details["authorization_ref"]["event_id"] == self.coding_authorization and auth.get("kind") == "coding" and auth.get("decision") == "granted" and auth.get("scope_epoch") == self.scope_epoch,
                    "Coding needs explicit authorization for the current material scope")
            self.context(details["invocation"], "Coder", True, entry)
            target = "coding_in_progress"

        elif event in {"coding-updated", "coding-complete"}:
            require(previous in {"coding_in_progress", "blocked"}, "Coding output outside implementation")
            start = self.entries[self.starts["Coder"]["trigger_event_id"]]
            self.pair(entry, "Coder", start["requestor"])
            wrapper = entry["change_wrapper"]
            validate_wrapper("change-wrapper", wrapper)
            self.context(wrapper["context"], "Coder")
            self.apply_artifacts(wrapper, entry, coder=True)
            self.apply_dispositions(wrapper["dispositions"], entry)
            self.outputs["code"] = entry_id
            self.inflight = None
            self.last_error = None
            if event == "coding-complete":
                require(wrapper["output_kind"] == "consolidated" and not wrapper["blockers"], "Coding completion requires consolidated unblocked output")
                require(wrapper["task_progress"] and all(t["status"] in {"completed", "dispositioned"} for t in wrapper["task_progress"]), "Required tasks remain incomplete")
                for task in wrapper["task_progress"]:
                    if task["status"] == "dispositioned":
                        auth = self.authorizations.get((task["disposition_ref"] or {}).get("event_id"), {})
                        require(auth.get("decision") == "granted" and auth.get("kind") == "external_operation"
                                and auth.get("operation") == "accept-task-result" and auth.get("scope") == task["task_id"]
                                and auth.get("scope_epoch") == self.scope_epoch,
                                "Incomplete task needs explicit accept-task-result authority for that task")
                require(wrapper["checks"], "Coding completion requires verification evidence")
                self.check_checks(wrapper["checks"])
                target = "coding_complete"
            else:
                require(wrapper["output_kind"] == "incremental", "Interim coding updates must be incremental")
                independent = any(b["independent_task_ids"] for b in wrapper["blockers"])
                target = "blocked" if wrapper["blockers"] and not independent else "coding_in_progress"

        elif event == "user-override":
            self.pair(entry, "User", "User")
            targets = [c["target"] for c in details["changes"]]
            require(len(set(targets)) == len(targets) and not any(a != b and b.startswith(a + "/") for a in targets for b in targets), "Overlapping override targets")
            old_level = self.config["assurance_level"]
            for change in details["changes"]:
                keys = change["target"].strip("/").split("/")
                parent = self.config
                for key in keys[:-1]:
                    parent = parent[key]
                require(parent[keys[-1]] == change["previous"], "Override previous value does not match effective configuration")
                parent[keys[-1]] = deepcopy(change["new"])
            validate_capability(self.config)
            if LEVELS[self.config["assurance_level"]] > LEVELS[old_level]:
                self.assurance_gaps.update(self.reviews)
            self.config_ref = entry_id
            self.configurations[entry_id] = deepcopy(self.config)

        elif event == "subagent-error":
            context = details["invocation"]
            role = context["role"]
            self.context(context, role)
            start = self.entries[context["trigger_event_id"]]
            self.pair(entry, role, start["requestor"])
            require(previous in {"spec_in_progress", "spec_in_review", "coding_in_progress", "blocked", "code_in_review"}, "Role failure outside active work")
            expected_role = {"spec_in_progress": "Planner", "spec_in_review": "Architect", "coding_in_progress": "Coder",
                             "blocked": "Coder", "code_in_review": "Reviewer"}[previous]
            require(role == expected_role, "Failure must belong to the active workflow role")
            require((details["category"] == "helper_failure") == (details["helper"] is not None),
                    "Helper failure must identify the actual failed helper and owning role")
            self.errors.setdefault(context["trigger_event_id"], []).append(details)
            self.last_error = {**details, "event_id": entry_id}
            self.inflight = role

        elif event == "implementation-complete":
            self.pair(entry, "Orchestrator", "User")
            require(previous == "code_approved" and not self.assurance_gaps, "Completion requires code approval at current assurance")
            require(details["review_ref"] == {"event_id": self.reviews["code"], "kind": "code_review"}, "Completion cites stale review")
            require(set(details["known_issues"]) == set(self.known_issues()), "Final acceptance must disclose current known issues")
            target = "implementation_complete"
        else:
            raise ValidationError(f"Unsupported event {event}")

        require(entry["status"] == target, f"{event}: resulting status must be {target}, got {entry['status']}")
        self.status = target
        self.entries[entry_id] = deepcopy(entry)

    def known_issues(self):
        return {fid: {"finding": f, "disposition": self.dispositions[fid]}
                for fid, f in self.findings.items() if not f.get("resolved") and fid in self.dispositions
                and self.dispositions[fid]["decision"] in {"defer", "accept_limitation"}
                and self.disposition_allowed(fid, self.dispositions[fid])}

    def next_action(self):
        if self.status == "implementation_complete":
            return "finish_final_checkpoint_then_squash_message"
        if self.last_error and self.inflight:
            gate = self.role_recovery_gate(self.last_error["invocation"])
            if gate:
                return gate
        if self.inflight:
            return "recover_invocation_or_output"
        if "spec" in self.assurance_gaps:
            return "review_assurance_gap_spec"
        if "code" in self.assurance_gaps and self.status == "code_approved":
            return "review_assurance_gap_code"
        if self.status == "spec_in_progress":
            if self.feedback_ref:
                return "continue_planner_" + self.earliest_artifact
            for name in ARTIFACTS:
                if self.artifacts[name] and name not in self.approvals:
                    return "obtain_" + name + "_approval"
                if not self.artifacts[name]:
                    return "continue_planner_" + name
            return "obtain_consolidated_spec_output"
        if self.status in {"spec_created", "spec_updated"}:
            return "start_architect_review"
        if self.status == "spec_approved":
            if "spec" in self.assurance_gaps:
                return "review_assurance_gap_spec"
            auth = self.authorizations.get(self.coding_authorization, {})
            return "start_coder" if auth.get("decision") == "granted" and auth.get("scope_epoch") == self.scope_epoch else "obtain_coding_authorization"
        if self.status == "code_approved":
            return "review_assurance_gap_code" if self.assurance_gaps else "obtain_final_user_acceptance"
        for phase in ("spec", "code"):
            if self.status in {phase + "_changes_requested", phase + "_conditionally_approved"}:
                if phase == "spec" and self.user_revision_pending:
                    return "start_planner_revision"
                if any(d["decision"] in {"reconsider", "clarify"} for fid, d in self.dispositions.items() if self.findings[fid]["phase"] == phase and not self.findings[fid].get("resolved")):
                    return "reconsider_" + phase + "_review"
                return self.repair_gate(phase) or ("start_planner_revision" if phase == "spec" else "start_coder_revision")
        return {"coding_in_progress": "continue_coder", "blocked": "resolve_scoped_blocker",
                "coding_complete": "start_reviewer_review"}.get(self.status, "recover_invocation_or_output")


def replay(log, reader_version=None, previous=None):
    require(isinstance(log, dict), "Task log must be a JSON object")
    check_compatibility(log.get("workflow_version"), reader_version)
    validate_shape("task-log", log)
    if previous is not None:
        require(log["history"][:len(previous["history"])] == previous["history"], "History is append-only")
        for key in ("feature", "feature_dir", "workflow_version", "branch_context", "requirements_ref", "design_ref", "tasks_ref", "task_log_ref"):
            require(previous[key] == log[key], f"Immutable feature identity changed: {key}")
    directory = ".docs/specs/" + log["feature"]
    require(log["feature_dir"] == directory, "Feature directory must match feature identity")
    for name in (*ARTIFACTS, "task_log"):
        suffix = ".json" if name == "task_log" else ".md"
        require(log[name + "_ref"] == directory + "/" + name + suffix, f"Invalid {name} reference")
    state = Replay(log)
    for entry in log["history"]:
        try:
            state.append(entry)
        except (KeyError, TypeError) as exc:
            raise ValidationError(f"History {entry['id']} ({entry['event']}): missing prerequisite {exc}") from exc
        except ValidationError as exc:
            raise ValidationError(f"History {entry['id']} ({entry['event']}): {exc}") from exc
    require(log["status"] == state.status, "Top-level status disagrees with history")
    require({key: log[key] for key in state.config} == state.config, "Effective configuration disagrees with override history")
    return state


def resume_action(log, observations=None, reader_version=None):
    state = replay(log, reader_version)
    observations = observations or {}
    action = state.next_action()
    delivery = observations.get("delivery", "unknown")
    if delivery != "delivered":
        action = {"failed": "obtain_checkpoint_recovery_direction", "uncommitted": "validate_and_commit_checkpoint",
                  "committed": "deliver_authorized_checkpoint", "uncertain": "obtain_checkpoint_outcome_direction"}.get(delivery, "reconcile_checkpoint_delivery")
    elif state.inflight:
        invocation = observations.get("invocation", "unknown")
        if action == "recover_invocation_or_output":
            action = {"running": "recover_running_invocation", "completed": "record_recovered_output", "paused": "continue_existing_role_context",
                      "not_started": "invoke_recorded_role"}.get(invocation, "establish_invocation_liveness")
    return {"status": state.status, "action": action, "workflow_action": state.next_action(),
            "configuration": state.config, "configuration_ref": state.config_ref,
            "artifacts": state.artifacts, "approval_bases": state.approvals, "repair_cycles": state.cycles,
            "assurance_gaps": sorted(state.assurance_gaps), "known_issues": state.known_issues()}
