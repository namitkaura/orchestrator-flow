"""Path-only relocation must preserve published history and content identity."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".codex/skills/orchestrator-flow/scripts"))
from workflow_artifacts import ValidationError
from workflow_protocol import replay, resume_action
from flow_fixtures import Flow, complete_flow
import test_checkpoint
from checkpoint_state import inspect_delivery


def relocate(flow, directory="component/.docs/specs/example", inputs=None):
    old = flow.log["feature_dir"]
    flow.add("feature-relocated", "Orchestrator", "User", flow.log["status"], details={
        "from_dir": old, "to_dir": directory, "user_statement": "Move this feature without changing its content.",
        "references": [], "input_moves": inputs or []})
    flow.log["feature_dir"] = directory
    for name in ("requirements", "design", "tasks", "task_log"):
        flow.log[name + "_ref"] = directory + "/" + name + (".json" if name == "task_log" else ".md")
    for name, artifact in flow.artifacts.items():
        if artifact:
            artifact["ref"] = flow.log[name + "_ref"]
    return old


class RelocationProtocolTests(unittest.TestCase):
    def test_nested_initial_location(self):
        flow = Flow()
        relocate(flow)
        flow.log["history"].pop()
        flow.spec_output("requirements")
        self.assertEqual(replay(flow.log).artifacts, flow.artifacts)

    def test_relocation_preserves_wrappers_configuration_approvals_and_assignment(self):
        flow = Flow()
        flow.spec_output("requirements")
        before = deepcopy(flow.log)
        context = deepcopy(flow.contexts)
        relocate(flow)
        state = replay(flow.log, previous=before)
        self.assertEqual(flow.log["history"][:-1], before["history"])
        self.assertEqual(state.artifacts, flow.artifacts)
        self.assertEqual(state.produced, {"requirements": "2"})
        self.assertEqual(state.approvals, {})
        self.assertEqual(flow.contexts, context)
        flow.approve("requirements")
        self.assertEqual(replay(flow.log).approvals["requirements"]["output_ref"]["event_id"], "2")

    def test_approved_and_completed_histories_remain_usable(self):
        flow = complete_flow()
        before = replay(flow.log)
        relocate(flow)
        after = replay(flow.log)
        self.assertEqual(after.approvals, before.approvals)
        self.assertEqual(after.scope_epoch, before.scope_epoch)
        self.assertEqual(resume_action(flow.log, {"delivery": "delivered"})["action"], "finish_final_checkpoint_then_squash_message")

    def test_relocation_preserves_ready_spec_and_rejects_older_reader(self):
        flow = Flow().finish_spec()
        relocate(flow)
        state = replay(flow.log)
        self.assertTrue(state.spec_ready())
        self.assertEqual(state.status, "spec_ready")
        with self.assertRaisesRegex(ValidationError, "2.1.1"):
            replay(flow.log, reader_version="2.1.0")
        previous = deepcopy(flow.log)
        relocate(flow, "another/.docs/specs/example")
        self.assertTrue(replay(flow.log, previous=previous).spec_ready())


    def test_unrecorded_path_change_and_escape_are_rejected(self):
        before = Flow().log
        changed = deepcopy(before)
        changed["feature_dir"] = "component/.docs/specs/example"
        with self.assertRaises(ValidationError):
            replay(changed, previous=before)
        for directory in ("../component/.docs/specs/example", "component/../.docs/specs/example", "C:/x/.docs/specs/example", "component\\.docs/specs/example", "./component/.docs/specs/example", "component//.docs/specs/example", "component/.docs/specs/wrong"):
            flow = Flow()
            relocate(flow, directory)
            with self.subTest(directory=directory), self.assertRaises(ValidationError):
                replay(flow.log)


class RelocationGitTests(unittest.TestCase):
    setUp = test_checkpoint.CheckpointTests.setUp
    git = test_checkpoint.CheckpointTests.git
    checkpoint = test_checkpoint.CheckpointTests.checkpoint
    artifact_checkpoint = test_checkpoint.CheckpointTests.artifact_checkpoint
    # Inherit the real temporary repository/local bare remote fixture only.
    def test_published_history_and_unchanged_return_survive_relocation(self):
        from validate_orchestrator_artifacts import validate_workspace
        self.checkpoint()
        old_ref = self.flow.log["requirements_ref"]
        body = "# Requirements\nContent version: 1\n\nApproved content\n\n## Revision History\n### Version 1 \u2014 2026-09-30\n- Initial draft.\n"
        commit = self.artifact_checkpoint(old_ref, body)
        self.git("push", "origin", "HEAD:refs/heads/feature/example")
        self.flow.checkpoint_commit = commit
        self.flow.spec_output("requirements")
        self.checkpoint(first=2)
        self.git("push", "origin", "HEAD:refs/heads/feature/example")
        feedback = self.flow.add("user-change-requested", "Orchestrator", "User", "spec_in_progress", details={
            "request": "Move the existing requirements only.", "earliest_artifact": "requirements", "references": []})
        self.checkpoint(first=3)
        previous = deepcopy(self.flow.log)
        old = relocate(self.flow)
        destination = self.repo / self.flow.log["feature_dir"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        (self.repo / old).rename(destination)
        validate_workspace(replay(self.flow.log, previous=previous), self.repo)
        path = destination / "task_log.json"
        import json
        path.write_text(json.dumps(self.flow.log, indent=2) + "\n", encoding="utf-8")
        self.git("add", "--", old, self.flow.log["feature_dir"])
        self.git("commit", "-m", "Relocate feature\n\nOrchestrator-Feature: example\nOrchestrator-Checkpoint: log\nOrchestrator-Role: Orchestrator\nOrchestrator-Log: " + self.flow.log["task_log_ref"] + "\nOrchestrator-Events: 4-4")
        self.git("push", "origin", "HEAD:refs/heads/feature/example")
        validate_workspace(replay(self.flow.log), self.repo)
        self.assertEqual(inspect_delivery(self.repo, self.flow.log)["delivery"], "delivered")
        self.flow.spec_output()
        self.flow.log["history"][-1]["spec_change_wrapper"]["causes"] = [{"event_id": feedback, "kind": "event"}]
        state = replay(self.flow.log)
        validate_workspace(state, self.repo)
        self.assertEqual(state.artifacts["requirements"]["version"], 1)
        self.assertEqual(self.flow.log["history"][:3], previous["history"])
        self.assertIsNone(state.feedback_ref)
        self.flow.approve("requirements")
        self.assertEqual(replay(self.flow.log).approvals["requirements"]["version"], 1)

    def test_nested_input_move_is_validated_and_tampering_or_duplicates_fail(self):
        from validate_orchestrator_artifacts import validate_workspace
        self.checkpoint()
        proposal = "component/.docs/specs/proposal-example.md"
        self.artifact_checkpoint(proposal, "original proposal\n", "Orchestrator")
        target = "component/.docs/specs/example/proposal-example.md"
        old = relocate(self.flow, inputs=[{"from": proposal, "to": target}])
        destination = self.repo / self.flow.log["feature_dir"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        (self.repo / old).rename(destination)
        (self.repo / proposal).rename(self.repo / target)
        original_bytes = (self.repo / target).read_bytes()
        validate_workspace(replay(self.flow.log), self.repo)
        (self.repo / target).write_bytes(original_bytes + b"changed")
        with self.assertRaisesRegex(ValidationError, "preserve file bytes"):
            validate_workspace(replay(self.flow.log), self.repo)
        (self.repo / target).write_bytes(original_bytes)
        (self.repo / proposal).write_bytes(original_bytes)
        with self.assertRaisesRegex(ValidationError, "duplicate source"):
            validate_workspace(replay(self.flow.log), self.repo)
        (self.repo / proposal).unlink()
        (destination / "extra.txt").write_text("unlisted", encoding="utf-8")
        with self.assertRaisesRegex(ValidationError, "unlisted files"):
            validate_workspace(replay(self.flow.log), self.repo)
        (destination / "extra.txt").unlink()
        (destination / "task_log.json").write_text(json.dumps(self.flow.log) + "\n", encoding="utf-8")
        self.git("add", "--", old, proposal, self.flow.log["feature_dir"])
        self.git("commit", "-m", "Relocate input\n\nOrchestrator-Feature: example\nOrchestrator-Checkpoint: log\nOrchestrator-Role: Orchestrator\nOrchestrator-Log: " + self.flow.log["task_log_ref"] + "\nOrchestrator-Events: 2-2")
        validate_workspace(replay(self.flow.log), self.repo)
        self.assertEqual((self.repo / target).read_bytes(), original_bytes)
