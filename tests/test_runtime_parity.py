"""Shared runtime parity and linked resources for every integration that implements workflow v2."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

# Integrations that implement v2. GitHub Copilot and Cursor join when they move to v2.
V2_INTEGRATIONS = {
    "codex": ROOT / ".codex/skills/orchestrator-flow",
    "claude-code": ROOT / ".claude/skills/orchestrator-flow",
}

# Runtime files every v2 integration carries byte for byte. A change to any of them, and any
# workflow VERSION bump, updates every v2 integration in the same change.
SHARED_RUNTIME_FILES = (
    "references/common.schema.json",
    "references/task_log_schema.json",
    "references/repository_config.schema.json",
    "references/wrappers/change_wrapper.schema.json",
    "references/wrappers/review_wrapper.schema.json",
    "references/wrappers/spec_change_wrapper.schema.json",
    "references/wrappers/spec_review_wrapper.schema.json",
    "scripts/checkpoint_state.py",
    "scripts/read_spec_body.py",
    "scripts/requirements.txt",
    "scripts/validate_orchestrator_artifacts.py",
    "scripts/workflow_artifacts.py",
    "scripts/workflow_protocol.py",
)

WRAPPER_KINDS = ("spec-change-wrapper", "spec-review-wrapper", "change-wrapper", "review-wrapper")

# Distributed examples and the wrapper each one demonstrates. Example files may carry
# platform-specific values; each integration's examples validate against its own schemas.
EXAMPLE_KINDS = (("partial-spec-change", "spec-change-wrapper"), ("accepted-limitation-review", "review-wrapper"),
                 ("same-version-progress", "change-wrapper"), ("no-artifact-planner", "spec-change-wrapper"),
                 ("resolved-spec-review", "spec-review-wrapper"), ("resolved-review", "review-wrapper"),
                 ("phased-plan", "spec-change-wrapper"), ("phase-change", "change-wrapper"),
                 ("phase-review", "review-wrapper"), ("final-phased-change", "change-wrapper"),
                 ("continued-planner", "spec-change-wrapper"), ("corrected-coder-output", "change-wrapper"))


def executable(path):
    return bool(path.stat().st_mode & 0o111)


class RuntimeParityTests(unittest.TestCase):
    def test_shared_runtime_files_are_identical_in_every_v2_integration(self):
        reference_name, reference = next(iter(V2_INTEGRATIONS.items()))
        problems = []
        for relative in SHARED_RUNTIME_FILES:
            expected = reference / relative
            if not expected.is_file():
                problems.append(f"{reference_name}: missing {relative}")
                continue
            for name, bundle in V2_INTEGRATIONS.items():
                actual = bundle / relative
                if name == reference_name:
                    continue
                if not actual.is_file():
                    problems.append(f"{name}: missing {relative}")
                elif actual.read_bytes() != expected.read_bytes():
                    problems.append(f"{name}: {relative} differs from {reference_name}")
                elif executable(actual) != executable(expected):
                    problems.append(f"{name}: {relative} executable bit differs from {reference_name}")
        self.assertEqual(problems, [], "Update every v2 integration together:\n" + "\n".join(problems))

    def test_shared_file_list_covers_the_codex_runtime(self):
        codex = V2_INTEGRATIONS["codex"]
        runtime = {p.relative_to(codex).as_posix() for p in (codex / "scripts").iterdir()
                   if p.is_file() and not p.name.startswith(".")}
        runtime |= {p.relative_to(codex).as_posix() for p in (codex / "references").rglob("*.schema.json")}
        self.assertEqual(sorted(runtime - set(SHARED_RUNTIME_FILES)), [],
                         "List new shared runtime files in SHARED_RUNTIME_FILES")

    def test_checkout_resources_are_real_relative_symlinks(self):
        for integration, bundle in V2_INTEGRATIONS.items():
            for name in ("VERSION", "templates"):
                with self.subTest(integration=integration, resource=name):
                    link = bundle / name
                    self.assertTrue(link.is_symlink(), f"Repair the checkout's {name} symlink")
                    self.assertEqual(link.readlink().as_posix(), "../../../" + name)
                    self.assertEqual(link.resolve(strict=True), ROOT / name)
            with self.subTest(integration=integration, resource="contents"):
                self.assertEqual((bundle / "VERSION").read_text(encoding="utf-8"), (ROOT / "VERSION").read_text(encoding="utf-8"))
                for name in ("proposal-template.md", "bugreport-template.md"):
                    self.assertTrue((bundle / "templates" / name).is_file())

    def test_tracked_resource_links_keep_git_symlink_mode(self):
        if not shutil.which("git"):
            self.skipTest("git is unavailable")
        for integration, bundle in V2_INTEGRATIONS.items():
            for name in ("VERSION", "templates"):
                with self.subTest(integration=integration, resource=name):
                    path = (bundle / name).relative_to(ROOT).as_posix()
                    result = subprocess.run(["git", "ls-files", "--stage", "--", path], cwd=ROOT, capture_output=True, text=True)
                    if result.returncode != 0 or not result.stdout.strip():
                        self.skipTest(f"{path} is not tracked yet; stage it and check its mode")
                    self.assertEqual(result.stdout.split()[0], "120000", f"{path} must be stored as a symlink")

    def test_cli_commands_from_foreign_working_directory(self):
        fixture = ROOT / "tests/fixtures/complete-standard.json"
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "VERSION").write_text("99.0.0", encoding="utf-8")
            for integration, bundle in V2_INTEGRATIONS.items():
                examples = bundle / "references/examples"
                cases = [("task-log", fixture), ("resume-action", fixture),
                         ("repository-config", examples / "repository-config.json")]
                cases += [(kind, bundle / "references/wrappers" / (kind.replace("-", "_") + ".json")) for kind in WRAPPER_KINDS]
                cases += [(kind, examples / (name + ".json")) for name, kind in EXAMPLE_KINDS]
                for kind, artifact in cases:
                    with self.subTest(integration=integration, command=kind, artifact=artifact.name):
                        result = subprocess.run([sys.executable, "-B", str(bundle / "scripts/validate_orchestrator_artifacts.py"), kind, str(artifact)],
                                                cwd=tmp, capture_output=True, text=True, encoding="utf-8", env=os.environ.copy())
                        self.assertEqual(result.returncode, 0, result.stderr)
                        if kind == "resume-action":
                            self.assertEqual(json.loads(result.stdout)["action"], "reconcile_checkpoint_delivery")


if __name__ == "__main__":
    unittest.main()
