# Orchestrator Flow protocol

This is the Claude Code v2 runtime contract. Read this skill's `VERSION`, never a consumer product version. Codex has its own v2 integration with the same protocol and task log; GitHub Copilot and Cursor keep their native contracts, and their v2 updates are deferred. Repository maintenance does not activate this consumer workflow.

Use this reference for normal coordination. Roles read their own contract and `assurance.md`. Consult `workflow-recovery.md` for interrupted or failed work, `implementation-phases.md` for an approved phased plan, and `maximum-assurance.md` when the applicable review assurance is Maximum. `<skill-dir>` is the skill directory Orchestrator passes to every role.

## Ownership and inputs

| Role | Claude Code agent | Ownership |
| --- | --- | --- |
| Orchestrator | the main conversation | User interaction, configuration, initialization, approvals, task log, known issues, log checkpoints and recovery coordination |
| Planner | `flow-planner` | Requirements, design, tasks, optional research/manual test plan, their artifact checkpoints and handoffs |
| Architect | `flow-architect` | Read-only specification review |
| Coder | `flow-coder` | Intentional implementation/test/documentation edits, task completion accounting, artifact checkpoints and cumulative completion |
| Reviewer | `flow-reviewer` | Read-only implementation review |
| Exploration helper | `flow-explorer` | Bounded questions about code, interfaces, dependencies and external sources, for its lead |
| Test and check helper | `flow-runner` | Specified tests, lint, type checks, builds and planned manual checks, for its lead |

Users, the task log and wrappers keep the role names; Orchestrator maps each role to its agent, so "switch the Reviewer to Fable" means exactly that. Helpers explore or execute specified checks; they do not intentionally edit project files or publish. All user questions pass through Orchestrator, because only the main conversation can ask the user. Orchestrator reads metadata, structured returns and concise mechanical diagnostics, never product patches, source/tests or spec/research bodies. Delegate content questions to the responsible role.

Accept a free-form request, completed proposal/bug-report path, or supported existing spec. Use `.docs/specs/{feature}/` with a lowercase feature identifier separated by hyphens or dots and workspace-relative POSIX paths. Approved documents and subsequent recorded decisions govern over superseded input wording. Follow the consuming project's `CLAUDE.md` and `AGENTS.md` and the project-owned coding directives they identify.

## Configuration and authority

Consumer-root `.orchestrator-flow.json` records `assurance_level` and `capability_defaults` for configured platforms. The `claude-code` map assigns model/effort to planner, architect, coder, reviewer and helpers, plus an optional `exploration_helpers` assignment. When `exploration_helpers` is present, exploration and research helpers use it and `helpers` covers test and check execution; when it is absent, `helpers` covers both. Setup establishes missing defaults with the user; the starting suggestion is:

| Role | `model` | `reasoning_effort` |
| --- | --- | --- |
| planner | `opus` | `xhigh` |
| architect | `opus` | `max` |
| coder | `opus` | `high` |
| reviewer | `opus` | `max` |
| exploration_helpers | `sonnet` | `medium` |
| helpers | `haiku` | `medium` |

Before Planner runs, present feature recommendations and obtain acceptance of the complete resolved configuration. Record it in the first start event and effective log fields. Feature acceptance leaves repository defaults unchanged; resume uses the feature settings.

Assurance is basic, standard or maximum for the entire feature, independently of capability. Difficulty concerns ambiguity, unfamiliar interfaces, integration and state, and conflicting evidence; assurance concerns project consequences, exposure, reversibility and user preference. Technical difficulty alone does not select Maximum.

Capability contains `platform: "claude-code"`, the resolved roles and acknowledged limitations. Models are the Agent tool's short names `opus`, `sonnet`, `haiku` and `fable`; efforts are `low`, `medium`, `high`, `xhigh` and `max`. Record the short name actually passed and always an explicit effort, because Claude Code's default effort differs by model. A short name resolves to the newest model in its family, or to the session's own version when the session uses that family; state this once in the recommendation, not as a per-feature limitation. Acknowledged limitations hold only real feature-specific limitations the user accepted: an environment override that defeats per-call choices (`CLAUDE_CODE_SUBAGENT_MODEL_FORCE`, `CLAUDE_CODE_EFFORT_LEVEL`), Fable's automatic fallback and usage-credit pauses when Fable is chosen, an `availableModels` or `fallbackModel` substitution that Claude Code reports, and an unmapped intermediate effort. If an assignment cannot be honored, or a model is unavailable or a usage limit is reached, pause the affected work for the user's choice; never silently substitute or change assurance.

Write the selected feature review policy explicitly; it is not a repository-default setting:

| Policy | Repair gate |
| --- | --- |
| `spec_user_code_auto` (built-in default) | User dispositions before Planner repairs; ordinary Coder repairs may proceed within approved scope |
| `all_user` | User dispositions before either producer repairs |
| `within_scope_auto` | Routine repairs in both loops may proceed within approved scope |

Every policy preserves material document approvals, product decisions, explicit must-fix exceptions, repair-limit decisions and new operational authority. Nits alone require no repair pass or extra decision.

An explicit `user-override` carries `changes: [{target, previous, new}]`, the user statement and any rationale. Allow only /assurance_level, /review_disposition_policy, complete /capability, or a complete /capability/roles/{role} for a configured role. Add or remove `exploration_helpers` with a complete /capability override. Platform changes replace capability. Reject overlapping targets and false previous values. Record the override with `<skill-dir>/.venv/bin/python <skill-dir>/scripts/claude_log.py append-entry`, which updates the effective fields with the appended history, then checkpoint.

Capability changes apply prospectively to subsequent affected work. Retain assignment, baseline, completed work, approvals and repair allowances. A helper-only change is sent to the running lead with SendMessage and applies to the helpers it starts next, without restarting the lead. SendMessage cannot change a lead's model or effort, so a lead change starts a replacement lead with the new settings at a coherent boundary, without duplicating a writer; the replacement keeps the logical assignment. Accept useful in-flight output after a capability-only change. No dispatch event, configuration-bound lineage or helper ledger is required.

An invocation is `{trigger_event_id, role, attempt, context_id?}`. Trigger/role identifies the assignment; the agent may change; attempt advances for a genuine recorded execution failure, not a setting change or small report correction. The `context_id` is the lead's Claude Code agent ID. A start event is recorded before its lead launches, so a lead's first start event and first return may omit it; Orchestrator gives the ID to the lead in continuation messages, and the lead includes it in later returns. Follow-up and repair start events for a continuing lead record it. Every lead's start prompt begins with the lines `Orchestrator-Feature: <feature>` and `Orchestrator-Invocation: <trigger>/<role>/<attempt>`; when the ID is not recorded, `<skill-dir>/.venv/bin/python <skill-dir>/scripts/claude_log.py find-agent --feature <feature> --invocation <trigger>/<role>/<attempt>` finds it from them, newest first. Review starting assurance and stage come from the start event's position in history. Returns retain actual assurance; capability changes cannot relabel Basic review work as Maximum.

## Starting and continuing roles

Start each lead with the Agent tool: `subagent_type` (its `flow-*` agent), a short `description`, the `prompt`, the accepted `model` and `effort`, and `run_in_background: true`. Never start a role as a fork (it would inherit this conversation and its model), never pass `isolation` (no worktrees), `name` (it can launch an agent-team teammate) or a team, and never use agent memory; workflow state lives in the task log and Git. One producer works at a time.

The prompt begins with the `Orchestrator-Feature` and `Orchestrator-Invocation` lines, then gives the skill directory and the contract paths to read, the invocation, effective configuration (including helper assignments), the explicit feature branch, remote and baseline, artifact paths and versions, approval bases, governing user decisions, findings/dispositions and bounded evidence. Pass large prior outputs by reference, the log path and event ID, and let the role read that exact entry rather than a paraphrase.

Background leads report through completion notices. Act when a notice arrives and stay available to the user meanwhile. Before sending a lead any message, run `<skill-dir>/.venv/bin/python <skill-dir>/scripts/claude_log.py record-return --log <log> --agent-id <id>` for it: carry on after `already_recorded` or `no_completed_report`, and handle a newly recorded return first, because a message to a finished lead starts a new run and its earlier report could no longer be recorded. After the recorder refuses a report (`report_not_json`, `report_truncated`, `invalid_native_output`), message the same agent to correct it. Continue a lead with SendMessage to its agent ID (Planner after each approval, Coder for repairs, Architect and Reviewer for follow-up reviews) only while its model and effort match the assignment its next work requires; otherwise start a replacement. For example, the final review of a phased feature uses a new `flow-reviewer` at `roles.reviewer`, never the intermediate reviewer. A continued lead keeps its context. Before Orchestrator takes Git for a decision or recovery update while Coder is working, SendMessage a coherent-yield request; Coder finishes its current coherent step, returns a coordination report with `yielded: true`, and waits for the message to continue. While Planner is working, Orchestrator records entries but checkpoints the log only after Planner's next handoff.

Roles return questions in their structured output: Planner in its incremental return, Coder as blockers in a coordination report, whose details allow only invocation, summary, task_progress, blockers, references, work_scope and yielded. Orchestrator asks the user, using AskUserQuestion for discrete choices, records the answer and continues the role with SendMessage. If a lead cannot start helpers, Orchestrator runs the permitted helper work itself and returns the evidence to the lead.

## Ordinary planning and review

1. Establish the feature branch, explicit integration branch, remote and baseline in the existing checkout (see Checkpoint cadence for the branch rule). A branch does not authorize a worktree.
2. Create the task log with the accepted settings and input, validate it, deliver its checkpoint, then delegate Planner.
3. Planner publishes requirements and returns its actual incremental JSON. Record that handoff, obtain exact-version approval and deliver the decision before dependent design. Repeat for design.
4. Planner publishes tasks and returns the consolidated Planner handoff **with that final draft**, before tasks approval. It contains all three current snapshots, material decisions/reasons, constraints and applicable dispositions. Record it once as `spec-updated`; stay `spec_in_progress` while tasks approval is outstanding.
5. Unchanged tasks approval establishes `spec_ready` when all approvals and consolidated context are valid. Pass the same immutable handoff, by reference, and subsequently recorded approval context to Architect. Do not recall Planner or copy the wrapper into another event.
6. Record Architect's actual review. Apply findings, assurance and policy. Acceptance requires separate explicit coding authorization; a refusal/deferral does not invent a spec-change request.

Feedback while Planner is drafting stays in that creation/revision cycle, even after an earlier handoff. Record `user-change-requested`, preserve trigger/requestor/context, continue Planner with SendMessage, and cite the request in the next return. After a completed handoff outside drafting, start a revision from the earliest affected artifact.

Requirements material changes must be approved before dependent design changes; design before tasks; tasks before Architect. Do not edit or reapprove unaffected documents. Editorial corrections and faithful recording can preserve a justified approval basis. A changed material decision requires the appropriate revised content/handoff and approval; consolidation cannot silently replace the tasks-bound phase plan.

## Documents and retrieval

Required documents start with a title and `Content version: N` immediately below it. Start at 1; each completed content update increments independently by one and appends meaningful changes/reasons in the final `## Revision History`. Include the initial draft; separate completed updates remain separate versions. Restoring old content creates a new version. No approvals, workflow state, branches or Git metadata belong in document bodies.

Coder may change actual numbered task-checkbox markers outside fenced code only. Report `change_kind: progress` on tasks with equal non-null previous/current versions and the existing approval reference. Preserve content version, Revision History, Planner producing reference and approval. Mechanical comparison normalizes newlines and those markers only. Other content remains Planner-owned. Later completion never implies earlier tasks completed.

Read bodies with `<skill-dir>/.venv/bin/python <skill-dir>/scripts/read_spec_body.py <path> --offset 0 --max-chars 8000`. The result is `{start_offset, next_offset, eof, text}` in decoded newline-normalized character offsets. Continue from next_offset through eof. Discard a truncated chunk and reread its starting offset with a smaller bound; never infer unread lines. Fence-aware retrieval excludes the final Revision History before output, including when chunks split long lines, Unicode or fences. Plain body and explicit --history modes remain available; no read-audit artifact.

Initial Architect and Reviewer reads cover all three complete current bodies. Tasks have no appendices: technical contracts belong in design, empirical evidence in optional research, process history in the log. Research uses Purpose and Scope; Investigations and Findings; Open Questions; Sources and References. It has no content version, Revision History or separate approval gate. Planner owns substantive corrections.

## Compact returns and recording

The four schemas under `wrappers/` are authoritative; `common.schema.json` holds local definitions. Every wrapper has a meaningful summary. Omit irrelevant optional collections/placeholders instead of emitting empty inventories.

| Return | Required core |
| --- | --- |
| Planner | context, output_kind (incremental/consolidated), summary, artifacts, checkpoint_commit |
| Coder | context, summary, artifacts, checkpoint_commit, task_progress, checks; always cumulative |
| Architect/Reviewer | context, summary, reviewed_output_ref, assurance_level, review_scope, accepted, issue_details |

Include applicable changes, causal references, material decisions with reasons, constraints, impacts, questions, dispositions and evidence. Coder's changed/new/deleted files form one cumulative inventory; checks contain actual commands/selections, statuses, useful counts, expected Red outcomes and failures. Do not repeat checks as CLI/test-result inventories. Material non-verification operations belong in the summary or relevant evidence.

Producer checkpoint_commit identifies already-published artifacts, not the containing log commit. Consolidation/report correction without content changes may reuse the applicable checkpoint. An incremental Planner return before any artifact/research exists may have null artifacts/checkpoint and specific blocking questions; no empty commit, approval or review readiness follows. Ordinary clarification still uses draft-first planning.

Embedded reviews reference the source handoff for versions/commit and the review start for prior-review context, stage and initial/follow-up status. Approval context current at review start remains available, including for an earlier phase reviewed after a spec revision. Standalone wrappers use context null; reviews supply reviewed_artifacts, reviewed_commit (nullable), review_kind and reviewed_output_ref null, with actual report/source descriptions instead of invented event references. Repair follow-ups include repair_class, changed_surfaces, scope_reason and meaningful_change.

Keep current findings (including accepted limitations) in issue_details, current responses in dispositions, and repaired identities in unique, disjoint resolved_findings. Preserve earlier reasons/authority/evidence in summary and sources. Unresolved findings cannot vanish. Finding IDs remain S-<first-review-start-id>-<ordinal> or C-<first-review-start-id>-<ordinal>; standalone uses 0.

Structured historical references are `{event_id, kind}`, referring backward to an existing event/wrapper of the declared type. Only schema-declared references are validated; narrative phrases and ordinary numbers are not parsed as history.

A role's report (its final message, or the SubagentHandback message when it reports through that tool in auto mode) is its JSON wrapper alone, with no code fences or prose and not also written out as text first, validated by the role before returning. Orchestrator records it with `<skill-dir>/.venv/bin/python <skill-dir>/scripts/claude_log.py record-return --log <authoritative-log> --agent-id <id> [--workspace <consumer-root>]`. The helper reads the role's final message for its latest completed run directly from the subagent transcript, parses it, and records it through the shared `record_handoff`, which derives event, next ID, UTC recording timestamp, role, causal requestor and resulting state, embeds the parsed object unchanged, validates the candidate and optional workspace, writes only the authoritative log and checks readback. The helper recognizes a Coder coordination report by its `invocation` and records it as `coding-updated`. The helper then prints a compact summary: the recorded event and status, the replay's next workflow action, review acceptance, open must_fix/should_fix findings with ID, severity and title, the nit count, questions, blockers, the agent ID, and the model and effort the transcript shows, with a `capability_note` when they differ from the recorded assignment. Show a `capability_note` to the user as a limitation to accept or address before dependent work continues. Work from that summary; do not load a large return into this conversation. Commit/push remain separate.

Never copy a completion notice's text into the log: notification text is escaped and may be altered by the harness. If the transcript cannot be found or read, `--transcript <path>` names it explicitly (for example the notice's output file); `--stdin` accepts only unaltered inline JSON from a foreground or standalone result and refuses escaped or harness-marked text. If neither works, stop and ask the user. Never record a summary, a pointer or a reconstruction. The helper refuses a return identical to its lead's latest recorded return, a run that has not finished, and a report cut at the output limit (`report_truncated`), which the same agent must return complete in one message.

Orchestrator records its own entries (start events, approvals, user changes, overrides, dispositions, authorizations, evidence assessments and final acceptance) with `<skill-dir>/.venv/bin/python <skill-dir>/scripts/claude_log.py append-entry --log <authoritative-log> [--workspace <consumer-root>]`, giving `{actor, requestor, event, details}` on stdin. The helper derives the ID, timestamp, resulting status and effective configuration through the shared replay, validates the candidate against the current log before writing, writes only the authoritative log and reads it back. The initial log, whose first entry carries the accepted configuration, is created with the Write tool and validated with `<skill-dir>/.venv/bin/python <skill-dir>/scripts/validate_orchestrator_artifacts.py task-log <log>`. Never edit an existing log by hand.

Malformed/pointer/status-only output cannot advance a completion gate. A small missing path or unclear summary is corrected in the same assignment, by SendMessage to the same agent, without a failure event, retry dispatch, repair cycle, empty commit or automatic retest. Actual execution failure, unusable output or repeated inability to return a usable report uses bounded recovery. Valid adverse findings are not execution failure. Recording errors belong to Orchestrator, not the producer; see recovery guidance.

Inputs on stdin are UTF-8. Other validators accept primary input `-`, and observations may use stdin when the log comes from a file. No routine wrapper files, snapshots or archives; exceptional temporary copies need a concrete tool/recovery necessity, stay outside durable project content and are removed after validated durable recording.

## State and events

Use exactly these statuses: spec_in_progress, spec_ready, spec_in_review, spec_approved, spec_changes_requested; coding_in_progress, coding_complete, blocked, code_in_review, code_approved, code_changes_requested; implementation_complete.

History has contiguous string IDs, real UTC timestamps, actor, causal requestor, resulting status and exactly one compatible details/wrapper payload. Requestor is never Orchestrator. Validate candidate append and complete history before checkpoint/dependent work. No persisted pending-action or duplicate state registry.

| Event | Actor / causal requestor | Effect |
| --- | --- | --- |
| spec-creation-started | Planner / User | Initialize once; spec_in_progress |
| spec-revision-started | Planner / User or Architect | Begin authorized revision; spec_in_progress |
| user-change-requested | Orchestrator / User | Continue active drafting; otherwise request spec revision |
| spec-updated | Planner / its start requestor | Record actual draft/consolidation; spec_ready only with valid approvals/context |
| spec-artifact-approved | User / Planner | Approve exact version/producing output; enable spec_ready when the final gate is satisfied |
| spec-review-started | Architect / Planner | spec_in_review; initial or required follow-up |
| spec-reviewed | Architect / Planner | spec_approved or spec_changes_requested under actual conditions/current gates |
| review-findings-dispositioned | User / relevant producer or reviewer | One actual decision, including batch findings; no duplicate user-approval event |
| review-evidence-assessed | Architect / Planner or Reviewer / Coder | Exceptional bounded applicability assessment; preserve phase, no new acceptance |
| coding-started | Coder / Planner | coding_in_progress with valid spec and coding authority |
| coding-revision-started | Coder / Reviewer | Repair the active review's scope under policy/allowance |
| coding-updated | Coder / its start requestor | Coordination details only; preserve assignment, or blocked if no independent approved work remains |
| coding-phase-complete | Coder / its start requestor | Nonfinal scoped completion; coding_in_progress pending phase gate |
| coding-complete | Coder / its start requestor | Whole-feature cumulative completion; coding_complete |
| code-review-started | Reviewer / Coder | code_in_review |
| code-reviewed | Reviewer / Coder | code_approved or code_changes_requested; accepted intermediate phase returns to coding_in_progress |
| user-override | User / User | Preserve phase; apply accepted configuration |
| user-authorization-recorded | User / User | Preserve phase; grant/deny/defer only stated operation and bounds |
| subagent-error | Failed role / its actual start requestor | Preserve phase and genuine failure evidence |
| implementation-complete | Orchestrator / User | Explicit accepted feature; implementation_complete, then deliver checkpoint |

Wrapper acceptance strings remain true, false, conditional. Open must-fix conditions yield false; remaining lesser acceptance conditions yield conditional; nits alone yield true at every assurance. An outstanding explicit user request to fix, clarify or reconsider a nit is a remaining condition. Both unresolved results use changes_requested, not an extra conditional state. Actual user decisions can close conditions; changed work still needs its required review.

## Findings, checks and implementation

Apply `assurance.md` before deciding remediation. Dispositions support fix, defer, accept_limitation, reject, reconsider and clarify with rationale. Omitted authority is a proposal, not permission. User disposition events record the actual decision; later returns cite it. Policy authority cannot override a contrary user instruction or waive must-fix. A fix response is intent until review resolves the finding.

Nits are nonblocking by default. Derive their default deferral and concise known issues directly from review/policy; no producer bounce or extra approval solely for nits. If the user explicitly requests a fix, record that actual decision through review-findings-dispositioned and use the existing repair path and allowances. Keep the decision's user authority through matching producer responses until follow-up review resolves the work. Do not invent a cleanup deadline. Required review work, evidence, tasks and checks remain necessary. Acceptance ends the loop without polishing or an unnecessary limit prompt.

After explicit coding authorization, Coder executes the approved concrete design/tasks with separate Red/Green stages at every level. Planner defines coherent behavioral steps, natural groups, documentation and final Test-Maintenance before Verification. Leads start their own helpers with the Agent tool, the accepted helper `model` and `effort`, and `run_in_background: false`, and wait for the result: `flow-explorer` uses `exploration_helpers` when configured, otherwise `helpers`; `flow-runner` uses `helpers`. Group related checks into one helper call, start fresh helpers after an interruption rather than resuming them, and read a helper's saved-output file if its report arrives as a preview instead of rerunning it. Coder owns edits and interpretation. Basic/Standard reuse fresh applicable results and check at meaningful integration boundaries; Maximum retains comprehensive fresh review work.

Ordinary Coder checkpoints need no interim wrapper or acknowledgement. coding-updated records meaningful coordination using invocation, summary, relevant progress/blockers/references and optional scope. Record yielded true only for an actual coherent yield; absence means false. Completed independent tasks are progress, not remaining independent IDs. Completion requires every actual required task/check or valid explicit exception. The cumulative return covers the original assignment baseline, including pre-interruption work.

## Checkpoint cadence

The feature branch is the user's explicit branch when one is given; otherwise it is exactly the feature name, which carries a release version when the user's feature name includes one (`v2.1.0-claude-code-integration`, `1.4.0-mail-migration`) and is the bare name otherwise (`unique-lines`). Never add a `claude/`, `codex/` or other prefix, even where Claude Code's own conventions would, and never invent or normalize a product version. Validate with `git check-ref-format --branch`; on a conflict or an existing branch, ask the user and never silently choose another name. Record `branch_context` (feature branch, explicit integration branch, remote, baseline) in the initial event and reuse it on resume. Use the existing checkout; a branch request is not a worktree request.

Planner publishes each substantive draft/revision/research update before returning. Coder publishes natural approved groups, meaningful partial work and completion/repairs. Orchestrator separately validates, commits and pushes actual log updates and its known-issue/configuration changes. Every checkpoint is committed on the feature branch and pushed to it on the recorded remote, never to the integration branch. Before each checkpoint the publisher confirms `git branch --show-current` names the recorded feature branch; on a mismatch it stops and reports instead of switching branches. Related events may share a logical log checkpoint; never batch away completed drafts or gates. Describe Red/incomplete work accurately. Ordinary checkpoints, polls and successful pushes create no events.

Serialize Git ownership through the active producer and coherent yields. Helpers never publish. Stage only owned changes; for wholly owned paths an explicit `git commit --only ... -- <paths>` can exclude unrelated staged files. Mixed files require owned hunks or direction. Run Git as plain `git …` from the project root. Orchestrator delegates content inspection; it sees names/statuses and concise checks. Never force-push, discard unrelated work or merge.

Every checkpoint has Orchestrator-Feature, Orchestrator-Checkpoint (artifacts/log), Orchestrator-Role. Producer artifacts also have Orchestrator-Invocation: <trigger>/<role>/<attempt>, and Orchestrator-Phase when applicable. Log commits have Orchestrator-Log and a contiguous Orchestrator-Events range. Artifact-only commits omit log/event ranges. Orchestrator may publish its own artifact-only change without a delegated invocation. No dispatch trailer and no containing commit's own hash in events.

Before each push, record attempt identity using `<skill-dir>/.venv/bin/python <skill-dir>/scripts/checkpoint_state.py attempt`; it writes local Git-metadata evidence only. After failure use `failure`, preserve the commit, globally pause and follow `workflow-recovery.md`. A commit failure blocks dependent work. Success is established by Git inspection, not a success receipt. Runtime utilities do not dispatch agents, commit, push or merge.

## Permissions

The permission mode is the user's choice; the workflow never changes it. Roles run Git and the workflow scripts through Bash; a background agent's permission prompts appear in the main session and name the agent. Report a declined prompt or an auto-mode classifier block, with its rule name, exactly as it happened, with no invented exit codes; any retry follows the bounded user-directed recovery. After repeated blocks auto mode falls back to prompts and the run waits for the user. If a completion notice carries a classifier security warning or a note to verify the work, show it to the user before recording or acting on that return. Headless `-p` runs are not supported.

## Known issues, completion and compatibility

Orchestrator derives known-issues.md from applicable unresolved findings and valid dispositions, including default nit deferral. Include ID, impact, severity, response/reason, sources and useful workaround/revisit conditions. Distinguish possible future work from accepted limitations with no planned fix. Remove fixed entries; rejected/historical resolutions remain in history/Git. Listing an issue does not grant permission.

After whole-feature code approval, present delivered behavior, verified results and limitations for explicit user acceptance. Record implementation-complete, deliver its checkpoint, then supply one conventional squash message describing the total change relative to the integration baseline. Include useful grouped implementation/spec/documentation/test coverage and evidence-backed results; no invented counts. The user merges manually. A commit-message request is not completion authority. After completion only necessary checkpoint recovery is allowed.

A released reader supports logs from 2.0.0 through its own version within major 2. Reject missing/pre-2, other major and unsupported newer writer versions before mutation. Pre-v2 Claude Code logs are unsupported; encountering one stops for user direction. Do not migrate prerelease shapes or historical runs. Future compatible additions preserve meaning. Read optional collections as empty and absent work_scope as feature only where allowed; an absent `exploration_helpers` means `helpers` covers exploration, and an absent helper-failure `assignment` means `helpers`; no absent phase assignment is inferred. Apply defaults in code without modifying captured returns; never manufacture approvals, evidence, assurance or user authority. Resume keeps the recorded workflow version. Switching an in-progress feature between platforms is not supported.
