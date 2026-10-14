"""Pure v2 history validation/replay; never dispatches agents or changes files/Git."""
from __future__ import annotations

from copy import deepcopy

from workflow_artifacts import (ValidationError, all_findings, check_compatibility,
                                require, validate_capability, validate_shape, validate_wrapper,
                                validate_progress, work_scope, validate_review_scope)

ARTIFACTS = ("requirements", "design", "tasks")
LEVELS = {"basic": 0, "standard": 1, "maximum": 2}
SETTLED = {"defer", "accept_limitation", "reject"}
WRAPPERS = {"spec-updated": "spec_change_wrapper",
            "spec-reviewed": "spec_review_wrapper",
            "coding-complete": "change_wrapper", "coding-phase-complete": "change_wrapper", "code-reviewed": "review_wrapper"}
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
        self.contexts = {}
        self.review_configurations = {}
        self.review_artifacts = {}
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
        self.last_error = None
        self.feedback_ref = None
        self.user_revision_pending = False
        self.review_returns = {}
        self.review_return_scopes = {}
        self.phases = []
        self.plan_ref = None
        self.current_scope = {"kind": "feature"}
        self.phase_coders = {}
        self.coder_assignments = {}
        self.completed_phases = set()
        self.assessments = []
        self.accepted_reviews = set()

    def stage(self, scope):
        if scope["kind"] == "feature":
            return "code"
        current = next((p for p in self.phases if p["id"] == scope["phase_id"]), None)
        require(current is not None, "Unknown phase identity")
        if self.plan_ref != scope["plan_ref"]:
            source = check_reference(scope["plan_ref"], self.entries).get("spec_change_wrapper", {})
            recorded = next((p for p in source.get("implementation_phases", []) if p["id"] == scope["phase_id"]), None)
            require(scope["plan_ref"]["kind"] == "spec_change_wrapper" and source.get("output_kind") == "consolidated"
                    and recorded and recorded["task_ids"] == current["task_ids"],
                    "Historical phase scope no longer matches the approved task ownership")
        return "phase:" + scope["phase_id"]

    @staticmethod
    def family(stage):
        return "spec" if stage == "spec" else "code"

    def review_stage(self, reference):
        review = check_reference(reference, self.entries)
        require(review["event"] in {"spec-reviewed", "code-reviewed"}, "Reference must identify a review")
        scope = work_scope(review.get("review_wrapper", {}))
        return "spec" if review["event"] == "spec-reviewed" else "code" if scope["kind"] == "feature" else "phase:" + scope["phase_id"]

    def level(self, stage, config=None):
        level = (config or self.config)["assurance_level"]
        return {"basic": None, "standard": "basic", "maximum": "standard"}[level] if stage.startswith("phase:") else level

    def initialize_stage(self, stage):
        self.cycles.setdefault(stage, 0)
        self.extra_cycles.setdefault(stage, 0)
        self.repair_pending.setdefault(stage, False)
        self.review_runs.setdefault(stage, [])

    def source_wrapper(self, stage):
        return self.entries[self.outputs[stage]]["spec_change_wrapper" if stage == "spec" else "change_wrapper"]

    def refresh_gaps(self):
        """Derive sufficiency from all accepted applicable evidence, not overrides."""
        gaps = set()
        stages = set(self.reviews) | {"phase:" + p["id"] for p in self.phases[:-1] if p["id"] in self.completed_phases}
        for stage in stages:
            required = self.level(stage)
            if required is None:
                continue
            source = self.source_wrapper(stage)
            sufficient = False
            for event_id in self.accepted_reviews:
                entry = self.entries[event_id]
                wrapper = entry.get("spec_review_wrapper", entry.get("review_wrapper"))
                candidate_stage = self.review_stage({"event_id": event_id, "kind": "event"})
                if candidate_stage != stage or LEVELS[wrapper["assurance_level"]] < LEVELS[required]:
                    continue
                reviewed = self.reviewed_source(wrapper)
                applicable = (reviewed["checkpoint_commit"] == source["checkpoint_commit"]
                              and self.review_artifacts[wrapper["context"]["trigger_event_id"]] == self.artifacts)
                for assessment in self.assessments:
                    if assessment["review_ref"]["event_id"] == event_id and assessment["source_ref"]["event_id"] == self.outputs[stage]:
                        applicable = assessment["conclusion"] == "applicable" and assessment["reviewed_artifacts"] == self.artifacts and assessment["current_commit"] == source["checkpoint_commit"]
                sufficient |= applicable
            if not sufficient:
                gaps.add(stage)
        self.assurance_gaps = gaps

    def phase_ready(self, phase_id):
        stage = "phase:" + phase_id
        return phase_id in self.completed_phases and (self.level(stage) is None or
            stage in self.reviews and stage not in self.assurance_gaps and self.result(stage) == "true")

    def pair(self, entry, actor, requestor):
        require(entry["actor"] == actor and entry["requestor"] == requestor,
                f"{entry['event']}: expected actor/requestor {actor}/{requestor}")

    def configuration_at(self, event_id):
        reference = max((ref for ref in self.configurations if int(ref) <= int(event_id)), key=int)
        return self.configurations[reference]

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
            failed_context = last["invocation"]
            failed_id = next(e["id"] for e in reversed(list(self.entries.values()))
                             if e["event"] == "subagent-error" and e["details"]["invocation"]["trigger_event_id"] == context["trigger_event_id"])
            old = self.assignment(self.configuration_at(failed_id), assigned_role, failed_context)
            if last.get("helper"):
                old["assignment"] = {k: last["helper"][k] for k in ("model", "reasoning_effort")}
            changed = old != self.assignment(self.config, assigned_role, failed_context)
            if not changed and not directed:
                return "obtain_model_direction"
        if attempt > 3 and not directed:
            return "obtain_role_failure_direction"
        return None

    def assignment(self, config, role, context=None):
        capability = config["capability"]
        assignment = capability["roles"][role.lower()]
        if role.lower() == "reviewer" and context:
            start = self.entries.get(context["trigger_event_id"], {}).get("details", {})
            if work_scope(start)["kind"] == "phase":
                assignment = capability.get("stage_assignments", {}).get("intermediate_reviewer")
        return {"platform": capability["platform"], "assignment": assignment}

    def active_context(self, role):
        return self.contexts[self.starts[role]["trigger_event_id"]]

    def context(self, context, role, starting=False, entry=None):
        require(context is not None and context["role"] == role, "Invocation role mismatch")
        trigger = context["trigger_event_id"]
        if starting:
            require(trigger == entry["id"] and context["attempt"] == 1,
                    "A new logical invocation uses its start event and attempt 1")
            self.starts[role] = deepcopy(context)
            if role in {"Architect", "Reviewer"}:
                self.review_configurations[trigger] = {k: self.config[k] for k in ("assurance_level", "review_disposition_policy")}
                self.review_artifacts[trigger] = deepcopy(self.artifacts)
            self.inflight = role
        else:
            require(role in self.starts and trigger == self.starts[role]["trigger_event_id"],
                    "Output belongs to a different invocation")
            failures = self.errors.get(trigger, [])
            require(context["attempt"] == len(failures) + 1, "Invocation attempt is duplicated or skips recovery")
            if failures:
                require(self.role_recovery_gate(context) is None, f"Role retry gate: {self.role_recovery_gate(context)}")
        self.contexts[trigger] = deepcopy(context)
        return context

    def spec_ready(self, source=None):
        if source is None:
            source = self.source_wrapper("spec") if "spec" in self.outputs else {}
        return (self.all_approved() and source.get("output_kind") == "consolidated"
                and source["artifacts"] == self.artifacts and not source.get("questions") and not self.feedback_ref)

    def reviewed_source(self, wrapper):
        reference = wrapper["reviewed_output_ref"]
        return self.entries[reference["event_id"]][reference["kind"]]

    def all_approved(self):
        return all(self.artifacts[name] and name in self.approvals for name in ARTIFACTS)

    def apply_artifacts(self, wrapper, entry, coder=False):
        changes = {c["artifact"]: c for c in wrapper.get("artifact_changes", [])}
        if not coder and self.artifacts["tasks"]:
            previous_plan = self.entries[self.produced["tasks"]]["spec_change_wrapper"].get("implementation_phases", [])
            plan = wrapper.get("implementation_phases", [])
            if plan != previous_plan:
                change = changes.get("tasks")
                require(change and change["change_kind"] in {"material", "editorial"},
                        "Changing the tasks phase plan requires a tasks content revision")
                # Phase order, identities and task ownership govern review gates.
                # A title-only editorial correction may preserve approval.
                previous_partition = [(p["id"], p["task_ids"]) for p in previous_plan]
                partition = [(p["id"], p["task_ids"]) for p in plan]
                require(partition == previous_partition or change["change_kind"] == "material",
                        "Changing the phase plan's task partition requires a material tasks revision")
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
                require(name in self.approvals, "Task progress requires an existing approval")
            else:
                for upstream in ARTIFACTS[:ARTIFACTS.index(name)]:
                    require(upstream in self.approvals, f"Approve {upstream} before changing dependent {name}")
            if change["change_kind"] == "material":
                self.approvals.pop(name, None)
                self.scope_epoch += 1
            elif name in self.approvals:
                require(change.get("approval_basis_ref") == {"event_id": self.approvals[name]["event_id"], "kind": "approval"},
                        "Nonmaterial update must cite its preserved approval basis")
            self.artifacts[name] = deepcopy(new)
            if change["change_kind"] != "progress":
                self.produced[name] = entry["id"]

    def disposition_allowed(self, finding_id, disposition, stage=None, config=None):
        if disposition["decision"] not in SETTLED:
            return False
        finding = self.findings[finding_id]
        if disposition.get("authority") == "user":
            return bool(disposition.get("recorded_user_event"))
        return (disposition.get("authority") == "policy" and finding["severity"] != "must_fix" and self.level(stage or finding["phase"], config) != "maximum"
                and disposition["decision"] in {"defer", "accept_limitation"})

    def apply_dispositions(self, values, entry, user=False):
        require(len({d["finding_id"] for d in values}) == len(values), "Duplicate disposition")
        for raw in values:
            disposition = deepcopy(raw)
            finding_id = disposition["finding_id"]
            require(finding_id in self.findings, f"Unknown finding {finding_id}")
            if not user and not disposition.get("authority"):
                continue  # Proposals remain in the return and grant no authority.
            old = self.dispositions.get(finding_id)
            if old and self.disposition_allowed(finding_id, old) and disposition["decision"] != old["decision"]:
                require(disposition["decision"] == "reconsider", "Settled disposition requires explicit reconsideration")
            if user:
                require(disposition["authority"] == "user" and disposition.get("authority_ref") is None,
                        "A user decision records its own authority, not another person's decision")
                disposition["recorded_user_event"] = entry["id"]
            elif disposition.get("authority") == "user":
                reference = disposition.get("authority_ref")
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
                if old and old["authority"] == "user":
                    require(disposition["decision"] == old["decision"], "Policy cannot replace the user's selected finding response")
                    # A matching producer response describes its work; it must
                    # not replace the actual user decision or its authority.
                    disposition = deepcopy(old)
            self.dispositions[finding_id] = disposition

    def open_findings(self, phase, config=None):
        findings = {}
        for fid, finding in self.findings.items():
            if not (finding["phase"] == phase or phase == "code" and finding["phase"].startswith("phase:")) or finding.get("resolved"):
                continue
            disposition = self.dispositions.get(fid, {"decision": "fix"})
            user_followup = (disposition.get("authority") == "user" and disposition.get("recorded_user_event")
                             and disposition["decision"] in {"fix", "clarify", "reconsider"})
            if finding["severity"] == "nit" and not user_followup:
                continue
            if not self.disposition_allowed(fid, disposition, phase, config):
                findings[fid] = finding
        return findings

    def result(self, phase, config=None):
        findings = self.open_findings(phase, config)
        if any(f["severity"] == "must_fix" for f in findings.values()):
            return "false"
        return "conditional" if findings else "true"

    def result_status(self, phase, accepted):
        if phase.startswith("phase:") and accepted == "true":
            return "coding_in_progress"
        return self.family(phase) + {"false": "_changes_requested", "conditional": "_changes_requested", "true": "_approved"}[accepted]

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
        level = self.level(phase)
        if level is None:
            level = self.entries[self.reviews[phase]]["review_wrapper"]["assurance_level"]
        limit = limits[level]
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
                reference = check.get("disposition_ref")
                require(reference is not None, f"Required check {check['name']} has not passed")
                auth = self.authorizations.get(reference["event_id"], {})
                require(auth.get("decision") == "granted" and auth.get("kind") == "external_operation"
                        and auth.get("operation") == "accept-check-result" and auth.get("scope") == check["name"]
                        and auth.get("scope_epoch") == self.scope_epoch,
                        "Check exception needs explicit authorization for this exact check")

    def append(self, entry, *, derive_status=False):
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
                require(previous in {"spec_changes_requested"}, "No spec revision is ready")
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

        elif event == "spec-updated":
            require(previous == "spec_in_progress", "Planner output requires a drafting cycle")
            start = self.entries[self.starts["Planner"]["trigger_event_id"]]
            self.pair(entry, "Planner", start["requestor"])
            wrapper = entry["spec_change_wrapper"]
            validate_wrapper("spec-change-wrapper", wrapper)
            self.context(wrapper["context"], "Planner")
            self.apply_artifacts(wrapper, entry)
            if self.feedback_ref:
                require({"event_id": self.feedback_ref, "kind": "event"} in wrapper.get("causes", []), "Planner output must carry the recorded user feedback")
                self.feedback_ref = None
            self.apply_dispositions(wrapper.get("dispositions", []), entry)
            self.outputs["spec"] = entry_id
            self.inflight = None
            self.last_error = None
            if wrapper["output_kind"] == "consolidated":
                phases = wrapper.get("implementation_phases", [])
                for phase in self.phases:
                    if phase["id"] in self.completed_phases:
                        revised = next((p for p in phases if p["id"] == phase["id"]), None)
                        require(revised and revised["task_ids"] == phase["task_ids"] and phases.index(revised) == self.phases.index(phase),
                                "Completed phase identities and task ownership cannot be renumbered or reused")
                self.phases = deepcopy(phases)
                self.plan_ref = {"event_id": entry_id, "kind": "spec_change_wrapper"}
                for phase in phases:
                    self.initialize_stage("phase:" + phase["id"])
                target = "spec_ready" if self.spec_ready(wrapper) else "spec_in_progress"

        elif event == "spec-artifact-approved":
            self.pair(entry, "User", "Planner")
            require(previous == "spec_in_progress", "Artifact approval outside drafting")
            name = details["artifact"]
            require(self.artifacts[name] and details["version"] == self.artifacts[name]["version"], "Approval is for a stale/absent version")
            require(details["output_ref"] == {"event_id": self.produced[name], "kind": "spec_change_wrapper"}, "Approval must cite the actual producing Planner output")
            require(name not in self.approvals, "Do not invent renewed approval for an unchanged approval basis")
            require(all(n in self.approvals for n in ARTIFACTS[:ARTIFACTS.index(name)]), "Approve upstream artifacts first")
            self.approvals[name] = {"event_id": entry_id, "version": details["version"], "output_ref": details["output_ref"]}
            target = "spec_ready" if self.spec_ready() else "spec_in_progress"

        elif event in {"spec-review-started", "code-review-started"}:
            family = event.split("-")[0]
            phase = "spec" if family == "spec" else self.stage(work_scope(details))
            role, requestor = ("Architect", "Planner") if family == "spec" else ("Reviewer", "Coder")
            self.pair(entry, role, requestor)
            allowed = {"spec_ready"} if phase == "spec" else {"coding_complete"} if phase == "code" else {"coding_in_progress"}
            if phase.startswith("phase:"):
                require(self.level(phase) is not None, "Basic has no intermediate phase review")
                require(work_scope(details)["phase_id"] != self.phases[-1]["id"], "Last phase goes directly to final review")
                require(self.config["capability"].get("stage_assignments", {}).get("intermediate_reviewer"),
                        "Resolve the intermediate Reviewer assignment before dispatch")
            if phase != "spec":
                require("spec" not in self.assurance_gaps, "Resolve specification assurance before dependent code review")
            if phase == "code":
                require(all(self.phase_ready(p["id"]) for p in self.phases[:-1]), "Resolve earlier phase readiness before final review")
            reconsidering = self.reviews.get(phase) and any(d["decision"] in {"reconsider", "clarify"} for fid, d in self.dispositions.items() if self.findings[fid]["phase"] == phase)
            catchup = phase in self.assurance_gaps and previous not in allowed
            require(previous in allowed or catchup or reconsidering, "Review has no completed handoff or reconsideration")
            require(self.inflight is None, "Recover/suspend existing role work before another review invocation")
            if catchup:
                self.review_returns[phase] = previous
                self.review_return_scopes[phase] = deepcopy(self.current_scope)
            source_kind = "spec_change_wrapper" if phase == "spec" else "change_wrapper"
            require(details["source_ref"] == {"event_id": self.outputs[phase], "kind": source_kind}, "Review must use latest consolidated output")
            source = self.entries[self.outputs[phase]][source_kind]
            require(phase != "spec" or self.spec_ready(), "Review requires consolidated context and valid approvals")
            require(work_scope(details) == work_scope(source), "Review scope must match its completed source handoff")
            prior = self.reviews.get(phase)
            require(details["prior_review_ref"] == ({"event_id": prior, "kind": family + "_review"} if prior else None), "Review must carry latest prior review")
            require(details["review_kind"] == ("follow_up" if prior else "initial"), "Incorrect review kind")
            self.context(details["invocation"], role, True, entry)
            if phase.startswith("phase:"):
                self.current_scope = deepcopy(work_scope(details))
            target = family + "_in_review"

        elif event in {"spec-reviewed", "code-reviewed"}:
            family = event.split("-")[0]
            phase = "spec" if family == "spec" else self.stage(work_scope(entry["review_wrapper"]))
            role, requestor = ("Architect", "Planner") if family == "spec" else ("Reviewer", "Coder")
            self.pair(entry, role, requestor)
            require(previous == family + "_in_review", "Review output without review start")
            wrapper = entry[WRAPPERS[event]]
            validate_wrapper(WRAPPERS[event].replace("_", "-"), wrapper)
            context = self.context(wrapper["context"], role)
            basis = self.review_configurations[context["trigger_event_id"]]
            require(wrapper["assurance_level"] == self.level(phase, basis), "Review assurance basis mismatch")
            start = self.entries[context["trigger_event_id"]]["details"]
            require(wrapper["reviewed_output_ref"] == start["source_ref"], "Review output disagrees with invocation scope")
            validate_review_scope(wrapper, initial=start["review_kind"] == "initial", repaired=self.repair_pending[phase])
            require(work_scope(wrapper) == work_scope(start), "Review work scope disagrees with invocation")
            require(self.review_artifacts[context["trigger_event_id"]] == self.artifacts, "Review uses stale document versions")
            new_findings = all_findings(wrapper)
            for fid, finding in new_findings.items():
                old = self.findings.get(fid)
                if old is None:
                    require(fid.startswith(("S" if phase == "spec" else "C") + "-" + context["trigger_event_id"] + "-"), "New finding identity must use its first review-start event")
                else:
                    require(old["phase"] == phase or phase == "code" and old["phase"].startswith("phase:"), "Finding belongs to the other review loop")
                    if old["severity"] != finding["severity"] or old.get("resolved"):
                        require(finding.get("reconsideration_reason"), "Changed classification/reopened finding requires grounds")
                    if finding.get("reconsideration_reason"):
                        self.dispositions.pop(fid, None)
                self.findings[fid] = {**finding, "phase": old["phase"] if old else phase, "resolved": False}
            for fid in wrapper.get("resolved_findings", []):
                require(fid in self.findings and (self.findings[fid]["phase"] == phase or phase == "code" and self.findings[fid]["phase"].startswith("phase:")) and fid not in new_findings, "Invalid resolved finding")
                self.findings[fid]["resolved"] = True
            retained = {fid for fid, f in self.findings.items() if not f.get("resolved") and
                        (f["phase"] == phase or phase == "code" and f["phase"].startswith("phase:"))}
            require(retained.issubset(new_findings), "Review silently dropped an unresolved finding (including accepted limitations)")
            self.apply_dispositions(wrapper.get("dispositions", []), entry)
            expected = self.result(phase, basis)
            require(wrapper["accepted"] == expected, f"Acceptance must be {expected} under the recorded dispositions")
            if expected == "true":
                self.check_checks(wrapper.get("checks", []))
            if self.repair_pending[phase]:
                self.cycles[phase] += 1
                self.repair_pending[phase] = False
            self.reviews[phase] = entry_id
            self.review_runs[phase].append({"accepted": expected, "must_fix": sorted(fid for fid, f in self.open_findings(phase).items() if f["severity"] == "must_fix"), "meaningful_change": wrapper.get("meaningful_change", False)})
            if expected == "true":
                self.accepted_reviews.add(entry_id)
            self.inflight = None
            self.last_error = None
            return_phase = self.review_returns.pop(phase, None)
            return_scope = self.review_return_scopes.pop(phase, None)
            current_result = self.result(phase)
            target = return_phase if return_phase and current_result == "true" else self.result_status(phase, current_result)
            if return_scope and current_result == "true":
                self.current_scope = return_scope

        elif event == "review-findings-dispositioned":
            reference = details["review_ref"]
            phase = self.review_stage(reference)
            family = self.family(phase)
            require(reference["kind"] in {"spec_review", "code_review"} and self.reviews.get(phase) == reference["event_id"], "Disposition must identify the latest review")
            requestors = {"Planner", "Architect"} if phase == "spec" else {"Coder", "Reviewer"}
            require(entry["actor"] == "User" and entry["requestor"] in requestors, "Invalid user disposition actor/requestor")
            require(previous in {family + "_changes_requested", family + "_approved", "coding_in_progress"} and phase in self.reviews, "Disposition outside findings state")
            require(all(self.findings.get(d["finding_id"], {}).get("phase") == phase or phase == "code" and self.findings.get(d["finding_id"], {}).get("phase", "").startswith("phase:") for d in details["decisions"]), "Cross-phase finding disposition")
            self.apply_dispositions(details["decisions"], entry, user=True)
            self.review_decisions.setdefault(reference["event_id"], set()).update(d["finding_id"] for d in details["decisions"])
            if self.result(phase) == "true":
                review = self.entries[self.reviews[phase]]
                self.check_checks(review[WRAPPERS[review["event"]]].get("checks", []))
            if self.result(phase) == "true":
                self.accepted_reviews.add(self.reviews[phase])
            target = self.result_status(phase, self.result(phase))

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
                require(phase in self.cycles and self.reviews.get(phase), "Repair authorization needs phase/review")
                require({"event_id": self.reviews[phase], "kind": self.family(phase) + "_review"} in details["references"], "Repair authorization must cite current review")
                require(details["limits"]["additional_cycles"] is not None, "Specify extra repair allowance (one for generic continue)")
                if details["decision"] == "granted":
                    self.extra_cycles[phase] += details["limits"]["additional_cycles"]
            elif kind == "checkpoint_recovery":
                attempts = auth["failed_attempts"] + auth["uncertain_attempts"]
                require(attempts, "Recovery authorization needs failed or uncertain push-attempt context")
                require(details["limits"]["max_attempts"] == 1, "Checkpoint retry authorizes exactly one push")
                require(len({a["attempt_id"] for a in attempts}) == len(attempts), "Recovery context repeats an attempt identity")
                for attempt in attempts:
                    # Earlier log-only attempts have this read-time meaning.
                    attempt.setdefault("checkpoint_kind", "log")
                    attempt.setdefault("publishing_role", "Orchestrator")
                    attempt.setdefault("invocation", None)
                    attempt.setdefault("phase_id", None)
                    require(attempt["event_ids"] or attempt["checkpoint_kind"] == "artifacts", "Only artifact checkpoints omit event ranges")
                    if attempt["publishing_role"] in {"Planner", "Coder"}:
                        invocation = attempt["invocation"]
                        require(invocation and invocation["role"] == attempt["publishing_role"], "Artifact recovery must retain producer invocation")
                        start = self.entries.get(invocation["trigger_event_id"], {})
                        require(start.get("actor") == invocation["role"] and start.get("event") in
                                {"spec-creation-started", "spec-revision-started", "coding-started", "coding-revision-started"},
                                "Unknown publishing invocation")
                        require(invocation["attempt"] <= len(self.errors.get(invocation["trigger_event_id"], [])) + 1,
                                "Recovery refers to an unrecorded producer attempt")
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
            scope = work_scope(details)
            stage = self.stage(scope)
            self.pair(entry, "Coder", "Reviewer" if revision else "Planner")
            require(self.all_approved() and "spec" not in self.assurance_gaps, "Coding requires valid artifact approvals and sufficient spec assurance")
            if revision:
                require(previous in {"code_changes_requested"}, "No code repair is ready")
                require(stage == self.stage(self.current_scope), "Code repair must target the active review scope")
                require(self.result(stage) != "true", "Code repair requires unresolved findings in the active review scope")
                require(self.repair_gate(stage) is None, f"Code repair gate: {self.repair_gate(stage)}")
                require(details["source_ref"] == {"event_id": self.reviews[stage], "kind": "code_review"}, "Code repair requires latest review in this scope")
                self.repair_pending[stage] = True
            else:
                require(previous == "spec_approved" or scope["kind"] == "phase" and previous == "coding_in_progress", "Initial/in-scope coding follows spec acceptance or phase readiness")
                require(details["source_ref"] == {"event_id": self.outputs["spec"], "kind": "spec_change_wrapper"}, "Coding requires latest spec handoff")
                require(self.inflight is None, "Recover the active writer before a new assignment")
                if self.phases:
                    require(scope["kind"] == "phase", "A phased plan needs explicit phase assignments")
                    require(scope["plan_ref"] == self.plan_ref, "Coding assignments use the current approved plan")
                    index = next(i for i, p in enumerate(self.phases) if p["id"] == scope["phase_id"])
                    require(all(self.phase_ready(p["id"]) for p in self.phases[:index]), "Earlier phases must be ready before advancement")
                    if stage in self.coder_assignments:
                        prior = self.entries[self.coder_assignments[stage]["trigger_event_id"]]["details"]
                        require(previous == "spec_approved" and scope["phase_id"] not in self.completed_phases
                                and work_scope(prior)["plan_ref"] != self.plan_ref,
                                "Existing phase assignment must be recovered, not restarted")
                    else:
                        require(not details["invocation"].get("context_id") or details["invocation"].get("context_id") not in self.phase_coders.values(), "Next phase starts in a fresh Coder context")
                    self.phase_coders[scope["phase_id"]] = details["invocation"].get("context_id")
                else:
                    require(scope["kind"] == "feature", "No phased task plan is approved")
            auth = self.authorizations.get(details["authorization_ref"]["event_id"], {})
            require(details["authorization_ref"]["event_id"] == self.coding_authorization and auth.get("kind") == "coding" and auth.get("decision") == "granted" and auth.get("scope_epoch") == self.scope_epoch,
                    "Coding needs explicit authorization for the current material scope")
            self.context(details["invocation"], "Coder", True, entry)
            self.coder_assignments[stage] = deepcopy(details["invocation"])
            self.current_scope = deepcopy(scope)
            target = "coding_in_progress"

        elif event in {"coding-updated", "coding-complete", "coding-phase-complete"}:
            require(previous in {"coding_in_progress", "blocked"}, "Coding output outside implementation")
            start = self.entries[self.starts["Coder"]["trigger_event_id"]]
            self.pair(entry, "Coder", start["requestor"])
            if event == "coding-updated":
                self.context(details["invocation"], "Coder")
                require(work_scope(details) == self.current_scope, "Coordination scope must retain its assignment")
                validate_progress(details)
                independent = any(b["independent_task_ids"] for b in details.get("blockers", []))
                target = "blocked" if details.get("blockers") and not independent else "coding_in_progress"
                self.inflight = None if details.get("yielded", False) else "Coder"
                if derive_status:
                    entry["status"] = target
                require(entry["status"] == target, f"Coordination status must be {target}")
                self.status = target
                self.entries[entry_id] = deepcopy(entry)
                return
            wrapper = entry["change_wrapper"]
            validate_wrapper("change-wrapper", wrapper)
            self.context(wrapper["context"], "Coder")
            scope = work_scope(wrapper)
            stage = self.stage(scope)
            final_phase = self.phases and self.current_scope.get("phase_id") == self.phases[-1]["id"]
            require(scope == self.current_scope or event == "coding-complete" and final_phase and scope["kind"] == "feature",
                    "Coder output must cover its assignment; only the last Coder consolidates the feature")
            self.apply_artifacts(wrapper, entry, coder=True)
            self.apply_dispositions(wrapper.get("dispositions", []), entry)
            self.outputs[stage] = entry_id
            self.inflight = None
            self.last_error = None
            if event in {"coding-complete", "coding-phase-complete"}:
                require(not wrapper.get("blockers"), "Coding completion requires unblocked output")
                require(wrapper["task_progress"] and all(t["status"] in {"completed", "dispositioned"} for t in wrapper["task_progress"]), "Required tasks remain incomplete")
                for task in wrapper["task_progress"]:
                    if task["status"] == "dispositioned":
                        auth = self.authorizations.get((task.get("disposition_ref") or {}).get("event_id"), {})
                        require(auth.get("decision") == "granted" and auth.get("kind") == "external_operation"
                                and auth.get("operation") == "accept-task-result" and auth.get("scope") == task["task_id"]
                                and auth.get("scope_epoch") == self.scope_epoch,
                                "Incomplete task needs explicit accept-task-result authority for that task")
                require(wrapper.get("checks", []), "Coding completion requires verification evidence")
                self.check_checks(wrapper.get("checks", []))
                if event == "coding-phase-complete":
                    require(scope["kind"] == "phase" and not final_phase, "Only a nonfinal phase uses coding-phase-complete")
                    phase = next(p for p in self.phases if p["id"] == scope["phase_id"])
                    require(set(phase["task_ids"]) == {t["task_id"] for t in wrapper["task_progress"]}, "Phase completion must account for exactly its assigned tasks")
                    self.completed_phases.add(phase["id"])
                    if "code" in self.outputs:
                        # Changed earlier work after final handoff needs the last
                        # Coder's renewed cumulative result and mandatory review.
                        self.completed_phases.discard(self.phases[-1]["id"])
                    target = "coding_in_progress"
                else:
                    require(scope["kind"] == "feature", "coding-complete is exclusively whole-feature completion")
                    if self.phases:
                        require(all(self.phase_ready(p["id"]) for p in self.phases[:-1]), "Final completion requires all earlier phases ready")
                        require({t for p in self.phases for t in p["task_ids"]} == {t["task_id"] for t in wrapper["task_progress"]}, "Final consolidation accounts for every phase task")
                        self.completed_phases.add(self.phases[-1]["id"])
                    self.current_scope = {"kind": "feature"}
                    target = "coding_complete"

        elif event == "review-evidence-assessed":
            phase = self.review_stage(details["review_ref"])
            role = "Architect" if phase == "spec" else "Reviewer"
            self.pair(entry, role, "Planner" if phase == "spec" else "Coder")
            context = details["invocation"]
            original = self.entries[context["trigger_event_id"]]
            require(original["actor"] == role and context["role"] == role and original["event"].endswith("review-started"), "Applicability needs an actual review-role context")
            require(self.inflight in {None, role}, "Obtain a coherent producer yield before assessment")
            require(details["source_ref"] == {"event_id": self.outputs[phase], "kind": "spec_change_wrapper" if phase == "spec" else "change_wrapper"}, "Assessment must identify the current source handoff")
            source = self.source_wrapper(phase)
            require(details["current_commit"] == source["checkpoint_commit"] and details["reviewed_artifacts"] == self.artifacts and work_scope(details) == work_scope(source), "Assessment basis disagrees with current work")
            require(all(e.get("freshness", "new") != "incomplete" and not e.get("coverage_gaps") and not e.get("uncertainty") for e in details["evidence"]) or details["conclusion"] != "applicable", "Incomplete/uncertain assessment cannot establish applicability")
            self.assessments.append(deepcopy(details))

        elif event == "user-override":
            self.pair(entry, "User", "User")
            targets = [c["target"] for c in details["changes"]]
            require(len(set(targets)) == len(targets) and not any(a != b and b.startswith(a + "/") for a in targets for b in targets), "Overlapping override targets")
            require(not self.phases or "/capability/roles/reviewer" not in targets, "Phased Reviewer changes require a complete capability replacement")
            for change in details["changes"]:
                keys = change["target"].strip("/").split("/")
                parent = self.config
                for key in keys[:-1]:
                    parent = parent[key]
                require(parent[keys[-1]] == change["previous"], "Override previous value does not match effective configuration")
                parent[keys[-1]] = deepcopy(change["new"])
            validate_capability(self.config)
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

        if derive_status:
            entry["status"] = target
        require(entry["status"] == target, f"{event}: resulting status must be {target}, got {entry['status']}")
        self.status = target
        self.entries[entry_id] = deepcopy(entry)
        self.refresh_gaps()
        # A catch-up/repair of an earlier phase does not erase an already-started
        # later assignment. Once ready, recover that same writer and baseline.
        current_id = self.current_scope.get("phase_id")
        if self.status == "coding_in_progress" and current_id in self.completed_phases and self.phase_ready(current_id):
            index = next(i for i, p in enumerate(self.phases) if p["id"] == current_id)
            for phase in self.phases[index + 1:]:
                next_stage = "phase:" + phase["id"]
                if phase["id"] in self.completed_phases:
                    if not self.phase_ready(phase["id"]):
                        self.current_scope = {"kind": "phase", "phase_id": phase["id"], "plan_ref": deepcopy(self.plan_ref)}
                        break
                    continue
                if next_stage in self.coder_assignments:
                    self.starts["Coder"] = deepcopy(self.coder_assignments[next_stage])
                    start = self.entries[self.starts["Coder"]["trigger_event_id"]]
                    self.current_scope = deepcopy(work_scope(start["details"]))
                    self.inflight = "Coder"
                break

    def known_issues(self):
        issues = {}
        for fid, finding in self.findings.items():
            if finding.get("resolved"):
                continue
            disposition = self.dispositions.get(fid)
            if finding["severity"] == "nit" and disposition is None:
                disposition = {"decision": "defer", "authority": "policy",
                               "rationale": "Nonblocking nit; revisit with relevant work or user direction."}
            if disposition and disposition["decision"] in {"defer", "accept_limitation"} and (
                    finding["severity"] == "nit" or self.disposition_allowed(fid, disposition)):
                issues[fid] = {"finding": finding, "disposition": disposition}
        return issues

    def next_action(self):
        if self.status == "implementation_complete":
            return "finish_final_checkpoint_then_squash_message"
        if self.last_error and self.inflight:
            gate = self.role_recovery_gate(self.last_error["invocation"])
            if gate:
                return gate
        if self.inflight == "Coder" and "spec" in self.assurance_gaps:
            return "yield_coder_for_assurance_review"
        if self.inflight == "Coder" and any(p["id"] in self.completed_phases and
                p["id"] != self.current_scope.get("phase_id") and not self.phase_ready(p["id"]) for p in self.phases[:-1]):
            return "yield_coder_for_phase_review"
        if self.status == "blocked":
            return "resolve_scoped_blocker"
        if self.inflight:
            return "recover_invocation_or_output"
        if "spec" in self.assurance_gaps and self.status not in {"spec_in_progress", "spec_changes_requested", "spec_ready"}:
            return "review_assurance_gap_spec"
        if self.status in {"spec_approved", "coding_in_progress", "coding_complete", "code_approved"}:
            for phase in self.phases[:-1]:
                stage = "phase:" + phase["id"]
                if phase["id"] in self.completed_phases and not self.phase_ready(phase["id"]):
                    if not self.config["capability"].get("stage_assignments", {}).get("intermediate_reviewer"):
                        return "resolve_intermediate_reviewer_assignment"
                    return "review_assurance_gap_" + stage if stage in self.reviews else "start_phase_review"
        if "code" in self.assurance_gaps and self.status == "code_approved":
            return "review_assurance_gap_code"
        if self.status == "spec_in_progress":
            if self.feedback_ref:
                return "continue_planner_" + self.earliest_artifact
            if not any(self.artifacts.values()) and "spec" in self.outputs and self.source_wrapper("spec").get("questions"):
                return "obtain_planner_clarification"
            for name in ARTIFACTS:
                if self.artifacts[name] and name not in self.approvals:
                    return "obtain_" + name + "_approval"
                if not self.artifacts[name]:
                    return "continue_planner_" + name
            return "obtain_consolidated_spec_output"
        if self.status in {"spec_ready"}:
            return "start_architect_review"
        if self.status == "spec_approved":
            if "spec" in self.assurance_gaps:
                return "review_assurance_gap_spec"
            auth = self.authorizations.get(self.coding_authorization, {})
            return "start_coder" if auth.get("decision") == "granted" and auth.get("scope_epoch") == self.scope_epoch else "obtain_coding_authorization"
        if self.status == "code_approved":
            return "obtain_final_user_acceptance"
        for phase in (("spec",) if self.status.startswith("spec_") else (self.stage(self.current_scope),)):
            family = self.family(phase)
            if self.status in {family + "_changes_requested"}:
                if phase == "spec" and self.user_revision_pending:
                    return "start_planner_revision"
                if any(d["decision"] in {"reconsider", "clarify"} for fid, d in self.dispositions.items() if self.findings[fid]["phase"] == phase and not self.findings[fid].get("resolved")):
                    return "reconsider_" + phase + "_review"
                return self.repair_gate(phase) or ("start_planner_revision" if phase == "spec" else "start_coder_revision")
        if self.phases and self.status == "coding_in_progress":
            if self.current_scope.get("phase_id") in self.completed_phases:
                return "start_next_phase_coder"
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
    elif observations.get("unrecorded_output") is not None:
        output = observations["unrecorded_output"]
        require(isinstance(output, dict) and output.get("event") in {*WRAPPERS, "review-evidence-assessed"},
                "Recovered output must be an actual role return, not a user decision or pointer")
        candidate = deepcopy(log)
        candidate["history"].append(output)
        candidate["status"] = output.get("status")
        replay(candidate, previous=log)
        action = "record_recovered_output"
    elif observations.get("unrecorded_approval") is not None:
        approval = observations["unrecorded_approval"]
        require(isinstance(approval, dict) and approval.get("event") == "spec-artifact-approved", "Recovered approval must be an actual artifact decision")
        candidate = deepcopy(log)
        candidate["history"].append(approval)
        candidate["status"] = approval.get("status")
        replay(candidate, previous=log)
        action = "record_recovered_approval"
    elif state.inflight:
        invocation = observations.get("invocation", "unknown")
        if action == "recover_invocation_or_output":
            action = {"running": "recover_running_invocation", "completed": "record_recovered_output", "paused": "continue_existing_role_context",
                      "not_started": "invoke_recorded_role"}.get(invocation, "establish_invocation_liveness")
            if state.inflight == "Coder" and invocation == "completed":
                action = "recover_cumulative_coder_output"
    elif observations.get("artifact_handoff_pending"):
        action = "recover_required_role_return"
    if (delivery == "delivered" and state.last_error and state.inflight
            and not observations.get("unrecorded_output") and not observations.get("unrecorded_approval")
            and observations.get("invocation") in {"completed", "paused", "not_started"}
            and state.role_recovery_gate(state.last_error["invocation"]) is None):
        action = "retry_role"
    role = state.inflight or ({"spec_in_progress": "Planner", "coding_in_progress": "Coder", "blocked": "Coder"}.get(state.status))
    active = state.active_context(role) if role in state.starts else None
    return {"status": state.status, "action": action, "workflow_action": state.next_action(),
            "active_assignment": deepcopy(active),
            "capability": state.assignment(state.config, role, active) if active else None,
            "configuration": state.config, "configuration_ref": state.config_ref,
            "artifacts": state.artifacts, "approval_bases": state.approvals, "repair_cycles": state.cycles,
            "assurance_gaps": sorted(state.assurance_gaps), "known_issues": state.known_issues(),
            "work_scope": state.current_scope,
            "phase_readiness": {p["id"]: state.phase_ready(p["id"]) for p in state.phases[:-1]}}
