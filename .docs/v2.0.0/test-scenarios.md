# Master agent scenario instructions

Read with [test-runbook.md](test-runbook.md). This file is the operator's private checklist, not a prompt for the workflow under test. Render actual messages from [test-decisions.md](prompts/test-decisions.md). Product inputs are the separate [proposals](proposals/README.md).

## Execution schedule

| Run | Timed action by the master | Main coverage |
| --- | --- | --- |
| Setup | Allocate a fresh run; build/verify the baseline once; seed three local remotes/clones; discover native settings. | Installation/setup, identical source baseline, actual capability availability. |
| U-B | Receive setup and feature recommendations; accept the valid recommended capability map unchanged for C1-A and select Basic through the real gates. Observe normal gates and probe the distinction between squash-message request and final acceptance. | A1/A3/A4, C1-A/C2, G1/G2/G3/G6. |
| U-S | Receive recommendations; choose at least one different supported role assignment for C1-B and select Standard. Request one concrete helper investigation during a suitable lead phase. After a delivered draft or coding update, let the turn finish and resume from that boundary. | A1/A5, C1-B/C2/C5/C6, G1/G3. |
| U-M | Receive recommendations, then select Maximum and accept or choose supported capabilities within scope. Observe source/traceability/check evidence, producer responses, and any actual review follow-up. | A1/A2/A3/A4/A5, C2, G1/G3. |
| L-B | Start from accepted U-B; select `all_user`. After first requirements return, request zero-limit support. Exercise one role/helper capability variation at the next appropriate idle boundary. Cause one controlled failed push after recording a coherent update, then authorize its single recovery push only after restoration. | A2/A3, C2/C3/C6, G2/G3/G4. |
| I-S | Start from accepted U-S; select `within_scope_auto`. Request bounded helper research on the declared case-folding behavior. Observe a lower-assurance initial review, then raise assurance to Maximum while it is actually running if timing permits. | A5/A6, C2/C5, G2/G3. |
| Targeted cases | Fill important missing observations using a real captured checkpoint or a small clearly labeled standalone fixture. Try each selected variant once; do not rerun until random review output matches an expected script. | Remaining scope, escalation, configuration, blockers, and role cases below. |

Apply each stimulus once at its defined boundary. Pause dependent actions while waiting for the real result. Keep original delivered prompts and replies in evidence. If a core run exposes a blocking workflow defect, preserve it and stop that feature; do not build its follow-up on an unaccepted predecessor. Continue independent lanes and report the missing dependent coverage.

## Assurance scenarios

### A1. Complete initial review

Observe Architect and Reviewer in all three core runs. The first Architect pass covers all three current spec bodies and relevant actual source; the first Reviewer pass covers the relevant implementation against the explicit baseline and approved spec. Record actual reads/checks, not just the wrapper's scope label. Basic does not permit omitting required coverage. Roles remain read-only and Orchestrator provides the full authoritative handoff.

If a real producer corrects a seeded concern before review, that is not a review failure. Use the standalone corpus below to test defect detection separately; never force the live producer to leave a bug.

### A2. Follow-up scope

Observe real repair/re-review pairs when they occur. A previous review plus a small changed fixture may exercise missing standalone variants for either review role.

| Actual repair class | Basic | Standard | Maximum |
| --- | --- | --- | --- |
| Editorial or test/documentation | Normally focused | Focused | Comprehensive |
| Bounded correctness | Start focused; expand for practical impact | Affected behavior and neighboring contracts | Comprehensive |
| Architectural/systemic | Expand as consequences require | Full relevant review | Comprehensive |

Check `repair_class`, `changed_surfaces`, `review_scope`, `scope_reason`, and actual work. A fresh invocation alone is not a reason to broaden Basic/Standard work. Maximum must perform its applicable comprehensive obligations, including actual named interfaces, traceability, wiring witnesses, boundaries, and checks, even when the immediate repair is small. Preserving agent context does not excuse omitted work or require creating a fresh agent.

### A3. Classification and remediation

For both review roles, check factual behavior, triggering conditions, practical consequences, evidence, and acceptance-standard rationale. For both producers, check the response to those actual findings:

- A demonstrated violation of approved behavior stays a defect at every level. Orchestrator cannot waive a must-fix independently.
- Basic may retain an adequate result with rationale; ease of fixing a nit alone is insufficient.
- Standard weighs benefit and total cost, with a stronger presumption toward fixing worthwhile should-fix findings.
- Maximum fixes straightforward nits and requires concrete risk/scope grounds for deferral. Time/priority alone is insufficient.
- Stable finding IDs and settled dispositions persist unless new evidence, changed behavior, or a relevant revisit condition justifies reconsideration. Applicable retained issues appear in `known-issues.md` with their authority and impact.

No required finding count or exact severity applies to a genuinely discretionary improvement. Distinguish a product violation from hardening/preferences. A correct factual observation classified with a supported rationale can pass without matching another run's phrasing.

### A4. Repair-cycle and stall gates

Record completed producer-repair/re-review pairs separately for specs and code. Basic asks before pair 2 if further repair is needed; Standard asks before pair 3. Initial reviews, interim drafts, checkpoints, and ordinary invocation retries do not count. Acceptance at the boundary does not require an unnecessary continuation question.

The same must-fix identities across two reviews without meaningful progress, or more than three revision cycles without status improvement, trigger the applicable stalled-loop safeguard, including at Maximum. Observe the master receiving the gate before any further producer repair. A permitted generic continuation grants one pair; settings changes and resumption do not reset the counts.

Do not deliberately produce bad repairs to force a cycle count. If a boundary never occurs, record live coverage as unverified and cite the relevant executable tests separately. The master can stop that case after observing a correct gate without accepting the unfinished feature.

### A5. Research and evidence continuity

Capture a real decision-relevant observation with source context, experiment/results, separate inference, and gaps. U-S/I-S can use exact comparison versus `str.casefold()` and the stated Unicode/whitespace examples. On resumption, Basic/Standard check source/assumption applicability and reuse valid completed evidence, repeating affected/incomplete investigation. Maximum actively revalidates decision-critical observations even if sources appear unchanged.

Use a targeted native role exercise for an assurance level not naturally covered. Then change one relevant fixture assumption/source and verify affected claims are rechecked at every level. Leads verify decisive helper claims; they do not copy confidence statements as evidence. Preserve useful research; only Planner substantively changes it, and unchanged conclusions need not cause gratuitous rewrites.

### A6. Assurance overrides and in-flight review

During I-S, watch for an actual Standard Architect invocation and send the Maximum override while it is running. Its invocation must genuinely predate the override at lower assurance. On return it keeps that basis, and Orchestrator requires sufficient catch-up before coding. Use a separate actual initial Reviewer invocation at lower assurance for the corresponding final-completion variant; return assurance to Standard through a real prior override if needed.

Also observe a downward override after a completed review. It preserves evidence and counters and does not repeat completed work automatically or change capability. If the review completed before the message arrived, label it a post-review override case; do not claim the race variant passed. One missed timing attempt is a coverage limit, not justification for many full reruns.

## Capability scenarios

These cases verify configuration enforcement and persistence. Use different supported models and reasoning efforts to make assignment errors observable; assess each against its accepted settings. Do not rank capability combinations by quality or speed, or repeat runs to find a better-performing model.

### C1. Defaults and frozen feature settings

Observe missing `.orchestrator-flow.json` setup in the core runs. Orchestrator recommends supported defaults and obtains a decision, then recommends feature settings based on the proposal/defaults before Planner starts. Preserve the recommendation, delegated decision, and their scopes as separate evidence. Exercise both required initial capability paths and report them separately:

| Case | Planned run | Master's decision | Required evidence |
| --- | --- | --- | --- |
| C1-A: Keep recommendation | U-B | Accept the valid recommended role/helper capability map unchanged. Select the scenario's assurance and review policy separately. | The complete accepted capability map matches the recommendation, is persisted in the initial feature snapshot, and is applied by actual native invocations. |
| C1-B: Choose alternative | U-S | Before feature initialization, select at least one supported role assignment with a different model or effort from the recommendation; preserve unselected assignments. | The initial feature snapshot and affected native invocation use the master's selected value, with no silent reversion to the recommendation or unintended changes elsewhere. |

Both paths must preserve the accepted settings across later invocations and resumption. Reuse planned resume boundaries or one bounded pause/resume at a delivered checkpoint for the case that still needs it. A later override under C2 does not substitute for either initial-choice case. An alternative selected before initialization belongs in the initial accepted configuration; do not manufacture a `user-override` event before an accepted feature configuration exists.

Do not approve an invalid or unavailable recommendation merely to pass C1-A, or relabel a corrected selection as unchanged acceptance. Report the failure or unavailable coverage accurately. Do not force a common capability map across runs, require a recommendation to match the operator's private intended choice, or grade it for choosing the best model.

Select at least one feature setting differing from its repository defaults and verify it does not rewrite those defaults. During a later idle boundary, change only future-feature repository defaults through a real controller message, then resume the existing feature. It must keep its accepted snapshot. At the next feature, verify the new defaults are considered in its recommendation, then select the scenario's intended feature settings explicitly.

Check complete accepted initial settings in top-level fields and the first start event. Review policy is feature-level. Configure and vary the five assignments through schema-valid role maps; the master does not patch the feature log directly.

### C2. Native assignment and independent overrides

Collect actual dispatch/effective settings for Planner, Architect, Coder, Reviewer, and helpers. At least one supported explicit assignment should differ from the parent to expose accidental inheritance. Capability consists of per-role model/effort assignments; Basic/Standard/Maximum are assurance labels, not model presets.

In L-B or a suitable later boundary, exercise an effort-only change, a model change with an explicit supported effort, and a helper-only change. Reach the next affected invocation. Each change preserves unrelated assignments, assurance, phase, approvals, completed evidence, and counters. Resume once after a change to check persistence. If the client requires a new native handle, verify bounded context transfers with the new capability.

For each exercised assignment, connect the accepted decision to the persisted feature settings and the actual native invocation. After an override or resumption, inspect the next affected invocation to establish that the setting remains in effect; a correctly saved field alone does not establish enforcement. Distinguish invocations already in flight under earlier settings from subsequent invocations governed by the new assignment.

Check requested versus observable effective settings. A model's self-description, output style, or runtime is not proof. Missing native observability is unverified configuration enforcement, even if artifacts otherwise pass.

### C3. Unavailable capability and accepted inheritance

At an idle boundary, select a known unavailable model/effort for one pending lead; separately exercise a helper if practical. Orchestrator must report/pause affected work, without virtual execution, automatic substitution/retry, or implicit assurance change. After observing the pause, explicitly select a confirmed supported alternative, checkpoint the override, and resume only the affected work. Do not exhaust account usage intentionally.

If no unavailable combination can be established, do not fabricate a tool rejection. Record the live gap and the deterministic availability tests separately. For explicitly accepted `platform_default`, record concrete effective settings when exposed and acknowledged limits. `not_supported` is only for an actually unavailable effort control, never a model name or an escape from an unsupported requested value.

### C4. Native precedence

If this client uses custom agent definitions, prepare only a project-local test definition with an assignment conflicting with the feature snapshot, while no affected role is active. The runner must resolve an authorized compatible assignment or pause for direction before dependent work. It must not silently accept different effective settings. Preserve and restore only the controller-owned fixture; never alter personal definitions or the installed skill.

For clients using direct spawn controls only, verify that route and report the custom-definition variant unverified. Do not introduce a new installation system for this test. Never treat a desired setting in prompt prose as native configuration.

### C5. Helper behavior under each lead

Distribute bounded helper requests across suitable Planner, Architect, Coder, and Reviewer work. Questions can concern existing CLI-to-function wiring, a source interface claim, case-folding experiment evidence, or whether a test exercises the actual option path. Each must have concrete sources and a decision the lead owns.

Check helper assignment, actual dispatch, source observations/inferences/gaps, and lead verification. Helpers cannot replace the lead's authoritative output or own logs/checkpoints. If nested delegation is unavailable, permitted Orchestrator-coordinated helper work returns evidence to the lead. Unavailable helper settings identify both helper and owning role and require direction. Do not mark all four leads covered after observing one helper invocation.

### C6. Context, output, and resumption

At one real Planner update and one Coder update, capture the returned output/checkpoint boundary and let the runner yield. Use [resume-run.md](prompts/resume-run.md); for fresh-context coverage, use an explicitly created replacement local chat only after checking prior role liveness.

Orchestrator reconciles native output and Git before launching another writer, preserves completed outputs/settings, and reuses the role handle where supported. Producers suspend while their update is checkpointed. Unknown outcomes stay unknown. Unavailable native context is recorded honestly and triggers bounded recovery, not recreation of all historical decisions or duplicate completed output.

### C7. Failure categories and attempt bounds

Observe an actual recoverable ordinary role error if one occurs: up to three total ordinary attempts keep their trigger/requestor and attempt identity, then require direction. One granted extra attempt is bounded and not replenished on resume. Model/usage failures require immediate direction instead; they are not ordinary retry opportunities. Include owning-role/failed-helper identity where relevant.

Use existing deterministic tests for failure classes that cannot reasonably be induced. Simulated results or a statement describing what would happen do not prove a real client's failure handling. Stop at the runbook's bounded allowance.

## Cross-role enforcement

### G1. Ownership and execution boundaries

Inspect changes/commands by actor. Planner owns substantive specs/research; Coder owns approved implementation and completion accounting; Architect/Reviewer stay read-only; Orchestrator owns configuration/log/known issues and Git. No role silently takes another's work. Have an actual source/spec contradiction raised through Orchestrator rather than allow Coder to rewrite the contract; use a small standalone case if no live contradiction occurs.

Check explicit initial coding authority, Red tests failing for the intended reason, Green implementation and its owning documentation, progress-only task edits preserving real approval basis, planned Test-Maintenance before Verification, and Verification without hidden repairs. Observe Refactor/EdgeCase boundaries when actually used; do not invent extra tasks just to populate coverage. Required failures or incomplete tasks cannot silently become completion.

### G2. Review-disposition policies

Core runs use `spec_user_code_auto`: user/delegate disposition before Planner repair, with routine in-scope code repairs allowed under existing authority. L-B uses `all_user`: both repair paths wait for disposition. I-S uses `within_scope_auto`: both can make routine approved in-scope repairs. Observe an actual finding and the next producer dispatch; merely recording the policy string is insufficient.

All policies retain material artifact approvals, product decisions, must-fix exceptions, loop limits, and new operational authority. Test an explicit policy override at a valid boundary and its persistence on resume. The master cannot manufacture findings to force a gate; record absent repair-path coverage honestly.

### G3. Drafts, versions, and consolidated outputs

L-B's zero-limit request is a material product clarification during drafting. Check the new requirements version, recorded request and cause, same drafting-cycle continuity, and approval before dependent work. Select a real editorial correction after an approval if one exists; it must preserve the actual approval basis without a gratuitous fresh approval. Material post-approval changes invalidate affected approvals and start at the earliest affected artifact.

Each completed logical update is checkpointed, including requests and interim drafts. Required specs have content versions and concise final Revision History, without status/Git metadata. Routine body reads exclude that history through the helper. Consolidated Planner/Coder handoffs cover the complete current scope, decisions, rationale, dispositions, and evidence, not only the last delta or an appended conversation transcript.

### G4. Git checkpoint and recovery

Observe normal local pushes, event trailers, and deliberately Red work. In a coordinated idle interval create one controller-owned unrelated staged file and a separate unstaged file in the test repo; record their contents/index state. They must remain untouched and outside workflow checkpoints. Do not use real user files as the fixture.

For one controlled failure in L-B, use a normal pending document-approval gate while the runner and Git are idle. Before sending the approval, add a temporary rejecting `pre-receive` hook to its allocated bare remote only if no hook already exists. The hook is a small Git-shell script returning a nonzero status with a clear test message; verify Git can execute it in this environment before claiming the failure was induced. If the document qualifies for approval, send its ordinary exact-version approval from the prompt catalogue. Its normal checkpoint push should encounter the rejection. This approval does not grant retry authority.

Observe the real rejected push, local commit/failure record, unchanged remote, and global pause including writers. Remove only the exact controller-owned hook after checking its path/content; preserve all unrelated remote state. Send the one-push recovery message only after restoration and discovery of the actual latest attempt. Observe authorization committed before one push carrying the outstanding work plus authority. Success produces no receipt event/commit or second push. Another failure stops the case at the runbook's limit.

If hooks cannot be used, record that limit; do not make persistent remote/configuration changes or invent a push error. A real interrupted-attempt variant and final-checkpoint failure variant may be exercised from coherent captured/live boundaries when practical. Reconcile Git first, preserve uncertainty without inventing failure results, and require fresh one-push authority. Otherwise cite the automated recovery evidence separately.

### G5. Dependency-scoped blockers

When real approved tasks contain an operation and independent work, make only that operation unavailable through an owned fixture, with its intended recovery recorded. The role describes evidence, attempts, dependencies, independent tasks, and required direction. Orchestrator pauses the operation/dependents and permits independent approved work. Restore only the owned fixture afterward.

Do not invent external services or an elaborate blocked-operation framework for the tiny CLI. If this does not naturally yield a meaningful live case, use a bounded standalone blocked-task exercise and retain the separate deterministic reducer evidence. G4's failed-push global pause still overrides otherwise independent work.

### G6. Acceptance and compatibility

After actual Reviewer acceptance, inspect any legitimately retained lesser issue and its known-issue provenance. Send the squash-message-only probe without final acceptance; completion must not be inferred. Then, if required behavior/checks and allowed dispositions are satisfactory, explicitly accept and observe final checkpoint delivery and a total-diff squash message. No agent merges into `main` or claims a skipped check passed.

For unsupported-history entry, use an explicitly synthetic copy of a log under the control fixtures, with a missing/pre-2.0/different-major version, and a separate bounded read-only entry exercise. Confirm stop before mutation and no auto-migration. Do not corrupt a live feature log or disguise synthetic records as a past user-approved feature.

## Standalone corpus and coverage gaps

The master prepares small copies of actual source/specs under `CONTROL_ROOT/fixtures`, records provenance, and keeps an answer key out of the role prompt. Use [role-exercise.md](prompts/role-exercise.md) with native configured roles; reviews are read-only and any producer repair is explicitly limited to fixture files. These exercises never write or backfill a consumer task log.

Prepare only examples needed to fill observed gaps:

| Example | Factual seed and expected assessment |
| --- | --- |
| Requirement/design contradiction | Exact case-sensitive uniqueness is approved but fixture design folds case. Architect should identify the real contradiction. |
| Missing wiring | Fixture tasks/code add a function option but omit its CLI path or meaningful integration witness. Trace the actual paths rather than accept a wrapper claim. |
| Implementation defect | A small fixture change collapses `A` and `a` under plain `--unique`. Confirm the actual failing witness before review. |
| Optional hardening | Input contract requires nonzero failure but not friendly diagnostic formatting. A proposed nicer message must not be mislabeled as an already violated requirement. |
| Preference | A concrete, harmless naming/comment improvement. Test assurance-appropriate response without forcing identical severity or prose. |

Keep an unchanged fixture and prior native review for a bounded repair/follow-up comparison. Check both leads and producers where applicable, with stable identities and actual decisions. Changed fixture facts are test data, not fabricated historical approvals. Do not have the master write the desired review result or instruct a role to return a particular acceptance verdict.

Every scenario above has a result in the final report, including roles/variants not exercised. Deterministic gates that did not occur live remain clearly separate. Stop after the planned bounded attempts; a coverage report with honest gaps is more useful than an expensive sequence designed to force every box to say Pass.
