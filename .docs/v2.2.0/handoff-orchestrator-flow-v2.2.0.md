# Handoff: Orchestrator Flow v2.2.0

Start the next release here. It is v2.2.0 unless the task-log schema changes in a non-backwards-compatible way. In that case it becomes v3.0.0, and this folder and file are renamed during planning.

This file carries forward what a new thread needs: why v2 exists, the settled workflow behavior, v2.1.0's Claude Code decisions and the implementation boundaries. The candidate items follow. They were found or deferred while releasing v2.1.0, or carried forward from v2.0.0, and the evidence behind the v2.1.0 ones is in the [v2.1.0 native-test summary](../v2.1.0/native-test-summary.md). The last sections hold test-kit intent, lessons for running the next release, and the Claude Code platform facts verified during v2.1.0.

## Start here

- **State:** v2.1.0 was completed on `v2.1.0-claude-code-integration`. Recheck whether it has since been merged into `main` and tagged; don't assume either.
- **Reading:** this file is the only required reading. [AGENTS.md](../../AGENTS.md), which holds the maintenance rules, loads automatically in Codex and Claude Code sessions in this checkout. Everything else is for when a topic needs it: the source map at the end points to the contracts, scripts and history. The proposals, the v2.1.0 handoff and the native-test summary hold rationale, history and evidence; what they settled is summarized here.
- **Status of the items:** they are candidates for the next proposal, not an approved backlog. Settled v2 and v2.1.0 decisions aren't reopened without a concrete reason.

## Why v2 exists

The motivating example was the user's FEC bot: a private repository, running from the user's laptop, serving roughly a dozen active users on one private Discord server. An API-provider migration worked very well, but the workflow spent approximately two and a half usage allocations hardening it. Repeated Architect and Reviewer passes kept reopening the whole specification or implementation and discovering increasingly minor improvements.

That outcome was too expensive for the project's consequences. Small, recoverable bugs would have been acceptable. The purpose of v2 was to match the cost of planning, implementation, and assurance to the work, while preserving deliberate engineering and useful recovery.

The governing instruction is **“perfection is the enemy of good.”** It applies to this workflow and its maintenance just as much as to the projects it produces.

- Optimize the ordinary successful path. Resumption is important but exceptional; extra bounded reconstruction during recovery can be preferable to permanent bookkeeping on every successful operation.
- Preserve enough information for the next agent and a future resume. A perfect process audit is not a deliverable.
- The user is often available to resolve an unusual situation. Do not build a transaction framework, watchdog, permission ledger, migration system, or elaborate recovery protocol merely to remove every possible question.
- Classify findings by actual project consequences and agreed assurance. Technical complexity alone does not make a private project mission-critical.
- Maximum preserves meaningful rigorous review. It does not justify useless diagrams, duplicate reports, polishing loops for nits, or administrative ceremony.
- Simpler process does not mean vague planning. The user has seen weaker Coders produce incoherent work when too much design is left implicit. Concrete requirements, design, task targets, dependencies, and test expectations remain valuable.

The user prioritizes Codex and Claude Code. GitHub Copilot and Cursor should eventually remain usable and behaviorally consistent, but their updates need their own proposal.

## Settled v2 workflow behavior

This carries forward section 3 of the v2.1.0 handoff, updated for v2.1.0. The runtime contracts and schemas remain the exact field and event definitions; do not create a second competing schema from this summary.

### Roles, ownership, and user gates

The pipeline remains **Planner → Architect → Coder → Reviewer**, coordinated by Orchestrator. Lower assurance does not bypass a lead role or a required document. Direct standalone role use remains supported with its own supplied context; it must not invent orchestrated approvals.

| Role | Responsibility |
| --- | --- |
| Orchestrator | User interaction; configuration; branch initialization; approvals and decisions; `task_log.json`; current `known-issues.md`; log checkpoints; recovery coordination. |
| Planner | Requirements, design, tasks, optional research, their artifact checkpoints, and incremental/consolidated specification handoffs. |
| Architect | Read-only specification review at the applicable assurance. |
| Coder | Intentional implementation, test, documentation, and task-checkbox edits; artifact checkpoints; cumulative implementation handoff. |
| Reviewer | Read-only implementation review at the applicable assurance. |
| Helpers | Bounded exploration/research and execution of specified checks; concise evidence returned to their owning lead. They do not intentionally edit project files or publish checkpoints. |

Orchestrator preserves its context by using structured outputs, metadata, file names/statuses, and concise mechanical diagnostics. It does not inspect specification/research bodies, product source, tests, or patches. Delegate content questions. Since v2.1.0, open questions in the input are evidence for Orchestrator's difficulty assessment, not questions for it to ask: Orchestrator never asks the user product or requirements questions itself, and Planner returns them for routing. These are consumer runtime boundaries, not restrictions on an agent maintaining this workflow repository.

Requirements must be approved before dependent design, design before dependent tasks, and tasks before Architect review. Material upstream changes require the affected approvals in that order. Unaffected documents do not need artificial revisions or repeated approvals. Architect acceptance is separate from the user's initial coding authorization; Reviewer acceptance is separate from final feature acceptance.

Questions from delegated roles pass through Orchestrator. Use real native role delegation; do not quietly simulate the roles in the Orchestrator's own context. A platform limitation needs an explicit design/user decision, not an invisible loss of separation.

### Capability and assurance are different settings

**Capability** selects model and reasoning/effort for each of Planner, Architect, Coder, Reviewer, and helpers. Since v2.1.0, the shared schema accepts an optional `exploration_helpers` assignment for exploration and research helpers, leaving `helpers` for test and check execution; Claude Code uses it, and Codex keeps one `helpers` assignment for now. Different role assignments are intentional: a stronger reviewer than producer is valid. **Assurance** selects the feature's process/review standard and is shared across the lead roles, apart from the explicitly defined intermediate phase reviews.

Consumer-root `.orchestrator-flow.json` contains `assurance_level` and `capability_defaults`, with maps for configured platforms. It does not belong in `AGENTS.md`, because those project instructions may also be used without Orchestrator Flow.

At first setup, the user and Orchestrator establish repository defaults. For each new feature, Orchestrator recommends a complete configuration and the user accepts or overrides it. The effective feature settings are recorded in `task_log.json`; later repository-default edits do not silently change an existing feature. Accepting a feature recommendation does not silently rewrite repository defaults.

Current task-log configuration fields include `workflow_version`, `assurance_level`, `capability`, and `review_disposition_policy`. Capability records the platform, resolved role assignments, and acknowledged limitations. The current schema already recognizes `codex`, `claude-code`, `github-copilot`, and `cursor`; each assignment uses `model` and `reasoning_effort`. Native inheritance and unavailable effort controls must be represented honestly using the contract's supported conventions, with user acceptance where required.

Accepted capability changes apply **prospectively** at a coherent boundary. Preserve approved work, logical assignment, cumulative reporting baseline, context where usable, and repair allowances. A model/effort change does not invalidate useful completed or in-flight work. A helper-only change affects subsequent helpers without requiring the lead to restart.

Do not restore the rejected dispatch-provenance design: no `role-dispatch-started`, execution-segment lineage, per-dispatch configuration matching, helper capability ledger, or retrospective proof of which model produced every portion of an artifact. Use real native controls and verify supported settings when selecting/using them; prompt text claiming a model is not a native model selection. Unavailable requested settings require user direction, not automatic substitution.

The user prefers cheaper suitable helpers, such as Luna in Codex, rather than routinely using Sol for them. This is a cost preference, not a fixed cross-platform model mapping. Some live tests intentionally used different assignments to verify that accepted choices stuck. Do not copy their test settings as universal runtime defaults.

### Assurance, findings, and when to stop

Initial Architect and Reviewer coverage includes the entire relevant specification/implementation at **every** assurance. Assurance changes depth, classification, evidence expectations, and follow-up scope; it does not permit conveniently omitting a file or document.

| Behavior | Basic | Standard | Maximum |
| --- | --- | --- | --- |
| Scrutiny | Intended behavior, meaningful preservation, and obvious consequential failures; recoverable limitations can be acceptable. | Stronger robustness and regression expectations, proportionate to consequences. | Comprehensive adversarial review and active revalidation of decision-critical evidence. |
| Follow-up review | Normally focused on the repair; expand when consequences/evidence warrant. | Focused, affected, or full according to repair impact. | Comprehensive on each required pass. |
| Should-fix findings | Weigh benefit, likelihood, impact, and the entire cost of another repair/review cycle. | Normally fix; defer with concrete grounds, such as disproportionate rework or risk. | Preserve rigorous repair and justified-deferral standards. |
| Nits | Normally defer and record concise known issues. | Nonblocking; do not create polishing cycles. | Still nonblocking; address straightforward nits alongside necessary repairs only. |
| Ordinary repair allowance | One completed repair/re-review cycle before further direction. | Two completed cycles before further direction. | Existing rigorous loop and stall safeguards. |

**Completed nit-only reviews accept at every assurance, including Maximum.** The factual issue may receive a different severity at different assurance levels; what remains a nit at Maximum is still nonblocking. An explicit user request to repair or reconsider one remains binding through the ordinary decision/repair path. Nits never excuse missing required work or failed required checks.

Must-fix exceptions require actual user disposition. Do not silently weaken a requirement. Preserve findings, authority, and rationale without reopening a settled decision absent new evidence or its agreed revisit condition. Initial reviews, checkpoints, and small reporting corrections are not repair cycles.

The built-in `review_disposition_policy` is `spec_user_code_auto`: user disposition before Planner repairs, ordinary in-scope Coder repairs allowed. Alternatives are `all_user` and `within_scope_auto`. This policy is an explicit feature field, not a repository-default field. All policies preserve material document approvals, user product decisions, operational authority, loop limits, and explicit final acceptance.

An assurance increase may require additional review work before the affected gate, including when a lower-assurance initial review was already running. Capability changes alone do not create that gap. Reuse sufficient applicable evidence: unchanged Maximum work remains applicable after Maximum → Standard → Maximum. Do not infer insufficiency solely from the last override or add a new full review merely because the agent context changed.

### Deliberate planning and Red/Green remain mandatory

The user explicitly rejected combining implementation and tests into loosely defined work to save planning cost. Preserve separate Red and Green stages at every assurance. Scale the depth of tests and review instead: Basic can cover intended use and obvious edge cases without exhaustively defending every remote possibility.

Requirements describe user/product behavior with deterministic acceptance criteria. Design names concrete interfaces, ownership, data flow, invariants, and relevant decisions. Tasks identify targets, dependencies, useful verification, and requirement mappings so a lower-capability Coder does not have to rediscover the design. The existing requirement-to-task coverage structure remains; do not treat the removal of pointless diagrams as permission to omit useful traceability.

Preserve the current task categories and their boundaries: behavior-free Scaffolding where needed; test-only Red; minimum production Green with source/API documentation; production-only Refactor; optional EdgeCase pairs for hardening existing behavior; concrete Documentation; explicit final Test-Maintenance; repair-free final Verification. Planner supplies the test-maintenance strategy; a justified no-change result is acceptable.

Size Red/Green pairs around coherent behavioral changes, not one pair per assertion and not one enormous pair for the whole feature. Planner uses Markdown headings for natural groups that become Coder checkpoint boundaries. A group is not an extra state, approval, phase review, or mandatory return to Orchestrator.

Coder delegates execution of applicable tests, lint/type checks, builds, and planned manual checks to helpers. It retains intentional edits, interpretation, and repairs. Exploration helpers answer bounded source questions; reuse suitable helper contexts across related work instead of spawning one per task. Keep tested work stable and return concise commands, actual outcomes, useful counts, and exact relevant failures rather than filling Coder's context with successful tool output. Basic/Standard can reuse fresh applicable results after checking relevant changes; reporting corrections and checkbox updates alone do not require retesting. Maximum preserves its comprehensive fresh-check obligations.

Diagrams are useful only when they clarify something. They are not mandatory even at Maximum.

### Documents, versions, and handoffs

Consumer feature artifacts normally live together under `.docs/specs/{feature}/`. The user's intended use places the completed proposal/bug-report input beside its task log and specifications. Repository-maintenance documents such as proposals and this handoff belong in repository-level `.docs/` folders, not artificial consumer spec folders.

- `requirements.md`, `design.md`, and `tasks.md` are required. Each has its own integer `Content version: N` from the first draft and a final top-level `## Revision History` with useful changes and rationale.
- Do not put workflow state, approval metadata, branch names, or Git hashes into those specification documents. The task log and Git already own that information.
- **Checking off tasks does not increment the tasks content version or add revision history.** Coder changes actual completion marks only, preserving task wording, Planner provenance, and the existing approval basis. Planner owns substantive task changes.
- Routine readers exclude the final Revision History before loading content. Read all required current bodies, and recover truncated chunks without skipping content. Do not create a separate read-audit artifact.
- `research.md` is optional when useful, organized into purpose/scope, investigations/findings, open questions, and sources/references. It is a current-state research document, not a scratch dump. It has no content version, Revision History, or independent approval gate; substantive changes are reported through Planner and the log.
- `known-issues.md` captures current deferred findings/accepted limitations with enough rationale and scope to be useful. It is not a second append-only history or a requirement to fix every recorded item.

Planner returns incremental complete structured outputs at approval boundaries. Its **final tasks draft already includes the consolidated Planner handoff**: current final state, requirements/design/tasks context, material decisions and reasons, constraints, and dispositions. After unchanged tasks approval, Orchestrator can send that same return plus approval context to Architect. Do not call Planner again merely to obtain a duplicate consolidation. The handoff describes the final agreed behavior, not the conversation's back-and-forth.

Coder normally returns one cumulative completion/repair wrapper for its assignment, covering work before and after interruptions against the original baseline. Ordinary artifact checkpoints need no interim completion wrapper or Orchestrator acknowledgement. Genuine progress/blocker coordination is distinct from claiming completion.

Record actual complete native JSON, not a pointer/status object or a rewritten summary. Give each fact one place rather than duplicating inventories and test results across fields. Minor report-only omissions are corrected in the same assignment without a formal failure, new repair cycle, empty checkpoint, or automatic retest. Genuine execution failure or repeatedly unusable output still uses bounded recovery.

Normal operation creates **no temporary wrapper files or snapshots**. A concrete tool/recovery need can justify a temporary file, removed after safe recording/recovery; it must not become committed spec-folder debris. Each platform's recorder accepts the actual return once, derives metadata, and validates and reads back internally. Codex uses the shared validator's `record-handoff` command; Claude Code uses `claude_log.py record-return`, which reads the return from the subagent's transcript. The Codex recorder fixed a demonstrated Windows Unicode corruption problem without making the agent prove every transport step. Preserve explicit UTF-8 handling when adapting this behavior.

### Git ownership, checkpoints, and final acceptance

The user supplies a feature name, which may contain a version or just a description. An explicit branch selection wins; otherwise use the feature name, usually matching the spec directory. Never add a `claude/`, `codex/` or other prefix, or an invented product version. Validate the name and obtain direction for a conflict. Record the integration branch, remote, and baseline.

Use the existing local checkout. A request for a separate/fresh chat does not authorize a worktree. No agent force-pushes or performs the final merge.

| Completed update | Publisher and checkpoint boundary |
| --- | --- |
| Specification/research draft or substantive revision | Planner publishes its owned artifacts before the handoff/approval boundary. |
| Natural coding group, meaningful partial work, or completion | Coder publishes implementation, tests, docs, and actual task progress. A deliberately Red checkpoint is described honestly. |
| Authoritative task-log update, user approval/request/override, review return, disposition, or final acceptance | Orchestrator publishes the log and its related owned artifacts. Related records from one logical update may share a checkpoint. |

Each checkpoint is committed and pushed. Do not batch away distinct completed drafts or approval gates; do not commit after every file write or command. Serialize Git ownership and use coherent yields when Orchestrator needs to record an asynchronous decision during producer work. Preserve unrelated staged, unstaged, and untracked changes.

Artifact checkpoints and log checkpoints intentionally differ. A legitimate Planner/Coder commit may contain no `task_log.json`. Commit metadata identifies the feature, publisher, kind, and relevant assignment; log checkpoints identify the event range. Do not create routine checkpoint events, success receipts, or recursive commits to record successful pushes.

On a failed/uncertain push, preserve local work and actual attempt evidence and follow the existing bounded, user-directed recovery. Commit the recovery authorization before its one permitted push; successful remote ancestry proves delivery without another receipt. Other blockers pause only dependent work. Since v2.1.0, a checkpoint attempt journal counts only records on the run's own branch and remote whose commits are in the current checkpoint's ancestry, so an earlier run of the same feature can't block a rerun.

On resume, Orchestrator examines the log, native ownership/output, branch/baseline, and recent Git metadata plus changed-file names/statuses, paging further if necessary. It still does not read product/spec diffs. Coder can inspect its own checkpoints, diffs, code, tests, and task progress to reconstruct cumulative work and distinguish historical checks from newly executed checks. Do not infer old test success from a checkbox or duplicate an active writer.

After Reviewer acceptance, obtain the user's explicit final feature acceptance, record/deliver completion, and generate one meaningful conventional squash-commit message describing the complete change against the integration baseline. A request for a commit message is not acceptance. **The user manually merges; neither Orchestrator nor any other agent does it.** Maintenance commits/branches/pushes in this source repository require separate user authorization.

### Exceptional implementation phases

Phases were accepted only for unusually large features whose Coder context genuinely needs to be split. Task count or multiple checkpoint groups is not sufficient justification; no fixed threshold was agreed. Even the substantial FEC bot migration was thought unlikely to need them.

An approved phase has stable task membership and a cumulative phase return. Subsequent phases use fresh Coders; repair/recovery preserves useful context. Basic has no intermediate reviews; Standard uses Basic intermediate reviews; Maximum uses Standard. Final review always uses full feature settings.

Intermediate Reviewer capability retains the full Reviewer model and uses the agreed effort mapping `max → high`, `xhigh → medium`, `high → low`; unsupported/unmapped settings require a decision. Standard and Maximum intermediate stages have one and two repair cycles respectively, separate from final-review allowances. The final Coder owns whole-feature integration, final Test-Maintenance/Verification, the consolidated whole-feature return, and all final-review repairs, including earlier-phase code.

Claude Code's per-call efforts can express this mapping; native phase execution remains untested on both platforms. Do not silently substitute a guessed equivalent, and do not make phase infrastructure part of every ordinary feature.

### Versions and compatibility

Workflow semantic versioning is separate from integer template versions, per-document content versions, and a consumer product's version. Both reusable input templates currently have template version 2; completed proposals remove the template-version line and authoring guidance.

The initial v2.0.0 deliberately does not migrate pre-v2 or missing-version logs. Old completed features stay untouched; an unusual request to use an incompatible log stops for explicit user-directed handling. The discarded prerelease shapes from disposable tests also did not justify a migration framework.

**Future patch/minor readers must keep supported older logs valid and usable.** A v2.0.0 or v2.1.0 log should keep working under v2.2.0 without inventing prior user decisions. Compatible additions need documented reasonable defaults when absent. Old readers need not understand new logs. Incompatible structural/semantic changes require a major-version decision and an explicit migration-or-breaking-change discussion.

v2.1.0 added Claude Code without breaking 2.0.0 logs (see "Settled in v2.1.0"). The next release is v2.2.0 unless it changes the log schema incompatibly; then it becomes v3.0.0 and needs that discussion. A canonical VERSION bump reaches both integrations through their symlinks, so compatibility matters even when a change is platform-specific.

## Settled in v2.1.0: the Claude Code integration

The [v2.1.0 proposal](../v2.1.0/proposal-orchestrator-flow-v2.1.0.md) records the reasoning; these are its decisions as implemented. Like the v2 behavior above, they aren't reopened without a concrete reason.

- **Installation:** two user-level links, `~/.claude/skills/orchestrator-flow` and `~/.claude/agents/orchestrator-flow`, as subfolders beside the user's other skills and agents. A venv inside the skill runs every workflow script; only the startup check uses `python3`.
- **Start:** the user types `/orchestrator-flow`, because the skill sets `disable-model-invocation`. A request in other words that Claude follows by hand asks once, before the run starts, then runs as if invoked.
- **Startup check:** every invocation, including a resume, checks:
  - the running Claude Code version, read from `$CLAUDE_CODE_EXECPATH`, against a minimum of 2.1.296
  - the venv
  - environment overrides that defeat per-call model or effort
- **Roles:** the main conversation is Orchestrator, on the session's own model. Planner, Architect, Coder and Reviewer are real `flow-*` subagents with Claude-native contracts. Each starts in the background, never as a fork, with the accepted model and effort passed on every call. Models are short names such as `opus`, `sonnet`, `haiku` or `fable`. Start prompts open with `Orchestrator-Feature` and `Orchestrator-Invocation` lines.
- **Capability:** separate from assurance, as in Codex. Orchestrator recommends settings per feature, with a reason for each, and the user accepts or overrides them. The starting repository defaults are:
  - Planner: opus/xhigh
  - Architect: opus/max
  - Coder: opus/high
  - Reviewer: opus/max
  - `exploration_helpers`: sonnet/medium
  - `helpers`: haiku/medium
- **Helpers:** `flow-explorer` and `flow-runner`, started by their lead. Explorers use `exploration_helpers` when it's set and `helpers` otherwise; runners use `helpers`. Under a background lead, helpers run asynchronously: the lead ends its turn while it waits, and the hand-back wakes it.
- **Recording:** the Claude-only `claude_log.py`:
  - records role returns straight from subagent transcripts (`record-return`), and runs before every message to a lead
  - validates Orchestrator's own entries (`append-entry`)
  - finds a lead's agent ID from its start-prompt lines (`find-agent`)

  Notice text is never copied into the log.
- **Continuation and resume:** leads are continued by agent ID with SendMessage, across approvals and repairs, while their model and effort still match. After an interruption, the user resumes the same session and runs `/orchestrator-flow` again. A lead whose helper was lost with the session is continued by message and reruns that work with a fresh helper.
- **Runtime:** Claude keeps its own copy of the shared runtime, byte-identical to Codex's and enforced by a parity test. Contracts and the Claude-only scripts stay platform-specific.
- **Permissions:**
  - Auto mode is recommended; acceptEdits with the README's allow rules is the alternative.
  - Headless `-p` runs aren't supported.
  - The workflow never changes the session's mode.
- **Versioning:** 2.1.0 is additive. 2.0.0 logs stay valid, an absent `exploration_helpers` keeps its 2.0.0 meaning, and Claude logs record `platform: "claude-code"`.
- **Rules tightened by the native tests:** the initial task log and repository defaults are created with the Write tool, never a shell redirect or heredoc. The two changes that apply to both platforms, no product or requirements questions from Orchestrator and run-scoped checkpoint journals, are in the v2 behavior above.
- **Not in scope:**
  - no Copilot or Cursor changes
  - no runtime shared by reference
  - no headless operation
  - no migration of pre-v2 Claude logs
  - Windows not yet covered (item 11)

## Implementation boundaries

The first v2 implementation attempted to make other platforms load shared files from the Codex integration and gutted much of their substantive native guidance. The user rejected this. Those platform folders were restored, and v2.0.0 was intentionally completed for Codex only. v2.1.0 then added Claude Code with its own native contracts and runtime copy.

The implementation also built export/copy/materialization machinery and treated links as text pointers. That was based on the wrong installation model. The user clones this repository and symlinks the integration into the relevant tool's configuration. There is no exported product package to build or deploy.

Preserve these boundaries:

- Each integration owns its substantive native instructions and runtime resources. No integration loads another's files, and there is no generic shared orchestration runtime: the shared runtime files are byte-identical copies in each v2 integration, checked by `tests/test_runtime_parity.py`.
- Required canonical `VERSION` and template resources are exposed through real relative symlinks within the integration, stored by Git as mode `120000`. No flattened-pointer parser, parent-directory search, consumer-product VERSION fallback, or export fallback. Each platform's layout and installation follow its verified native support.
- Required runtime utilities belong with the integration that executes them. The validation/replay, document-reader, handoff-recorder and checkpoint helpers, and Claude Code's startup check and log writer, are functional runtime support, not an installation framework. Do not remove useful helpers merely because the exported-package approach was rejected.
- Development tests belong under repository-level `tests/`, not in a symlinked skill directory. The live test kits belong under `tests/live/`, not release proposal folders.
- `Directives/codingAgentDirectives.md` remains reusable, project-owned coding guidance outside the integrations. Users copy/customize it as appropriate. Workflow policy must not be added to that general document or imposed through an automatically loaded distribution copy.
- README explains what the repository provides and how to use it. Do not narrate “part-2 corrections,” plans, revision tracking, or implementation minutiae in operational guidance. Do not add release-folder READMEs or validation-report documents merely for ceremony.
- Retain meaningful behavioral, schema, and actual linked-resource tests. Export/materialization tests, extra symlink-creation/clone exercises requiring special privileges, broad distribution infrastructure, and wording-only tests were rejected or removed. Tests that validate literal instructions do not establish native agent compliance.

## Before the next release

1. **Watch the next real Codex run.** v2.1.0 changed two parts of the shared runtime:
   - the optional `exploration_helpers` assignment
   - checkpoint journals scoped to the current run (`run_attempts` in `checkpoint_state.py`)

   Only the development suite exercised these on Codex. The decision was not to run a separate Codex test before release, because the next release will be validated anyway. If either change misbehaves in a real Codex run first, ship a v2.1.1 fix.

   v2.1.0 also moved the Codex live kit to `tests/live/codex/`, with its inputs shared in `tests/live/common/proposals/`. Its master now finds the source checkout three levels above the kit, and the next Codex run of the kit will be the first real use of that discovery. If it fails, fix it in v2.1.1 too.

## Workflow and contracts

2. **Shapes of Orchestrator's own log entries.** In the first native run, Orchestrator couldn't find an example of what to pass to `claude_log.py append-entry` for its own events.
   - It read the references with `cat` and ran 11 inline Python scripts against `common.schema.json` and `task_log_schema.json` to learn each event's `details`.
   - One entry was refused ("Final acceptance must disclose current known issues") before a corrected retry.
   - `references/examples/` holds only role returns and repository configuration.

   Give Orchestrator a reference or examples for every event it records. If the clearest fix changes the schema itself, the release becomes v3.0.0.

   The checkpoint helper has a related gap. Neither recovery contract names `checkpoint_state.py attempt --authorization-event <event-id>`, which an authorized push retry needs. Without it, the helper refuses with "Previous delivery failed/is uncertain; obtain recovery direction", which could send Orchestrator back to the user for an authorization it already has. `failure`'s required flags are likewise documented only by `--help`. Until the v2.1.0 README cleanup, the README held the only list of these flags.
3. **Prompts in acceptEdits mode.** The same `cat` reads and inline scripts match none of the documented allow rules, so in acceptEdits mode each one would prompt; auto mode was unaffected. Item 2 should remove most of them. The contracts could also steer Orchestrator to the Read tool, which the README's `Read` rules already cover.

## Claude transcript recorder (`claude_log.py`)

4. **Helpers that finish without a peer hand-back.** `pending_helpers` treats a helper as finished only when its hand-back arrives as a peer message. If a helper finished some other way *and* its lead's report were malformed, the recorder would read the lead as still waiting. Orchestrator would then wait instead of asking for a correction. All 11 helpers that finished in the native runs handed back as peer messages. Consider also checking the helper's own transcript for a finished run.
5. **The coordinator-message reset.** A coordinator message clears the pending-helper list, because helpers lost with an interrupted session never hand back. If Orchestrator messages a lead while it waits, and the lead replies in plain text before its helper hands back, `record-return` reports `report_not_json`, and a stray correction request can follow. It's recoverable, since the lead just says it's still waiting. A precise fix needs a way to tell a resume from an ordinary message, or to see whether a helper is still alive.

## Shared runtime

6. **Cost of the journal filter.** `run_attempts` runs one `git merge-base --is-ancestor` for each journal record on the run's own branch. That's fine at today's journal sizes; batch it if journals grow large.

## Testing

7. **A Claude version of the live test kit.** The short [Claude native test](../../tests/live/claude/README.md) is the starting point. Codex's design, where a master session holds the user's delegated authority and answers each Orchestrator's dialogs, doesn't carry over. A probe on 2026-10-16 found:
   - another session's message can't answer an open AskUserQuestion dialog; it queues behind it
   - the tool for stopping a session's turn refuses while that session waits for the user
   - a slash command runs only when it's the CLI's opening prompt, not when it's a desktop session's opening prompt or a message

   The options:
   - the user answers the dialogs, with features possibly launched in CLI tabs by a master session
   - a contract option to ask in plain text when the user has delegated decisions, then a test of whether Orchestrator honors labeled delegated decisions
   - an Agent SDK host program that answers dialogs in code, if the SDK supports that, which hasn't been checked
8. **Not yet covered natively.** No native run has shown these yet, though most have deterministic tests. The [Claude native test](../../tests/live/claude/README.md) can cover several of them in its next run:
   - the `flow-explorer` helper, which neither native feature needed
   - the plain final-message report form, because every return used SubagentHandback
   - a tool call interrupted inside a lead after a resume, the Claude Code 2.1.296 fix; in run 2 the Coder was waiting, not mid-call
   - `find-agent` choosing between two sessions' leads with the same feature and invocation; run 2 got a different invocation from run 1
   - the desktop app as the workflow host, since both native runs used the CLI
   - an Opus Orchestrator after the step-4 checklist fix; before it, Opus left out the per-choice reasons until asked
   - a confirmed start through context compaction: whether a `SKILL.md` that Claude followed by hand holds up as well as an invoked skill, and whether the confirmation is still never asked twice

9. **Codex live-kit issues deferred from v2.0.0.** The [v2.1.0 handoff](../v2.1.0/handoff-orchestrator-flow-v2.1.0.md) (§7) kept these from v2.0.0's third run for the next significant workflow change. v2.1.0 only moved the kit.
   - Fix the deliberate push-rejection hook so it accepts the workflow's paragraph-separated checkpoint trailers, and preflight it against a real checkpoint commit. This is a harness defect.
   - State that a successor's eligibility follows actual acceptance and delivery, not a historical protocol Fail.
   - Set out the local push destinations and their standing scope in the setup the user authorizes, so delegated pushes don't ask repeatedly.
   - Keep these as observations:
     - Git exit codes invented after a tool refusal
     - the Maximum Architect's disagreement between its startup and status signals
     - the missed in-flight Reviewer override, which stays Unverified
10. **Codex coverage still open from v2.0.0** (v2.1.0 handoff §6.2):
    - The full Maximum feature sequence wasn't validated.
    - Native exceptional-phase execution remains deferred.
    - The deterministic inventory has gaps around some intermediate effort mappings and the Maximum two-cycle intermediate boundary.

    Choose proportionate coverage. A full matrix isn't the default response to every kit fix (see "Test-kit intent").

## Platforms

11. **Windows.** Claude Code setup on Windows, and a native test from PowerShell, aren't covered yet.
12. **Copilot and Cursor.** Their v2 updates remain deferred, as set out in `AGENTS.md`.

## Test-kit intent

The live kits exercise real native agents on a small Python line-list CLI. They are compliance and behavior observation kits, **not benchmarks of which model or assurance is fastest or best**. They test acceptance of recommendations, deliberate supported overrides, and whether the selected settings govern subsequent work. They don't manufacture product bugs to make every row green.

The next paragraphs describe the managed Codex kit in [tests/live/codex](../../tests/live/codex/README.md): an overview, runbook, scenario catalogue and six prompt files. Its four product proposals live in [tests/live/common/proposals](../../tests/live/common/proposals/README.md), beside the Claude native test's proposal. The kits were intentionally moved out of release `.docs/` folders.

The user supplies one parent test folder. Allocate the next unused `testrun-N` there, with all working repositories, local bare remotes, and evidence inside that run. A fresh empty parent starts at `testrun-1`; occupied/incomplete entries are not overwritten. Working repositories are named `basic`, `standard`, and `maximum`, with corresponding `basic-repo`, `standard-repo`, and `maximum-repo` local bare remotes. A working Git repository and initial commit must exist before its first push; cloning the prepared local bare repository is also a valid setup approach.

Setup provides ordinary project guidance, ignore rules, and proposal inputs only. **The initial application itself must be built through Flow in all three projects**, followed by unique lines, output limit, and ignore case: four proposals times three assurance cases. Each proposal is copied into its own `.docs/specs/{feature}/proposal.md` beside that feature's later log/specs. Private controller stimuli and expected results stay outside the product proposals and runner context.

Use one new chat per feature. A planned fresh-context replacement continues the same feature; it is not a new feature or permission to reuse a completed feature's chat. This is the user's practice and a test-kit requirement, **not a requested runtime prohibition on ever reusing a chat**.

Successors start from the accepted/delivered predecessor branch tip as their explicit integration baseline. `main` remains at bootstrap; the kit does not merge features. Independent projects may continue when another predecessor chain is blocked.

The human-submitted master prompt delegates setup, native chat creation/messaging, normal scripted workflow decisions, and evidence collection within the disposable scope. The master selects supported capability choices after actual Orchestrator recommendations; exercise both accepting a recommendation unchanged and overriding it. Master and top-level Orchestrators used GPT-6.1 Sol High to control cost; lead/helper assignments vary deliberately. These are Codex test choices, not Claude model defaults.

Keep controller evidence under run-level `.orchestrator-test/`, outside consumer repositories. Controller helpers do not count as workflow-role helpers. Unrelated staged/unstaged/untracked fixtures belong only to their assigned scenario and must be identified as intentional; the three projects do not all need identical injected disturbances. Do not record controller-only actions as invented feature events.

Reports distinguish accepted product delivery, protocol observations, actual native role returns, deterministic tests, and inference. Use Pass/Fail/Unverified/Not run honestly. A later success does not erase a historical failure, but a historical failure does not automatically prevent an accepted product from being used. Close out when no authorized work can advance, identifying pending human choices separately from technical blockers; do not leave the master idle indefinitely or repeatedly poll unchanged state.

Do not require another full matrix as the default response to every small kit fix. Native phases remain deferred unless specifically selected for future testing. Claude Code has its own short [native test](../../tests/live/claude/README.md) rather than a reproduction of Codex's chat and project orchestration; item 7 covers a fuller Claude kit.

## Lessons for running the next release

- **Carry the baseline forward.** "Why v2 exists", the settled v2 behavior, "Settled in v2.1.0", the implementation boundaries and the test-kit intent all still apply. Don't reopen settled decisions. Perfection is the enemy of good.
- **Test natively early, and compare runs.** Three contract assumptions failed only on real runs:
  - the symlink allow-rule behavior
  - helpers running asynchronously under background leads
  - a model following `SKILL.md` by hand when a slash command didn't run as one

  Comparing run 1, which passed an explicit `run_in_background: false`, with run 2, which omitted it, is what separated platform behavior from model behavior.
- **Verify documentation claims natively** when users will follow them. Part D confirmed the README's auto-mode `Read` rules this way.
- **Keep review separate from implementation.** A review thread that checked every diff and claim against the files and transcripts caught a confirm-first condition that would have fired on every typed run, and a misread finding.
- **Messages between threads need care.** They're delivered only when the receiving thread's turn ends, and can't be recalled once queued. Agree on the content before sending; "yes, but…" is still discussion. A hold must arrive before the work starts. In this release, a reorganization was done, undone and redone because a hold and an undo were queued behind work already under way.
- **Commit shared files in order.** When several pending changes touch the same files, commit them in order and apply later edits only after the earlier commit. Then no commit links to a file that doesn't exist yet.

## Reference: Claude Code platform facts

These were verified natively during v2.1.0, on CLI 2.1.300 to 2.1.304 and the desktop app's 2.1.299.

### Transcript structure the recorder relies on

Items 4 and 5 rely on these, which were checked on real transcripts.

- **Where a run starts:** at a user prompt that isn't `isMeta`, or at an `isMeta` user record whose `origin.kind` is `coordinator` (a SendMessage continuation) or `peer` (a helper's hand-back). Harness nudges are `isMeta` with no `origin`.
- **How a message is recorded:** one record per content block, all sharing `message.id`. The final record carries `stop_reason: "end_turn"`, while `max_tokens` marks a cut-off.
- **Hand-backs and refusals:** a SubagentHandback's tool result is `{"success": true, …}`, and refusals set `is_error`.
- **Async helpers:** the launch's tool result carries `toolUseResult.status: "async_launched"` and the `agentId`. The hand-back arrives with `origin.from` set to that ID.
- **Large outputs:** tool results over 50,000 characters are saved to the session's `tool-results/` folder, and the model gets a 2 KB preview.
- **Background notices:** the desktop app XML-escapes their text. The CLI delivers them as `<task-notification>` entries in `queue-operation` records.

### Skills, permissions and resume

- **Skills:**
  - `${CLAUDE_SKILL_DIR}` expands to the link path, `~/.claude/skills/orchestrator-flow`, not the checkout.
  - An inline `` !`…` `` command that matches `allowed-tools` runs pre-approved.
  - `disable-model-invocation` hides a skill from the model, but not its files.
- **Permissions:**
  - A read through a symlink is allowed only when both the link path and the resolved path match allow rules. Separate rules may match each one.
  - Narrow `Read` rules suppress the out-of-project read prompt in both acceptEdits and auto mode. That prompt's "keep allowing" and "block … from now on" options are both permanent, and both apply to every read outside the project.
  - Bash allow rules match the command text as written.
- **Resume:** `claude --resume` keeps the session ID. Background agents cut off when a session ends aren't restarted, so a lead's lost helpers never hand back.
- **Commit attribution:** Claude Code's `attribution` setting controls the Co-Authored-By trailer. `false` hides all attribution on 2.1.281 or later; earlier versions reject it and skip the settings file that holds it. The object form, with empty `commit` and `pr` strings and `sessionUrl: false`, also works on older versions.

## Source map

| Read when needed | Source |
| --- | --- |
| Maintenance boundaries, layout and validation | [AGENTS.md](../../AGENTS.md) |
| User-facing setup and behavior | [README.md](../../README.md) |
| Proposal format | [Proposal template](../../templates/proposal-template.md) |
| Codex entry and contracts | [SKILL.md](../../.codex/skills/orchestrator-flow/SKILL.md), [references](../../.codex/skills/orchestrator-flow/references/) |
| Claude Code entry, contracts and agents | [SKILL.md](../../.claude/skills/orchestrator-flow/SKILL.md), [references](../../.claude/skills/orchestrator-flow/references/), [agents](../../.claude/agents/orchestrator-flow/) |
| Shared runtime, byte-identical in both skills | Each skill's `scripts/` and schemas, enforced by `tests/test_runtime_parity.py` |
| Claude-only runtime | `check_claude_code.py` and `claude_log.py` in the Claude skill's [scripts](../../.claude/skills/orchestrator-flow/scripts/) |
| Development tests and their limits | [tests/README.md](../../tests/README.md) |
| Live test kits | [tests/live](../../tests/live/README.md): `codex/`, `claude/`, `common/` |
| History and rationale | [.docs/v2.0.0](../v2.0.0/) (v2 proposals, corrections, test kit) and [.docs/v2.1.0](../v2.1.0/) (Claude proposal, the v2.1.0 handoff with v2.0.0's test history, native-test summary) |
