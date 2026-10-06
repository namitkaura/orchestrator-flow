# Workflow runner prompt

The master renders this file for each feature, using observed manifest values. Send it as the initial message of a local test chat, or as a follow-up in that lane's idle chat. Do not send unresolved placeholders or the private scenario answer key.

---

Use `$orchestrator-flow` to deliver the feature described in `{{PROPOSAL_PATH}}` in the existing local repository `{{WORKING_REPO}}`.

Feature identifier: `{{FEATURE_ID}}`
Feature branch: `{{FEATURE_BRANCH}}`
Explicit integration branch: `{{INTEGRATION_BRANCH}}`
Starting baseline commit: `{{BASELINE_COMMIT}}`
Local remote: `origin`, resolving to `{{BARE_REMOTE}}`
Human-supplied configuration constraints or explicit assignments: `{{USER_CONSTRAINTS_OR_NONE}}`
Workflow helper Python interpreter: `{{PYTHON_PATH}}`

This is a disposable test project. The human user has authorized the master test agent to create/message this chat and to supply bounded workflow decisions on their behalf. The actual authorization is: `{{HUMAN_TEST_AUTHORITY}}`. Treat subsequent messages explicitly identified as master test decisions as that delegate's decisions, preserving their provenance in statements/rationale. Do not describe them as newly typed human approvals. This initial prompt does not accept a complete configuration or approve documents that do not yet exist.

Run the normal workflow and all its real gates. Recommend supported repository defaults when absent and obtain a decision before establishing them. Assess the proposal and repository defaults, then present your recommended feature assurance, role/helper model and effort assignments, and review-disposition policy with rationale and any limitations. Respect explicit human constraints. Wait for the master's delegated acceptance or alternative selection before recording the accepted feature configuration and starting Planner. A feature selection does not change repository defaults unless explicitly requested. Request approval of actual document versions, separate initial coding authorization, any required dispositions/continuations, and final feature acceptance. At a gate, present the concrete artifact/output and references needed for the next decision, then wait. Do not infer all future decisions from this starting prompt.

Use actual native Planner, Architect, Coder, and Reviewer subagents and their assigned capabilities. Pass their full applicable contracts and authoritative bounded context. Invoke helpers through supported mechanisms with their own assignment. If a required native setting/delegation cannot be honored, report the actual limitation and await direction; do not substitute silently or act as a virtual role.

The sample project is local, private, and small. Keep product scope consistent with the proposal and actual accepted later decisions. Apply the selected assurance while retaining mandatory roles, artifacts, task boundaries, and initial review coverage. Use the installed linked skill; do not copy its runtime into this repository.

Only this Orchestrator coordinates feature Git writes and task-log/configuration updates. The human has authorized this test feature's branch and checkpoint operations against its named local origin. Keep unrelated work out of checkpoints. Do not merge, force-push, deploy, create a worktree or PR, or modify other repositories/installations. A failed checkpoint push follows the normal global pause and explicit recovery procedure.

Return meaningful progress and required decisions in this chat. The master reads this chat and artifacts directly; no cross-chat reply is required. Do not mark a feature complete merely because the controller asks for progress or a squash message.
