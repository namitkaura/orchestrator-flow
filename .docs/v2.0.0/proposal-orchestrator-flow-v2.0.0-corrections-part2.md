# Proposal: Orchestrator Flow v2.0.0 corrections, part 2

## Problem Statement

The second live test run of the Codex v2 implementation exposed a configuration-continuation defect, corruption while recording a role handoff, and incomplete failure accounting. Seven of the twelve sample features were accepted and delivered, two stopped at unresolved gates, and three dependent cases did not run. Successful product delivery does not erase the observed workflow failures.

This proposal supplements the original v2.0.0 proposal and the first corrections proposal. It defines three bounded corrections to the unreleased Codex v2.0.0 workflow. It supersedes conflicting behavior only for those corrections; the existing assurance levels, ownership, approvals, checkpoint cadence, and proportional review process remain the baseline. The separate [test-kit part-2 proposal](proposal-orchestrator-flow-v2.0.0-testkit-part2.md) addresses the master's delayed closeout and corresponding test expectations.

The aim remains reliable coordination without unnecessary work. A settings change should not force completed planning to restart, correcting a completion wrapper should not repeat product tests without a reason, and recording JSON should not create an archive of temporary files.

### An accepted Planner override cannot be used by the next planning step

In run 2's Basic output-limit case, L-B, the user delegate approved requirements version 2 and then changed the feature's Planner assignment from `gpt-6.1-sol/medium` to `gpt-6.1-sol/high`. The override was recorded and delivered. The Planner was idle at the document-approval boundary, with design and tasks still to produce in the same planning cycle.

The original Planner invocation referred to configuration event 1; the effective configuration became event 7. The runtime rejected the prospective continuation with `Returned work must retain its original invocation configuration`. A read-only replay of the actual feature log independently reproduced that rejection. No High Planner invocation was performed, so this is a runtime continuation defect rather than evidence of model unavailability or a failed High Planner response.

The current check protects a legitimate invariant: an already-dispatched review must retain the configuration under which it actually ran, even if settings change before its return. Applying that invariant to every subsequent segment of an unfinished assignment prevents legitimate future work from using an accepted override. A blanket substitution of the latest configuration would instead allow historical work to be relabeled incorrectly.

### Valid JSON can contain a corrupted copy of the actual role return

In Standard unique-lines, U-S, the Planner's returned text `tasks 1–7` was recorded in the task log as `tasks 1â€“7`. The specification artifact was unaffected, but the recorded handoff no longer matched the native return. A later no-artifact-change reconciliation preserved the historical entry rather than rewriting it.

Schema validation can accept both strings. The supported Windows shell/Python recording path therefore needs an explicit encoding contract and a comparison against the original decoded return. Successfully writing or reparsing a JSON document does not establish faithful capture if the comparison starts from an already-corrupted value. The observed mismatch establishes the recording failure; its precise transport boundary must be identified during implementation rather than assumed from its appearance alone.

### Corrected completion output can bypass failure and retry accounting

In Maximum unique-lines, U-M, the Coder's first complete completion wrapper omitted five added feature paths from its cumulative inventory against the original feature baseline. The Orchestrator correctly rejected that return before advancing to review. The same Coder supplied a corrected completion wrapper, and the feature subsequently passed review and final acceptance.

Both completion returns used attempt 1. The actual history advanced from `coding-started` to the corrected `coding-complete` without recording a `subagent-error` or advancing the ordinary retry attempt. The product result was accepted, but the workflow history omitted a real invalid-output recovery.

The protocol already requires ordinary failure accounting and bounds the available attempts. Its handoff instructions need to make that path explicit for completed returns that fail semantic validation, while distinguishing normal drafts, valid reviews with findings, and mistakes made by the Orchestrator while recording a valid return. A validator that sees only the recorded log cannot independently discover an omitted native failure.

## Proposed Solution

Correct configuration continuation, faithful handoff recording, and invalid-output recovery in the Codex contracts and the runtime mechanisms that enforce them. Use the existing workflow structure and focused regression tests. Do not introduce additional product phases, routine intermediate artifacts, or broader recovery permissions.

### 1. Distinguish subsequent work from the return of previously dispatched work

An accepted capability override must apply to the next affected work after it is recorded and delivered. Preserve the actual configuration of completed work and work already dispatched. The following distinctions govern the corrected behavior:

| Situation | Required behavior |
| --- | --- |
| A role returns work dispatched before an override | Retain its actual dispatch configuration. Apply existing evidence-applicability and assurance checks to determine what that result permits next. |
| Planner continues from an approved document to the next document after an override | Use the effective assignment for that subsequent work while retaining the same logical planning cycle and completed approvals. |
| Coder continues or resumes unfinished implementation after an affected override | Preserve the cumulative assignment and original reporting baseline; apply the accepted setting to subsequent affected work at a coherent continuation boundary. |
| Only the helper assignment changes | Apply it to the next affected helper dispatch. Preserve the lead's actual prior work and unchanged role assignment. |
| The native context cannot adopt the selected setting | Continue through a compatible native context using supported controls, preserving the assignment and evidence. If the setting cannot be used, follow the existing user-direction gate. |
| An unrelated configuration field changes | Preserve unaffected execution and evidence; do not invent a role failure, restart, or review requirement solely to account for the new configuration reference. |

The durable invocation/continuation representation must let validation and resumption establish which configuration applies to each actual dispatch and returned result. Define any necessary metadata and schema rules explicitly during design. Preserve meaningful validation of existing histories and the distinction between a logical assignment, a native context, and an ordinary retry. Merely changing a wrapper's `configuration_ref` to the latest event is not a sufficient implementation.

For the demonstrated Planner case, the corrected path must preserve requirements version 2 and its approval, continue with design under High, and retain the original requirements outputs under their original configuration. It must not fabricate `subagent-error`, create a specification-change request, or consume a repair/retry allowance just to activate the override.

Use the same interpretation in dispatch, returned-output validation, replay, and resume-action selection. Check the analogous Coder and helper paths because the shared configuration mechanism must not retain the same defect there. Preserve current review behavior: an in-flight Architect or Reviewer result cannot claim a newer configuration it did not use, and an assurance increase may still require genuine catch-up work.

Changing capability does not change approved product scope, reset cycle counters, replenish operational authority, or invalidate settled artifact approvals by itself. Continue or recover actual existing work before creating another writer. Retain native context where its supported controls permit the accepted setting; replacement must not cause a fresh whole-project investigation or repeat completed checks without an applicability reason.

### 2. Preserve decoded role-output data through recording and publication

Establish an explicit encoding path for native JSON capture, supported stdin transport, file serialization, and reading the resulting task log. Identify and fix the demonstrated Windows transport failure without depending on a user's ambient console code page. UTF-8 handling and, where useful, ASCII-escaped JSON transport are implementation options; the required outcome is preservation of the decoded values.

Validate the complete original native return before embedding it. Compare the embedded wrapper with that original decoded object, and verify that serialization and reading the written log preserve the intended candidate and its unchanged historical prefix before publishing the log checkpoint. JSON indentation and equivalent escape spelling may differ; wrapper strings, arrays, values, and required fields must retain their meaning and contents. Do not normalize or rewrite text merely to make comparison succeed.

The comparison must start from the actual original return. Comparing two copies of the same corrupted candidate does not establish fidelity. A clipped capture, pointer, or summary cannot substitute for the original required JSON response. Recover the available actual return through the existing native-output path when necessary, preserving the normal context and attempt semantics.

Keep the normal path in memory or through supported stdin interfaces. Do not add routine wrapper files, task-log snapshots, a scratch directory, or a permanent return archive to consumer repositories. Preserve the existing narrowly justified exception for temporary files required by a concrete tool or recovery constraint.

When a valid native return is corrupted only during Orchestrator recording, correct that recording operation from the original. Do not charge the producer with an invalid-output failure or rerun its product work. If corrupted content was already published, preserve append-only history and reconcile it through the existing truthful correction path; do not rewrite past entries to conceal the error.

### 3. Route invalid completed returns through ordinary failure recovery

Make the handoff decision explicit in Orchestrator guidance and the supporting validation/recovery path:

| Observed result | Required handling |
| --- | --- |
| A required completed native return is malformed, incomplete, or semantically invalid for its actual assignment | Do not advance the gate. Record the failed attempt as `subagent-error` with category `invalid_output`, then recover corrected output within the ordinary attempt bounds. |
| A valid incremental draft needs feedback or the next document | Continue the normal planning/approval process. Multiple valid incremental returns do not become role failures merely because work remains. |
| A valid Architect or Reviewer return reports findings or rejects the work | Use the existing finding-disposition and repair/review process. A valid adverse review is not an invalid-output failure. |
| A valid native return is damaged or incorrectly embedded by Orchestrator | Correct Orchestrator's recording operation; preserve the producer's actual successful return and invocation accounting. |

Record the invalid completion's causal role, actual invocation, category, and enough evidence to explain the rejection. Derive identity from the actual dispatched work rather than trusting invalid metadata in the rejected response. Checkpoint the authoritative failure update under the existing rules. The corrected return retains the logical trigger and advances the ordinary attempt number, with a truthful native context and configuration basis.

Reuse the same native role context where appropriate. A reporting correction alone does not require another Coder, product edits, a product repair cycle, or another test run. Preserve completed checkpoints and applicable checks. Re-execute work only when the actual deficiency or changed evidence warrants it.

Retain the existing limit of three ordinary attempts and the established direction requirements at exhaustion or model/usage failure. Neither context replacement nor a configuration override replenishes those limits. Do not manufacture retrospective failure entries in run 2 to make its historical record appear compliant.

The runtime can enforce consistency among recorded failures, attempts, and returns. The Orchestrator remains responsible for recording failures it actually observes; passing replay cannot prove that no external failure was omitted. Verification must preserve that distinction.

### 4. Align the affected contracts and verify behavior proportionately

Update `SKILL.md`, the Orchestrator and other affected role references, the workflow protocol, schemas/examples where their representation changes, and the runtime validation/replay/resume mechanisms as required for these three corrections. Keep the declared interfaces and unaffected workflow behavior consistent. Update existing developer guidance when an actual command or contract changes; do not create a separate implementation-validation document or a README in the release-spec folder.

Add or extend focused behavioral coverage for:

- Planner's approved-document boundary followed by a supported effort override and subsequent document work, preserving previous output provenance, approvals, and cycle counts.
- Relevant Coder continuation/resumption and helper-only override paths, including compatible context reuse or replacement without inventing a failed attempt or resetting the cumulative baseline.
- A result dispatched before a configuration change retaining its actual old basis, and rejection of a result falsely relabeled as using the new configuration. Keep the existing in-flight review provenance protection effective.
- Unicode values traveling through the supported JSON input and recording paths on Windows, including literal non-ASCII input rather than only the default ASCII-escaped output of `json.dumps`. Verify equality with the original decoded wrapper and preservation of prior history.
- A genuinely invalid completed return followed by recorded `invalid_output` recovery and the next permitted attempt, with no product repair cycle or automatic repetition of completed checks. Verify that an Orchestrator recording error is distinguished from a producer failure.

Use the existing protocol, recovery, and stdin test fixtures where suitable. Do not add tests that merely search instruction wording or claim native compliance from a valid example log. Run relevant tests during implementation and the existing development suite for the final combined runtime change, along with `git diff --check` and applicable valid/invalid schema examples.

The previously identified phase-test gaps, including unestablished reasoning mappings and the Maximum intermediate two-repair boundary, remain separate coverage dependencies. They are not newly demonstrated defects and are not silently added to this correction's scope. Existing phase behavior and tests must remain intact, and release reporting must continue to disclose any unresolved gaps.

### 5. Preserve scope and separate run recovery from implementation

This work remains Codex only and part of v2.0.0. Preserve the deferred integrations, symlink-based installation, project-owned coding directives, existing assurance/disposition policies, artifact ownership, document-version rules, complete required returns, and bounded checkpoint recovery.

The Standard unique-lines push was rejected by automatic approval review before Git executed. Its separate explicit recovery decision is not a reason to weaken push authorization or bypass approval controls. Basic output-limit's choice to hold or continue under a different assignment also remains a run-specific user decision; this proposal does not grant that decision or authorize modifying a consumer feature.

Implementation must not rewrite run-2 task logs, repair its historical evidence, resume or launch a live run, message existing feature chats, change machine-local installations, or perform source-maintenance Git operations without their separate authorization. Preserve original findings if a later authorized continuation succeeds, and identify changed source when interpreting new observations.

Schedulers, watchdogs, new workflow phases, a new configuration-profile system, automatic model fallback, export/install tooling, broad Unicode normalization, and permanent wrapper archives are outside scope. The master's closeout correction belongs to the separate test-kit proposal.

## Questions

The recorded behavior forms the planning baseline. The precise continuation representation and encoding-safe recording mechanism remain requirements/design choices within these constraints. Planning should raise any genuine conflict with provenance, compatibility, native capability controls, or existing recovery semantics rather than silently weakening those protections.

No decision to resume a blocked live case is implied. Obtain that direction separately if a later task requests resumption. Remaining phase-test coverage is a separate dependency, not an unresolved policy choice for these corrections.

## References

- [Proposal template](../../templates/proposal-template.md): the self-contained authoring contract used for this document.
- [Original v2.0.0 proposal](proposal-orchestrator-flow-v2.0.0.md) and [first workflow corrections proposal](proposal-orchestrator-flow-v2.0.0-corrections.md): existing behavior, decisions, and preservation boundaries.
- [Test-kit corrections, part 2](proposal-orchestrator-flow-v2.0.0-testkit-part2.md): the separate controller closeout change and alignment of live observations.
- [Repository guidance](../../AGENTS.md) and [project README](../../README.md): Codex-only maintenance scope, installation model, and Git boundaries.
- [Codex skill](../../.codex/skills/orchestrator-flow/SKILL.md), [Orchestrator contract](../../.codex/skills/orchestrator-flow/references/orchestrator.md), and [workflow protocol](../../.codex/skills/orchestrator-flow/references/workflow-protocol.md): configuration, handoff, ordinary-failure, and checkpoint rules.
- [Runtime protocol implementation](../../.codex/skills/orchestrator-flow/scripts/workflow_protocol.py) and [artifact validator](../../.codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py): current context binding, replay, and JSON input behavior.
- [Protocol tests](../../tests/test_protocol.py), [recovery tests](../../tests/test_recovery_and_reviews.py), [stdin/resource tests](../../tests/test_distribution.py), and [development-test guide](../../tests/README.md): existing behavioral fixtures and verification entry points.
- [Run-2 final report](../../../orchestrator-flow-test-runs/testrun-2/.orchestrator-test/report.md): accepted, blocked, and unrun cases, with separate workflow, controller, and environmental findings.
- [Planner continuation incompatibility audit](../../../orchestrator-flow-test-runs/testrun-2/.orchestrator-test/evidence/L-B-observer-effort-only-override-runtime-continuation-incompatibility-audit.json): actual accepted override and read-only reproduction of the binding error.
- [Standard planning handoff assessment](../../../orchestrator-flow-test-runs/testrun-2/.orchestrator-test/evidence/U-S-observer-planning-bounded-assessment.json): original-return corruption and subsequent reconciliation.
- [Maximum Coder invalid-output accounting audit](../../../orchestrator-flow-test-runs/testrun-2/.orchestrator-test/evidence/U-M-observer-Coder-invalid-output-recovery-contract-audit.json): rejected and corrected complete returns with the missing failure/attempt accounting.

Run-2 evidence is outside the source repository and is supplemental. It was available when this proposal was written; later authorized disposal may remove it. The problem statements and required behavior above must remain understandable without those files or the chat history.
