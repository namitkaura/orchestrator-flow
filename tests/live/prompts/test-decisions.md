# Master decision and stimulus messages

Render one message at its actual gate; never send this catalogue to a runner. Consult [the runbook decision table](../runbook.md#bounded-delegated-decisions) and [scenario timing](../scenarios.md). Inspect the actual output first and save the delivered decision plus its source/delivery reference outside the consumer repository.

Substitution checklist:

- Prefix each message with the rendered `RUN_ID` and the delegated-authority statement below.
- Fill only the selected message's placeholders, using actual recommendations, full supported capability maps, prior/new assignments, file versions, hashes, finding IDs, attempt IDs, and evidence references. Preserve the recommendation separately from the decision.
- State a decision's real operational/product rationale. Keep case labels, hidden expected outcomes, planned failures, and private controller commentary out of the delivered text.
- Check the manifest for consumed grants. A template is neither advance approval nor a replenished allowance. Never send unresolved placeholders or the instructions surrounding a quoted message.

> Master test decision under the human's delegated test authority for {{RUN_ID}}. This decision is by the authorized test controller within the bounds of the initial test request.

## Accept or select repository defaults

After the actual missing-default recommendation, accept or choose supported values. Review policy is feature-level and must not be added to repository defaults. Preserve any genuine human assignment. Do not invent a pre-initialization task-log event.

> In response to your repository-default recommendation {{RECOMMENDATION_REF}}, select assurance {{ASSURANCE}} and these supported native role/helper assignments: {{CAPABILITY_MAP}}. Rationale and accepted native limitations: {{DECISION_RATIONALE_AND_LIMITATIONS}}. Establish these repository defaults through the normal initialization checkpoint. This does not yet accept the feature configuration.

## Accept or select feature configuration

Wait for the actual feature recommendation. For U-B C1-A accept the complete valid recommended capability map unchanged. For U-S C1-B change one supported initial assignment, preferably a different supported effort on the same model; use a supported alternate model only if necessary. An invalid recommendation corrected before acceptance does not pass C1-A. Human constraints take priority; unsupported or unobservable variations retain their limitations.

### Keep recommended capabilities

> In response to your feature recommendation {{RECOMMENDATION_REF}}, accept your complete role/helper capability map unchanged for feature {{FEATURE_ID}}: {{RECOMMENDED_CAPABILITY_MAP}}. Select assurance {{ASSURANCE}} and review policy {{REVIEW_POLICY}}. Rationale: {{DECISION_RATIONALE}}. Record the accepted feature configuration before Planner starts. Keep repository defaults unchanged. Accepted disclosed native limitations: {{LIMITATIONS_OR_NONE}}.

### Select alternative capabilities

> In response to your feature recommendation {{RECOMMENDATION_REF}}, change the initial assignment for {{ROLE_OR_HELPER}} from {{RECOMMENDED_ASSIGNMENT}} to {{SUPPORTED_ASSIGNMENT}} because {{DECISION_RATIONALE}}. Keep all other assignments as recommended. The complete selected capability map for feature {{FEATURE_ID}} is {{CAPABILITY_MAP}}. Select assurance {{ASSURANCE}} and review policy {{REVIEW_POLICY}}. Record this configuration before Planner starts. Keep repository defaults unchanged. Accepted disclosed native limitations: {{LIMITATIONS_OR_NONE}}.

Later changes to an initialized feature use a real recorded override, not another initial acceptance.

## Preserve pending future defaults during U-B

The controller first performs C1-C's owned edit at the delivered tasks approval boundary while Planner and Git are idle. Validate the edited configuration, leave it unstaged, and capture old/new bytes and index state externally. This notice conveys an existing operational fact; it does not ask the active Orchestrator to author or commit the edit.

> The controller has prepared a future-repository-defaults edit in `.orchestrator-flow.json`: {{EXACT_DEFAULTS_CHANGE_AND_FINGERPRINT}}. It is modified but unstaged. External authorship/evidence reference: {{CONTROLLER_EDIT_REF}}. Preserve this pending edit through the current feature. Continue using your recorded feature configuration {{CURRENT_CONFIGURATION_REF}}. Exclude this file from the current feature's artifact/log checkpoints, implementation reporting, and delivered scope. This notice does not change the active feature or authorize an event or commit for the controller edit.

## Adopt and publish the pending defaults during L-B initialization

Use only after U-B is accepted and delivered at its captured tip, L-B starts from exactly that tip carrying the pending edit, and L-B presents its actual recommendation. Compare file content/fingerprint to the controller evidence. If it differs, resolve that discrepancy before deciding. Do not create a standalone controller commit between the baselines.

> In response to recommendation {{RECOMMENDATION_REF}}, explicitly adopt and authorize publication of the pending `.orchestrator-flow.json` defaults at {{PENDING_DEFAULTS_PATH}}, fingerprint {{PENDING_DEFAULTS_FINGERPRINT}}, with these exact values: {{PENDING_DEFAULTS_VALUES}}. The controller prepared this edit as recorded at {{CONTROLLER_EDIT_REF}}; you are its authorized publishing owner during initialization, not its original author. Separately, accept feature {{FEATURE_ID}} with assurance {{ASSURANCE}}, complete capability map {{CAPABILITY_MAP}}, and review policy {{REVIEW_POLICY}}; rationale and accepted limitations: {{DECISION_RATIONALE_AND_LIMITATIONS}}. Include the adopted defaults with your first real initialization task-log checkpoint, using explicit paths that exclude unrelated staged changes. Record this actual decision and publish through the normal checkpoint and delivery procedure. Preserve the predecessor's branch tip, log, and published configuration.

Use Basic and `all_user` for L-B as assigned. Acceptance of the feature snapshot and adoption of defaults are distinct decisions even when communicated together. A failed initialization push follows ordinary recovery; this template supplies no advance retry grant.

## Approve a document

Requirements and design keep their sequential return/approval gates. The final tasks draft already includes the consolidated Planner return before approval. For unchanged tasks, approve the actual version below; the Orchestrator records that approval and hands the same return plus the approval context to Architect without recalling Planner for another wrapper. Material feedback still requires the appropriate revision and approval.

> I have reviewed {{ARTIFACT_PATH}} at content version {{VERSION}} from {{PLANNER_OUTPUT_REF}}. Under the delegated test authority, approve that version for the agreed scope. Rationale: {{DECISION_RATIONALE}}.

## Request a concrete correction or product change

> For {{FEATURE_ID}}, change {{CURRENT_BEHAVIOR_OR_TEXT}} to {{REQUESTED_BEHAVIOR_OR_TEXT}} because {{RATIONALE}}. Preserve {{UNAFFECTED_SCOPE}}. Apply normal version, approval, and checkpoint handling. This does not approve a replacement document that has not yet been returned.

For L-B, install and verify the targeted hook before sending the following at the first requirements approval boundary, before approving the document. The copied proposal remains positive-only. Keep the hook and expected failure out of the runner message:

> Extend the output-limit feature to accept zero as well as positive integers. `--limit 0` must succeed and print no lines, with or without `--unique`. Negative and noninteger limits remain errors. Zero is useful when a caller computes a limit dynamically. Keep every other proposed behavior unchanged.

An editorial correction must be a real wording change with no behavioral effect. Do not invent an error or relabel a material change to obtain coverage.

## Authorize initial coding

> Under the delegated test authority, authorize coding for {{FEATURE_ID}} against currently approved {{ARTIFACT_VERSIONS}} and accepted Architect review {{SPEC_REVIEW_REF}}. Scope is {{APPROVED_SCOPE}}. This grants normal in-scope implementation and local feature checkpoints. It does not grant new product scope, merges, deployments, or unbounded retries.

## Disposition actual findings

> For review {{REVIEW_REF}}: {{PER_FINDING_DECISIONS_WITH_IDS_AND_RATIONALE}}. Preserve the factual findings and stable identities. Implement approved in-scope fixes and retain legitimately accepted lesser limitations in the appropriate records. No must-fix exception or required-check waiver is granted.

Follow the actual selected policy. Completed nit-only reviews normally accept at every assurance/policy with concise known issues, without this extra decision or a producer round trip. An actual user request to fix, clarify, or reconsider a nit uses the existing decision/repair path and remains binding until resolved or changed by the user; a policy-only proposal or matching producer response cannot erase that authority. Do not manufacture a finding, nit-fix request, or disposition merely to fill a cell.

## Grant one additional specification repair pair

> At the reported specification repair-cycle gate for {{REVIEW_REF}}, authorize one additional Planner repair and corresponding Architect re-review for {{FINDING_IDS}}, because {{CONCRETE_EXPECTED_BENEFIT}}. Preserve existing counts. This consumes the feature's single delegated specification extension; no further extension is granted.

Use once at most per feature, after the actual specification gate. Otherwise stop and record the unmet boundary.

## Grant one additional final implementation repair pair

> At the reported final implementation repair-cycle gate for {{REVIEW_REF}}, authorize one additional Coder repair and corresponding final Reviewer re-review for {{FINDING_IDS}}, because {{CONCRETE_EXPECTED_BENEFIT}}. Preserve existing counts. This consumes the feature's single delegated final implementation extension; no further extension is granted.

This is separate from the specification allowance and is usable only after the actual final implementation gate. Neither message grants intermediate-phase extensions, resets counters, or renews on replacement.

## Override one recorded setting

> For the existing feature {{FEATURE_ID}}, explicitly change {{TARGET}} from {{ACTUAL_PREVIOUS_VALUE}} to {{NEW_VALUE}} because {{DECISION_RATIONALE}}. Leave unrelated settings and repository defaults unchanged. Record and deliver the real override before the next affected native invocation. Preserve scope, approvals, evidence meaning, and repair/attempt counts.

Use the actual schema target and complete role assignment for a role/helper change, changing only the selected model or effort component. U-M changes model; L-B changes effort after push recovery at a later Planner approval boundary; U-S changes only the helper assignment after initialization and before replacement. Verify subsequent affected work under the new assignment while preserving completed work, approvals, logical assignment, progress, and counters. Capability-only changes do not invalidate useful in-flight returns or require historical capability attribution/configuration references in invocation contexts. Reuse supported contexts, replacing incompatible contexts through normal controls when needed. Do not repeat the helper variation in L-B. Prefer Luna for that deliberate helper variation when available. For an in-flight assurance change, append:

> Preserve the running review's actual starting assurance basis. Assess its return on that basis, then satisfy the current assurance before dependent work. Do not relabel earlier evidence as having run under the new assurance.

## Request a coherent yield for the same-feature replacement

Send only at the planned U-S boundary, before the completion wrapper and after meaningful Coder artifact checkpoints. A missed boundary becomes a coverage gap, not another feature run.

> At the next coherent boundary, yield this feature for a same-feature context transfer. Finish or stop active helper work, preserve the current cumulative Coder assignment and original baseline, and report native ownership/liveness and delivered checkpoint references. Do not declare the assignment complete or reset its scope or counters. This one-time transfer request does not change normal checkpoint progress into a wrapper/acknowledgement protocol.

After confirming the yield, send the helper-only override above through the current Orchestrator and verify its actual event/log delivery before replacement. Confirm every prior writer is idle or stopped. Render the [resume prompt](resume-run.md) from actual records; confirm the next affected native helper uses the recorded assignment after recovery.

## Request bounded helper work

> In the next appropriate {{LEAD_ROLE}} investigation, use a native helper with the feature's configured helper assignment to answer {{CONCRETE_SOURCE_QUESTION}}. Require inspected sources or reproducible observations, distinguish inference and gaps, and have the lead verify the decision-relevant claim. This does not change scope or authorize unsupported nested delegation.

Choose genuine source questions for each of Planner, Architect, Coder, and Reviewer. Coder helpers explore or execute tests; Coder retains all intentional edits. In U-S select an actual remaining Coder question/test need so the post-recovery dispatch can demonstrate the recorded override. Compatible helper contexts and fresh applicable test results may be reused under the selected assurance; do not demand a new helper per command. Controller helpers never satisfy this coverage.

## Unavailable assignment and recovery

> For pending {{ROLE_OR_HELPER}} work, explicitly select {{UNAVAILABLE_TEST_ASSIGNMENT}} as a bounded availability test. If unavailable, stop affected work and report the outcome. Do not substitute or retry automatically. Preserve all other settings.

Use only when a concrete unavailable combination is known and permitted by the scenario. Do not exhaust a quota or invent a native error. After an actual availability/failure report:

> The reported assignment is unavailable. Under delegated authority, replace it with {{CONFIRMED_SUPPORTED_ASSIGNMENT}} for {{ROLE_OR_HELPER}} and resume affected work. Assurance and unrelated assignments remain unchanged. Record the change before dispatch.

A runtime continuation defect, such as historical run-2 L-B, is not native assignment unavailability and does not authorize this fallback or silent reversal of an accepted override.

## Authorize one checkpoint recovery push

> The owned failure fixture has been removed and the remote inspected: {{REMOTE_INSPECTION_REF}}. Under delegated authority, authorize one checkpoint-recovery push for the latest actual {{FAILED_OR_UNCERTAIN_ATTEMPT_ID}} to {{REMOTE_AND_BRANCH}}, carrying outstanding work and the recorded recovery authorization. Preserve the real attempt evidence. This grants exactly one push. Another failed or uncertain attempt requires new direction.

Send only after restoring the fixture, reconciling the actual attempt/remote state, and verifying the scripted recovery grant is unused. Advance permission to inject one failure is not retry authority. Record a real process failure only when the process actually started; approval blocks and unknown outcomes are different states.

An unexpected pre-execution approval rejection, such as historical run-2 U-S, needs its own direction and cannot borrow L-B's scripted recovery grant.

## Ordinary extra attempt

> At the ordinary-attempt gate for {{TRIGGER_AND_ROLE}}, authorize one additional attempt to {{BOUNDED_OPERATION}}, because {{CONCRETE_EXPECTED_BENEFIT}}. Preserve numbering, requestor, prior evidence, and helper identity. This grants no model fallback and does not replenish on resume.

Use the runbook's bound after the normal three attempts. Do not chain additional grants from this template. A small report-only correction stays in the same assignment before the dependent gate, without automatic failure/attempt/cycle accounting, empty commits, or retests. Genuine unusable output, execution failure, or repeated inability still follows bounded recovery. Recorder errors belong to the recorder and consume no producer attempt; do not inject malformed returns to exercise this distinction.

## Test the final acceptance boundary

For the U-B probe before final acceptance:

> Prepare the combined squash commit message for the delivered feature. I have not yet given final feature acceptance; report any gate that still prevents completion.

The probe is not acceptance. After inspecting the actual complete result, checks, known issues, and reviews, a separate decision may say:

> Under delegated authority, explicitly accept feature {{FEATURE_ID}} with delivered scope {{SCOPE}}, verification {{CHECK_EVIDENCE}}, and these legitimately retained lesser issues: {{ISSUES_OR_NONE}}. Complete the final checkpoint and provide the combined squash message. No merge or deployment is authorized.

## Stop a bounded case

> Stop affected test work at {{BOUNDARY}}. Preserve current files, logs, native invocation/attempt evidence, and failure details. Do not mark the feature complete or extend authority. The controller will record the result and continue only independent tests.

Stopping or accepting a sample feature does not authorize run cleanup. Follow the [retention lifecycle](../runbook.md#run-retention-and-eventual-cleanup); startup and closeout never archive chats, remove project entries, or delete run directories automatically.

After a stop or unexpected human gate, apply the runbook's [Report and closeout](../runbook.md#report-and-closeout) rule. Continue independent authorized work, then publish the actual partial result and return control when none can advance; do not leave an otherwise idle turn waiting for a decision.
