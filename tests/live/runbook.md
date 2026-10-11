# Agent runbook: local tests

Read this runbook and [scenarios.md](scenarios.md) privately before operating the kit. The user starts a run by submitting [prompts/master-agent.md](prompts/master-agent.md); reading or maintaining these files does not start one. This kit targets the Codex v2 contract.

## Inputs, source discovery, and run allocation

The required setup input is an absolute parent `TEST_ROOT`. Resolve the kit from the referenced master-prompt file: its parent is `prompts/`, its grandparent is `KIT_ROOT = tests/live/`, and two levels above `KIT_ROOT` is `SOURCE_ROOT`. Verify the source's `VERSION`, `AGENTS.md`, `tests/README.md`, and `.codex/skills/orchestrator-flow/SKILL.md`. A copied prompt without a resolvable source reference needs that reference before setup; do not guess another installation or checkout.

For a fresh run, inspect immediate children and choose one greater than the largest numeric `testrun-N`, or 1 when none exist. Files, directories, links, broken links, and incomplete runs count as occupied. Never fill earlier gaps or clear an occupied name. Recheck absence at allocation; if another process takes the name, advance and recheck. A different empty parent starts at 1 independently.

Resolve the parent and existing links before mutation. Every owned path must stay under the newly allocated `RUN_ROOT`, outside the workflow source, installations, older runs, and unrelated projects. Record the number and resolved paths immediately. An explicit resume request reuses its named run only after reconciling the existing manifest and actual state; it does not repeat setup blindly.

```text
TEST_ROOT/
  testrun-N/
    basic/
    basic-repo/               # basic's local bare origin
    standard/
    standard-repo/            # standard's local bare origin
    maximum/
    maximum-repo/             # maximum's local bare origin
    .orchestrator-test/       # CONTROL_ROOT, outside consumer repositories
      run.json
      decisions.md
      evidence/
      fixtures/
      report.md
```

All controller records, rendered prompts, original output captures, ad hoc scripts, synthetic fixtures, optional helper environments, and evidence belong under `CONTROL_ROOT`. Declared in-repository preservation/native-precedence fixtures and the owned remote hook are the scoped exceptions described in the scenarios. No worktrees, hosted repositories, PRs, force-pushes, merges, installation changes, or global Git changes are authorized. Use the user's existing Git identity; ask if absent rather than inventing one.

## Discover and record the environment

1. Resolve the installed linked skill and its bundled VERSION/templates. Verify real links and required Python/Git/helper dependencies. Read its entry, protocol, assurance policy, and relevant role contracts. A broken installation is a setup limit, not permission to repair personal installations during the run.
2. Inventory the actual runtime source and kit source separately if they differ. Record resolved roots, HEADs, workflow version, tracked modifications, relevant untracked files, and a sorted path/content-hash inventory. Cover the runtime files actually used, canonical linked resources, every operating file recursively under `KIT_ROOT`, and copied input hashes. Record link targets as well as resolved content. A commit hash alone is insufficient when uncommitted content runs.
3. Reuse a working helper interpreter. If needed, create one environment under `CONTROL_ROOT` and install only the skill's declared requirements there. Pass its exact interpreter path to runners. Do not add workflow dependencies to the application. Record blocked setup accurately.
4. Discover exposed native controls and supported assignments. Record requested versus observable effective settings and human limits. Keep planned capability choices private until the corresponding recommendation/gate. Do not purchase capacity, guess model IDs, or alter personal definitions.
5. Preserve the submitted human authority. Source/runtime/kit changes during a run require identifying affected evidence; do not combine mixed sources as one unchanged implementation. Deterministic results must identify the exact runtime source tested.

## Prepare bootstrap repositories

Use explicit working directories and separately checked results. Stop dependent setup after an error. Initialize or clone before repository-scoped operations, and create an initial commit before pushing.

For each project, initialize its bare remote and ordinary working checkout with `main`. Create only: a minimal `AGENTS.md` using ordinary standard-library Python/unittest conventions; `.gitignore` rules for Python caches; and all four product inputs copied to their planned feature directories as `proposal.md`. The Standard initial input belongs in `.docs/specs/line-list-project-v1.0.0/`; the other initial inputs use `.docs/specs/line-list-project/`. Subsequent directories are `unique-lines`, `output-limit`, and `ignore-case` in every project.

Do not create application source/tests, product README, workflow task logs, specs, research, or known issues. Leave `.orchestrator-flow.json` absent so P-B/P-S/P-M exercise the missing-default recommendation path. Product guidance contains no answer keys or workflow-policy overrides. Common non-application material may be shared; project-specific proposal placement can produce different bootstrap commits.

Commit only these bootstrap paths and push `main` to that checkout's own local origin. Verify each checkout's clean state, branch, bootstrap hash, and both fetch/push URLs. Record the three baselines. Setup verifies this layout and inputs; application testing belongs to the initial Flow feature. Controller-owned synthetic Git preflight fixtures, if needed for G4, stay under `CONTROL_ROOT/fixtures` and never count as feature runs.

## Feature sequence

This is the authoritative matrix. `Omit` means remove the optional explicit-branch sentence entirely from the runner prompt; do not send an empty value, `auto`, or a generated branch instruction. The expected default branch is the complete feature identifier.

| Order | Case | Project | Proposal | Feature identifier | Explicit branch selection | Starting assurance / policy | Predecessor |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | P-B | basic | `00-line-list-project.md` | `line-list-project` | Omit | Basic / `spec_user_code_auto` | Bootstrap |
| 2 | P-S | standard | `00-line-list-project.md` | `line-list-project-v1.0.0` | Omit | Standard / `spec_user_code_auto` | Bootstrap |
| 3 | P-M | maximum | `00-line-list-project.md` | `line-list-project` | `test/line-list-project` | Maximum / `spec_user_code_auto` | Bootstrap |
| 4 | U-B | basic | `01-unique-lines.md` | `unique-lines` | Omit | Basic / `spec_user_code_auto` | P-B |
| 5 | U-S | standard | `01-unique-lines.md` | `unique-lines` | Omit | Standard / `spec_user_code_auto` | P-S |
| 6 | U-M | maximum | `01-unique-lines.md` | `unique-lines` | Omit | Maximum / `spec_user_code_auto` | P-M |
| 7 | L-B | basic | `02-output-limit.md` | `output-limit` | Omit | Basic / `all_user` | U-B |
| 8 | L-S | standard | `02-output-limit.md` | `output-limit` | Omit | Standard / `spec_user_code_auto` | U-S |
| 9 | L-M | maximum | `02-output-limit.md` | `output-limit` | Omit | Maximum / `spec_user_code_auto` | U-M |
| 10 | I-B | basic | `03-ignore-case.md` | `ignore-case` | Omit | Basic / `spec_user_code_auto` | L-B |
| 11 | I-S | standard | `03-ignore-case.md` | `ignore-case` | Omit | Standard / `within_scope_auto` | L-S |
| 12 | I-M | maximum | `03-ignore-case.md` | `ignore-case` | Omit | Maximum / `spec_user_code_auto` | L-M |

Run in this order with one active feature by default. Every predecessor must be explicitly accepted and its final checkpoint delivered. Use that branch's actual tip as the successor's explicit integration branch/baseline; leave `main` at bootstrap. A blocked successor is Not run while independent projects can continue. Each feature gets a new local chat. Never reuse a completed feature's chat for another feature. The U-S replacement is the same feature, not a thirteenth product case.

All twelve features should use one ordinary Coder assignment with natural checkpoint groups. Do not force implementation phases, per-group reviews, or extra tasks. Observe unnecessary splitting against the runtime contract and keep native phased execution deferred.

## Establish chats and observe progress

Prepare the repositories first, then use `list_projects` to match their exact saved paths. If registration requires human action, ask once with the three prepared paths and continue independent preparation. Do not substitute an unrelated project or source checkout.

Use the app's native `create_thread` for each feature, with its saved project ID and local environment explicitly selected. Render [workflow-runner.md](prompts/workflow-runner.md) using the observed manifest values. The human-submitted master prompt explicitly selects `model: "gpt-6.1-sol"` and `thinking: "high"` for every top-level Orchestrator, including replacements. If unavailable, obtain direction before starting that chat. Record requested and exposed effective settings. Role/helper maps remain separate gated choices.

Record ready `threadId` and `hostId` before messaging. A queued `clientThreadId` is not a ready ID; use the platform's supported completion mechanism. Surface created-chat links as the native tool requires. Follow-ups continue the owning feature chat and omit model/effort overrides to retain the top-level setting. The master reads results; runners need no authority to message it back.

Use `wait_threads` in bounded calls of at most 60 seconds, retaining cursors. Use targeted `read_thread` requests for actual gates or evidence; progress summaries are not original native returns. Avoid repeated whole-conversation reads. Follow the [U-S recovery sequence](scenarios.md#c6-context-output-and-resumption), verifying original writer/helper liveness before replacement. A commit alone does not prove a writer stopped.

At meaningful coordination boundaries, apply [Report and closeout](#report-and-closeout) to select remaining authorized work or finish the run. An unanswered human decision does not justify an otherwise idle observation loop.

## Bounded delegated decisions

Send only fully rendered messages from [test-decisions.md](prompts/test-decisions.md) after the corresponding real gate or condition exists. Record exact delivered text, artifact versions/finding IDs/attempts, delegated provenance, and delivery reference in controller evidence. Runtime statements/rationale preserve that real provenance without inventing a human turn or schema field.

| Decision | Delegated allowance |
| --- | --- |
| Configuration | Inspect recommendations; accept valid settings or select supported scripted alternatives. Keep repository-default acceptance, initial feature acceptance, and later overrides distinct. |
| Document approval | Inspect and approve that exact conforming version, or request a concrete bounded correction. |
| Initial coding | Authorize actual approved scope after Architect acceptance; document approval alone is insufficient. |
| Findings | Request in-scope fixes and assurance-permitted lesser limitations with rationale. Never waive a demonstrated must-fix, required failure, or incomplete required behavior. |
| Specification extension | At most one extra Planner repair/Architect re-review pair per feature, after its real gate and only with concrete expected benefit. |
| Final implementation extension | At most one extra Coder repair/Reviewer re-review pair per feature under the same conditions. |
| Ordinary retry | At most one additional ordinary attempt for the selected recoverable case after exhaustion. Model/usage failures use their separate choice/wait path. |
| Checkpoint recovery | For the scripted failed/uncertain attempt, reconcile it, restore the owned fixture where applicable, then authorize exactly one recovery push. Another failure/uncertainty stops the affected case for direction. |
| Final acceptance | Inspect delivered behavior, checks, Reviewer acceptance, and known issues before explicitly accepting. A squash-message request is not acceptance. |

These are controller extensions beyond normal assurance allowances, not resets or grants for every implementation phase. No native phase exercise or intermediate-phase extension is authorized. Resume, replacement, and overrides do not replenish allowances. Unexpected scope/policy/cost/exception decisions return to the human. Missing a gate is a coverage limit; do not manufacture findings or failed repairs to reach it.

Completed nit-only reviews normally accept at every assurance and policy, retaining concise known issues without a producer round trip or extra approval. An actual user request to fix, clarify, or reconsider a nit remains binding through the existing decision/repair path; a proposed disposition or policy-only response cannot create or erase that exception. Observe naturally occurring cases without adding a nit-fix stimulus or repair allowance.

Git ownership follows the corrected runtime: Planner/Coder publish owned artifacts; Orchestrator publishes authoritative log updates; Git yields are coordinated. Ordinary Coder groups need neither a wrapper nor acknowledgement. Required handoffs contain the complete actual JSON return under the current compact schemas; irrelevant optional fields may be omitted. Follow [G3](scenarios.md#g3-drafts-versions-and-consolidated-outputs) for the single consolidated final tasks return and faithful recording. Failed checkpoint delivery globally pauses workflow work. Successful delivery creates no success receipt, extra commit, or second push. Final merging remains manual and outside this run's authority.

## Controller records and evidence

`run.json` is lightweight controller bookkeeping, not a second workflow task log or runtime schema. Record these fields as structured objects/arrays, using null or an explicit pending observation until known:

| Record | Contents |
| --- | --- |
| Run and source | Run number, resolved roots, submitted authority/reference, runtime and kit inventories, linked installation, interpreter, native capabilities, source changes. |
| Projects and cases | Project IDs, working/bare paths, case and feature IDs, copied proposal/hash, feature directory, predecessor, explicit branch selection or null, resolved branch, integration baseline, original/replacement chat IDs/hosts, and current owner. |
| Configuration | Recommendations, separately accepted defaults and initial snapshots, actual override event references and settings sequence, requested versus observed native assignments. |
| Interventions | Prerequisite/boundary, stimulus and delivery reference, owned files/index state, attempt status, consumed grants, blockers, and evidence references. |
| Defaults transition | U-B old/new file hashes and unstaged state, unchanged feature configuration, final delivered tip, and L-B's explicit adoption decision and publication checkpoint. |
| Recovery | Orchestrator/Coder continuity separately, writer/helper liveness, pre/post-replacement checkpoints, recorded override, and next affected native invocation. |
| Closeout | Actual feature states, scenario/variant results, unresolved findings, pending decisions and causes, current owners, timestamped liveness and delivery observations/limits, why no further authorized work can advance, report/evidence paths, and retention status. |

Keep `decisions.md` as the ordered record of delivered decisions and their evidence references. Preserve actual native returns before parsing, including malformed or pointer-only completion responses. An exact-return verdict requires a complete original capture with source identity; a summary, missing original, or potentially truncated capture is Unverified for that claim. Record narrower observed runtime validation separately. A saved valid wrapper is not a substitute for the original return.

Configuration evidence connects accepted values and actual override decisions to subsequent affected native use. Keep requested controls, exposed effective settings, role/context identity, and unavailable backend telemetry distinct. Do not require configuration references in invocation contexts, execution-segment events, historical model attribution, or a consumer dispatch ledger. A small reporting correction may succeed in the same assignment without a failure event; distinguish it from genuine unusable output and recorder errors under [C7](scenarios.md#c7-failure-categories-and-attempt-bounds).

Collect evidence at meaningful boundaries, including available prior log snapshots kept externally. Validate actual outputs and log updates with the installed read-only helpers; use `--previous` for genuine earlier snapshots and `--workspace` at relevant completed boundaries. Do not recreate missing original snapshots or require routine consumer snapshots. `resume-action`, checkpoint `inspect`, and `recent` use real observations. `record-handoff` is an explicit writer for the owning workflow Orchestrator, never an evidence-audit operation. Preserve failed/skipped commands and incomplete reads. See [repository validation guidance](../../AGENTS.md#validation).

Inspect both current file/index states and committed history. Distinguish product source/tests/docs, workflow Git-metadata journals, ignored caches, declared controller fixtures, and accidental scratch artifacts. Keep unexpected artifacts as evidence; do not clean them away to manufacture a clean result. Roles do not create wrapper files or consumer `.orchestrator-test` directories for the controller.

For synthetic standalone exercises, validate coherent metadata and provenance before invoking the role; document intentional defects separately. Keep all fixture writes under control storage. Standalone output is never inserted into a consumer log as live history. Native invocation evidence, not Git author names or role self-identification, substantiates publisher/helper settings where exposed.

## Report and closeout

Use [collect-evidence.md](prompts/collect-evidence.md) directly or through an explicitly authorized read-only evidence agent. It may write controller reports and evidence but cannot message runners, repair their work, or mutate histories.

At each meaningful coordination boundary, inspect the existing schedule, dependencies, actual grants, ownership, bounded liveness evidence, and remaining controller/reporting tasks:

| Observed condition | Master action |
| --- | --- |
| An authorized case or controller task can advance | Continue it under the existing sequence, dependencies, and allowances, including independent projects when another case is blocked. |
| Assigned work required for progress or closeout is active | Observe with the existing bounded waits and cursors; act on actual completion, failure, or a decision gate. |
| A helper remains active after its assigned work is finished | Resolve its owner and finish or stop it through the existing authorized native coordination path. Preserve the actual outcome; do not invent a completion return or rerun checks to obtain one. |
| No authorized work can advance, no required assigned work is active, and remaining cases need human decisions or blocked predecessors | Publish the partial/blocked report and manifest, identify pending decisions, and return a final response. Do not wait for the human in an otherwise idle execution turn. |
| All planned work has finished | Publish actual coverage/verdicts and the manifest, then return a final response. Completion does not imply all variants passed. |

Ask for unexpected direction when needed and continue independent permitted work. If that work ends before an answer arrives, close with the blocked result. Reporting is already authorized and needs no further feature acceptance or maintenance approval. Reuse valid observations with their timestamps; recheck changed or uncertain state rather than routinely rereading all chats or repeating validation. Do not add exercises, repeated status refreshes, a fixed timeout, heartbeat, scheduler, or watchdog to occupy the wait.

If liveness or a reporting prerequisite cannot be resolved within existing controls and authority, report the specific uncertainty and needed direction, including the locations and limits of records actually saved. Do not infer a writer stopped, introduce unsupported interruption, or wait indefinitely for a context with no assigned work. A commentary promise to report is not closeout: finish the permitted reporting and send the final response. These instructions do not establish or repair the technical cause of an unexplained platform stall.

Write `CONTROL_ROOT/report.md` with source identity, actual feature states, scenario/variant and role, configuration, delivered stimulus, expected/observed behavior, references, result, and limitations. Use Pass only for exercised behavior with supporting evidence, Fail for observed contract violations, Unverified for attempted but insufficiently observed variants, and Not run for unattempted cases. Retain historical failures after later success. Classify supported causes as workflow defect, harness defect, agent compliance failure, or environmental/observability limit.

Separate native workflow, standalone role, deterministic test, and inspection/inference evidence. Use the [deterministic inventory](scenarios.md#deterministic-phase-coverage) with tested source and actual results; a whole-suite pass does not establish missing cases. Mark native phases Deferred/Not run. Report pending gates, active/idle agents, delivery blockers, real branch tips, and preserved evidence. A user-requested bounded stop prevents starting additional scenarios or repairs.

The report, `CONTROL_ROOT/run.json` closeout fields, and final response must agree on accepted/delivered features, partially executed blocked cases, unattempted cases, pending decisions and their observed causes, current ownership, timestamped liveness/delivery evidence and limits, historical failures, and coverage by evidence type. Preserve product acceptance separately from workflow compliance. Use the existing records; no reporting receipts, additional summary file, or controller schema is required.

Keep the historical run-2 gates distinct: U-S's automatic approval rejection occurred before a push executed, so it was not an executed Git failure and cannot consume L-B's scripted recovery grant. L-B's runtime continuation defect was not model unavailability and does not authorize fallback or reverting its accepted effort. Any later continuation needs actual direction and source attribution; closeout neither grants it nor rewrites past evidence.

Include a concise release-summary draft in the report: tested source/version and relevant dirty content, run IDs, feature outcomes, coverage by evidence type, unresolved findings and material limitations. It must make sense without external files. The source-maintenance work later retains the actual final validation summary with release documentation before disposal. The master does not gain write authority to the workflow source or fabricate a final live-validation result.

## Run retention and eventual cleanup

Closing a run preserves its complete directory while the Orchestrator Flow feature is being implemented, validated, or investigated. A completed run or accepted sample feature does not authorize disposal.

After a run is closed and reviewed, the user may separately archive its master and feature chats and remove the three local test-project entries from the app. Keep the main `orchestrator-flow` project and all run files. Use existing app archive/project-entry controls, or explicitly ask Codex to archive the identified chats. To find archived chats, use the app's archived-chat view or ask Codex to list archived chats and restore the selected ones. To restore a removed local project entry, add/open its existing `basic`, `standard`, or `maximum` folder as a project again; do not initialize a replacement repository. Removing a project entry is not deleting its files.

After the Orchestrator Flow feature itself is explicitly accepted and merged into `main`, the user may request deletion of selected closed `testrun-N` folders in full, including working repositories, bare remotes, fixtures, and raw evidence. Retain the concise actual final validation summary in release documentation first. Use ordinary filesystem operations for the explicitly selected resolved run folders; there is no requirement to retain raw archives indefinitely or copy them into the source repository.

Archived chats remain historical records, but links to deleted files stop working and deleted runs cannot be resumed. Ordinary startup/closeout authority authorizes none of the archiving, project-entry removal, or directory deletion. Do not add cleanup scripts, automatic deletion, schedules, or project-management infrastructure. Preparing this kit performs no cleanup of existing runs.
