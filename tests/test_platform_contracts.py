"""Recorded Codex v2 workflow and capability-override checks."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / ".codex/skills/orchestrator-flow"
sys.path.insert(0, str(BUNDLE / "scripts"))
from workflow_protocol import replay, resume_action
from flow_fixtures import Flow


class PlatformContractTests(unittest.TestCase):
    def test_codex_drafting_interruption_and_finalization_walkthrough(self):
        flow = Flow("basic")
        capability = deepcopy(flow.log["capability"])
        flow.spec_output("requirements")
        self.assertEqual(resume_action(flow.log, {"delivery": "delivered"})["action"], "obtain_requirements_approval")
        flow.approve("requirements")
        for name in ("design", "tasks"):
            flow.spec_output(name)
            flow.approve(name)
        flow.spec_output(consolidated=True)
        flow.review("spec", freshness="reused")
        self.assertEqual(replay(flow.log).next_action(), "obtain_coding_authorization")
        flow.authorize()
        flow.start_coding()
        self.assertEqual(resume_action(flow.log, {"delivery": "delivered", "invocation": "completed"})["action"], "record_recovered_output")
        flow.code_output(consolidated=False, progress=True)
        flow.code_output()
        flow.review("code", freshness="reused")
        self.assertEqual(replay(flow.log).next_action(), "obtain_final_user_acceptance")
        flow.complete()
        self.assertEqual(resume_action(flow.log, {"delivery": "uncertain"})["action"], "obtain_checkpoint_outcome_direction")
        self.assertEqual(resume_action(flow.log, {"delivery": "delivered"})["action"], "finish_final_checkpoint_then_squash_message")
        self.assertEqual(replay(flow.log).config["capability"], capability)

    def test_capability_override_preserves_assurance(self):
        flow = Flow()
        capability = {**deepcopy(flow.log["capability"]), "platform": "claude-code"}
        flow.override("/capability", capability)
        state = replay(flow.log)
        self.assertEqual(state.config["capability"], capability)
        self.assertEqual(state.config["assurance_level"], "standard")


if __name__ == "__main__":
    unittest.main()
