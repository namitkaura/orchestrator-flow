"""Small coherent histories used by scenario tests and distributed examples."""
from copy import deepcopy


def reference(event_id, kind="event"):
    return {"event_id": str(event_id), "kind": kind}


def evidence(freshness="new"):
    return {"sources": [{"ref": "src/example.py", "context": "Feature baseline and current working changes inspected"}],
            "observations": ["The implemented branch meets the approved acceptance criterion."],
            "inferences": [], "coverage_gaps": [], "uncertainty": [], "assumptions": ["The approved deployment remains local."],
            "freshness": freshness, "applicability_check": "Compared relevant source content and deployment assumptions with the prior inspection."}


def finding(identity, basis="demonstrated_defect"):
    return {"id": identity, "file": "src/example.py", "description": "The empty-input branch does not meet its required result.",
            "rationale": "An explicit acceptance criterion is violated in the agreed deployment.",
            "triggering_conditions": "The caller supplies an empty input.", "practical_consequences": "The user's ordinary local operation fails.",
            "basis": basis, "source_refs": ["requirements.md criterion 1.1", "src/example.py empty-input branch"], "reconsideration_reason": None}


def disposition(fid, decision="fix", authority="user", authority_ref=None):
    return {"finding_id": fid, "decision": decision, "rationale": "The user selected this response for the intended deployment.",
            "authority": authority, "authority_ref": authority_ref, "revisit_condition": None, "workaround": None}


class Flow:
    def __init__(self, assurance="standard", policy="spec_user_code_auto", baseline="a" * 40):
        self.log = {"feature": "example", "feature_dir": ".docs/specs/example", "workflow_version": "2.0.0",
                    **{name + "_ref": f".docs/specs/example/{name}.md" for name in ("requirements", "design", "tasks")},
                    "task_log_ref": ".docs/specs/example/task_log.json", "assurance_level": assurance,
                    "capability": {"platform": "codex", "roles": {role: {"model": "example-model", "reasoning_effort": "high"}
                        for role in ("planner", "architect", "coder", "reviewer", "helpers")}, "acknowledged_limitations": []},
                    "review_disposition_policy": policy, "branch_context": {"feature_branch": "feature/example", "integration_branch": "main", "remote": "origin", "baseline_commit": baseline},
                    "status": "spec_in_progress", "history": []}
        self.artifacts = dict.fromkeys(("requirements", "design", "tasks"))
        self.contexts = {}
        self.outputs = {}
        self.reviews = {}
        self.produced = {}
        self.approvals = {}
        self.config_ref = "1"
        self.authorization = None
        self.spec_requestor = "User"
        self.code_requestor = "Planner"
        self.handed_off = False
        self.checkpoint_commit = "b" * 40
        self.implementation_phases = []
        context = self.context("Planner", start=True)
        self.add("spec-creation-started", "Planner", "User", "spec_in_progress", details={
            "request": "Support the agreed local input behavior.", "references": [], "earliest_artifact": "requirements", "invocation": context,
            "initial_configuration": self.configuration(), "branch_context": deepcopy(self.log["branch_context"]), "user_acceptance": "Use these assignments and assurance for this feature."})

    @property
    def next_id(self):
        return str(len(self.log["history"]) + 1)

    def configuration(self):
        return deepcopy({key: self.log[key] for key in ("assurance_level", "capability", "review_disposition_policy")})

    def context(self, role, start=False):
        if start:
            self.contexts[role] = {"trigger_event_id": self.next_id, "role": role, "attempt": 1,
                                   "context_id": role.lower() + "-session", "configuration_ref": self.config_ref}
        return deepcopy(self.contexts[role])

    def add(self, event, actor, requestor, status, **payload):
        entry = {"id": self.next_id, "timestamp": "2026-09-30T12:00:00Z", "event": event, "actor": actor, "requestor": requestor, "status": status, **deepcopy(payload)}
        self.log["history"].append(entry)
        self.log["status"] = status
        return entry["id"]

    def spec_output(self, artifact=None, change_kind="material", consolidated=False, dispositions=None):
        changes = []
        if artifact:
            old = self.artifacts[artifact]
            version = old["version"] + 1 if old else 1
            self.artifacts[artifact] = {"ref": self.log[artifact + "_ref"], "version": version}
            changes = [{"artifact": artifact, "previous_version": old["version"] if old else None, "current_version": version,
                        "change_kind": change_kind, "summary": "Record the current approved behavior and its rationale.",
                        "rationale": "Make this artifact actionable for its downstream consumer.",
                        "approval_basis_ref": reference(self.approvals[artifact], "approval") if change_kind != "material" and artifact in self.approvals else None}]
            self.produced[artifact] = self.next_id
        wrapper = {"context": self.context("Planner"), "checkpoint_commit": self.checkpoint_commit if any(self.artifacts.values()) else None,
                   "implementation_phases": deepcopy(self.implementation_phases), "notes": "No hidden decisions.", "feature": self.log["feature"], "feature_dir": self.log["feature_dir"],
                   **{n + "_ref": v["ref"] if v else None for n, v in self.artifacts.items()}, "user_request": {"original_request": "Support the agreed local input behavior.", "additional_context": ""},
                   "output_kind": "consolidated" if consolidated else "incremental", "artifacts": deepcopy(self.artifacts), "artifact_changes": changes,
                   "causes": [], "decisions": ["Manual retry is adequate for the accepted deployment."], "constraints": ["Preserve existing nonempty-input behavior."],
                   "downstream_impacts": [], "dispositions": dispositions or [], "questions": [], "research_updates": []}
        event = "spec-updated" if self.handed_off or not consolidated else "spec-created"
        status = ("spec_updated" if self.handed_off else "spec_created") if consolidated else "spec_in_progress"
        self.outputs["spec"] = self.add(event, "Planner", self.spec_requestor, status, spec_change_wrapper=wrapper)
        self.handed_off |= consolidated
        return wrapper

    def approve(self, name):
        self.approvals[name] = self.add("spec-artifact-approved", "User", "Planner", "spec_in_progress", details={
            "artifact": name, "version": self.artifacts[name]["version"], "output_ref": reference(self.produced[name], "spec_change_wrapper"), "user_statement": "I approve this document version."})

    def finish_spec(self):
        for name in self.artifacts:
            self.spec_output(name)
            self.approve(name)
        self.spec_output(consolidated=True)
        return self

    def start_review(self, phase):
        role, requestor = ("Architect", "Planner") if phase == "spec" else ("Reviewer", "Coder")
        self.add(phase + "-review-started", role, requestor, phase + "_in_review", details={
            "source_ref": reference(self.outputs[phase], "spec_change_wrapper" if phase == "spec" else "change_wrapper"),
            "prior_review_ref": reference(self.reviews[phase], phase + "_review") if phase in self.reviews else None,
            "review_kind": "follow_up" if phase in self.reviews else "initial", "invocation": self.context(role, start=True)})

    def review_output(self, phase, issues=None, accepted="true", resolved=None, dispositions=None, scope="full", repair_class="bounded_correctness", freshness="new"):
        role, requestor = ("Architect", "Planner") if phase == "spec" else ("Reviewer", "Coder")
        followup = phase in self.reviews
        source = self.log["history"][int(self.outputs[phase]) - 1]
        wrapper = {"context": self.context(role), "reviewed_commit": source["spec_change_wrapper" if phase == "spec" else "change_wrapper"]["checkpoint_commit"],
                   "notes": "Inspected current sources and applicable prior decisions.", "accepted": accepted,
                   "issue_details": issues or {"must_fix": [], "should_fix": [], "nit": []}, "dispositions": dispositions or [],
                   "reviewed_artifacts": deepcopy(self.artifacts), "reviewed_output_ref": reference(self.outputs[phase], "spec_change_wrapper" if phase == "spec" else "change_wrapper"),
                   "prior_review_ref": reference(self.reviews[phase], phase + "_review") if followup else None,
                   "review_kind": "follow_up" if followup else "initial", "assurance_level": self.log["assurance_level"], "review_disposition_policy": self.log["review_disposition_policy"],
                   "repair_class": repair_class if followup else None, "changed_surfaces": ["src/example.py"], "review_scope": scope,
                   "scope_reason": "Cover the complete relevant work on the initial pass; verify affected contracts on repair.", "meaningful_change": True,
                   "evidence": [evidence(freshness)], "resolved_findings": resolved or []}
        if phase == "code":
            wrapper.update(test_results=self.test_results(), checks=self.checks())
        status = phase + {"true": "_approved", "false": "_changes_requested", "conditional": "_conditionally_approved"}[accepted]
        self.reviews[phase] = self.add(phase + "-reviewed", role, requestor, status, **{("spec_review_wrapper" if phase == "spec" else "review_wrapper"): wrapper})
        return wrapper

    def review(self, phase, **kwargs):
        self.start_review(phase)
        return self.review_output(phase, **kwargs)

    def authorize(self, kind="coding", decision="granted", phase=None, failures=None, operation=None, uncertain=None):
        references = [reference(self.reviews[phase or "spec"], (phase or "spec") + "_review")] if kind in {"coding", "repair_cycle"} else []
        event_id = self.add("user-authorization-recorded", "User", "User", self.log["status"], details={
            "kind": kind, "decision": decision, "operation": operation or {"coding": "implement-approved-spec", "repair_cycle": "continue-repair", "checkpoint_recovery": "retry-checkpoint-push", "external_operation": "external-operation"}[kind],
            "scope": "Current approved feature scope", "references": references, "limits": {"max_attempts": 1 if kind == "checkpoint_recovery" else None, "additional_cycles": 1 if kind == "repair_cycle" else None, "phase": phase},
            "user_statement": "Proceed within these explicit limits." if decision == "granted" else "Wait for further direction.", "failed_attempts": failures or []})
        if uncertain is not None:
            self.log["history"][-1]["details"]["uncertain_attempts"] = deepcopy(uncertain)
        if kind == "coding" and decision == "granted":
            self.authorization = event_id
        return event_id

    def start_coding(self, revision=False):
        self.code_requestor = "Reviewer" if revision else "Planner"
        self.add("coding-revision-started" if revision else "coding-started", "Coder", self.code_requestor, "coding_in_progress", details={
            "source_ref": reference(self.reviews["code"], "code_review") if revision else reference(self.outputs["spec"], "spec_change_wrapper"),
            "authorization_ref": reference(self.authorization, "authorization"), "invocation": self.context("Coder", start=True)})

    @staticmethod
    def test_results():
        return {kind: {"status": "pass", "details": "The relevant behavioral checks passed."} for kind in ("unit_tests", "integration_tests")}

    @staticmethod
    def checks():
        return [{"name": "behavioral-tests", "status": "pass", "required": True, "details": "Expected result and preservation witness passed.", "disposition_ref": None}]

    def code_output(self, consolidated=True, blockers=None, dispositions=None, progress=False):
        changes = []
        if progress:
            old = self.artifacts["tasks"]["version"]
            changes = [{"artifact": "tasks", "previous_version": old, "current_version": old, "change_kind": "progress", "summary": "Mark task 1 complete.",
                        "rationale": "The behavioral witness passed.", "approval_basis_ref": reference(self.approvals["tasks"], "approval")}]
        wrapper = {"context": self.context("Coder"), "checkpoint_commit": self.checkpoint_commit,
                   "notes": "No unrelated changes.", "output_kind": "consolidated" if consolidated else "incremental",
                   "artifacts": deepcopy(self.artifacts), "artifact_changes": changes, "changed_files": ["src/example.py"], "new_files": ["tests/test_example.py"], "deleted_files": [],
                   "cli_runs": ["python -m unittest"], "test_results": self.test_results(), "checks": self.checks(), "implementation_details": "Implemented and verified the approved input behavior.",
                   "task_progress": [{"task_id": "1", "status": "completed", "evidence": "Behavioral witness passes.", "disposition_ref": None}],
                   "blockers": blockers or [], "dispositions": dispositions or [], "causes": [], "cumulative_scope": ["src/example.py", "tests/test_example.py"], "evidence": [evidence()]}
        status = "coding_complete" if consolidated else ("blocked" if blockers and not any(b["independent_task_ids"] for b in blockers) else "coding_in_progress")
        self.outputs["code"] = self.add("coding-complete" if consolidated else "coding-updated", "Coder", self.code_requestor, status, change_wrapper=wrapper)
        return wrapper

    def user_dispositions(self, phase, values, accepted="false"):
        status = phase + {"true": "_approved", "false": "_changes_requested", "conditional": "_conditionally_approved"}[accepted]
        return self.add("review-findings-dispositioned", "User", "Architect" if phase == "spec" else "Reviewer", status,
                        details={"review_ref": reference(self.reviews[phase], phase + "_review"), "decisions": values, "user_statement": "Use these finding decisions."})

    def start_spec_revision(self, requestor="Architect", earliest="requirements"):
        self.spec_requestor = requestor
        self.add("spec-revision-started", "Planner", requestor, "spec_in_progress", details={"request": "Apply the recorded decisions.",
                 "references": [reference(self.reviews["spec"], "spec_review")] if requestor == "Architect" else [], "earliest_artifact": earliest, "invocation": self.context("Planner", start=True)})

    def override(self, target, value):
        keys = target.strip("/").split("/")
        parent = self.log
        for key in keys[:-1]:
            parent = parent[key]
        old = deepcopy(parent[keys[-1]])
        parent[keys[-1]] = deepcopy(value)
        self.config_ref = self.add("user-override", "User", "User", self.log["status"], details={"changes": [{"target": target, "previous": old, "new": value}], "rationale": "The user selected this configuration.", "user_statement": "Use the new value for this feature."})

    def complete(self, known_issues=None):
        self.add("implementation-complete", "Orchestrator", "User", "implementation_complete", details={"review_ref": reference(self.reviews["code"], "code_review"), "user_statement": "I accept this feature and its disclosed limitations.", "known_issues": known_issues or [], "summary": "Delivered and verified the approved behavior."})
        return self


def complete_flow(assurance="standard", policy="spec_user_code_auto", baseline="a" * 40):
    flow = Flow(assurance, policy, baseline).finish_spec()
    flow.review("spec")
    flow.authorize()
    flow.start_coding()
    flow.code_output(progress=True)
    flow.review("code")
    return flow.complete()
