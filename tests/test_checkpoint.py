from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".codex/skills/orchestrator-flow/scripts"))
from checkpoint_state import (committed_checkpoint, event_commits, inspect_delivery, journal_path,
                              read_attempts, record_push_attempt, record_push_failure, recent_history, select_feature_branch,
                              workflow_checkpoints)
from workflow_artifacts import ValidationError
from workflow_protocol import replay, resume_action
from flow_fixtures import Flow, complete_flow


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo, self.remote = self.root / "repo", self.root / "remote.git"
        self.git("init", "--initial-branch=main", str(self.repo), cwd=self.root)
        self.git("config", "user.name", "Workflow tests")
        self.git("config", "user.email", "workflow-tests@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        (self.repo / "baseline.txt").write_text("fixture baseline\n", encoding="utf-8")
        self.git("add", "baseline.txt")
        self.git("commit", "-m", "Fixture baseline")
        self.baseline = self.git("rev-parse", "HEAD").stdout.strip()
        self.git("checkout", "-b", "feature/example")
        self.git("init", "--bare", str(self.remote), cwd=self.root)
        self.git("remote", "add", "origin", str(self.remote))
        self.flow = Flow(baseline=self.baseline)

    def git(self, *args, cwd=None, check=True):
        result = subprocess.run(["git", "-C", str(cwd or self.repo), *args], capture_output=True, text=True, encoding="utf-8")
        if check:
            self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def checkpoint(self, first=1, log=None):
        log = log or self.flow.log
        path = self.repo / log["task_log_ref"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")
        self.git("add", "--", log["task_log_ref"])
        self.git("commit", "--only", "-m", f"Record fixture update\n\nOrchestrator-Feature: {log['feature']}\nOrchestrator-Checkpoint: log\nOrchestrator-Role: Orchestrator\nOrchestrator-Log: {log['task_log_ref']}\nOrchestrator-Events: {first}-{len(log['history'])}", "--", log["task_log_ref"])
        return self.git("rev-parse", "HEAD").stdout.strip()

    def fail_push(self, authorization=None):
        attempt = record_push_attempt(self.repo, self.flow.log, authorization)
        self.git("remote", "set-url", "origin", str(self.root / "missing.git"))
        result = self.git("push", "origin", "HEAD:refs/heads/feature/example", check=False)
        self.assertNotEqual(result.returncode, 0)
        failure = record_push_failure(self.repo, "example", attempt["attempt_id"], result.returncode, "Fixture remote was unavailable.")
        self.git("remote", "set-url", "origin", str(self.remote))
        return failure

    def artifact_checkpoint(self, path="requirements.md", body="draft", role="Planner"):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
        self.git("add", "--", path)
        invocation = self.flow.contexts[role] if role != "Orchestrator" else None
        trailers = f"Orchestrator-Feature: example\nOrchestrator-Checkpoint: artifacts\nOrchestrator-Role: {role}"
        if invocation:
            trailers += f"\nOrchestrator-Invocation: {invocation['trigger_event_id']}/{role}/{invocation['attempt']}"
        self.git("commit", "--only", "-m", "Preserve artifact progress\n\n" + trailers, "--", path)
        return self.git("rev-parse", "HEAD").stdout.strip()

    def test_artifact_delivery_and_uncertain_recovery_after_delivered_log(self):
        log_commit = self.checkpoint()
        self.git("push", "origin", "HEAD:refs/heads/feature/example")
        artifact = self.artifact_checkpoint()
        observed = inspect_delivery(self.repo, self.flow.log)
        self.assertEqual(observed["delivery"], "committed")
        self.assertEqual(observed["checkpoint"]["commit"], artifact)
        self.assertNotEqual(artifact, log_commit)
        attempt = record_push_attempt(self.repo, self.flow.log)
        self.assertEqual(attempt["event_ids"], [])
        self.assertEqual(attempt["publishing_role"], "Planner")
        uncertain = inspect_delivery(self.repo, self.flow.log)["uncertain_attempt"]
        self.assertEqual(uncertain["attempt_id"], attempt["attempt_id"])
        auth = self.flow.authorize("checkpoint_recovery", uncertain=[uncertain])
        self.checkpoint(first=2)
        record_push_attempt(self.repo, self.flow.log, auth)
        count = self.git("rev-list", "--count", "HEAD").stdout
        self.git("push", "origin", "HEAD:refs/heads/feature/example")
        self.assertEqual(inspect_delivery(self.repo, self.flow.log)["delivery"], "delivered")
        self.assertEqual(self.git("rev-list", "--count", "HEAD").stdout, count)

    def test_coder_artifact_checkpoints_need_no_interim_wrapper(self):
        self.flow.finish_spec()
        self.flow.review("spec")
        self.flow.authorize()
        self.flow.start_coding()
        self.checkpoint()
        self.git("push", "origin", "HEAD:refs/heads/feature/example")
        for number in range(3):
            self.artifact_checkpoint("src/example.py", f"value = {number}\n", "Coder")
            record_push_attempt(self.repo, self.flow.log)
            self.git("push", "origin", "HEAD:refs/heads/feature/example")
        result = resume_action(self.flow.log, {**inspect_delivery(self.repo, self.flow.log), "invocation": "paused"})
        self.assertEqual(result["action"], "continue_existing_role_context")
        self.assertNotIn("code", replay(self.flow.log).outputs)
        failure_commit = self.artifact_checkpoint("src/example.py", "value = 4\n", "Coder")
        failure = self.fail_push()
        self.assertEqual(failure["attempted_commit"], failure_commit)
        self.assertEqual(failure["publishing_role"], "Coder")
        self.assertEqual(inspect_delivery(self.repo, self.flow.log)["delivery"], "failed")
        self.assertEqual(resume_action(self.flow.log, inspect_delivery(self.repo, self.flow.log))["action"], "obtain_checkpoint_recovery_direction")

    def test_artifact_identity_uses_history_at_commit_without_inventing_native_context(self):
        self.checkpoint()
        first_context = self.flow.context("Planner")
        self.flow.add("subagent-error", "Planner", "User", "spec_in_progress", details={
            "invocation": first_context, "category": "role_failure", "message": "Invocation interrupted.",
            "helper": None, "output_ref": None})
        self.flow.contexts["Planner"].update(attempt=2, context_id="replacement-native-session")
        self.checkpoint(first=2)
        artifact = self.artifact_checkpoint()
        started = record_push_attempt(self.repo, self.flow.log)
        self.assertEqual(started["invocation"], {"trigger_event_id": "1", "role": "Planner", "attempt": 2})
        # Git identifies the attempt; it cannot infer a replacement native handle.
        uncertain = inspect_delivery(self.repo, self.flow.log)["uncertain_attempt"]
        self.flow.authorize("checkpoint_recovery", uncertain=[uncertain])
        self.flow.override("/assurance_level", "maximum")
        self.checkpoint(first=3)
        replay(self.flow.log)
        old = next(c for c in workflow_checkpoints(self.repo, self.flow.log) if c["commit"] == artifact)
        self.assertEqual(old["invocation"], started["invocation"])

    def test_later_failure_record_cannot_authorize_an_earlier_artifact_attempt(self):
        self.checkpoint()
        original = self.flow.context("Planner")
        self.flow.contexts["Planner"]["attempt"] = 2
        self.artifact_checkpoint()
        self.flow.add("subagent-error", "Planner", "User", "spec_in_progress", details={
            "invocation": original, "category": "role_failure", "message": "Only recorded after the artifact.",
            "helper": None, "output_ref": None})
        self.checkpoint(first=2)
        with self.assertRaisesRegex(ValidationError, "unrecorded attempt"):
            inspect_delivery(self.repo, self.flow.log)

    def test_recent_history_paginates_metadata_without_bodies_and_preserves_dirty_state(self):
        first = self.checkpoint()
        secret = "THIS_IS_FILE_CONTENT_NOT_RECOVERY_METADATA"
        for number in range(3):
            self.artifact_checkpoint(body=secret + str(number))
        (self.repo / "unrelated.txt").write_text("untouched", encoding="utf-8")
        page = recent_history(self.repo, self.flow.log, limit=2)
        self.assertIsNotNone(page["next_cursor"])
        older = recent_history(self.repo, self.flow.log, cursor=page["next_cursor"], limit=2)
        self.assertEqual(older["commits"][-1]["commit"], first)
        self.assertIsNone(older["next_cursor"])
        self.assertNotIn(secret, json.dumps([page, older]))
        self.assertIn("?? unrelated.txt", page["working_tree"])
        self.assertEqual(len({c["commit"] for c in page["commits"] + older["commits"]}), 4)
        self.artifact_checkpoint(body="newer")
        with self.assertRaisesRegex(ValidationError, "HEAD changed"):
            recent_history(self.repo, self.flow.log, cursor=page["next_cursor"])

    def test_native_branch_validation_does_not_invent_a_prefix_or_version(self):
        for feature, explicit, expected in (("mail-migration", None, "mail-migration"),
                ("v2.0.0-mail-migration", None, "v2.0.0-mail-migration"), ("mail-migration", "provider-migration", "provider-migration")):
            self.assertEqual(select_feature_branch(self.repo, feature, explicit), expected)
        with self.assertRaises(ValidationError):
            select_feature_branch(self.repo, "bad name")

    def published_coding(self):
        """Prepare real published artifacts and one cumulative Coder return."""
        self.checkpoint()
        def document(name):
            return f"# {name}\nContent version: 1\n\n" + ("- [ ] 1. **[Verification]** Check the approved behavior\n" if name == "tasks" else "Approved content\n") + "\n## Revision History\n### Version 1 — 2026-09-30\n- Initial draft.\n"
        for name in ("requirements", "design", "tasks"):
            commit = self.artifact_checkpoint(self.flow.log[name + "_ref"], document(name))
            self.git("push", "origin", "HEAD:refs/heads/feature/example")
            self.flow.checkpoint_commit = commit
            self.flow.spec_output(name)
            self.flow.approve(name)
        self.flow.spec_output(consolidated=True)
        self.flow.review("spec")
        self.flow.authorize()
        self.flow.start_coding()
        self.checkpoint(first=2)
        commit = self.artifact_checkpoint(self.flow.log["tasks_ref"], document("tasks").replace("[ ] 1.", "[x] 1."), "Coder")
        self.git("push", "origin", "HEAD:refs/heads/feature/example")
        self.flow.checkpoint_commit = commit
        self.flow.code_output(progress=True)
        return document("tasks").replace("[ ] 1.", "[x] 1.")

    def test_workspace_provenance_and_task_progress_compare_actual_git_content(self):
        from validate_orchestrator_artifacts import validate_workspace
        self.published_coding()
        state = replay(self.flow.log)
        validate_workspace(state, self.repo)
        path = self.repo / self.flow.log["tasks_ref"]
        path.write_text(path.read_text(encoding="utf-8").replace("approved behavior", "different behavior"), encoding="utf-8")
        with self.assertRaisesRegex(ValidationError, "content changes"):
            validate_workspace(state, self.repo)
        # A dishonest producer report still cannot hide material edits in a commit.
        commit = self.artifact_checkpoint(self.flow.log["tasks_ref"], path.read_text(encoding="utf-8"), "Coder")
        self.git("push", "origin", "HEAD:refs/heads/feature/example")
        self.flow.log["history"][-1]["change_wrapper"]["checkpoint_commit"] = commit
        with self.assertRaisesRegex(ValidationError, "concealed"):
            validate_workspace(replay(self.flow.log), self.repo)

    def test_historical_completion_does_not_require_newly_planned_tasks_done(self):
        from validate_orchestrator_artifacts import validate_workspace
        content = self.published_coding()
        self.checkpoint(first=13)
        request = self.flow.add("user-change-requested", "Orchestrator", "User", "spec_changes_requested", details={
            "request": "Add the agreed follow-up verification.", "earliest_artifact": "tasks", "references": []})
        self.flow.start_spec_revision("User", "tasks")
        self.checkpoint(first=14)
        revised = content.replace("Content version: 1", "Content version: 2").replace(
            "## Revision History", "- [ ] 2. **[Verification]** Run the additional approved check\n\n## Revision History")
        revised += "### Version 2 — 2026-10-01\n- Add the user-requested verification.\n"
        commit = self.artifact_checkpoint(self.flow.log["tasks_ref"], revised)
        self.git("push", "origin", "HEAD:refs/heads/feature/example")
        self.flow.checkpoint_commit = commit
        self.flow.spec_output("tasks")
        self.flow.log["history"][-1]["spec_change_wrapper"]["causes"] = [{"event_id": request, "kind": "event"}]
        state = replay(self.flow.log)
        validate_workspace(state, self.repo)
        self.assertEqual(state.next_action(), "obtain_tasks_approval")

    def test_retry_authorization_is_committed_before_one_push_without_receipt(self):
        original = self.checkpoint()
        failure = self.fail_push()
        self.assertEqual(inspect_delivery(self.repo, self.flow.log)["delivery"], "failed")
        auth = self.flow.authorize("checkpoint_recovery", failures=[failure])
        with self.assertRaises(ValidationError):
            record_push_attempt(self.repo, self.flow.log, auth)
        authorization_commit = self.checkpoint(first=2)
        self.assertNotEqual(original, authorization_commit)
        self.assertEqual(inspect_delivery(self.repo, self.flow.log)["authorization_event_id"], auth)
        attempt = record_push_attempt(self.repo, self.flow.log, auth)
        self.assertEqual(attempt["attempted_commit"], authorization_commit)
        before = self.git("rev-list", "--count", "HEAD").stdout
        self.git("push", "origin", "HEAD:refs/heads/feature/example")
        self.assertEqual(inspect_delivery(self.repo, self.flow.log)["delivery"], "delivered")
        self.assertEqual(before, self.git("rev-list", "--count", "HEAD").stdout)
        self.assertEqual(len(read_attempts(self.repo, "example")), 3)
        with self.assertRaises(ValidationError):
            record_push_attempt(self.repo, self.flow.log, auth)

    def test_failed_retry_survives_restart_without_replenishing_authority(self):
        self.checkpoint()
        first = self.fail_push()
        auth = self.flow.authorize("checkpoint_recovery", failures=[first])
        self.checkpoint(first=2)
        second = self.fail_push(auth)
        restored = json.loads((self.repo / self.flow.log["task_log_ref"]).read_text(encoding="utf-8"))
        self.assertEqual(read_attempts(self.repo, "example")[-1]["attempt_id"], second["attempt_id"])
        self.assertEqual(inspect_delivery(self.repo, restored)["delivery"], "failed")
        with self.assertRaises(ValidationError):
            record_push_attempt(self.repo, restored, auth)
        auth2 = self.flow.authorize("checkpoint_recovery", failures=[second])
        self.checkpoint(first=3)
        record_push_attempt(self.repo, self.flow.log, auth2)
        self.git("push", "origin", "HEAD:refs/heads/feature/example")
        self.assertEqual(inspect_delivery(self.repo, self.flow.log)["delivery"], "delivered")

    def test_interrupted_attempt_requires_inspection_not_another_push(self):
        self.checkpoint()
        record_push_attempt(self.repo, self.flow.log)
        self.assertEqual(inspect_delivery(self.repo, self.flow.log)["delivery"], "uncertain")
        with self.assertRaises(ValidationError):
            record_push_attempt(self.repo, self.flow.log)
        self.git("push", "origin", "HEAD:refs/heads/feature/example")
        self.assertEqual(inspect_delivery(self.repo, self.flow.log)["delivery"], "delivered")

    def test_interrupted_attempt_can_receive_one_committed_retry_authorization(self):
        self.checkpoint()
        started = record_push_attempt(self.repo, self.flow.log)
        observed = inspect_delivery(self.repo, self.flow.log)
        self.assertEqual(observed["delivery"], "uncertain")
        self.assertEqual(resume_action(self.flow.log, observed)["action"], "obtain_checkpoint_outcome_direction")
        uncertain = {k: v for k, v in started.items() if k != "record"}
        uncertain["observation"] = "The attempt has no recorded result and the remote branch is absent."
        auth = self.flow.authorize("checkpoint_recovery", uncertain=[uncertain])
        self.assertEqual(replay(self.flow.log).status, "spec_in_progress")
        with self.assertRaisesRegex(ValidationError, "Commit the update"):
            record_push_attempt(self.repo, self.flow.log, auth)
        checkpoint = self.checkpoint(first=2)
        observed = inspect_delivery(self.repo, self.flow.log)
        self.assertEqual(observed["authorization_event_id"], auth)
        self.assertEqual(resume_action(self.flow.log, observed)["action"], "deliver_authorized_checkpoint")
        retry = record_push_attempt(self.repo, self.flow.log, auth)
        self.assertEqual(retry["attempted_commit"], checkpoint)
        self.assertNotEqual(retry["attempt_id"], started["attempt_id"])
        with self.assertRaisesRegex(ValidationError, "already consumed"):
            record_push_attempt(self.repo, self.flow.log, auth)
        before = self.git("rev-list", "--count", "HEAD").stdout
        self.git("push", "origin", "HEAD:refs/heads/feature/example")
        self.assertEqual(inspect_delivery(self.repo, self.flow.log)["delivery"], "delivered")
        self.assertEqual(before, self.git("rev-list", "--count", "HEAD").stdout)
        self.assertEqual([r["record"] for r in read_attempts(self.repo, "example")], ["started", "started"])

    def test_interrupted_retry_needs_fresh_authority_for_its_actual_attempt(self):
        self.checkpoint()
        failure = self.fail_push()
        first_auth = self.flow.authorize("checkpoint_recovery", failures=[failure])
        self.checkpoint(first=2)
        interrupted = record_push_attempt(self.repo, self.flow.log, first_auth)
        observed = inspect_delivery(self.repo, self.flow.log)
        self.assertEqual(observed["delivery"], "uncertain")
        self.assertEqual(observed["uncertain_attempt"]["attempt_id"], interrupted["attempt_id"])
        self.assertNotIn("exit_code", observed["uncertain_attempt"])
        self.assertNotIn("error_summary", observed["uncertain_attempt"])
        stale_auth = self.flow.authorize("checkpoint_recovery", failures=[failure])
        self.checkpoint(first=3)
        self.assertEqual(inspect_delivery(self.repo, self.flow.log)["delivery"], "uncertain")
        with self.assertRaisesRegex(ValidationError, "latest local attempt"):
            record_push_attempt(self.repo, self.flow.log, stale_auth)
        auth = self.flow.authorize("checkpoint_recovery", uncertain=[observed["uncertain_attempt"]])
        self.checkpoint(first=4)
        record_push_attempt(self.repo, self.flow.log, auth)
        restored = json.loads((self.repo / self.flow.log["task_log_ref"]).read_text(encoding="utf-8"))
        self.assertEqual(inspect_delivery(self.repo, restored)["delivery"], "uncertain")
        with self.assertRaisesRegex(ValidationError, "already consumed"):
            record_push_attempt(self.repo, restored, auth)
        self.git("push", "origin", "HEAD:refs/heads/feature/example")
        self.assertEqual(inspect_delivery(self.repo, restored)["delivery"], "delivered")

    def prepare_final_checkpoint(self):
        self.flow = complete_flow(baseline=self.baseline)
        count = len(self.flow.log["history"])
        # Deliver the fixture's prior history once; final acceptance stays separate.
        prefix = deepcopy(self.flow.log)
        prefix["history"] = prefix["history"][:-1]
        prefix["status"] = prefix["history"][-1]["status"]
        self.checkpoint(log=prefix)
        self.git("push", "origin", "HEAD:refs/heads/feature/example")
        self.checkpoint(first=count)
        return count

    def test_final_checkpoint_recovery_needs_no_success_receipt(self):
        count = self.prepare_final_checkpoint()
        failure = self.fail_push()
        auth = self.flow.authorize("checkpoint_recovery", failures=[failure])
        self.checkpoint(first=count + 1)
        self.assertEqual(replay(self.flow.log).status, "implementation_complete")
        record_push_attempt(self.repo, self.flow.log, auth)
        self.git("push", "origin", "HEAD:refs/heads/feature/example")
        observations = inspect_delivery(self.repo, self.flow.log)
        self.assertEqual(resume_action(self.flow.log, observations)["action"], "finish_final_checkpoint_then_squash_message")
        self.assertEqual(len(event_commits(self.repo, self.flow.log["task_log_ref"])), 3)
        self.assertEqual(self.git("status", "--porcelain").stdout, "")

    def test_interrupted_final_checkpoint_recovers_without_reopening_work(self):
        count = self.prepare_final_checkpoint()
        record_push_attempt(self.repo, self.flow.log)
        observed = inspect_delivery(self.repo, self.flow.log)
        auth = self.flow.authorize("checkpoint_recovery", uncertain=[observed["uncertain_attempt"]])
        self.checkpoint(first=count + 1)
        self.assertEqual(replay(self.flow.log).status, "implementation_complete")
        record_push_attempt(self.repo, self.flow.log, auth)
        self.git("push", "origin", "HEAD:refs/heads/feature/example")
        observed = inspect_delivery(self.repo, self.flow.log)
        self.assertEqual(observed["delivery"], "delivered")
        self.assertEqual(resume_action(self.flow.log, observed)["action"], "finish_final_checkpoint_then_squash_message")
        self.assertEqual(len(event_commits(self.repo, self.flow.log["task_log_ref"])), 3)
        self.assertEqual([r["record"] for r in read_attempts(self.repo, "example")], ["started", "started"])

    def test_uncertain_retry_can_be_authorized_when_remote_inspection_is_unavailable(self):
        self.checkpoint()
        record_push_attempt(self.repo, self.flow.log)
        self.git("remote", "set-url", "origin", str(self.root / "missing.git"))
        observed = inspect_delivery(self.repo, self.flow.log)
        self.assertEqual(observed["delivery"], "uncertain")
        self.assertIn("Cannot inspect remote", observed["uncertain_attempt"]["observation"])
        auth = self.flow.authorize("checkpoint_recovery", uncertain=[observed["uncertain_attempt"]])
        self.checkpoint(first=2)
        self.assertEqual(inspect_delivery(self.repo, self.flow.log)["authorization_event_id"], auth)
        attempt = record_push_attempt(self.repo, self.flow.log, auth)
        # Dispatch can still fail; that real result is recorded as a failure,
        # while the earlier interrupted attempt remains honestly uncertain.
        result = self.git("push", "origin", "HEAD:refs/heads/feature/example", check=False)
        self.assertNotEqual(result.returncode, 0)
        record_push_failure(self.repo, "example", attempt["attempt_id"], result.returncode, "Fixture remote was unavailable.")
        with self.assertRaisesRegex(ValidationError, "already consumed"):
            record_push_attempt(self.repo, self.flow.log, auth)
        self.assertEqual([r["record"] for r in read_attempts(self.repo, "example")], ["started", "started", "failed"])

    def test_uncertain_retry_requires_matching_journal_identity_and_latest_decision(self):
        self.checkpoint()
        record_push_attempt(self.repo, self.flow.log)
        uncertain = inspect_delivery(self.repo, self.flow.log)["uncertain_attempt"]
        misstated = {**uncertain, "attempted_commit": self.baseline}
        bad_auth = self.flow.authorize("checkpoint_recovery", uncertain=[misstated])
        self.checkpoint(first=2)
        self.assertEqual(inspect_delivery(self.repo, self.flow.log)["delivery"], "uncertain")
        with self.assertRaisesRegex(ValidationError, "misstates latest local attempt"):
            record_push_attempt(self.repo, self.flow.log, bad_auth)
        granted = self.flow.authorize("checkpoint_recovery", uncertain=[uncertain])
        self.checkpoint(first=3)
        denied = self.flow.authorize("checkpoint_recovery", decision="denied", uncertain=[uncertain])
        self.checkpoint(first=4)
        self.assertEqual(inspect_delivery(self.repo, self.flow.log)["delivery"], "uncertain")
        with self.assertRaisesRegex(ValidationError, "supersedes"):
            record_push_attempt(self.repo, self.flow.log, granted)
        with self.assertRaisesRegex(ValidationError, "Missing checkpoint retry authorization"):
            record_push_attempt(self.repo, self.flow.log, denied)

    def test_uncommitted_log_and_mutated_committed_log_are_not_delivered(self):
        self.assertEqual(inspect_delivery(self.repo, self.flow.log)["delivery"], "uncommitted")
        self.checkpoint()
        self.flow.log["history"][0]["details"]["request"] = "Mutated request"
        with self.assertRaises(ValidationError):
            committed_checkpoint(self.repo, self.flow.log)

    def test_failed_commit_leaves_checkpoint_uncommitted_and_cannot_push(self):
        path = self.repo / self.flow.log["task_log_ref"]
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(self.flow.log), encoding="utf-8")
        self.git("add", "--", self.flow.log["task_log_ref"])
        result = self.git("-c", "user.name=", "-c", "user.email=", "commit", "-m", "Fixture identity failure", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.git("rev-parse", "HEAD").stdout.strip(), self.baseline)
        self.assertEqual(inspect_delivery(self.repo, self.flow.log)["delivery"], "uncommitted")
        with self.assertRaisesRegex(ValidationError, "Commit the update"):
            record_push_attempt(self.repo, self.flow.log)

    def test_git_metadata_location_is_discovered(self):
        metadata = self.root / "metadata"
        separate = self.root / "separate"
        self.git("init", "--separate-git-dir", str(metadata), str(separate), cwd=self.root)
        self.assertTrue((separate / ".git").is_file())
        self.assertEqual(journal_path(separate, "example").resolve(), metadata / "orchestrator-flow/example/checkpoint-attempts.jsonl")

    def test_next_checkpoint_after_success_has_no_invented_uncertainty(self):
        self.checkpoint()
        record_push_attempt(self.repo, self.flow.log)
        self.git("push", "origin", "HEAD:refs/heads/feature/example")
        with self.assertRaisesRegex(ValidationError, "already delivered"):
            record_push_attempt(self.repo, self.flow.log)
        self.flow.spec_output("requirements")
        self.checkpoint(first=2)
        self.assertEqual(inspect_delivery(self.repo, self.flow.log)["delivery"], "committed")
        record_push_attempt(self.repo, self.flow.log)
        self.git("push", "origin", "HEAD:refs/heads/feature/example")
        self.assertEqual(inspect_delivery(self.repo, self.flow.log)["delivery"], "delivered")

    def test_unrelated_commit_after_checkpoint_is_not_pushed_as_its_update(self):
        self.checkpoint()
        (self.repo / "unrelated.txt").write_text("separate work", encoding="utf-8")
        self.git("add", "unrelated.txt")
        self.git("commit", "-m", "Separate unrelated work")
        with self.assertRaisesRegex(ValidationError, "unrelated commits"):
            record_push_attempt(self.repo, self.flow.log)

    def test_delivery_helpers_work_with_unrelated_staged_and_unstaged_changes(self):
        (self.repo / "unrelated.txt").write_text("separate staged work", encoding="utf-8")
        self.git("add", "unrelated.txt")
        (self.repo / "baseline.txt").write_text("separate unstaged work", encoding="utf-8")
        # File selection/commit is fixture setup; the helpers only track delivery.
        self.checkpoint()
        self.assertEqual(self.git("diff", "--cached", "--name-only").stdout.strip(), "unrelated.txt")
        self.assertEqual(self.git("diff", "--name-only").stdout.strip(), "baseline.txt")
        staged = self.git("diff", "--cached").stdout
        unstaged = self.git("diff").stdout
        record_push_attempt(self.repo, self.flow.log)
        self.git("push", "origin", "HEAD:refs/heads/feature/example")
        self.assertEqual(inspect_delivery(self.repo, self.flow.log)["delivery"], "delivered")
        self.assertEqual(self.git("diff", "--cached").stdout, staged)
        self.assertEqual(self.git("diff").stdout, unstaged)


if __name__ == "__main__":
    unittest.main()
