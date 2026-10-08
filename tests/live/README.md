# Orchestrator Flow local test kit

Use this kit in a separate Codex chat to observe the Codex v2 workflow in three disposable local projects at Basic, Standard, and Maximum assurance. Each project delivers the same four product features through real Planner, Architect, Coder, and Reviewer delegation. Preparing or reading the kit does not start a run.

## Start a run

Open the [master prompt](prompts/master-agent.md) in the new chat and supply one absolute parent test folder. Keep the prompt file available as a file reference so its relative source paths can be resolved. Choose the master's model and reasoning in the UI; GPT-6.1 Sol High is the recommended default. The prompt explicitly selects that assignment for every top-level test Orchestrator, including the planned replacement.

The master allocates the next `testrun-N` under your parent, prepares `basic`, `standard`, and `maximum` working repositories with their own local `*-repo` bare remotes, and keeps private controller records in the run-level `.orchestrator-test/`. Setup contains product inputs and ordinary project guidance only. The first Flow feature creates the application independently in each project.

The master follows the [twelve-case sequence](runbook.md#feature-sequence), creating one new local chat per feature and one replacement for U-S if that recovery boundary is reached. Accepted predecessor branch tips are the next features' explicit baselines. No worktrees, hosted remotes, or merges are needed.

If the three prepared folders must be added as saved Codex projects, the master gives you one request listing those paths. It renders the later prompts, supplies the authorized bounded decisions at real gates, and collects the report. It does not require you to construct fixtures or repeatedly paste prompts.

A fresh request always gets a new run number; numbering is local to the supplied parent. To resume, explicitly name an existing run and request resumption. Submission of the master prompt authorizes the bounded run described there. Repository maintenance alone authorizes none of those consumer operations.

## Operating documents

| Document | Responsibility |
| --- | --- |
| [Overview](overview.md) | Purpose, architecture, evidence standards, and limitations. |
| [Runbook](runbook.md) | Required operator input: setup, lifecycle, authority, evidence, and closeout. |
| [Scenarios](scenarios.md) | Required private operator input: assignments, stimuli, timing, expected observations, and deterministic coverage inventory. |
| [Product proposals](proposals/README.md) | Four completed inputs copied beside each feature's eventual specifications. |
| [Master prompt](prompts/master-agent.md) | User-submitted starting authority and scope. |
| [Workflow runner](prompts/workflow-runner.md) | One feature in one new local chat. |
| [Decisions and stimuli](prompts/test-decisions.md) | Bounded messages delivered at actual workflow gates. |
| [Resume](prompts/resume-run.md) | Same-feature continuation and replacement with actual recovery evidence. |
| [Standalone role exercise](prompts/role-exercise.md) | Clearly labelled supplemental role evidence. |
| [Evidence collection](prompts/collect-evidence.md) | Report and concise release-summary draft without repairing history. |

## Results and retention

The master writes the run's `.orchestrator-test/report.md`. A passed product test, valid wrapper, or completed role turn does not prove native configuration enforcement or final feature acceptance. Reports distinguish Pass, Fail, Unverified, and Not run, and retain historical failures after later success.

Keep complete run folders during workflow implementation, validation, and investigation. UI cleanup and eventual folder disposal are separate user-directed actions; follow the [retention instructions](runbook.md#run-retention-and-eventual-cleanup). Native implementation-phase exercises remain deferred. The [development suite](../README.md) supplies separate deterministic evidence, with gaps recorded in the [coverage inventory](scenarios.md#deterministic-phase-coverage).

Release-specific design decisions remain in the [v2 proposals](../../.docs/v2.0.0/). The current target is Codex v2, not an assurance of compatibility with unknown future contracts.
