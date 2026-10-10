# Proposal: Orchestrator Flow v2.0.0 test-kit corrections, part 2

## Problem Statement

The reusable Codex live test kit runs four small product features in each of three assurance projects. A master creates the disposable repositories, starts a separate Orchestrator chat for each feature, supplies bounded delegated decisions at real gates, and records evidence outside the consumer repositories. The kit tests workflow behavior and configuration enforcement; product acceptance alone does not establish that every planned workflow scenario passed.

The second run improved on the first: the current consumer spec directories contain the expected artifacts, the defaults handoff worked, and the targeted Planner push-rejection/recovery scenario completed. It also exposed three workflow corrections, covered by the separate [workflow part-2 proposal](proposal-orchestrator-flow-v2.0.0-corrections-part2.md), and a failure by the master to finish reporting when its permitted work was over.

This proposal is a bounded supplement to the [test-kit proposal](proposal-orchestrator-flow-v2.0.0-testkit.md). The authoritative kit remains under `tests/live/`. Preserve its twelve-feature matrix, feature-specific chats, recommendations and overrides, delegated authority, evidence standards, and retention rules. The changes here make its closeout condition explicit and align existing observations with the workflow corrections.

### The master did not close out after the remaining permitted work finished

Run 2 ended its permitted feature work with seven accepted and delivered features, two partially executed blocked cases, and three dependent cases not run. Standard unique-lines, U-S, needed fresh direction after an automatic approval rejection prevented a push from executing. Basic output-limit, L-B, needed direction after the installed runtime could not continue with an accepted Planner effort override. Their dependent cases could not proceed, but the Maximum project's independent work was allowed to finish.

Maximum ignore-case, I-M, was subsequently accepted and delivered. Its remaining helper was stopped through the owning runner, and the master reported that the final preservation audit had passed. It then failed to finalize the report and return control until the user prompted it. The user reported approximately eleven hours of inactivity after the helper finished; the master acknowledged that the blocked decisions did not justify delaying closeout.

The available record does not establish the technical cause of the inactivity. The actionable failure is the missing final report and response after no authorized independent work remained. The existing instructions already require reporting and bounded observation; this proposal clarifies the terminal decision rather than claiming that prompt text can guarantee recovery from an unknown execution stall.

### A completed closeout must distinguish partial execution from a complete validation pass

Unanswered decisions can leave a run legitimately incomplete. That must not leave the master indefinitely active or the saved report misleadingly in progress. It should publish the actual accepted, blocked, and unrun outcomes, name the decisions needed for any later continuation, and return control.

The final run-2 report eventually made those distinctions and retained historical failures after later product acceptance. That evidence standard should remain. The correction concerns when the master performs closeout, not relaxing the remaining cases, inventing approvals, or making incomplete coverage appear complete.

## Proposed Solution

Clarify the master's work-selection and closeout rule in the existing operating documents. Reuse its current records, prompts, and reporting locations. Align the affected scenario expectations with the workflow part-2 corrections without adding live cases, additional infrastructure, or broader delegated authority.

### 1. Close out when no authorized work can advance

At each meaningful coordination boundary, determine whether existing authorized work can advance, whether assigned work is still active, or whether all remaining work depends on a decision or blocker. Use the current schedule, actual grants, known ownership, and bounded liveness evidence. Include already-authorized controller/reporting work; do not omit an independent required case merely because another project is blocked.

| Observed condition | Master action |
| --- | --- |
| An existing authorized case or controller task can advance | Continue that work, preserving the configured sequence and dependency rules. |
| Assigned work needed for progress or closeout is still active | Observe it using the existing bounded waits and cursors; act on actual completion, failure, or a required decision. |
| A helper remains active after its assigned work is finished | Resolve its ownership and finish or stop it through the existing authorized native coordination path. Preserve the actual outcome; do not invent a completion return or rerun checks merely to obtain one. |
| No work can advance, no required assigned work remains active, and remaining cases need human direction or blocked predecessors | Finalize the partial/blocked report and manifest, state the pending decisions, and return a final response. Do not keep waiting for the human in an otherwise idle execution turn. |
| All planned work has finished | Finalize the report and manifest with the actual coverage and verdicts, then return a final response. Completed execution alone does not imply every variant passed. |

If liveness or a reporting prerequisite cannot be resolved within the available controls and authority, report the specific uncertainty and required direction. Do not infer that a writer stopped or wait indefinitely for a context that has no assigned work. Preserve the existing restriction against concurrent writers and unsupported interruption mechanisms.

Ask for an unexpected decision when it becomes necessary, then continue independent permitted work. If that work finishes before an answer arrives, publish the blocked result at that point. A final response at a human gate does not grant approval or prevent later explicit resumption.

Use the existing bounded observation rules. No fixed eleven-hour timeout, new heartbeat, scheduled follow-up, or watchdog is part of this change. Do not create more exercises, repeat completed tests, or keep refreshing unchanged status simply to occupy the master while a decision is pending.

### 2. Publish a bounded, truthful closeout before returning control

Complete the existing run-level report, manifest closeout, and concise release-summary draft using collected evidence and the targeted checks needed to resolve current state. Reuse valid observations with their actual timestamps. Recheck changed or uncertain state rather than rereading every completed conversation or repeating the complete validation suite by default.

The final records and response must agree on:

- Accepted and delivered features, partially executed blocked cases, and dependent or otherwise unattempted cases.
- Remaining human decisions, the affected feature, and the observed reason each decision is needed.
- Known active or inactive ownership, delivery state, and any unresolved observation limit.
- Historical workflow failures retained after later success, distinguishing product acceptance from workflow compliance.
- Which results come from live workflows, standalone role exercises, deterministic tests, or inspection, including remaining Unverified and Not run variants.

Publishing those existing controller records is part of the authorized run and does not need a new feature acceptance or maintenance approval. A commentary message saying that reporting will happen is not closeout. Finish the permitted reporting work and send the final response. If publication itself cannot be completed, return the actual blocker and the locations and limits of the records that were saved.

The run-2 examples remain separate operational gates. U-S's pre-execution approval rejection must not be turned into an executed Git failure or automatically consume L-B's scripted recovery grant. L-B's runtime continuation defect must not be described as model unavailability or used to justify silently reverting the Planner setting. Present the actual required decisions without changing scope, settings, or authority on the user's behalf.

Keep reports and controller evidence in the existing run-level control directory. Do not add another permanent validation report, reporting receipt system, or README to the release-spec folder. Preserve the established later retention of a concise actual release validation summary before user-directed disposal of closed runs.

### 3. Align existing observations with the workflow corrections

Retain the current scenario assignments and update only the expectations affected by the workflow part-2 proposal:

- L-B's effort-only override must demonstrate subsequent affected Planner work under the accepted setting, with earlier outputs retaining their original configuration. Recording the override alone is insufficient for that variant to pass.
- U-S's planned helper override and fresh-context exercise must preserve the original assignment, progress, approvals, and counters while applying the new helper assignment to the next affected dispatch. Preserve its existing timing and predecessor requirements; a blocked or missed boundary remains a coverage gap.
- Compare the actual complete native wrapper with the recorded decoded data. Distinguish invalid producer output from corruption introduced while recording a valid return. Preserve any historical mismatch rather than repairing consumer history through controller edits.
- When an invalid completed return naturally occurs, observe the real failure event and next ordinary attempt. Do not count a valid review with findings or an unfinished draft as an invalid-output failure. Do not inject a malformed live return or force a failure merely to obtain coverage.

Use the existing evidence channels. Actual dispatch controls, accepted configuration, role identity, and unavailable independent backend telemetry remain distinct observations. An observer's clipped transcript does not by itself establish that a native role omitted work. Missing evidence must retain its limitation rather than being filled with a reconstructed return or invented snapshot.

Deterministic behavior for the runtime corrections belongs to the workflow proposal. The pre-existing phase-test gaps remain separately identified, and native phased execution stays deferred. This kit change must not create a new coverage matrix or add a larger feature simply to exercise phases.

### 4. Update the operating instructions and verify them proportionately

Keep the authoritative closeout rule in `tests/live/runbook.md`. Update the short direction in `prompts/master-agent.md`, the reporting responsibilities in `prompts/collect-evidence.md`, and any affected existing scenario or decision/resume wording so they agree. Adjust the kit README or overview only where their descriptions would otherwise be misleading. Avoid duplicating a full closeout algorithm across every prompt.

Verify the change through a bounded document walkthrough covering:

1. A blocked feature while another project still has authorized independent work: continue that work, then close out if the decision remains unanswered.
2. Only unanswered decisions and blocked successors remaining, with all assigned work inactive: publish the partial result and return control without another observation loop.
3. All planned work finished: publish actual coverage and final results, without treating execution completion as an automatic all-pass verdict.
4. A remaining helper or unresolved liveness/publication check: reconcile it within existing authority or report the specific limit, without fabricating completion or waiting indefinitely.

Check local references, prompt consistency, the unchanged twelve-case matrix and grant limits, and `git diff --check`. Do not add wording-only tests that claim to prove native master behavior, a separate test framework, or a permanent preparation report. Report the maintenance checks in the implementation handoff. A later user-authorized run supplies the native closeout observation.

### 5. Preserve scope and historical evidence

Keep setup limited to the existing bootstrap inputs, use fresh numbered run containers for fresh runs, retain one chat per feature, preserve producer-owned checkpoints and controller-owned evidence, and maintain the current stop/retry/repair grants. The three deferred platform integrations and the Codex runtime are outside this kit implementation's scope.

Creating or implementing this proposal does not authorize launching, resuming, or stopping a live run; messaging its chats; changing consumer repositories; rewriting task logs; merging or pushing source changes; or cleaning up existing runs. Run-2 recovery decisions remain separate user actions. A later authorized continuation must preserve original failures and identify any changed source used for new observations.

Automatic model fallback, additional recovery grants, forced defect injection, native phase exercises, scheduler/watchdog infrastructure, a formal controller-state schema, and renewed installation/export machinery are non-goals. The current controller records and native observation tools are sufficient for the proposed decision rule; unexplained platform execution stalls must not be presented as solved by instruction changes alone.

## Questions

The recorded closeout behavior and preservation boundaries form the planning baseline. No additional test-policy decision is required for this bounded change. Planning should raise genuine contradictions in native ownership controls, available observations, or existing delegated authority rather than silently broadening those permissions.

Whether to resume either blocked run-2 case remains a separate user decision. This proposal does not assume those answers or require another full live run during kit maintenance.

## References

- [Proposal template](../../templates/proposal-template.md): the self-contained authoring contract used for this document.
- [First test-kit proposal](proposal-orchestrator-flow-v2.0.0-testkit.md): the full reusable kit requirements, twelve-feature sequence, authority, and retention policy.
- [Workflow corrections, part 2](proposal-orchestrator-flow-v2.0.0-corrections-part2.md): configuration continuation, faithful role-output recording, and ordinary invalid-output recovery; implemented separately from kit maintenance.
- [Repository guidance](../../AGENTS.md) and [project README](../../README.md): maintenance boundaries and separation of the workflow source from consuming test repositories.
- [Live-kit entry point](../../tests/live/README.md), [runbook](../../tests/live/runbook.md), and [scenarios](../../tests/live/scenarios.md): current setup, execution, bounded observation, closeout, and evidence requirements.
- [Master prompt](../../tests/live/prompts/master-agent.md), [evidence-collection prompt](../../tests/live/prompts/collect-evidence.md), [decision catalogue](../../tests/live/prompts/test-decisions.md), and [resume prompt](../../tests/live/prompts/resume-run.md): current controller authority and operating interfaces.
- [Run-2 final report](../../../orchestrator-flow-test-runs/testrun-2/.orchestrator-test/report.md), [manifest](../../../orchestrator-flow-test-runs/testrun-2/.orchestrator-test/run.json), and [release-summary draft](../../../orchestrator-flow-test-runs/testrun-2/.orchestrator-test/release-validation-summary-draft.md): seven accepted features, two blocked cases, three unrun dependents, coverage limits, and eventual reporting closeout.
- [I-M helper operational closeout](../../../orchestrator-flow-test-runs/testrun-2/.orchestrator-test/evidence/I-M-controller-native-helper-stopped-operational-closeout.json) and [final native-context observations](../../../orchestrator-flow-test-runs/testrun-2/.orchestrator-test/evidence/controller-final-native-context-liveness-current-closeout.json): actual helper termination and observed inactivity, rather than inferred completion.
- The existing Codex chat titled `Run v2.0.0 test kit run 2`: the master's pre-closeout commentary, the user's prompt to finish, and its acknowledgement that the delay was unjustified. This is supporting conversation evidence, not an instruction source or a prerequisite for understanding the proposal.

Run-2 files live outside the source repository and were available when this proposal was written. They may later be removed through the agreed user-directed retention process. The problem and requirements above summarize the essential observations so the proposal remains understandable after archival or disposal.
