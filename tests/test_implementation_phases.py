"""Behavioral phase gates, stage evidence and cumulative final ownership."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".codex/skills/orchestrator-flow/scripts"))
from workflow_artifacts import ValidationError
from workflow_protocol import replay, resume_action
from flow_fixtures import Flow, evidence, finding, disposition, reference


class PhasedFlow(Flow):
    def __init__(self, assurance="standard", assignment=True, phases=None):
        super().__init__(assurance, "within_scope_auto")
        self.implementation_phases = phases or [
            {"id": "P1", "title": "Foundations", "task_ids": ["1", "2"]},
            {"id": "P2", "title": "Integration, Test-Maintenance and Verification", "task_ids": ["3", "4", "5"]}]
        self.phase_reviews = {}
        self.phase_outputs = {}
        if assignment:
            capability = deepcopy(self.log["capability"])
            capability["stage_assignments"] = {"intermediate_reviewer": {"model": "example-model", "reasoning_effort": "low"}}
            self.override("/capability", capability)
        self.finish_spec()
        self.review("spec")
        self.authorize()

    def scope(self, phase):
        return {"kind": "phase", "phase_id": phase, "plan_ref": reference(self.outputs["spec"], "spec_change_wrapper")}

    def start_phase(self, phase, revision=False, context=None):
        if revision:
            self.reviews["code"] = self.phase_reviews[phase]
        self.start_coding(revision)
        details = self.log["history"][-1]["details"]
        details["work_scope"] = self.scope(phase)
        details["invocation"]["context_id"] = context or "coder-" + phase
        self.contexts["Coder"] = deepcopy(details["invocation"])

    def finish_phase(self, phase, dispositions=None):
        self.code_output(dispositions=dispositions, progress=True)
        entry = self.log["history"][-1]
        wrapper = entry["change_wrapper"]
        if phase != self.implementation_phases[-1]["id"]:
            wrapper["work_scope"] = self.scope(phase)
            entry["event"] = "coding-phase-complete"
            entry["status"] = self.log["status"] = "coding_in_progress"
            task_ids = next(p["task_ids"] for p in self.implementation_phases if p["id"] == phase)
        else:
            wrapper["work_scope"] = {"kind": "feature"}
            task_ids = [t for p in self.implementation_phases for t in p["task_ids"]]
            wrapper["causes"] = [reference(output, "change_wrapper") for output in self.phase_outputs.values()]
            self.reviews.pop("code", None)
        wrapper["task_progress"] = [{"task_id": task, "status": "completed", "evidence": "Assigned behavioral and integration checks pass.", "disposition_ref": None} for task in task_ids]
        self.phase_outputs[phase] = entry["id"]
        return wrapper

    def phase_review(self, phase="P1", **kwargs):
        self.outputs["code"] = self.phase_outputs[phase]
        if phase in self.phase_reviews:
            self.reviews["code"] = self.phase_reviews[phase]
        else:
            self.reviews.pop("code", None)
        self.start_review("code")
        self.log["history"][-1]["details"]["work_scope"] = self.scope(phase)
        wrapper = self.review_output("code", **kwargs)
        wrapper["work_scope"] = self.scope(phase)
        wrapper["assurance_level"] = {"standard": "basic", "maximum": "standard"}[self.log["assurance_level"]]
        entry = self.log["history"][-1]
        entry["review_wrapper"] = deepcopy(wrapper)
        if wrapper["accepted"] == "true":
            entry["status"] = self.log["status"] = "coding_in_progress"
        self.phase_reviews[phase] = entry["id"]
        return wrapper


class PhaseTests(unittest.TestCase):
    def test_consolidation_cannot_replace_the_approved_phase_plan(self):
        flow = Flow()
        flow.implementation_phases = PhasedFlow().implementation_phases
        for name in flow.artifacts:
            flow.spec_output(name)
            flow.approve(name)
        flow.spec_output(consolidated=True)
        self.assertEqual(replay(flow.log).phases, flow.implementation_phases)
        replacement = deepcopy(flow.implementation_phases)
        replacement[0]["task_ids"] = ["1"]
        replacement[1]["task_ids"] = ["2", "3", "4", "5"]
        for phases in ([], replacement):
            with self.subTest(phases=phases):
                broken = deepcopy(flow.log)
                handoff = broken["history"][-1]
                handoff["spec_change_wrapper"]["implementation_phases"] = phases
                with self.assertRaisesRegex(ValidationError, "tasks.*phase plan"):
                    replay(broken)

    def test_changed_phase_boundaries_require_tasks_revision_and_approval(self):
        flow = PhasedFlow("basic", assignment=False)
        request = flow.add("user-change-requested", "Orchestrator", "User", "spec_changes_requested", details={
            "request": "Move task 2 into the final phase.", "earliest_artifact": "tasks", "references": []})
        flow.start_spec_revision("User", "tasks")
        flow.implementation_phases[0]["task_ids"] = ["1"]
        flow.implementation_phases[1]["task_ids"] = ["2", "3", "4", "5"]
        editorial = deepcopy(flow)
        editorial.spec_output("tasks", change_kind="editorial")
        editorial.log["history"][-1]["spec_change_wrapper"]["causes"] = [reference(request)]
        with self.assertRaisesRegex(ValidationError, "phase plan.*material"):
            replay(editorial.log)
        flow.spec_output("tasks")
        flow.log["history"][-1]["spec_change_wrapper"]["causes"] = [reference(request)]
        before_approval = deepcopy(flow)
        before_approval.spec_output(consolidated=True)
        self.assertEqual(replay(before_approval.log).status, "spec_in_progress")
        before_approval.start_review("spec")
        with self.assertRaises(ValidationError):
            replay(before_approval.log)
        flow.approve("tasks")
        flow.spec_output(consolidated=True)
        state = replay(flow.log)
        self.assertEqual(state.phases, flow.implementation_phases)
        self.assertEqual(state.approvals["tasks"]["version"], 2)

    def test_editorial_phase_title_keeps_the_existing_tasks_approval(self):
        flow = PhasedFlow("basic", assignment=False)
        approval = deepcopy(replay(flow.log).approvals["tasks"])
        request = flow.add("user-change-requested", "Orchestrator", "User", "spec_changes_requested", details={
            "request": "Clarify the phase heading without changing its scope.", "earliest_artifact": "tasks", "references": []})
        flow.start_spec_revision("User", "tasks")
        flow.implementation_phases[0]["title"] = "Foundation checks"
        flow.spec_output("tasks", change_kind="editorial")
        flow.log["history"][-1]["spec_change_wrapper"]["causes"] = [reference(request)]
        flow.spec_output(consolidated=True)
        state = replay(flow.log)
        self.assertEqual(state.approvals["tasks"], approval)
        self.assertEqual(state.phases, flow.implementation_phases)

    def test_final_review_repairs_cannot_use_an_earlier_phase_review(self):
        for severity, accepted in (("must_fix", "false"), ("should_fix", "conditional")):
            with self.subTest(severity=severity):
                flow = PhasedFlow("maximum")
                flow.start_phase("P1")
                flow.finish_phase("P1")
                flow.phase_review()
                flow.start_phase("P2")
                final_context = flow.context("Coder")
                cumulative = deepcopy(flow.finish_phase("P2"))
                fid = "C-" + flow.next_id + "-1"
                issues = {"must_fix": [], "should_fix": [], "nit": []}
                issues[severity] = [finding(fid)]
                flow.review("code", issues=issues, accepted=accepted)
                wrong = deepcopy(flow)
                wrong.start_phase("P1", revision=True)
                with self.assertRaisesRegex(ValidationError, "active review scope"):
                    replay(wrong.log)
                flow.start_coding(revision=True)
                flow.log["history"][-1]["details"]["invocation"]["context_id"] = final_context["context_id"]
                flow.contexts["Coder"] = deepcopy(flow.log["history"][-1]["details"]["invocation"])
                state = replay(flow.log)
                self.assertEqual(state.current_scope, {"kind": "feature"})
                self.assertTrue(state.repair_pending["code"])
                self.assertFalse(state.repair_pending["phase:P1"])
                self.assertEqual(state.starts["Coder"]["context_id"], final_context["context_id"])
                flow.code_output()
                flow.log["history"][-1]["change_wrapper"]["task_progress"] = cumulative["task_progress"]
                flow.review("code", resolved=[fid])
                state = replay(flow.log)
                self.assertEqual(state.cycles["code"], 1)
                self.assertEqual(state.cycles["phase:P1"], 0)
                flow.complete()
                self.assertEqual(replay(flow.log).status, "implementation_complete")

    def test_approved_revision_rebinds_unfinished_phase_and_preserves_completed_history(self):
        for level in ("basic", "standard"):
            with self.subTest(level=level):
                flow = PhasedFlow(level, assignment=level != "basic")
                flow.start_phase("P1")
                flow.finish_phase("P1")
                old_scope = flow.scope("P1")
                completed_output = flow.phase_outputs["P1"]
                if level != "basic":
                    flow.phase_review()
                flow.start_phase("P2")
                original_context = flow.context("Coder")
                flow.add("coding-updated", "Coder", "Planner", "coding_in_progress", details={
                    "invocation": original_context, "work_scope": flow.scope("P2"), "yielded": True,
                    "summary": "Yield for a user-selected revision to remaining integration work.", "task_progress": [], "blockers": [], "references": []})
                request = flow.add("user-change-requested", "Orchestrator", "User", "spec_changes_requested", details={
                    "request": "Add the approved final verification task.", "earliest_artifact": "tasks", "references": []})
                flow.start_spec_revision("User", "tasks")
                flow.implementation_phases[-1]["title"] = "Revised integration and final verification"
                flow.implementation_phases[-1]["task_ids"].append("6")
                flow.spec_output("tasks")
                flow.log["history"][-1]["spec_change_wrapper"]["causes"] = [reference(request)]
                flow.approve("tasks")
                flow.spec_output(consolidated=True)
                rejected = deepcopy(flow)
                fid = "S-" + rejected.next_id + "-1"
                rejected.review("spec", issues={"must_fix": [finding(fid)], "should_fix": [], "nit": []}, accepted="false")
                self.assertEqual(replay(rejected.log).next_action(), "start_planner_revision")
                flow.review("spec")
                if level != "basic":
                    self.assertEqual(replay(flow.log).next_action(), "review_assurance_gap_phase:P1")
                    flow.phase_review()
                    flow.log["history"][-2]["details"]["work_scope"] = old_scope
                    flow.log["history"][-1]["review_wrapper"]["work_scope"] = old_scope
                    flow.log["history"][-1]["status"] = flow.log["status"] = "spec_approved"
                flow.authorize()
                self.assertEqual(resume_action(flow.log, {"delivery": "delivered"})["action"], "start_coder")
                counts = deepcopy(replay(flow.log).cycles)
                flow.start_phase("P2", context=original_context["context_id"])
                state = replay(flow.log)
                self.assertEqual(state.current_scope, flow.scope("P2"))
                self.assertEqual(state.cycles, counts)
                self.assertEqual(state.outputs["phase:P1"], completed_output)
                duplicate = deepcopy(flow)
                duplicate.start_phase("P2")
                with self.assertRaises(ValidationError):
                    replay(duplicate.log)
                flow.finish_phase("P2")
                flow.review("code")
                flow.complete()
                self.assertEqual(replay(flow.log).status, "implementation_complete")

    def test_phase_gap_after_final_handoff_returns_to_final_review_without_reopening_coding(self):
        flow = PhasedFlow("maximum")
        flow.override("/assurance_level", "basic")
        flow.start_phase("P1")
        flow.finish_phase("P1")
        flow.start_phase("P2")
        flow.finish_phase("P2")
        flow.override("/assurance_level", "maximum")
        self.assertEqual(replay(flow.log).next_action(), "start_phase_review")
        premature = deepcopy(flow)
        premature.start_review("code")
        with self.assertRaisesRegex(ValidationError, "phase readiness"):
            replay(premature.log)
        final_output = flow.outputs["code"]
        flow.phase_review("P1")
        flow.log["history"][-1]["status"] = flow.log["status"] = "coding_complete"
        self.assertEqual(replay(flow.log).next_action(), "start_reviewer_review")
        self.assertEqual(replay(flow.log).current_scope, {"kind": "feature"})
        flow.outputs["code"] = final_output
        flow.reviews.pop("code", None)
        flow.review("code")
        flow.complete()
        self.assertEqual(replay(flow.log).status, "implementation_complete")

    def test_multiple_completed_phases_catch_up_before_restoring_active_writer(self):
        flow = PhasedFlow("maximum", phases=[{"id": "P1", "title": "One", "task_ids": ["1"]},
            {"id": "P2", "title": "Two", "task_ids": ["2"]},
            {"id": "P3", "title": "Final integration and verification", "task_ids": ["3", "4", "5"]}])
        flow.override("/assurance_level", "basic")
        for phase in ("P1", "P2"):
            flow.start_phase(phase)
            flow.finish_phase(phase)
        flow.start_phase("P3")
        active = flow.context("Coder")
        flow.override("/assurance_level", "maximum")
        flow.add("coding-updated", "Coder", "Planner", "coding_in_progress", details={
            "invocation": active, "work_scope": flow.scope("P3"), "yielded": True,
            "summary": "Coherent yield for required earlier phase reviews.", "task_progress": [], "blockers": [], "references": []})
        flow.phase_review("P1")
        state = replay(flow.log)
        self.assertIsNone(state.inflight)
        self.assertEqual(state.current_scope, flow.scope("P2"))
        self.assertEqual(state.next_action(), "start_phase_review")
        flow.phase_review("P2")
        state = replay(flow.log)
        self.assertEqual(state.starts["Coder"], active)
        self.assertEqual(state.current_scope, flow.scope("P3"))
        self.assertEqual(state.assurance_gaps, set())

    def test_inflight_intermediate_review_can_return_after_basic_override(self):
        flow = PhasedFlow()
        flow.start_phase("P1")
        flow.finish_phase("P1")
        flow.start_review("code")
        flow.log["history"][-1]["details"]["work_scope"] = flow.scope("P1")
        fid = "C-" + flow.contexts["Reviewer"]["trigger_event_id"] + "-1"
        flow.override("/assurance_level", "basic")
        flow.review_output("code", issues={"must_fix": [finding(fid)], "should_fix": [], "nit": []}, accepted="false")
        flow.log["history"][-1]["review_wrapper"]["work_scope"] = flow.scope("P1")
        state = replay(flow.log)
        self.assertEqual(state.next_action(), "start_coder_revision")
        self.assertEqual(state.current_scope, flow.scope("P1"))

    def test_assurance_catchup_restores_suspended_later_coder_without_new_assignment(self):
        flow = PhasedFlow("maximum")
        flow.override("/assurance_level", "basic")
        flow.start_phase("P1")
        flow.finish_phase("P1")
        flow.start_phase("P2")
        p2_context = flow.context("Coder")
        flow.override("/assurance_level", "maximum")
        self.assertEqual(replay(flow.log).next_action(), "yield_coder_for_phase_review")
        self.assertEqual(resume_action(flow.log, {"delivery": "delivered", "invocation": "paused"})["action"], "yield_coder_for_phase_review")
        flow.add("coding-updated", "Coder", "Planner", "coding_in_progress", details={
            "invocation": p2_context, "work_scope": flow.scope("P2"), "yielded": True,
            "summary": "Paused at a coherent boundary for earlier-phase assurance catch-up.", "task_progress": [], "blockers": [], "references": []})
        self.assertIsNone(replay(flow.log).inflight)
        fid = "C-" + flow.next_id + "-1"
        flow.phase_review(issues={"must_fix": [finding(fid)], "should_fix": [], "nit": []}, accepted="false")
        self.assertEqual(replay(flow.log).current_scope, flow.scope("P1"))
        flow.start_phase("P1", revision=True)
        flow.finish_phase("P1")
        flow.phase_review(resolved=[fid])
        state = replay(flow.log)
        self.assertEqual(state.current_scope, flow.scope("P2"))
        self.assertEqual(state.starts["Coder"], p2_context)
        self.assertEqual(state.cycles["phase:P1"], 1)
        self.assertEqual(resume_action(flow.log, {"delivery": "delivered", "invocation": "paused"})["action"], "continue_existing_role_context")
        flow.contexts["Coder"] = p2_context
        flow.code_requestor = "Planner"
        continued = replay(flow.log)
        self.assertEqual(continued.active_context("Coder")["trigger_event_id"], p2_context["trigger_event_id"])
        self.assertEqual(continued.active_context("Coder")["context_id"], p2_context["context_id"])
        self.assertEqual(continued.cycles, state.cycles)
        flow.finish_phase("P2")
        self.assertEqual(replay(flow.log).status, "coding_complete")

    def test_all_levels_finish_only_through_whole_feature_review(self):
        for level in ("basic", "standard", "maximum"):
            with self.subTest(level=level):
                flow = PhasedFlow(level, assignment=level != "basic")
                flow.start_phase("P1")
                flow.finish_phase("P1")
                state = replay(flow.log)
                self.assertEqual(state.status, "coding_in_progress")
                self.assertEqual(state.next_action(), "start_next_phase_coder" if level == "basic" else "start_phase_review")
                if level != "basic":
                    flow.phase_review()
                self.assertTrue(replay(flow.log).phase_ready("P1"))
                flow.start_phase("P2")
                flow.finish_phase("P2")
                self.assertEqual(replay(flow.log).next_action(), "start_reviewer_review")
                flow.review("code")
                self.assertEqual(flow.log["history"][-2]["details"]["review_kind"], "initial")
                flow.complete()
                self.assertEqual(replay(flow.log).status, "implementation_complete")

    def test_basic_needs_assignment_only_after_assurance_requires_review(self):
        flow = PhasedFlow("basic", assignment=False)
        capability = deepcopy(flow.log["capability"])
        capability["roles"]["reviewer"]["reasoning_effort"] = "medium"
        flow.override("/capability", capability)
        flow.start_phase("P1")
        flow.finish_phase("P1")
        self.assertEqual(replay(flow.log).next_action(), "start_next_phase_coder")
        flow.override("/assurance_level", "standard")
        # First satisfy the separately required higher-assurance spec review.
        flow.start_review("spec")
        flow.review_output("spec")
        flow.log["history"][-1]["status"] = flow.log["status"] = "coding_in_progress"
        self.assertEqual(replay(flow.log).next_action(), "resolve_intermediate_reviewer_assignment")
        bad = deepcopy(flow)
        bad.phase_review()
        with self.assertRaisesRegex(ValidationError, "assignment"):
            replay(bad.log)
        capability = deepcopy(flow.log["capability"])
        capability["stage_assignments"] = {"intermediate_reviewer": {"model": "example-model", "reasoning_effort": "low"}}
        unsupported = deepcopy(flow)
        unsupported.override("/capability", capability)
        with self.assertRaisesRegex(ValidationError, "unmapped"):
            replay(unsupported.log)
        capability["acknowledged_limitations"] = ["User accepted low intermediate effort because medium has no predefined reduction."]
        flow.override("/capability", capability)
        flow.phase_review()
        self.assertTrue(replay(flow.log).phase_ready("P1"))

    def test_task_partition_and_scope_are_enforced(self):
        flow = PhasedFlow()
        flow.start_phase("P1")
        flow.finish_phase("P1")
        for mutation in ("tasks", "plan", "event"):
            broken = deepcopy(flow.log)
            entry = broken["history"][-1]
            if mutation == "tasks":
                entry["change_wrapper"]["task_progress"].pop()
            elif mutation == "plan":
                entry["change_wrapper"]["work_scope"]["plan_ref"] = reference("2", "event")
            else:
                entry["event"] = "coding-complete"
            with self.subTest(mutation=mutation), self.assertRaises(ValidationError):
                replay(broken)

    def test_unreviewed_phase_cannot_advance_and_last_has_no_intermediate_review(self):
        flow = PhasedFlow()
        flow.start_phase("P1")
        flow.finish_phase("P1")
        broken = deepcopy(flow)
        broken.start_phase("P2")
        with self.assertRaisesRegex(ValidationError, "Earlier phases"):
            replay(broken.log)
        flow.phase_review()
        flow.start_phase("P2")
        flow.finish_phase("P2")
        flow.phase_review("P2")
        with self.assertRaisesRegex(ValidationError, "Last phase"):
            replay(flow.log)

    def test_phase_repair_allowance_survives_context_and_configuration_changes(self):
        flow = PhasedFlow()
        flow.start_phase("P1")
        flow.finish_phase("P1")
        fid = "C-" + flow.next_id + "-1"
        issues = {"must_fix": [finding(fid)], "should_fix": [], "nit": []}
        flow.phase_review(issues=issues, accepted="false")
        flow.start_phase("P1", revision=True, context="recovered-phase-coder")
        flow.finish_phase("P1")
        flow.phase_review(issues=issues, accepted="false")
        state = replay(flow.log)
        self.assertEqual(state.cycles, {"spec": 0, "code": 0, "phase:P1": 1, "phase:P2": 0})
        capability = deepcopy(flow.log["capability"])
        capability["roles"]["coder"]["model"] = "replacement-model"
        flow.override("/capability", capability)
        self.assertEqual(replay(flow.log).next_action(), "obtain_repair_cycle_authorization")
        review_id = flow.phase_reviews["P1"]
        flow.authorize("repair_cycle", phase="code")
        decision = flow.log["history"][-1]["details"]
        decision["limits"]["phase"] = "phase:P1"
        decision["references"] = [reference(review_id, "code_review")]
        flow.start_phase("P1", revision=True)
        flow.finish_phase("P1")
        flow.phase_review(resolved=[fid])
        self.assertEqual(replay(flow.log).cycles["phase:P1"], 2)
        self.assertEqual(replay(flow.log).next_action(), "start_next_phase_coder")

    def test_final_assurance_reconsiders_policy_limitation_without_erasing_provenance(self):
        flow = PhasedFlow("maximum")
        flow.start_phase("P1")
        flow.finish_phase("P1")
        fid = "C-" + flow.next_id + "-1"
        issues = {"must_fix": [], "should_fix": [finding(fid)], "nit": []}
        flow.phase_review(issues=issues, accepted="conditional")
        flow.start_phase("P1", revision=True)
        choice = disposition(fid, "accept_limitation", "policy")
        flow.finish_phase("P1", dispositions=[choice])
        flow.phase_review(issues=issues, dispositions=[choice])
        flow.start_phase("P2")
        flow.finish_phase("P2")
        flow.review("code", issues=issues, dispositions=[choice], accepted="conditional")
        state = replay(flow.log)
        self.assertEqual(state.status, "code_changes_requested")
        self.assertEqual(state.findings[fid]["phase"], "phase:P1")
        self.assertIn(fid, state.open_findings("code"))
        flow.start_coding(revision=True)
        flow.code_output()
        wrapper = flow.log["history"][-1]["change_wrapper"]
        wrapper["task_progress"] = deepcopy(flow.log["history"][-5]["change_wrapper"]["task_progress"])
        flow.review("code", resolved=[fid])
        self.assertEqual(replay(flow.log).status, "code_approved")


if __name__ == "__main__":
    unittest.main()
