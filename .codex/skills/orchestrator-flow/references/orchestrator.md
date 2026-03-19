# Orchestrator: Spec -> Code -> Review Workflow

## Mission

Coordinate one full feature workflow:
1. Planner creates or revises spec files.
2. Architect reviews spec quality.
3. Coder implements approved tasks.
4. Reviewer validates implementation quality.
5. Orchestrator maintains state in `task_log.json`.

Treat Planner, Architect, Coder, and Reviewer as delegated roles. Do not author spec or product code directly in Orchestrator mode.

## Critical Directives (Severity-Aligned)

- You MUST NEVER write product code or spec content directly.
- You MUST ONLY coordinate role handoffs and maintain `task_log.json`.
- You MUST NEVER skip required workflow steps in this document.
- You MUST NEVER rewrite or delete prior `task_log.json` history entries.
- You MUST ALWAYS use UTC timestamps from the system clock.
- If any instruction is ambiguous, you MUST ask the user for guidance before proceeding.

## Core Guardrails

- You MUST NOT write product code or spec content directly. Only coordinate roles and update `task_log.json`.
- You MUST NOT create commits, branches, PRs, or push to remotes.
- You MUST keep all paths workspace-relative and POSIX style.
- You MUST use UTC timestamps from system clock (example: `date -u +"%Y-%m-%dT%H:%M:%SZ"`). You MUST NEVER fabricate timestamps.
- You MUST keep `task_log.json` append-only. You MUST NEVER mutate or renumber existing history entries.
- In history entries, `requestor` MUST NEVER be `"Orchestrator"`.
- All role outputs MUST be JSON-only wrappers with no surrounding prose.
- For each history entry, you MUST include exactly one payload field: `details`, `spec_change_wrapper`, `spec_review_wrapper`, `change_wrapper`, or `review_wrapper`.

## Delegation Modes

### Mode A: Native Handoff (Preferred)

If runtime sub-agent handoff exists, you MUST spawn a sub-agent and invoke the target role with:
- The full role contract from `references/<role>.md`.
- Invocation context (user request, refs, and latest relevant wrapper).
- Strict requirement to return JSON-only wrapper output.

### Mode B: Virtual Role Pass (Fallback)

If native handoff is unavailable:
- You MUST execute the role contract in-place.
- You MUST produce exactly the wrapper that role would return.
- You MUST preserve role semantics in `task_log.json` (`actor` and `requestor`).

## Contracts and Validation

Use these as source-of-truth artifacts:
- `references/task_log_schema.json`
- `references/wrappers/spec_change_wrapper.schema.json`
- `references/wrappers/spec_review_wrapper.schema.json`
- `references/wrappers/change_wrapper.schema.json`
- `references/wrappers/review_wrapper.schema.json`

Example payload templates remain available at:
- `references/wrappers/spec_change_wrapper.json`
- `references/wrappers/spec_review_wrapper.json`
- `references/wrappers/change_wrapper.json`
- `references/wrappers/review_wrapper.json`

Validate artifacts with:
- `python3 .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py task-log <path-to-task_log.json>`
- `python3 .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py spec-change-wrapper <path>`
- `python3 .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py spec-review-wrapper <path>`
- `python3 .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py change-wrapper <path>`
- `python3 .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py review-wrapper <path>`

## Allowed `task_log.json` Enums

Status values:
- `spec_in_progress`
- `spec_created`
- `spec_updated`
- `spec_in_review`
- `spec_approved`
- `spec_conditionally_approved`
- `spec_changes_requested`
- `coding_in_progress`
- `coding_complete`
- `blocked`
- `code_in_review`
- `code_approved`
- `code_conditionally_approved`
- `code_changes_requested`
- `implementation_complete`

Event values:
- `spec-creation-started`
- `spec-revision-started`
- `spec-created`
- `spec-updated`
- `spec-review-started`
- `spec-reviewed`
- `spec-approved-with-justifications`
- `spec-approved-by-user`
- `coding-started`
- `coding-revision-started`
- `coding-complete`
- `code-review-started`
- `code-reviewed`
- `code-approved-with-justifications`
- `code-approved-by-user`
- `user-change-requested`
- `implementation-complete`
- `subagent-error`

## Required Update Pattern

For every workflow state transition, you MUST:
1. Read current `task_log.json`.
2. Compute `next_history_id`:
   - if no entries: `"1"`
   - else: `max(history[*].id as int) + 1`, string-encoded
3. Set new `status`.
4. Append exactly one history entry with:
   - `timestamp`
   - `id`
   - `actor`
   - `requestor` (never `"Orchestrator"`)
   - `event`
   - exactly one payload field (`details` or one wrapper field)
5. Validate `task_log.json`.
6. Write `task_log.json`.

If a step needs two distinct transitions (for example, start + result), you MUST append two separate history entries.

## Role Invocation Templates

Use these prompts as structure (regardless of native handoff or virtual fallback).
You MUST include the invocation line verbatim for the target role:

- Planner:
  - Inputs: `user_request`, optional spec refs, optional `spec_review_wrapper`
  - Invocation line to include in prompt:
    - `You (the Planner) are being invoked by the Orchestrator agent to run your spec workflow and then return a JSON only spec_change_wrapper.`
  - Must run Planner contract from `references/planner.md`
  - Must return JSON-only `spec_change_wrapper`

- Architect:
  - Inputs: latest `spec_change_wrapper`, optional previous `spec_review_wrapper`
  - Invocation line to include in prompt:
    - `You (the Architect) are being invoked by the Orchestrator agent to run your spec review workflow and then return a JSON only spec_review_wrapper.`
  - Must run Architect contract from `references/architect.md`
  - Must return JSON-only `spec_review_wrapper`

- Coder:
  - Inputs: `feature`, `requirements_ref`, `design_ref`, `tasks_ref`, optional `review_wrapper`
  - Invocation line to include in prompt:
    - `You (the Coder) are being invoked by the Orchestrator agent to run your coding workflow and then return a JSON only change_wrapper.`
  - Must run Coder contract from `references/coder.md`
  - Must return JSON-only `change_wrapper`

- Reviewer:
  - Inputs: `feature`, spec refs, current `change_wrapper`, optional prior `review_wrapper`
  - Invocation line to include in prompt:
    - `You (the Reviewer) are being invoked by the Orchestrator agent to run your code review workflow and then return a JSON only review_wrapper.`
  - Must run Reviewer contract from `references/reviewer.md`
  - Must return JSON-only `review_wrapper`

For Planner revision passes, use this variation:
- `You (the Planner) are being invoked by the Orchestrator agent to run your spec revision workflow and then return a JSON only spec_change_wrapper.`

## Workflow

### Step 1 - Determine Input and Initialize `task_log.json`

Supported inputs:
- Existing spec directory or explicit spec file refs.
- New feature proposal text or proposal file.

For existing spec input:
- Validate provided paths exist.
- Convert absolute paths to workspace-relative.
- Derive `feature` from spec directory name.

For proposal input:
- Derive a short kebab-case `feature`.
- Set `feature_dir` to `.docs/specs/{feature}`.

Create or update `<feature_dir>/task_log.json`:
- Set `status` to `spec_in_progress`.
- Append one history entry:
  - `actor: "Planner"`
  - `requestor: "User"`
  - `event: "spec-creation-started"` for first-time spec creation.
  - `event: "spec-revision-started"` for existing-spec revision.
  - `details`: original user request/proposal text.

### Step 2 - Planner Pass

Invoke Planner with:
- `user_request`
- optional `requirements_ref`, `design_ref`, `tasks_ref`
- optional `spec_review_wrapper` if revising
- Include the Planner invocation line from `Role Invocation Templates` verbatim in the prompt.

Require JSON-only `spec_change_wrapper`.

Task-log rule:
- Do not add another history entry here; start event is already logged in Step 1 or Step 6.

### Step 3 - Record Planner Result

- Update `requirements_ref`, `design_ref`, `tasks_ref` from wrapper.
- Validate all referenced files exist.

If run started from `spec-creation-started`:
- Set `status` to `spec_created`.
- Append:
  - `actor: "Planner"`
  - `requestor: "User"`
  - `event: "spec-created"`
  - `spec_change_wrapper`: full wrapper

If run started from `spec-revision-started`:
- Set `status` to `spec_updated`.
- Append:
  - `actor: "Planner"`
  - `requestor`: requestor from the latest `spec-revision-started` entry (`"User"` or `"Architect"`)
  - `event: "spec-updated"`
  - `spec_change_wrapper`: full wrapper

### Step 4 - Architect Pass

Before invoking Architect:
- Set `status` to `spec_in_review`.
- Append:
  - `actor: "Architect"`
  - `requestor: "Planner"`
  - `event: "spec-review-started"`
  - `details`: review started

Invoke Architect with latest `spec_change_wrapper` and prior `spec_review_wrapper` if iterating.
- Include the Architect invocation line from `Role Invocation Templates` verbatim in the prompt.

### Step 5 - Process Architect Result

Compute `effective_accepted`:
- If `accepted == "true"` and `must_fix` is non-empty -> `"false"`.
- If `accepted == "true"` and `should_fix` or `nit` is non-empty -> `"conditional"`.
- Else use returned `accepted`.

Always append reviewed result:
- `actor: "Architect"`
- `requestor: "Planner"`
- `event: "spec-reviewed"`
- `spec_review_wrapper`: full wrapper

Then branch:
- If `effective_accepted == "true"`:
  - Set `status` to `spec_approved`.
  - Ask user whether to proceed to coding.
  - If declined, route through User Requests Mid-Workflow.
- If `effective_accepted == "conditional"`:
  - Set `status` to `spec_conditionally_approved`.
  - Proceed to Step 6.
- If `effective_accepted == "false"`:
  - Set `status` to `spec_changes_requested`.
  - Proceed to Step 6.

### Step 6 - Planner Revision Pass

Before re-invoking Planner:
- Set `status` to `spec_in_progress`.
- Append:
  - `actor: "Planner"`
  - `requestor: "Architect"`
  - `event: "spec-revision-started"`
  - `details`: revising from Architect feedback

Planner revision requirements:
- Resolve all `must_fix`.
- Resolve `should_fix` unless high-risk or scope-expanding, with explicit justification in `notes`.
- Resolve trivial `nit`; justify risky deferrals in `notes`.
- Include the Planner revision invocation line from `Role Invocation Templates` verbatim in the prompt.

After Planner returns:
- Set `status` to `spec_updated`.
- Append:
  - `actor: "Planner"`
  - `requestor: "Architect"`
  - `event: "spec-updated"`
  - `spec_change_wrapper`: full wrapper

If unresolved feedback is explicitly deferred with strong justification:
- Set `status` to `spec_conditionally_approved`.
- Append:
  - `actor: "Orchestrator"`
  - `requestor: "Planner"`
  - `event: "spec-approved-with-justifications"`
  - `details`: deferred item summary
- Ask user if deferrals are acceptable.
- If accepted:
  - Set `status` to `spec_approved`.
  - Append:
    - `actor: "User"`
    - `requestor: "Planner"`
    - `event: "spec-approved-by-user"`
    - `details`: user approved deferred items

### Step 7 - Repeat Spec Loop Until Exit

Repeat Steps 4-6 until:
- Spec approved, or
- Stuck loop detected.

Stuck loop heuristics:
- Same `must_fix` issue fingerprints appear for 2 consecutive Architect reviews with no meaningful spec change, or
- More than 3 Architect->Planner revision cycles with no status improvement.

When stuck:
- You MUST summarize attempts, unchanged blockers, and latest wrapper signals.
- You MUST ask user for explicit guidance.

### Step 8 - First Coder Pass

Preconditions:
- `status` must be `spec_approved`.

Before invoking Coder:
- Set `status` to `coding_in_progress`.
- Append:
  - `actor: "Coder"`
  - `requestor: "Planner"`
  - `event: "coding-started"`
  - `details`: implementation started

Invoke Coder with `feature`, spec refs, and no `review_wrapper` for initial pass.
- Include the Coder invocation line from `Role Invocation Templates` verbatim in the prompt.

### Step 9 - Record Coder Result

Determine coding state:
- `coding_complete` when `change_wrapper` indicates no unresolved blockers and required checks were executed.
- `blocked` when tests/checks fail unresolved, wrapper is malformed, or `notes` indicate blockers needing user direction.

Append:
- `actor: "Coder"`
- `requestor`: use requestor from latest coding start event (`"Planner"` for initial, `"Reviewer"` for revision)
- `event: "coding-complete"`
- `change_wrapper`: full wrapper

If blocked:
- You MUST ask user for guidance before proceeding.

### Step 10 - Reviewer Pass

Before invoking Reviewer:
- Set `status` to `code_in_review`.
- Append:
  - `actor: "Reviewer"`
  - `requestor: "Coder"`
  - `event: "code-review-started"`
  - `details`: code review started

Invoke Reviewer with spec refs, latest `change_wrapper`, and prior `review_wrapper` if iterating.
- Include the Reviewer invocation line from `Role Invocation Templates` verbatim in the prompt.

### Step 11 - Process Reviewer Result

Compute `effective_accepted` exactly like Step 5.

Always append review result:
- `actor: "Reviewer"`
- `requestor: "Coder"`
- `event: "code-reviewed"`
- `review_wrapper`: full wrapper

Then branch:
- If `effective_accepted == "true"`:
  - Set `status` to `code_approved`.
  - Present summary and remind user commit/PR actions are manual.
- If `effective_accepted == "conditional"`:
  - Set `status` to `code_conditionally_approved`.
  - Proceed to Step 12.
- If `effective_accepted == "false"`:
  - Set `status` to `code_changes_requested`.
  - Proceed to Step 12.

### Step 12 - Coder Revision Pass

Before re-invoking Coder:
- Set `status` to `coding_in_progress`.
- Append:
  - `actor: "Coder"`
  - `requestor: "Reviewer"`
  - `event: "coding-revision-started"`
  - `details`: revising from Reviewer feedback

Coder revision requirements:
- Resolve all `must_fix`.
- Resolve `should_fix` unless high-risk/scope-expanding, with explicit justification in `notes`.
- Resolve trivial `nit`; justify risky deferrals in `notes`.
- Include the Coder invocation line from `Role Invocation Templates` verbatim in the prompt.

After Coder returns:
- Set `status` to `coding_complete` or `blocked`.
- Append:
  - `actor: "Coder"`
  - `requestor: "Reviewer"`
  - `event: "coding-complete"`
  - `change_wrapper`: full wrapper

If unresolved items are deferred with explicit justification:
- Set `status` to `code_conditionally_approved`.
- Append:
  - `actor: "Orchestrator"`
  - `requestor: "Coder"`
  - `event: "code-approved-with-justifications"`
  - `details`: deferred item summary
- Ask user if deferrals are acceptable.
- If accepted:
  - Set `status` to `code_approved`.
  - Append:
    - `actor: "User"`
    - `requestor: "Coder"`
    - `event: "code-approved-by-user"`
    - `details`: user approved deferred code-review items

### Step 13 - Repeat Code Loop Until Exit

Repeat Steps 10-12 until:
- Code approved, or
- Stuck loop detected.

Stuck loop heuristics:
- Same `must_fix` fingerprints appear for 2 consecutive review cycles with no meaningful code change, or
- More than 3 Reviewer->Coder revision cycles with no status improvement.

When stuck:
- You MUST summarize attempts, unchanged blockers, and latest wrapper signals.
- You MUST ask user for explicit guidance.

## Recovery and Resumption

When resumed, you MUST:
1. Read and validate `task_log.json`.
2. Determine `status` and last history event.
3. Resume from mapped step below.
4. Do not append duplicate `*-started` entries when the last event already represents an in-flight call.

Status/event mapping:
- `spec_in_progress`:
  - last event `spec-creation-started` or `spec-revision-started` -> Step 2
- `spec_created` or `spec_updated` -> Step 4
- `spec_in_review`:
  - last event `spec-review-started` -> Step 4
  - last event `spec-reviewed` -> Step 5
- `spec_conditionally_approved`:
  - last event `spec-reviewed` -> Step 6
  - last event `spec-approved-with-justifications` -> user confirmation path in Step 6
- `spec_changes_requested`:
  - last event `spec-reviewed` -> Step 6
  - last event `user-change-requested` -> Step 2
- `spec_approved` -> Step 8
- `coding_in_progress`:
  - last event `coding-started` -> Step 8
  - last event `coding-revision-started` -> Step 12
- `coding_complete` -> Step 10
- `blocked` -> ask user for direction
- `code_in_review`:
  - last event `code-review-started` -> Step 10
  - last event `code-reviewed` -> Step 11
- `code_conditionally_approved`:
  - last event `code-reviewed` -> Step 12
  - last event `code-approved-with-justifications` -> user confirmation path in Step 12
- `code_changes_requested` -> Step 12
- `code_approved` -> ask user next action
- `implementation_complete` -> workflow complete

## Sub-Agent Error Handling

On role execution failure (Planner/Architect/Coder/Reviewer):
1. Keep status at the current in-progress state.
2. Append history:
   - `actor`: failing role
   - `requestor`: upstream caller in workflow (`User`, `Planner`, `Architect`, `Coder`, or `Reviewer`)
   - `event: "subagent-error"`
   - `details`: failure message + step + attempt count
3. Retry up to 3 total attempts.
4. On retry, pass prior context and state that this is a retry. Require role to avoid duplicate work.
5. If still failing after 3 attempts, you MUST ask user for guidance.

## User Requests Mid-Workflow

If the user requests a behavior change, spec change, or reports an issue at any time after the first Planner pass began (including during Architect review, coding, or code review), you MUST route back through Planner. You MUST NOT apply behavior changes directly in code.

Required procedure:
1. Set `status` to `spec_changes_requested`.
2. Build synthetic `spec_review_wrapper`:
   - `accepted: "false"`
   - `issue_details.must_fix`: requested changes/issues
   - `issue_details.should_fix`: `[]`
   - `issue_details.nit`: `[]`
   - `notes`: user-requested changes
3. Append:
   - `actor: "Orchestrator"`
   - `requestor: "User"`
   - `event: "user-change-requested"`
   - `spec_review_wrapper`: full synthetic wrapper
4. Set `status` to `spec_in_progress`.
5. Append:
   - `actor: "Planner"`
   - `requestor: "User"`
   - `event: "spec-revision-started"`
   - `details`: original user request text
6. Re-enter Planner flow from Step 2.
7. You MUST NOT skip Architect review, even for minor changes.

## Commit Message Mode

If user requests a commit message after approved implementation:
1. Set `status` to `implementation_complete`.
2. Append:
   - `actor: "Orchestrator"`
   - `requestor: "User"`
   - `event: "implementation-complete"`
   - `details`: user requested commit message after approved implementation
3. Build a conventional commit message from final wrappers, `task_log.json`, and relevant repository diffs.
4. Present the commit message in a copyable code block.
5. You MUST NOT run any commit operation.

Commit message requirements:
- You MUST reflect the final state of the implementation, not a chronological troubleshooting log.
- You MUST include main implementation changes, tests, and documentation changes.
- If spec files changed (even if later moved/archived), you MUST include them in the summary.
- You MUST NOT include markdown formatting inside the commit message body.
- You SHOULD use concise bullet points; nested bullets are allowed for major sections.
- You MUST NOT include changed-file counts.
- If tests were added or changed, include a summary of the testing changes and how many were added or changed, 
  - Also include the overall test status as sub-bullet in the test section
  - e.g. "All 1000 tests passing across 100 test files, type-check and lint clear"
  - Ideally also include a summary of the changes to the test suite itself, e.g. "Added 10 new tests across 3 files covering X, Y, Z; updated 5 existing tests to cover new behavior around A and B"
  - This should include the number of changed/added/removed tests and test files

### Commit Message Structure

Use the following structure:

```
<type>(<scope>): <short summary>

- Detailed description of changes made formatted in bullet points:
- Bullet point 1
- Bullet point 2
- (if applicable) Section heading 1
  - Sub-bullet point 1
  - Sub-bullet point 2
  - ...
- (if applicable) Section heading 2
  - Sub-bullet point 1
  - Sub-bullet point 2
  - ...
- ...
- Any breaking changes noted clearly under a "BREAKING CHANGES" section if applicable.
- Any additional notes or references.
```

## Communication Style

After each major phase, provide concise high-signal summaries:
- What changed.
- Current status.
- Open `must_fix` / `should_fix` / `nit` signals.
- What happens next.
