from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".codex/skills/orchestrator-flow/scripts"))
from workflow_artifacts import ValidationError, validate_wrapper
from workflow_protocol import replay, resume_action
from flow_fixtures import Flow, disposition, finding, reference


def coding_flow(assurance="standard", policy="spec_user_code_auto"):
    flow = Flow(assurance, policy).finish_spec()
    flow.review("spec")
    flow.authorize()
    flow.start_coding()
    return flow


def failed_role(flow, role="Planner", category="role_failure", helper=None):
    context = flow.context(role)
    start = flow.log["history"][int(context["trigger_event_id"]) - 1]
    flow.add("subagent-error", role, start["requestor"], flow.log["status"], details={
        "invocation": context, "category": category, "message": "Recorded fixture failure; no automatic substitution.",
        "helper": helper, "output_ref": None})
    flow.contexts[role]["attempt"] += 1


def allow_attempt(flow, role="Planner", count=1):
    flow.authorize("external_operation", operation="continue-role")
    details = flow.log["history"][-1]["details"]
    details["scope"] = flow.contexts[role]["trigger_event_id"]
    details["limits"]["max_attempts"] = count


def feedback(flow):
    return flow.add("user-change-requested", "Orchestrator", "User",
                    "spec_in_progress" if flow.log["status"] == "spec_in_progress" else "spec_changes_requested", details={
                        "request": "Clarify the empty-input acceptance criterion.", "earliest_artifact": "requirements", "references": []})


class RecoveryAndReviewTests(unittest.TestCase):
    def test_coder_repairs_and_reviewer_followup_keep_causal_requestors(self):
        flow = coding_flow()
        flow.code_output()
        flow.start_review("code")
        fid = "C-" + flow.contexts["Reviewer"]["trigger_event_id"] + "-1"
        flow.review_output("code", issues={"must_fix": [finding(fid)], "should_fix": [], "nit": []}, accepted="false")
        self.assertEqual(replay(flow.log).next_action(), "start_coder_revision")
        flow.start_coding(revision=True)
        failed_role(flow, "Coder")
        flow.code_output(consolidated=False)
        flow.code_output()
        flow.review("code", resolved=[fid], scope="affected")
        state = replay(flow.log)
        self.assertEqual(state.cycles, {"spec": 0, "code": 1})
        self.assertEqual(state.next_action(), "obtain_final_user_acceptance")
        self.assertTrue(all(e["requestor"] == "Reviewer" for e in flow.log["history"][-4:-2]))

    def test_all_user_code_repairs_need_disposition(self):
        flow = coding_flow(policy="all_user")
        flow.code_output()
        flow.start_review("code")
        fid = "C-" + flow.contexts["Reviewer"]["trigger_event_id"] + "-1"
        flow.review_output("code", issues={"must_fix": [finding(fid)], "should_fix": [], "nit": []}, accepted="false")
        self.assertEqual(replay(flow.log).next_action(), "obtain_findings_disposition")
        flow.user_dispositions("code", [disposition(fid)])
        self.assertEqual(replay(flow.log).next_action(), "start_coder_revision")

    def test_standard_stops_before_third_completed_repair_pair(self):
        flow = Flow(policy="within_scope_auto").finish_spec()
        flow.start_review("spec")
        fid = "S-" + flow.contexts["Architect"]["trigger_event_id"] + "-1"
        issues = {"must_fix": [finding(fid)], "should_fix": [], "nit": []}
        flow.review_output("spec", issues=issues, accepted="false")
        for cycle in range(2):
            self.assertEqual(replay(flow.log).next_action(), "start_planner_revision")
            flow.start_spec_revision()
            flow.spec_output("requirements")
            flow.approve("requirements")
            flow.spec_output(consolidated=True)
            flow.review("spec", issues=issues, accepted="false", scope="affected")
            self.assertEqual(replay(flow.log).cycles["spec"], cycle + 1)
        self.assertEqual(replay(flow.log).next_action(), "obtain_repair_cycle_authorization")
        flow.authorize("repair_cycle", phase="spec")
        self.assertEqual(replay(flow.log).extra_cycles["spec"], 1)

    def test_maximum_stalled_loop_requires_user_direction(self):
        flow = Flow("maximum", "within_scope_auto").finish_spec()
        flow.start_review("spec")
        fid = "S-" + flow.contexts["Architect"]["trigger_event_id"] + "-1"
        issues = {"must_fix": [finding(fid)], "should_fix": [], "nit": []}
        flow.review_output("spec", issues=issues, accepted="false", freshness="revalidated")
        flow.start_spec_revision()
        flow.spec_output("requirements")
        flow.approve("requirements")
        flow.spec_output(consolidated=True)
        flow.review("spec", issues=issues, accepted="false", freshness="revalidated")
        flow.log["history"][-1]["spec_review_wrapper"]["meaningful_change"] = False
        self.assertEqual(replay(flow.log).next_action(), "obtain_stalled_loop_direction")
        flow.authorize("repair_cycle", phase="spec")
        self.assertEqual(replay(flow.log).next_action(), "start_planner_revision")

    def test_standard_followup_scope_depends_on_repair_not_invocation(self):
        for repair_class, scope, valid in (("editorial", "focused", True), ("test_documentation", "focused", True),
                                           ("bounded_correctness", "focused", False), ("bounded_correctness", "affected", True),
                                           ("architectural_systemic", "affected", False), ("architectural_systemic", "full", True)):
            flow = Flow().finish_spec()
            wrapper = flow.review("spec")
            wrapper.update(context=None, review_kind="follow_up", prior_review_ref=reference(10, "spec_review"),
                           repair_class=repair_class, review_scope=scope)
            with self.subTest(repair_class=repair_class, scope=scope):
                if valid:
                    validate_wrapper("spec-review-wrapper", wrapper)
                else:
                    with self.assertRaises(ValidationError):
                        validate_wrapper("spec-review-wrapper", wrapper)

    def test_model_direction_is_not_satisfied_by_unrelated_override(self):
        flow = Flow()
        failed_role(flow, category="model_unavailable")
        flow.override("/review_disposition_policy", "all_user")
        self.assertEqual(replay(flow.log).next_action(), "obtain_model_direction")
        flow.override("/capability/roles/planner", {"model": "accepted-other-model", "reasoning_effort": "high"})
        self.assertEqual(replay(flow.log).next_action(), "recover_invocation_or_output")
        self.assertEqual(replay(flow.log).config["assurance_level"], "standard")
        flow.contexts["Planner"]["configuration_ref"] = flow.config_ref
        flow.spec_output("requirements")
        replay(flow.log)

    def test_model_unavailability_cannot_silently_retry(self):
        flow = Flow()
        failed_role(flow, category="usage_limit")
        flow.spec_output("requirements")
        with self.assertRaisesRegex(ValidationError, "obtain_model_direction"):
            replay(flow.log)

    def test_three_ordinary_attempts_and_one_explicit_additional_attempt(self):
        flow = Flow()
        for _ in range(3):
            failed_role(flow)
        self.assertEqual(replay(flow.log).next_action(), "obtain_role_failure_direction")
        allow_attempt(flow)
        self.assertEqual(replay(flow.log).next_action(), "recover_invocation_or_output")
        failed_role(flow)
        self.assertEqual(replay(flow.log).next_action(), "obtain_role_failure_direction")
        flow.spec_output("requirements")
        with self.assertRaisesRegex(ValidationError, "Role retry gate"):
            replay(flow.log)

    def test_helper_usage_failure_identifies_helper_and_bounds_retry(self):
        flow = Flow()
        helper = {"id": "source-inspector-2", "model": "example-model", "reasoning_effort": "high", "category": "usage_limit"}
        failed_role(flow, category="helper_failure", helper=helper)
        self.assertEqual(replay(flow.log).next_action(), "obtain_model_direction")
        allow_attempt(flow)
        failed_role(flow, category="helper_failure", helper=helper)
        self.assertEqual(replay(flow.log).next_action(), "obtain_role_failure_direction")
        self.assertEqual(replay(flow.log).last_error["helper"]["id"], "source-inspector-2")

    def test_scoped_blockers_leave_independent_work_running(self):
        flow = coding_flow()
        blocker = {"id": "live-check", "operation": "remote validation", "task_ids": ["2"], "reason": "Access needs user authority.",
                   "attempts": [], "evidence": ["No live operation was attempted."], "depends_on": ["external access"],
                   "independent_task_ids": ["1"], "required_authorization": "One bounded live check."}
        flow.code_output(consolidated=False, blockers=[blocker])
        progress = [{"task_id": str(i), "status": "pending", "evidence": "Recorded pending work.", "disposition_ref": None} for i in (1, 2)]
        flow.log["history"][-1]["change_wrapper"]["task_progress"] = deepcopy(progress)
        self.assertEqual(replay(flow.log).next_action(), "continue_coder")
        blocker["independent_task_ids"] = []
        blocker["task_ids"] = ["1", "2"]
        flow.code_output(consolidated=False, blockers=[blocker])
        flow.log["history"][-1]["change_wrapper"]["task_progress"] = deepcopy(progress)
        self.assertEqual(replay(flow.log).next_action(), "resolve_scoped_blocker")
        flow.code_output()
        self.assertEqual(replay(flow.log).next_action(), "start_reviewer_review")

    def test_initial_feedback_stays_in_cycle_and_is_carried_by_output(self):
        flow = Flow()
        flow.spec_output("requirements")
        event_id = feedback(flow)
        flow.override("/assurance_level", "basic")
        flow.override("/review_disposition_policy", "all_user")
        self.assertEqual(replay(flow.log).next_action(), "continue_planner_requirements")
        flow.spec_output("requirements")
        flow.log["history"][-1]["spec_change_wrapper"]["causes"] = [reference(event_id)]
        state = replay(flow.log)
        self.assertEqual(state.artifacts["requirements"]["version"], 2)
        self.assertEqual(sum(e["event"] == "spec-creation-started" for e in flow.log["history"]), 1)

    def test_feedback_continues_existing_user_or_architect_revision(self):
        for requestor in ("User", "Architect"):
            for interim_output in (False, True):
                with self.subTest(requestor=requestor, interim_output=interim_output):
                    flow = Flow(policy="within_scope_auto").finish_spec()
                    flow.start_review("spec")
                    fid = "S-" + flow.contexts["Architect"]["trigger_event_id"] + "-1"
                    issues = {"must_fix": [finding(fid)], "should_fix": [], "nit": []}
                    flow.review_output("spec", issues=issues if requestor == "Architect" else None,
                                       accepted="false" if requestor == "Architect" else "true")
                    pending_causes = []
                    if requestor == "User":
                        pending_causes.append(reference(feedback(flow)))
                        self.assertEqual(replay(flow.log).next_action(), "start_planner_revision")
                    flow.start_spec_revision(requestor)
                    context = deepcopy(flow.contexts["Planner"])
                    if interim_output:
                        flow.spec_output("requirements")
                        flow.log["history"][-1]["spec_change_wrapper"]["causes"] = pending_causes
                        pending_causes = []
                    version = flow.artifacts["requirements"]["version"]
                    for _ in range(2):
                        pending_causes.append(reference(feedback(flow)))
                        state = replay(flow.log)
                        self.assertEqual(state.status, "spec_in_progress")
                        self.assertEqual(state.next_action(), "continue_planner_requirements")
                        self.assertEqual(state.starts["Planner"], context)
                        self.assertFalse(state.user_revision_pending)
                        self.assertEqual(state.cycles["spec"], 0)
                        redundant = deepcopy(flow)
                        redundant.start_spec_revision(requestor)
                        with self.assertRaisesRegex(ValidationError, "No spec revision is ready"):
                            replay(redundant.log)
                        flow.spec_output("requirements")
                        output = flow.log["history"][-1]
                        output["spec_change_wrapper"]["causes"] = pending_causes
                        pending_causes = []
                        version += 1
                        self.assertEqual(output["requestor"], requestor)
                        self.assertEqual(output["spec_change_wrapper"]["context"], context)
                        self.assertEqual(replay(flow.log).artifacts["requirements"]["version"], version)
                        self.assertEqual(replay(flow.log).next_action(), "obtain_requirements_approval")
                    flow.approve("requirements")
                    flow.spec_output(consolidated=True)
                    flow.review("spec", resolved=[fid] if requestor == "Architect" else [], scope="affected")
                    state = replay(flow.log)
                    self.assertEqual(state.status, "spec_approved")
                    self.assertEqual(state.cycles["spec"], 1 if requestor == "Architect" else 0)
                    self.assertEqual(sum(e["event"] == "spec-revision-started" for e in flow.log["history"]), 1)

    def test_fixed_known_issue_is_removed_without_rewriting_history(self):
        flow = Flow("basic").finish_spec()
        flow.start_review("spec")
        fid = "S-" + flow.contexts["Architect"]["trigger_event_id"] + "-1"
        flow.review_output("spec", issues={"must_fix": [], "should_fix": [finding(fid)], "nit": []}, accepted="conditional")
        flow.user_dispositions("spec", [disposition(fid, "accept_limitation")], accepted="true")
        self.assertIn(fid, replay(flow.log).known_issues())
        old_history = deepcopy(flow.log["history"])
        event_id = feedback(flow)
        flow.start_spec_revision("User")
        flow.spec_output("requirements")
        flow.log["history"][-1]["spec_change_wrapper"]["causes"] = [reference(event_id)]
        flow.approve("requirements")
        flow.spec_output(consolidated=True)
        flow.review("spec", resolved=[fid], scope="focused")
        self.assertFalse(replay(flow.log).known_issues())
        self.assertEqual(flow.log["history"][:len(old_history)], old_history)

    def test_declining_coding_supersedes_prior_grant_without_spec_change(self):
        flow = Flow().finish_spec()
        flow.review("spec")
        flow.authorize()
        flow.authorize(decision="denied")
        self.assertEqual(replay(flow.log).next_action(), "obtain_coding_authorization")
        self.assertEqual(replay(flow.log).status, "spec_approved")
        flow.start_coding()
        with self.assertRaisesRegex(ValidationError, "explicit authorization"):
            replay(flow.log)

    def test_legacy_approval_event_cannot_approve_other_review_loop(self):
        flow = coding_flow()
        flow.code_output()
        flow.start_review("code")
        fid = "C-" + flow.contexts["Reviewer"]["trigger_event_id"] + "-1"
        flow.review_output("code", issues={"must_fix": [], "should_fix": [finding(fid)], "nit": []}, accepted="conditional")
        flow.user_dispositions("code", [disposition(fid, "accept_limitation")], accepted="true")
        flow.log["history"][-1].update(event="spec-approved-by-user", requestor="Coder")
        with self.assertRaisesRegex(ValidationError, "other review loop"):
            replay(flow.log)

    def test_catchup_assurance_review_returns_to_interrupted_coding(self):
        flow = coding_flow("basic")
        flow.code_output(consolidated=False)
        flow.override("/assurance_level", "maximum")
        self.assertEqual(replay(flow.log).next_action(), "review_assurance_gap_spec")
        flow.review("spec", freshness="revalidated")
        flow.log["history"][-1]["status"] = flow.log["status"] = "coding_in_progress"
        self.assertEqual(replay(flow.log).next_action(), "continue_coder")
        flow.code_output()
        flow.review("code", freshness="revalidated")
        self.assertFalse(replay(flow.log).assurance_gaps)

    def test_assurance_increase_during_first_review_requires_catchup(self):
        for phase in ("spec", "code"):
            for initial, required in (("basic", "standard"), ("basic", "maximum"), ("standard", "maximum")):
                with self.subTest(phase=phase, initial=initial, required=required):
                    flow = Flow(initial).finish_spec() if phase == "spec" else coding_flow(initial)
                    if phase == "code":
                        flow.code_output()
                    flow.start_review(phase)
                    flow.override("/assurance_level", required)
                    self.assertEqual(replay(flow.log).next_action(), "recover_invocation_or_output")
                    flow.review_output(phase, freshness="reused")
                    wrapper_key = "spec_review_wrapper" if phase == "spec" else "review_wrapper"
                    flow.log["history"][-1][wrapper_key]["assurance_level"] = initial
                    state = replay(flow.log)
                    self.assertIn(phase, state.assurance_gaps)
                    self.assertEqual(state.next_action(), "review_assurance_gap_spec")
                    premature = deepcopy(flow)
                    if phase == "spec":
                        premature.authorize()
                    else:
                        premature.complete()
                    with self.assertRaisesRegex(ValidationError, "current assurance"):
                        replay(premature.log)
                    # Completed old-basis evidence remains recorded; only a sufficient
                    # catch-up pass can close the gap and unblock dependent work.
                    flow.review("spec", freshness="revalidated")
                    if phase == "code":
                        flow.log["history"][-1]["status"] = flow.log["status"] = "code_approved"
                        self.assertEqual(replay(flow.log).next_action(), "review_assurance_gap_code")
                        flow.review("code", freshness="revalidated")
                        flow.complete()
                    else:
                        flow.authorize()
                        flow.start_coding()
                    self.assertFalse(replay(flow.log).assurance_gaps)
                    self.assertEqual(replay(flow.log).cycles, {"spec": 0, "code": 0})

    def test_uncertain_recovery_context_has_no_invented_failure_or_authority(self):
        uncertain = {"attempt_id": "interrupted-push", "timestamp": "2026-09-30T12:00:00Z", "attempted_commit": "b" * 40,
                     "event_ids": ["1"], "remote": "origin", "feature_branch": "feature/example", "authorization_event_id": None,
                     "observation": "No recorded result; remote delivery cannot be established."}
        flow = Flow()
        auth = flow.authorize("checkpoint_recovery", uncertain=[uncertain])
        self.assertEqual(replay(flow.log).authorizations[auth]["uncertain_attempts"], [uncertain])
        for field, value in (("exit_code", 1), ("error_summary", "Invented failure"), ("observation", ""),
                             ("remote", "other-remote"), ("event_ids", ["99"])):
            invalid = deepcopy(flow.log)
            invalid["history"][-1]["details"]["uncertain_attempts"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValidationError):
                replay(invalid)
        for mutation in ("missing_context", "duplicate_context", "unbounded", "wrong_kind"):
            invalid = deepcopy(flow.log)
            details = invalid["history"][-1]["details"]
            if mutation == "missing_context":
                details["uncertain_attempts"] = []
            elif mutation == "duplicate_context":
                details["uncertain_attempts"].append(deepcopy(uncertain))
            elif mutation == "unbounded":
                details["limits"]["max_attempts"] = 2
            else:
                details["kind"] = "external_operation"
            with self.subTest(mutation=mutation), self.assertRaises(ValidationError):
                replay(invalid)
        existing = Flow()
        old_auth = existing.authorize("external_operation")
        saved = deepcopy(existing.log)
        self.assertEqual(replay(existing.log).authorizations[old_auth]["uncertain_attempts"], [])
        self.assertEqual(existing.log, saved)

    def test_evidence_requires_verifiable_sources_and_exposed_gaps(self):
        flow = Flow().finish_spec()
        wrapper = flow.review("spec", freshness="reused")
        for field in ("sources", "observations", "inferences", "coverage_gaps", "uncertainty", "applicability_check"):
            invalid = deepcopy(wrapper)
            del invalid["evidence"][0][field]
            with self.subTest(field=field), self.assertRaises(ValidationError):
                validate_wrapper("spec-review-wrapper", invalid)

    def test_finding_wrappers_require_classification_context(self):
        flow = Flow().finish_spec()
        template = flow.review("spec")
        concern = finding("S-0-1", "hardening_opportunity")
        concern.update(description="A transient provider rejection requires manual retry.",
                       triggering_conditions="The provider rejects a request temporarily.")
        for level, severity, accepted in (("basic", "nit", "true"), ("maximum", "should_fix", "conditional")):
            wrapper = deepcopy(template)
            wrapper.update(context=None, reviewed_output_ref=None, assurance_level=level, accepted=accepted)
            item = deepcopy(concern)
            item["practical_consequences"] = "A local operator reruns the command." if level == "basic" else "Unattended production work remains delayed until intervention."
            item["rationale"] = "Manual retry meets the agreed local acceptance standard." if level == "basic" else "The agreed operational target warrants automated recovery."
            wrapper["issue_details"] = {"must_fix": [], "should_fix": [], "nit": []}
            wrapper["issue_details"][severity] = [item]
            wrapper["dispositions"] = [disposition(item["id"], "accept_limitation", "policy")] if level == "basic" else []
            validate_wrapper("spec-review-wrapper", wrapper)
            for field in ("triggering_conditions", "practical_consequences", "basis", "rationale"):
                invalid = deepcopy(wrapper)
                del invalid["issue_details"][severity][0][field]
                with self.subTest(assurance=level, field=field), self.assertRaises(ValidationError):
                    validate_wrapper("spec-review-wrapper", invalid)

    def test_standalone_user_decision_is_not_embedded_authority(self):
        flow = Flow().finish_spec()
        flow.start_review("spec")
        fid = "S-" + flow.contexts["Architect"]["trigger_event_id"] + "-1"
        wrapper = flow.review_output("spec", issues={"must_fix": [finding(fid)], "should_fix": [], "nit": []},
                                     dispositions=[disposition(fid, "accept_limitation")])
        standalone = deepcopy(wrapper)
        standalone.update(context=None, reviewed_output_ref=None)
        validate_wrapper("spec-review-wrapper", standalone)
        with self.assertRaisesRegex(ValidationError, "historical decision"):
            replay(flow.log)

    def test_review_cannot_invent_producer_deferral(self):
        flow = Flow("basic").finish_spec()
        flow.start_review("spec")
        fid = "S-" + flow.contexts["Architect"]["trigger_event_id"] + "-1"
        flow.review_output("spec", issues={"must_fix": [], "should_fix": [], "nit": [finding(fid)]},
                           dispositions=[disposition(fid, "defer", "policy")])
        with self.assertRaisesRegex(ValidationError, "not invent"):
            replay(flow.log)

    def test_task_exception_requires_exact_task_authority(self):
        flow = coding_flow()
        flow.authorize("external_operation", operation="accept-task-result")
        authorization = flow.log["history"][-1]
        authorization["details"]["scope"] = "1"
        flow.code_output()
        task = flow.log["history"][-1]["change_wrapper"]["task_progress"][0]
        task.update(status="dispositioned", disposition_ref=reference(authorization["id"], "authorization"))
        replay(flow.log)
        authorization["details"]["scope"] = "2"
        with self.assertRaisesRegex(ValidationError, "for that task"):
            replay(flow.log)

    def test_missing_and_overlapping_overrides_are_rejected(self):
        flow = Flow()
        flow.override("/capability", flow.log["capability"])
        change = flow.log["history"][-1]["details"]["changes"]
        assignment = flow.log["capability"]["roles"]["planner"]
        change.append({"target": "/capability/roles/planner", "previous": assignment, "new": assignment})
        with self.assertRaisesRegex(ValidationError, "Overlapping"):
            replay(flow.log)
        change.pop()
        change[0]["target"] = "/capability/platform"
        with self.assertRaises(ValidationError):
            replay(flow.log)

    def test_settled_limitation_is_not_reopened_by_rediscovery(self):
        flow = Flow("basic").finish_spec()
        flow.start_review("spec")
        fid = "S-" + flow.contexts["Architect"]["trigger_event_id"] + "-1"
        issues = {"must_fix": [], "should_fix": [finding(fid)], "nit": []}
        flow.review_output("spec", issues=issues, accepted="conditional")
        flow.user_dispositions("spec", [disposition(fid, "accept_limitation")], accepted="true")
        event_id = feedback(flow)
        flow.start_spec_revision("User")
        flow.spec_output("requirements")
        flow.log["history"][-1]["spec_change_wrapper"]["causes"] = [reference(event_id)]
        flow.approve("requirements")
        flow.spec_output(consolidated=True)
        flow.review("spec", issues=issues, scope="focused")
        self.assertEqual(replay(flow.log).status, "spec_approved")
        flow.log["history"][-1]["spec_review_wrapper"]["accepted"] = "conditional"
        with self.assertRaisesRegex(ValidationError, "Acceptance must be true"):
            replay(flow.log)


if __name__ == "__main__":
    unittest.main()
