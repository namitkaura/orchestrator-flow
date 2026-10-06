from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".codex/skills/orchestrator-flow/scripts"))
from checkpoint_state import (committed_checkpoint, event_commits, inspect_delivery, journal_path,
                              read_attempts, record_push_attempt, record_push_failure)
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
        self.git("commit", "--only", "-m", f"Record fixture update\n\nOrchestrator-Log: {log['task_log_ref']}\nOrchestrator-Events: {first}-{len(log['history'])}", "--", log["task_log_ref"])
        return self.git("rev-parse", "HEAD").stdout.strip()

    def fail_push(self, authorization=None):
        attempt = record_push_attempt(self.repo, self.flow.log, authorization)
        self.git("remote", "set-url", "origin", str(self.root / "missing.git"))
        result = self.git("push", "origin", "HEAD:refs/heads/feature/example", check=False)
        self.assertNotEqual(result.returncode, 0)
        failure = record_push_failure(self.repo, "example", attempt["attempt_id"], result.returncode, "Fixture remote was unavailable.")
        self.git("remote", "set-url", "origin", str(self.remote))
        return failure

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
        for index in range(1, count):
            prefix = deepcopy(self.flow.log)
            prefix["history"] = prefix["history"][:index]
            prefix["status"] = prefix["history"][-1]["status"]
            self.checkpoint(first=index, log=prefix)
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
        self.assertEqual(len(event_commits(self.repo, self.flow.log["task_log_ref"])), count + 1)
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
        self.assertEqual(len(event_commits(self.repo, self.flow.log["task_log_ref"])), count + 1)
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
        with self.assertRaisesRegex(ValidationError, "without later unrelated commits"):
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
