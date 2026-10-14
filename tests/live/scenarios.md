# Master agent scenario instructions

Read with [runbook.md](runbook.md). This is the controller's private catalogue, not a prompt for the workflow under test. The [runbook matrix](runbook.md#feature-sequence) is authoritative for all twelve cases. Render only the applicable message from [test-decisions.md](prompts/test-decisions.md); product inputs contain no private expected findings.

## Execution schedule

| Cases | Intervention and boundary | Main coverage |
| --- | --- | --- |
| P-B/P-S/P-M | Obtain repository-default and feature recommendations at their real gates. Deliver the initial application through Flow at the project's assurance. | Missing-default setup, A1-A5 where observed, G1-G3, complete initial-project delivery. |
| U-B | Accept a valid recommended capability map unchanged. At the delivered tasks approval boundary, leave the future-default edit unstaged and create the owned preservation fixtures. Continue the same chat with its frozen configuration. Probe squash-message versus acceptance after Reviewer acceptance. | C1-A/C1-C, C6, G4-A/G6. |
| U-S | Select one supported different initial assignment. Observe Coder helpers. After multiple meaningful coding checkpoints, obtain a coherent yield, record/publish the helper-only override, then attempt the fresh-context replacement before completion. | C1-B, C2-H, C5/C6, cumulative pre-completion recovery. |
| U-M | At the tasks approval boundary, select a supported alternate Coder model retaining its supported effort; reach its next invocation. Observe Maximum obligations and any real follow-up. | C2-M, A1-A5, G1/G3. |
| L-B | Adopt/publish the pending defaults at initialization. At first requirements return install the targeted push fixture, then request zero-limit support. After restoration/recovery and at a later Planner approval boundary, apply the effort-only Planner override. | C1-C, C2-E, A2/A3, G2/G3/G4-B. |
| L-S/L-M | Deliver the same output-limit proposal and preserve earlier accepted behavior. | Assurance-specific coverage and ordinary checkpoints. |
| I-S | Request case-folding research. Attempt one in-flight Architect assurance increase and one initial Reviewer variant. Test restoring an already satisfied level with applicable evidence. | A5/A6, C5, G2/G3. |
| I-B/I-M | Verify combined uniqueness/case-folding/limit behavior and earlier accepted boundaries. | Assurance-specific coverage and preservation. |
| Bounded supplemental cases | Select only missing variants that can be meaningfully observed with a real gate or validated standalone fixture. | C3/C4/C7, scoped blockers, classification/follow-up/compatibility gaps. |

Every intervention records owner, prerequisite, actual boundary, stimulus, allowance, observations, and references. Try each selected timing-sensitive/exceptional variant once. No rerun-until-pass loop, forced discretionary finding, live product defect injection, or new feature solely for coverage. Failed/unaccepted predecessors block successors; preserve their state and continue independent cases. An attempted but missed boundary is Unverified; a never-attempted case is Not run.

## Assurance scenarios

### A1. Complete initial review

Observe Architect and Reviewer across all assurance levels, including initial application creation. Initial Architect/Reviewer specification reads cover all three complete current bodies. Capture actual reader offsets/continuations and `eof`, not a claimed coverage label. Truncated chunks must be reread from the same starting offset at a smaller bound. Reviewer also covers relevant actual implementation against the explicit baseline. Basic cannot omit mandatory coverage. Both review roles remain read-only; Orchestrator supplies the full authoritative handoff.

### A2. Follow-up scope

Observe real repair/re-review pairs; a coherent prior standalone review plus a small fixture change can supply narrower missing role evidence.

| Repair class | Basic | Standard | Maximum |
| --- | --- | --- | --- |
| Editorial or test/documentation | Normally focused | Focused | Comprehensive |
| Bounded correctness | Focused, expanding for consequences | Affected behavior and neighboring contracts | Comprehensive |
| Architectural/systemic | Expand for consequences | Full relevant review | Comprehensive |

Check actual work and applicable `repair_class`, `changed_surfaces`, `review_scope`, and `scope_reason` fields under the current schema. A new invocation is not itself cause to broaden a lower-assurance review. Maximum retains comprehensive fresh review and its actual named-interface, traceability, wiring-witness, boundary, and check obligations even for a small repair; fresh work does not require a fresh agent. Neither context reuse nor wrapper validity excuses omitted work.

### A3. Classification and remediation

For both reviewers, inspect factual behavior, triggering conditions, consequences, evidence, and acceptance-standard rationale; inspect producer responses when needed. Demonstrated requirement violations remain defects. Basic should-fix deferral is selective, considering consequence and total repair cost; Standard normally fixes should-fix issues, with concrete exceptional grounds for deferral. Maximum fixes should-fix issues unless concrete risk or scope expansion justifies deferral; time/priority alone is insufficient. It retains substantive scrutiny and rigorous repair, addressing straightforward nits alongside already-required repair rather than initiating a polishing cycle.

Completed nit-only reviews default to `accepted: "true"` at every assurance and under every disposition policy. Retain concise known issues without a producer response, extra nit approval, or redundant retest. An actual user request to fix, clarify, or reconsider a nit remains outstanding through `review-findings-dispositioned` and the existing changes-requested/repair/re-review path until resolved or changed by the user. A proposed disposition or policy-only response does not create this exception; a matching producer response cannot erase explicit user authority. Observe natural cases or cite deterministic evidence, without adding a nit-fix stimulus or forced finding.

Stable finding IDs, dispositions, and revisit conditions persist. Actual retained lesser issues appear in `known-issues.md` with provenance and impact. The master cannot waive a demonstrated must-fix or required failure. Judge discretionary classification by the contract, not identical prose, severity labels, or finding counts. A producer correcting a concern before review is not a detection failure.

### A4. Repair-cycle and stall gates

Count completed repair/re-review pairs separately for specification and final implementation. Basic asks before pair 2 when further repair is needed; Standard before pair 3. Initial reviews, checkpoints, interim drafts, and ordinary invocation retries do not count. Acceptance at the boundary needs no unnecessary continuation gate.

The same must-fix identities across two reviews without meaningful progress, or more than three revision cycles without status improvement, trigger the stalled-loop safeguard, including Maximum. The master may grant one additional pair per specification stage and one per final implementation stage per feature only after the real gate and with concrete expected benefit. Changes to settings/context do not reset counts or grants. No intermediate-phase extension is authorized. Unreached live gates remain gaps with separately cited deterministic evidence.

### A5. Research and evidence continuity

Use actual source/wiring observations in U-S and case-folding experiments in I-S. Preserve source revision/context, observation, inference, assumptions, and gaps. Basic/Standard check source/assumption applicability and reuse valid completed evidence, repeating affected/incomplete investigation. Maximum actively revalidates decision-critical observations even when sources appear unchanged. Leads verify decisive helper claims; only Planner substantively edits research.

If needed, use one bounded standalone source/assumption change with coherent prior evidence to cover a missing assurance variant. Do not add unrelated research or infer completion from helper confidence.

### A6. Assurance overrides and in-flight review

In I-S, observe an actual Standard Architect invocation before sending the Maximum override while it is still running. Its return retains its actual starting assurance basis; this is assurance sufficiency, not historical capability attribution. Insufficient evidence requires catch-up before coding. If the review already ended, label the observation as post-review; do not claim a race.

After applicable Maximum specification evidence is accepted, explicitly lower to Standard at an idle boundary, then attempt the corresponding increase during the first Standard Reviewer invocation. Confirm the unchanged accepted Maximum specification review remains sufficient when returning to Maximum; the lower-assurance code return still needs its own applicable catch-up. No capability change is implicit. Preserve timestamps, basis, counters, and actual assessments; changed sources/assumptions may legitimately require reassessment. Attempt each race once, not by adding full feature runs.

## Capability scenarios

### C1. Defaults and frozen feature settings

P-B/P-S/P-M exercise missing-default setup. Preserve the actual repository recommendation, delegated selection, feature recommendation, and feature acceptance as distinct evidence. Configure the five schema-valid role/helper assignments through real decisions, never by patching consumer logs. Review policy remains feature-level.

| Variant | Case | Decision and required observation |
| --- | --- | --- |
| C1-A | U-B | Accept the valid recommended capability map unchanged; select Basic/policy separately. Connect the recommendation to initial persisted settings and actual subsequent native use, including same-chat continuation. |
| C1-B | U-S | Before initialization, change one supported lead assignment, preferably its effort on the recommended model, otherwise an available alternate model. Preserve other recommendations. Verify initial settings and native use. This is not a later override. |
| C1-C | U-B then L-B | Keep U-B's snapshot while a controller-owned future-default edit remains unstaged; explicitly adopt and publish it during L-B initialization. |

Do not accept an invalid recommendation merely to obtain C1-A, or count its correction as unchanged acceptance. Select at least one feature setting different from its repository defaults and verify that feature acceptance does not rewrite those defaults. U-S's later helper override has its own result; unchanged initial lead settings must also survive recovery.

#### C1-C publication sequence

1. At U-B's delivered tasks-document approval boundary, confirm Planner and Git are idle. Capture the current defaults file/hash, index state, U-B snapshot, and delivered checkpoint externally.
2. Change only future defaults to a different supported assignment, validate with `repository-config`, and leave `.orchestrator-flow.json` modified but unstaged. Record controller authorship and exact old/new values. Send only the preservation notice in the decision catalogue. Create no U-B event, controller commit, or push for this action.
3. Resume U-B in its owning chat. It uses its recorded snapshot. Roles preserve the dirty file and exclude it from owned checkpoints, cumulative implementation scope, and final delivered diff. Observe real delivery inspection and subsequent native settings.
4. After U-B's actual acceptance and delivery, capture its final tip and configuration and the still-pending edit. If U-B fails, keep L-B blocked and preserve the edit for direction.
5. Start L-B's new local chat from that exact accepted U-B tip with the working-tree edit carried forward. Supply only its controller authorship, exact pending file/values, and unpublished state. L-B reads the new working defaults and makes its normal recommendation.
6. Inspect the recommendation. Explicitly authorize adoption/publication of those exact defaults and separately accept L-B's feature configuration. L-B's Orchestrator commits the config together with its first real initialization task-log checkpoint using explicit paths, then uses normal attempt/delivery handling. No standalone controller commit precedes it. Preserve the real adoption decision in the existing initialization acceptance statement and controller evidence; add no invented event/schema field.
7. Verify L-B's baseline, accepted snapshot, committed defaults, changed paths, normal log trailers and delivery. The master authored the edit; L-B's Orchestrator actually published it. U-B's branch tip, log, and published defaults remain unchanged. Finish U-B delivery checks at its own tip before switching; do not validate its log against the later L-B HEAD.

The helper checks every commit from a feature's baseline through HEAD, including already-pushed commits. An ordinary controller commit in that interval is rejected as unaccounted-for. The unstaged-edit/authorized-successor-initialization sequence avoids that conflict without runtime changes, fake U-B events, or false publisher attribution. Other staged/unstaged/untracked fixtures must remain untouched. A failed initialization push follows ordinary recovery.

### C2. Native assignment and independent overrides

Collect requested and exposed effective settings for each lead and helper. A saved map, prompt request, model self-identification, style, or runtime does not establish native use. Include an assignment differing from its parent where supported.

| Variant | Case and timing | Change |
| --- | --- | --- |
| C2-M | U-M tasks approval boundary, before coding | Different supported Coder model; retain its accepted effort and include it explicitly in the complete assignment. |
| C2-E | L-B later Planner approval boundary after push recovery | Change Planner effort only; retain its accepted model. |
| C2-H | U-S after initialization and meaningful Coder checkpoints, before replacement | Change only the complete helpers assignment; prefer Luna where available. |

For every change, capture the actual decision, persisted `user-override`, checkpoint delivery, and next affected native invocation. Preserve unrelated assignments, assurance, approvals, progress, evidence, logical assignment identity, and counters. In L-B, verify subsequent affected Planner work under the new effort without restarting completed work or approvals. If no supported alternate model accepts the current effort, record the unavailable model-only variant and follow the direction process rather than changing another component silently.

Capabilities apply prospectively. A capability-only change does not invalidate a useful in-flight return or require attribution of earlier work to historical settings. Reuse native contexts when supported; replace them through normal mechanisms only when needed to honor the accepted assignment. Current invocation identity uses `trigger_event_id`, `role`, `attempt`, and optional `context_id`, without `configuration_ref`. The current configuration decision reference exposed by `resume-action` is diagnostic, not dispatch provenance. Keep accepted values, decisions, exposed controls/identity, and subsequent native-use evidence in controller storage; request no execution-segment events or consumer helper/dispatch ledger. Unavailable independent backend telemetry remains a limitation. The helper override moved from L-B to U-S; do not repeat it in L-B or add capability combinations.

### C3. Unavailable capability and accepted inheritance

Use a suitable idle boundary in L-S for at most one known unavailable pending lead assignment; use a bounded supplemental helper variant only if meaningful and supported by the client's observations. Report immediate affected-work pause without simulation, automatic substitution, retry, or assurance change. After the actual result, explicitly select a confirmed supported replacement and observe its next affected invocation. Never intentionally exhaust account usage.

If no unavailable setting can be established, record the limitation and deterministic evidence separately. For explicitly accepted `platform_default`, record exposed concrete settings and limitations. `not_supported` denotes an actually unavailable effort control, not a model name or fallback for an unsupported value.

### C4. Native precedence

In L-M at an idle pre-dispatch boundary, use an owned project-local custom-agent definition only if the client actually supports that route. Record/restore its exact original state and keep the fixture uncommitted. Conflicting effective settings must be reconciled through an authorized compatible assignment or pause, without silent substitution. Never alter personal definitions or the installed skill. With direct spawn controls only, verify that route and leave the custom-definition variant unverified; add no installation system.

### C5. Helper behavior under each lead

Distribute bounded questions across suitable Planner, Architect, Coder, and Reviewer work. Use real interfaces, CLI wiring, a case-folding experiment, or a relevant verification witness. Record owner, purpose, accepted assignment, actual dispatch, sources, observations/inferences/gaps, and lead verification. One helper under one lead does not establish all four.

Coder owns intentional source/test/docs/progress edits. Its helpers explore and execute tests without intentional edits or publication. Test evidence identifies command/selection, actual result, available counts, skipped/unavailable checks, and useful failures. Distinguish expected Red behavioral failure from collection/setup/environment failure. Concise evidence reaches Coder; no full passing transcript or unsupported success claim. Keep tested work stable and reuse compatible helpers; impose no fixed count or helper per task. Controller checks do not substitute for Coder test-helper observations.

Do not require a new helper per test command. At Basic/Standard, fresh applicable test results may be reused after checking the tested source and affected behavior. Progress checkboxes, report-only corrections, or unrelated documentation alone do not require retesting. Leads still verify decision-critical claims and required checks remain mandatory; Maximum retains its required comprehensive fresh work.

If nested delegation is unavailable, permitted Orchestrator-coordinated helper work returns evidence to the owning lead. Unavailable helper settings identify both helper and lead and require direction.

### C6. Context, output, and resumption

Observe a normal Planner approval/handoff boundary in U-B and continue the same chat with its accepted snapshot. Planner suspends at document gates; ordinary Coder checkpoints continue without an interim wrapper or acknowledgement.

For U-S, after multiple meaningful Coder artifact checkpoints and before its completion return:

1. Obtain a coherent yield and establish that affected helpers have finished/stopped. Preserve the actual original baseline, task progress, checkpoint/delivery evidence, and existing handles.
2. Deliver C2-H through the real Orchestrator; validate, record, and publish its actual override before replacement. Capture the override event reference, accepted assignment/current configuration, and delivery. C1-B remains the separate initial-selection observation; do not manufacture invocation configuration lineage.
3. Establish original Orchestrator/Coder/helper liveness before creating a replacement for the same feature/log/branch/project. Prevent duplicate active writers. Send only the bounded [resume prompt](prompts/resume-run.md), including actual override references; no private controller materials.
4. Observe Orchestrator reconcile commit metadata/messages, changed-file names, actual log/native output, and liveness. Use `checkpoint_state.py recent` with cursors beyond the first batch when needed. Orchestrator does not open spec/code bodies or patches; content questions go to the owning role.
5. Recover the recorded override, logical assignment, progress, and original cumulative scope without resetting approvals, findings, counters, grants, or baseline. A capability-only change preserves useful in-flight returns. Seek a fresh Coder only where native controls allow safe replacement; otherwise retain the existing Coder and report fresh-Coder reconstruction Unverified.
6. Observe the next affected native helper invocation after recovery against C2-H. Reuse only compatible helper contexts. A recovered field without observable actual use establishes persistence only, not enforcement.
7. Require the eventual completion wrapper to include pre-interruption work, reversals/amendments, current dispositions, and verification against the original baseline. Distinguish historical recovered checks from new checks; do not repeat settled implementation merely because context changed.

Report Orchestrator and Coder context continuity separately. The controller may inspect bodies to assess this case; that does not relax Orchestrator's boundary. One missed timing/fresh-context attempt stays a limit, not permission to add another feature run. Unknown outcomes and unavailable handles do not establish completion.

### C7. Failure categories and attempt bounds

Observe actual ordinary role failures if they occur: up to three total ordinary attempts preserve trigger/role/attempt identity, then need explicit direction. The controller's one extra ordinary attempt is bounded and not replenished on resume. Model/usage failures, including helper failures, require immediate separate assignment/wait direction. Simulated failures or an explanation of intended behavior are not live evidence; cite existing deterministic tests for variants not reasonably induced.

Distinguish a small missing path, unclear summary, or other report-only correction from unusable output. The owner may correct that return in the same assignment before the dependent gate, reusing applicable checkpoints and tests. Absence of `subagent-error`, a new attempt, repair cycle, empty commit, or retest is not a failure for that routine correction. Do not count routine corrections or inject malformed outputs to obtain coverage. Actual execution failure, unusable output, or repeated inability to provide a usable return still follows bounded failure recovery; this is not unlimited retry authority. A valid adverse review follows finding policy, not invocation-failure handling.

A recording error belongs to the recorder, not the producer, and consumes no producer attempt. The recorder's `invalid_native_output` blocks recording but does not alone classify a small correction versus a genuine failure. Preserve any observed published corruption as a historical failure and obtain actual recovery direction without controller edits to consumer history. Assess old runs against their then-applicable contract; do not erase their failures or mark successful current routine corrections as failures merely for lacking a failure event.

## Cross-role enforcement

### G1. Ownership and execution boundaries

Inspect actor-attributed operations: Planner owns substantive specs/research and their artifact publication; Coder owns implementation/test/docs/progress edits and artifact publication; Orchestrator owns configuration/log/known issues and log publication; reviewers remain read-only; helpers do not intentionally edit or publish. An actual source/spec contradiction returns through Orchestrator, or use a bounded standalone case if absent live.

Observe explicit coding authority, meaningful Red failures, Green plus owning documentation, progress-only checkboxes with unchanged content version/history, planned Test-Maintenance before Verification, and no repairs hidden inside Verification. Preserve Refactor/EdgeCase boundaries when used without inventing tasks for coverage. Every small feature remains an ordinary assignment; natural task groups do not justify phases.

Planning still needs concrete design and executable tasks, grouped by coherent behavior rather than artificial per-edit steps. Diagrams serve useful explanation, not a quota. Apply C5's test-result and helper-context reuse rules without relaxing Red/Green, required checks, or assurance-specific review depth.

### G2. Review-disposition policies

The matrix uses `spec_user_code_auto` except L-B (`all_user`) and I-S (`within_scope_auto`). For an actual finding requiring repair/disposition, observe the decision and subsequent producer dispatch: specification disposition waits under the default, both repair paths wait under all-user, and routine in-scope repairs may proceed under within-scope-auto. Default nit-only acceptance needs no such gate under any policy and does not demonstrate repair-policy enforcement. An explicit actual user request remains binding under A3's existing repair path. A recorded policy string alone is not enforcement evidence.

All retain material approvals, product decisions, required failures, loop limits, and operational authority. If a bounded real gate permits an explicit policy override, record and observe it through ordinary controls; otherwise retain that variant as a gap. Never manufacture findings to force policy coverage.

### G3. Drafts, versions, and consolidated outputs

L-B's zero-limit request arrives after requirements v1 is returned and before its approval. Verify a recorded material clarification, new version/cause, the same unfinished Planner cycle, and approval before dependent design. A real editorial correction after approval preserves the genuine approval basis; do not invent one. Material post-approval changes invalidate affected approvals and restart at the earliest affected artifact.

Required specifications retain content versions and concise final Revision History without status or Git metadata. Routine body reads use the spec reader to exclude that history. Consolidated handoffs contain the complete current scope, decisions, rationale, dispositions, and evidence rather than only the last delta or a conversation transcript.

Planner publishes each draft/revision before its return. Orchestrator validates and publishes the log update, requests exact-version approval, then publishes approval before authorizing the next document. Architect/Reviewer returns are recorded/checkpointed before dependent work. Every authoritative logical update needs publication; related events may share one, but never batch away drafts or gates.

On the normal path, requirements and design each retain their sequential incremental return and real approval. The final tasks draft supplies one consolidated Planner return before tasks approval. Recording it produces `spec-updated` with `spec_in_progress` while approval is pending. Actual unchanged tasks approval via `spec-artifact-approved`, with valid earlier approvals and current decision context, permits `spec_ready` and Architect using that same immutable return plus the separately recorded approval context. Do not request another Planner consolidation, duplicate wrapper, invented prior approval, or obsolete readiness/approval event. Material feedback still requires the appropriate revised handoff and approval.

Coder publishes Planner's natural groups without per-task commits, per-group reviews, interim wrappers, or automatic full-suite reruns solely for a checkpoint. Artifact-only commits validly omit log-event ranges; `coding-updated` records coordination details rather than an interim completion wrapper. Consolidated Planner/Coder completion returns contain actual complete JSON and cumulative current scope; a pointer is not a handoff. Current compact schemas allow irrelevant optional fields to be omitted. Coder reports one cumulative changed/new/deleted inventory and checks once, retaining useful downstream information. Embedded reviews derive reviewed versions/commit from the source handoff and previous review/stage from their start; standalone returns retain explicit standalone context and reviewed artifacts/commit/review kind.

The owning Orchestrator feeds the one actual native wrapper JSON to `validate_orchestrator_artifacts.py record-handoff - --log <AUTHORITATIVE_LOG> [--workspace <CONSUMER_ROOT>]`. This explicit writer derives causal/state metadata, validates the candidate, and checks write/readback. UTF-8 stdin is required; PowerShell pipelines carrying literal Unicode set `$OutputEncoding = [System.Text.UTF8Encoding]::new($false)`. Do not require a second agent-authored payload, routine consumer wrapper files/snapshots, transport-proof steps, or a full-log reread after every handoff. The controller/evidence collector never runs this writer against consumer history.

When complete captures exist, compare the actual accepted native return's decoded JSON with its recorded object, including Unicode. Formatting or escaped Unicode can differ while the decoded value agrees; changed string values, types, array order, or Unicode normalization do not establish identical recording. Preserve originals, including malformed returns and any routine corrected return, before interpretation. A clipped observer transcript cannot prove the producer omitted content: exact-return compliance remains Unverified. Apply C7's correction/failure distinctions and the contract in force at the time to historical evidence.

### G4. Git checkpoint and recovery

#### G4-A. Unrelated changes

In U-B at the coordinated tasks boundary, capture the original file/index state and create one staged new text fixture, one unstaged modification to an existing tracked file, and one separate untracked file. Use declared controller-owned content; for the tracked fixture, select a non-application input unrelated to U-B such as the future ignore-case proposal and append a harmless identifying HTML comment. Preserve its original bytes/hash and exact index entry. Do not edit application behavior or real user files. These fixture changes stay outside every workflow checkpoint; never describe an untracked file as an unstaged tracked edit. After U-B verification and at an idle boundary, restore only these owned fixture changes to their recorded original states so later inputs remain canonical, recording the restoration externally. Do not restore the separate C1-C defaults edit, which must carry into L-B. Do not clean unexpected artifacts.

#### G4-B. Planner artifact push failure

Use L-B's first requirements-return boundary while Planner and Git are idle. Before sending its zero-limit clarification, prepare an owned temporary `pre-receive` hook for the allocated Basic bare remote, only if no existing hook would be replaced. Pin the selected feature ref and hash the hook contents. It reads each proposed ref update, permits other refs and Orchestrator log tips, and rejects the selected ref only when the new tip's parsed trailers identify this feature, `Orchestrator-Checkpoint: artifacts`, and `Orchestrator-Role: Planner`. Handle a deletion without looking up a nonexistent commit. Do not use a blanket nonzero hook that rejects the earlier Orchestrator request checkpoint.

First verify the actual Git-shell hook mechanism in a small synthetic repository/bare remote under `CONTROL_ROOT/fixtures`: a log-tip push is accepted, a matching Planner-artifact tip is rejected, and an unrelated ref is accepted. Record these as fixture evidence only. If execution is unavailable, leave live coverage unverified and do not change remote URLs or invent a rejection.

Install the verified fixture, then deliver the ordinary zero-limit clarification. Observe the Orchestrator publish that real request and the Planner's subsequent revised-artifact push encounter the hook. Record actual publisher/invocation, exit/result, local commit and attempt journal, unchanged remote, and global pause. If another publisher fails, report what occurred and the intended coverage gap.

Verify and remove only the owned hook after the rejection, preserving unrelated remote state. Reconcile the latest actual failed/uncertain attempt and send one exact recovery grant. Observe Orchestrator commit the real recovery authorization before one push carrying outstanding work and authority. Success has no receipt/event/extra commit/second push. Another failure or uncertainty stops for direction. An approval system preventing execution is not a failed push.

Real interrupted/final-checkpoint variants can use already available bounded observations; otherwise cite deterministic evidence separately. Unknown attempts retain identity and consume their allowance, with no invented failure code or replenished authorization.

### G5. Dependency-scoped blockers

Only if real approved tasks contain an operation and pending independent work, use one owned fixture at an idle boundary to make that operation unavailable. Record intended recovery. Observe task/operation IDs, evidence, attempts, dependencies, pending independent tasks, and needed direction. Completed work is progress, not pending independent work. Restore only the fixture. Do not invent external services or an operational framework for this CLI. Prefer a bounded standalone blocked-task example for an otherwise absent case. Failed checkpoint delivery still globally pauses work.

### G6. Acceptance and compatibility

Use U-B for the explicit squash-message-only probe after Reviewer acceptance. It grants no final feature acceptance. Inspect behavior, checks, known issues, and their provenance before the separate acceptance message; then observe final delivery and a total-diff squash message. Every other feature still requires explicit final acceptance. No agent merges or claims skipped checks passed.

Use a synthetic copy of a log under control fixtures for missing/pre-2.0/different-major/unsupported-newer entry cases. A bounded read-only entry check must stop before mutation with no migration. Do not corrupt live logs or present synthetic history as user-approved work.

## Standalone corpus and evidence gaps

Prepare only a named missing observation, using small copies of actual sources/specs and coherent provenance under `CONTROL_ROOT/fixtures`. Validate document versions, revision-history order, task references, and relevant wrapper/log semantics before invocation. Preserve the unchanged baseline and prior real standalone output. Record the intentional injected defect in the private controller evidence; unrelated invalid metadata must not determine the result.

| Fixture | Intended factual observation |
| --- | --- |
| Requirement/design contradiction | Exact uniqueness is approved but fixture design folds case. |
| Missing wiring | A function option lacks its CLI path or meaningful integration witness. |
| Implementation defect | A fixture change collapses `A` and `a` under plain `--unique`; establish the failing witness first. |
| Optional hardening | Nonzero input failure is required; friendly diagnostic wording is not. |
| Preference | A harmless naming/comment improvement assessed proportionately. |

Use [role-exercise.md](prompts/role-exercise.md) with actual supported native settings and standalone context. Reviewer/Architect are read-only; producer repairs stay within explicitly granted fixture scope. Never insert these outputs into a consumer log or instruct a verdict/finding count. Preserve original returns and actual decisions for any follow-up. No standalone native phase exercises are authorized.

## Deterministic phase coverage

Native implementation phases are Deferred/Not run. The twelve ordinary cases cannot establish large-feature phase selection, fresh successive phase Coders, or actual intermediate Reviewer settings. Keep that limit even if all deterministic tests pass.

The following inventory identifies current development-test evidence, not a standing claim of passing results. At each run, record tested source fingerprints, exact test identities, actual command/results, valid/invalid cases, and remaining gaps. These tests belong to corrections work; the master must not edit them or the runtime to fill a gap.

| Requirement | Current behavioral test identities | Coverage limit/dependency |
| --- | --- | --- |
| Basic skips intermediate review; Standard uses Basic stage review; Maximum uses Standard stage review; final review retains feature assurance with no last-phase duplicate | `PhaseTests.test_all_levels_finish_only_through_whole_feature_review`; `test_unreviewed_phase_cannot_advance_and_last_has_no_intermediate_review` in [test_implementation_phases.py](../test_implementation_phases.py) | Recorded behavior only; no native stage invocation. |
| Same-model effort reductions `max` to `high`, `xhigh` to `medium`, and `high` to `low`; persisted assignments and explicit unmapped/unavailable handling | `PhaseTests.test_basic_needs_assignment_only_after_assurance_requires_review`; `PhasedFlow` uses `high`/`low` | Unmapped/missing assignment behavior is exercised. No focused behavioral cases were identified for `max` to `high`, `xhigh` to `medium`, wrong mapped/same-model assignments, or native unavailability of derived effort. Retain as corrections-work dependencies. |
| Intermediate repair allowances of one pair in Standard and two in Maximum; separate final policy; counts retained on replacement/configuration changes | `PhaseTests.test_phase_repair_allowance_survives_context_and_configuration_changes`; `test_final_review_repairs_cannot_use_an_earlier_phase_review`; `test_assurance_catchup_restores_suspended_later_coder_without_new_assignment` | Standard's one-cycle allowance is directly exercised; a dedicated Maximum two-cycle intermediate-limit boundary remains a dependency. Final-policy evidence also comes from [test_recovery_and_reviews.py](../test_recovery_and_reviews.py). |
| Scope, task partition, phase plans and pending recovery | `PhaseTests.test_task_partition_and_scope_are_enforced`; `test_changed_phase_boundaries_require_tasks_revision_and_approval`; `test_approved_revision_rebinds_unfinished_phase_and_preserves_completed_history`; `test_multiple_completed_phases_catch_up_before_restoring_active_writer` | Assertions cover represented histories; actual native reads/progress require observation. |
| Stage sufficiency across assurance changes and final handoff | `PhaseTests.test_inflight_intermediate_review_can_return_after_basic_override`; `test_phase_gap_after_final_handoff_returns_to_final_review_without_reopening_coding`; `test_assurance_catchup_restores_suspended_later_coder_without_new_assignment` | Do not conflate intermediate readiness with whole-feature approval. |
| Final Coder consolidation against the original feature baseline and ownership of final-review repairs, including earlier-phase work | `PhaseTests.test_final_review_repairs_cannot_use_an_earlier_phase_review`; `test_final_assurance_reconsiders_policy_limitation_without_erasing_provenance`; `test_consolidation_cannot_replace_the_approved_phase_plan` | Representable scope/evidence checks do not prove native Coder synthesis or Reviewer coverage. |

Related ordinary-path evidence includes `CheckpointTests.test_coder_artifact_checkpoints_need_no_interim_wrapper`, `test_artifact_delivery_and_uncertain_recovery_after_delivered_log`, `test_recent_history_paginates_metadata_without_bodies_and_preserves_dirty_state`, and `test_retry_authorization_is_committed_before_one_push_without_receipt` in [test_checkpoint.py](../test_checkpoint.py). Body reading and actual-return stdin checks are in [test_distribution.py](../test_distribution.py). A suite pass, instruction-text match, or valid example JSON does not fill absent behavioral or live coverage.

The current ordinary-path corrections also have these source-inspected behavioral dependencies. Record actual execution results against the tested runtime/test content, including relevant staged and unstaged changes; a HEAD hash alone does not identify a dirty source. These references are not a claim that the tests ran or that native compliance passed:

- **Prospective settings and recovery:** `ProtocolTests.test_approved_planner_document_continues_under_new_effort` checks preserved approved work and Planner continuation under new effort; `test_helper_override_preserves_lead_and_changes_subsequent_assignment` checks recorded helper settings and preserved lead identity; `test_inflight_review_survives_capability_change` checks a useful in-flight review remains valid in [test_protocol.py](../test_protocol.py). `RecoveryAndReviewTests.test_context_replacement_keeps_coder_assignment_and_authority` checks Coder identity, authority, baseline, and counters across override/replacement in [test_recovery_and_reviews.py](../test_recovery_and_reviews.py). None proves actual next native use or fresh-Coder reconstruction.
- **One consolidated tasks handoff and compact returns:** `ProtocolTests.test_consolidated_tasks_need_approval_and_current_decision_context`, `test_delivered_prefixes_resume_at_expected_workflow_boundaries`, and `test_optional_collections_default_without_changing_captured_returns` check approval/context readiness, ordinary resume boundaries, and preserved optional-field omission. `DistributionTests.test_recorder_derives_causal_metadata_and_readiness` checks final tasks recording as `spec-updated`/`spec_in_progress`, then actual approval enabling Architect. These recorded transitions do not establish native document-reading depth or absence of an unnecessary live recall.
- **Faithful recording:** `DistributionTests.test_record_handoff_preserves_literal_unicode_under_non_utf8_stdio`, `test_powershell_utf8_pipeline_preserves_actual_return`, `test_native_value_comparison_preserves_types_order_and_unicode`, and `test_recording_detects_concurrent_changes_and_failed_readback` in [test_distribution.py](../test_distribution.py) exercise actual recorder input, decoded values, and recording-error detection. The PowerShell case can skip if its executable is unavailable; report that result rather than claiming a pass. Reader/stdin tests alone do not establish these guarantees, and complete native captures remain necessary for live comparison.
- **Correction versus failure:** `DistributionTests.test_small_output_correction_keeps_assignment_and_checkpoint` and `test_invalid_native_return_does_not_write_or_invent_failure` check correction without new producer failure accounting and invalid-input rejection. `RecoveryAndReviewTests.test_unusable_output_retry_preserves_assignment_and_failure_count` and `test_explicit_retry_exhaustion_survives_override_and_replacement` check genuine failure bounds and continuity. Runtime rejection alone does not establish how a native agent classifies a small reporting correction.
- **Nit acceptance and actual user authority:** `RecoveryAndReviewTests.test_nit_only_initial_and_repair_reviews_accept_without_extra_decisions` checks default nit-only acceptance; `test_explicit_user_nit_fix_uses_existing_repair_path` checks the explicit user exception across both review roles, levels, and policies, preserving it against policy-only or matching producer responses until resolved; `test_disposition_without_authority_is_only_a_proposal` checks decision authority. Live proportionality, review quality, and applicable test/helper reuse remain separate observations, not inferred from test names or valid logs.
