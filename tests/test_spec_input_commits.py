"""External commits are accounted for by the user's exact decision and Git history."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import unittest

import test_checkpoint
from checkpoint_state import inspect_delivery, read_attempts, record_push_attempt, workflow_checkpoints
from test_relocation import relocate
from validate_orchestrator_artifacts import validate_workspace
from workflow_artifacts import ValidationError
from workflow_protocol import replay, resume_action


ROOT = Path(__file__).resolve().parents[1]


class SpecInputTests(unittest.TestCase):
    git = test_checkpoint.CheckpointTests.git
    checkpoint = test_checkpoint.CheckpointTests.checkpoint
    artifact_checkpoint = test_checkpoint.CheckpointTests.artifact_checkpoint
    fail_push = test_checkpoint.CheckpointTests.fail_push

    def setUp(self):
        test_checkpoint.CheckpointTests.setUp(self)
        self.flow.log["workflow_version"] = "2.1.1"

    def input_path(self, name):
        return self.flow.log["feature_dir"] + "/" + name

    def write(self, path, data):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        self.git("add", "--", path)

    def commit(self):
        self.git("commit", "-m", "User supplied documents")
        return self.git("rev-parse", "HEAD").stdout.strip()

    def add_input(self, *names):
        for name in names or ("proposal-followup.md",):
            self.write(self.input_path(name), "# Révision — 音楽 🎵\n".encode("utf-8"))
        return self.commit()

    def decide(self, commit, decision="granted", operation="accept-spec-input-commit"):
        self.flow.authorize("external_operation", decision=decision, operation=operation)
        entry = self.flow.log["history"][-1]
        entry["details"].update(scope=commit, user_statement=f"My decision on the entire commit {commit} is {decision}.",
                                uncertain_attempts=[])
        return entry

    def request_change(self):
        status = "spec_in_progress" if self.flow.log["status"] == "spec_in_progress" else "spec_changes_requested"
        return self.flow.add("user-change-requested", "Orchestrator", "User", status, details={
            "request": "Revise Requirements for the proposed follow-up.", "earliest_artifact": "requirements", "references": []})

    def candidate(self):
        validate_workspace(replay(self.flow.log), self.repo)

    def push(self):
        self.git("push", "origin", "HEAD:refs/heads/feature/example")

    def record_decision(self, entry):
        log_file = self.repo / self.flow.log["task_log_ref"]
        args = ["--workspace", str(self.repo)]
        scripts = "skills/orchestrator-flow/scripts"
        codex = [ROOT / ".codex" / scripts / "validate_orchestrator_artifacts.py", "task-log", "-", "--previous", log_file]
        claude = [ROOT / ".claude" / scripts / "claude_log.py", "append-entry", "--log", log_file]
        for command, payload in ((codex, self.flow.log), (claude, {key: entry[key] for key in ("actor", "requestor", "event", "details")})):
            result = subprocess.run([sys.executable, "-B", *command, *args], input=json.dumps(payload).encode(), capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.flow.log = json.loads(log_file.read_text(encoding="utf-8"))

    def test_existing_native_recorders_and_intervening_log_checkpoint(self):
        self.checkpoint()
        commit = self.add_input("proposal-café.md", "bugreport-audio.md")
        self.push()
        change = self.request_change()
        intervening = self.checkpoint(first=int(change))
        previous = deepcopy(self.flow.log)
        entry = self.decide(commit)
        self.record_decision(entry)
        self.assertEqual(self.flow.log["history"][:-1], previous["history"])
        self.assertEqual(self.flow.log["history"][-1]["details"], entry["details"])
        self.assertEqual(self.flow.log["status"], previous["status"])
        ack = self.checkpoint(first=int(entry["id"]))
        checkpoints = workflow_checkpoints(self.repo, self.flow.log)
        self.assertEqual([c["commit"] for c in checkpoints][-2:], [intervening, ack])
        self.assertNotIn(commit, [c["commit"] for c in checkpoints])
        self.assertEqual(record_push_attempt(self.repo, self.flow.log)["attempted_commit"], ack)
        self.push()
        self.assertEqual(inspect_delivery(self.repo, self.flow.log)["delivery"], "delivered")

    def test_each_input_commit_needs_its_own_grant(self):
        first_checkpoint = self.checkpoint()
        first = self.add_input("proposal-one.md")
        self.decide(first)
        ack = self.checkpoint(first=2)
        self.push()
        second = self.add_input("bugreport-two.md")
        with self.assertRaisesRegex(ValidationError, second):
            self.candidate()
        self.decide(second)
        self.candidate()
        last = self.checkpoint(first=3)
        self.assertEqual([c["commit"] for c in workflow_checkpoints(self.repo, self.flow.log)], [first_checkpoint, ack, last])
        self.artifact_checkpoint()
        with self.assertRaisesRegex(ValidationError, last):
            record_push_attempt(self.repo, self.flow.log)

    def test_missing_malformed_and_superseded_authority(self):
        self.checkpoint()
        commit = self.add_input()
        self.push()
        previous = deepcopy(self.flow.log)
        with self.assertRaisesRegex(ValidationError, commit):
            self.candidate()
        with self.assertRaisesRegex(ValidationError, commit):
            record_push_attempt(self.repo, self.flow.log)
        for scope in (commit[:12], "a" * len(commit), "feature/example", self.input_path("proposal-followup.md")):
            with self.subTest(scope=scope):
                self.flow.log = deepcopy(previous)
                self.decide(scope)
                with self.assertRaisesRegex(ValidationError, "exact ordinary commit ID"):
                    self.candidate()
        self.flow.log = deepcopy(previous)
        grant = self.decide(commit)
        grant["details"]["limits"]["max_attempts"] = 1
        with self.assertRaisesRegex(ValidationError, "Invalid authority"):
            self.candidate()
        grant["details"]["limits"]["max_attempts"] = None
        self.candidate()
        with self.assertRaisesRegex(ValidationError, "Commit the update"):
            record_push_attempt(self.repo, self.flow.log)
        self.assertEqual(read_attempts(self.repo, "example"), [])
        for decision in ("denied", "deferred"):
            with self.subTest(decision=decision):
                self.decide(commit, decision)
                with self.assertRaisesRegex(ValidationError, "missing effective"):
                    self.candidate()
        self.checkpoint(first=2)
        with self.assertRaisesRegex(ValidationError, "missing effective"):
            workflow_checkpoints(self.repo, self.flow.log)

    def test_withdrawal_requires_delivery_and_preserves_established_history(self):
        self.checkpoint()
        commit = self.add_input()
        self.push()
        self.decide(commit)
        ack = self.checkpoint(first=2)
        self.decide(commit, "denied")
        with self.assertRaisesRegex(ValidationError, ack):
            self.candidate()
        self.git("remote", "set-url", "origin", str(self.root / "unavailable.git"))
        with self.assertRaisesRegex(ValidationError, ack):
            self.candidate()
        self.git("remote", "set-url", "origin", str(self.remote))
        # Model reconciliation finding that the earlier acknowledgment actually reached origin.
        self.git("push", "origin", ack + ":refs/heads/feature/example")
        history = deepcopy(self.flow.log["history"][:2])
        self.candidate()
        self.checkpoint(first=3)
        record_push_attempt(self.repo, self.flow.log)
        self.push()
        self.decide(commit, "deferred")
        self.request_change()
        self.checkpoint(first=4)
        record_push_attempt(self.repo, self.flow.log)
        self.push()
        self.assertEqual(self.flow.log["history"][:2], history)
        self.assertEqual(replay(self.flow.log).authorizations["4"]["decision"], "deferred")
        self.assertEqual(inspect_delivery(self.repo, self.flow.log)["delivery"], "delivered")
        self.candidate()

    def test_remote_must_already_have_ack_even_beneath_later_log_head(self):
        self.checkpoint()
        commit = self.add_input()
        self.push()
        self.decide(commit)
        ack = self.checkpoint(first=2)
        # A stale local tracking ref is not proof of remote delivery.
        self.git("update-ref", "refs/remotes/origin/feature/example", ack)
        self.artifact_checkpoint()
        for head in ("producer", "later log"):
            with self.subTest(head=head):
                if head == "later log":
                    self.request_change()
                    self.checkpoint(first=3)
                observation = inspect_delivery(self.repo, self.flow.log)
                self.assertEqual(observation["delivery"], "uncertain")
                self.assertIn(ack, observation["reason"])
                with self.assertRaisesRegex(ValidationError, ack):
                    record_push_attempt(self.repo, self.flow.log)
                self.assertEqual(read_attempts(self.repo, "example"), [])
                self.assertEqual(self.git("ls-remote", "origin", "refs/heads/feature/example").stdout.split()[0], commit)

    def test_published_ack_allows_later_producer_and_withdrawal(self):
        self.checkpoint()
        commit = self.add_input()
        self.push()
        self.decide(commit)
        ack = self.checkpoint(first=2)
        self.assertEqual(record_push_attempt(self.repo, self.flow.log)["attempted_commit"], ack)
        self.push()
        producer = self.artifact_checkpoint()
        self.assertEqual(record_push_attempt(self.repo, self.flow.log)["attempted_commit"], producer)
        self.push()
        self.decide(commit, "denied")
        self.candidate()
        self.checkpoint(first=3)
        record_push_attempt(self.repo, self.flow.log)
        self.push()
        self.assertEqual(inspect_delivery(self.repo, self.flow.log)["delivery"], "delivered")
        self.assertIn(producer, [c["commit"] for c in workflow_checkpoints(self.repo, self.flow.log)])

    def test_recovery_authority_cannot_bundle_a_hidden_producer(self):
        self.checkpoint()
        commit = self.add_input()
        self.push()
        self.decide(commit)
        ack = self.checkpoint(first=2)
        attempt = record_push_attempt(self.repo, self.flow.log)
        uncertain = inspect_delivery(self.repo, self.flow.log)["uncertain_attempt"]
        self.assertEqual(uncertain["attempt_id"], attempt["attempt_id"])
        self.artifact_checkpoint()
        recovery = self.flow.authorize("checkpoint_recovery", uncertain=[uncertain])
        self.checkpoint(first=3)
        journal = read_attempts(self.repo, "example")
        with self.assertRaisesRegex(ValidationError, ack):
            record_push_attempt(self.repo, self.flow.log, recovery)
        self.assertEqual(read_attempts(self.repo, "example"), journal)

    def test_ack_push_failure_still_needs_exactly_one_recovery_grant(self):
        self.checkpoint()
        commit = self.add_input()
        self.push()
        self.decide(commit)
        self.checkpoint(first=2)
        failure = self.fail_push()
        self.assertEqual(inspect_delivery(self.repo, self.flow.log)["delivery"], "failed")
        with self.assertRaises(ValidationError):
            record_push_attempt(self.repo, self.flow.log)
        recovery = self.flow.authorize("checkpoint_recovery", failures=[failure])
        self.checkpoint(first=3)
        record_push_attempt(self.repo, self.flow.log, recovery)
        self.push()
        with self.assertRaises(ValidationError):
            record_push_attempt(self.repo, self.flow.log, recovery)
        self.assertEqual(inspect_delivery(self.repo, self.flow.log)["delivery"], "delivered")

    def test_late_grant_cannot_excuse_intervening_producer(self):
        self.checkpoint()
        commit = self.add_input()
        self.artifact_checkpoint()
        self.decide(commit)
        with self.assertRaisesRegex(ValidationError, "producer work precedes"):
            self.candidate()
        self.checkpoint(first=2)
        with self.assertRaisesRegex(ValidationError, "producer work precedes"):
            record_push_attempt(self.repo, self.flow.log)

    def test_input_before_relocation_acknowledged_afterward(self):
        self.checkpoint()
        commit = self.add_input()
        old = relocate(self.flow, directory="research/.docs/specs/example")
        destination = self.repo / self.flow.log["feature_dir"]
        destination.parent.mkdir(parents=True)
        (self.repo / old).rename(destination)
        (destination / "task_log.json").write_text(json.dumps(self.flow.log), encoding="utf-8")
        self.git("add", "--", old, self.flow.log["feature_dir"])
        self.git("commit", "-m", "Relocate feature\n\nOrchestrator-Feature: example\nOrchestrator-Checkpoint: log\n"
                 "Orchestrator-Role: Orchestrator\nOrchestrator-Log: " + self.flow.log["task_log_ref"] + "\nOrchestrator-Events: 2-2")
        self.decide(commit)
        self.candidate()
        self.checkpoint(first=3)
        self.push()
        self.candidate()
        self.write(old + "/proposal-stale.md", b"# Stale\n")
        self.decide(self.commit())
        with self.assertRaisesRegex(ValidationError, "outside the permitted"):
            self.candidate()

    def test_mixed_changes_modes_text_and_paths_fail_as_whole_commits(self):
        self.checkpoint()
        old = self.input_path("proposal-old.md")
        base = self.artifact_checkpoint(old, "Original text", "Orchestrator")
        previous = deepcopy(self.flow.log)
        self.git("config", "diff.ignoreSubmodules", "all")
        for defect in ("code", "test", "config", "log", "approved spec", "wrong folder", "lookalike folder", "untitled",
                       "modify", "delete", "rename", "symlink", "submodule", "binary", "encoding", "empty"):
            with self.subTest(defect=defect):
                self.git("switch", "-C", "feature/example", base)
                self.flow.log = deepcopy(previous)
                path = self.input_path("proposal-extra.md")
                if defect == "empty":
                    self.git("commit", "--allow-empty", "-m", "Empty input")
                    commit = self.git("rev-parse", "HEAD").stdout.strip()
                else:
                    self.write(self.input_path("bugreport-valid.md"), b"# Valid input\n")
                    extras = {"code": "app.py", "test": "tests/test_app.py", "config": ".orchestrator-flow.json",
                              "log": self.flow.log["task_log_ref"], "approved spec": self.flow.log["requirements_ref"],
                              "wrong folder": "other/.docs/specs/example/proposal-out.md",
                              "lookalike folder": self.flow.log["feature_dir"] + "-other/proposal-out.md",
                              "untitled": self.input_path("notes.md"), "modify": old}
                    if defect in extras:
                        self.write(extras[defect], b"Changed\n")
                    elif defect == "delete":
                        self.git("rm", "--", old)
                    elif defect == "rename":
                        self.git("mv", old, path)
                    elif defect in ("symlink", "submodule"):
                        mode, obj = ("120000", self.git("rev-parse", base + ":" + old).stdout.strip()) if defect == "symlink" else ("160000", base)
                        self.git("update-index", "--add", "--cacheinfo", mode, obj, path)
                    else:
                        self.write(path, b"# a\0b" if defect == "binary" else b"# bad \xff")
                    commit = self.commit()
                self.decide(commit)
                with self.assertRaisesRegex(ValidationError, "Unaccounted-for commit " + commit):
                    self.candidate()

    def test_commit_message_and_replaced_blob_cannot_supply_authority(self):
        self.checkpoint()
        self.decide("a" * 40)
        with self.assertRaisesRegex(ValidationError, "exact ordinary commit ID"):
            self.candidate()
        self.flow.log["history"].pop()
        ref = self.input_path("proposal-binary.md")
        self.write(ref, b"# binary\0")
        self.git("commit", "-m", "User grants accept-spec-input-commit for the proposal")
        commit = self.git("rev-parse", "HEAD").stdout.strip()
        with self.assertRaisesRegex(ValidationError, commit):
            self.candidate()
        self.decide(commit)
        original = self.git("rev-parse", commit + ":" + ref).stdout.strip()
        replacement = self.git("rev-parse", self.baseline + ":baseline.txt").stdout.strip()
        self.git("replace", original, replacement)
        with self.assertRaisesRegex(ValidationError, "NUL byte"):
            self.candidate()

    def test_malformed_flow_trailer_cannot_fall_back_to_input(self):
        self.checkpoint()
        self.write(self.input_path("proposal-input.md"), b"# Input\n")
        self.git("commit", "-m", "User document\n\nOrchestrator-Checkpoint:")
        self.decide(self.git("rev-parse", "HEAD").stdout.strip())
        with self.assertRaisesRegex(ValidationError, "malformed Flow checkpoint trailer"):
            self.candidate()

    def test_wrong_branch_merge_and_side_parent_are_rejected(self):
        self.checkpoint()
        self.git("switch", "-c", "other")
        side = self.add_input()
        self.decide(side)
        with self.assertRaisesRegex(ValidationError, "Wrong active feature branch"):
            self.candidate()
        self.git("switch", "feature/example")
        self.git("merge", "--no-ff", "-m", "Merge input", "other")
        merge = self.git("rev-parse", "HEAD").stdout.strip()
        self.decide(merge)
        with self.assertRaisesRegex(ValidationError, side + ": expected a single-parent"):
            self.candidate()
        self.flow.log["history"] = self.flow.log["history"][:1]
        self.decide(merge)
        self.decide(side)
        with self.assertRaisesRegex(ValidationError, merge + ": expected a single-parent"):
            self.candidate()

    def publish_blocked_feature(self):
        relocate(self.flow, directory="research/.docs/specs/example")
        self.flow.log["history"].pop()  # Initial nested placement, before the first checkpoint.
        self.checkpoint()
        for name in ("requirements", "design", "tasks"):
            body = "Approved scope.\n"
            if name == "tasks":
                body = "- [ ] 1. **[Stage A]** Complete measurements\n- [ ] 2. **[Stage B]** Verify follow-up\n"
            document = f"# {name}\nContent version: 1\n\n{body}\n## Revision History\n### Version 1 — 2026-09-30\n- Initial draft.\n"
            self.flow.checkpoint_commit = self.artifact_checkpoint(self.flow.log[name + "_ref"], document)
            self.push()
            self.flow.spec_output(name)
            self.flow.approve(name)
        self.flow.spec_output(consolidated=True)
        self.flow.review("spec")
        self.flow.authorize()
        self.flow.start_coding()
        self.checkpoint(first=2)
        task_ref = self.flow.log["tasks_ref"]
        task_text = document.replace("[ ] 1.", "[x] 1.")
        stage_a = self.artifact_checkpoint(task_ref, task_text, "Coder")
        self.push()
        blocked_id = int(self.flow.next_id)
        blocker = {"id": "stage-b", "operation": "Proceed to Stage B", "task_ids": ["2"], "reason": "A2 budget exhausted.",
                   "attempts": [], "evidence": ["Stage A completed."], "depends_on": ["user direction"],
                   "independent_task_ids": [], "required_authorization": "User must select a method within the A2 budget."}
        self.flow.code_output(consolidated=False, blockers=[blocker])
        self.flow.log["history"][-1]["details"]["task_progress"].append(
            {"task_id": "2", "status": "pending", "evidence": "Await scope.", "disposition_ref": None})
        self.checkpoint(first=blocked_id)
        self.push()
        return stage_a, task_text

    def test_blocked_211_feature_resumes_requirements_with_completed_work_preserved(self):
        stage_a, task_text = self.publish_blocked_feature()
        task_ref = self.flow.log["tasks_ref"]
        before = deepcopy(self.flow.log)
        approvals = deepcopy(replay(before).approvals)
        commit = self.add_input("proposal-stage-a2.md")
        self.push()
        with self.assertRaisesRegex(ValidationError, commit):
            self.candidate()
        self.decide(commit)
        self.assertEqual(replay(self.flow.log).status, "blocked")
        self.request_change()
        self.candidate()
        self.checkpoint(first=len(before["history"]) + 1)
        record_push_attempt(self.repo, self.flow.log)
        self.push()
        state = replay(self.flow.log, previous=before)
        self.assertEqual(resume_action(self.flow.log, inspect_delivery(self.repo, self.flow.log))["action"], "start_planner_revision")
        self.assertEqual(state.earliest_artifact, "requirements")
        self.assertEqual(state.approvals, approvals)
        self.assertEqual(self.flow.log["workflow_version"], "2.1.1")
        self.assertEqual(self.flow.log["history"][:len(before["history"])], before["history"])
        self.assertEqual(self.git("show", stage_a + ":" + task_ref).stdout, task_text)
        self.flow.start_spec_revision("User", "requirements")
        self.assertEqual(replay(self.flow.log).status, "spec_in_progress")
        self.flow.authorize("coding")
        with self.assertRaisesRegex(ValidationError, "Coding decision must concern an accepted specification"):
            replay(self.flow.log)

    def test_continuity_acknowledgment_resumes_at_original_blocker(self):
        self.flow.log["workflow_version"] = "2.1.2"
        self.publish_blocked_feature()
        before = deepcopy(self.flow.log)
        ref = before["task_log_ref"]
        self.write(".docs/handoffs/music-analyzer-continuity-002.md", b"# Handoff to the next planning discussion\n")
        commit = self.commit()
        self.push()
        with self.assertRaisesRegex(ValidationError, commit):
            self.candidate()
        grant = self.decide(commit, operation="accept-external-commit")
        self.record_decision(grant)
        ack = self.checkpoint(first=int(grant["id"]))
        self.assertEqual(record_push_attempt(self.repo, self.flow.log)["attempted_commit"], ack)
        self.push()
        delivered = json.loads(self.git("show", "refs/heads/feature/example:" + ref, cwd=self.remote).stdout)
        self.assertEqual(delivered["history"][:-1], before["history"])
        self.assertEqual(delivered["history"][-1]["details"], grant["details"])
        self.assertEqual(delivered["workflow_version"], before["workflow_version"])
        self.assertEqual(delivered["status"], "blocked")
        validate_workspace(replay(delivered, previous=before), self.repo)
        self.assertNotIn(commit, [c["commit"] for c in workflow_checkpoints(self.repo, delivered)])
        observation = inspect_delivery(self.repo, delivered)
        self.assertEqual(observation["delivery"], "delivered")
        self.assertEqual(resume_action(delivered, observation)["action"], "resolve_scoped_blocker")

    def test_mixed_external_commit_uses_effective_operation_at_each_boundary(self):
        self.checkpoint()
        self.git("mv", "baseline.txt", "notes.md")
        self.write("tests/test_input.py", b"# External correction\n")
        self.write("input.bin", b"\xff\x00\x01")
        commit = self.commit()
        self.decide(commit)
        self.decide(commit, operation="accept-external-commit")
        self.candidate()
        ack = self.checkpoint(first=2)
        self.decide(commit)
        with self.assertRaisesRegex(ValidationError, commit):
            self.candidate()
        self.decide(commit, operation="accept-external-commit")
        self.candidate()
        self.checkpoint(first=4)
        self.artifact_checkpoint()
        with self.assertRaisesRegex(ValidationError, ack):
            record_push_attempt(self.repo, self.flow.log)

    def test_general_grant_rejects_external_log_edit(self):
        self.checkpoint()
        ref = self.flow.log["task_log_ref"]
        self.write(ref, (self.repo / ref).read_bytes() + b"\n")
        commit = self.commit()
        self.decide(commit, operation="accept-external-commit")
        with self.assertRaisesRegex(ValidationError, "external change to authoritative log"):
            self.candidate()
