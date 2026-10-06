"""Codex resources, schema examples, linked setup and document-reader checks."""
from pathlib import Path
import errno
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / ".codex/skills/orchestrator-flow"
sys.path.insert(0, str(BUNDLE / "scripts"))
from read_spec_body import check_document, check_task_completion, spec_lines
from workflow_artifacts import ValidationError, load_schemas, validate_shape, validate_wrapper, workflow_version
from workflow_protocol import replay


class DistributionTests(unittest.TestCase):
    def symlink(self, path, target, directory=False):
        try:
            path.symlink_to(target, target_is_directory=directory)
        except OSError as exc:
            if exc.errno in {errno.EPERM, errno.EACCES} or getattr(exc, "winerror", None) == 1314:
                self.skipTest(f"Native symlink creation unavailable: {exc}")
            raise

    def git(self, directory, *args):
        result = subprocess.run(["git", "-C", str(directory), *args], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_all_distributed_examples_validate(self):
        for name in ("spec_change_wrapper", "spec_review_wrapper", "change_wrapper", "review_wrapper"):
            validate_wrapper(name.replace("_", "-"), json.loads((BUNDLE / "references/wrappers" / (name + ".json")).read_text(encoding="utf-8")))
        examples = BUNDLE / "references/examples"
        for name, kind in (("partial-spec-change", "spec-change-wrapper"), ("blocked-change", "change-wrapper"), ("accepted-limitation-review", "review-wrapper")):
            validate_wrapper(kind, json.loads((examples / (name + ".json")).read_text(encoding="utf-8")))
        validate_shape("repository-config", json.loads((examples / "repository-config.json").read_text(encoding="utf-8")))
        replay(json.loads((ROOT / "tests/fixtures/complete-standard.json").read_text(encoding="utf-8")))

    def test_source_layout_keeps_skill_runtime_and_separates_development_files(self):
        for directory in ("references", "scripts"):
            self.assertTrue((BUNDLE / directory).is_dir())
            self.assertFalse((BUNDLE / directory).is_symlink())
        self.assertFalse((BUNDLE / "Workflow").exists())
        self.assertFalse((BUNDLE / "references/Directives").exists())
        self.assertFalse((BUNDLE / "tests").exists())
        self.assertTrue((ROOT / "Directives/codingAgentDirectives.md").is_file())
        self.assertTrue((ROOT / "tests/fixtures/complete-standard.json").is_file())

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

    def test_broken_version_link_is_a_setup_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            self.symlink(bundle / "VERSION", "missing-version")
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

    def test_linked_skill_uses_its_own_resources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            linked = root / "orchestrator-flow"
            self.symlink(linked, BUNDLE, directory=True)
            (root / "VERSION").write_text("99.0.0", encoding="utf-8")
            self.assertEqual(workflow_version(linked), workflow_version())
            self.assertEqual(len(load_schemas(linked)[0]), 7)
            self.assertTrue((linked / "templates/proposal-template.md").is_file())
            result = subprocess.run([sys.executable, "-B", str(linked / "scripts/validate_orchestrator_artifacts.py"),
                                     "task-log", str(ROOT / "tests/fixtures/complete-standard.json")],
                                    cwd=tmp, capture_output=True, text=True, encoding="utf-8", env=os.environ.copy())
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_relative_resource_links_survive_git_push_and_clone(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, remote, cloned = root / "source", root / "remote.git", root / "clone"
            bundle = source / ".codex/skills/orchestrator-flow"
            bundle.mkdir(parents=True)
            shutil.copyfile(ROOT / "VERSION", source / "VERSION")
            shutil.copytree(ROOT / "templates", source / "templates")
            self.symlink(bundle / "VERSION", "../../../VERSION")
            self.symlink(bundle / "templates", "../../../templates", directory=True)
            self.git(root, "init", "--initial-branch=main", str(source))
            self.git(source, "config", "core.symlinks", "true")
            self.git(source, "config", "user.name", "Workflow tests")
            self.git(source, "config", "user.email", "workflow-tests@example.invalid")
            self.git(source, "config", "commit.gpgsign", "false")
            self.git(source, "add", "--", "VERSION", "templates", ".codex/skills/orchestrator-flow")
            self.git(source, "commit", "-m", "Relative resource link fixture")
            self.git(root, "init", "--bare", "--initial-branch=main", str(remote))
            self.git(source, "push", str(remote), "main")
            self.git(root, "clone", "--config", "core.symlinks=true", str(remote), str(cloned))
            restored = cloned / ".codex/skills/orchestrator-flow"
            for name in ("VERSION", "templates"):
                with self.subTest(resource=name):
                    mode = self.git(cloned, "ls-files", "--stage", "--", ".codex/skills/orchestrator-flow/" + name).split()[0]
                    self.assertEqual(mode, "120000")
                    self.assertTrue((restored / name).is_symlink())
                    self.assertEqual((restored / name).readlink().as_posix(), "../../../" + name)
                    self.assertEqual((restored / name).resolve(strict=True), cloned / name)
            self.assertEqual(workflow_version(restored), workflow_version())
            self.assertTrue((restored / "templates/proposal-template.md").is_file())

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
