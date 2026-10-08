# Workflow runner prompt

Render this for one new feature-specific local chat using observed manifest values. A different feature always gets a new chat; same-feature replacement uses [resume-run.md](resume-run.md). Keep the private scenario catalogue and planned controller choices out of this message.

Substitution checklist:

- Required: `PROPOSAL_PATH`, `WORKING_REPO`, `FEATURE_ID`, `INTEGRATION_BRANCH`, `BASELINE_COMMIT`, `BARE_REMOTE`, `USER_CONSTRAINTS_OR_NONE`, `SKILL_PATH`, `PYTHON_PATH`, and `HUMAN_TEST_AUTHORITY`. Paths and baseline are actual resolved values. Human constraints contain only genuine user-supplied constraints, or `None`.
- `EXPLICIT_BRANCH_INSTRUCTION`: for P-M only, render the complete sentence `Feature branch: test/line-list-project.` For omitted selections remove this entire placeholder paragraph and adjacent excess blank lines. Do not insert an empty value, `auto`, or a generated branch name. Record the resolved default later in the manifest.
- `PENDING_DEFAULTS_CONTEXT`: for L-B only, describe the controller-prepared, unstaged `.orchestrator-flow.json` edit with its exact current values/fingerprint, unchanged index status, U-B accepted tip, and external provenance reference. State that publication and feature-configuration acceptance still require the forthcoming explicit decision. For every other case remove the entire paragraph. Do not include scenario expectations or the private manifest.
- Confirm the predecessor is accepted and delivered, or the initial baseline is the verified bootstrap. Confirm the native chat is created with GPT-6.1 Sol High before sending. Resolve every placeholder; send only text below the divider.

---

Use `$orchestrator-flow` to deliver the feature described in `{{PROPOSAL_PATH}}` in the existing local repository `{{WORKING_REPO}}`.

Feature identifier: `{{FEATURE_ID}}`
Explicit integration branch: `{{INTEGRATION_BRANCH}}`
Starting baseline commit: `{{BASELINE_COMMIT}}`
Local remote: `origin`, resolving to `{{BARE_REMOTE}}`
Human-supplied configuration constraints or explicit assignments: `{{USER_CONSTRAINTS_OR_NONE}}`
Installed linked workflow skill: `{{SKILL_PATH}}`
Workflow helper Python interpreter: `{{PYTHON_PATH}}`

{{EXPLICIT_BRANCH_INSTRUCTION}}

{{PENDING_DEFAULTS_CONTEXT}}

The human has authorized the master test agent to create/message this chat and supply bounded workflow decisions on their behalf. The actual authorization is: {{HUMAN_TEST_AUTHORITY}}. Treat follow-ups explicitly identified as master test decisions as that delegate's decisions, preserving their provenance. Do not describe them as newly typed human approvals. This initial request does not accept configuration or approve future documents.

Run the normal workflow and its real gates. Recommend supported repository defaults when absent and obtain a decision before establishing them. Read the proposal and working-tree defaults, then present the complete feature recommendation: assurance, role/helper model and effort assignments, review-disposition policy, rationale, and any native limitations. Respect explicit human constraints. Wait for delegated acceptance or alternative selection before recording the accepted feature configuration and starting Planner. Feature selection alone does not change or publish repository defaults. Request exact-version artifact approvals, separate initial coding authority, required dispositions/continuations, and final feature acceptance. Present the actual artifact/output and decision references at each gate.

Use actual native Planner, Architect, Coder, and Reviewer subagents with accepted capabilities and their full applicable contracts and bounded authoritative context. Helpers use their own accepted assignments through supported controls. Report an unavailable or unobservable setting and follow the normal direction process; do not silently substitute or simulate a role.

This is a small local personal project. Implement only the proposal and actual accepted later decisions. Preserve existing bootstrap inputs and prior accepted product behavior. Apply the accepted assurance without removing mandatory roles, artifacts, or initial review coverage. Use the installed linked skill and its declared helper environment.

The human authorizes this feature's branch and checkpoint operations against the named local origin. Follow the normal ownership contracts: Planner and Coder publish their owned artifact checkpoints; Orchestrator owns the task log, user gates, and its log/configuration checkpoints. Use explicit paths, preserve unrelated index/working-tree changes, and keep them out of feature reporting and delivery. A failed push triggers the normal global pause and explicit recovery. Do not merge, force-push, deploy, create a worktree or PR, or modify other repositories/installations.

Normal Coder progress at natural checkpoint groups requires neither an interim wrapper nor an acknowledgement before continuing. Every required completion handoff remains complete JSON under its current contract; a pointer or summary does not replace it. Return meaningful progress and required decisions in this chat. The master reads outputs directly; no cross-chat reply is required. A progress request or squash-message request is not final acceptance.
