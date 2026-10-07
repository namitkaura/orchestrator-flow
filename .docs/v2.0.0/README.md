# Orchestrator Flow v2.0.0 documents

The implemented v2 scope is Codex. Claude Code, GitHub Copilot, and Cursor remain deferred. Historical background stays in [../archived/](../archived/).

The corrections govern producer-owned artifact checkpoints, separate Orchestrator log checkpoints, cumulative Coder handoffs, direct JSON validation, bounded recovery, helper responsibilities and exceptional implementation phases. They take precedence over conflicting original-proposal behavior; workflow version remains 2.0.0. Automated coverage lives in the repository-level [test suite](../../tests/README.md). Test-kit implementation and live runs remain separately authorized work.

| Document | Purpose |
| --- | --- |
| [Original proposal](proposal-orchestrator-flow-v2.0.0.md) | Design intent and decisions, with the subsequent Codex-only scope noted. |
| [Workflow corrections proposal](proposal-orchestrator-flow-v2.0.0-corrections.md) | Focused v2.0.0 workflow corrections and contract clarifications from live testing; takes precedence on its stated changes and excludes test-kit revisions. |
| [Test-kit proposal](proposal-orchestrator-flow-v2.0.0-testkit.md) | Intended live-test kit, historical implementation and findings, and requirements for its correction and relocation to `tests/live/`. |
| [Live test overview](orchestrator-flow-v2.0.0-live-test-plan.md) | Coverage, evidence standards, and the division between automated checks and live observations. |
| [Agent runbook](test-runbook.md) | Set up three working repositories and local remotes, operate the tests, and collect results. |
| [Scenario instructions](test-scenarios.md) | Timed stimuli, expected behavior, and the coverage matrix for the master agent. |
| [Project and feature proposals](proposals/README.md) | Finished inputs for building the baseline and running the follow-up features. |
| [Master prompt](prompts/master-agent.md) | The user-facing starting point; supply only the parent test folder. |

## Starting the tests

Give an agent the [master prompt](prompts/master-agent.md), with the parent test folder. The prompt authorizes bounded setup, creation/messaging of local test chats, scripted decisions on the user's behalf, and evidence collection. The agent reads the runbook and expands the remaining prompts itself.

Choose the master chat's own model and reasoning in the UI. The prompt explicitly tells it to create every test Orchestrator chat with GPT-6.1 Sol High, including replacement chats; no separate model instruction is needed. Each Orchestrator recommends its workflow role/helper capabilities, and the master accepts or changes those recommendations according to the test cases.

The master creates `<test-root>/testrun-1/`, then `testrun-2/` for the next run, and so on. Each container holds `basic`, `standard`, `maximum`, their corresponding `*-repo` bare remotes, and its own `.orchestrator-test` control/evidence/report directory. Existing runs are never reused by a fresh request. The master builds the baseline once per run and seeds its three repositories from that same commit. No worktrees or hosted remotes are needed.

Numbers belong to the chosen parent folder. Supplying a different empty parent starts again at `testrun-1`; there is no global counter shared between test folders.

The desktop chat-creation tool can target saved projects but cannot register new folders as projects. If necessary, the master prepares everything, asks the user once to add the three folders to Codex, and then creates the test chats. No manual editing of JSON, fixture construction, repeated prompt pasting, or gate-by-gate supervision is expected.

Submitting the master prompt starts work. Merely reading these documents does not run the workflow, initialize repositories, or authorize changes to this distribution. These files define a test kit, not completed test results.

## Other prompts

- [Workflow runner](prompts/workflow-runner.md): starts a feature in a local test chat using its proposal.
- [Scripted decisions and stimuli](prompts/test-decisions.md): messages the master renders at actual workflow boundaries.
- [Resume](prompts/resume-run.md): continues an existing test feature without rebuilding its history.
- [Standalone role exercise](prompts/role-exercise.md): fills a coverage gap with a clearly labeled native role test.
- [Evidence collection](prompts/collect-evidence.md): audits the recorded runs without repairing them.

The master owns coordination records inside the allocated run container. Orchestrator owns each consumer feature's real task log and log checkpoints; Planner/Coder publish their owned artifact checkpoints. Do not put test expectations or answer keys into product proposals or runtime role instructions.
