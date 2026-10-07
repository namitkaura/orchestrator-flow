# Proposal: Orchestrator Flow v2.0.0 test kit

## Problem Statement

### The kit needs a documented purpose and requirements baseline

Orchestrator Flow's Python tests validate schemas, recorded workflow transitions, document reading, and checkpoint recovery. They cannot establish whether actual agents invoke the required roles, honor accepted model and reasoning assignments, read the required inputs, enforce user gates, or produce the claimed results. A live test kit is needed to observe those behaviors in disposable projects.

The intended user experience is to give a master agent one parent test folder and the reusable master prompt. The master prepares the test environment, starts real Orchestrator chats, makes explicitly delegated test decisions at actual workflow gates, and collects an evidence-based report. The user should not need to construct fixtures, edit JSON, repeatedly paste prompts, or supervise every document approval. Unexpected choices outside the scripted authority still return to the user.

The kit was built directly from conversation without a separate creation proposal or implementation plan. Its existing documents describe how to operate that first implementation, but there is no single account of the intended kit, its requirements, and the reasons for its boundaries. This proposal supplies that missing baseline and defines the corrections arising from the first run. It covers both useful existing behavior to preserve and changes still needed.

The objective is to test configuration enforcement and workflow behavior across Basic, Standard, and Maximum assurance. Capability means the accepted model and reasoning assignment for each lead role and helpers; it is independent of assurance. The kit should demonstrate that those choices are applied and persist. It is not a comparison of which model produces better work, runs faster, or consumes fewer tokens.

### The first implementation is an agent-operated kit inside release documentation

The current kit lives under `.docs/v2.0.0/` and contains:

- An overview named `orchestrator-flow-v2.0.0-live-test-plan.md`, whose actual title is a live-test overview. It explains coverage, run shape, evidence standards, and limits; it is not a plan for implementing the kit.
- A runbook and scenario catalogue describing setup, orchestration, interventions, and expected observations.
- Four completed sample proposals for a small standard-library Python command-line project and its follow-up features.
- Separate master, workflow-runner, decision, resume, standalone-role, and evidence-collection prompts.

The master startup prompt explicitly requires the runbook and scenarios. The evidence-collection prompt also refers to the overview. These files therefore form a functioning kit with operational cross-references, rather than a set of historical notes that can be moved independently.

Existing useful behavior includes allocating a fresh `testrun-N` container, using three ordinary local repositories with local bare remotes, preserving source identity and accepted settings, driving native workflow agents through real gates, and distinguishing passed, failed, unverified, and unattempted scenarios. The user authorized the master to make scripted decisions within disposable test scope. The master operates outside the workflow being tested and does not grant approvals to its own implementation.

The first setup built `line-list-project` once as ordinary controller work and copied that application baseline into all three projects. All three were assigned `unique-lines`, but only Basic was assigned `output-limit` and only Standard was assigned `ignore-case`. The instructions also allowed each project's chat to continue into a different feature. This made the runs difficult to compare and did not exercise the intended initial project creation or feature-specific chat lifecycle.

### The first run exposed harness problems as well as workflow problems

`testrun-1` was closed with findings and preserved for analysis. Its actual outcomes were:

| Feature case | Observed outcome |
| --- | --- |
| Basic unique-lines | Stopped without final acceptance because the initial Reviewer missed part of a truncated specification read despite reporting full coverage. |
| Standard unique-lines | Accepted and delivered. A historical malformed Coder native return remained a recorded failure. |
| Maximum unique-lines | Stopped without final acceptance because the consolidated Planner returned a pointer/status object instead of the required wrapper. |
| Standard ignore-case | Implementation reviews completed, but final acceptance remained blocked by a specification assurance gap requiring workflow-reducer correction. |
| Output-limit | Not run because its required accepted Basic predecessor was unavailable. |

Only four Orchestrator chats were used: three initial unique-lines chats and a Standard replacement chat that was later reused for ignore-case. There were no Flow runs for `line-list-project`. Some additional coverage came from standalone role exercises; those demonstrated narrower role behavior, not complete workflow enforcement.

The run also revealed these kit problems:

- Proposals were copied into `.docs/inputs/`, away from their feature logs and specifications.
- Basic committed thirteen intermediate role-wrapper files. Standard's spec directories were clean. Maximum's spec directory was clean, but its consumer repository accumulated an untracked `.orchestrator-test` subtree containing scripts, wrapper copies, transcripts, fixtures, log snapshots, and temporary directories.
- A controller-only change to future repository defaults was represented as a feature authorization event in Basic. The active feature's settings remained unchanged, so the controller action did not warrant a feature event.
- A synthetic specification fixture had invalid revision-history ordering, confounding its acceptance result. Some follow-up and blocker outputs passed only structural checks or failed semantic validation.
- A runner relaxed the required consolidated return to a pointer. A resumed runner also saw controller-prompt and manifest excerpts and later reused that context for another feature. There is no evidence that it read a private answer key, but the run cannot be described as fully isolated from controller expectations.
- Important scenarios remained unverified or unattempted, including live finding-to-repair policy handling, retained known issues, some capability failure variants, and the planned rejected-push case. Successful standalone exercises or parser checks did not fill those live gaps.

The unrelated staged and untracked files in Basic were intentional fixtures for preservation testing, not accidental application artifacts. Testing that intervention once is reasonable if the scenario and report identify its placement and exact file states.

Workflow defects and clarified runtime behavior are covered by the separate workflow corrections proposal. This proposal changes the kit so it tests those contracts accurately, owns its controller artifacts, and reports evidence without hiding failures or creating unnecessary work.

### The revised workflow changes what the kit must observe

The corrections now assign artifact checkpoints to Planner/Coder and task-log checkpoints to Orchestrator. Coder continues through natural checkpoint groups without interim wrappers, owns intentional edits, and uses helpers for exploration and test execution. Recovery must account for work before a completion wrapper exists. The old resume scenario's blanket instruction that producers suspend while their updates are checkpointed does not fit this Coder behavior.

Exceptionally large features also gain implementation phases with lighter intermediate reviews, explicit reasoning reductions, separate repair allowances, and final Coder consolidation. The small sample features should exercise the ordinary path. This revision covers phase rules through deterministic workflow tests and checks that ordinary features are not split unnecessarily; native phase exercises are deferred.

## Proposed Solution

Maintain a reusable Codex live test kit under `tests/live/`, with this release-specific proposal remaining in `.docs/v2.0.0/`. The requirements below define the complete intended kit. Implement the relocation and harness corrections while preserving the working setup, authority, isolation, and evidence behavior.

### 1. Give the reusable kit one home and clear document responsibilities

Move the operating kit as a unit, updating its references and source-path discovery:

| Current location within `.docs/v2.0.0/` | Target location | Responsibility |
| --- | --- | --- |
| Kit entry material in `README.md` | `tests/live/README.md` | Explain how the user starts a run and where the operating documents are. |
| `orchestrator-flow-v2.0.0-live-test-plan.md` | `tests/live/overview.md` | Explain purpose, coverage, architecture, evidence standards, and limitations. |
| `test-runbook.md` | `tests/live/runbook.md` | Define setup, execution, resumption, bounded decisions, and closeout procedures. |
| `test-scenarios.md` | `tests/live/scenarios.md` | Define private controller stimuli, timing, expected observations, and coverage assignments. |
| `proposals/` | `tests/live/proposals/` | Hold the finished product inputs used by the test features. |
| `prompts/` | `tests/live/prompts/` | Hold reusable message text with documented substitution rules. |

Keep the original workflow proposal, the workflow corrections proposal, and this test-kit proposal in `.docs/v2.0.0/`. Retain a release-document index there with a link to the kit's new entry point. Do not leave a second editable copy of the operating kit in the old location.

Use release-neutral operating filenames; record the actual workflow version and source used for each run. This does not promise support for an unknown future workflow contract. The present target remains the Codex v2 implementation.

The overview should contain explanation rather than unique operational requirements that the master might miss. The runbook and scenarios remain required operator inputs; prompts reference the relevant sources. Evidence collection may consult the overview, but its verdicts must follow the scenario and runtime contracts. Keep the documents consistent without copying every rule into every file.

### 2. Preserve one-input setup and isolated, repeatable run containers

The user supplies an absolute parent test folder and submits the master prompt. For a fresh run, choose one greater than the largest existing immediate `testrun-N` entry, or 1 when none exist. Files, directories, incomplete runs, and links occupying a candidate name all count as occupied. Do not fill numbering gaps or reuse an existing run for a fresh request. A different empty parent starts at `testrun-1` independently.

The complete run lives under that allocated container:

```text
<test-root>/
  testrun-N/
    basic/
    basic-repo/
    standard/
    standard-repo/
    maximum/
    maximum-repo/
    .orchestrator-test/
      run.json
      decisions.md
      evidence/
      fixtures/
      report.md
```

The three `*-repo` directories are local bare remotes. Each working repository has its own correct `origin`; pushes exercise real Git locally without requiring a hosted repository. Initialize or clone a working repository before using repository-scoped commands, and create an initial commit before trying to push its branch.

Setup creates only the bootstrap material needed to run the workflow: product inputs, appropriate ignore rules, and minimal normal project guidance. Application implementation and its application tests belong to the first Flow feature. An identical non-application bootstrap may be shared between projects, but finished application code must not be seeded as setup.

Resolve and record owned paths before mutation. Use ordinary checkouts, not worktrees. Reuse a working helper Python environment where available; if setup needs an environment, keep it within the run's control directory and install only the existing workflow-helper dependencies. Do not add them to each sample application's dependencies or modify the user's installed skill.

Prepare the repositories before resolving their saved Codex project IDs through native tools. If project registration requires user action, ask once with the three prepared paths and continue independent preparation. Do not substitute unrelated projects or ask the user to assemble the test inputs manually.

An explicit resume request reuses the recorded run and reconciles its actual state. It does not blindly repeat initialization or allocate another fresh run.

### 3. Run all four product proposals through Flow in every project

Use the same four proposals and dependency order in all three assurance projects:

| Order | Product proposal | Basic | Standard | Maximum |
| --- | --- | --- | --- | --- |
| 1 | `line-list-project` | Complete Flow feature | Complete Flow feature | Complete Flow feature |
| 2 | `unique-lines` | Complete Flow feature | Complete Flow feature | Complete Flow feature |
| 3 | `output-limit` | Complete Flow feature | Complete Flow feature | Complete Flow feature |
| 4 | `ignore-case` | Complete Flow feature | Complete Flow feature | Complete Flow feature |

The initial application must be planned, reviewed, implemented, reviewed again, and explicitly accepted through the actual workflow in each project. The master does not implement it as setup or impersonate any role. Every feature uses native Planner, Architect, Coder, and Reviewer delegation with the real gates and artifacts.

Update sample-proposal prerequisites and preservation expectations for this complete sequence. In particular, ignore-case follows output-limit and must preserve earlier accepted functionality. Keep the product deliberately small and consistent across projects; differences in assurance do not imply different product requirements.

All twelve cases are expected to use the ordinary single-Coder-assignment path, with natural checkpoint groups and normal recovery where needed. Do not enlarge the sample proposals or force implementation phases to obtain coverage. Record and assess any unnecessary split or intermediate review against the corrected contract; do not hide it by changing the reported scenario. Section 9 defines the separate deterministic phase coverage and its live-evidence limitation.

Place each completed input alongside its feature's eventual task log and specifications under `.docs/specs/{feature-name}/`, using a clear local input filename such as `proposal.md`. Do not create the workflow-owned task log or specs during controller setup. Do not use a separate `.docs/inputs/` collection, and do not put scenario expectations in the product proposals.

Special interventions may remain distributed across selected feature cases. The common product sequence gives understandable coverage; it does not require repeating every failure variant or capability combination in every project. A failed or unaccepted predecessor blocks its dependent feature. Other independent projects may continue, with missing dependent coverage reported honestly.

### 4. Use feature-specific chats and explicit branch continuity

Create one new top-level Orchestrator chat per feature. Never reuse a completed feature's chat for a different proposal or task log. This is a test-kit operating rule, not a new Orchestrator Flow restriction.

The planned fresh-context resume case creates a replacement chat for the same feature, directory, log, branch, and repository. Target a boundary after meaningful Coder artifact checkpoints but before its completion wrapper. Confirm the original writer and its delegated work are idle or stopped before replacement. Preserve the accepted feature configuration and actual checkpoint state. A replacement is not an additional feature or a reset of its authority and counters.

Record Orchestrator and Coder context continuity separately. A fresh Orchestrator continuing the original Coder demonstrates coordination recovery, not reconstruction by a fresh Coder. Seek the latter within the existing bounded resume scenario where native controls permit it; otherwise report that part as unverified. Do not fabricate context loss or start a second active writer.

A full run therefore has twelve feature chats, plus the planned replacement chat if that resume case is reached. The manifest must map each project and feature to its original/replacement chats and current owner. The master may remain in one chat for the entire run.

Keep one active feature run at a time by default to bound usage and simplify observation. Follow-ups within a feature continue in its owning chat or replacement. Starting a new feature always creates a new chat, even when the preceding chat is idle.

After a feature is accepted and delivered, its actual branch tip becomes the explicitly selected integration baseline for its successor. Leave `main` at the bootstrap and do not merge merely to prepare the next feature. Record the integration branch and baseline for every new feature rather than assuming that `main` contains its predecessor.

Exercise the corrected workflow branch rule across existing cases: an explicit branch name takes precedence; otherwise the branch defaults to the feature name. Cover feature names with and without a version. Runner prompts must support omitting an explicit branch name so the default is actually tested. Do not insert `codex/` or require a product version. Keep logical feature labels, directory names, explicit selections, and resolved branches clear in the manifest; no extra feature runs are needed solely for naming coverage.

### 5. Test capability decisions and assurance independently

Keep the agreed economical controller setup. The user selects the master's model and reasoning when launching it, with GPT-6.1 Sol High as the recommended default. Create every top-level test Orchestrator, including replacements, with the explicitly selected GPT-6.1 Sol High assignment through native chat controls. Record the actual settings exposed by the client. If that required Orchestrator assignment is unavailable, obtain direction for the affected work instead of silently substituting another model.

Workflow role and helper assignments are separate. Let each Orchestrator recommend repository defaults when absent and present feature-specific capability and assurance recommendations through its normal gates. The master then acts as the user's delegate to accept or select supported alternatives.

The scenario catalogue must separately cover:

- Accepting valid recommended capabilities unchanged.
- Selecting at least one different supported assignment before feature initialization.
- Explicit overrides after a feature's configuration is recorded.
- Actual use of the accepted assignments on subsequent role/helper invocations and after resumption.
- Repository defaults affecting future features while an existing feature retains its accepted snapshot.
- Supported bounded unavailable-assignment or failure cases, with honest limits when a native condition cannot be induced or observed.

Use a small mix of supported role/helper capabilities. Prefer Luna for deliberately selected helper variations where available, consistent with the user's preference; do not silently replace a different accepted assignment. The unchanged-recommendation case must remain unchanged when the recommendation is valid. Passing that case and selecting an alternative are different observations.

Associate helper settings with their actual owning role and purpose. Coder's exploration and test-execution helpers need observable native assignments; a controller helper or a generic investigation elsewhere does not prove those assignments were used. Intermediate Reviewer reasoning mappings have deterministic coverage under section 9, not native coverage in these ordinary feature runs.

Basic, Standard, and Maximum are the three primary assurance cases. Explicit scenario overrides can change an individual feature's effective assurance; report the actual sequence rather than implying that its folder name describes every review it received. Capability changes must not implicitly change assurance.

Initial runner prompts carry genuine human constraints, not the controller's private planned capability selections or expected findings. Observe the real recommendation before making the scenario's decision. Use native invocation evidence where exposed; saved settings, prompt requests, and a model's self-identification are not proof that the configured assignment was used. Do not benchmark model quality, speed, or token consumption or expand into a capability-combination grid.

### 6. Preserve real gates and bounded delegated authority

The master prompt must carry the user's explicit authority to create and message local test chats and make scripted workflow decisions within the disposable test scope. Delivered decisions identify their delegated provenance and the actual artifact version, finding, configuration, or operation concerned. They must not pretend to be newly typed human messages or authorize every future gate in advance.

The master may accept conforming configuration and documents, authorize the approved coding scope, make policy-permitted finding dispositions, and explicitly accept a satisfactory feature. It must inspect the actual result before doing so. Scope changes, unplanned policy choices, or exceptions beyond the script return to the user.

Preserve the existing bounded allowances:

| Situation | Controller allowance |
| --- | --- |
| Specification repair-cycle gate | At most one additional Planner repair and Architect re-review per feature, after the actual gate and only when another bounded pair has a concrete expected benefit. |
| Final implementation repair-cycle gate | At most one additional Coder repair and Reviewer re-review per feature, after the actual gate and only when another bounded pair has a concrete expected benefit. |
| Exhausted ordinary role attempts | At most one additional ordinary attempt for the selected recoverable case; model/usage failures follow their separate assignment/wait decision path. |
| Scripted failed or uncertain checkpoint push | After reconciling the actual attempt and restoring the owned failure fixture where applicable, authorize one recovery push for that attempt. Another failure stops the affected case for direction. |
| Final acceptance | Require satisfactory delivered behavior, applicable checks, Reviewer acceptance, and properly handled known issues. A request for a squash message alone is not acceptance. |

Preserve the workflow's existing no-success-receipt push behavior and manual final merge. The kit must not grant extra retries, reset counters, manufacture findings, or waive a required failure simply to complete the matrix. It may close a scenario at a correctly observed gate without accepting the feature.

These controller extensions are separate from the workflow's normal assurance-based repair allowances. The former phrase "per phase" referred to specification and implementation review, not a new extension for every implementation phase. This revision authorizes no native phase exercise or intermediate-phase repair extension. Resume and context replacement do not replenish either workflow allowances or controller grants.

Use bounded progress waits and targeted history reads rather than repeatedly rereading whole conversations. Preserve the intended top-level settings on follow-up messages. The master observes the feature chats; they do not need authority to send unsolicited messages back to it.

### 7. Separate controller bookkeeping from feature history and artifacts

Keep controller records, captured original outputs, standalone fixtures, answer keys, ad hoc test scripts, and evidence under the run-level `.orchestrator-test/` directory, outside all three consumer repositories. The manifest records paths, source identity, feature/chat mappings, actual accepted settings, branch baselines, scenario progress, blockers, and evidence references. It is controller bookkeeping, not another workflow task log.

When the master changes repository defaults solely to test future-feature behavior, perform that controller-owned action at a coordinated idle boundary and record it only in controller evidence. Do not ask the current Orchestrator to manufacture an authorization or override event for it. Confirm that the existing feature's configuration remains unchanged and that a subsequent feature sees the new defaults. An actual requested override of an existing feature still goes through that feature's normal workflow event and checkpoint.

Do not direct roles to write wrapper files or scratch evidence into the consumer repository to help the master collect results. Capture actual native returns and authoritative feature artifacts externally. The workflow's temporary-output lifecycle remains defined by its own contracts; the kit observes compliance rather than imposing a second runtime storage policy.

Inspect both working trees and committed history for unexpected files, not just specification directories. Distinguish intended product source/tests/docs, workflow Git-metadata journals, ignored caches, declared controller fixtures, and accidental scratch artifacts. Preserve unexpected files as evidence when closing a failed run; do not silently clean the repository and report that it stayed clean.

The unrelated-change scenario may run in one selected project. Record precisely whether each owned fixture is staged, modified but unstaged, or untracked, with its original content and index state. An untracked file must not be described as evidence for preserving an unstaged edit to a tracked file. The other projects need not receive those fixtures merely to make their directory listings identical.

### 8. Correct scenario design and preserve valid observations

Remap existing assurance, capability, and cross-role scenarios onto the full four-feature matrix, including the new Flow-based project creation. Make intervention ownership, prerequisites, timing, expected behavior, bounded allowance, and evidence explicit. Keep product behavior in the proposals and private test expectations in controller documents.

Prioritize the actual gaps and corrected contracts:

- Complete initial review reads and valid actual native wrappers at required handoffs, including consolidated completion reports. Ordinary Coder checkpoints and necessary coordination messages do not require interim wrappers.
- Progress-only task checkboxes without content-version or Revision History changes, alongside real material/editorial revision behavior.
- Producing-role artifact checkpoints, separately published authoritative log updates, sequential document approval gates, and natural coding groups without per-group review or acknowledgement.
- Coder-owned edits, actual exploration/test helpers, concise test evidence, and accepted helper capabilities.
- Assurance increases with genuinely insufficient evidence, in-flight review changes, and returning to a previously satisfied level without an unnecessary repeat review.
- Real findings and subsequent producer/reviewer handling under the three disposition policies, retained known issues, and the applicable continuation gates.
- Changed configuration and cumulative implementation scope surviving the planned fresh-context resume before Coder completion.
- The selected local rejected-push recovery case, unrelated-change preservation, scoped blockers, and explicit feature acceptance.

#### Checkpoint and completion evidence

Observe Planner publishing each draft/revision before returning its wrapper; Orchestrator then records and publishes the wrapper, requests approval, and records/publishes approval before authorizing the next document. Observe Architect/Reviewer returns being recorded and checkpointed before dependent work. Every actual authoritative log update needs its checkpoint, but directly related events may share one; do not require one commit per event.

Observe Planner-defined natural coding groups and Coder's own commit/push operations. Coder continues after successful delivery without an interim wrapper, fabricated event, or Orchestrator acknowledgement solely for the checkpoint. Artifact-only commits are valid and need not carry task-log event ranges. Do not require a commit per numbered task or a new full test run merely because a checkpoint occurs. At completion, require the full cumulative wrapper against the original feature baseline.

#### Recovery before the completion wrapper

Use the existing selected resume case to preserve multiple meaningful implementation checkpoints before Coder completion. Orchestrator must reconcile recent commit metadata/messages, changed-file lists, real log/native evidence, and writer liveness, extending its history inspection when necessary. Observe that it does not open code/specification bodies or patches; content questions go to the responsible role. Replace the old blanket producer-suspension expectation with the distinct Planner gate and Coder checkpoint rules.

When Coder context is replaced, observe recovery from checkpoints, task progress, actual implementation, and available verification evidence. The eventual wrapper must include pre-interruption work and current dispositions without resetting the reporting baseline or repeating completed implementation. Distinguish recovered results from new checks. The controller may inspect artifacts to assess this behavior; its access does not relax Orchestrator's boundary. If the intended timing or fresh-Coder condition is not observed within the bounded attempt, report the limitation instead of claiming full recovery coverage.

#### Coder helpers and test evidence

Verify that Coder makes intentional implementation/test/documentation/progress edits while helpers explore and execute tests. Test helpers report the actual command/selection, result, available counts, skipped/unavailable checks, and useful failure details. Expected Red failures must be distinguished from unrelated command or setup failures. Look for concise results reaching Coder, not full passing transcripts or unsupported success claims. Reuse is appropriate; impose no fixed helper count or helper per task. Controller checks and standalone exercises do not substitute for observed workflow helper use.

#### Publishing-role failures and required returns

The selected controlled push failure should target a Planner- or Coder-owned artifact checkpoint to exercise the changed ownership. Use an owned local-remote fixture installed at a coordinated idle boundary, with timing or targeting that identifies the intended publisher. Verify the fixture can actually cause the intended failure, restore only the owned change, and observe the real push result and Orchestrator-coordinated bounded recovery. If a different publisher encounters the fixture, report what actually happened and the intended coverage gap. An approval system preventing a process from starting is not an executed failing push. Do not fabricate an exit result, retry allowance, or delivery receipt. Other publisher/failure variants can use the workflow's deterministic tests without multiplying live feature runs.

Preserve original native outputs, including malformed or pointer-only responses, before interpretation. Validate actual required handoffs against the full applicable contract. A valid saved file elsewhere does not repair an invalid native completion return; an ordinary progress message or absent checkpoint wrapper is not a failed completion handoff. Preserve first-run failures under the contract applicable at that time without importing its obsolete interim-wrapper requirement into new verdicts. Conversely, byte differences between two complete valid outputs are not automatically a workflow failure; establish what actually governed the handoff.

#### Isolation and bounded supplemental cases

Do not expose the master prompt, private scenarios, manifest commentary, or answer keys to runners to solve a test problem. Supply only the ordinary product input, actual settings/decisions, and operational facts needed at that gate. Record any accidental exposure as a limitation. Fresh feature chats prevent carrying controller expectations into unrelated features.

Use standalone role exercises only for identified gaps they can meaningfully cover; native implementation-phase exercises are deferred under section 9. Validate a synthetic fixture before use, document any intentional injected defect, and preserve a coherent source snapshot and provenance before repair. Unrelated invalid metadata must not confound the intended test. Use the real role with standalone context and keep all fixture writes inside the controller-owned fixture area. Never insert standalone output into a consumer log as if it were a live workflow event.

Try a selected timing-sensitive or exceptional variant once within its planned allowance. If it cannot be observed economically, record the limitation and cite deterministic coverage separately. Do not deliberately degrade live implementations, force finding counts, or repeat full workflows until discretionary reviews match an answer key.

### 9. Cover phase rules deterministically and defer native phase exercises

Keep the twelve-feature matrix unchanged and observe that its small features stay on the ordinary path. Do not add a large product proposal, fixture-backed native phase run, forced phase setting, or extra phase-review chat in this revision. Native phase execution is explicitly deferred, including fresh successive phase Coders and actual intermediate Reviewer invocations.

Require attributable behavioral-test evidence from the workflow corrections implementation for:

- The assurance mapping: Basic has no intermediate review; Standard uses Basic phase reviews; Maximum uses Standard phase reviews. Final review retains the feature assurance, and the last phase goes directly to final review without a duplicate intermediate pass.
- The same-model reasoning reductions: `max` to `high`, `xhigh` to `medium`, and `high` to `low`, with persisted assignments, applicable override/resume behavior, and explicit handling of unmapped or unavailable settings rather than silent substitution.
- Independent repair allowances: one cycle per intermediate review in Standard features, two in Maximum features, and the existing separate final-review policy. Initial reviews are not repair cycles; replacement/resumption cannot reset an unresolved cycle or invent additional authority.
- Phase completion/review scope, truthful task progress, and pending-action recovery. An intermediate result cannot establish whole-feature completion or acceptance. A correctly configured lower-assurance phase review must not create a spurious assurance gap, and it cannot replace the required final review.
- Final Coder consolidation of all phases against the original feature baseline and ownership of final-review repairs, including earlier-phase changes. Exercise the representable scope/evidence checks without claiming that validator acceptance proves native Coder synthesis or Reviewer coverage.

These tests belong to the existing workflow development suite and corrections work, not a second implementation in the kit. Reference test identities, tested source, actual results, and relevant valid/invalid cases. Instruction-text searches and valid example JSON alone do not establish the behavior. Missing coverage remains a reported dependency or gap; the master must not modify the runtime or fabricate an equivalent result.

Report ordinary-path observations and deterministic phase results separately. Mark native phased execution as deferred/not run, even if all deterministic tests pass. The normal runs do not prove that Planner would identify a genuinely large feature correctly or that native agents would honor phase assignments; do not fill those gaps with standalone phase exercises in this revision.

### 10. Produce an attributable report with clear coverage limits

Record the actual workflow version, source checkout and content fingerprint, kit inputs, linked installation, helper interpreter, and relevant native capabilities at the start. Include uncommitted source content when it is part of what runs. Keep those sources stable during a run; if they change, identify affected evidence instead of treating mixed results as one implementation.

Collect evidence progressively at meaningful boundaries so interruption does not erase the run's observations. Preserve native role outputs, delivered decisions, real task logs and available prior snapshots, actual document changes, Git correspondence, and relevant checks. Keep the evidence necessary to substantiate findings without creating redundant archives of every file at every poll.

Where exposed, associate checkpoint and test operations with native role/helper invocations and their actual settings. Git author names alone do not identify the publishing agent, and a passing controller test does not demonstrate a Coder test-helper run. Record unavailable attribution as an evidence limit. Preserve enough pre/post-resume context and Git correspondence to assess cumulative reporting without asking roles for extra wrapper files or reading every conversation repeatedly.

Report each planned case with its actual configuration, delivered stimulus, expected and observed behavior, references, and one of these results:

| Result | Meaning |
| --- | --- |
| Pass | The behavior was exercised and the evidence supports the expectation. |
| Fail | An observed action or omission contradicts the applicable contract. |
| Unverified | The attempt or environment did not provide enough observation to establish the behavior. |
| Not run | The case was not attempted, including a successor blocked by its predecessor. |

Separate full native workflow evidence, standalone role evidence, deterministic fixture tests, and inspection/inference. Attribute findings to workflow defects, harness defects, agent compliance failures, or environmental/observability limits as supported. An accepted feature can still have a historical observed failure; an unaccepted feature can still provide valid evidence for particular behaviors.

Judge discretionary classification and remediation against approved behavior, project consequences, and assurance, not matching prose or identical issue counts. Preserve unresolved findings and coverage gaps. Do not claim that valid JSON proves complete review, that a passing product suite proves authority enforcement, or that a completed role turn proves final feature acceptance.

Closeout must identify actual feature states, pending gates, active or idle agents, delivery blockers, and preserved repositories/evidence. A user-requested bounded stop prohibits new scenarios or repair cycles beyond that instruction. Controller closeout must not manufacture feature events or acceptance.

### 11. Update references and verify the kit proportionately

Update the root README, `AGENTS.md`, `tests/README.md`, the v2 documentation index, and all internal prompt/runbook/scenario links for the new layout. Keep the existing Python suite in its current development-test role. Adjust source discovery and recorded kit-file inventories so moving the files does not omit them from run provenance.

Verify before handing back the revised kit:

- All operating files resolve from `tests/live/`, its master prompt, and the intended source checkout; there is one authoritative kit copy.
- Every matrix entry has the correct proposal, predecessor, assurance case, new-chat requirement, and recorded branch/default behavior.
- A first-project prompt invokes Flow with its colocated proposal and does not rely on controller-built application code or pre-created workflow artifacts.
- Prompts preserve actual gated recommendations and decisions, use complete substitutions, and keep private expectations out of feature contexts.
- Controller-only defaults actions and evidence storage no longer direct agents to create unrelated feature events or consumer scratch directories.
- Fixture validation, actual native-return capture, and the report's evidence categories address the first-run attribution problems.
- Scenario and prompt expectations distinguish Planner approval gates, Coder-owned artifact checkpoints, Orchestrator log checkpoints, and required completion wrappers; they do not retain the old pause/wrapper-per-update behavior.
- Resume and helper scenarios specify the actual native observations needed, including fresh Orchestrator versus fresh Coder context, pre-resumption scope, intentional edit ownership, and who ran tests.
- Repair-decision prompts distinguish specification and final implementation allowances from controller extensions; no intermediate-phase grants or native phase exercises are introduced.
- Deterministic phase coverage is traceable to workflow tests, and the report explicitly retains the deferred native-phase coverage gap without enlarging the twelve-feature matrix.
- Existing automated checks affected by reference/layout changes still pass, and `git diff --check` is clean.

Prefer targeted checks and a coherent walkthrough of setup, one feature, a replacement resume, and the next feature's new chat over a new large test framework. Static checks cannot certify live agent compliance. Launching the revised kit is a separate user-authorized action; its acceptance report must distinguish preparation checks from actual live execution.

### 12. Non-goals and preservation boundaries

- Implementing the runtime changes defined in the separate workflow corrections proposal, or editing runtime schemas, agent roles, and replay code to make a test pass.
- Turning the kit's one-feature-per-chat rule or colocated sample inputs into new general workflow restrictions.
- Claude Code, GitHub Copilot, or Cursor test runners in this Codex-only phase.
- Exported packages, installation frameworks, hosted remotes, worktrees, automated merges, or edits to the user's installed skill and personal settings.
- Model benchmarking, exhaustive capability combinations, forced discretionary findings, or open-ended repair and rerun loops.
- Native implementation-phase exercises, including synthetic starting fixtures and genuinely large feature runs, or extra sample features introduced solely to test phases. This revision uses ordinary-path observations and deterministic workflow coverage only for that extension.
- Moving collected run outputs into `tests/live/` or committing consumer test repositories and evidence into the workflow source repository.
- Rewriting, cleaning, migrating, resuming, or retroactively repairing `testrun-1` as part of kit maintenance. Its observations and original failures remain preserved.
- Starting chats, setting up a new test run, sending messages, or performing maintenance Git writes merely because this proposal or the operating files are being edited. Those actions require the applicable user authorization.

## Questions

The intended kit and the user-selected corrections above form the planning baseline. No additional proposal-level decision is required before producing an implementation plan.

Phase coverage is settled for this revision: preserve the ordinary twelve-feature run, require deterministic evidence for the phase rules, and defer all native phase exercises. Cover the other corrected checkpoint, recovery, helper, authority, and reporting behavior within the existing cases and bounded supplemental scenarios.

Planning should make the scenario allocation, feature-name/branch examples, bootstrap contents, prompt substitutions, and necessary evidence handling concrete. These are bounded implementation choices within the stated requirements. Keep the complete four-feature sequence and distinguish preserved behavior from corrections rather than treating every requirement as a request to rebuild the kit.

Use the corrected workflow contracts when preparing the next run's expectations. If a required runtime correction is not yet available, disclose that dependency rather than weakening the test or implementing a runtime workaround in the harness. Raise genuinely new user-visible choices during planning instead of adding scope or assuming authority.

## References

Repository links below identify the current source locations before the planned move. When implementing the relocation, update these references to the canonical new locations. The first-run evidence lives outside the repository and is supplemental; the essential observations and requirements are summarized in this proposal.

- [Workflow corrections proposal](proposal-orchestrator-flow-v2.0.0-corrections.md): separate runtime work and deterministic coverage for task-progress versions, assurance applicability, temporary artifacts, handoffs, review representations, blockers, branch defaults, producing-role checkpoints, recovery, Coder helpers, and exceptional implementation phases.
- [Original workflow proposal](proposal-orchestrator-flow-v2.0.0.md), [repository guidance](../../AGENTS.md), and [README](../../README.md): workflow purpose, current Codex scope, repository maintenance boundaries, and installation policy.
- [Current live-test overview](orchestrator-flow-v2.0.0-live-test-plan.md), [runbook](test-runbook.md), and [scenario catalogue](test-scenarios.md): implemented testing approach and operating instructions to preserve or correct as specified here.
- [Sample proposals](proposals/README.md): the four product inputs to run consistently across all three projects.
- [Master prompt](prompts/master-agent.md), [runner prompt](prompts/workflow-runner.md), [decision catalogue](prompts/test-decisions.md), and [resume prompt](prompts/resume-run.md): current authority, chat lifecycle, settings, gates, and continuation instructions.
- [Standalone-role prompt](prompts/role-exercise.md) and [evidence-collection prompt](prompts/collect-evidence.md): bounded gap exercises and evidence/reporting responsibilities.
- [Python test guide](../../tests/README.md), [workflow protocol](../../.codex/skills/orchestrator-flow/references/workflow-protocol.md), and [assurance contract](../../.codex/skills/orchestrator-flow/references/assurance.md): separation of deterministic and native evidence and the runtime standards under test.
- [First-run closeout report](../../../orchestrator-flow-test-runs/testrun-1/.orchestrator-test/closeout-report.md) and [manifest](../../../orchestrator-flow-test-runs/testrun-1/.orchestrator-test/run.json): preserved outcomes, coverage gaps, and next-revision requirements.
- [Artifact/source inventory](../../../orchestrator-flow-test-runs/testrun-1/.orchestrator-test/evidence/closeout-layout-and-source-status.json), [Maximum handoff audit](../../../orchestrator-flow-test-runs/testrun-1/.orchestrator-test/evidence/U-M-native-return-causal-audit-output.md), and [standalone fixture/review assessment](../../../orchestrator-flow-test-runs/testrun-1/.orchestrator-test/evidence/Maximum-standalone-initial-result-assessment.json): supporting evidence for artifact handling, relaxed returns, fixture validity, and attribution limits.
