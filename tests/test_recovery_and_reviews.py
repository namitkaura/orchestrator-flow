from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".codex/skills/orchestrator-flow/scripts"))
from workflow_artifacts import ValidationError, validate_wrapper
from workflow_protocol import replay, resume_action
from flow_fixtures import Flow, disposition, finding, reference, complete_flow, evidence


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
    def test_explicit_user_nit_fix_uses_existing_repair_path(self):
        for phase in ("spec", "code"):
            for level in ("basic", "standard", "maximum"):
                for policy in ("spec_user_code_auto", "all_user", "within_scope_auto"):
                    with self.subTest(phase=phase, level=level, policy=policy):
                        flow = Flow(level, policy).finish_spec() if phase == "spec" else coding_flow(level, policy)
                        if phase == "code":
                            flow.code_output()
                        flow.start_review(phase)
                        fid = ("S" if phase == "spec" else "C") + "-" + flow.log["history"][-1]["id"] + "-1"
                        nit = finding(fid, "preference")
                        nit.update(description="A clear label could be shorter.", triggering_conditions="Reading the label.",
                                   practical_consequences="Minor reading preference; intended behavior is unaffected.",
                                   rationale="Optional wording improvement under this project's acceptance standard.")
                        original = flow.review_output(phase, issues={"nit": [nit]})
                        self.assertEqual(replay(flow.log).status, phase + "_approved")
                        standalone = deepcopy(original)
                        standalone.update(context=None, reviewed_output_ref=None, reviewed_artifacts=flow.artifacts,
                                          reviewed_commit=None, review_kind="initial", dispositions=[disposition(fid, "fix")])
                        kind = "spec-review-wrapper" if phase == "spec" else "review-wrapper"
                        with self.assertRaises(ValidationError):
                            validate_wrapper(kind, standalone)
                        standalone["accepted"] = "conditional"
                        validate_wrapper(kind, standalone)
                        # A proposal or policy response alone still cannot turn
                        # an optional nit into a mandatory repair.
                        standalone["accepted"] = "true"
                        standalone["dispositions"][0]["authority"] = "policy"
                        validate_wrapper(kind, standalone)
                        standalone["dispositions"][0].pop("authority")
                        validate_wrapper(kind, standalone)
                        decision = flow.user_dispositions(phase, [disposition(fid, "fix")], accepted="conditional")
                        state = replay(flow.log)
                        self.assertEqual(state.status, phase + "_changes_requested")
                        self.assertEqual(state.next_action(), "start_planner_revision" if phase == "spec" else "start_coder_revision")
                        self.assertIn(fid, state.open_findings(phase))
                        self.assertEqual(state.cycles[phase], 0)
                        self.assertEqual(original["accepted"], "true")
                        blocked = deepcopy(flow)
                        if phase == "spec":
                            blocked.authorize()
                        else:
                            blocked.complete()
                        with self.assertRaises(ValidationError):
                            replay(blocked.log)
                        # A producer's matching policy response cannot erase the
                        # actual user instruction while the fix awaits review.
                        response = disposition(fid, "fix", "policy")
                        contrary = deepcopy(flow)
                        if phase == "spec":
                            contrary.start_spec_revision(earliest="tasks")
                            contrary.spec_output("tasks", change_kind="editorial", consolidated=True,
                                                 dispositions=[disposition(fid, "defer", "policy")])
                        else:
                            contrary.start_coding(revision=True)
                            contrary.code_output(dispositions=[disposition(fid, "defer", "policy")])
                        with self.assertRaisesRegex(ValidationError, "Policy cannot replace"):
                            replay(contrary.log)
                        if phase == "spec":
                            flow.start_spec_revision(earliest="tasks")
                            flow.spec_output("tasks", change_kind="editorial", consolidated=True, dispositions=[response])
                        else:
                            flow.start_coding(revision=True)
                            flow.code_output(dispositions=[response])
                        pending = replay(flow.log)
                        self.assertEqual(pending.dispositions[fid]["recorded_user_event"], decision)
                        self.assertIn(fid, pending.open_findings(phase))
                        flow.review(phase, resolved=[fid])
                        finished = replay(flow.log)
                        self.assertEqual(finished.status, phase + "_approved")
                        self.assertEqual(finished.cycles[phase], 1)
                        self.assertNotIn(fid, finished.known_issues())

    def test_nit_only_initial_and_repair_reviews_accept_without_extra_decisions(self):
        for phase in ("spec", "code"):
            for level in ("basic", "standard", "maximum"):
                for followup in (False, True):
                    with self.subTest(phase=phase, level=level, followup=followup):
                        flow = Flow(level, "within_scope_auto").finish_spec() if phase == "spec" else coding_flow(level, "within_scope_auto")
                        if phase == "code":
                            flow.code_output()
                        flow.start_review(phase)
                        prefix = "S" if phase == "spec" else "C"
                        start = flow.log["history"][-1]["id"]
                        nit_id, defect_id = prefix + "-" + start + "-1", prefix + "-" + start + "-2"
                        nit = finding(nit_id, "preference")
                        nit.update(description="A label could be shorter.", triggering_conditions="Reading an already clear label.",
                                   practical_consequences="Minor reading preference; intended behavior is unaffected.",
                                   rationale="No material effect on this project's acceptance standard.")
                        issues = {"nit": [nit]}
                        if followup:
                            flow.review_output(phase, issues={**issues, "must_fix": [finding(defect_id)]}, accepted="false")
                            if phase == "spec":
                                flow.start_spec_revision(earliest="tasks")
                                flow.spec_output("tasks", consolidated=True)
                                flow.approve("tasks")
                            else:
                                flow.start_coding(revision=True)
                                flow.code_output()
                            flow.start_review(phase)
                        native = flow.review_output(phase, issues=issues, resolved=[defect_id] if followup else [])
                        state = replay(flow.log)
                        self.assertEqual(state.status, phase + "_approved")
                        self.assertEqual(state.next_action(), "obtain_coding_authorization" if phase == "spec" else "obtain_final_user_acceptance")
                        self.assertEqual(state.known_issues()[nit_id]["disposition"]["authority"], "policy")
                        self.assertNotIn(nit_id, state.dispositions)
                        self.assertEqual(state.cycles[phase], int(followup))
                        # Standalone acceptance uses the same nit rule.
                        standalone = deepcopy(native)
                        standalone.update(context=None, reviewed_output_ref=None, reviewed_artifacts=flow.artifacts,
                                          reviewed_commit=None, review_kind="follow_up" if followup else "initial")
                        validate_wrapper("spec-review-wrapper" if phase == "spec" else "review-wrapper", standalone)
                        if followup:
                            standalone.pop("changed_surfaces")
                            with self.assertRaisesRegex(ValidationError, "Repair follow-up"):
                                validate_wrapper("spec-review-wrapper" if phase == "spec" else "review-wrapper", standalone)
                        # A nit cannot hide a required unsuccessful check.
                        key = "spec_review_wrapper" if phase == "spec" else "review_wrapper"
                        flow.log["history"][-1][key]["checks"] = [{"name": "required-check", "status": "not_run", "required": True, "details": "Unavailable."}]
                        with self.assertRaises(ValidationError):
                            replay(flow.log)

    def test_disposition_without_authority_is_only_a_proposal(self):
        flow = Flow("basic").finish_spec()
        flow.start_review("spec")
        fid = "S-" + flow.log["history"][-1]["id"] + "-1"
        proposal = {"finding_id": fid, "decision": "accept_limitation", "rationale": "Ask whether the user accepts this consequence."}
        wrapper = flow.review_output("spec", issues={"must_fix": [finding(fid)]}, accepted="false", dispositions=[proposal])
        state = replay(flow.log)
        self.assertEqual(state.status, "spec_changes_requested")
        self.assertNotIn(fid, state.dispositions)
        self.assertFalse(state.known_issues())
        standalone = deepcopy(wrapper)
        standalone.update(context=None, reviewed_output_ref=None, reviewed_artifacts=flow.artifacts, reviewed_commit=None, review_kind="initial")
        validate_wrapper("spec-review-wrapper", standalone)
        standalone["accepted"] = "true"
        with self.assertRaises(ValidationError):
            validate_wrapper("spec-review-wrapper", standalone)

    def test_unusable_output_retry_preserves_assignment_and_failure_count(self):
        flow = Flow()
        failed_role(flow, category="invalid_output")
        flow.override("/capability/roles/planner", {"model": "future-model", "reasoning_effort": "high"})
        flow.spec_output("requirements")
        state = replay(flow.log)
        self.assertEqual(state.active_context("Planner")["attempt"], 2)
        self.assertEqual(state.cycles["spec"], 0)
        self.assertEqual(len(state.errors["1"]), 1)

    def test_output_only_review_retry_does_not_upgrade_assurance(self):
        flow = Flow("basic").finish_spec()
        flow.start_review("spec")
        failed_role(flow, "Architect", category="invalid_output")
        flow.override("/assurance_level", "maximum")
        flow.review_output("spec", freshness="reused")
        flow.log["history"][-1]["spec_review_wrapper"]["assurance_level"] = "basic"
        state = replay(flow.log)
        self.assertEqual(state.assurance_gaps, {"spec"})
        self.assertEqual(state.next_action(), "review_assurance_gap_spec")
        upgraded = deepcopy(flow.log)
        upgraded["history"][-1]["spec_review_wrapper"].update(assurance_level="maximum", evidence=[evidence("revalidated")])
        with self.assertRaisesRegex(ValidationError, "assurance basis"):
            replay(upgraded)

    def test_context_replacement_keeps_coder_assignment_and_authority(self):
        flow = coding_flow()
        before = replay(flow.log)
        flow.override("/capability/roles/coder", {"model": "accepted-coder", "reasoning_effort": "max"})
        flow.contexts["Coder"]["context_id"] = "replacement-coder"
        flow.code_output()
        after = replay(flow.log)
        self.assertEqual(after.active_context("Coder")["trigger_event_id"], before.starts["Coder"]["trigger_event_id"])
        self.assertEqual(after.active_context("Coder")["context_id"], "replacement-coder")
        self.assertEqual(after.coding_authorization, before.coding_authorization)
        self.assertEqual(after.cycles, before.cycles)
        self.assertEqual(after.log["branch_context"], before.log["branch_context"])
        self.assertEqual(after.errors, {})

    def test_explicit_retry_exhaustion_survives_override_and_replacement(self):
        flow = Flow()
        for attempt in range(3):
            failed_role(flow, category="invalid_output")
            flow.contexts["Planner"]["context_id"] = f"recovery-{attempt}"
        flow.override("/capability/roles/planner", {"model": "next-model", "reasoning_effort": "medium"})
        self.assertEqual(replay(flow.log).next_action(), "obtain_role_failure_direction")
        flow.spec_output("requirements")
        with self.assertRaisesRegex(ValidationError, "Role retry gate"):
            replay(flow.log)

    def test_failed_helper_uses_its_own_new_basis_for_direction(self):
        flow = Flow()
        flow.override("/capability/roles/helpers", {"model": "new-helper", "reasoning_effort": "medium"})
        helper = {"id": "native-helper", "model": "new-helper", "reasoning_effort": "medium", "category": "usage_limit"}
        failed_role(flow, category="helper_failure", helper=helper)
        self.assertEqual(replay(flow.log).next_action(), "obtain_model_direction")
        flow.override("/capability/roles/helpers", {"model": "replacement-helper", "reasoning_effort": "medium"})
        self.assertEqual(replay(flow.log).next_action(), "recover_invocation_or_output")

    def test_inflight_acceptance_keeps_original_basis_with_current_gate_separate(self):
        flow = coding_flow("maximum")
        flow.code_output()
        fid = "C-" + flow.next_id + "-1"
        issues = {"must_fix": [], "should_fix": [finding(fid)], "nit": []}
        flow.review("code", issues=issues, accepted="conditional")
        flow.override("/assurance_level", "standard")
        flow.start_coding(revision=True)
        response = disposition(fid, "accept_limitation", "policy")
        flow.code_output(dispositions=[response])
        flow.start_review("code")
        flow.override("/assurance_level", "maximum")
        flow.review_output("code", issues=issues, dispositions=[response])
        entry = flow.log["history"][-1]
        entry["review_wrapper"]["assurance_level"] = "standard"
        entry["status"] = flow.log["status"] = "code_changes_requested"
        state = replay(flow.log)
        self.assertEqual(entry["review_wrapper"]["accepted"], "true")
        self.assertIn("code", state.assurance_gaps)
        self.assertIn(fid, state.open_findings("code"))

    def test_bounded_applicability_clears_only_the_assessed_stage(self):
        flow = complete_flow("maximum")
        flow.log["history"].pop()
        flow.log["status"] = "code_approved"
        old_reviews = deepcopy(flow.reviews)
        old_contexts = deepcopy(flow.contexts)
        flow.override("/assurance_level", "standard")
        feedback_id = feedback(flow)
        flow.start_spec_revision("User", "tasks")
        flow.checkpoint_commit = "c" * 40
        flow.spec_output("tasks", "editorial")
        flow.log["history"][-1]["spec_change_wrapper"]["causes"] = [reference(feedback_id)]
        flow.spec_output(consolidated=True)
        flow.review("spec")
        flow.authorize()
        flow.start_coding()
        flow.code_output()
        # Changed work still needs its mandatory review despite earlier evidence.
        self.assertEqual(replay(flow.log).next_action(), "start_reviewer_review")
        flow.review("code")
        flow.override("/assurance_level", "maximum")
        self.assertEqual(replay(flow.log).assurance_gaps, {"spec", "code"})
        for stage, role, requestor in (("spec", "Architect", "Planner"), ("code", "Reviewer", "Coder")):
            flow.add("review-evidence-assessed", role, requestor, flow.log["status"], details={
                "review_ref": reference(old_reviews[stage], stage + "_review"),
                "source_ref": reference(flow.outputs[stage], "spec_change_wrapper" if stage == "spec" else "change_wrapper"),
                "work_scope": {"kind": "feature"}, "reviewed_artifacts": deepcopy(flow.artifacts), "current_commit": "c" * 40,
                "conclusion": "applicable", "evidence": [evidence("revalidated")], "invocation": old_contexts[role]})
            if stage == "spec":
                self.assertEqual(replay(flow.log).assurance_gaps, {"code"})
        state = replay(flow.log)
        self.assertEqual(state.assurance_gaps, set())
        self.assertEqual(state.cycles, {"spec": 0, "code": 0})
        self.assertEqual(state.next_action(), "obtain_final_user_acceptance")
        for conclusion in ("inapplicable", "uncertain"):
            invalidated = deepcopy(flow.log)
            invalidated["history"][-1]["details"]["conclusion"] = conclusion
            self.assertEqual(replay(invalidated).assurance_gaps, {"code"})
        broken = deepcopy(flow.log)
        broken["history"][-1]["details"]["evidence"][0]["coverage_gaps"] = ["Could not inspect current implementation."]
        with self.assertRaisesRegex(ValidationError, "Incomplete"):
            replay(broken)

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
            wrapper.update(context=None, reviewed_output_ref=None, reviewed_artifacts=flow.artifacts, reviewed_commit=flow.checkpoint_commit, review_kind="follow_up",
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
        flow.log["history"][-1]["details"]["task_progress"] = deepcopy(progress)
        self.assertEqual(resume_action(flow.log, {"delivery": "delivered", "invocation": "running"})["action"], "recover_running_invocation")
        blocker["independent_task_ids"] = []
        blocker["task_ids"] = ["1", "2"]
        flow.code_output(consolidated=False, blockers=[blocker])
        flow.log["history"][-1]["details"]["task_progress"] = deepcopy(progress)
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


    def test_catchup_assurance_review_returns_to_interrupted_coding(self):
        flow = coding_flow("basic")
        flow.code_output(consolidated=False)
        flow.log["history"][-1]["details"]["yielded"] = True
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
        self.assertEqual(replay(flow.log).authorizations[auth]["uncertain_attempts"],
                         [dict(uncertain, checkpoint_kind="log", publishing_role="Orchestrator", invocation=None, phase_id=None)])
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
        for field in ("sources", "observations", "applicability_check"):
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
            wrapper.update(context=None, reviewed_output_ref=None, reviewed_artifacts=flow.artifacts, reviewed_commit=flow.checkpoint_commit, review_kind="initial", assurance_level=level, accepted=accepted)
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
        standalone.update(context=None, reviewed_output_ref=None, reviewed_artifacts=flow.artifacts, reviewed_commit=flow.checkpoint_commit, review_kind="initial")
        validate_wrapper("spec-review-wrapper", standalone)
        with self.assertRaisesRegex(ValidationError, "historical decision"):
            replay(flow.log)

    def test_review_cannot_invent_producer_deferral(self):
        flow = Flow("basic").finish_spec()
        flow.start_review("spec")
        fid = "S-" + flow.contexts["Architect"]["trigger_event_id"] + "-1"
        flow.review_output("spec", issues={"must_fix": [], "should_fix": [finding(fid)], "nit": []},
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
