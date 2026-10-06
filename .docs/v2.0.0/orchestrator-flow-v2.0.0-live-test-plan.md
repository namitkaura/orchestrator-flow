# Orchestrator Flow v2.0.0 live test overview

Test the Codex workflow in three disposable local repositories at Basic, Standard, and Maximum assurance. An agent performs setup and drives the tests; the user supplies only a parent test folder. Each fresh run gets its own `testrun-N` container with fixed repository names and isolated evidence. Begin with the [master prompt](prompts/master-agent.md). Operational details live in the [runbook](test-runbook.md), [scenarios](test-scenarios.md), and separate prompt files.

## What is tested

The existing [Python suite](../../tests/README.md) checks schemas, recorded transitions, document reading, and Git recovery. Live runs establish whether real agents select the correct actions, invoke the correct native roles/settings, respect gates, and produce the claimed artifacts. Neither layer substitutes for the other.

| Area | Coverage |
| --- | --- |
| Assurance | Complete initial reviews at all levels; proportional Basic/Standard remediation; impact-based follow-up; comprehensive Maximum passes; cycle limits and stalled loops; evidence reuse/revalidation; in-flight overrides. |
| Capability | Per-role model and effort, helpers, explicit inheritance, unavailable assignments, configuration precedence, persistent overrides, repository defaults, and native context continuity. |
| Ownership | Planner authors specs; Coder implements approved work; Architect/Reviewer remain read-only; Orchestrator owns user gates, task log, known issues, and Git checkpoints. |
| Workflow | All repair policies, artifact approval/version rules, incremental and consolidated outputs, checkpoints, scoped blockers, push failure/recovery, final acceptance, and unsupported historical logs. |

Each scenario checks both the Orchestrator's enforcement and the relevant role's actual behavior. High capability does not imply Maximum assurance; lower assurance does not permit skipping roles, documents, initial coverage, or explicit authorization.

Capability coverage verifies that accepted model/effort assignments are applied to the intended roles and helpers, remain in effect, and survive overrides and resumption. Cover accepting the Orchestrator's recommendations unchanged and selecting different supported settings before initialization as separate cases, followed by overrides to an existing feature. Use a small mix of supported assignments to expose unintended inheritance or fallback. This is workflow contract verification; do not rank models or reasoning levels by output quality, speed, token use, or cost, or run a benchmark grid. Capability maps can differ across runs; check each assurance contract against that feature's accepted settings.

Assurance names are defined in [common.schema.json](../../.codex/skills/orchestrator-flow/references/common.schema.json), and their behavior in [assurance.md](../../.codex/skills/orchestrator-flow/references/assurance.md). Capability has no named tiers: it is a model/effort assignment for each of the four roles plus helpers. The [configuration contract](../../.codex/skills/orchestrator-flow/references/workflow-protocol.md#configuration-and-capability) defines repository defaults in `.orchestrator-flow.json` and accepted feature snapshots in `task_log.json`. Each Orchestrator recommends settings first; the master then acts as the user's delegate to accept or select alternatives. It records both the recommendation and the final choice in controller evidence, and the accepted map in the run manifest. Initial runner prompts carry actual human constraints, not preselected test assignments.

## Test project and run shape

The [baseline proposal](proposals/00-line-list-project.md) defines a tiny standard-library Python CLI. The master builds it once as ordinary test setup and seeds all three repositories with identical code. That setup is not counted as an Orchestrator Flow run.

All three lanes run [unique lines](proposals/01-unique-lines.md) from the same baseline. Basic accepts the valid recommended capability map unchanged; Standard selects a supported alternative before initialization. These are separately reported cases C1-A and C1-B. Maximum accepts or selects supported settings within scope. Basic then runs [output limit](proposals/02-output-limit.md); Standard runs [case-insensitive uniqueness](proposals/03-ignore-case.md). These two short follow-ups exercise additional gates, settings, evidence, and recovery, including later capability overrides. Maximum gets targeted follow-up review exercises if its core run does not naturally exercise those obligations. Do not repeat every feature for every model/effort combination.

Follow-up branches start from the preceding accepted feature branch. Its tip is the explicitly selected integration baseline for that next test. Agents never merge into `main`; no manual merge is needed between test features.

## Master agent and delegated decisions

The master operates outside the workflow under test. It creates and messages separate local test chats, observes real gates, and supplies bounded decisions as the user's explicitly authorized test representative. Each runner uses actual Planner, Architect, Coder, and Reviewer subagents. This avoids testing an Orchestrator that grants its own approvals.

The user authorized scripted document approvals, coding authorization, bounded retry/continuation decisions, and final acceptance in the disposable test scope. The [master prompt](prompts/master-agent.md) carries that authorization when submitted for a run. Decisions must identify this provenance; do not pretend they are newly typed human messages or alter the runtime schemas to add a test bypass. This tests delegated decision handling; direct human interaction remains a separate observation.

The master approves only conforming artifacts and work. Unexpected scope/policy choices return to the user. A failure can stop one scenario while the master collects evidence and continues unaffected repositories. It does not trigger open-ended repair work.

## Evidence and limits

| Result | Meaning |
| --- | --- |
| Pass | The behavior was exercised and its evidence supports the expected result. |
| Fail | An observed action or omission contradicts the contract. |
| Unverified | The client lacks required observability or the condition could not reasonably be exercised. |
| Not run | The scenario or variant was not attempted. |

Preserve actual user/delegate decisions, native invocation records, role outputs, commands/results, document versions, logs, and Git correspondence. Requested settings and effective settings are separate evidence. A model's self-identification is not proof of its configuration. A wrapper saying `full` is not proof that comprehensive review occurred.

Native standalone role exercises demonstrate that role's behavior, not an orchestrated handoff. They use standalone context and must not be inserted into a live log as historical role output. Synthetic fixture/replay tests remain separately labeled; never invent approval, invocation, or push history to make a live scenario pass.

Judge factual defects and authority violations strictly. Judge discretionary classification/remediation against project consequences and assurance, without requiring exact wording or a fixed count of findings. Observe avoidable rereads, redundant fresh contexts, repeated questions, and unnecessary repairs without imposing an exact token threshold.

Local bare remotes exercise real Git delivery without a hosting service. They do not test network/hosting authentication. Previously skipped symlink-creation checks remain a limitation until run with suitable privileges. Rare failures that cannot be induced economically retain their automated coverage and a clearly stated live gap.

## Contract references

- [Workflow protocol](../../.codex/skills/orchestrator-flow/references/workflow-protocol.md)
- [Assurance policy](../../.codex/skills/orchestrator-flow/references/assurance.md)
- [Codex entry and capability rules](../../.codex/skills/orchestrator-flow/SKILL.md)
- [Role contracts and schemas](../../.codex/skills/orchestrator-flow/references/)
- [Automated coverage](../../tests/README.md)
