# Proposal: Orchestrator Flow v2.0.0 corrections and contract clarifications

## Problem Statement

The first live test run of the Codex v2 implementation exposed workflow defects, ambiguous output contracts, and agent compliance failures. It also exposed separate problems in the test kit. The workflow changes in this proposal address the former group while keeping test-kit corrections separate.

The original v2 proposal aimed to make rigor proportional to consequences while preserving reliable approvals, explicit configuration, recoverable checkpoints, and independent review. These corrections support that aim. Unnecessary document revisions, repeated reviews, and duplicate artifacts consume time and context without improving the delivered result. Required handoffs and initial review coverage still need to work at every assurance level.

This is a bounded supplement to the [original v2.0.0 proposal](proposal-orchestrator-flow-v2.0.0.md). It supersedes conflicting requirements for the changes it specifies while preserving the rest of that design. It defines corrections to the unfinished v2.0.0 release. The current implementation scope is Codex only; the subsequent scope decision recorded in `AGENTS.md` takes precedence over the original proposal's broader platform rollout.

### Task progress and assurance changes cause unnecessary churn

The current Coder contract instructs the agent to increment the `tasks.md` content version and append Revision History when marking tasks complete. The semantic validator also requires every reported artifact change to advance its version. In the live run, unique-lines task documents advanced from version 1 to 8, and ignore-case advanced to 12, through completion accounting. The agents followed the implemented contract, but that contract does not reflect the user's intended distinction between specification content and task progress.

The assurance override reducer adds every previously reviewed phase to `assurance_gaps` whenever assurance increases. In Standard's ignore-case feature, an accepted Maximum specification review was already recorded at event 15. Assurance decreased at event 16 and increased again at event 32. The increase introduced a specification gap without first establishing that the existing Maximum review had become insufficient. The Maximum code review at event 35 cleared only the code gap, leaving final completion blocked on the specification gap.

The defect can also be isolated with an accepted Maximum specification review followed by Maximum → Standard → Maximum and no intervening artifact changes. Existing evidence needs an applicability assessment; the configuration transition alone is not grounds to repeat the review.

### Scratch artifacts accumulate while required handoffs can still be incomplete

Basic committed thirteen intermediate role-wrapper JSON files alongside its specifications. Those files duplicated wrappers already embedded in the feature task log and came from Planner, Architect, Coder, and Reviewer. Standard's specification directories remained clean. Maximum's specification directory was also clean, but its consumer repository contained an untracked `.orchestrator-test/unique-lines/` directory with wrapper copies, transcripts, a Python probe, fixtures, task-log snapshots, and temporary directories. Some research references depended on scratch files there. Avoiding commits alone does not prevent a repository from becoming a dumping ground.

At the same time, saving a valid wrapper did not ensure a valid return. Maximum's consolidated Planner native return was a pointer/status object instead of the required complete `spec_change_wrapper`; the runner had permitted that relaxation. Standard also had a historical Coder native return that was malformed JSON even though a separately saved wrapper was valid. The later valid Standard completion and review do not make that earlier return well formed, and the available evidence does not establish that every subsequent gate was invalid.

These observations require clearer artifact ownership and handoff rules. They do not justify a new archive of every intermediate output.

### Review coverage and follow-up representations need clearer contracts

Basic's initial Reviewer read was truncated inside a task line. Recovery resumed at the following line, omitting the remainder of the interrupted line, while the wrapper asserted complete coverage. Passing application tests did not establish the mandatory complete-current-body read. This was an agent compliance failure against an existing obligation.

Standalone follow-up reviews exposed another ambiguity: the role instructions require preserving settled decisions, while the standalone semantic validator permits dispositions only for current findings. Several outputs preserved a resolved finding's disposition with no current findings and were rejected or had only schema-level validation. A supported representation must preserve history without making resolved findings appear open.

The blocked-work exercise continued independent work correctly but listed an already completed task in `independent_task_ids`. The validator treats that field as remaining work and rejected the output. This is a reporting ambiguity, not evidence that independent work should have stopped.

Feature-branch naming is also underspecified. The user may supply a branch name at initialization. Otherwise, the intended default is the feature name, which may include a version or may be purely descriptive. Neither a mandatory version nor an automatic platform prefix is desired.

### Checkpoint timing needs concrete workflow boundaries

The existing instruction to checkpoint every completed logical update leaves room for different interpretations of coding granularity. The user requires checkpoints when Planner returns a document for approval, whenever Orchestrator records an authoritative task-log update or transition, when review wrappers return, and when approvals, specification change requests, or other decisions are recorded. Coding must preserve progress after natural groups of related tasks defined by Planner, and at completion. These groups need explicit section headings in the approved plan so Coder does not have to invent the normal checkpoint boundaries during implementation. The user has selected artifact checkpoints published by the producing role, with separate Orchestrator task-log checkpoints. Coder returns its cumulative wrapper only when its implementation or repair assignment is complete; requiring an Orchestrator handoff after every coding checkpoint adds unwanted coordination overhead.

The FEC bot `v2.0.0-mal-provider-independence` branch provides a concrete cadence example. Its completed plan contains 47 numbered tasks, including 17 Red/Green pairs. Coding commits grouped related work, such as tasks 1–5 for provider foundations, 6–7 for bounded response reading, and 26–33 for command/runtime integration. Planner and Coder published their own artifact checkpoints; Orchestrator separately checkpointed task-log updates. The conversation confirms sequential requirements, design, and tasks approval gates. However, the committed log retained only its initial event through the first task-plan draft; formal draft-feedback recording began later at the user's explicit request. Later log checkpoints preserved approvals, review results, and transitions, sometimes as related event pairs. This historical example illustrates cadence and grouping without establishing complete early handoff recording. Its older schema and other implementation conventions are not new requirements.

### Resumption needs recent Git evidence as well as workflow history

An interruption can leave completed files, a local or delivered commit, an unrecorded role return, or a user approval ahead of the last authoritative task-log entry. Looking only at the current workflow state can therefore cause completed work to be repeated or a second writer to be dispatched. Git history provides evidence of preserved changes, while the task log and actual role/user messages establish workflow meaning and authorization. Recovery needs an explicit, bounded inspection of recent commit metadata and changed-file lists. Orchestrator must preserve its context and coordination role: it does not read patches, specification bodies, or product code to reconcile progress. Questions requiring content inspection go to the responsible role. Neither commit messages nor file presence establish approval or completion.

Because intermediate Coder checkpoints do not require wrappers, a resumed Coder must reconstruct cumulative implementation context rather than report only its new work. Its own checkpoint history is a primary source, combined with approved task progress and examination of the actual code. Orchestrator cannot perform that reconstruction by loading the artifacts into its own context.

### Coder context needs proportionate delegation and exceptional phase handoffs

Exploration and verbose test output can crowd out the implementation history Coder needs to integrate changes and produce an accurate completion report. The selected division of work keeps intentional edits with Coder while helpers explore and run tests, returning concise evidence. It does not require a separate coding helper for every task or checkpoint group.

Exceptionally large features may need planned implementation phases with fresh Coder contexts. This is a separate boundary from an ordinary checkpoint group: even FEC bot v2.0.0's 47-task migration likely would not have been split. Intermediate phase reviews need a defined, lighter assurance and capability policy so these rare handoffs do not reproduce full-feature review overhead at every boundary. Final integration and cumulative reporting still need one responsible Coder and a full-feature review at the accepted settings.

## Proposed Solution

Correct the behaviors below in the Codex implementation and its related documentation and development tests. Where this document conflicts with the original proposal or current contracts on these specific points, this document defines the target behavior. Preserve unaffected workflow behavior, including the existing assurance levels, capability controls, user gates, checkpoint recovery, and manual final merge.

### 1. Keep task progress separate from specification content versions

Completion accounting for already approved tasks does not constitute a new specification content version.

- Coder may update task-completion checkboxes during implementation, checkpoint them with the related work, and report cumulative progress and evidence in its completion `change_wrapper`.
- A progress-only update leaves the `tasks.md` content version and Revision History unchanged. It preserves the actual approval basis without inventing approval of a new version.
- The changed task file and related implementation changes still belong in Coder's artifact checkpoint. Orchestrator separately checkpoints authoritative task-log updates when they occur; an intermediate coding checkpoint does not require a new wrapper or log event. No checkpoint is omitted because the specification version stayed the same.
- Substantive task instructions remain Planner-owned. Changes to behavior, scope, dependencies, or executable instructions must follow the applicable specification revision and approval process; they cannot be disguised as progress.
- Requirements, design, and genuine task-content revisions retain their existing independent version and Revision History rules. An unchanged document is not revised to keep versions aligned.

For example, completing task 3 in an approved `tasks.md` at content version 1 leaves it at version 1 with the same history. Its checkbox changes and is included in Coder's next artifact checkpoint; the eventual completion wrapper includes that progress even if a different Coder context finishes the assignment. A subsequent substantive Planner revision advances the content version normally.

Align wrapper semantics, replay, document validation, examples, and test fixtures with this distinction. Planning may choose the smallest consistent representation using the existing progress and artifact-change fields; it must not leave the unconditional version-increment rule in conflict with the new behavior. Preserve validation of every actual numbered checkbox at consolidated coding completion.

### 2. Require assurance catch-up only for an actual evidence gap

When assurance changes, assess whether prior accepted review evidence meets the current assurance and still applies to the relevant specification or implementation. Consider the reviewed scope and applicable changes, not just the direction of the assurance transition. Do not repeat completed work solely because the configuration changed.

| Situation | Required behavior |
| --- | --- |
| Accepted Maximum specification review, then Standard, then Maximum; relevant specification remains unchanged | Retain the sufficient review without introducing a new specification gap. |
| Existing Standard review, followed by a requirement for Maximum | Identify the missing assurance and require the applicable catch-up before dependent work. |
| Review begins at Standard and returns after the feature changes to Maximum | Record its actual Standard invocation basis and result; require sufficient catch-up where the result does not meet the current requirement. |
| Prior review had sufficient assurance, but relevant work or assumptions have changed | Determine whether that evidence remains applicable and require the necessary review of changed work. An assurance label alone does not establish coverage. |

Apply the principle to both specification and implementation evidence. A gap in one phase must not imply a gap in the other. Preserve phase/resume behavior and the actual recorded invocation configuration. Never relabel an old review as having run at a different assurance.

For the exceptional implementation phases in section 12, assess evidence against the review stage's required assurance and scope. A correctly configured lower-assurance intermediate review is neither a whole-feature approval nor, solely because its level is lower, an assurance gap blocking the next phase. The final whole-feature review remains required at the feature assurance.

This correction concerns whether another review is required. Every review that is required at Maximum still performs the full applicable review and active revalidation prescribed by the existing contract. Lower-assurance follow-ups retain their impact-based scope. Existing approval, disposition, and final-acceptance gates remain effective.

Derive the result from authoritative history and the applicable review evidence. A separate review registry, duplicate workflow status, or new user decision solely to preserve already sufficient evidence is not a requirement of this change.

### 3. Default to no temporary role artifacts

Apply one artifact-lifecycle rule to Orchestrator, Planner, Architect, Coder, Reviewer, and their helpers, at every assurance level.

The normal workflow creates no temporary role artifacts. Roles return their required structured output directly at the applicable handoffs, and Orchestrator records that output in the authoritative task-log event, with useful findings and rationale in the appropriate durable documents. In almost all cases, no intermediate file should exist. Do not routinely create files such as `planner-design-output.json`, `coder-task-3-output.json`, or `reviewer-output.json`, even if they would be deleted afterward.

Temporary files are permitted only when absolutely necessary because of a concrete tool or recovery constraint. Convenience, habit, or a routine save-then-read validation pattern is insufficient. Make ordinary validation and handoff paths work without intermediate files; existing helper interfaces must not turn an exceptional necessity into the default.

When an unavoidable temporary file is needed:

- Keep it out of staged and committed feature content. Merely relocating scratch files into another consumer-repository directory is insufficient.
- Preserve it while validation, recording, or recovery still needs it. Do not delete the only recoverable output after an interrupted or failed handoff.
- Remove the workflow-owned temporary copy once its useful content has been validated and durably recorded. Cleanup must not destroy unrelated user files or required recovery evidence.
- Retain useful empirical findings in the task log, optional research, or another intended project artifact as appropriate. Durable documents must not depend on temporary file paths that disappear during normal cleanup.

The same rule covers ad hoc probe scripts, scratch fixtures, copied task logs, handoff transcripts, and temporary text or JSONL files. It does not prohibit legitimate project source, planned tests and fixtures, required documentation, or intentional durable evidence. It also does not remove the checkpoint helper's required journal under Git metadata; that journal has a defined recovery purpose and is not a role-wrapper archive.

Keep an unavoidable exception as small and short-lived as its actual constraint permits. Do not introduce a routine temporary-file convention, exported package, artifact service, permanent scratch archive, or additional approval gate. This policy governs future workflow output; it does not authorize cleaning up the preserved first test run.

### 4. Accept only the required complete role handoff

At a required completion or approval/review handoff, orchestrated roles must return the complete JSON wrapper required by their role contract. A path, pointer, status object, or prose summary is not a substitute, even when a valid file exists elsewhere. A temporary validation file does not replace the required return.

Before treating a return as a successful handoff, Orchestrator validates the actual output's structure, semantics, invocation/configuration context, references, and applicable approval basis. A malformed or incomplete return must not authorize dependent review, coding, or completion. Follow the existing invocation/output recovery process and obtain the corrected output from its owning role; do not reconstruct missing producer content or decisions.

Planner retains incremental wrappers at its required draft/revision handoffs and approval gates. Its consolidated output must express the full current specification state, decisions, rationale, and dispositions needed by Architect, rather than only the latest delta or the conversation chronology. In the normal single-assignment path, Coder returns one full cumulative `change_wrapper` when its implementation or assigned repair pass is complete. It need not return an interim wrapper for a checkpoint, interruption, resumption, or context replacement. Each completed repair pass still returns the cumulative implementation scope and evidence needed for the ensuing review, including applicable work from prior contexts and passes. Section 12 defines the exceptional phase-completion handoff and final Coder consolidation; it does not add wrappers at ordinary checkpoints.

Coder must promptly communicate blockers, failures, contradictions, and requests needing Orchestrator or user action. Such in-progress coordination is not a completion handoff and does not require a full cumulative wrapper or authorize `coding-complete`. Align invocation handling with that distinction instead of treating a necessary interruption report as a malformed completion return. Required completion wrappers remain complete and validated; the historical malformed intermediate Coder return was a failure under the earlier contract, not a reason to preserve mandatory interim wrappers.

Formatting recovery does not by itself establish a new product defect or require repeating completed product work. Retain completed work and the real invocation history while recovering the required output under existing retry and authorization rules. Preserve standalone role response conventions, including a readable summary where permitted; this correction does not force all direct role use into the orchestrated JSON-only presentation.

### 5. Recover truncated reads without losing required coverage

Initial Architect and Reviewer coverage remains comprehensive at every assurance level: the current bodies of all three specification documents must be available, together with the relevant source or implementation context required by the role. Assurance controls scrutiny and follow-up scope, not permission to omit part of an initial specification read.

Use the existing current-body reader and suitably bounded output. If a tool truncates content, recover the missing portion before claiming complete coverage. If the interruption occurs inside a line, reread that line or an overlapping range; advancing to the next line is not sufficient. The agent must not infer unread content from a summary or from passing tests.

Continue excluding the final Revision History section from routine context. Retrieving the full file and only then ignoring history does not meet the context-efficiency objective. Preserve the reader's treatment of headings inside fenced code blocks.

Planning may improve the reader interface if necessary to make bounded retrieval reliable. The required outcome is complete relevant content with no skipped boundaries, not a new persisted read-audit artifact or a larger review checklist. Required Maximum passes and appropriately scoped lower-assurance follow-ups retain their existing obligations.

### 6. Distinguish current dispositions from resolved historical decisions

Make the follow-up contract consistent for Architect and Reviewer, both orchestrated and standalone.

- Preserve stable finding identities, actual prior decisions, their authority, and relevant rationale.
- Identify resolved findings without silently dropping unresolved ones or reopening settled decisions without new grounds.
- Distinguish a repaired finding from an unresolved finding with an accepted limitation. Acceptance and `known-issues.md` must continue to reflect that distinction.
- Permit a valid follow-up with no current findings to retain the relevant history of its resolved findings and prior decisions.
- Standalone output must not invent task-log events or authority references. Orchestrated output must retain its real history and authority checks.

The recommended representation uses existing `resolved_findings` and notes/source references for resolved history, with current `dispositions` associated with current findings. This is a design recommendation, not a requirement to introduce a new schema field or replace the existing finding model. Planning must make the chosen representation explicit and align instructions, examples, and semantic validation.

For example, a follow-up that confirms a repaired standalone finding may have empty current findings, record the resolved identity, and preserve the earlier decision and evidence in supported historical context. It should validate without pretending the finding is still open. An unresolved issue without an allowed disposition must continue to block or condition acceptance as prescribed by assurance.

### 7. Report completed independent work separately from remaining work

Clarify that a blocker's `independent_task_ids` lists independent tasks that remain `pending` or `in_progress` at the time of the returned wrapper. Completed tasks remain represented in `task_progress` and their results/evidence; they are not available remaining work.

Preserve the existing checks that referenced task IDs exist, that blocked tasks are not also classified as independent, and that reported progress is internally consistent. Provide an example containing both completed independent work and another independent task still available to continue.

Only work dependent on an ordinary blocked operation pauses. Other approved independent work may continue. If no independent work remains, report that accurately rather than retaining completed IDs to keep the workflow in progress. This clarification does not authorize retries, model substitutions, or continuation past other existing gates. In particular, the established failed-checkpoint-push pause and bounded recovery rules remain unchanged.

### 8. Default the branch name to the feature name

Resolve the branch name once at initialization:

1. Use the branch name explicitly supplied by the user, when present.
2. Otherwise, use the feature name. This is the name used for the feature's specification directory, not its full path.

The feature name can include a release version and descriptive name or only a descriptive name. Do not add a version, a `codex/` prefix, or any other prefix automatically. Do not ask for a target release version solely to construct a branch name, and do not derive a product version from the workflow's `VERSION`.

| Feature name | Explicit branch name | Resolved branch |
| --- | --- | --- |
| `v2.0.0-mail-migration` | Not supplied | `v2.0.0-mail-migration` |
| `mail-migration` | Not supplied | `mail-migration` |
| `mail-migration` | `v2.1.0-provider-migration` | `v2.1.0-provider-migration` |
| `v2.0.0-mail-migration` | `provider-migration` | `provider-migration` |

Record the resolved name in the existing `branch_context.feature_branch` and initialization context, and reuse it on resume. An explicit branch name does not rename the feature or its directory. Normal Git name validity and existing-branch/baseline handling still apply; the default does not authorize overwriting an unrelated branch or silently inventing a different name.

This naming rule does not change the explicit integration target, baseline, remote, or user-owned final merge. Checkpoint cadence is clarified separately below. No new branch-naming configuration field or override event is required by this proposal.

### 9. Publish checkpoints through the role that owns the work

A checkpoint is a commit and push to the recorded feature branch. The role producing the work publishes its own artifacts: Planner checkpoints specification/research changes, Coder checkpoints implementation/tests/documentation and task-completion progress, and Orchestrator checkpoints the task log and its other owned artifacts. Related artifact and task-log changes need not share a commit. Apply this requirement at every assurance level, using coherent work boundaries rather than a timer, file count, or individual filesystem write.

Orchestrator retains branch initialization, user interaction, authoritative task-log writes, and recovery coordination. Planner and Coder do not write the task log. Architect and Reviewer retain their read-only artifact contracts and return review results for Orchestrator to record. Coder's helpers explore and run tests; Coder owns intentional edits, integration, and artifact checkpoints as specified in section 11.

| Boundary | Required checkpoint |
| --- | --- |
| Workflow initialization or recorded phase transition | Orchestrator checkpoints the authoritative log update before proceeding with the work it enables. |
| Planner returns a document draft or revision for approval | Planner commits and pushes its changed artifacts before returning the actual wrapper. Orchestrator then records and checkpoints the wrapper before requesting approval. This applies separately to requirements, design, tasks, and returned revisions. |
| User approval, substantive request, specification change request, disposition, or configuration override is recorded | Orchestrator checkpoints the decision and its related owned artifacts before dependent work. An event that leaves the major workflow phase unchanged still requires its checkpoint. |
| Architect or Reviewer returns a review wrapper | Orchestrator records and checkpoints the actual result before proceeding to the resulting revision, coding, approval, or completion action. |
| Coder completes a planned group or preserves an earlier coherent partial update | Coder commits and pushes related implementation, tests, documentation, and task progress. It continues authorized work after successful delivery without an interim wrapper, new log event, or Orchestrator acknowledgement solely for that checkpoint. |
| Coder finishes whole-feature implementation or a final-review repair pass | Coder publishes the remaining artifacts and returns the full cumulative completion wrapper. Orchestrator validates, records, and checkpoints that handoff before code review. |
| Coder finishes a nonfinal implementation phase in an approved phased plan | Coder publishes its artifacts and returns the complete phase-scoped wrapper defined in section 12. Orchestrator validates, records, and checkpoints it before the intermediate review or next phase. Review results and resulting transitions follow the same log-checkpoint rule. |
| Completed research, known-issue, or verification update | The owning role checkpoints changed durable artifacts, with directly related work where appropriate. Orchestrator checkpoints any actual resulting log update. Coder verification remains part of its completion report; this row adds no interim Coder wrapper or separate research approval gate. |
| Explicit final feature acceptance | Orchestrator checkpoints the completion record and establishes its delivery before producing the final squash message. |

Every completed authoritative update to `task_log.json` triggers an Orchestrator checkpoint. Do not postpone an already recorded transition until a later coding milestone. A single logical update may record several directly related events together, such as a review result and the next phase's start, and commit them in one checkpoint before dispatching the next role. This does not permit batching separate approval gates, user requests, or completed handoffs merely to reduce commits. Conversely, an artifact-only checkpoint does not require a new log event. Read-only inspection and progress polling do not create checkpoint obligations by themselves.

At each Planner document gate, Planner first publishes its artifacts and returns its wrapper, then pauses. Orchestrator records and checkpoints the actual returned wrapper before requesting approval. It records and checkpoints the user's approval before authorizing the next document: requirements before design, design before tasks, and tasks before the required Architect review. Preserve these individual records during initial drafting as well as revisions; do not wait for all three documents to be approved before recording the early handoffs and approvals.

#### Planner-defined coding groups

Planner organizes the numbered tasks into natural implementation groups using proper Markdown subheadings within the task list. Use `###` for groups directly under the task-list section, or `####` for narrower groups within a broader `###` area when useful. Make each group's intended outcome and boundaries clear through its heading and task descriptions. A broad heading such as provider integration may contain several coherent groups; it must not become a reason to defer all checkpoints until that entire area is complete.

Choose groups by related behavior, dependencies, and a useful implementation outcome, not by a fixed task count or an agent quota. Keep sequential whole-number task IDs, requirement coverage, and existing task-category rules. Related Red/Green tasks can belong to one group while retaining their separate execution order and required failure/passing evidence. Do not add fake numbered checkpoint tasks, per-group workflow states, or separate group-approval gates.

Coder uses these approved groups as its normal artifact-checkpoint boundaries, commits and pushes its own work, and continues the approved task sequence without returning a wrapper after each group. Earlier coherent partial checkpoints remain available when an interruption, blocker, or meaningful partial update requires preserving progress. They must describe unfinished or deliberately Red work accurately. A substantive change to approved task content or dependencies still follows the existing Planner revision process.

Coder returns its cumulative wrapper at implementation/repair completion, or the explicitly planned phase boundary in section 12, while communicating required decisions and problems promptly through Orchestrator as described in section 4. Keep the same native Coder context across checkpoints where supported. Neither a new checkpoint nor a resumed context starts a new coding scope or resets cumulative reporting.

Use meaningful checkpoint messages that identify the work and task progress, relevant verification results, and unresolved limitations. Together with the changes themselves, these messages must support later reconstruction without requiring interim wrapper files or a separate progress journal. The full wrapper at completion still carries the required cumulative report.

Coordinate Git operations in the shared checkout so publishing roles do not race over the index, commit, or push. Stage only owned changes and preserve unrelated staged or unstaged work. This coordination does not require returning every Coder checkpoint to Orchestrator or giving Orchestrator access to specification/code bodies.

Checkpoints preserve accurately described progress, including incomplete or deliberately Red work. Verification remains what the task and assurance require; creating a checkpoint does not independently require a fresh agent, a full project reread, another complete test suite, an additional user approval, or an extra review cycle. Preserve all existing required gates and checks.

Apply the existing commit-failure, failed-push, uncertain-attempt, and bounded recovery rules to every publishing role. The role preserves and reports a failed or uncertain attempt; Orchestrator handles user direction, authoritative recovery records, and coordination. In particular, a failed push pauses workflow work; recovery does not create success receipts or automatic extra push attempts. Adapt checkpoint helpers and metadata to recognize artifact-only checkpoints without inventing task-log events or assigning them duplicate event ranges. Preserve meaningful event-range correspondence for commits that actually update the log. This ownership change does not authorize changes to the integration branch or the user's final merge.

### 10. Inspect recent Git checkpoints when resuming or recovering

#### Orchestrator recovery uses metadata and authoritative workflow records

Before resuming dependent workflow work after an interruption or in a fresh context, Orchestrator must inspect recent Git history alongside the authoritative task log. This is a recovery obligation at every assurance level, not a recurring full-history audit at every normal handoff.

Orchestrator's Git inspection is limited to commit metadata/messages, checkpoint references and delivery evidence, and changed-file names/statuses. It must not open Git patches/diffs or read specification, research, source, or test-file bodies. This preserves its coordination contract and context budget during recovery; uncertainty and higher assurance do not create an exception. Existing validators may mechanically inspect artifacts and return concise validation results or diagnostics, without loading those artifacts into Orchestrator's context.

1. Confirm the current checkout, recorded feature branch and baseline, and the names/statuses of staged, unstaged, and untracked files, without opening their contents or diffs. Preserve unrelated work and investigate a branch mismatch before mutation. Validate the supported task log and derive its current phase, approvals, configuration, and next permitted action using the existing read-only helpers.
2. Inspect the current HEAD and a small window of preceding commits. Read their messages, changed-file lists, and applicable checkpoint metadata only. Include artifact-only commits as well as task-log commits. Filtering only for commits touching `task_log.json` would miss preserved work.
3. Extend the metadata inspection backward when the latest few commits do not account for the relevant work since the last reconciled handoff or checkpoint. A recent-commit window is an initial reading batch, not a hard recovery limit. Stop when the relevant history is accounted for; do not load unrelated repository history or expand into file-content inspection.
4. Reconcile commit metadata and working-tree file lists with task-log events, reported artifact versions/task progress, actual native role outputs and liveness, concise validator results, and any actual user decisions received before interruption. Check existing push-attempt and delivery evidence under the recovery protocol. A local commit alone does not establish successful delivery, and a completed commit does not establish that its producer has stopped writing.
5. Recover completed output or continue the existing role context before launching a replacement writer. Finish any interrupted recording or delivery step under its existing authority, then derive the resume action from the reconciled evidence. Preserve applicable completed work and checks; resumption alone is not a reason to repeat them.

When metadata and available handoffs leave a content question unresolved, direct a bounded check to the responsible role: Planner for specification content, Coder for implementation progress, and Architect/Reviewer for questions within an applicable review. That role may inspect the relevant files or diffs and communicate a concise finding with references. A required completion/gate handoff still uses its complete wrapper; a Coder recovery question does not impose an interim completion wrapper. Do not ask the role to relay raw files, patches, or exploration transcripts into Orchestrator's context. Prefer the existing role context where available; a recovery question does not itself require a new full review or fresh investigation of settled work.

The resulting behavior must distinguish these cases:

| Recovered evidence | Required action |
| --- | --- |
| Document checkpoint and valid role return exist; return is not recorded in the log | Recover and validate the actual return, then record and checkpoint the handoff. If the required return is missing or malformed, obtain it from the owning role through existing recovery rules; do not manufacture it from a commit message. |
| Document handoff is recorded; approval is pending | Present the existing document's link and Planner's returned summary for approval without reading its body. Do not begin the next document. |
| Actual user approval exists but was not recorded | Recover its statement, scope, and applicable artifact version from the original user evidence, then record and checkpoint it before dependent work. Do not ask for the same approval again when that evidence is clear. |
| Applicable approval is already recorded and delivered | Continue the authorized next stage without reopening the approval or regenerating the approved document. |
| Implementation checkpoints exist but Coder has not completed its assignment | Absence of an interim wrapper is expected. Preserve the identified work and resume Coder to reconstruct cumulative context from its checkpoints, task progress, and actual implementation, then continue remaining work. Orchestrator does not inspect code or task bodies itself or demand a wrapper merely to resume. |
| Completed Coder assignment has a valid wrapper that was not recorded | Recover and validate the actual cumulative wrapper, then record and checkpoint it. If it is unavailable or incomplete, have Coder reconstruct the complete result before proceeding to review; do not substitute a report covering only work after resumption. |
| Local checkpoint exists but delivery failed or remains uncertain | Follow the existing failed-push or uncertain-attempt process. Inspection does not authorize another push or replenish a consumed attempt. |

Git evidence cannot invent an approval, a role wrapper, or a workflow transition. Where missing or conflicting evidence prevents a reliable next action, explain the specific gap and seek only the direction needed under the existing recovery rules. Retain existing pause scopes, including the global pause for failed checkpoint delivery.

Use existing history, Git evidence, and native invocation context. Do not add document status/hash fields, a parallel recovery-state registry, routine scratch snapshots, or a new event merely to say that recent commits were inspected. Read-only reconciliation does not itself require a checkpoint. Publishing roles retain the checkpoint ownership defined in section 9.

#### Coder reconstructs cumulative implementation context before continuing

On resumption partway through implementation or a repair pass, Coder must reconstruct the information needed for its eventual full `change_wrapper`, including work performed before interruption or by an earlier Coder context. Reuse available native context and prior results, but do not assume the task log contains an interim wrapper for every checkpoint.

Use these sources together:

- **Coder's own Git checkpoints are a primary recovery source.** Inspect their sequence, messages, changed paths, and relevant diffs against the recorded implementation baseline. Trace earlier checkpoints as needed to recover the assignment's cumulative work; the latest commit or the commits since resumption are not the complete scope. Checkpoint purpose, affected paths, and invocation evidence identify relevant work; a shared Git author identity alone does not distinguish roles.
- **The approved `tasks.md` and its progress markers identify intended and reported work.** Reconcile them with the checkpoints and implementation. Preserve actual completed tasks, identify unfinished or partial tasks, and keep the approved dependencies and task-category rules.
- **Explore the actual code and relevant tests to establish what is present.** Account for committed and uncommitted work, later amendments or reversals, and integration between earlier changes. Coder may read the relevant specifications, code, and diffs for this purpose; Orchestrator's metadata-only boundary does not apply to Coder.
- **Recover applicable verification evidence, decisions, dispositions, and remaining obligations.** Use available prior role outputs and checkpoint evidence. Distinguish recovered historical results from checks performed after resumption. Do not invent an earlier test run or success from a checkbox or commit subject; resolve material evidence gaps with proportionate checks under the selected assurance.

Continue from the actual remaining work. Context loss does not itself require repeating completed implementation, restarting all tests, reopening settled decisions, or recreating past Red states. Preserve required assurance checks and repeat affected or insufficient verification where needed.

When the assignment is complete, return one cumulative wrapper covering the entire implementation relative to its recorded baseline, including earlier work, later work, relevant verification and limitations, task completion, and current dispositions. A completed repair pass likewise preserves the cumulative feature report while identifying the repair. The resumption point must not become a new reporting baseline. Orchestrator validates and records that actual Coder output; it does not reconstruct implementation content itself. Do not create interim wrapper files or another persistent recovery artifact to implement this requirement.

For a nonfinal phase assignment under section 12, apply this recovery rule to the complete assigned phase, including its pre-interruption work and dependencies on earlier phases. A resumed phase does not begin a new phase or reset its repair allowance. The final Coder additionally reconstructs and reports the cumulative whole feature against the original feature baseline.

### 11. Keep edits with Coder and delegate exploration and test execution

Coder makes the implementation, test, documentation, and task-progress edits assigned to its role, integrates the result, and publishes its artifact checkpoints. Its helpers are limited to exploration and test execution; they do not make intentional project edits or take over an implementation group. Delegating bounded code or test edits can be reconsidered in a future change, but is not permitted by this contract.

Use exploration helpers for bounded questions about relevant code, interfaces, dependencies, and existing behavior. They return concise findings with enough source context, uncertainty, and limitations for Coder to make implementation decisions. Coder retains the coding history and responsibility for inspecting decision-critical evidence at the feature assurance. Do not require a new exploration round or helper for every task, group, or checkpoint.

Coder's test runs are executed by helpers using the accepted helper capability. Coder remains responsible for implementation and test changes, interpreting results, repairing failures, and the final cumulative report. A test runner does not become another implementation or review role.

Give the helper the exact intended command or test selection and the expected purpose, including an expected Red failure where applicable. Reuse an appropriate helper across related runs rather than spawning a new agent for every command, task, or checkpoint. Keep the tested work stable during a run so returned results apply to the code Coder is evaluating.

Return concise, concrete evidence: what actually ran, its exit/result status, available pass/fail/skip counts, and any failure or limitation. On failure, return the failing test identity and relevant assertion/error details needed to diagnose it, distinguishing a behavioral failure from collection, setup, timeout, or environment failure. An expected Red failure must be identified accurately; it is not interchangeable with an unrelated command failure. Do not return the entire passing-test listing or raw execution transcript, and do not reduce the result to an unsupported assertion that everything passed.

Helpers may use concise runner output and bounded failure details to limit their own context as well as Coder's. They do not fix code/tests, weaken checks, change the selected capability, or expand authorized external operations. Existing authorization, assurance, and task-category rules continue to apply. Use normal tool results and concise reports without creating routine result files or another evidence archive. Coder includes the relevant results in meaningful checkpoints and its completion wrapper so resumption can recover the evidence.

This division of work applies to Coder and its helpers. It does not remove independent Architect/Reviewer verification or change the other main roles' artifact ownership.

### 12. Use implementation phases only for exceptionally large features

The normal path remains one Coder assignment across natural checkpoint groups, with exploration/test helpers and ordinary resumption as needed. Even FEC bot v2.0.0's 47-task implementation likely would not have been split. Task count, section headings, multiple checkpoints, or Standard/Maximum assurance alone do not justify phases. The earlier suggestion of approximately 50 tasks is not a hard phase-size limit or a splitting threshold.

For an exceptionally large feature, Planner proposes coherent implementation phases in `tasks.md`, each containing several checkpoint groups and clear outcomes, dependencies, and completion boundaries. Approve these through the existing tasks-document gate. Preserve the complete requirements/design/tasks specification and normal Architect review; do not introduce separate specification sets or task logs for each implementation phase.

#### Phase completion and review

At a nonfinal phase boundary, Coder publishes its artifacts and returns a complete phase-scoped change wrapper. It covers the entire assigned phase, including resumed work, verification, current findings/dispositions, and relevant integration with earlier phases. Orchestrator validates, records, and checkpoints the actual output. A phase result must not assert that all feature tasks are complete or establish whole-feature `coding-complete`, `code_approved`, or final acceptance.

Use this fixed review policy for nonfinal phases:

| Feature assurance | Intermediate phase review | Final whole-feature review and its repair reviews |
| --- | --- | --- |
| Basic | None; proceed to the next Coder after recording and delivering the phase result | Basic |
| Standard | Basic | Standard |
| Maximum | Standard | Maximum |

An intermediate Reviewer examines the complete delivered phase and relevant dependencies against the governing specification. Intentional future-phase work is not an omission in that phase. Resolve findings that block readiness to continue with the original phase Coder before starting the next phase in a fresh Coder context. Retain remaining findings and their actual dispositions for later work and final review; permission to proceed does not itself waive an issue under the final acceptance standard. Preserve existing valid user decisions and their revisit conditions.

Keep the feature assurance unchanged. Intermediate reviews are explicitly scoped stages with their own required review rigor, not assurance overrides or substitutes for final acceptance. Planner, Architect, and Coder retain the feature assurance. Maximum's comprehensive obligations remain in force for the Architect and final whole-feature review cycle. Do not add an intermediate review after the last phase immediately before the final review.

#### Intermediate Reviewer capability

Keep the accepted Reviewer model and derive the intermediate reasoning effort from the accepted full Reviewer assignment:

| Full Reviewer reasoning | Intermediate Reviewer reasoning |
| --- | --- |
| Max (`max`) | High (`high`) |
| Extra high (`xhigh`) | Medium (`medium`) |
| High (`high`) | Low (`low`) |

Present and record the resolved phase assignment with the feature's accepted capability configuration when phases apply, and reuse it on resume. Applying the recorded stage assignment is not a new capability override on every handoff. Final review and its repairs use the full accepted Reviewer assignment. Preserve actual invocation settings and the existing rules for explicit later overrides, native capability enforcement, and unavailable settings.

The observation that High is likely the lowest normal full Reviewer setting does not establish a new schema minimum. If a full Reviewer setting has no defined mapping or the platform cannot honor the derived setting, resolve the phase assignment explicitly through the existing configuration/limitation process. Do not invent an additional mapping, silently substitute a model, or assume a prompt changes native reasoning controls.

#### Repair allowances and final Coder ownership

Each intermediate phase review has its own repair allowance, and the final review has a separate allowance:

| Feature assurance | Repair cycles allowed per intermediate phase review before additional user direction | Final-review allowance |
| --- | --- | --- |
| Basic | Not applicable; no intermediate review | One repair cycle under the existing Basic policy |
| Standard | One | Two repair cycles under the existing Standard policy |
| Maximum | Two | Existing Maximum rigorous loop and stall safeguards; no new fixed cap |

These intermediate allowances use the lower review assurance's existing limits; do not subtract another cycle. Count a cycle only after a producer repair and its completed re-review. Preserve counts across interruptions, replacements, and capability changes; returning to an unresolved phase is not a fresh allowance. Initial reviews, invocation retries, and ordinary checkpoints do not count. Existing stall detection, explicit continuation, disposition authority, and truthful progress rules still apply. If another repair is needed beyond the allowance, obtain user direction before starting it; acceptance within the allowance does not create an unnecessary pause.

The last Coder owns final integration and consolidation. Use prior phase wrappers, task progress, checkpoint history, actual resulting code, and relevant verification to produce one full-feature cumulative `change_wrapper` against the original feature baseline. Account for later amendments or reversals rather than concatenating stale phase reports. Include current unresolved findings and dispositions and distinguish recovered evidence from newly run checks.

That Coder also owns repairs from the final Reviewer, including changes spanning earlier phases, and returns the updated cumulative wrapper after each completed repair pass. Earlier role context may supply information but does not transfer edit ownership to helpers or make Orchestrator assemble implementation content. Final review covers the whole feature and interactions across phases at the full accepted settings; earlier phase acceptance does not exempt work from that review. Complete all required final tasks and preserve explicit user acceptance and the user-owned merge.

Planning must define the minimal phase representation in wrappers, task-log history, validation, replay, and resume actions. Distinguish implementation phases from the existing specification/implementation workflow stages, preserve ordinary single-assignment behavior, and retain artifact/log checkpoint ownership and bounded recovery. Phase wrappers belong in the task log, not separate scratch files or another progress archive.

### 13. Align documentation and verify the affected behavior

Update the affected Codex entry and role instructions, shared protocol, schema descriptions, wrapper examples, runtime validation/replay/document helpers, and repository documentation together. Change only the files relevant to these corrections. Keep development tests under `tests/` and runtime helpers inside the Codex skill.

Keep this proposal discoverable through direct links from the original proposal and repository documentation. Retain the original proposal as the broader design baseline and make the precedence of these corrections clear. README and test guidance should describe corrected behavior where they currently promise or demonstrate the old behavior. Test-kit runbooks, scenarios, sample proposals, and operator prompts are a separate work item.

Use proportionate verification with actual behavioral assertions:

| Area | Required evidence |
| --- | --- |
| Task progress | Progress-only checkbox changes validate without version/history changes and retain approval. Completion still checks real tasks. Substantive revisions still follow their version and approval rules. |
| Assurance | Maximum → Standard → Maximum with applicable unchanged evidence needs no redundant review. Insufficient or stale evidence still requires catch-up. In-flight reviews preserve their original basis and are compared with the current requirement. Cover specification and implementation evidence and relevant resume actions; intermediate phase reviews are compared with their declared stage requirements. |
| Handoffs | Complete valid wrappers are accepted; malformed JSON, pointer/status-only output, and invalid authority/context cannot establish a successful completion/gate handoff. Intermediate Coder checkpoints and necessary coordination messages do not require a cumulative wrapper or establish completion. Recovery preserves completed work and existing authorization limits. |
| Temporary artifacts | Ordinary validation and handoffs create no intermediate files. Unavoidable exceptions follow the defined lifecycle, preserve recoverable output on failure, and leave no committed duplicates or dangling durable references. |
| Current-body reads | Any changed retrieval helper preserves the complete body across bounded reads, including an interrupted-line boundary, and excludes routine Revision History correctly. |
| Findings | Resolved historical context is representable in valid standalone and orchestrated follow-ups. Current unresolved findings still require valid dispositions; no fictitious authority is accepted. |
| Blockers | Completed independent work is reported as completed, remaining independent work can proceed, and dependent work remains blocked. |
| Branch names | Both optional-version forms work; explicit selection takes precedence over the feature-name default, and resume retains the recorded branch. |
| Checkpoints | Planner/Coder publish their owned artifacts; Orchestrator separately checkpoints actual log updates and owned artifacts. Planner publishes each returned draft before its wrapper is recorded and approval requested; each approval is recorded and delivered before the next document. Coder checkpoints natural groups and accurate earlier partial work without interim wrappers, fake log events, duplicate event ranges, or unnecessary return/resume cycles. Completion wrappers and review results are recorded and delivered before dependent review/work. |
| Recovery | Orchestrator inspects commit metadata and file lists without reading patches or spec/code bodies; content questions go to the responsible role and return concise findings. Reconcile artifact-only commits, unrecorded actual returns/approvals, and uncommitted work without duplicate writers or repeated completed work. A checkpoint outside the initial recent-commit window is found when relevant. Pending approvals remain gates; misleading commit subjects do not grant authority; failed or uncertain delivery by any publishing role retains its bounded recovery rules. |
| Coder continuity | Interrupt after multiple implementation checkpoints with no interim wrappers. On resume, Coder uses its Git history, task progress, actual code, and available evidence to continue remaining work and produce a cumulative completion wrapper that includes pre-interruption changes. Verification claims distinguish recovered evidence from new checks; neither context replacement nor a repair pass resets the feature reporting baseline. |
| Coder helpers | Exploration and test helpers use the accepted capability and return bounded evidence without making intentional project edits. Test reports apply to the intended code and command and preserve expected Red failures, actual failures, skipped/unavailable checks, and relevant error details without passing raw logs to Coder. |
| Exceptional phases | An ordinary feature retains the single-assignment path. An approved phased plan uses scoped completion wrappers, fresh subsequent Coder contexts, the fixed intermediate assurance/reasoning mappings, and separate repair allowances without implying whole-feature approval or resetting unresolved cycles. Final Coder consolidation and repairs cover all phases against the original feature baseline; final review uses full settings and does not exempt earlier work. Resume preserves the pending phase/review, real capability assignment, delivery evidence, and remaining allowance. |

Extend existing fixtures and focused tests where they demonstrate changed behavior. Do not add tests that merely search for instruction wording and present them as proof of agent compliance. Validator tests cannot prove that a native agent returned the actual wrapper, read every required line, or selected only intended files for a commit. Clearly report those limits; native observation belongs to a separately authorized live test run.

Run the applicable artifact validators and repository test suite after implementation, including relevant valid and invalid cases, and `git diff --check`. Report environmental skips accurately. Preserve existing resource-link, checkpoint-recovery, append-only history, and approval guarantees without broadening this work into a new test framework.

### 14. Non-goals and preservation boundaries

- Changes to the test kit, including its proposal matrix, baseline setup, proposal placement, controller records, evidence directory layout, capability scenarios, and thread creation/reuse instructions.
- A workflow restriction of one feature per chat. The user will enforce that convention personally, and the test kit will enforce it for its own runs; it is not a new runtime rule.
- Changes to Claude Code, GitHub Copilot, or Cursor integrations, shared adapters, or a new distribution/export mechanism. Preserve their committed native implementations and the current symlink-based Codex installation.
- A new assurance hierarchy, arbitrary per-role assurance, model fallback, weakened Maximum Architect/final-review obligations, extra user approval gates, or an unrelated state-machine redesign. The scoped phase extension in section 12 is intentional and must be implemented consistently without broadening the ordinary path.
- Updating, migrating, repairing, cleaning, or reinterpreting the preserved `testrun-1` repositories and histories as though they were produced by the corrected workflow. They remain development evidence.
- A v2.0.1 release or migration machinery for this unreleased development iteration. Keep the workflow version at `2.0.0`; retain the established compatibility policy for future released minor and patch updates.
- Automatically starting live tests, messaging other chats, installing dependencies in consumer projects, or modifying machine-local installations. Repository maintenance does not itself activate the consumer workflow.
- New maintenance branches, commits, pushes, or merges without separate user authorization. Runtime checkpoint permissions do not grant maintenance Git permissions, and the final feature merge remains the user's action.

## Questions

No user-policy questions remain from this discussion. Coder owns edits and uses helpers for exploration and test execution. Exceptional implementation phases, their intermediate review assurance and reasoning mappings, separate repair allowances, and final Coder ownership are selected requirements in sections 11–12. Standard features permit one repair cycle per intermediate phase review; Maximum features permit two. Final-review allowances retain the existing feature-assurance policy. Ordinary checkpoint groups remain free of intermediate wrapper/review handoffs.

The plan should make the remaining implementation choices concrete: unchanged content versions with progress, stage-aware review applicability, temporary-output lifecycle, complete bounded reads, resolved-finding history, artifact-only publishing, and phase-aware wrappers/history/resume while preserving recovery limits. The recommendation in section 6 should be assessed against the current contracts without silently changing the required behavior. Exact schema fields and event representations belong in that plan and must satisfy the agreed behavior without adding a separate state or evidence archive.

If inspection reveals a genuine contradiction or requires a new user-visible policy, identify it with its consequences during planning. Do not expand the work to cover test-kit fixes, add workflow restrictions from test-controller conventions, or replace recorded user decisions with a more elaborate process.

## References

Repository references are relative to this document. The local test evidence is outside the repository in a sibling directory and is supplemental: the observations and intended behavior needed for planning are summarized above. Missing access to that evidence must not be represented as a new reproduction or a successful validation.

- [Original v2.0.0 proposal](proposal-orchestrator-flow-v2.0.0.md): broader design baseline, especially assurance, overrides, document versions, handoffs, artifact boundaries, scoped blockers, and finalization. This corrections proposal and current Codex-only repository guidance govern the stated differences.
- [Repository guidance](../../AGENTS.md) and [README](../../README.md): maintenance scope, native integrations, installation, and validation expectations.
- [Codex skill](../../.codex/skills/orchestrator-flow/SKILL.md), [role contracts](../../.codex/skills/orchestrator-flow/references/), [workflow protocol](../../.codex/skills/orchestrator-flow/references/workflow-protocol.md), and [assurance contract](../../.codex/skills/orchestrator-flow/references/assurance.md): current runtime instructions and preservation boundaries.
- [Common schema](../../.codex/skills/orchestrator-flow/references/common.schema.json), [task-log schema](../../.codex/skills/orchestrator-flow/references/task_log_schema.json), and [wrapper contracts](../../.codex/skills/orchestrator-flow/references/wrappers/): current progress, finding, blocker, branch, and handoff representations.
- [Artifact validation](../../.codex/skills/orchestrator-flow/scripts/workflow_artifacts.py), [protocol replay](../../.codex/skills/orchestrator-flow/scripts/workflow_protocol.py), and [current-body reader](../../.codex/skills/orchestrator-flow/scripts/read_spec_body.py): executable behavior implicated by these corrections.
- [Development-test guide](../../tests/README.md), [protocol tests](../../tests/test_protocol.py), [recovery/review tests](../../tests/test_recovery_and_reviews.py), and [resource/document tests](../../tests/test_distribution.py): existing behavioral coverage to extend where relevant.
- [FEC bot v2.0.0 task list](../../../fec-bot/.docs/specs/v2.0.0-mal-provider-independence/tasks.md) and [task log](../../../fec-bot/.docs/specs/v2.0.0-mal-provider-independence/task_log.json): supplemental local evidence for checkpoint cadence. The local `v2.0.0-mal-provider-independence` branch preserves the original coding groups and workflow-transition commits; inspect it without checking out or modifying the consuming repository. Its older workflow schema is not a compatibility or migration target.
- [First-run closeout report](../../../orchestrator-flow-test-runs/testrun-1/.orchestrator-test/closeout-report.md): observed outcomes, attribution, evidence limits, and the distinction between workflow and harness failures. Its discussion of one-feature-per-chat is superseded for workflow scope by the user's decision recorded in this proposal.
- [Ignore-case task log](../../../orchestrator-flow-test-runs/testrun-1/standard/.docs/specs/ignore-case/task_log.json): actual review and assurance-override sequence underlying the unnecessary specification gap.
- [Basic review-read assessment](../../../orchestrator-flow-test-runs/testrun-1/.orchestrator-test/evidence/U-B-reviewer-evidence-assessment.json), [Maximum handoff audit](../../../orchestrator-flow-test-runs/testrun-1/.orchestrator-test/evidence/U-M-native-return-causal-audit-output.md), and [Standard native-return discrepancy](../../../orchestrator-flow-test-runs/testrun-1/.orchestrator-test/evidence/U-S-task6-native-return-discrepancy.json): evidence for the read and handoff failures, with their stated limits.
- [Standalone review assessment](../../../orchestrator-flow-test-runs/testrun-1/.orchestrator-test/evidence/Maximum-standalone-initial-result-assessment.json), [blocked-work assessment](../../../orchestrator-flow-test-runs/testrun-1/.orchestrator-test/evidence/G5-blocked-assessment.json), and [committed-artifact inventory](../../../orchestrator-flow-test-runs/testrun-1/.orchestrator-test/evidence/closeout-layout-and-source-status.json): reporting incompatibilities and the committed-wrapper observation.
