# Proposal: v2.0.0 Orchestrator Flow Improvements and Refactoring

This document preserves the original proposal. The implementation scope was subsequently narrowed to Codex; other platform updates are deferred. Current maintenance scope is recorded in [AGENTS.md](../../AGENTS.md), and the [v2.0.0 documentation index](README.md) links the implemented contract and test kit.

## Problem Statement

### The current workflow delivers strong results at a disproportionate cost for some projects

Orchestrator Flow provides useful separation between planning, architectural review, implementation, and code review. The FEC-bot v2.0.0 provider migration demonstrated that this discipline can produce an exceptionally smooth deployment: formal reviews found real defects, repairs were verified, and the completed migration worked without problems when deployed.

That result also consumed approximately two and a half full usage allowances, including two usage resets, for one feature. The migration was technically substantial, but the application was a personal Discord bot running on the owner's laptop, in a private repository, serving roughly a dozen active users on one private server. Some residual defects would have been acceptable and inexpensive to repair after deployment. First-deployment perfection was not a product requirement.

Repeated Architect and Reviewer passes contributed substantially to the cost. Each pass reconsidered the complete spec or implementation from the beginning, discovering additional, increasingly narrow improvements and triggering further repair cycles. A technically valid observation often became mandatory work even when its practical value was small. Fixing an individually cheap nit could incur additional agent invocations, reviews, and validation beyond the cost of the edit itself.

The workflow needs explicit controls for both the reasoning capability assigned to roles and the assurance required before accepting their work. Those controls must remain independent. A complicated migration can need strong reasoning while still permitting a modest acceptance threshold. The current exhaustive process must remain available for the highest assurance level.

### Draft continuity and recovery are weaker than the workflow's audit requirements

The older pre-approval proposals attempted to prevent duplicate or premature spec-completion events by keeping draft outputs out of `task_log.json`. A subsequent proposal preserved cumulative draft wrappers in conversation state. Those approaches avoid some false transitions, but leave substantive decisions and intermediate work dependent on conversation continuity.

The intended working model now includes a feature branch, a commit and push for every substantive update, and a history rich enough to inspect or restore intermediate work. The branch will eventually be squash-merged manually, so its working history should prioritize recovery and traceability. Cloud agents and other reviewers also need access to current progress without depending on the original local checkout.

The spec documents currently lack explicit content versions. Revision History has acted as a partial substitute, while some runs introduced approval statuses and Git metadata directly into documents. Maintaining those duplicated workflow fields caused unnecessary edits because the authoritative state was already in the task log. Lengthy Revision History sections also consumed context when later agents needed only the current specification.

### Protocol correctness and platform consistency need explicit contracts

The earlier protocol-drift incident exposed incorrect actor/requestor relationships, premature implementation completion, duplicate revision starts, stale history references, and role ownership violations. JSON validity alone did not establish that the workflow history was correct.

The new behavior must be expressed consistently in the shared directives, role instructions, schemas, wrapper examples, validation tools, and recovery rules across Codex, Claude Code, GitHub Copilot, and Cursor. It must also distinguish current effective configuration from configuration history, preserve explicit user authority, and prevent older logs from being silently interpreted under an incompatible workflow.

## Proposed Solution

### 1. Preserve the existing role workflow and task structure

Retain the five-role workflow: Orchestrator coordinates Planner, Architect, Coder, and Reviewer through specification, specification review, implementation, and code review. Requirements, design, and tasks remain mandatory artifacts. Preserve Red, Green, Refactor, Documentation, Test-Maintenance, and Verification responsibilities at every assurance level.

Assurance changes the depth of evidence, hardening, review, and remediation within this structure. It does not introduce a route that bypasses Planner or Architect for small changes. Alternative execution paths are outside this refactor.

Role ownership remains explicit:

| Role | Ownership |
| --- | --- |
| Orchestrator | User interaction and gates, configuration, role handoffs, task-log updates, known-issues maintenance, and coordinated Git checkpoints. |
| Planner | Requirements, design, tasks, and optional research; incremental and consolidated spec-change wrappers. |
| Architect | Read-only assessment of the specification against current source and evidence. |
| Coder | Approved implementation, tests, documentation, and permitted task-progress updates; structured change outputs. |
| Reviewer | Read-only assessment of the implementation and verification evidence. |

Orchestrator must not author spec content or product implementation. Maintaining known issues is an explicit addition to its artifact ownership, not permission to rewrite the specification or independently waive findings. Planner owns substantive task-plan changes; existing Coder task-completion accounting must be reconciled with the new version and checkpoint rules during design.

The Orchestrator owns communication with the user. Roles return questions, outputs, and findings through the platform's supported handoff mechanism; the workflow must not depend on hidden subagent conversations to obtain or remember approvals.

### 2. Introduce workflow version 2.0.0 and a documented compatibility policy

Establish one canonical semantic version for the distributed workflow, starting at `2.0.0`, with a repository version file such as `VERSION`. All four integrations implement the same workflow contract version. Record `workflow_version` as a top-level field in each new feature or bug's task log.

Version 2.0.0 applies to new work. It does not include compatibility with pre-2.0 logs, migration tooling, or automatic repair of historical logs. Completed historical features remain untouched. If a user attempts to resume an unsupported log, the Orchestrator must stop, explain the incompatibility, and ask how to proceed. Any exceptional repair is separately directed work with the user.

Future releases must follow this compatibility contract:

| Update | Required behavior |
| --- | --- |
| Patch, such as `2.0.0` to `2.0.1` | Compatible corrections; older logs within the supported major version remain usable. |
| Minor, such as `2.0.0` to `2.1.0` | Compatible additions; earlier 2.x logs continue to work without a breaking migration. |
| Major, such as `2.1.1` to `3.0.0` | Incompatible schema or behavioral changes are permitted. Migration support or an explicit breaking boundary must be considered for that release. |

Compatibility covers execution and resumption, not merely parsing JSON. Existing events, approvals, configurations, and histories must retain their meaning. Adding a field is compatible only when older logs can omit it or receive a documented, reasonable default or initial value. That value must preserve prior behavior and must not invent authorization, a user override, or an assurance decision.

Defaults for absent fields must be defined consistently in schemas, validation, and runtime instructions. New logs write the applicable fields explicitly. Older logs may use the defined value on read; any persisted initialization must not masquerade as historical user action. A schema `default` annotation alone is not sufficient unless the consuming implementation actually applies the specified behavior.

The README must explain this policy. An exact-version-only check must not unnecessarily reject a 2.0.0 log under a compatible 2.1.0 workflow. This does not promise that an older workflow can understand logs written by a newer release.

### 3. Establish repository defaults and independent feature configuration

Store general repository defaults in a committed, hidden root file named `.orchestrator-flow.json`. Do not put those defaults in `AGENTS.md`, whose instructions apply beyond Orchestrator Flow.

During first-time setup, the user and Orchestrator establish capability defaults and a default assurance level. For each new feature, the Orchestrator reads those defaults, assesses the proposal, and presents feature-specific recommendations for acceptance or override before the first Planner invocation.

Record the complete resolved feature configuration in `task_log.json`, including inherited values. Storing only differences from repository defaults is insufficient: later repository changes must not implicitly change an existing feature.

| Configuration source | Responsibility |
| --- | --- |
| Workflow instructions | Built-in workflow policy, including the default review-disposition policy. |
| `.orchestrator-flow.json` | Repository defaults for new features, including platform-appropriate capability assignments and assurance. |
| Feature `task_log.json` | Effective settings for this feature, explicit user overrides, and configuration history. |

On resume, use the feature's recorded settings. Repository-default changes affect future features only. Applying new defaults to an existing feature requires explicit user direction and a recorded configuration change. Accepting a feature-specific recommendation does not silently modify repository defaults.

### 4. Configure capability per role without automatic substitution

Use saved per-role defaults with per-feature overrides, rather than requiring named capability bundles or selecting every assignment from scratch. Configure model and reasoning effort for Planner, Architect, Coder, Reviewer, and helpers. Resolve assignments from the feature's recorded configuration when invoking roles.

Capability recommendations concern reasoning difficulty: ambiguity, integration complexity, stateful behavior, unfamiliar interfaces, and the need to reconcile unexpected evidence. A strong lead remains responsible for synthesis and integration; helpers perform bounded investigation or execution and provide evidence rather than unverified authority.

Model and effort names must be platform-appropriate. Codex and Claude Code are the priorities for specific defaults and setup support. Copilot and Cursor may retain generic defaults where appropriate, but must implement equivalent behavior and accurately report any unsupported configuration mechanism. Fixed model names scattered through role instructions must not defeat explicit feature settings.

A lead using a high reasoning effort and a reviewer using a maximum effort can share the same assurance level. Model-family choices belong in platform-appropriate configuration rather than the shared workflow contract.

If an assigned model is unavailable or reaches a usage limit, pause the affected work and ask the user whether to choose an alternative or wait. This applies to lead roles and helpers. No automatic model fallback is authorized. Preserve completed work and evidence, and record any user-selected substitution without changing assurance implicitly.

### 5. Define three workflow-wide assurance levels

Introduce Basic, Standard, and Maximum assurance. Use one level for the entire feature workflow; per-role assurance overrides are outside this release. Each role follows its own responsibilities under that shared standard.

Every level includes an initial Architect review of the complete relevant spec and an initial Reviewer review of the complete relevant implementation. Lower assurance reduces scrutiny and obligations, not initial coverage to only a convenient subset of the work.

| Dimension | Basic | Standard | Maximum |
| --- | --- | --- | --- |
| Intended use | Personal or low-consequence work where limited defects and follow-up repairs are acceptable. | Ordinary shared work needing stronger robustness and regression confidence. | Work requiring the existing exhaustive assurance process. |
| Initial review | Complete relevant coverage, emphasizing fitness for actual use and consequential failures. | Complete relevant coverage with stronger edge-case and evidence expectations. | Preserve the current exhaustive, adversarial review depth. |
| Hardening and evidence | Sufficient for intended use; avoid speculative obligations without practical benefit. | Meaningful robustness and regression evidence proportionate to consequences. | Preserve existing demanding evidence and hardening expectations. |
| Follow-up review | Fixes and directly affected behavior, expanding when evidence warrants it. | Focused, broad, or full according to actual change impact. | Preserve fresh comprehensive re-review and current rigorous remediation behavior. |
| Acceptance | Permitted limitations and deferred findings can remain explicitly recorded. | Stronger acceptance threshold, with justified dispositions under the selected policy. | Preserve current acceptance and justified-deferral obligations. |

Assess assurance from consequences, reversibility, recovery cost, exposure, affected users, and the user's preferences. Technical difficulty alone does not justify Maximum assurance. Conversely, a small change with difficult-to-recover consequences may warrant stronger assurance.

Maximum preserves the rigor of the current process while receiving the cross-cutting improvements in this proposal, such as draft recording, configuration, checkpoints, and clearer user gates. Planning must audit the current contracts to retain their actual maximum-rigor obligations rather than replacing them with a vague summary.

### 6. Make finding severity and remediation depend on assurance

Architect and Reviewer findings must explain the issue, the conditions under which it matters, and its consequences for the actual project. Distinguish a demonstrated correctness problem from a hardening opportunity or preference. Severity should reflect the agreed acceptance standard without disguising the underlying facts.

At lower assurance, a technically possible improvement does not automatically become a completion requirement. A concern that warrants `should_fix` in a high-consequence deployment may be a `nit` or accepted limitation in a personal project.

Preserve `must_fix`, `should_fix`, and `nit` categories, with explicit response rules:

- `must_fix` blocks acceptance unless the user explicitly dispositions it under the applicable policy; record the rationale for an override rather than erasing the finding.
- At Basic, evaluate `should_fix` items by practical benefit, likelihood, consequence, and total workflow cost. At Standard, use a stronger presumption toward fixing. Maximum retains current remediation and justified-deferral requirements.
- For lower-assurance nits, ease of editing is not by itself sufficient reason to act. Planner or Coder can conclude that the current result is adequate and record why the improvement is not worthwhile.
- At Maximum, preserve the current treatment of straightforward nits and justified deferrals.
- Previously accepted dispositions must not be reopened merely because the next reviewer notices the same concern. New evidence, changed behavior, or a relevant revisit condition may justify reconsideration.

For behavioral findings, reproduce a meaningful failing witness where practical before repairing the defect. Verification depth follows assurance. Do not require another full audit solely because a narrower witness or documentation improvement was made at a lower level.

`spec_approved` and `code_approved` mean accepted under the selected assurance and disposition policy. They need not imply an empty known-issues record. Unresolved acceptance conditions and accepted limitations must remain distinguishable.

### 7. Select follow-up scope explicitly and bound lower-assurance review loops

For Standard assurance, apply the agreed impact-based policy to both Architect and Reviewer:

| Change | Normal follow-up scope |
| --- | --- |
| Tests, documentation, clerical reconciliation, or narrow task wording | Focused verification of the change and relevant consistency. |
| Bounded design or production correctness repair | Verify the repair, meaningful evidence, and affected neighboring contracts. |
| Material architectural change, invalidated earlier conclusions, or evidence of systemic problems | Full re-review of the relevant work. |

Record the repair class, changed surfaces, selected scope, and reason in the relevant workflow output. Use earlier review conclusions and dispositions as context. Broaden a focused review when evidence justifies it; starting another invocation is not itself a reason to restart the complete audit.

Basic normally uses focused follow-up with consequence-based expansion. Maximum retains the current comprehensive re-review behavior. Required checks still apply at each level; focused review is not permission to disregard failed checks or approved requirements.

Add separate limits for each specification and implementation review loop:

| Assurance | User decision before another repair cycle |
| --- | --- |
| Basic | After one completed repair-and-re-review cycle, if further repairs are needed. |
| Standard | After two completed repair-and-re-review cycles, if further repairs are needed. |
| Maximum | Retain current rigorous loop behavior and existing stalled-loop safeguards. |

The initial review does not count as a repair cycle. A cycle consists of a Planner/Coder repair pass followed by Architect/Reviewer re-review. Successful acceptance does not trigger an unnecessary pause. At the limit, present remaining findings and the expected value of more work; ask whether to continue, accept permitted deferrals, or change scope or assurance. Do not automatically waive defects or reset the allowance without the user's direction. Existing stuck-loop detection remains applicable.

### 8. Make review disposition an explicit, overridable feature policy

The built-in policy is: always obtain user disposition of Architect findings before Planner revision; permit Reviewer-driven repairs inside approved scope and assurance unless a user decision is needed.

Reviewer findings require user input when they entail a product/spec decision, an exception to the assurance policy, or new authorization. Routine implementation repairs can proceed under existing approval. The user can accept proposed responses in a batch; a gate need not require a separate exchange for every nit.

This default belongs in the instruction/skill files, not repository configuration. Record its effective value in a top-level `review_disposition_policy` field in each task log. The schema must enumerate the supported policies and their semantics, including the stricter or less-interruptive alternatives available as explicit feature overrides. The exact enum spellings belong in the design, not free-form agent prose.

User disposition may accept a finding, clarify intent, require a different resolution, reject an invalid finding, request reconsideration, or explicitly accept a limitation. Planner must revise according to the recorded disposition rather than treating the Architect as the product owner.

Requirements, design, and tasks retain separate approvals. Material changes to requirements, behavior, scope, architecture, contracts, or executable task instructions require renewed approval before dependent work proceeds. Editorial corrections and faithful recording of already-approved decisions may proceed without another gate, with the basis recorded in the task log. Approval of requirements does not automatically approve dependent design or tasks, and approval of design does not automatically approve dependent task instructions.

Follow the dependency order for material revisions: requirements, then design, then tasks. Planner first revises requirements and obtains user approval through Orchestrator before revising dependent design or tasks. Any resulting material design revision receives its own user approval before Planner revises dependent tasks; materially revised tasks then receive separate user approval before the applicable Architect follow-up. A revision that begins at design or tasks follows the same rule from that point. Do not revise downstream artifacts around an upstream material decision that is still awaiting approval, and do not require edits or renewed approval for unaffected artifacts.

Architect acceptance does not itself grant initial coding authorization. Obtain the user's explicit approval to begin implementation, honoring approval already given for that scope, and carry it forward for ordinary in-scope repairs.

### 9. Record configuration overrides as real workflow events

Introduce a general `user-override` event for explicit changes to workflow configuration, including capability, assurance, and review-disposition policy. Update the effective fields and append the event in the same task-log update, then commit and push the checkpoint.

Each override must identify the affected setting or settings, their previous and new values, and any supplied rationale or scope. The schema must explicitly define allowed field names, accepted values, and which settings are overridable. Use the same value definitions for effective configuration and override payloads. Validate the claimed previous values against the actual configuration.

Overrides persist for the feature until explicitly changed again. They do not implicitly update repository defaults, affect another feature, or rewrite historical results. Product changes remain `user-change-requested` events; individual review decisions belong in disposition records.

An override preserves the workflow phase. Resume from the preceding workflow action, looking past consecutive configuration-override entries, and apply the new policy to the pending work. Do not repeat completed work merely because a setting changed. Any additional work required by an explicit increase in assurance must be identified rather than silently declaring earlier evidence sufficient.

### 10. Require a feature branch and a commit-and-push checkpoint for every update

Establish the active feature branch, integration target, and baseline explicitly at initialization. Supply that context to roles; do not let reviewers guess that the default branch represents the work under review. Feature branches do not imply worktrees: creating or running in a worktree still requires explicit user instruction.

Commit and push every completed substantive update, including:

- workflow initialization and recorded user requests;
- initial and revised drafts, with their Planner outputs;
- approvals and finding dispositions;
- configuration overrides;
- implementation updates and repair outputs;
- research corrections, known-issue changes, and verification/review outcomes;
- the final user-accepted completion record.

An update is a completed logical unit, not every filesystem write. Related artifact edits and their corresponding log output belong in the same checkpoint. Do not batch away intermediate draft updates until document approval, or wait until the end of a long implementation to preserve completed work. Planner may identify meaningful coding milestones, but those annotations do not replace update-level checkpoints or become fake numbered tasks.

Checkpointing records the current state; it does not mean approval or readiness to merge. Incomplete or deliberately Red work must remain accurately identified when checkpointed. Prior guidance preferring only stable milestone commits must not suppress the agreed checkpoint after an actual update.

Pushing every checkpoint makes progress available for user-requested cloud or independent reviews. Do not trigger those reviews or send messages automatically merely because the branch is remote.

If a commit succeeds but its push fails, preserve the commit, report the failure, pause further workflow work, and ask the user how to proceed. Retry is a likely response, not an automatic substitution for the user's decision. Never force-push or overwrite remote work to satisfy the checkpoint rule.

Checkpointing accompanies real workflow events; it is not an additional progression event such as `checkpoint-pushed`. The design must provide recoverable correspondence between events and commits without creating an endless extra commit to record the preceding commit's hash. Spec documents must not carry checkpoint metadata.

The new checkpoint policy replaces the distributed workflow's blanket prohibition on feature-branch commits and pushes. It does not authorize merging into the integration branch, discarding unrelated work, or rewriting shared history.

### 11. Record interim drafts while preserving the existing major workflow states

Retain the existing phase structure where it adequately describes the workflow. Multiple requests, draft updates, and artifact approvals can occur while status remains `spec_in_progress`. A real recorded event need not change phase.

Use one initial `spec-creation-started` event for the creation cycle, and preserve substantive feedback and Planner outputs within that cycle. Do not label each clarification as a new formal revision or record initial spec completion before the required approvals.

The following is the proposed event/resume baseline for design:

| State | Event | Resume action |
| --- | --- | --- |
| `spec_in_progress` | `spec-creation-started` | Begin or recover initial Planner work. |
| `spec_in_progress` | `spec-revision-started` | Begin or recover the current revision with its request and findings. |
| `spec_in_progress` | `user-change-requested` | Route recorded feedback to Planner within the current cycle. |
| `spec_in_progress` | `spec-updated` | Continue the artifact-approval path; present the returned version for user review when approval is required. |
| `spec_in_progress` | `spec-artifact-approved` | Continue the next required artifact, or obtain the consolidated wrapper when required approvals are complete. |
| `spec_created` | `spec-created` | Begin initial Architect review using the complete consolidated handoff. |
| `spec_updated` | `spec-updated` | Begin the applicable Architect follow-up using the consolidated handoff and prior findings. |
| `spec_changes_requested` | `user-change-requested` | Start a revision of the previously completed spec. |
| `spec_changes_requested` or `spec_conditionally_approved` | `spec-reviewed` | Obtain the required user disposition of Architect findings. |
| Relevant spec/code findings state | `review-findings-dispositioned` | Follow the recorded decisions: revise, reconsider, or process acceptance under policy. |
| Current phase | `user-override` | Continue the underlying workflow action with the changed configuration. |

Reuse `spec-updated` for interim outputs instead of introducing separate draft-produced and draft-updated events. Its state and payload distinguish an interim artifact update from the completed revision handoff. Distinguish a `spec-artifact-approved` event for a particular document version from the existing `spec-approved-by-user` event used for approval of deferred review items.

The two proposed approval/disposition additions and `user-override` must be reconciled with the complete existing event inventory during design. Define every accepted state/event combination and its resume action, including role failure, conditional acceptance, configuration initialization, partial blockers, and explicit completion. Do not add speculative events merely to justify additional state machinery.

Use the state, event payload, and recorded history to determine resumption; do not add a duplicate pending-action field. For an in-flight role, recover running work or completed output before launching a duplicate invocation. Preserve actor/requestor semantics: actor identifies who performed the event, while requestor identifies whose request or handoff caused it. Record UTC timestamps and keep history append-only.

### 12. Give required spec documents content versions without duplicated workflow metadata

`requirements.md`, `design.md`, and `tasks.md` carry an explicit integer content version beginning at 1 with the first draft and increasing with each update. Each document advances independently; requirements version 3, design version 7, and tasks version 5 is a valid combination.

Increment once per completed logical content update and append that document's Revision History entry. Two completed updates in one conversation are two versions; the old same-session consolidation rule no longer applies. Do not increment an unchanged document merely because another artifact changed.

Documents contain no approval status, review status, branch names, Git hashes, or other duplicated workflow state. The task log records which versions were approved or reviewed. A pure approval or phase transition updates the log and checkpoint without changing the document version or Revision History.

When earlier content is restored, represent it as a new content version and explain the restoration. Preserve intervening history rather than reusing an old version number.

### 13. Keep useful Revision History while excluding it from routine context

Revision History begins with the initial draft and is always the final top-level section, at the same heading level as the document's other main sections. Use a consistent heading so tools can retrieve current content without loading the history.

Each entry identifies the version, date, meaningful changes, and concise reasoning. Preserve enough explanation to make the revision useful to a human without imposing an arbitrary short word limit. Avoid reproducing the conversation, duplicating large contracts, or recording workflow metadata that belongs in the log.

Architect, Coder, Reviewer, and other consumers normally retrieve the current document content only up to the final Revision History section. They consult that section when history is relevant. Reading the whole file and then being told to ignore its last section does not meet the context-saving goal.

Reasoning necessary to understand the current contract remains beside that contract in the document body. Later agents must not need historical reconstruction to discover why a current design choice applies.

### 14. Preserve complete incremental outputs and a consolidated final Planner handoff

For each substantive Planner update, return a `spec_change_wrapper` sufficient to record:

- the initiating user request or review finding;
- affected documents and previous/current versions where versioned;
- material changes and effects on related artifacts;
- resulting decisions, rationale, and constraints;
- dispositions, unresolved questions, and relevant research updates.

The Orchestrator records the actual output promptly in the task log. It must not reconstruct missing rationale, replace it with a vague summary, or rely on a hidden Planner conversation as the only record. Draft-stage wrappers must support partially produced specs without pretending that not-yet-created artifacts exist.

On each Planner reinvocation, Orchestrator supplies the relevant prior wrapper and governing decisions from the durable record together with the new feedback or findings. Preserve continuity across interruptions without requiring every interim wrapper to repeat the complete cumulative history; each incremental output records its own changes, while the final handoff consolidates the current state.

Before the Architect handoff, Planner produces a complete consolidated wrapper representing the current specification, relevant artifact versions, governing decisions and rationale, and current dispositions. It includes everything needed to understand the final planning state, not just the latest delta or a concatenation of interim wrappers.

For example, the consolidated handoff should say that the user specified manual retry because it is adequate for the intended deployment. It need not recount that an earlier draft proposed automatic retries and was corrected. That chronology remains in the task log and Git.

Orchestrator supplies authoritative approval and configuration context from the log and checks handoff consistency. Planner owns the consolidated account of spec content. Apply the same principle of sufficient change scope and cumulative context to code-review handoffs, without forcing every role to ingest the complete history on each invocation.

### 15. Enforce artifact boundaries and define optional research

A completed proposal or bug report is the starting input. As planning evolves, the approved requirements, design, and tasks become the authoritative specification. Apply subsequent approved changes through those artifacts and the task log; do not treat stale wording in the original input as overriding them.

| Artifact | Required | Content responsibility |
| --- | --- | --- |
| `requirements.md` | Yes | User stories, acceptance criteria, required behavior, and scope constraints. |
| `design.md` | Yes | Architecture, interfaces, invariants, state/error semantics, and technical decisions with relevant rationale. |
| `tasks.md` | Yes | Concrete executable work, targets, test ownership, requirement mapping, and verification instructions. |
| `research.md` | When substantive research is needed | Current empirical findings and evidence informing the specification. |
| `task_log.json` | Yes | Workflow state, configuration, requests, outputs, approvals, dispositions, and recovery history. |
| Known-issues record | As applicable | Currently unresolved findings and accepted limitations, maintained by Orchestrator. |

`tasks.md` must not contain appendices. Move technical contracts to design, evidence to research, and process history to the log. Tasks must still be specific enough to execute: removing appendices must not produce vague instructions or require Coder to rediscover foreseeable architecture.

When present, `research.md` has fixed core sections with flexible investigation subsections:

1. Purpose and Scope.
2. Investigations and Findings.
3. Open Questions.
4. Sources and References.

Investigations identify the question, relevant sources or methods, findings, limitations, and conclusions as applicable. Distinguish observations from inferences. Summarize and reference substantial raw evidence rather than using the document as a dump of command output.

Research represents the best current findings. Correct or replace superseded conclusions; preserve relevant negative findings when they still explain a constraint. Authoritative implementation decisions belong in design.

Research has no document version and no Revision History. Its changes and reasons are recorded through Planner wrappers, the task log, and Git. Source dates or experiment details may accompany evidence where freshness matters, without adding document-level workflow metadata. Do not create an empty research file or a fourth mandatory artifact-approval gate.

### 16. Preserve evidence across interruptions according to assurance

Helpers report inspected sources, concrete observations, inferences, coverage gaps, and uncertainty. Lead roles own synthesis and verify decision-critical claims at the applicable assurance level; helper confidence is not a substitute for evidence.

Preserve completed research and reports so a usage interruption, model change, or resumed session does not automatically repeat all discovery. Record enough source context to determine whether the evidence remains applicable.

- Basic and Standard check relevant sources and assumptions for changes, reuse valid completed evidence, and repeat affected or incomplete work.
- Maximum actively revalidates decision-critical research observations and conclusions against current sources, even if those sources appear unchanged, and corrects or extends the research when necessary.

Revalidation that confirms existing research can be recorded without a pointless document rewrite. Substantive corrections are owned by Planner and checkpointed. Read-only reviewers return findings rather than editing the research themselves. Evidence reuse does not waive Maximum's required fresh review passes.

### 17. Maintain a current known-issues artifact

Add a feature-level known-issues document, with `known-issues.md` as the proposed filename. Orchestrator maintains it from review findings, producer responses, applicable assurance rules, and user dispositions. It has one owner across the spec and implementation phases.

Include only applicable unresolved findings: deferred issues and accepted limitations, including nits or should-fix items permitted to remain under the chosen policy. Entries identify the finding, practical impact, severity, disposition, rationale, relevant references, and any useful revisit condition or workaround. Distinguish possible future work from a limitation for which no fix is planned.

When an issue is fixed, remove it from the current record; the task log and Git preserve its history. Invalid or rejected findings remain in review history rather than appearing as outstanding defects. Update dispositions when they occur and reconcile the record before final acceptance.

Document maintenance does not give Orchestrator independent authority to waive findings. An accepted disposition remains settled unless new evidence or changed circumstances justify reopening it. Maximum retains its existing obligations; the artifact does not create a new bypass around them.

The delivered feature may be accepted at its selected assurance level with documented limitations. The user can discover those limitations without reconstructing every review wrapper. The artifact can be referenced when preparing the release or future work.

### 18. Keep approved work moving around scoped blockers

Ordinary implementation approval carries forward within its scope. Do not repeatedly request permission for offline repairs, tests, or a reopened Red/Green slice that implements the approved design.

If an external operation requires fresh authorization or is blocked, pause that operation and work that depends on it. Continue other approved work that can proceed correctly without its result. Do not bundle an authorized offline repair with a separately restricted live request into one stop condition.

For relevant external operations, the plan should identify the exact operation, applicable request limits, retry and redirect policies, credential handling, response-body and deadline bounds, failure handling, and authorization constraints. Specify whether approved offline validation can continue after a failure without another gate. Include these details where relevant to the operation rather than imposing a checklist on every task. One authorized attempt does not implicitly authorize another when the permission was explicitly bounded.

Blocker records should identify the affected task or operation, reason, attempts, evidence, dependent work, work that can continue, and what user input or authority is needed. Reconcile partial blockers with the existing state/event contract rather than treating every blocker as proof the entire feature must stop.

A failed checkpoint push remains the explicit global pause rule established above. Missing model availability pauses the affected work and requires the user's substitution decision. Product changes and genuine contradictions route through Planner and the applicable approval gates.

### 19. Preserve test ownership and deliberate final maintenance

Retain the existing execution boundaries at every assurance level:

- Red establishes failing behavioral evidence in tests and necessary test support, with failure for the intended reason; it does not change production implementation.
- Green changes production implementation and its owning source/API documentation to satisfy approved behavior; if test changes are needed, return to the appropriate Red work.
- Refactor changes production code only, preserves the now-green behavior, and does not change tests.
- Documentation work has concrete targets and changes documentation only unless explicitly defined otherwise; source documentation belongs with the implementation that owns the changed contract rather than requiring a late rediscovery pass.
- Final Test-Maintenance precedes Verification. Planner specifies which tests to keep, merge, remove, rewrite, or strengthen; Coder executes the disposition rather than independently inventing a test strategy.
- Verification runs checks and reports evidence without making repairs inside the verification task. Failures return to the owning task category.

Do not invent cleanup when no cleanup is needed. Assurance scales breadth and evidence requirements, while the execution structure remains intact. Mini-milestones support long runs but cannot suppress the per-update checkpoint rule.

### 20. Separate review acceptance, user completion, and manual squash merge

Reviewer acceptance produces `code_approved` under the configured policy. It does not automatically complete the feature. Present the delivered behavior, verification results, and remaining known issues for explicit user acceptance or finalization.

Only that explicit user action authorizes recording `implementation_complete`. Finish the final checkpoint and push, then generate one consolidated squash-commit message for the user to manually merge the feature branch into `main` or the explicitly selected integration branch.

The Orchestrator and every other agent are prohibited from performing that squash merge. Supplying a message does not authorize a merge, deployment, or rewrite of the integration branch.

Use the current commit-message structure and level of detail: a conventional commit subject, useful grouped bullets, implementation/spec/documentation coverage, meaningful test changes and verified results, and breaking changes where applicable. Reflect the total resulting change relative to the integration baseline, not the sequence of intermediate commits, failed attempts, and repairs. Derive test counts and results from evidence rather than inventing them.

The old convention that a request for a commit message itself drives completion must be replaced by explicit feature acceptance. Frequent checkpoint commits are unrelated to the final completion decision.

### 21. Update all integrations and validate the protocol, not just JSON syntax

Implement shared semantics across Codex, Claude Code, GitHub Copilot, and Cursor in this release. Prioritize Codex and Claude Code for platform-specific configuration and defaults. Keep the other integrations functional and behaviorally equivalent with generic defaults where suitable; do not defer their contract updates and allow drift.

Preserve `Directives/codingAgentDirectives.md` as the shared directive source of truth and its portable references. Inspect every affected role, command, rule, schema, wrapper example, and validation utility. Update README setup and workflow descriptions, including Git behavior, version compatibility, configuration precedence, assurance, recovery, and finalization. Existing setup mechanisms must make required version/configuration definitions available to the installed integrations.

Own and distribute the workflow's input templates in this repository: `templates/proposal-template.md` and `templates/bugreport-template.md`. Give each an explicit integer template version starting at 2, advancing independently as its authoring contract changes. Template versions identify authoring revisions; workflow semantic versioning governs compatibility, including any breaking change to required input contracts. Make the templates' canonical locations discoverable in README and platform guidance. Each template must provide visible Markdown authoring guidance, section-specific expectations, and enough style and detail guidance to stand alone without a previous proposal or bug report. Preserve the established completed-document outlines, remove the template-version line and authoring guidance from completed artifacts, and scale detail to the work. Proposals explain intended changes and rationale; bug reports establish observed failure, reproduction, expected correction, and relevant preservation boundaries without requiring a speculative diagnosis. Do not embed downstream-project documentation assumptions or machine-specific paths in the reusable templates.

Add a dedicated README section covering the templates as inputs to Orchestrator Flow. It must:

- Link to both canonical files under `templates/` and explain when to use a feature/improvement proposal versus a bug report.
- Describe how to copy the appropriate template into a completed input document in the consuming repository, following that repository's artifact-location conventions without overwriting the reusable template.
- Explain that the templates contain self-contained, visible authoring guidance, including section expectations and optional heading hierarchy; users do not need earlier proposals or bug reports as style references.
- Explain how to remove the template-version line, authoring instructions, examples, and placeholders from the completed document while preserving the applicable document outline.
- Show how to supply the completed document's path to the Orchestrator to begin planning, using the relevant platform invocation guidance.
- Explain independent integer template versions, starting at 2, and distinguish them from workflow semantic versions, product release versions, and spec-document content versions.
- Cover access to the canonical templates under the supported setup approaches so users of copied or linked platform artifacts can find the inputs too.

Define exact field names, types, accepted values, defaults, and payload compatibility in schemas. Keep validators and examples consistent. Include protocol validation for:

- state/event transitions and deterministic resumption;
- actor/requestor relationships, including failed-role events;
- event-to-wrapper compatibility and partial versus consolidated Planner outputs;
- document-version and approval references;
- finding identities, dispositions, and current known issues;
- valid override targets, previous values, and resulting configuration;
- contiguous unique event IDs and valid historical references;
- workflow-version support and documented compatibility defaults;
- explicit user authorization for final completion.

Validation must accept legitimate repeated interim updates and configuration overrides while rejecting premature completion and invalid transitions. Do not copy the old duplicate-update heuristics without adapting them to the new drafting contract.

Before appending an event, Orchestrator checks its meaning, actor/requestor, permitted transition, resulting state, required payload, historical references, and whether it improperly duplicates an in-flight action. After every task-log update, run schema and semantic validation before the associated checkpoint or dependent handoff. Resolve invalid records before treating the update as a valid workflow checkpoint.

Historical-reference validation covers structured references and references inside nested wrapper text. Check that referenced IDs exist and denote the intended event or wrapper type: a review reference must identify a review event, and a wrapper reference must identify an event containing the appropriate wrapper. Do not stop at JSON validity or numeric ID existence; account for singular and plural references in supported text forms.

Verification should exercise representative complete flows and interruptions: iterative drafting, renewed versus unnecessary approvals, both review loops at each assurance level, override-and-resume behavior, scoped blockers, failed pushes, explicit completion, and unsupported historical logs. Cover the same-major compatibility rules as the contract evolves. Tests must demonstrate behavior and failure handling rather than merely mirror instruction text.

### 22. Explicit non-goals for v2.0.0

This refactor does not include:

- bypassing roles or introducing an alternate lightweight feature/bug execution path;
- per-role assurance levels or a more granular assurance hierarchy;
- automatic model fallback for leads or helpers;
- automatic migration or compatibility with pre-2.0 task logs;
- silent changes to an existing feature when repository defaults change;
- agent-performed squash merges into `main` or another integration branch;
- automatic external reviews, deployments, or unbounded live-operation retries;
- mandatory research for every feature or a separate research approval gate;
- status, branch, or Git metadata in the spec documents;
- speculative workflow states or checkpoint events without a real progression need;
- modification of completed downstream features or machine-local installations as part of this repository refactor.

## Questions

The policy decisions above were resolved with the owner before this proposal was created and form the planning baseline. This proposal consolidates and supersedes the four archived background documents listed below as the input for this refactor. Their applicable requirements are carried forward here; their examples, incident chronology, and tentative alternatives remain historical context rather than additional requirements. Superseded approaches include draft-history suppression, conversation-only wrapper continuity, same-session revision consolidation, blanket Git prohibitions, per-role assurance, and universal exhaustive re-review. All four integrations receive the shared contract updates in this release.

Requirements and design must make the remaining implementation details concrete without reopening those policies unnecessarily. In particular, define the complete configuration and event schemas; exhaustive state/event resume mappings; the detailed assurance rubric; invocation/output recovery; checkpoint correspondence without self-referential commit churn; and the platform-specific packaging of shared version and validation definitions. The event names and mappings identified as proposed must be checked against the full contract before being finalized.

If planning or implementation exposes a genuine contradiction or requires a new user-visible policy, ask the user at the appropriate phase. Do not silently substitute a different behavior or invent approval. Ask unresolved decisions individually with concrete options and tradeoffs.

## References

Should read for project context before creating the spec:

- Main README: `README.md`.
- Repository guidance: `AGENTS.md`.
- Shared directives: `Directives/codingAgentDirectives.md`.
- Canonical proposal template: `templates/proposal-template.md`.
- Canonical bug-report template: `templates/bugreport-template.md`.

Optional historical background and incident evidence. These archived documents are not required planning inputs or additional sources of requirements; consult them only when their original examples or incident details are useful:

- Consolidated V2 improvement notes: `.docs/archived/orchestrator-flow-consolidated-improvement-notes-2026-09-19-v2.md`.
- Protocol-drift incident: `.docs/archived/codex-flow-issues.md`.
- Earlier pre-approval logging proposal: `.docs/archived/codex-tighten-orchestrator-step-3-pre-approval-logging.md`.
- Earlier draft-wrapper continuity proposal: `.docs/archived/codex-preserve-pre-approval-planner-wrapper-continuity.md`.

Current implementation contracts to inspect and reconcile:

- Codex skill and role contracts: `.codex/skills/orchestrator-flow/SKILL.md` and `.codex/skills/orchestrator-flow/references/`.
- Codex task-log schema: `.codex/skills/orchestrator-flow/references/task_log_schema.json`.
- Codex wrapper schemas and examples: `.codex/skills/orchestrator-flow/references/wrappers/`.
- Artifact validator: `.codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py`.
- Existing detailed commit-message contract: `.codex/skills/orchestrator-flow/references/orchestrator.md`, Commit Message Mode.
- GitHub Copilot artifacts: `.github/agents/`.
- Claude Code artifacts: `.claude/agents/` and `.claude/commands/`.
- Cursor artifacts: `.cursor/agents/`, `.cursor/commands/`, and `.cursor/rules/`.

The repository-owned templates define the authoring conventions for future proposals and bug reports. Earlier FEC-bot examples informed those conventions, but are not required style references or dependencies for using the templates.
