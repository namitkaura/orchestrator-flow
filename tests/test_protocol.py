from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".codex/skills/orchestrator-flow/scripts"))
from workflow_artifacts import ValidationError, check_compatibility, validate_shape, validate_wrapper
from workflow_protocol import replay, resume_action
from flow_fixtures import Flow, complete_flow, disposition, finding, reference


class ProtocolTests(unittest.TestCase):
    def rejected(self, flow, message=None):
        with self.assertRaises(ValidationError) as caught:
            replay(flow.log)
        if message:
            self.assertIn(message, str(caught.exception))

    def test_complete_flows_at_each_assurance_and_policy(self):
        for assurance in ("basic", "standard", "maximum"):
            for policy in ("spec_user_code_auto", "all_user", "within_scope_auto"):
                with self.subTest(assurance=assurance, policy=policy):
                    flow = complete_flow(assurance, policy)
                    state = replay(flow.log)
                    self.assertEqual(state.status, "implementation_complete")
                    self.assertEqual(state.approvals["tasks"]["version"], 1)
                    self.assertEqual(state.artifacts["tasks"]["version"], 2)
                    self.assertEqual(resume_action(flow.log, {"delivery": "delivered"})["action"], "finish_final_checkpoint_then_squash_message")

    def test_delivered_prefixes_resume_at_expected_workflow_boundaries(self):
        flow = complete_flow()
        expected = [
            ("initial Planner invocation", "invoke_recorded_role"),
            ("requirements draft", "obtain_requirements_approval"),
            ("requirements approval", "continue_planner_design"),
            ("design draft", "obtain_design_approval"),
            ("design approval", "continue_planner_tasks"),
            ("tasks draft", "obtain_tasks_approval"),
            ("tasks approval", "obtain_consolidated_spec_output"),
            ("consolidated specification", "start_architect_review"),
            ("Architect invocation", "invoke_recorded_role"),
            ("Architect acceptance", "obtain_coding_authorization"),
            ("coding authorization", "start_coder"),
            ("Coder invocation", "invoke_recorded_role"),
            ("interim implementation", "continue_coder"),
            ("consolidated implementation", "start_reviewer_review"),
            ("Reviewer invocation", "invoke_recorded_role"),
            ("Reviewer acceptance", "obtain_final_user_acceptance"),
            ("final user acceptance", "finish_final_checkpoint_then_squash_message"),
        ]
        # Keep every prefix covered if the complete-flow fixture gains a boundary.
        self.assertEqual(len(flow.log["history"]), len(expected))
        for length, (boundary, action) in enumerate(expected, start=1):
            with self.subTest(boundary=boundary):
                log = deepcopy(flow.log)
                log["history"] = log["history"][:length]
                log["status"] = log["history"][-1]["status"]
                observations = {"delivery": "delivered", "invocation": "not_started"}
                self.assertEqual(resume_action(log, observations)["action"], action)

    def test_initialization_cannot_be_completion(self):
        flow = complete_flow()
        flow.log["history"] = [flow.log["history"][-1]]
        flow.log["history"][0]["id"] = "1"
        self.rejected(flow)

    def test_partial_artifacts_and_repeat_drafts(self):
        flow = Flow()
        first = flow.spec_output("requirements")
        self.assertIsNone(first["design_ref"])
        flow.spec_output("requirements", "editorial")
        self.assertEqual(replay(flow.log).artifacts["requirements"]["version"], 2)
        self.assertEqual(resume_action(flow.log, {"delivery": "delivered"})["action"], "obtain_requirements_approval")

    def test_dependent_draft_requires_upstream_approval(self):
        flow = Flow()
        flow.spec_output("requirements")
        flow.spec_output("design")
        self.rejected(flow, "Approve requirements")

    def test_stale_approval_and_unrecorded_change_rejected(self):
        flow = Flow()
        flow.spec_output("requirements")
        flow.spec_output("requirements")
        flow.approve("requirements")
        flow.log["history"][-1]["details"]["version"] = 1
        self.rejected(flow, "stale")
        flow = Flow().finish_spec()
        flow.log["history"][-1]["spec_change_wrapper"]["artifacts"]["requirements"]["version"] = 2
        self.rejected(flow, "Unrecorded")

    def test_editorial_and_progress_preserve_real_approval_basis(self):
        flow = Flow()
        flow.spec_output("requirements")
        flow.approve("requirements")
        original = deepcopy(replay(flow.log).approvals)
        flow.spec_output("requirements", "editorial")
        self.assertEqual(replay(flow.log).approvals, original)
        flow.log["history"][-1]["spec_change_wrapper"]["artifact_changes"][0]["approval_basis_ref"] = None
        self.rejected(flow, "approval basis")

    def test_overrides_preserve_phase_and_reject_false_previous(self):
        flow = Flow()
        flow.spec_output("requirements")
        flow.override("/assurance_level", "basic")
        flow.override("/review_disposition_policy", "all_user")
        state = replay(flow.log)
        self.assertEqual(state.status, "spec_in_progress")
        self.assertEqual(state.next_action(), "obtain_requirements_approval")
        flow.log["history"][-2]["details"]["changes"][0]["previous"] = "maximum"
        self.rejected(flow, "previous")

    def test_invalid_configuration_override_and_effective_snapshot(self):
        flow = Flow()
        flow.override("/assurance_level", "basic")
        flow.log["assurance_level"] = "maximum"
        self.rejected(flow, "configuration disagrees")
        flow = Flow()
        flow.override("/capability/roles/helpers", {"model": "platform_default", "reasoning_effort": "not_supported"})
        self.rejected(flow, "acknowledged_limitations")

    def test_coding_has_a_distinct_user_authorization(self):
        flow = Flow().finish_spec()
        flow.review("spec")
        self.assertEqual(replay(flow.log).next_action(), "obtain_coding_authorization")
        flow.authorize(decision="deferred")
        self.assertEqual(replay(flow.log).status, "spec_approved")
        self.assertEqual(replay(flow.log).next_action(), "obtain_coding_authorization")
        flow.authorize()
        flow.start_coding()
        self.assertEqual(replay(flow.log).status, "coding_in_progress")

    def test_default_spec_disposition_gate_and_user_exception(self):
        flow = Flow().finish_spec()
        flow.start_review("spec")
        fid = "S-" + flow.contexts["Architect"]["trigger_event_id"] + "-1"
        flow.review_output("spec", issues={"must_fix": [finding(fid)], "should_fix": [], "nit": []}, accepted="false")
        self.assertEqual(replay(flow.log).next_action(), "obtain_findings_disposition")
        flow.user_dispositions("spec", [disposition(fid, "accept_limitation")], accepted="true")
        state = replay(flow.log)
        self.assertEqual(state.status, "spec_approved")
        self.assertEqual(set(state.known_issues()), {fid})

    def test_conditional_with_undispositioned_must_fix_is_invalid(self):
        flow = Flow().finish_spec()
        flow.start_review("spec")
        fid = "S-" + flow.contexts["Architect"]["trigger_event_id"] + "-1"
        flow.review_output("spec", issues={"must_fix": [finding(fid)], "should_fix": [], "nit": []}, accepted="conditional")
        self.rejected(flow, "Acceptance must be false")

    def test_repair_cycle_count_and_basic_limit(self):
        flow = Flow("basic").finish_spec()
        flow.start_review("spec")
        fid = "S-" + flow.contexts["Architect"]["trigger_event_id"] + "-1"
        issues = {"must_fix": [finding(fid)], "should_fix": [], "nit": []}
        flow.review_output("spec", issues=issues, accepted="false")
        flow.user_dispositions("spec", [disposition(fid)])
        flow.start_spec_revision()
        flow.spec_output("requirements")
        flow.approve("requirements")
        flow.spec_output(consolidated=True)
        flow.review("spec", issues=issues, accepted="false", scope="focused")
        flow.user_dispositions("spec", [disposition(fid)])
        state = replay(flow.log)
        self.assertEqual(state.cycles, {"spec": 1, "code": 0})
        self.assertEqual(state.next_action(), "obtain_repair_cycle_authorization")
        flow.authorize("repair_cycle", phase="spec")
        self.assertEqual(replay(flow.log).next_action(), "start_planner_revision")

    def test_success_after_repair_does_not_prompt_for_another_cycle(self):
        flow = Flow("basic").finish_spec()
        flow.start_review("spec")
        fid = "S-" + flow.contexts["Architect"]["trigger_event_id"] + "-1"
        flow.review_output("spec", issues={"must_fix": [finding(fid)], "should_fix": [], "nit": []}, accepted="false")
        flow.user_dispositions("spec", [disposition(fid)])
        flow.start_spec_revision()
        flow.spec_output("requirements")
        flow.approve("requirements")
        flow.spec_output(consolidated=True)
        flow.review("spec", resolved=[fid], scope="focused")
        self.assertEqual(replay(flow.log).next_action(), "obtain_coding_authorization")

    def test_initial_reviews_full_and_maximum_cannot_reuse_research(self):
        flow = Flow().finish_spec()
        flow.review("spec", scope="focused")
        self.rejected(flow, "complete coverage")
        flow = Flow("maximum").finish_spec()
        flow.review("spec", freshness="reused")
        self.rejected(flow, "cannot merely reuse")
        for level in ("basic", "standard"):
            flow = Flow(level).finish_spec()
            flow.review("spec", freshness="reused")
            self.assertEqual(replay(flow.log).status, "spec_approved")

    def test_assurance_increase_does_not_silently_reuse_acceptance(self):
        flow = Flow("basic").finish_spec()
        flow.review("spec")
        flow.override("/assurance_level", "maximum")
        self.assertEqual(replay(flow.log).next_action(), "review_assurance_gap_spec")
        flow.authorize()
        self.rejected(flow, "current assurance")

    def test_wrong_actor_requestor_and_duplicate_event_id(self):
        flow = complete_flow()
        flow.log["history"][9]["requestor"] = "User"
        self.rejected(flow, "actor/requestor")
        flow = complete_flow()
        flow.log["history"][3]["id"] = "2"
        self.rejected(flow, "contiguous")

    def test_nested_plural_references_check_types(self):
        flow = Flow().finish_spec()
        flow.log["history"][-1]["spec_change_wrapper"]["notes"] = "Source context: history entries 2, 4 and 6."
        replay(flow.log)
        flow.log["history"][-1]["spec_change_wrapper"]["notes"] = "Use spec_review_wrapper from history entries 2, 4."
        self.rejected(flow, "does not contain")
        flow.log["history"][-1]["spec_change_wrapper"]["notes"] = "Use SPEC_REVIEW_WRAPPER from history entries 2, 4."
        self.rejected(flow, "does not contain")
        flow.log["history"][-1]["spec_change_wrapper"]["notes"] = "Use history entry 900."
        self.rejected(flow, "Unknown/forward")

    def test_history_append_only_and_final_acceptance(self):
        flow = complete_flow()
        previous = deepcopy(flow.log)
        previous["history"][0]["details"]["request"] = "Different original request"
        with self.assertRaises(ValidationError):
            replay(flow.log, previous=previous)
        flow.log["history"][-1]["details"]["user_statement"] = ""
        self.rejected(flow)

    def test_failed_and_uncertain_delivery_override_normal_resumption(self):
        flow = complete_flow()
        self.assertEqual(resume_action(flow.log, {"delivery": "failed"})["action"], "obtain_checkpoint_recovery_direction")
        self.assertEqual(resume_action(flow.log, {"delivery": "uncertain"})["action"], "obtain_checkpoint_outcome_direction")

    def test_running_and_completed_invocations_are_recovered(self):
        flow = Flow()
        self.assertEqual(resume_action(flow.log, {"delivery": "delivered", "invocation": "running"})["action"], "recover_running_invocation")
        self.assertEqual(resume_action(flow.log, {"delivery": "delivered", "invocation": "completed"})["action"], "record_recovered_output")
        self.assertEqual(resume_action(flow.log, {"delivery": "delivered", "invocation": "paused"})["action"], "continue_existing_role_context")

    def test_check_failure_cannot_be_hidden_by_completion(self):
        flow = Flow().finish_spec()
        flow.review("spec")
        flow.authorize()
        flow.start_coding()
        flow.code_output()
        flow.log["history"][-1]["change_wrapper"]["checks"][0]["status"] = "fail"
        self.rejected(flow, "has not passed")

    def test_version_support_is_not_exact_version_only(self):
        for writer, reader in (("2.0.0", "2.0.1"), ("2.0.0", "2.1.0"), ("2.1.0", "2.1.1")):
            check_compatibility(writer, reader)
        for writer, reader in ((None, "2.0.0"), ("1.0.0", "2.0.0"), ("2.1.0", "2.0.0"), ("3.0.0", "3.0.0")):
            with self.assertRaises(ValidationError):
                check_compatibility(writer, reader)
        self.assertEqual(replay(complete_flow().log, reader_version="2.1.0").status, "implementation_complete")

    def test_repository_config_excludes_policy_and_requires_complete_roles(self):
        flow = Flow()
        config = {"assurance_level": "basic", "capability_defaults": {"codex": flow.log["capability"]["roles"]}}
        validate_shape("repository-config", config)
        config["review_disposition_policy"] = "all_user"
        with self.assertRaises(ValidationError):
            validate_shape("repository-config", config)

    def test_schema_rejects_malformed_events_and_settings(self):
        for defect in ("timestamp", "two_payloads", "assurance", "unsupported_model_marker", "pending_action", "missing_version"):
            flow = Flow()
            entry = flow.log["history"][0]
            if defect == "timestamp":
                entry["timestamp"] = "2026-09-30T12:00:00-04:00"
            elif defect == "two_payloads":
                entry["change_wrapper"] = {}
            elif defect == "assurance":
                flow.log["assurance_level"] = "automatic"
            elif defect == "unsupported_model_marker":
                flow.log["capability"]["roles"]["planner"]["model"] = "not_supported"
            elif defect == "pending_action":
                flow.log["pending_action"] = "start coding"
            else:
                del flow.log["workflow_version"]
            with self.subTest(defect=defect), self.assertRaises(ValidationError):
                replay(flow.log)


if __name__ == "__main__":
    unittest.main()
