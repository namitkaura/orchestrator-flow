# Agent runbook: v2.0.0 local tests

The master agent reads this file. The user starts it with [prompts/master-agent.md](prompts/master-agent.md); all further message text is in separate [prompt files](README.md#other-prompts). This runbook does not start tests when read during repository maintenance.

## Inputs and layout

The only required setup input is an absolute parent `TEST_ROOT`. Allocate a new `RUN_ROOT` as `TEST_ROOT/testrun-N`, with N starting at 1 and advancing for each subsequent fresh run. The working names are fixed: `basic`, `standard`, and `maximum`; their bare remotes are `basic-repo`, `standard-repo`, and `maximum-repo`. Infer the source checkout from this kit's location and resolve the installed skill through its existing symlink.

```text
TEST_ROOT/
  testrun-1/
    basic/                   # working repository
    basic-repo/              # bare origin
    standard/
    standard-repo/
    maximum/
    maximum-repo/
    .orchestrator-test/       # CONTROL_ROOT for this run only
      run.json               # paths, accepted settings, chat IDs, progress
      decisions.md           # delegated decisions and delivery references
      evidence/              # captured outputs and per-scenario observations
      fixtures/              # standalone exercises and private answer keys
      report.md              # this run's coverage/results
  testrun-2/                 # next run, with the same complete structure
```

Inspect immediate children of the parent and choose one greater than the largest existing numeric `testrun-N` name, or 1 if none exist. Any file, directory, or link with that name counts as occupied, including an incomplete run or broken link. Never fill an earlier numbering gap or clear/reuse an existing run for a fresh request. Check absence again when allocating the directory; if another process takes that number, advance and recheck before proceeding.

Numbering is local to the selected parent. A different empty `TEST_ROOT` starts at `testrun-1` even if another parent already contains many runs. Do not maintain a global counter or consult another test root to allocate this one's number.

Resolve the parent and any existing links before mutation. The new run container must remain beneath that parent, and all six repository paths plus `CONTROL_ROOT = RUN_ROOT/.orchestrator-test` must remain inside the selected run. They must not resolve into the workflow source, an installation, another run, or an unrelated project. Record the allocated number and resolved paths immediately. All artifacts, optional helper environments, prompts, fixtures, and evidence belong to this run container; do not create a shared evidence directory in the parent.

Only an explicit request to resume an existing run permits reuse of its recorded manifest and owned paths. Inspect that state before continuing; do not rerun initialization blindly. No deletion, reset, or history rewriting is part of either mode.

Do not create worktrees, hosted repositories, PRs, installations, or global Git changes. Git writes are authorized only in the six selected test locations. Use the user's existing Git identity; ask if it is missing rather than inventing one.

## 1. Discover and record the environment

1. Read the current skill entry, workflow protocol, assurance policy, and the relevant role contracts. They govern the consumer runs. Read [test-scenarios.md](test-scenarios.md) privately as the test operator; do not feed its answer key to the workflow roles.
2. Record source checkout, HEAD, and a content fingerprint including the uncommitted/untracked runtime files actually used. Record client/native tool availability and the installed skill's resolved location/version. Keep the source frozen during each run. If it changes, identify affected results instead of silently combining two implementations.
3. Verify Python/Git and linked resources. Reuse a Python environment where the workflow dependencies work. If necessary, create one environment under the control directory and install only the skill's declared requirements there, once; pass its interpreter path to every runner. Do not add those dependencies to the sample application. Report a blocked install accurately.
4. Discover available native model/effort controls and any user-supplied limits. Leave role/helper selections pending the real Orchestrator recommendation and delegated decision; do not prefill the runner's initial prompt with a test capability map. Keep the scenario's intended choices private until the corresponding gate. Pass through actual human-supplied constraints or explicit assignments. Do not purchase capacity or guess unavailable model IDs.
5. Record the user's delegated test authority. Each test Orchestrator recommends supported repository defaults when absent, then feature settings based on the input and defaults. The master reads the recommendation and makes the scenario's decision: U-B accepts the recommended capability map unchanged when valid; U-S explicitly selects at least one different supported role assignment before initialization. U-M can accept or select supported alternatives within scope. Use a small mix across these choices and the later scripted overrides to exercise `planner`, `architect`, `coder`, `reviewer`, and `helpers`, including assignments differing from the parent where available. Do not force a common map across runs or search for the best-performing map. A capability override never changes assurance implicitly. `platform_default` is accepted inheritance, not proof of an unavailable explicit assignment; record disclosed limits and concrete settings when exposed.

Store a small `CONTROL_ROOT/run.json` outside the consumer repos with the allocated run number and resolved paths, source fingerprint, Python path, each lane's saved project/chat IDs, feature branch/baseline, and scenario progress. Record each feature's capability map when actually selected at its configuration gate; identify unresolved settings as pending. This is controller bookkeeping, not another workflow task log or a new runtime schema.

## 2. Build one baseline and seed three repositories

Perform setup sequentially so all lanes receive the same verified baseline. Shell commands must use explicit working directories and separately checked exit codes; stop dependent setup on a failure. A plain `git -C` does not initialize a repository.

1. Initialize the allocated Basic bare remote with initial branch `main`, then clone it to the allocated Basic working directory. An empty-clone warning is expected. On an explicitly resumed setup, inspect which of these operations already completed before continuing.
2. Implement [00-line-list-project.md](proposals/00-line-list-project.md) once in this clone as ordinary setup, using a bounded setup subagent if useful. Include the CLI, meaningful baseline tests, README, minimal project coding guidance, and an appropriate `.gitignore`. Do not activate Orchestrator Flow for this seed-building step or manufacture a task log.
3. Copy the four completed proposals to `.docs/inputs/` in the seed repository. Keep operator prompts, scenario expectations, controller records, and seeded defects outside it. The completed proposals have no template instructions or template-version lines.
4. Run the baseline tests, verify the CLI behavior, and inspect the diff. Commit the baseline with explicit paths and push `main` to its local origin. Record the resulting seed commit. Do not push an unborn branch before the first commit exists.
5. Initialize the Standard and Maximum bare remotes. Push the verified seed repository's `main` directly to each new local remote as `main`, then clone each into its designated working directory. This gives all three the same seed commit and each clone its own origin. Never substitute the Basic origin for the other lanes' configured remotes.
6. Verify each repository is clean, on `main`, at the same seed commit, and has only its intended local origin. Verify the baseline tests in the two new clones. Check both fetch and push URLs. Record evidence without repeating application development.

Leave `.orchestrator-flow.json` absent initially so the native workflow's setup/default recommendation path is exercised. Each runner recommends its settings before the master selects the scenario's assurance and capability map through real decisions. Repository-default acceptance and feature-specific choices have explicit separate scopes. The sample repo's `AGENTS.md` should contain normal coding guidance, not test answers, special bypasses, or a competing copy of workflow policy.

## 3. Establish local test chats

Use the Codex app's project/chat tools, not an Orchestrator subagent acting as another top-level workflow. The master and runner chats are separate contexts; each runner has its own local repository workspace and can delegate to its normal role subagents.

1. Call `list_projects` and match the exact prepared repository paths. Do not guess project IDs.
2. If any repositories are not saved projects, finish setup and ask the user once to add those prepared working folders to Codex. The available chat tools do not register new project folders. Re-list after that step. Do not silently substitute a projectless workspace or the source checkout.
3. Create one local chat per lane using its returned project ID and [workflow-runner.md](prompts/workflow-runner.md). Select the local environment explicitly; never a worktree. The human's master prompt explicitly selects GPT-6.1 Sol with High reasoning for every top-level test Orchestrator: pass `model: "gpt-6.1-sol"` and `thinking: "high"` to the native chat-creation tool, including for replacement chats. If unavailable, report and obtain direction before starting that chat. Role/helper settings come from their separately accepted feature map.
4. Save each ready `threadId` and `hostId`, the selected top-level model/effort, and any exposed effective-setting evidence in the control manifest. A queued client ID is not a ready thread ID; use the platform's completion mechanism before calling tools that require the latter. Surface created-chat links to the user when the tool provides them.
5. Run one lane at a time by default to bound usage and simplify evidence collection. The user may explicitly request concurrent lanes. Stop or finish existing work before starting another writer in the same repository.

The human-submitted master prompt explicitly authorizes creating these test chats and messaging them. Each initial prompt carries that authority and the bounded delegated-decision policy. The master may send subsequent feature prompts and decisions to these same chats, preserving the top-level Sol High setting by omitting model/effort overrides on follow-up messages. The runners need not message the master: it reads their output.

Use bounded `wait_threads` calls (up to 60 seconds), carrying cursors forward; use `read_thread` for the specific output needed at a gate. Avoid repeatedly rereading entire conversations or polling unchanged state. The master owns observation and decisions, not the runner's implementation or task log.

## 4. Drive real gates with bounded delegated decisions

Render messages from [test-decisions.md](prompts/test-decisions.md) only after the corresponding actual output or condition exists. Record the message, its user-delegated provenance, exact target versions/finding IDs/attempt, and delivery reference in the control directory. Orchestrator records that real communicated decision under the existing schema, including the delegation explanation in its statement/rationale. No fabricated human turn or new schema field is needed.

| Decision | Master may do within this test scope |
| --- | --- |
| Settings | Respond to the Orchestrator's actual recommendation by accepting or choosing supported alternatives for the scenario. Distinguish repository defaults from feature selections; record the decision before Planner starts. Later overrides are limited to the scripted changes. |
| Artifact approval | Read the returned current artifact; approve that exact version only if consistent with the proposal and delivered test decisions. Return a concrete bounded correction otherwise. |
| Initial coding | Authorize the actual accepted scope after Architect acceptance. Do not infer authority from spec approval. |
| Finding disposition | Request in-scope fixes; retain lesser issues only with assurance-appropriate rationale. Do not waive a demonstrated must-fix, a failed required check, or incomplete required behavior. |
| Extra repair | Grant at most one additional repair/re-review pair per phase per feature after a real cycle gate. Further exhaustion stops that scenario and is reported; do not reset counts. |
| Ordinary role retry | Respect the normal limit. Grant at most one additional ordinary attempt for a recoverable failure; model/usage failures require a separate supported assignment/wait decision. |
| Failed push | After the scripted failure and restoration, grant one push for the exact latest failure/uncertain attempt. An unexpected second failure stops the affected run for direction. |
| Final feature acceptance | Accept only after inspecting actual delivered behavior, required checks, Reviewer acceptance, and known issues. A request for a squash message is not acceptance. |

Do not automatically approve every return. If scope, policy, account cost, or a must-fix exception is outside this table, collect the evidence and refer the decision to the human. Do not repair the source workflow during tests. Failures should produce a useful report, not a new implementation project.

A gate that is never reached stays unverified. Never manufacture failing repairs, retroactive approvals, or fake subagent errors to reach it. Where a controlled standalone example can cover role behavior economically, use it and label that evidence accurately.

## 5. Run sequence

| Run | Repository | Proposal | Starting assurance / policy | Purpose |
| --- | --- | --- | --- | --- |
| U-B | Basic | `01-unique-lines.md` | Basic / `spec_user_code_auto` | Core flow, proportionate review/remediation, accepting recommended capabilities unchanged (C1-A). |
| U-S | Standard | `01-unique-lines.md` | Standard / `spec_user_code_auto` | Standard contract enforcement, selecting alternative initial capabilities (C1-B), context/evidence continuity. |
| U-M | Maximum | `01-unique-lines.md` | Maximum / `spec_user_code_auto` | Comprehensive obligations and full native role handoffs. |
| L-B | Basic | `02-output-limit.md` | Basic / `all_user` | Draft changes, approval preservation/invalidation, capability overrides, failed-push recovery. |
| I-S | Standard | `03-ignore-case.md` | Standard / `within_scope_auto` | Helper evidence, changed assumptions, assurance escalation during review, overrides/resume. |

The master expands the runner prompt with actual paths and branches. Suggested feature IDs are `unique-lines`, `output-limit`, and `ignore-case`; branches use `codex/` and are created by the feature's Orchestrator. After a feature is accepted and delivered, start its successor from that feature branch's actual tip, explicitly selecting it as the successor's integration branch/baseline. Leave `main` at the seed. Do not merge merely to prepare the next feature.

Apply the timed stimuli and remaining targeted checks in [test-scenarios.md](test-scenarios.md). Watch the actual review-start signal before attempting an in-flight override; a completed review followed by an override is a different case. Missed timing is reported honestly, not repaired by rewriting timestamps.

For a resume scenario, first ensure the prior runner is idle or explicitly stopped with its role liveness known. Resume the existing chat normally. To test a genuinely fresh context, create a new local chat for the same saved project using [resume-run.md](prompts/resume-run.md), with the human's scoped authorization preserved. Do not create duplicate active writers.

## 6. Collect evidence and finish

Use [collect-evidence.md](prompts/collect-evidence.md) in the master context or an explicitly authorized read-only evidence subagent. It may inspect this run's test chats and artifacts; it must not alter consumer history, collect another run's results as this run's evidence, or claim that a role's self-report proves an action.

For each actual logical update, preserve the previous log snapshot when feasible and validate the new log using `--previous`. Use the workspace check at appropriate completed boundaries, and the read-only resume/checkpoint helpers with real observations. A missing previous snapshot is a limit on append-only evidence, not permission to reconstruct one. See the [existing validation commands](../../AGENTS.md#validation).

Write `CONTROL_ROOT/report.md` with scenario/variant and role, configuration, actual stimulus, expected/observed behavior, evidence links, result, and limits. Keep native execution, standalone role exercises, and deterministic fixture tests separately labeled. Include failed/skipped commands and unavailable model observability. Do not label all Maximum obligations passed merely because one wrapper or summary says so.

Report test source fingerprint, three repo/remotes, chat links, feature baselines and tips, completed cases, failures, and remaining gaps. Leave repositories, branches, and evidence available for inspection. Do not clean them up, merge, publish, or change installations. The user can request those actions separately.
