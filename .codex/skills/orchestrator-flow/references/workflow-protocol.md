# Orchestrator Flow protocol

Read the bundled `VERSION`; the initial contract is 2.0.0. This reference and the JSON schemas define the Codex v2 workflow. The skill's `SKILL.md` defines native Codex invocation and permission mechanisms. The other integrations retain their independent native contracts; their v2 updates are deferred. Follow the consuming repository's AGENTS.md, README and any project-owned codingAgentDirectives.md they identify. Such coding directives are optional project policy, not a bundled workflow resource. Do not load the distribution's reusable directives as project policy or copy them into the project automatically.

Maintaining this distribution does not activate the consumer workflow. These runtime rules apply when the user invokes Orchestrator Flow in a consuming repository.

## Ownership and entry points

| Role | Owns | Does not own |
| --- | --- | --- |
| Orchestrator | User interaction, gates, configuration, task log, known issues, delegation, branch/checkpoints | Spec content, implementation, independently waiving findings |
| Planner | Requirements, design, tasks, optional research/manual test plan, incremental and consolidated spec output | Product implementation, task log, Git operations |
| Architect | Read-only specification review and evidence | Spec/research edits, task log, Git operations |
| Coder | Approved implementation/tests/docs and task-completion accounting | Substantive spec/task changes, task log, Git operations |
| Reviewer | Read-only implementation review and evidence | Product/spec/research edits, task log, Git operations |

Accept free-form proposals, completed proposal/bug-report paths, and supported existing spec directories. Use `templates/proposal-template.md` and `templates/bugreport-template.md` from the bundle for new input documents. The input starts planning; approved requirements/design/tasks and subsequent recorded decisions become authoritative. Do not give stale input wording precedence over approved changes.

Use `.docs/specs/{feature}/`, with a lowercase feature identifier separated by hyphens or dots. Keep distributed artifact paths workspace-relative and POSIX-style. Orchestrator may inspect metadata and structured outputs; delegate substantive interpretation/authoring to the owning role. All orchestrated role outputs are JSON-only wrappers, without surrounding prose. Questions return through Orchestrator; hidden role conversations are not approval records.

## Version support

Read the workflow bundle's `VERSION`, never a consumer product's version file. A reader supports released logs from 2.0.0 through its own version in major version 2. Missing/pre-2.0 versions, a different major, or a newer unsupported writer version stop execution/resumption before mutation. Explain and obtain direction. There is no automatic migration, historical-log repair, or modification of completed historical features.

Patch/minor upgrades must preserve earlier supported logs' execution semantics, configuration and approval meaning. An additive field must be optional for older logs or have a documented behavior-preserving read-time value actually applied by validators and runtime code. A schema `default` annotation is not an implementation. Never initialize an absent field by inventing authorization, a user override, or an assurance choice. Version 2.0.0 has no missing required-field defaults. The optional authorization field `uncertain_attempts` reads as `[]` when absent; the reducer and checkpoint helper apply this value without modifying historical records or granting authority. New logs write the full applicable contract explicitly. Do not rewrite the log's version on resume.

## Configuration and capability

The schema `repository_config.schema.json` defines committed consumer-root `.orchestrator-flow.json`: `assurance_level` and `capability_defaults` for configured platforms. Defaults belong there, not in `AGENTS.md`. Each platform maps `planner`, `architect`, `coder`, `reviewer`, and `helpers` to a `model` and `reasoning_effort`.

At setup, recommend supported assignments and assurance and obtain acceptance. At feature initialization, read repository defaults, assess the input, present feature recommendations, and record the user's acceptance before Planner starts. Resolve all inherited settings into top-level `assurance_level`, `capability`, and `review_disposition_policy` in `task_log.json`. Record the complete accepted initial configuration in the first start event. Repository-default changes affect future features only. Applying them to an existing feature requires explicit override; accepting a feature recommendation does not change defaults.

One assurance level (`basic`, `standard`, `maximum`) governs the feature. Capability is independent: reasoning difficulty concerns ambiguity, unfamiliar interfaces, integration and stateful behavior; assurance concerns consequences, exposure, reversibility, recovery cost and user preference. Technical difficulty does not itself require Maximum.

`capability` contains `platform`, five resolved `roles`, and `acknowledged_limitations`. Use real native model/effort controls. `platform_default` represents explicitly accepted inheritance; `not_supported` is allowed only for an effort control that is unavailable. Record limitations and resolve concrete values when the platform exposes them. Never claim a prompt alone enforces a native assignment. If a configured assignment cannot be honored, pause affected work and obtain the user's alternative or wait decision. No automatic model fallback, including for helpers. A substitution never changes assurance implicitly.

The built-in policy is `spec_user_code_auto`. Write it explicitly in the feature log, not repository defaults:

| Policy | Repair gate |
| --- | --- |
| `spec_user_code_auto` | User disposition of Architect findings before Planner repair; routine Reviewer-driven Coder repairs may continue within approved scope/assurance. |
| `all_user` | User disposition before either producer repair pass. |
| `within_scope_auto` | Both producers may make routine approved in-scope repairs under policy. |

All policies retain separate material artifact approvals, product decisions, explicit must-fix exceptions, loop-limit decisions and new operational authority. Batch user finding decisions when useful. Preserve authorization already granted for ordinary in-scope repairs.

`user-override` records `changes: [{target, previous, new}]`, supplied rationale and the user statement. Allowed targets are `/assurance_level`, `/review_disposition_policy`, `/capability`, and a complete `/capability/roles/{role}` assignment. Platform changes replace the entire capability. Reject overlapping targets and false previous values. Append history and update effective fields in the same validated write; checkpoint it. Overrides preserve phase and do not rewrite earlier results. Consecutive overrides do not hide the underlying resume action. An increase in assurance requires explicit evidence-gap review, not automatic repetition of all work or assumed equivalence. A review already running retains its actual invocation basis. On every returned review, also compare its assurance with the feature's current requirement, including the first review: a lower-assurance result leaves a gap that blocks dependent coding or final completion until sufficient catch-up review. Record the returned evidence accurately; do not relabel it as higher assurance.

## Documents, versions and approvals

Requirements, design, and tasks are mandatory and approved separately in dependency order. Initial requirements and each material requirements change require approval before dependent design work. Material design changes require approval before dependent task work. Material task changes require approval before the applicable Architect review. Begin a revision at the earliest affected artifact; do not edit or reapprove unaffected artifacts.

Each required document starts with its title and `Content version: N` on the next line. Begin at 1, increment once per completed content update, and append `### Version N — YYYY-MM-DD` with meaningful changes and concise reasoning under the final `## Revision History` section. Include the first draft. Versions advance independently; two updates in one session are two versions. Restore old content as a new version without erasing intervening history. No approvals, workflow status, branch names, Git hashes or checkpoint metadata belong in these documents.

`spec-artifact-approved` identifies artifact, content version, producing Planner-output reference and the actual user statement. Pure approvals do not change documents. Material edits invalidate the affected approval. Editorial corrections, faithful recording of an already-approved decision, and Coder task-progress edits may preserve approval; record `change_kind` and the real `approval_basis_ref` rather than inventing approval of the new version. Coder changes only completion accounting and corresponding tasks version/history; Planner owns substantive task instructions.

Consumers retrieve current content with `scripts/read_spec_body.py <path>`. It streams only the body before the final Revision History heading outside code fences. Use `--history` when history is actually needed; reading everything and ignoring history afterward wastes context. Current design rationale remains beside the relevant contract.

Tasks contain no appendices. Keep technical contracts in design, empirical evidence in research, process history in the task log, and executable targets/test ownership/requirements mapping in tasks. Optional research uses Purpose and Scope; Investigations and Findings; Open Questions; Sources and References. Distinguish observations from inferences, preserve relevant negative findings, correct superseded conclusions and reference large evidence. Research has no content version, Revision History or fourth approval gate. Planner owns substantive research changes; reviewers return findings.

## Outputs and references

The four schemas under `wrappers/` and their examples are authoritative. `common.schema.json` supplies shared definitions. All schemas use locally registered URNs; validators never fetch remote schemas.

Planner and Coder return `output_kind: incremental | consolidated`. Each logical update returns promptly for recording and checkpointing. Incremental Planner outputs include current artifact snapshots (null when absent), previous/current changed versions, initiating causes, decisions/rationale, downstream impacts, dispositions, questions and research changes. The final Planner handoff consolidates current decisions and rationale rather than concatenating the conversation. Before review, all three current artifacts and approvals must be available. Code handoffs likewise identify cumulative implementation scope and evidence.

Invocation context contains `trigger_event_id`, workflow `role`, `attempt`, native `context_id`, and `configuration_ref`. Initial configuration is event 1; later configuration references identify an override. New logical starts use attempt 1; ordinary retries retain the trigger and advance the attempt. Multiple incremental outputs can belong to the same invocation/context. Standalone wrappers use `context: null`; embedding them as orchestrated output requires actual authoritative context, not invented history.

Standalone reviews may record actual directly supplied user dispositions and omit historical output/prior-review references. Identify prior standalone reports and decisions in notes/source evidence instead of inventing event IDs. The validator derives standalone acceptance from those supplied responses; embedding the output later still requires the real configuration, invocation and recorded user authority.

Structured references use `{event_id, kind}`. Kinds are `event`, `spec_review`, `code_review`, `approval`, `authorization`, `override`, or one of the four wrapper names. References point backward to an existing event of the right type. Supported text references are `history entry 2`, `history entries 2, 4 and 6`, `spec_review_wrapper from history entry 10`, and `spec review events 10, 15` (equivalent code-review/plural wrapper forms are supported). Use structured references for authority and precise relationships. Numbers without these labels are not history references.

Finding IDs are `S-<first-review-start-id>-<ordinal>` or `C-<first-review-start-id>-<ordinal>`; retain identity on follow-up. Standalone reviews use 0 for the absent start ID. Findings explain conditions, consequences and the acceptance-standard rationale, with `basis` distinguishing `demonstrated_defect`, `hardening_opportunity`, and `preference`. New evidence or changed classification has a `reconsideration_reason`.

Responses are `fix`, `defer`, `accept_limitation`, `reject`, `reconsider`, or `clarify`, with rationale and `authority`. User disposition events have `authority: user` and a null `authority_ref` because that event is the actual decision. A later wrapper reusing it cites the user event. Producers record policy-permitted decisions as `authority: policy`, never as user action. A `fix` response is intent; the subsequent review identifies genuinely resolved findings. No role silently drops an unresolved finding.

Review wrappers carry or confirm existing producer/user dispositions; review roles do not invent producer responses. A policy response cannot replace a user's contrary instruction. One actual user decision may support several related records in the same logical checkpoint; do not ask the user to grant the same approval twice merely to populate those records.

Reviews state actual reviewed artifact versions, output/prior-review references, assurance/policy basis, repair class, changed surfaces, chosen scope, reason and evidence. `meaningful_change` reports whether the reviewed work materially progressed since the prior review; it supports stalled-loop checks. Acceptance strings remain `true`, `false`, `conditional`: undispositioned must-fix blocks; open lesser acceptance conditions are conditional; appropriately accepted limitations can remain with acceptance.

## Events and deterministic resumption

History is append-only. IDs are contiguous string-encoded integers starting at 1. Obtain real UTC timestamps from the system. Each entry contains actor, causal requestor, resulting status, event, and exactly one event-specific `details` object or compatible wrapper. `requestor` is never Orchestrator. The first start event records the original request, accepted complete configuration, branch context and user acceptance.

| Event | Actor / requestor | Result and next action |
| --- | --- | --- |
| `spec-creation-started` | Planner / User | One initial creation event; `spec_in_progress`; recover/begin Planner. |
| `spec-revision-started` | Planner / User or Architect | `spec_in_progress`; begin approved revision from recorded request/findings and earliest affected artifact. |
| `user-change-requested` | Orchestrator / User | Feedback while `spec_in_progress` stays in the current Planner creation or revision cycle, even after an earlier completed handoff. Outside drafting, use `spec_changes_requested` and start a revision. Route through Planner, including requests received during coding/review. |
| Incremental `spec-updated` | Planner / requestor of its start | `spec_in_progress`; record actual output, checkpoint, then obtain necessary artifact approval or continue the same Planner context. |
| `spec-artifact-approved` | User / Planner | `spec_in_progress`; continue the next dependency or obtain consolidation. |
| Consolidated `spec-created` / `spec-updated` | Planner / requestor of its start | `spec_created` / `spec_updated`; begin Architect using the consolidated handoff. |
| `spec-review-started` | Architect / Planner | `spec_in_review`; recover active work/output before another invocation. |
| `spec-reviewed` | Architect / Planner | `spec_approved`, `spec_conditionally_approved`, or `spec_changes_requested`, derived from findings/dispositions. |
| `review-findings-dispositioned` | User / relevant reviewing or producing role | Apply actual decisions. Fix routes to producer; reconsider/clarify routes to review using recorded context. A product change is separately recorded as `user-change-requested`. |
| `spec-approved-with-justifications` / `code-approved-with-justifications` | Orchestrator / Planner or Coder | Conditional acceptance proposal for reviewed work; never silently waive must-fix. |
| `spec-approved-by-user` / `code-approved-by-user` | User / relevant producer | Apply explicit deferred-finding decisions. Reuse actual authority, and do not skip required review of changed work. |
| `user-authorization-recorded` | User / User | Preserve phase; grant, deny or defer only the described operation and bounds. |
| `coding-started` | Coder / Planner | `coding_in_progress`; requires spec acceptance and distinct explicit coding authority for current material scope. |
| `coding-revision-started` | Coder / Reviewer | `coding_in_progress`; apply current findings after relevant policy/cycle gate; retain existing in-scope coding authority. |
| `coding-updated` | Coder / requestor of its start | Interim progress; `coding_in_progress`, or `blocked` only if no approved independent work remains. |
| `coding-complete` | Coder / requestor of its start | `coding_complete`; consolidated output with required tasks/checks satisfied or explicitly dispositioned; prepare Reviewer. |
| `code-review-started` | Reviewer / Coder | `code_in_review`; recover existing work/output. |
| `code-reviewed` | Reviewer / Coder | `code_approved`, `code_conditionally_approved`, or `code_changes_requested`. |
| `user-override` | User / User | Preserve phase; apply new configuration to the pending action without discarding completed evidence. |
| `subagent-error` | Failed workflow role / original causal requestor | Preserve affected phase; record invocation, category, attempt, evidence and any actual failed helper identity. |
| `implementation-complete` | Orchestrator / User | Requires code acceptance and explicit feature acceptance; `implementation_complete`; finish checkpoint delivery, then provide squash message. |

Unlisted transitions are invalid. Feedback during an unfinished draft preserves the Planner cycle's triggering event, causal requestor and native context where supported; do not add another `spec-revision-started` or consume another repair cycle. Record the request, return an incremental output citing it, and continue the applicable artifact-version and approval path from the earliest affected artifact. Each completed logical update still requires its checkpoint. An assurance catch-up review may temporarily enter the existing review phase from the interrupted phase; successful acceptance returns to that recorded phase, while findings route through the normal loop. This return is derived from history, not another persisted state field. Changes to capability/policy do not themselves repeat completed work.

`user-authorization-recorded` defines kind (`coding`, `repair_cycle`, `external_operation`, `checkpoint_recovery`), operation, scope, decision (`granted`, `denied`, `deferred`), references, explicit limits, user statement and applicable push-attempt context. Recovery decisions use `failed_attempts` for recorded failures and `uncertain_attempts` for interrupted attempts whose outcome cannot be established. An uncertain entry retains the original started record's identity, timestamp, commit/event range, remote/branch and authorization reference, plus an `observation` explaining the uncertainty; it has no invented exit code or error summary. The checkpoint helper matches this evidence to the latest local attempt before accepting a retry. Coding authority cites the current spec review. Repair authority cites the current phase review and records additional cycles (one for a generic continue). `external_operation` can authorize an exact `accept-check-result` with the check name as scope, `accept-task-result` with the numbered task ID as scope, or explicit additional `continue-role` attempts with the original trigger ID as scope; none is implicit. Additional role attempts are bounded from the number of failures at the decision, not replenished on resume. Final completion itself records the user's acceptance, not a request for a commit message.

Validate candidate append meaning/actor/requestor/transition/payload/references before writing. Validate the complete log against schemas and replay before checkpoint or dependent work. Use `--previous` against the preceding saved log to detect history rewrites and `--workspace` to check actual document versions/history and every numbered task's completion at consolidated coding handoff. `resume-action` is read-only; it derives configuration, approval bases, findings, cycles and workflow action, then applies supplied delivery/invocation observations. Without delivery evidence it first asks to reconcile the checkpoint. No script dispatches roles, commits, pushes, repairs files, or merges.

## Checkpoints and recovery

At initialization establish feature branch, explicit integration branch, remote and baseline commit. Use the existing checkout; a feature branch does not authorize a worktree. Only Orchestrator coordinates Git. Never discard unrelated changes or include unrelated staged work. Do not force-push, rewrite shared history, create a PR implicitly, or merge into the integration branch.

Inspect both the working diff and index before staging. For wholly workflow-owned paths, stage those explicit paths and commit with `git commit --only ... -- <paths>` so unrelated staged files remain outside the checkpoint. For mixed ownership within a file, isolate the intended hunks using an appropriate index workflow, or obtain direction if they cannot be separated safely. Never use an indiscriminate `git add .` or commit the existing index without checking its ownership. Reconcile the committed paths against the actual role output before pushing.

Every completed logical update is a commit-and-push checkpoint, including initialization, requests, drafts, approvals, dispositions, overrides, code/repair updates, research/known-issue changes, review/verification results and final acceptance. Related artifacts and log output belong together. A checkpoint does not imply approval or merge readiness: describe deliberately Red/incomplete work accurately. Milestones cannot suppress update-level checkpoints. Do not trigger cloud reviews or send messages solely because the branch is remote.

Commit trailers provide correspondence without recording the commit's own hash in its contents:

```text
Orchestrator-Log: .docs/specs/example/task_log.json
Orchestrator-Events: 4-5
```

Ranges are contiguous and nonduplicated. Include multiple events only when they belong to one completed logical update; do not batch away drafts or approval gates. After commit, record local attempt identity before dispatching its push. `scripts/checkpoint_state.py` supports `inspect`, `attempt`, and `failure`; it never commits/pushes/retries. The small append-only attempt journal is found via `git rev-parse --git-path orchestrator-flow/{feature}/checkpoint-attempts.jsonl`, so `.git` need not be a directory. It stores attempts/failures, not pending workflow actions, and must contain no credentials.

On failed push, preserve the commit, record failure immediately, report it, globally pause workflow work, and obtain direction. An interrupted attempt with no recorded result also pauses work until Git establishes delivery or the user gives direction. `inspect` returns an `uncertain_attempt` suitable for recording with that decision when delivery cannot be established; it does not fabricate a failure or grant a retry. On an authorized retry:

1. Append `user-authorization-recorded` with the actual latest failed-push or uncertain-attempt context, target operation, and `max_attempts: 1`. Use `failed_attempts` for a recorded failure or `uncertain_attempts` for the interrupted started record and current observation. A later recovery decision supersedes an earlier one.
2. Validate and commit that update locally before retrying. Recovery bookkeeping is allowed during the pause; product/spec work is not.
3. Persist the attempt identity before invoking one push that delivers the outstanding work and authorization together.
4. Determine successful delivery from Git remote ancestry and commit trailers. Create no success event, success receipt, extra commit, or second push.
5. If it fails, persist the new failure locally and pause again. If it is interrupted without a known result, retain its started record and reconcile Git. The next user-directed recovery update carries the new failure or uncertainty into the task log before another attempt; citing an older attempt cannot authorize this retry.

The final checkpoint follows exactly this sequence. Once Git proves delivery of acceptance and any recovery authorization, produce the squash message with no pending receipt or extra approval. If interrupted before dispatch or after sending a push, inspect Git before repeating it. If the outcome cannot be established, ask for direction; a fresh explicit one-push authorization can permit another attempt without pretending the earlier one failed. An uncertain attempt consumes its recorded authorization and never replenishes it. Commit failures block dependent work. Push failures globally pause work even when offline tasks would otherwise be independent.

Recover running role work or completed output before dispatching a duplicate writer. Use trigger/role/attempt and native context IDs. Producers yield at coherent logical updates; resume the same delegated role context after Orchestrator checkpoints where the platform supports it. A checkpoint does not require a fresh agent or a complete project reload. New invocations receive the full role contract, effective configuration, current artifact/approval context, relevant prior output and bounded durable evidence, not the entire history by default.

For ordinary role failures, retain up to three total authorized attempts. Record each failure and retry context without duplicating completed output. At exhaustion ask for explicit direction; a bounded further allowance must be recorded. Model/usage-limit failures, including helpers, require immediate user choice; never automatically substitute. Failed-helper evidence identifies both helper and owning workflow role.

For other blockers pause the affected operation and dependencies, continue independent approved work, and record operation/task IDs, evidence, attempted remedies, dependency/independent work and required authority. Where relevant, specify request limits, retry/redirect policy, credential handling, response-body/deadline bounds and offline validation permission. One bounded authorized attempt does not imply another. Do not impose unrelated operational checklists on every task.

## Known issues and final acceptance

Orchestrator maintains `known-issues.md` from applicable unresolved deferred findings and accepted limitations. Include finding identity, practical impact, severity, disposition, rationale, references and useful workaround/revisit conditions. Distinguish future work from limitations with no planned fix. Remove fixed entries; historical/rejected findings remain in the log/Git. Known issues do not confer permission to waive a finding.

Reviewer acceptance means `code_approved` under the configured policy. Present delivered behavior, verified results and known issues for explicit user acceptance. Only that decision permits `implementation-complete`. After its successful checkpoint, provide one conventional squash message for the user to manually merge into the selected integration branch. Reflect the total final diff against the baseline, not repair chronology. Include useful grouped implementation/spec/documentation/test bullets, evidence-backed test additions/changes/removals and results, and breaking changes where applicable. Do not invent counts or list changed-file counts. Keep the message body plain text (inside a copyable code block), with useful nested bullets where needed. No agent performs the squash merge, deployment, or integration-branch rewrite.
