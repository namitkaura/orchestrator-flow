# Orchestrator Flow live test overview

The Codex v2 kit observes real agents in three disposable local repositories at Basic, Standard, and Maximum assurance. The user supplies a parent test folder and submits the [master prompt](prompts/master-agent.md) in a separate chat. The [runbook](runbook.md) and private [scenarios](scenarios.md) contain the operating requirements; this overview explains their purpose and limits.

## What the two test layers establish

The [development suite](../README.md) checks schemas, recorded transitions, document reading, and Git recovery. Live runs observe whether native agents actually choose the required actions, use accepted settings, read the necessary inputs, and produce the claimed results. Neither layer substitutes for the other.

| Area | Live observations |
| --- | --- |
| Assurance | Complete initial reviews; proportionate Basic/Standard remediation; comprehensive Maximum review; real repair limits, evidence continuity, and assurance overrides. |
| Capability | Accepted recommendations and changed initial selections; recorded later overrides; native role/helper assignments; unavailable settings; persistence through recovery. |
| Ownership | Planner publishes specs; Coder owns intentional implementation/test/documentation/progress edits and artifact checkpoints; helpers explore and execute tests; Orchestrator owns gates, configuration, logs and their checkpoints. |
| Workflow | Sequential document approvals, coding authority, dispositions, cumulative completion returns, recovery before a completion wrapper, rejected artifact pushes, unrelated-change preservation, and explicit feature acceptance. |

Capability is a model/effort assignment, independently of assurance. The goal is enforcement and persistence, not comparing model quality, speed, token use, or cost. The [configuration contract](../../.codex/skills/orchestrator-flow/references/workflow-protocol.md#configuration-and-authority) distinguishes repository defaults from accepted feature snapshots. The [assurance policy](../../.codex/skills/orchestrator-flow/references/assurance.md) retains mandatory roles and complete initial coverage at every level.

## Product and chat lifecycle

Each project runs four complete features: initial line-list application, exact uniqueness, output limit, and case-insensitive uniqueness. Setup supplies only ordinary guidance, ignore rules, and the completed [product inputs](proposals/README.md). The master does not build the application. Each feature has its own Orchestrator chat and starts from its accepted predecessor's actual branch tip. There are twelve planned feature chats plus the U-S replacement if its recovery boundary is reached.

The small features use the ordinary single-Coder-assignment path, with natural checkpoint groups and no per-group review or acknowledgement. Native implementation phases are deferred; their deterministic evidence and remaining gaps are listed in the [phase coverage inventory](scenarios.md#deterministic-phase-coverage).

The master operates outside the workflow under test and acts as the user's explicitly authorized delegate at actual gates. Each feature uses native Planner, Architect, Coder, Reviewer, and helper delegation. The master inspects actual work before approving it, and records provenance for its decisions. This tests delegated decision handling; direct human interaction is a separate observation.

The revised recovery case distinguishes an initially selected capability from a recorded helper override, and fresh Orchestrator context from fresh Coder context. U-B's future-default edit remains uncommitted during that feature and is explicitly adopted and published by L-B's Orchestrator during initialization. These are test-kit scenario choices, not new runtime restrictions.

## Evidence and limitations

| Result | Meaning |
| --- | --- |
| Pass | The behavior occurred and sufficient evidence supports the expectation. |
| Fail | An observed action or omission contradicts the applicable contract. |
| Unverified | An attempted variant or available observations cannot establish the behavior. |
| Not run | The variant was not attempted, including blocked successors and deferred native phases. |

Reports separate full native workflows, standalone role exercises, deterministic tests, and inspection/inference. Saved settings do not prove actual invocation settings. A wrapper saying `full` does not establish complete review. An accepted feature can retain a historical failure; an unaccepted feature can still provide useful evidence for particular behaviors.

A complete original native return is required for an exact-return verdict. Summaries and truncated captures retain an evidence limit even if the recorded wrapper validates. Product tests cannot establish authority enforcement. Git author names alone cannot establish which agent published a checkpoint.

Local bare remotes exercise actual Git delivery without hosting/authentication coverage. Missing native controls, lost timing windows, or unavailable original outputs remain explicit limits. Fixture metadata is validated before a standalone exercise so unrelated invalid input does not confound the intended observation. The master does not repair the runtime to make a case pass.

## Closeout and retention

Closeout preserves all run files during workflow implementation, validation, and investigation. Later UI cleanup and eventual disposal are separate user-directed actions under the [runbook lifecycle](runbook.md#run-retention-and-eventual-cleanup). A concise final validation summary remains with release documentation before disposable runs are deleted; raw evidence is not retained indefinitely by default.

## Contract references

- [Workflow protocol](../../.codex/skills/orchestrator-flow/references/workflow-protocol.md)
- [Assurance policy](../../.codex/skills/orchestrator-flow/references/assurance.md)
- [Codex entry and capability rules](../../.codex/skills/orchestrator-flow/SKILL.md)
- [Role contracts and schemas](../../.codex/skills/orchestrator-flow/references/)
- [Release proposals](../../.docs/v2.0.0/)
