"""Codex resource lookup, schema examples and document-reader checks."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / ".codex/skills/orchestrator-flow"
sys.path.insert(0, str(BUNDLE / "scripts"))
from read_spec_body import check_document, check_task_completion, spec_lines, body_chunk, progress_basis
from workflow_artifacts import ValidationError, validate_shape, validate_wrapper, workflow_version
from workflow_protocol import replay


class DistributionTests(unittest.TestCase):
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
        for name, kind in (("partial-spec-change", "spec-change-wrapper"), ("blocked-change", "change-wrapper"), ("accepted-limitation-review", "review-wrapper"),
                           ("same-version-progress", "change-wrapper"), ("no-artifact-planner", "spec-change-wrapper"),
                           ("resolved-spec-review", "spec-review-wrapper"), ("resolved-review", "review-wrapper"),
                           ("phased-plan", "spec-change-wrapper"), ("phase-change", "change-wrapper"),
                           ("phase-review", "review-wrapper"), ("final-phased-change", "change-wrapper")):
            validate_wrapper(kind, json.loads((examples / (name + ".json")).read_text(encoding="utf-8")))
        validate_shape("repository-config", json.loads((examples / "repository-config.json").read_text(encoding="utf-8")))
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
