# Proposal: Orchestrator Flow v2.0.0 corrections, part 2

## Problem Statement

Orchestrator Flow v2 separates capability from assurance so that the effort spent planning, implementing, and reviewing a feature can match its complexity and consequences. A private application with a few users and straightforward manual recovery should not incur the same diligence as a critical public service. The workflow should help deliver a useful result, preserve enough information to resume, and give downstream agents sufficient context to continue effectively.

The current Codex workflow increasingly treats process fidelity as a deliverable of its own. Small reporting discrepancies and settings changes can require extra events, checkpoints, output reconstruction, and validation. Extensive common instructions and repeated evidence fields add context even to simple work. This undermines the intended savings from Basic and Standard assurance.

The governing principle for these corrections is **“perfection is the enemy of good.”** Overengineering is a defect in the workflow when its cost exceeds its practical contribution to delivery, downstream understanding, or recovery. Maximum assurance justifies more rigorous product scrutiny; it does not justify useless content or administrative detail.

This proposal revises the current, unreleased Codex v2.0.0 implementation. It replaces the earlier direction in this same proposal that required historical capability provenance and formal failure accounting for every rejected completion report. The intended behavior is described here without requiring completed proposals or the discussion transcript.

### A settings change became a provenance problem

In run 2's Basic output-limit case, the accepted Planner assignment changed from Medium to High after requirements version 2 was approved. The next document could not begin because validation bound the unfinished planning assignment to its original configuration reference. No High Planner invocation actually occurred.

The attempted correction introduced execution segments, `role-dispatch-started`, dispatch references, continuation purposes, boundary evidence, helper dispatch histories, additional checkpoint metadata, and compatibility handling. Those mechanisms try to prove which settings produced each portion of the work. That is not a user requirement. The accepted settings need to govern subsequent work; completed planning or coding does not need a historical model/reasoning audit.

### Small reporting problems receive disproportionate treatment

In Standard unique-lines, `tasks 1–7` became `tasks 1â€“7` while recording a Planner return. This is a real encoding defect: the task log should preserve the returned information. In Maximum unique-lines, a Coder completion report omitted five added paths and was then corrected. That omission did not itself demonstrate a product defect or require reimplementation.

The response should be proportionate. Reliable encoding is useful; requiring the agent to construct the same wrapper twice and prove every transport step is excessive. A small report correction can be handled matter-of-factly without turning it into a failed product attempt and a separate recovery sequence. The accepted record must still be sufficient for the next agent and a later resume.

### The normal path carries machinery intended for exceptional situations

The current schema has 15 states and 26 event types. The latest dispatch work added one event and no states; the broader complexity predates that addition. Some distinctions preserve real approvals or ownership, while others describe equivalent readiness or repeat decisions already represented elsewhere.

Every lead is also directed to read the substantial shared protocol and assurance reference, including exceptional phase and recovery behavior. Completion wrappers repeat information across file inventories, cumulative scope, checks, test results, evidence, and task progress. Broad review checklists can override the intended practical meaning of lower assurance, even where the assurance reference already describes proportionality.

Resumption is valuable but generally exceptional. Optimizing it by recording every intermediate transition imposes a recurring cost on the usual successful path. Some additional checking and replay during a resume is acceptable if it makes ordinary work simpler, faster, and cheaper. The process must retain the facts needed to reconstruct progress and authority, rather than precompute every possible recovery action.

### The live run demonstrates cost, but does not isolate its causes

Run 2 took approximately 45 hours from bootstrap start to report publication. The last live feature was accepted and delivered about 10 hours after bootstrap; roughly 35 hours followed before the report. That later window includes controller work, evidence collection, reporting, and waiting. The master acknowledged an avoidable idle period after its work had completed; the timestamps do not establish that the entire later window was idle.

The live work comprised nine feature attempts across three projects, with seven accepted, two blocked, and three dependent cases not run. First-to-last feature-log windows were:

| Feature | Basic | Standard | Maximum |
| --- | --- | --- | --- |
| Initial application | 54 minutes | 45 minutes | 86 minutes |
| Unique lines | 56 minutes | 47 minutes, then blocked | 68 minutes |
| Output limit | 23 minutes, then blocked | Not run | 72 minutes |
| Ignore case | Not run | Not run | 100 minutes |

These are elapsed workflow windows, including tools, approvals, and coordination, not isolated model execution time. Different interventions and incomplete cases prevent a controlled assurance comparison. Nevertheless, planning and specification gates occupied about 36 of Basic unique-lines' 56 minutes and 44 of Maximum unique-lines' 68 minutes; their Coder windows were approximately 10 and 13 minutes. The cost is not confined to Maximum review. The evidence supports simplifying routine workflow work, but cannot quantify the time attributable to each proposed simplification.

The separate test-kit proposal owns master scheduling, closeout, and test-controller overhead. This proposal addresses the consumer workflow.

## Proposed Solution

Simplify the ordinary path while preserving deliberate product discipline, sufficient downstream context, and recoverability. Keep the four lead roles, the three required specification documents and their sequential approvals, mandatory Red/Green development, meaningful checkpoints, assurance-dependent review, and explicit final feature acceptance. Remove process detail whose main purpose is demonstrating perfect execution of the process itself.

### 1. Apply accepted capability settings prospectively

Keep the accepted feature configuration in `task_log.json`, with the existing override record when the user changes it. Use the current accepted assignment for subsequent affected work. A settings change alone does not restart planning, invalidate approved documents, repeat completed work, consume a repair cycle, or change the Coder's cumulative reporting baseline.

| Situation | Required behavior |
| --- | --- |
| Planner proceeds to design after an approved effort change | Continue the same planning assignment under the new setting, preserving requirements and their approval. |
| Coder continues unfinished implementation | Use the new setting for subsequent work and retain completed tasks, checkpoints, decisions, and applicable validation. |
| A helper assignment changes | Use it for subsequent helper work; do not rebuild a history of earlier helper settings. |
| A role returns after a capability-only change | Evaluate the useful result normally. Do not reject or relabel it to satisfy historical capability accounting. |
| A native context cannot adopt the selected setting | Use a supported replacement when necessary, passing sufficient context and preserving the assignment. If the requested setting is unavailable, obtain user direction; do not silently substitute. |

Remove the dispatch-provenance machinery: `role-dispatch-started`, segment lineage, per-dispatch configuration matching, helper dispatch ledgers, and dispatch checkpoint trailers. Retain native role handles and assignment information where they actually support continuation, recovery, or identifying a genuine failure. Do not retain obsolete fields solely to audit older capability choices.

Assurance remains a separate acceptance policy. A capability override does not increase assurance or establish that a review occurred. A review must still satisfy the effective assurance for its actual scope. If assurance increases and required review work remains, perform that work; Maximum still requires its comprehensive pass. Retain the review level and scope needed to establish this, without tracing the model/reasoning used for each part. Reuse applicable completed evidence and raise a bounded question when a consequential ambiguity cannot be resolved cheaply.

### 2. Reduce states and events around durable meaning

Review the current state/event model as part of the implementation design. Each retained distinction should represent a meaningful result, decision, active assignment, approval, or blocker. Its normal-path cost must be justified; merely making a rare resume cheaper is insufficient when the same information can reasonably be reconstructed from existing history, native context, and Git checkpoints.

Consolidation candidates include:

| Current distinction | Proposed simplification to evaluate |
| --- | --- |
| `spec_created` versus `spec_updated` readiness states | Use one readiness state when both lead to the same Architect gate. Initial versus revised work remains understandable from the actual planning history. |
| `spec-approved-with-justifications` and `code-approved-with-justifications` | Keep a proposed disposition with the relevant result instead of adding a separate event that grants no new authority. |
| `spec-approved-by-user` and `code-approved-by-user` | Represent the actual user decision through the existing findings-disposition mechanism where it preserves the same scope and authority. |
| `role-dispatch-started` and routine helper-dispatch records | Remove; current accepted settings and sufficient assignment context govern subsequent execution. |
| Ordinary artifact checkpoints or small report corrections | Do not manufacture task-log transitions merely to mirror these operations. |

The design must identify the resulting states/events and explain any retained candidate distinction with a concrete behavioral need. Do this in the normal design/plan, without a separate audit artifact, migration framework, or target event count. Do not merely move the same machinery into a parallel set of subtype fields.

Preserve real document approvals, requests that change scope, effective configuration decisions, coding/recovery authority, meaningful role results, unresolved findings, actual blockers, and final acceptance. A user decision must be recorded once with sufficient scope, not restated through several events to satisfy overlapping rules. Keep an exceptional-phase distinction when it changes which work or review is required; do not require ordinary features to populate phase bookkeeping.

Resume may perform additional bounded reconstruction. It must never manufacture approval, infer an authorization that was not given, silently choose a model, or duplicate an active writer. If the available record cannot establish a consequential fact, ask the user instead of adding speculative normal-path machinery for every possible ambiguity.

### 3. Make proportionality explicit for Architect, Reviewer, and producers

Put the delivery principle in the lead-role contracts, including Architect and Reviewer: **perfection is the enemy of good; review to the accepted assurance and project consequences, then stop when the result is adequate.** The more specific role checklists must agree with this rule rather than implicitly requiring Maximum diligence everywhere.

Initial Architect and Reviewer coverage still includes the whole relevant specification and implementation at every level. The difference is depth, evidence, finding priority, and follow-up scope, not permission to ignore part of the feature.

| Assurance | Practical review expectation |
| --- | --- |
| Basic | Establish intended behavior, important preservation boundaries, and obvious consequential failures. Small, recoverable bugs or limitations may remain with an appropriate disposition. Do not search for remote possibilities merely to improve completeness. |
| Standard | Add meaningful regression and relevant edge-case scrutiny, proportionate to expected use and the cost of failure. A possible improvement is still not automatically a completion requirement. |
| Maximum | Retain comprehensive adversarial scrutiny, decision-critical source/research checks, rigorous follow-up, and existing loop safeguards. Every required check must still have a useful purpose. |

Findings should state the actual behavior or uncertainty, its triggering conditions, and its practical consequence concisely. Classify against the selected assurance level as well as exposure, likelihood, affected users, reversibility, recovery cost, and explicit user expectations. Distinguish demonstrated defects from optional hardening and preference. A genuine nit at that assurance level has no material effect on intended operation or the applicable acceptance standard; a minor maintenance inconvenience can be acceptable until that area is refactored. Do not promote a nit merely to require cleanup, or demote a consequential defect to avoid work. A requirement violation still needs the appropriate disposition.

**Classify first at the selected assurance, then apply the acceptance rule.** The same concern may reasonably be a nit at Basic or Standard and a should-fix at Maximum because the higher assurance demands stronger robustness, evidence, or maintainability. Its factual behavior does not change, but its completion priority can. Maximum's deeper scrutiny and stronger acceptance standard mean that findings still classified as nits there are genuinely minor; accepting a nit-only Maximum review does not apply Basic's classification threshold to it.

Remove automatic must-fix/should-fix classifications for cosmetic or style violations. For example, the current Maximum checklist makes workflow references or line-by-line narration in source comments must-fix, and redundant verbosity should-fix. Keep the guidance to write useful comments, but classify an actual violation by its consequence under the selected assurance. An unnecessary comment would normally be a nit; a materially misleading comment can warrant higher priority. A style rule alone must not create a repair loop regardless of practical impact.

Apply these remediation defaults in Architect and Reviewer judgments as well as Planner and Coder responses:

| Assurance | Nits | Should-fix issues |
| --- | --- | --- |
| Basic | Record identified nits concisely in `known-issues.md` and defer them. They do not enter the repair loop or block acceptance. Revisit when the area is refactored or the user requests cleanup. | Scrutinize whether fixing now provides sufficient practical benefit. Low-impact, unlikely, or readily recoverable issues may be deferred with a brief reason; the label alone does not require a fix. |
| Standard | Also defer by default. Selective cleanup may be worthwhile for a concrete maintenance benefit at modest total cost, but being easy to fix is insufficient and a nit alone does not justify another repair/re-review cycle. | Normally fix most or all. Deferral is an exception justified by substantial refactoring, rework, disproportionate risk, or comparable scope/cost, rather than a routine response to ordinary repair effort. |
| Maximum | Fix straightforward nits alongside already-required repairs where useful. If only nits remain, accept and record them in known issues; they never justify another repair/re-review cycle on their own. | Retain the current rigorous expectation to fix, with concrete risk/scope justification for deferral. |

**At every assurance level, including Maximum, a completed Architect or Reviewer review whose only remaining findings are genuine nits returns acceptance `true`.** Do not return conditional acceptance, request another repair pass, or require separate nit-disposition approval solely because those nits remain. This rule applies to initial reviews and follow-ups. Required review work and acceptance checks must still be complete; missing evidence or a consequential defect cannot be relabeled as a nit to invoke it.

For Basic and Standard, assess total follow-up cost: planning, editing, tests, review, approvals, and coordination as well as coding effort. Reviewers should apply the selected assurance when deciding whether a finding warrants repair, rather than produce a Maximum-style repair list and leave the producer to negotiate every item downward. They need not seek additional nits merely to populate known issues.

Make default nit deferral and acceptance of nit-only reviews part of the assurance policy, so the Orchestrator can record them with the review and maintain `known-issues.md` without sending work back to a producer solely to obtain a response. Keep each retained nit brief and do not invent a cleanup deadline or future commitment. Carry it forward without reopening it at each review unless its consequence changes or the user asks.

Honor explicit user directions and the selected disposition policy for findings that require a decision. Include required user decisions in the normal consolidated gate; do not turn nonblocking nits into an additional approval prerequisite. Preserve must-fix authority boundaries, document approvals, coding authorization, and explicit final feature acceptance. Architect/Reviewer acceptance with nits does not grant those separate approvals or authorize later cleanup.

After a lower-assurance repair, verify the repair and affected behavior. Broaden only for a material dependency or new evidence, not to begin another hunt for unrelated improvements. Do not reopen a settled disposition without a reason. Maximum retains the agreed comprehensive re-review behavior. Repair allowances are ceilings, not work to consume; acceptance ends the review loop without another polishing pass.

### 4. Preserve Red/Green while scaling test depth and document detail

**Red/Green is mandatory at every assurance level.** Meaningful behavioral work must establish the failing behavior and then implement the passing behavior. Do not combine these stages merely to reduce task count, weaken the failing witness, or replace tests with reviewer confidence.

Planner should size each Red/Green pair around a coherent behavioral step. One pair may cover several related assertions or input cases for that behavior; do not create a separate pair merely for each assertion, file, or line of wiring. Preserve incremental development, dependencies, meaningful failing witnesses, and natural checkpoint groups rather than combining the entire feature into one large pair.

Scale coverage to assurance and actual risk. Basic normally covers intended use, the happy path, and obvious relevant failures or boundaries. Standard adds useful regression and edge-case coverage. Maximum retains the more exhaustive obligations. Rare cases can remain untested at lower levels when the consequence does not justify the work; disclose a material limitation without turning every untested possibility into a mandatory finding. Required failed tests remain a real issue.

For Basic and Standard, use targeted checks to establish Red and Green, then broader regression checks at meaningful integration boundaries and final verification. Rerun affected checks when relevant implementation, tests, dependencies, or environment change. Reporting corrections, checkbox progress, and unrelated documentation changes alone do not invalidate applicable results. Final verification may reuse fresh results for the final tested work instead of repeating the same commands solely because the workflow reached a new task label. Reviewer still independently assesses the implementation, meaningful assertions, and evidence, rerunning checks where that adds useful confidence rather than automatically repeating every Coder command. Maximum retains its comprehensive fresh review checks.

Keep test execution delegated to helpers. Coder should reuse suitable helper contexts across related Red/Green runs and verification, supplying the current command, expected outcome, and relevant changes. Do not start a fresh helper for each command, task, or checkpoint. Keep the tested work stable during a run and return concise useful results. Existing handoff/checkpoint context is sufficient for ordinary result reuse; do not introduce a separate test-evidence tracking system.

Keep requirements, design, tasks, their versions, sequential approvals, useful requirement-to-task traceability, natural task groups, test maintenance, and final verification. Their detail should make the work clear without repeating the same contract throughout several documents or adding tasks solely to make a checklist look complete. Test maintenance may accurately conclude that no changes are needed.

Preserve the existing boundary between planning and implementation. Planner must still think through and write a concrete, coherent design and actionable tasks with enough detail for the selected Coder capability. Lower assurance does not justify a vague plan or leaving foreseeable design decisions for Coder to improvise. Coder follows the approved design and task structure and routes contradictions or proposed departures through the existing Planner/change process. This refactor does not broaden Coder discretion over implementation choices; savings come from reduced ceremony and proportionate verification while retaining useful up-front design.

**Unhelpful diagrams must not be added at any assurance level, including Maximum.** Include a diagram when it clarifies structure or behavior. More generally, omit irrelevant boilerplate and elaborate treatment of inapplicable concerns; Maximum means useful rigor, not compulsory decoration. Keep required document structure understandable and consistent while removing unconditional content rules that serve no practical purpose.

### 5. Supply sufficient context once, where it belongs

Organize the existing entry and role references so an agent loads the common essentials, its own responsibilities, and the applicable assurance requirements. Load detailed recovery and exceptional-phase instructions when the situation requires them. Do not require every role or helper to reread the entire orchestration protocol, all schemas, or unrelated role machinery. Keep ownership and applicable rules discoverable; do not create another profile or adapter system.

Simplify wrappers and handoffs around the information the recipient needs:

- Current scope and intended outcome, including material user decisions and their reasons.
- Relevant artifact versions, approval bases, assignment/baseline, and published work.
- A coherent account of completed work and remaining work.
- Actual validation results and evidence needed to assess important claims.
- Unresolved findings, accepted limitations, blockers, and any decision needed next.

The final Planner handoff remains consolidated. Include its complete current context in the return accompanying the final tasks draft, with approval facts stated accurately at that time. If the user approves that draft unchanged and all required document approvals are valid, Orchestrator can pass the unchanged Planner return and the subsequently recorded approval context to Architect without invoking Planner again solely to restate the same work. Architect must not begin before the actual approvals. Orchestrator must not rewrite the native return, invent Planner conclusions, or claim an approval existed before it was given. If feedback changes an artifact or a relevant decision, obtain the appropriate revised Planner handoff. Align the wrapper/readiness rules so this ordinary path requires neither a duplicate consolidated return nor a duplicate log copy of that wrapper.

A Coder completion remains cumulative for its assignment, including work before an interruption; the final phase Coder still consolidates the feature. Shortening a wrapper must not reduce it to a pointer/status object, omit important decisions, or force the recipient to rediscover the feature. The task log carries durable handoff context; approved documents and code remain the detailed sources.

Give each fact one canonical place. Remove duplicate inventories, repeated configuration snapshots, mandatory empty evidence fields, and repeated descriptions of the same test run. Optional evidence detail should become required when a real finding or decision depends on it. A straightforward test result may report what ran and passed; a failure needs the exact useful failure information. Leads still verify decision-critical helper claims, and the established Coder/test-helper ownership remains.

Validate explicit structured references used for authority and relationships. Do not interpret incidental prose such as “history entry 1” as a foreign key whose wording can invalidate an otherwise useful report. Keep factual findings and dispositions traceable without prescribing an essay for each minor issue.

### 6. Record handoffs faithfully and correct small errors routinely

Fix the demonstrated Windows encoding problem through an explicit supported Unicode/UTF-8 recording path. Pass the actual complete native return once, together with the necessary event metadata; the recording helper should embed that object rather than require the agent to author a second copy. Preserve decoded values and existing history. The agent should receive a concise result, not need to reload and compare the entire log after each write.

Keep useful schema and transition validation, preferably within one ordinary handoff-recording operation. Cheap internal checks may remain when they prevent a concrete error. Do not add multiple agent-visible proof steps, redundant tool invocations, routine wrapper files, task-log snapshots, or permanent scratch artifacts merely to demonstrate transport fidelity.

Handle a missing path, unclear summary, or similarly small report-only correction in the same assignment. Obtain the corrected information before a dependent gate requires it, then record the useful accepted result. No separate `subagent-error`, retry dispatch, product repair cycle, or test rerun is required solely for that correction. If interrupted, the current assignment, native context, and published artifacts should support recovering the outstanding handoff; the final accepted record must remain adequate for resumption and downstream use.

Genuinely unusable output, actual execution failures, or repeated inability to provide a usable result still use bounded recovery and user direction. Preserve the existing ordinary failure limits; do not create a new correction-counter framework or permit endless retries disguised as formatting fixes. A review that validly reports defects follows finding disposition, not invocation-failure recovery.

An Orchestrator recording mistake is not a producer failure. Correct it from the original return. If an incorrect record was already published, preserve append-only history and make a concise truthful correction when it matters. Do not rewrite closed test histories to make past execution appear cleaner.

### 7. Keep meaningful checkpoints; move exceptional investigation to recovery

Preserve the chosen checkpoint cadence and ownership. Planner publishes each meaningful specification/research update; Coder publishes natural groups and meaningful partial/completed work; Orchestrator publishes actual task-log updates, decisions, reviews, and acceptance. Related records from one logical update can share its checkpoint. Coder does not need an interim completion wrapper or an Orchestrator acknowledgement at each artifact checkpoint.

Reducing unnecessary events also removes their unnecessary log checkpoints. Do not compensate by adding extra status receipts or delivery acknowledgements. Keep normal publication straightforward, with the metadata needed to identify the feature and actual checkpoint work. Retain protection of unrelated changes and deliberate Git ownership.

On interruption or failure, use the current log, branch/baseline, recent checkpoint metadata and changed-file names, native role context, and available results to establish what happened. More replay or targeted checking here is an acceptable tradeoff for a simpler normal path. The Orchestrator's content boundary remains: it delegates code/specification inspection rather than reading product bodies or diffs itself. The producer may inspect its own history and artifacts to reconstruct the cumulative handoff.

Keep explicit bounded push recovery, no automatic model substitution, no duplicate active writers, and user-controlled final acceptance/merge. Use existing concise attempt evidence where it prevents an unauthorized repeated operation. Do not build a generic transaction, lock, receipt, watchdog, or recovery-proof system to handle every conceivable interruption. When an exceptional ambiguity cannot be resolved with the available evidence, present it to the user.

### 8. Align the current contracts and verify practical behavior

Update the Codex entry instructions, affected role references, assurance/protocol guidance, schemas, wrapper examples, and validation/replay/resume helpers consistently. Remove superseded dispatch and duplication rules instead of layering simplifying prose over contradictory mandatory instructions. Define the resulting fields and accepted values explicitly; do not leave schema behavior to implication.

Keep README content focused on what the repository provides and how to use it. Remove references to “part-2 corrections,” implementation plans, or revision tracking from operational explanations. Update repository/development guidance for actual interface changes. Do not create an extra release-folder README, audit report, or implementation-validation document.

Use focused behavioral tests for the affected contracts:

- Accepted Planner, Coder, and helper capability changes apply prospectively without invalidating completed work or requiring dispatch provenance.
- Assurance changes still enforce genuinely required review, while a capability-only change does not create a review gap.
- The simplified state/event model preserves sequential document approvals, authority, meaningful decisions, and correct next actions, including representative interrupted/resumed paths.
- The final tasks return can supply consolidated Planner context once: unchanged approval permits Architect handoff without another Planner invocation, while missing approvals or changed artifacts/decisions still require their normal handling.
- A complete handoff preserves Unicode through the supported Windows input/write path and retains the prior history without duplicate agent-authored payloads.
- Small report corrections can reach a valid handoff without fabricated failure/repair cycles; actual unusable output and failed operations remain bounded.
- Nit-only Architect and Reviewer results receive acceptance at every assurance level, including Maximum, without a producer repair round trip or extra nit-disposition gate. The disposition rules support selective Basic should-fix deferral and Standard's default to fix should-fix issues while honoring explicit user direction.
- Concise handoffs retain the information needed for cumulative reporting, downstream review, and recovery; irrelevant prose cannot accidentally become a structured reference.

Retain meaningful existing tests for approvals, task-content/version rules, artifact ownership, checkpoint delivery, Red/Green-related contracts, and exceptional phases. Replace or remove tests whose sole purpose is enforcing discarded machinery. Do not add wording-only tests that pretend to establish agent diligence, new installation tests, or a large test framework. Use the relevant tests during implementation and the existing development suite plus `git diff --check` for the combined runtime change. Native agent behavior still requires observation; passing schema tests alone does not prove proportional review.

### 9. Scope and non-goals

This remains Codex-only work for the unreleased v2.0.0. Preserve deferred integrations, symlink installation, project-owned coding directives, required document approvals, mandatory Red/Green, content-version rules, useful checkpoints, and explicit final acceptance. Exceptional phases remain available only for genuinely large features; this correction does not expand their use.

Do not preserve obsolete unreleased dispatch/state shapes through a compatibility subsystem solely for closed disposable test runs. Preserve those runs as historical evidence. The released-version compatibility policy remains: future minor/patch releases must keep supported older logs usable with reasonable defaults; incompatible structural changes require a major version decision.

Implementation does not authorize resuming live tests, repairing historical consumer logs, changing installations, launching or messaging feature chats, committing, or pushing. Align the separate test-kit work with the revised runtime expectations before another authorized run; it must not demand a provenance ledger or formal failure for a routine report correction. Master closeout and controller scheduling remain in the test-kit scope.

Skipping lead roles or required specification documents, broadening Coder implementation discretion, removing Red/Green, automatic model fallback, blanket time/token caps, a generic orchestration framework, and exhaustive automation of exceptional user decisions are outside scope.

## Questions

The policy decisions are established: optimize the usual successful path; retain enough durable information for resumption and downstream context; apply capability settings prospectively; preserve Red/Green at every assurance; scale test and review depth; defer Basic nits and assess Basic should-fix issues selectively; normally fix Standard should-fix issues while deferring nits; accept completed nit-only reviews at every assurance level, including Maximum; omit unhelpful diagrams even at Maximum; and handle small reporting corrections matter-of-factly.

Additional accepted simplifications are consequence-based style findings, consolidated Planner context with the final tasks return, proportionate test execution/result reuse, coherent Red/Green task sizing, and helper reuse. Preserve concrete up-front planning and the existing Coder boundaries; additional implementation discretion is not part of the change.

The exact state/event consolidation, smaller wrapper shape, and instruction organization are design choices for the implementation plan. Evaluate them against the concrete gates and recovery cases above. Raise a genuine change to user authority or product discipline for review; do not expand the proposal with speculative edge-case machinery merely to eliminate every uncertainty.

## References

- [Proposal template](../../templates/proposal-template.md).
- [Repository guidance](../../AGENTS.md) and [usage documentation](../../README.md).
- [Current Codex entry instructions](../../.codex/skills/orchestrator-flow/SKILL.md), [workflow protocol](../../.codex/skills/orchestrator-flow/references/workflow-protocol.md), and [assurance policy](../../.codex/skills/orchestrator-flow/references/assurance.md).
- Current [Planner](../../.codex/skills/orchestrator-flow/references/planner.md), [Architect](../../.codex/skills/orchestrator-flow/references/architect.md), [Coder](../../.codex/skills/orchestrator-flow/references/coder.md), and [Reviewer](../../.codex/skills/orchestrator-flow/references/reviewer.md) contracts.
- [Task-log schema](../../.codex/skills/orchestrator-flow/references/task_log_schema.json), [shared schema](../../.codex/skills/orchestrator-flow/references/common.schema.json), and [development tests](../../tests/README.md).
- [Test-kit part-2 proposal](proposal-orchestrator-flow-v2.0.0-testkit-part2.md), which owns controller closeout and live-test expectations.
- Run-2 [manifest](../../../orchestrator-flow-test-runs/testrun-2/.orchestrator-test/run.json), [report](../../../orchestrator-flow-test-runs/testrun-2/.orchestrator-test/report.md), and [decisions](../../../orchestrator-flow-test-runs/testrun-2/.orchestrator-test/decisions.md). These are external historical evidence; the problem description above retains the context needed if the disposable run is later removed.
