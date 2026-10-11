"""Codex resource lookup, schema examples and document-reader checks."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / ".codex/skills/orchestrator-flow"
sys.path.insert(0, str(BUNDLE / "scripts"))
from read_spec_body import check_document, check_task_completion, spec_lines, body_chunk, progress_basis
from workflow_artifacts import ValidationError, validate_shape, validate_wrapper, workflow_version
from workflow_protocol import replay
from validate_orchestrator_artifacts import record_handoff, prepare_handoff, HandoffError
from workflow_artifacts import json_values_equal


class DistributionTests(unittest.TestCase):
    def handoff(self):
        from flow_fixtures import Flow
        flow = Flow()
        previous = deepcopy(flow.log)
        flow.spec_output("requirements")
        entry = flow.log["history"][-1]
        entry["spec_change_wrapper"]["summary"] = "tasks 1–7; café; 漢字; 😀; e\u0301"
        return previous, entry["spec_change_wrapper"]

    def test_record_handoff_preserves_literal_unicode_under_non_utf8_stdio(self):
        previous, wrapper = self.handoff()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "task_log.json"
            path.write_text(json.dumps(previous), encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(BUNDLE / "scripts/validate_orchestrator_artifacts.py"),
                                     "record-handoff", "-", "--log", str(path)],
                                    input=json.dumps(wrapper, ensure_ascii=False).encode("utf-8"), capture_output=True,
                                    env={**os.environ, "PYTHONIOENCODING": "cp1252"})
            self.assertEqual(result.returncode, 0, result.stderr)
            recorded = json.loads(path.read_bytes())
            self.assertEqual(recorded["history"][:-1], previous["history"])
            self.assertEqual(recorded["history"][-1]["spec_change_wrapper"], wrapper)
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_powershell_utf8_pipeline_preserves_actual_return(self):
        shell = shutil.which("pwsh")
        if shell is None:
            self.skipTest("PowerShell is unavailable; direct UTF-8 transport is tested separately")
        previous, wrapper = self.handoff()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "task_log.json"
            path.write_text(json.dumps(previous), encoding="utf-8")
            # ASCII source reconstructs the actual captured Unicode, then sends
            # literal non-ASCII bytes through the documented PowerShell pipe.
            native = json.dumps(wrapper)
            def quote(value):
                return "'" + value.replace("'", "''") + "'"
            command = "$OutputEncoding = [System.Text.UTF8Encoding]::new($false); "
            command += quote(native) + " | ConvertFrom-Json | ConvertTo-Json -Depth 100 -Compress | & "
            command += quote(sys.executable) + " -B " + quote(str(BUNDLE / "scripts/validate_orchestrator_artifacts.py"))
            command += " record-handoff - --log " + quote(str(path)) + "; exit $LASTEXITCODE"
            result = subprocess.run([shell, "-NoProfile", "-Command", command], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(path.read_bytes())["history"][-1]["spec_change_wrapper"], wrapper)

    def test_recorder_derives_causal_metadata_and_readiness(self):
        from flow_fixtures import Flow
        flow = Flow()
        for artifact in ("requirements", "design"):
            flow.spec_output(artifact)
            flow.approve(artifact)
        previous = deepcopy(flow.log)
        native = flow.spec_output("tasks", consolidated=True)
        recorded = prepare_handoff(previous, native)
        entry = recorded["history"][-1]
        self.assertEqual((entry["id"], entry["event"], entry["actor"], entry["requestor"], entry["status"]),
                         ("6", "spec-updated", "Planner", "User", "spec_in_progress"))
        self.assertEqual(entry["spec_change_wrapper"], native)
        self.assertEqual(recorded["history"][:-1], previous["history"])
        flow.log = recorded
        flow.approve("tasks")
        self.assertEqual(replay(flow.log).next_action(), "start_architect_review")

    def test_small_output_correction_keeps_assignment_and_checkpoint(self):
        from test_recovery_and_reviews import coding_flow
        flow = coding_flow()
        previous = deepcopy(flow.log)
        flow.code_output()
        entry = flow.log["history"][-1]
        native = json.dumps(entry["change_wrapper"])
        invalid_summary = deepcopy(entry["change_wrapper"])
        invalid_summary["summary"] = ""
        with self.assertRaises(HandoffError):
            prepare_handoff(previous, invalid_summary)
        recorded = prepare_handoff(previous, native)
        self.assertEqual(recorded["history"][-1]["event"], "coding-complete")
        self.assertEqual(recorded["history"][-1]["requestor"], "Planner")
        self.assertEqual(recorded["history"][-1]["change_wrapper"], entry["change_wrapper"])
        self.assertEqual(recorded["history"][:-1], previous["history"])
        self.assertEqual(replay(recorded).cycles, replay(previous).cycles)
        # A real producer deficiency still fails under the correct event.
        invalid = deepcopy(entry)
        invalid["change_wrapper"]["task_progress"][0]["status"] = "pending"
        with self.assertRaises(HandoffError) as caught:
            prepare_handoff(previous, json.dumps(invalid["change_wrapper"]))
        self.assertEqual(caught.exception.category, "invalid_native_output")

    def test_recorder_derives_review_and_phase_completion_events(self):
        from flow_fixtures import Flow
        from test_implementation_phases import PhasedFlow
        for phase in ("spec", "code"):
            flow = Flow().finish_spec()
            if phase == "code":
                flow.review("spec")
                flow.authorize()
                flow.start_coding()
                flow.code_output()
            flow.start_review(phase)
            previous = deepcopy(flow.log)
            native = flow.review_output(phase)
            recorded = prepare_handoff(previous, native)
            self.assertEqual(recorded["history"][-1]["event"], phase + "-reviewed")
            self.assertEqual(recorded["history"][-1]["requestor"], "Planner" if phase == "spec" else "Coder")
            self.assertEqual(recorded["status"], phase + "_approved")
        flow = PhasedFlow()
        flow.start_phase("P1")
        previous = deepcopy(flow.log)
        native = flow.finish_phase("P1")
        recorded = prepare_handoff(previous, native)
        self.assertEqual(recorded["history"][-1]["event"], "coding-phase-complete")
        self.assertEqual(recorded["history"][-1]["change_wrapper"], native)
        self.assertEqual(replay(recorded).next_action(), "start_phase_review")

    def test_invalid_native_return_does_not_write_or_invent_failure(self):
        previous, wrapper = self.handoff()
        for native in ("{broken", '{"status":"done"}', {"native_return": json.dumps(wrapper), "entry": {}}):
            with self.subTest(native=native), self.assertRaises(HandoffError) as caught:
                prepare_handoff(previous, native)
            self.assertEqual(caught.exception.category, "invalid_native_output")
        self.assertEqual(len(previous["history"]), 1)

    def test_recording_detects_concurrent_changes_and_failed_readback(self):
        previous, wrapper = self.handoff()
        before = json.dumps(previous).encode("utf-8")
        for reads in ([before, b"concurrent update"], [before, before, b"{}"]):
            with self.subTest(reads=len(reads)), patch.object(Path, "read_bytes", side_effect=reads), \
                    patch.object(Path, "write_bytes") as write, self.assertRaises(HandoffError) as caught:
                record_handoff("task_log.json", wrapper)
            self.assertEqual(caught.exception.category, "recording_error")
            self.assertEqual(write.call_count, len(reads) - 2)

    def test_native_value_comparison_preserves_types_order_and_unicode(self):
        self.assertTrue(json_values_equal({"a": "–", "b": [1]}, {"b": [1], "a": "\u2013"}))
        for left, right in ((True, 1), ([1, 2], [2, 1]), ("é", "e\u0301"), ("–", "â€“")):
            self.assertFalse(json_values_equal(left, right))

    def test_bounded_reader_reassembles_unicode_long_lines_and_fences(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tasks.md"
            body = "# Tasks\nContent version: 1\n" + "é😀漢" * 3000 + "\n~~~md\n## Revision History\n~~~\nTail\n"
            path.write_bytes((body + "## Revision History\nPast revisions\n").replace("\n", "\r\n").encode("utf-8"))
            for size in (7, 17, 8000):
                parts, offset = [], 0
                while True:
                    chunk = body_chunk(path, offset, size)
                    self.assertEqual(chunk["start_offset"], offset)
                    parts.append(chunk["text"])
                    offset = chunk["next_offset"]
                    if chunk["eof"]:
                        break
                self.assertEqual("".join(parts), body)
            # A truncated transport response is discarded; reread its start.
            chunk = body_chunk(path, 30, 71)
            recovered = body_chunk(path, 30, 19)
            self.assertEqual(recovered["text"], chunk["text"][:19])
            self.assertNotIn("Past revisions", chunk["text"])

    def test_progress_normalizes_only_numbered_checkbox_marks_and_newlines(self):
        approved = "# Tasks\nContent version: 1\n- [ ] 1. **[Red]** Witness\n```md\n- [ ] 2. Example\n```\n## Revision History\nInitial\n"
        self.assertEqual(progress_basis(approved), progress_basis(approved.replace("[ ] 1.", "[x] 1.").replace("\n", "\r\n")))
        for old, new in (("Witness", "Different"), ("1. **", "3. **"), ("version: 1", "version: 2"),
                         ("Initial", "Rewritten"), ("[ ] 2.", "[x] 2."), ("Witness", "Witness ")):
            with self.subTest(change=old):
                self.assertNotEqual(progress_basis(approved), progress_basis(approved.replace(old, new)))

    def test_cli_stdin_validates_actual_return_and_candidate_without_snapshots(self):
        from flow_fixtures import Flow
        flow = Flow()
        cli = BUNDLE / "scripts/validate_orchestrator_artifacts.py"
        with tempfile.TemporaryDirectory() as directory:
            authoritative = Path(directory) / "task_log.json"
            authoritative.write_text(json.dumps(flow.log), encoding="utf-8")
            flow.spec_output("requirements")
            def run(kind, value, *args):
                return subprocess.run([sys.executable, "-B", str(cli), kind, "-", *args], input=value,
                                      capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(run("task-log", json.dumps(flow.log), "--previous", str(authoritative)).returncode, 0)
            for bad in ('{"status":"done"}', '{"path":"valid-saved-wrapper.json"}', '{broken'):
                self.assertNotEqual(run("spec-change-wrapper", bad).returncode, 0)
            self.assertNotEqual(run("resume-action", json.dumps(flow.log), "--observations", "-").returncode, 0)
            result = subprocess.run([sys.executable, "-B", str(cli), "resume-action", str(authoritative), "--observations", "-"],
                                    input='{"delivery":"delivered","invocation":"running"}', capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["action"], "recover_running_invocation")
            self.assertEqual([p.name for p in Path(directory).iterdir()], ["task_log.json"])

    def test_all_distributed_examples_validate(self):
        for name in ("spec_change_wrapper", "spec_review_wrapper", "change_wrapper", "review_wrapper"):
            validate_wrapper(name.replace("_", "-"), json.loads((BUNDLE / "references/wrappers" / (name + ".json")).read_text(encoding="utf-8")))
        examples = BUNDLE / "references/examples"
        for name, kind in (("partial-spec-change", "spec-change-wrapper"), ("accepted-limitation-review", "review-wrapper"),
                           ("same-version-progress", "change-wrapper"), ("no-artifact-planner", "spec-change-wrapper"),
                           ("resolved-spec-review", "spec-review-wrapper"), ("resolved-review", "review-wrapper"),
                           ("phased-plan", "spec-change-wrapper"), ("phase-change", "change-wrapper"),
                           ("phase-review", "review-wrapper"), ("final-phased-change", "change-wrapper"),
                           ("continued-planner", "spec-change-wrapper"), ("corrected-coder-output", "change-wrapper")):
            validate_wrapper(kind, json.loads((examples / (name + ".json")).read_text(encoding="utf-8")))
        validate_shape("repository-config", json.loads((examples / "repository-config.json").read_text(encoding="utf-8")))
        from test_recovery_and_reviews import coding_flow
        flow = coding_flow()
        flow.log["history"].append(json.loads((examples / "blocked-coordination.json").read_text(encoding="utf-8")))
        replay(flow.log)
        for path in (ROOT / "tests/fixtures").glob("*.json"):
            replay(json.loads(path.read_text(encoding="utf-8")))

    def test_checkout_resources_are_real_relative_symlinks(self):
        for name in ("VERSION", "templates"):
            with self.subTest(resource=name):
                link = BUNDLE / name
                self.assertTrue(link.is_symlink(), f"Repair the checkout's {name} symlink")
                self.assertEqual(link.readlink().as_posix(), "../../../" + name)
                self.assertEqual(link.resolve(strict=True), ROOT / name)
        self.assertEqual(workflow_version(), (ROOT / "VERSION").read_text(encoding="utf-8").strip())
        for name in ("proposal-template.md", "bugreport-template.md"):
            self.assertTrue((BUNDLE / "templates" / name).is_file())

    def test_missing_or_flattened_version_is_a_setup_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            with self.assertRaisesRegex(ValidationError, "Workflow setup"):
                workflow_version(bundle)
            for content in ("../../../VERSION", "2.0.0"):
                with self.subTest(content=content):
                    (bundle / "VERSION").write_text(content, encoding="utf-8")
                    with self.assertRaisesRegex(ValidationError, "Workflow setup"):
                        workflow_version(bundle)

    def test_cli_commands_from_foreign_working_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "VERSION").write_text("99.0.0", encoding="utf-8")
            cases = [("task-log", ROOT / "tests/fixtures/complete-standard.json"),
                     ("repository-config", BUNDLE / "references/examples/repository-config.json"),
                     ("resume-action", ROOT / "tests/fixtures/complete-standard.json")]
            cases += [(kind, BUNDLE / "references/wrappers" / (kind.replace("-", "_") + ".json"))
                      for kind in ("spec-change-wrapper", "spec-review-wrapper", "change-wrapper", "review-wrapper")]
            for kind, artifact in cases:
                with self.subTest(command=kind):
                    result = subprocess.run([sys.executable, "-B", str(BUNDLE / "scripts/validate_orchestrator_artifacts.py"), kind, str(artifact)],
                                            cwd=tmp, capture_output=True, text=True, encoding="utf-8", env=os.environ.copy())
                    self.assertEqual(result.returncode, 0, result.stderr)
                    if kind == "resume-action":
                        self.assertEqual(json.loads(result.stdout)["action"], "reconcile_checkpoint_delivery")

    def test_spec_reader_excludes_history_before_context_and_handles_fences(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "design.md"
            body = "# Design\nContent version: 1\n\n## Architecture\n```markdown\n## Revision History\n```\nCurrent rationale.\n\n"
            history = "## Revision History\n### Version 1 — 2026-09-30\n- Initial draft and rationale.\n"
            path.write_text(body + history, encoding="utf-8")
            self.assertEqual("".join(spec_lines(path)), body)
            self.assertEqual("".join(spec_lines(path, history=True)), history)
            check_document(path, 1)
            with self.assertRaises(ValueError):
                check_document(path, 2)
            path.write_text(body + history + "## Appendix\nForbidden later main section.\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                check_document(path, 1)

    def test_task_completion_checks_each_actual_checkbox(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tasks.md"
            path.write_text("# Tasks\nContent version: 1\n- [ ] 1. **[Red]** Earlier task\n- [x] 2. **[Green]** Later task\n", encoding="utf-8")
            progress = [{"task_id": "2", "status": "completed"}]
            with self.assertRaisesRegex(ValueError, "every numbered task"):
                check_task_completion(path, progress)
            progress.insert(0, {"task_id": "1", "status": "completed"})
            with self.assertRaisesRegex(ValueError, "task 1 is unchecked"):
                check_task_completion(path, progress)
            progress[0]["status"] = "dispositioned"
            check_task_completion(path, progress)


if __name__ == "__main__":
    unittest.main()
