# Master decision and stimulus messages

These are message templates for the master, not instructions to approve unknown work. Read the actual gate/output first, render exact references, and append the actual sent message/delivery reference to the controller evidence. Do not send the whole catalogue to a runner.

Prefix each delivered message with:

> Master test decision under the human's delegated test authority for {{RUN_ID}}. This is a decision by the authorized test controller, with the bounds established in the initial test request.

## Accept or select repository defaults

Send only after the Orchestrator has returned its actual setup recommendation. Identify the recommendation in controller evidence; do not invent a task-log event before the feature exists.

> In response to your repository-default recommendation {{RECOMMENDATION_REF}}, select assurance {{ASSURANCE}} and these supported native role/helper assignments: {{CAPABILITY_MAP}}. {{ACCEPTED_RECOMMENDATIONS_AND_CHANGED_CHOICES_WITH_RATIONALE}}. Record these as repository defaults. This decision does not yet accept the feature configuration. Review policy remains feature-level.

## Accept or select feature configuration

Send only after the Orchestrator has assessed the proposal/defaults and returned its feature recommendation. Use the unchanged-capability response for C1-A in U-B and the alternative-selection response for C1-B in U-S. Do not send the map in initial runner prompts or force the maps to match across runs. Assurance and review policy are separate choices for the scenario.

### Keep recommended capabilities

> In response to your feature recommendation {{RECOMMENDATION_REF}}, accept your role/helper capability map unchanged for feature {{FEATURE_ID}}: {{RECOMMENDED_CAPABILITY_MAP}}. Select assurance {{ASSURANCE}} and review policy {{REVIEW_POLICY}} for {{SCENARIO_RATIONALE}}. Record this accepted feature snapshot before Planner starts. Keep repository defaults unchanged. Disclosed native limitations accepted for this feature: {{LIMITATIONS_OR_NONE}}.

### Select alternative capabilities

> In response to your feature recommendation {{RECOMMENDATION_REF}}, select these different supported assignments: {{CHANGED_ROLE_ASSIGNMENTS_WITH_PREVIOUS_RECOMMENDED_VALUES_AND_RATIONALE}}. Keep the remaining role/helper assignments as recommended. The complete selected capability map for feature {{FEATURE_ID}} is {{CAPABILITY_MAP}}. Select assurance {{ASSURANCE}} and review policy {{REVIEW_POLICY}}. Record this accepted feature snapshot before Planner starts. Keep repository defaults unchanged. Disclosed native limitations accepted for this feature: {{LIMITATIONS_OR_NONE}}.

Preserve the actual recommendation and final selection separately in controller evidence. Later changes to an initialized feature use the override message below. A user-supplied setting constrains the choice; a test operator's planned selection is not prior acceptance.

## Approve a document

> I have reviewed {{ARTIFACT_PATH}} at content version {{VERSION}} from {{PLANNER_OUTPUT_REF}}. Under the delegated test authority, approve that version for the agreed scope. {{RELEVANT_DECISION_RATIONALE}}.

## Request a concrete correction or product change

> For {{FEATURE_ID}}, change {{CURRENT_BEHAVIOR_OR_TEXT}} to {{REQUESTED_BEHAVIOR_OR_TEXT}} because {{RATIONALE}}. Preserve {{UNAFFECTED_SCOPE}}. Apply the normal version, approval, and checkpoint handling; this message does not approve a replacement document that has not yet been returned.

For L-B, deliver the following after requirements v1 is returned and before approving it:

> Extend the output-limit feature to accept zero as well as positive integers. `--limit 0` must succeed and print no lines, with or without `--unique`. Negative and noninteger limits remain errors. Zero is useful when a caller computes a limit dynamically. Keep every other proposed behavior unchanged.

For an editorial correction, select a real typo or wording clarification that does not change behavior. Do not invent an error or call a material change editorial merely to complete the case.

## Authorize initial coding

> Under the delegated test authority, authorize coding for {{FEATURE_ID}} against the currently approved {{ARTIFACT_VERSIONS}} and accepted Architect review {{SPEC_REVIEW_REF}}. Scope is {{APPROVED_SCOPE}}. This grants the normal in-scope implementation work and local feature checkpoints; it does not grant scope changes, merges, deployments, or unbounded retries.

## Disposition actual findings

> For review {{REVIEW_REF}}: {{PER_FINDING_DECISIONS_WITH_IDS_AND_RATIONALE}}. These are the test controller's delegated decisions. Preserve the factual findings and stable identities. Implement only approved in-scope fixes and retain accepted lesser limitations in the appropriate records. No must-fix exception or required-check waiver is granted.

## Grant one additional repair cycle

> At the reported {{SPEC_OR_CODE}} repair-cycle gate for {{REVIEW_REF}}, authorize one additional producer repair and corresponding re-review for {{FINDING_IDS}}. This is one additional cycle, not a counter reset. No further extension is authorized by this message.

Use at most once per phase per feature, only where another bounded repair has a concrete expected benefit. Otherwise stop the scenario and record the gate; do not force a completed feature.

## Override one setting

> For the existing feature {{FEATURE_ID}}, explicitly change {{TARGET}} from {{ACTUAL_PREVIOUS_VALUE}} to {{NEW_VALUE}} because {{SCENARIO_REASON}}. Leave all other settings and repository defaults unchanged. Record the override and preserve phase, prior evidence, approval meaning, and cycle counts.

Use the actual schema target and the complete role assignment for role changes. For an in-flight assurance change, add:

> Preserve the running review's actual invocation basis. Apply the new assurance to acceptance of subsequent work; do not relabel evidence obtained at the earlier assurance.

For the repository-defaults case instead say:

> Change only this repository's future-feature defaults to {{NEW_DEFAULTS}}. The current feature must keep its accepted snapshot. This is not an override of the current feature.

## Request bounded helper work

> In the next appropriate {{LEAD_ROLE}} investigation, use one native helper with the feature's configured helper assignment to answer {{CONCRETE_SOURCE_QUESTION}}. Require inspected sources or reproducible observations, distinguish inference and gaps, and have the lead verify the decision-relevant claim. This does not change product scope or authorize unsupported nested delegation.

## Unavailable assignment and recovery

> For the pending {{ROLE_OR_HELPER}} assignment, explicitly select {{UNAVAILABLE_TEST_ASSIGNMENT}} as a bounded availability test. If it is unavailable, stop the affected invocation and report that outcome; do not substitute or retry automatically. Preserve all other settings.

Send only when an actual unavailable combination can be identified; do not invent client errors. After the actual failure/availability report:

> The reported assignment is unavailable. Under the delegated test authority, replace that assignment with {{CONFIRMED_SUPPORTED_ASSIGNMENT}} for {{ROLE_OR_HELPER}} and resume the affected work. Assurance and unrelated assignments remain unchanged. Record the change before dispatch.

## Authorize one checkpoint recovery push

> The test remote is restored and has been inspected. Under the delegated test authority, authorize one checkpoint-recovery push for the latest {{FAILED_OR_UNCERTAIN_ATTEMPT_ID}} to {{REMOTE_AND_BRANCH}}, carrying the outstanding work and the recorded recovery authorization. Preserve the real attempt evidence. This grants exactly one push; another failed or uncertain attempt needs a new decision.

Do not send this before restoring the fixture or before the actual attempt identity is known. A scenario's advance permission to inject one failure is not itself permission to retry.

## Ordinary extra attempt

> For the ordinary failure at {{TRIGGER_AND_ROLE}}, authorize one additional attempt to {{BOUNDED_OPERATION}}. Preserve actual attempt numbering, requestor, prior evidence, and helper identity where relevant. This does not grant model fallback or replenish on resume.

## Test the final acceptance boundary

> Prepare the combined squash commit message for the delivered feature. I have not yet given final feature acceptance; report any gate that still prevents completion.

Do not treat any response to this probe as final acceptance. After the actual result, checks, known issues, and review have been inspected:

> Under the delegated test authority, explicitly accept feature {{FEATURE_ID}} with delivered scope {{SCOPE}}, verification {{CHECK_EVIDENCE}}, and these legitimately retained lesser issues: {{ISSUES_OR_NONE}}. Complete the final checkpoint and provide the combined squash message. No merge or deployment is authorized.

## Stop a bounded case

> Stop the affected test work at {{BOUNDARY}}. Preserve its current files, log, invocation/attempt evidence, and failure details. Do not mark the feature complete or extend its authority. The controller will record the result and continue only independent tests.
