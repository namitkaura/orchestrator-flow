# Orchestrator Flow — Consolidated Improvement Notes and Future Workflow Design

**Compiled:** 2026-09-19  
**Version:** V2  
**Purpose:** Preserve all Orchestrator Flow improvements, workflow lessons, model-allocation and assurance-profile ideas, approval-gate changes, artifact conventions, and recovery/checkpoint ideas discussed during the FEC-bot v2.0.0 MAL Provider Independence work.

**V2 integration note:** This version preserves the original consolidated notes except where the later FEC-bot Reviewer/repair cycle materially changes or extends them. V2 adds a second, independent workflow-control axis for **assurance/rigor** alongside model/reasoning **capability/resources**, and uses that distinction to make Architect/Reviewer re-review breadth risk-aware rather than automatically exhaustive.

> **Important scope note**
>
> These notes are for a **future Orchestrator Flow improvement effort**. They are not changes to implement inside FEC-bot v2.0.0. The FEC-bot work exposed the problems and provided the examples; the workflow changes belong in the separate Orchestrator Flow project.

---

# 1. Why these changes are being considered

The FEC-bot v2.0.0 MAL Provider Independence feature became a useful stress test for the current Orchestrator Flow.

The existing workflow did many things well:

- strong separation between Planner, Architect, Coder, and Reviewer;
- formal spec artifacts;
- explicit Red/Green sequencing;
- task logs and review wrappers;
- support for delegated exploration;
- the ability to use stronger models on planning/review and cheaper models on implementation/exploration.

But the run exposed several weaknesses:

1. **Model assignment was too static.**
   - The original assumption was that a very strong Planner/Architect could make the task plan explicit enough that a cheaper Coder could execute it mechanically.
   - That worked for early bounded tasks, but failed once implementation reality diverged from the plan.
   - The lead Coder still needed to reconcile unexpected evidence against the approved design.

2. **Approval gates were sometimes in the wrong place.**
   - The Orchestrator sometimes bundled an already-authorized offline repair with a separately restricted live action.
   - This caused unnecessary stop/start behavior.

3. **The user did not always get a disposition gate before expensive revision loops.**
   - Architect findings could flow directly into Planner revision even when the user might want to reject, reinterpret, or resolve a finding differently.

4. **Spec artifact ownership needed sharper rules.**
   - `tasks.md` briefly became overloaded with appendices that were really design/research material.
   - Revision-history placement and ownership were not consistently encoded.

5. **Long coding runs need durable checkpoints.**
   - A 47-task implementation benefits from stable mini-milestones that are committed and pushed.
   - This is especially important when usage limits, model changes, or tool interruptions occur.

6. **Subagent output needs a stronger evidence discipline.**
   - Cheap exploration is valuable, but a strong parent should not accept incomplete or inferred helper reports as authoritative on decision-critical questions.

7. **The current workflow does not treat feature branches and runtime resource selection as first-class orchestration state.**

8. **Model capability and workflow assurance were implicitly coupled.**
   - Choosing Astra Max for a difficult Architect/Reviewer decision was effectively coupled to maximum review breadth and repeated fresh re-review.
   - The final FEC-bot review loop demonstrated that a strong model can remain appropriate even when the project does not justify repeating the most exhaustive possible verification after every bounded repair.
   - The first formal Reviewer pass found real production defects; later passes mostly found test-witness and documentation gaps while production behavior was already correct.
   - The workflow therefore needs a separate control for **how much verification is required**, not just **which model performs it**.

The improvements below are meant to preserve the strengths of the workflow while reducing wasted model usage, unnecessary approval interruptions, ambiguous ownership, restart risk, and disproportionate assurance cost.

---

# 2. Core design principle

The future Orchestrator Flow should optimize for:

> **Use the strongest reasoning only where it materially improves decisions, use cheaper agents for bounded evidence gathering/execution, and place user gates before expensive or product-significant loops.**

Related principles:

- The user remains the product owner.
- Review roles identify risks; they do not unilaterally redefine product intent.
- Strong lead roles own synthesis and cross-cutting judgment.
- Cheap helpers gather evidence or execute narrowly specified work.
- Workflow state should be durable and resumable.
- Spec artifacts should have clear, non-overlapping ownership.
- Expensive model calls should occur with maximum information and minimum churn.
- **Capability and assurance are separate decisions:** task difficulty determines how much reasoning capability is useful; consequence/risk determines how much verification rigor is justified.
- A strong model does not imply that every iteration must use the maximum possible review breadth.
- No silent downgrade of lead-role model quality or assurance level.

---

# 3. Capability/resource and assurance selection should become an explicit startup gate

## 3.1 Current problem

Historically, role/model assignments were largely preconfigured.

During the FEC-bot run, the original strategy was roughly:

- Planner: GPT-6 Astra High
- Architect: GPT-6 Astra Max
- Coder: GPT-5.6 Luna Max
- Reviewer: GPT-6 Astra Max
- helper subagents: GPT-5.6 Luna Max

The theory was:

> Astra does the difficult reasoning up front, then Luna executes a highly specified plan.

This turned out to be unreliable for a large, interconnected implementation.

The taxonomy-parser incident showed that the Coder still had to:

- interpret real upstream HTML that differed from assumptions;
- notice that implementation contradicted an approved design invariant;
- distinguish parser defects from spec contradictions;
- reopen the correct Red/Green slice;
- make a local architectural judgment;
- preserve fail-closed behavior while narrowing the defect.

That is not purely mechanical execution.

## 3.2 Proposed startup capability-and-assurance gate

At the beginning of an Orchestrator Flow run, **before the first Planner invocation**, the Orchestrator should pause and establish two related but independent configurations:

1. **Capability/resource configuration** — which model and reasoning effort each role receives.
2. **Assurance/rigor configuration** — how exhaustively each role and review loop must validate the work.

It should show:

- the configured default model and reasoning effort for each lead role;
- the helper/subagent default;
- the configured default assurance profile and any role-specific assurance overrides;
- an optional recommendation for both axes based on the proposal's difficulty and risk;
- the choice to accept defaults or override either axis or individual roles.

The interaction should happen once near the beginning, not repeatedly throughout the workflow. Later material changes can trigger a recommendation to raise or lower assurance, but never a silent change.

Example:

```text
Proposed workflow configuration for this feature:

Capability/resource profile: maximum
  Planner: Astra High
  Architect: Astra Max
  Coder: Astra High
  Reviewer: Astra Max
  Supporting agents: Luna Max

Assurance profile: thorough
  Planner evidence/artifact validation: thorough
  Architect initial review: full adversarial
  Architect re-review: risk-adjusted
  Reviewer initial review: full adversarial
  Reviewer re-review: repair-scoped unless material production/spec changes
  Test/doc-only repair: targeted witness verification + normal regression suite

Assessment: This is a technically difficult cross-cutting provider migration
involving external APIs, credentials, runtime wiring, persistent identity
contracts, taxonomy generation, compatibility boundaries, and extensive tests.
The project is private with a small blast radius, so maximum reasoning capability
can be justified without automatically requiring high-assurance fresh re-review
after every bounded repair.

Accept this configuration, customize capability, customize assurance, or customize both?
```

If the user accepts, the workflow proceeds immediately.

If the user changes a role, model/effort, assurance level, or re-review policy, that assignment becomes part of workflow state.

## 3.3 Likely default capability/resource profile

The likely new general-purpose default is:

- **Planner:** Astra High
- **Architect:** Astra Max
- **Coder:** Astra High
- **Reviewer:** Astra Max
- **All helper/subagents:** Luna Max

This is intentionally conservative for nontrivial feature work.

## 3.4 Simpler capability configurations may use Sol or Luna

The Orchestrator should have guidance for lower-cost configurations.

Possible examples:

### Substantial / high-capability feature
- Planner: Astra High
- Architect: Astra Max
- Coder: Astra High
- Reviewer: Astra Max
- helpers: Luna Max

### Moderate / well-contained change
Possible recommendation:
- Planner: Sol High or Extra High
- Architect: Astra High or Sol Extra High
- Coder: Sol High
- Reviewer: Astra High or Sol Extra High
- helpers: Luna Max

### Simple / low-risk change
Possible recommendation:
- Planner: Sol
- Architect: Sol
- Coder: Sol or Luna Max
- Reviewer: Sol
- helpers: Luna Max

### Trivial / mechanical change
Potentially:
- Luna Max for most or all roles;
- perhaps a reduced review path if the workflow rules eventually permit it.

The important rule is **not** to equate cheaper with bad. Luna is appropriate when the task is truly bounded/mechanical.

## 3.5 Proposal-aware recommendation rubric

The Orchestrator should inspect the proposal and consider factors such as:

- number of affected subsystems;
- architectural novelty;
- state-machine complexity;
- concurrency or locking;
- persistence/data durability;
- external APIs;
- credentials/security;
- live network dependencies;
- migration/backward compatibility;
- size of test changes;
- number of behavioral contracts;
- ambiguity remaining in the proposal;
- likelihood that implementation reality will diverge from the plan.

The recommendation should be concise and explain why. These factors primarily inform **capability/resource needs**; some also inform assurance, but assurance has its own risk/blast-radius rubric below.

## 3.6 Named capability/resource profiles

It may be useful to expose named profiles, for example:

- `economy`
- `standard`
- `maximum`
- `custom`

A repository could have a configured default profile while the Orchestrator still recommends moving up or down for a specific proposal.

`high-assurance` should be reserved for the **assurance/rigor axis**, not used as a synonym for an expensive model bundle.

Capability profiles should be shortcuts, not rigid all-role bundles.

## 3.7 Capability recommendations should be role-specific

A feature may not need one uniform capability tier.

For example:

- simple planning but difficult implementation;
- difficult security review but mechanical code;
- complex requirements but straightforward code.

The Orchestrator should be able to recommend a mixed role assignment rather than only selecting whole-feature presets.

## 3.8 Persist capability and assurance configuration in workflow state

The selected role/model/effort configuration **and** assurance/rigor configuration should be recorded in `task_log.json` or equivalent workflow state.

Delegations should resolve their model and applicable assurance/re-review policy from that stored configuration rather than scattering model names or review-depth assumptions through workflow instructions.

If the user changes a role, model, effort, assurance level, or review policy mid-run, that should also be logged as a workflow-state change.

The FEC-bot example:

- lead Coder started as Luna Max;
- after execution-quality concerns, user changed lead Coder to Astra High;
- helpers stayed Luna Max.

That change should be durably visible in the workflow history.

## 3.9 No silent lead-role substitution

For lead roles:

- Planner
- Architect
- Coder
- Reviewer

the Orchestrator should **not silently substitute a cheaper/weaker model** because of availability, usage limits, or configuration failure.

If the requested model cannot be used:

- stop;
- tell the user;
- allow the user to choose an alternate model or wait.

Helper agents may optionally have a configured fallback policy because they are not the primary decision owner.

## 3.10 Assurance/rigor is an independent workflow axis

The FEC-bot review cycle showed that **model capability and assurance breadth must not be treated as the same setting**.

A task may need a very strong model because the reasoning is difficult while still having a small real-world blast radius. Conversely, a conceptually simple change may deserve unusually strong assurance because it affects credentials, destructive data, safety, money, public APIs, or many users.

A useful rule is:

> **Task difficulty determines how much intelligence is useful; consequence, reversibility, and blast radius determine how much verification is justified.**

This means Astra Max may be the correct Reviewer or Architect model without requiring the most exhaustive possible fresh review after every revision.

## 3.11 Named assurance/rigor profiles

Possible assurance shortcuts:

- `lean`
- `standard`
- `thorough`
- `high-assurance`
- `custom`

Illustrative semantics:

### `lean`
- intended for trivial/private/mechanical changes with low consequence and easy rollback;
- focused artifact/code validation;
- targeted re-review after repairs;
- normal deterministic tests/checks;
- no requirement for exhaustive criterion-by-criterion mutation-style review.

### `standard`
- appropriate default for ordinary private/internal feature work;
- full initial review of relevant approved artifacts and changed implementation;
- meaningful requirement/test traceability for changed behavior;
- subsequent review normally verifies prior findings, affected neighboring contracts, and the full regression suite rather than restarting every audit from zero.

### `thorough`
- appropriate for major features, broad refactors, public projects, persistent state, or meaningful operational risk;
- full adversarial initial Architect/Reviewer passes;
- broad re-review after production behavior or architecture changes;
- targeted re-review after test/doc-only repairs unless the repair exposes wider uncertainty;
- stronger edge-case and counterexample expectations.

### `high-assurance`
- reserved for security/safety/financial/high-impact infrastructure, difficult-to-recover data changes, or an explicit user request for forensic verification;
- current maximum-rigor behavior remains available: full spec reread, explicit criterion-to-code-to-test traceability, adversarial counterexamples, and fresh review from first principles on subsequent iterations when configured;
- cost is intentionally secondary to confidence.

### `custom`
- lets the user combine specific rules, including per-role overrides.

The exact profile names and thresholds remain implementation-design questions, but the two-axis concept should be normative.

## 3.12 Assurance should also be role-specific

Just as capability assignments can differ by role, assurance can differ by role.

Examples:

- **Planner:** depth of repository/research evidence, internal cross-checking, artifact consistency validation, and whether a revision must re-audit unaffected sections.
- **Architect:** breadth of source-grounded review, criterion traceability, edge-case analysis, and targeted-versus-full re-review after Planner changes.
- **Coder:** strength of Red/Green behavioral witnesses, verification breadth, and whether counterexample/mutation-style checks are required.
- **Reviewer:** initial review breadth, adversarial testing, criterion/test traceability, and whether each repair forces a fresh full review or a repair-scoped pass.
- **Helpers:** evidence-format discipline remains mandatory, while helper breadth/model can still be bounded by the parent role.

A configuration may therefore use Astra Max for Reviewer capability while selecting `standard` or `thorough` Reviewer assurance rather than `high-assurance`.

## 3.13 Re-review scope should follow repair class and assurance level

After a finding is fixed, the Orchestrator should classify the repair before launching another expensive pass.

Suggested repair classes:

1. **Material requirement/design/architecture or product-behavior change**
   - full relevant approval/review path;
   - full Architect/Reviewer re-review when required by the assurance profile.
2. **Production correctness fix within an already-approved design**
   - verify the defect and regression, affected neighboring contracts, and normal full checks;
   - broaden to a full fresh review only when the assurance profile or change radius warrants it.
3. **Test-only strengthening**
   - prove the new witness fails the demonstrated wrong behavior and passes the correct behavior;
   - run the required regression suite;
   - do not automatically restart the entire criterion/architecture audit outside `high-assurance`.
4. **Documentation/JSDoc/comment correction**
   - targeted source/doc consistency verification is normally sufficient.
5. **Accounting/spec reconciliation with no behavioral change**
   - targeted scope check;
   - user may explicitly waive another Architect pass when no design decision changed.

`high-assurance` may deliberately require a broader/full pass even for narrower repairs. Lower assurance profiles should not silently inherit that cost.

---

# 4. Strong lead + cheap helpers should replace “cheap autonomous lead”

## 4.1 Lesson from the Luna Coder experiment

The experiment was not “Luna is bad at coding.”

The better conclusion is:

> Luna Max was a poor fit as the autonomous lead implementer for a large, stateful, highly constrained feature where unexpected evidence had to be reconciled against a detailed approved design.

The lead Coder must do more than type the plan.

It must often:

- interpret unexpected behavior;
- understand when a test passes for the wrong reason;
- distinguish spec defects from implementation defects;
- choose which earlier Red/Green slice to reopen;
- notice cross-module invariants;
- avoid locally plausible changes that violate system contracts.

## 4.2 Preferred model pattern

Use:

> **Strong lead Coder + cheap supporting workers**

The lead owns:

- task sequencing;
- integration;
- debugging;
- interpretation of unexpected evidence;
- cross-cutting design consistency;
- final decisions inside approved scope.

Helpers can do:

- repository searches;
- locating affected tests;
- import/symbol census;
- repetitive fixture work;
- narrowly bounded implementation;
- mechanical file moves;
- focused verification.

## 4.3 General rule

A useful future guideline:

> **The more a role must reconcile unexpected evidence against an approved design, the stronger the lead model should be.**

Cheap models are best for:

- evidence gathering;
- bounded execution;
- repetitive edits;
- deterministic checks.

They should not be the sole synthesis point for ambiguous, cross-cutting decisions unless the feature is truly trivial.

---

# 5. Helper/subagent evidence discipline

## 5.1 Cheap explorers remain valuable

Luna Max remains attractive for supporting exploration because of cost/usage efficiency.

The workflow should continue to use inexpensive helpers heavily where appropriate.

## 5.2 Helpers should gather evidence, not own decisions

A helper report should be treated as an evidence package.

The stronger parent role should own:

- interpretation;
- decision;
- architectural synthesis.

## 5.3 Required evidence quality

Supporting agents should, where practical, report:

- exact files inspected;
- functions/types/tests examined;
- concrete observations;
- direct source locations;
- what was inferred rather than observed;
- what was not inspected;
- uncertainty or incomplete coverage.

This reduces anchoring from confident-but-incomplete summaries.

## 5.4 Parent verification rule

For decision-critical or exhaustive claims, the lead role should independently verify the important evidence before making the decision.

Examples:

- “this is the only runtime import”;
- “all tests already cover this”;
- “no other state transition renews expiry”;
- “this path is frozen everywhere”;
- “all external network calls use this helper.”

A Luna helper can locate likely evidence, but the parent should confirm exhaustive claims.

## 5.5 Escalate helper model only when exploration itself requires synthesis

Default helper: Luna Max.

Escalate a helper to Astra when the exploration task itself requires:

- ambiguous cross-subsystem synthesis;
- architectural judgment;
- reconciliation of contradictory evidence;
- high-risk security analysis;
- complex state-machine reasoning.

---

# 6. Feature branch should become first-class workflow state

## 6.1 Current gap

The Orchestrator Flow historically did not make the feature branch a strong first-class concept.

The FEC-bot run showed that branch state is crucial to:

- inspect current work from multiple tools/agents;
- resume after interruptions;
- review exactly what changed;
- keep spec and implementation aligned;
- preserve diagnostic evidence.

## 6.2 Desired behavior

At workflow initialization, establish:

- repository;
- feature branch;
- feature/spec directory;
- baseline commit.

The Orchestrator should keep this state available throughout the run.

## 6.3 No branch guessing

Roles should receive the active branch explicitly.

Reviewers should inspect that branch rather than assuming main/default branch state.

---

# 7. Meaningful workflow checkpoints should be committed and pushed

## 7.1 Why

A long feature can span:

- multiple days;
- model/session limits;
- user pauses;
- provider outages;
- failed live operations;
- model changes.

Durable checkpoints reduce the risk of losing state.

## 7.2 Checkpoint principle

> When tracked files change and the change represents a meaningful workflow-state transition or completed revision/implementation slice, commit and push a feature-branch checkpoint before handoff or a major gate.

Not every write needs a commit.

Avoid commit spam for tiny transient edits.

## 7.3 Useful checkpoint boundaries

Examples:

- initial proposal/research baseline;
- requirements approved;
- design approved;
- task plan approved;
- Architect review resolution complete;
- coding foundation complete;
- taxonomy maintenance complete;
- provider A complete;
- provider B complete;
- runtime cutover complete;
- formatting/confirmation changes complete;
- docs/test-maintenance complete;
- verification/reviewer checkpoint.

## 7.4 Commit identity should include workflow-state changes

`task_log.json` changes are not incidental.

If the task log records:

- approval;
- model change;
- blocker;
- review outcome;
- task milestone;
- live-operation result;

that state should normally be committed with the logical checkpoint.

---

# 8. Coding mini-milestones should be planned by the Planner

## 8.1 Problem

A 47-task plan is too long to treat as one uninterrupted coding phase.

## 8.2 Proposed solution

The Planner should define **mini-milestone/checkpoint boundaries** in the implementation plan.

These should not become fake numbered implementation tasks.

They can be annotations/group boundaries such as:

```text
Checkpoint A — Foundation complete
After Tasks 1–9:
- run focused foundation checks;
- ensure Green/refactor state;
- commit and push;
- record SHA and task-log milestone.
```

## 8.3 Checkpoint rules

Checkpoint only after stable boundaries:

- paired Red/Green completed;
- refactor complete;
- no deliberately red test remains in the just-completed slice.

Do not checkpoint in the middle of a Red/Green pair unless there is a genuine blocker and the incomplete state needs durable preservation.

## 8.4 Benefits

- easier resume;
- easier review;
- lower context reconstruction cost;
- more useful audit trail;
- localized regressions;
- clearer model-switch handoff;
- less risk when usage limits interrupt a run.

---

# 9. Preserve completed subagent evidence across interruptions

## 9.1 Problem

Usage/model interruptions can cause expensive work to be repeated.

A role may already have:

- explorer reports;
- file census;
- review evidence;
- failure reproduction;
- partial but valid conclusions.

## 9.2 Desired behavior

Completed subagent evidence should be durably preserved and reused when resuming.

The Orchestrator should not automatically restart expensive discovery merely because:

- the lead model changed;
- a session resumed;
- a usage cap interrupted work.

## 9.3 Resume behavior

On resume:

1. identify durable completed evidence;
2. identify unfinished work;
3. verify whether evidence is still current against branch SHA;
4. continue from the first genuinely incomplete step.

---

# 10. Approval gates should distinguish ordinary implementation from restricted actions

## 10.1 FEC-bot example

Task 15 demonstrated a bad stop/start pattern:

- the live generation attempt was correctly restricted;
- a diagnostic capture was separately authorized;
- diagnostic evidence exposed an ordinary in-scope parser defect;
- offline repair was already covered by the existing coding approval;
- another live MAL request still required explicit authorization.

The Orchestrator temporarily bundled:

- “fix parser offline”
- “make another live request”

into one approval question.

That caused an unnecessary stop.

## 10.2 Desired rule

The Orchestrator should separate:

### Already-authorized implementation work
Examples:
- fix a bug that clearly violates the approved design;
- add/update tests inside an approved Red/Green slice;
- perform offline deterministic validation.

### Separately restricted action
Examples:
- another live production/provider request;
- destructive external action;
- credential-bearing operation;
- a product decision not covered by spec.

Only the restricted part should require a new gate.

## 10.3 Stop only for genuine new authority

Once coding is approved, the Coder should not repeatedly return for permission to perform ordinary in-scope implementation.

Stop for:

- a genuine spec contradiction;
- a new product decision;
- an explicitly gated live/destructive operation;
- missing credentials/user input;
- a policy/security boundary requiring user authority.

---

# 11. User disposition gate after Architect findings

## 11.1 Current problem

A formal Architect can produce:

- must-fix;
- should-fix;
- nit findings.

Historically, the workflow can move directly from Architect findings to Planner revision.

That treats the Architect too much like a product owner.

## 11.2 Desired flow

Use:

> **Architect review → User disposition → Planner revision**

The user should see the findings before they trigger potentially expensive revision loops.

## 11.3 User disposition options

For each material finding, the user should be able to choose:

- accept;
- accept with clarification;
- accept but require a different resolution;
- reject/override with rationale;
- ask Architect to reconsider;
- defer as explicitly accepted risk.

## 11.4 `must_fix` semantics

`must_fix` should mean:

> blocking by default unless the user explicitly dispositions/overrides it.

It should not mean:

> Architect has authority to override product owner intent.

If the user overrides a must-fix, the rationale should be recorded.

## 11.5 Why this saves usage

This gate prevents:

- Planner revising something the user never wanted changed;
- Architect re-reviewing an unwanted Planner solution;
- repeated Astra Max cycles;
- wasted spec churn.

## 11.6 Architect re-review scope should be disposition- and repair-aware

After the user dispositions Architect findings and Planner revises the affected artifacts, the Orchestrator should not assume every change requires another complete Architect pass.

The re-review scope should be selected from:

- the configured Architect assurance level;
- the finding severity;
- whether requirements/product behavior changed;
- whether architecture/interfaces/state/error semantics changed;
- whether the revision is only task wording, documentation, or accounting reconciliation;
- the breadth of changed source/spec surfaces.

Examples:

- material state-machine or interface revision → full/broad Architect re-review;
- bounded design clarification → affected-section/source re-review;
- task-only translation of an already-approved design → targeted task/design consistency check;
- exact accounting reconciliation of previously user-authorized behavior → targeted review or explicit user waiver.

This resolves the earlier open question in principle: **targeted Architect re-review is valid and should be first-class; full re-review remains available when risk or assurance level justifies it.**

---

# 12. Approval of one artifact does not imply approval of another

## 12.1 FEC-bot example

The D7.1 long-MAL-URL issue caused:

1. a material design revision;
2. user approval of the new design behavior;
3. later task-plan changes to implement it.

Approving the design should not automatically imply that the new task plan is also approved.

## 12.2 Desired rule

Material design revision flow:

1. Planner revises design;
2. user approves revised design;
3. Planner updates tasks;
4. user explicitly approves updated task plan;
5. Architect re-reviews the affected/full spec as required.

## 12.3 Independent artifact gates

Requirements, design, and tasks have different responsibilities.

Approval should be explicit at the relevant boundary.

Do not infer:

- “design approved” → “tasks approved”;
- “requirements approved” → “implementation plan approved.”

---

# 13. Initial spec approval and pre-approval revision logging

## 13.1 Existing useful convention

The initial spec is not “approved” merely because Planner produced draft artifacts.

The user must explicitly approve.

A `spec-created` / equivalent final initial-approval event should not be recorded prematurely.

## 13.2 Improvement: record substantive draft changes incrementally

At the same time, pre-approval history should not disappear.

During the FEC-bot work, meaningful draft-stage feedback included things like:

- “Task 38 is too vague”;
- “tasks.md must not contain appendices”;
- “move these contracts into design.md”;
- “Revision History belongs at the end.”

These should be auditable.

## 13.3 Proposed event distinction

Possible conceptual event classes:

- draft change requested;
- Planner draft updated;
- draft approval granted;
- formal spec revision requested;
- approved spec revised;
- review finding dispositioned.

Exact event names can be decided later.

The important point:

- do not mislabel pre-approval changes as approved-spec revisions;
- do not discard the fact that substantive pre-approval changes occurred.

## 13.4 Record Planner wrappers incrementally

The Planner’s `spec_change_wrapper` response should be captured when a substantive revision is performed, not only reconstructed later.

This gives a reliable history of:

- what the user requested;
- what Planner changed;
- what remained unchanged;
- what was deferred.

---

# 14. Approval-gate behavior must be harness-native

## 14.1 Codex-specific lesson

In Codex, delegated subagents do not necessarily own the direct user conversation.

The Orchestrator is the component that can reliably:

- ask the user questions;
- request approval;
- receive answers;
- resume the appropriate role.

Therefore approval handling must be designed around the harness rather than assuming every role can directly ask the user.

## 14.2 Desired semantic rule

The workflow semantics should say:

> The Orchestrator owns user gates.

Each harness then implements that appropriately.

## 14.3 Audit implication

The Orchestrator should log:

- the role’s question/finding;
- the actual user response;
- the resulting revision/resume action.

Do not rely on hidden subagent conversation state as the only record.

---

# 15. Canonical spec artifact ownership

## 15.1 `proposal.md`

The proposal is the feature starting point.

It is not the authoritative final specification after planning evolves.

Use the current repository `proposal-template.md` when creating proposals.

Preserve whatever headings/title formatting the current template contains.

Do not confuse:

- reusable template files;
- completed proposal artifacts.

Likewise, use `bugreport-template.md` for bug reports when appropriate.

## 15.2 Canonical evolving spec artifacts

The authoritative planning artifacts are:

- `requirements.md`
- `design.md`
- `tasks.md`

## 15.3 `requirements.md`

Owns:

- user stories;
- acceptance criteria;
- normative behavior;
- required externally observable outcomes;
- major scope constraints.

It should not be a technical implementation dump.

## 15.4 `design.md`

Owns:

- technical architecture;
- module boundaries;
- interfaces/contracts;
- state machines;
- error/result unions;
- configuration semantics;
- algorithm/policy decisions;
- technical rationale;
- implementation-relevant invariants;
- important test-layer ownership when architectural.

If a contract is needed by multiple tasks or is the authoritative technical truth, it belongs here rather than in a `tasks.md` appendix.

## 15.5 `research.md`

Owns:

- empirical discovery;
- experiments;
- current code findings;
- upstream behavior;
- measured limitations;
- source census;
- evidence that informed design.

Research is evidence, not the final normative implementation contract.

## 15.6 `tasks.md`

Owns:

- numbered executable work;
- exact file/task targets;
- Red/Green/Refactor/Documentation/Test-Maintenance/Verification actions;
- focused checks;
- requirement mapping;
- sufficient implementation instruction for Coder.

It should not become a second design document.

## 15.7 `task_log.json`

Owns:

- process history;
- user approvals;
- review wrappers;
- change requests;
- role transitions;
- model changes;
- blockers;
- checkpoints;
- implementation milestones;
- verification/review outcomes.

---

# 16. No appendices in `tasks.md`

## 16.1 Problem encountered

The Planner responded to “make the tasks detailed enough for Luna” by adding large Appendices A–H to `tasks.md`.

The content was useful, but the artifact structure was wrong.

The appendices contained:

- interface contracts;
- design decisions;
- evidence;
- code census;
- test ownership;
- helper APIs.

## 16.2 Rule

> **`tasks.md` should have no appendices.**

## 16.3 Redistribution

When detailed support material exists:

- technical contract → `design.md`;
- evidence/discovery → `research.md`;
- executable instruction → numbered task;
- process history → `task_log.json` / wrapper.

## 16.4 Important nuance

“No appendices” must **not** become an excuse to make tasks vague.

The tasks must still tell the Coder exactly what to do.

They may reference authoritative design sections for complex contracts, but the task itself should specify:

- what file;
- what behavior;
- what test;
- what boundary;
- what verification.

---

# 17. Canonical Revision History rule

## 17.1 Canonical files

Revision History rules apply to:

- `requirements.md`
- `design.md`
- `tasks.md`

## 17.2 When to add it

A canonical file gains a Revision History **only after that specific file changes from its initial version**.

Examples:

- requirements never changed after initial creation → no Revision History required;
- design changed after initial approval → add Revision History to design;
- tasks changed after Architect findings → add Revision History to tasks.

## 17.3 Once present, keep it

After a file has a Revision History:

- preserve it;
- append new entries;
- do not remove prior entries.

## 17.4 Placement

Revision History should be the **last top-level section**.

## 17.5 `research.md`

Research is auxiliary.

Revision History is optional, not required.

---

# 18. Task authoring must leave no architecture discovery to the Coder

## 18.1 Desired level of specificity

The Planner should resolve:

- affected modules;
- ownership boundaries;
- helper/API shape;
- expected test layer;
- existing behavior that must remain;
- exact failure semantics;
- known edge cases;
- refactor/test-maintenance disposition.

The Coder should not be asked to “explore and decide” what the architecture should be.

## 18.2 But implementation is not perfectly mechanical

Even a detailed plan cannot predict all real implementation evidence.

Therefore:

- Planner removes foreseeable ambiguity;
- Coder still needs enough capability to handle unexpected reality.

This is another reason the lead Coder should often be Astra High rather than Luna Max.

---

# 19. Red / Green / Refactor ownership rules

The FEC-bot work clarified strict task boundaries that should remain part of Orchestrator Flow.

## 19.1 Red

Red tasks should change:

- tests;
- test fixtures/helpers when needed for the Red.

They should:

- demonstrate missing behavior;
- fail for the intended reason;
- avoid production implementation.

## 19.2 Green

Green tasks should change:

- production/non-test code;
- owning source JSDoc/comments that are part of the implementation contract.

They should:

- implement only enough to satisfy the preceding Red and approved design;
- not modify tests.

If Green reveals that an assertion is missing or wrong, go back to Red rather than casually editing tests inside Green.

## 19.3 Refactor

Refactor tasks:

- production code only;
- no behavior change;
- no test changes;
- should preserve the now-green behavior.

## 19.4 Documentation

Documentation tasks:

- docs only, unless explicitly defined otherwise.

Source JSDoc should usually be handled in the Green task that owns the source change.

## 19.5 Verification

Verification tasks:

- make no changes;
- run checks;
- report results.

A failed verification returns to the owning task category rather than “fixing things inside Verification.”

---

# 20. Final Test-Maintenance is deliberate and mandatory

## 20.1 Important discovery

There was an initial temptation to distribute all test cleanup earlier and remove the final Test-Maintenance phase.

Reading the actual Planner contract showed that this would be wrong.

## 20.2 Why it exists

TDD Red tests may legitimately contain temporary implementation-oriented scaffolding:

- spies;
- decomposition assertions;
- duplicate cases;
- transitional fixtures;
- overly narrow implementation witnesses.

Once implementation is complete, the final regression suite should focus on durable behavioral contracts.

## 20.3 Planner decides disposition

Before Coder reaches Test-Maintenance, the Planner should have already decided:

- keep;
- merge;
- remove;
- rewrite;
- move;
- table-drive;
- replace with stronger behavioral coverage.

The Coder should **execute**, not audit/decide.

## 20.4 Coder should not rediscover test architecture

A task like:

> “review the tests and remove brittle ones”

is not acceptable.

Instead:

> “merge tests A/B into test C while preserving cases X/Y; remove temporary spy assertion Z because durable service behavior is covered by test D.”

## 20.5 Test-Maintenance occurs before Verification

Desired sequence:

1. feature implementation complete;
2. Test-Maintenance executes Planner-owned durable-test disposition;
3. Verification runs the final suite/checks.

---

# 21. JSDoc ownership

Source JSDoc should generally be implemented with the **Green task that creates or changes the owning API**.

Avoid a late “documentation” task that must rediscover every changed exported contract.

A documentation task may still update:

- README;
- technical-reference docs;
- operator guidance.

But source/API JSDoc is part of implementation ownership.

---

# 22. Formal Architect and Reviewer should be adversarial and source-grounded

## 22.1 Architect role

Architect should not merely read the prose and say it looks reasonable.

It should verify against:

- current source;
- tests;
- real paths;
- state transitions;
- edge conditions;
- requirement coverage.

The FEC-bot Architect found issues that earlier review missed:

- Search Again expiry reset behavior;
- wrong frozen archived paths;
- a stale frozen-doc link;
- overlong accepted MAL URL sendability;
- malformed-detail test assigned to the wrong lookup path.

This validates the value of a strong adversarial review.

## 22.2 Reviewer role

Final Reviewer should similarly verify actual implementation against:

- requirements;
- design;
- tasks;
- final tests;
- known review findings;
- changed branch state.

## 22.3 Avoid false equivalence between review and ownership

Architect/Reviewer identify correctness risks.

The user remains the authority for product decisions and explicit accepted risk.

## 22.4 Adversarial review does not require identical breadth on every pass

The requirement that Architect/Reviewer be skeptical and source-grounded should remain. V2 should **not** weaken the initial formal review.

What changes is the assumption that skepticism always requires restarting the entire audit from zero after every repair.

A targeted re-review can still be adversarial:

- reproduce the prior defect or wrong-behavior counterexample;
- verify the fix;
- inspect affected neighboring contracts;
- run the required regression/static checks;
- challenge the changed assertions for meaningfulness;
- broaden scope if new evidence suggests a systemic issue.

The assurance profile decides whether that targeted process is sufficient or whether a full fresh review is mandatory.

## 22.5 Initial review and re-review are separate policy decisions

A project may configure:

- full/high-capability initial Architect review;
- full/high-capability initial Reviewer review;
- risk-adjusted targeted re-review after bounded fixes.

This is not a downgrade in model quality. It is a change in verification breadth.

For `high-assurance`, fresh full re-review may remain mandatory. For lower profiles, test/doc-only or narrowly bounded repairs should normally receive targeted re-review.

## 22.6 Reviewer findings should move from hypothesis to demonstrated defect where practical

For actionable behavioral findings, a useful evidence progression is:

> **Reviewer finding → reproducible failing witness → repair → green regression → re-review.**

A finding does not need to be blindly accepted merely because a strong model produced it. The Coder should reproduce it when practical, and the Reviewer should verify the resulting witness is meaningful rather than tautological.

The original FEC-bot bounded-body/taxonomy findings followed this pattern and became stronger once the Coder independently reproduced them with failing tests.

---

# 23. Usage/resource efficiency should be an explicit workflow goal

The workflow should acknowledge modern model economics directly.

Goal:

> Invoke expensive models when the evidence is already assembled and the decision scope is clear.

Preferred ordering:

1. cheap evidence gathering;
2. capable Planner synthesis;
3. user gate;
4. expensive Architect at the configured assurance breadth;
5. user disposition;
6. targeted Planner revision;
7. risk/repair-class decision for targeted versus full Architect re-review;
8. strong Coder lead with cheap helpers;
9. expensive final Reviewer when implementation is ready;
10. risk/repair-class decision for targeted versus full Reviewer re-review.

Avoid:

- repeated Astra Max review of unstable drafts;
- expensive reviewers discovering basic missing source evidence;
- Planner revisions before user agrees with findings;
- restarting completed exploration after interruptions;
- automatically equating strongest model with maximum assurance;
- automatically restarting a full spec/criterion/source audit after a test-only or documentation-only repair;
- unbounded expensive review loops whose later passes find only progressively smaller witness/documentation issues on a low-blast-radius project.

## 23.1 Diminishing returns should be an explicit workflow concept

The FEC-bot final review cycle provided a concrete example. The first formal Reviewer pass found genuine production cleanup/typed-contract defects that earlier review and 1,525 passing tests had missed. That high-end adversarial review clearly added value.

After those production defects were fixed, later full passes found increasingly narrow issues:

- a confirmation-clock test that did not distinguish the correct clock from an incorrect implementation;
- documentation/JSDoc accuracy;
- formatter reduction-priority witness strength;
- original-draft preservation witness strength;
- startup override witness strength;
- provider-free upcoming-list witness strength.

Those were legitimate findings and improved the suite, but the later repairs did not change production behavior. Re-running a complete maximum-rigor review after every such repair consumed disproportionate premium-model usage for a private bot with a small user population.

The lesson is not to weaken the Reviewer. It is to make **review breadth proportional to configured assurance and actual repair risk**.

## 23.2 Suggested loop-control rule

After the first full formal review, every subsequent re-review should record:

- repair class;
- changed surfaces;
- whether production behavior changed;
- whether requirements/design changed;
- configured assurance profile;
- selected re-review scope (`targeted`, `broad`, or `full`);
- reason for that scope.

If a full re-review finds **no new production/spec defect** and only test-quality/documentation findings, then another full fresh review should require one of:

- `high-assurance` configuration;
- a newly material production/spec change;
- new evidence of systemic risk;
- explicit user approval.

Otherwise, the next pass should normally be targeted/broad rather than automatically full.

## 23.3 High assurance remains available

This cost control must not remove the current forensic mode.

For genuinely high-consequence work, the user may intentionally choose:

- fresh full review after every repair;
- explicit criterion-to-code-to-test traceability;
- adversarial counterexample/mutation testing;
- repeated source-grounded audits;
- confidence prioritized above model cost.

The problem is not that this mode exists. The problem is applying it implicitly to every difficult task merely because the strongest model is selected.

---

# 24. Process state should support explicit blockers

A blocker should record:

- task number;
- exact reason;
- what was attempted;
- what evidence exists;
- what is authorized next;
- what requires new user authority.

Example from FEC-bot:

```text
Task 15 blocked:
- first authorized live generation failed invalid_structure;
- no retry authorized;
- offline evidence insufficient because original body not retained;
- one bounded diagnostic capture authorized;
- diagnostic isolated parser defect;
- offline repair is already authorized;
- second live generation remains separately gated.
```

This is much more useful than simply `status: blocked`.

---

# 25. Live-operation gates should be narrowly scoped

When a task involves external/live work, the plan should define:

- exact operation;
- maximum number of requests;
- redirect policy;
- retry policy;
- credential policy;
- body/deadline bounds;
- what happens on failure;
- whether offline validation may continue without another gate.

Then the user can authorize precisely.

This prevents the Orchestrator from repeatedly asking for broad permission.

---

# 26. User approval should carry forward within its scope

Once the user approves implementation:

- ordinary in-scope offline coding should continue;
- do not ask again at every local defect;
- do not treat each reopened Red/Green slice as a new product decision.

Approval should stop carrying forward only when:

- spec contradiction appears;
- new product behavior is required;
- restricted external action is reached;
- user input/secret is needed;
- destructive/high-risk boundary is crossed.

---

# 27. Cross-harness workflow semantics vs harness implementation

Orchestrator Flow currently spans multiple harnesses:

- Codex;
- GitHub Copilot;
- Claude Code;
- Cursor.

The future redesign should separate:

## 27.1 Canonical workflow semantics

Examples:

- startup resource gate;
- Planner owns spec creation;
- Architect review;
- user disposition;
- Coder implementation;
- checkpoint rules;
- task-log semantics;
- Revision History rules;
- final Reviewer.

## 27.2 Harness-specific adaptation

Each harness may implement those semantics differently.

Examples:

- Codex: skill/subagents;
- GitHub Copilot: custom agents;
- Claude Code: skill/subagent mechanics;
- Cursor: instruction/ruleset flow.

Do not force identical low-level mechanics where the products differ.

## 27.3 Future parity matrix

A useful future deliverable would be a matrix with rows such as:

- user approval gate;
- subagent delegation;
- role/model assignment;
- model fallback;
- branch awareness;
- persistent workflow state;
- task-log updates;
- checkpoint commits;
- resume behavior;
- role handoff;
- user question routing.

Columns:

- Codex
- Copilot
- Claude Code
- Cursor

This would show which parts are canonical semantics and which need harness-specific implementation.

---

# 28. Current harness priorities

Based on usage discussed:

- **Codex** is currently the most heavily exercised implementation and the immediate source of workflow lessons.
- **GitHub Copilot** was historically the primary/mature implementation and should not be allowed to drift too far behind newer conventions.
- **Claude Code** is used sometimes and should stay maintained.
- **Cursor** is rarely used but should remain reasonably compatible.

This work is deferred until the FEC-bot v2 effort is complete.

---

# 29. Proposal and bug-report template conventions

The workflow should preserve these existing project conventions:

- use `proposal-template.md` as the reusable proposal template;
- use `bugreport-template.md` as the reusable bug-report template;
- preserve the current template’s actual title and section formatting;
- do not rely on memorized older wording;
- do not confuse the reusable template file with a completed proposal/bug-report artifact.

The proposal is the starting point; the evolving spec becomes authoritative later.

---

# 30. Suggested future workflow state machine

The exact implementation can vary by harness, but the desired semantics look roughly like this:

## Phase 0 — Initialization

1. Identify repo / branch / feature directory.
2. Inspect proposal.
3. Evaluate **task complexity/capability need** and **project/change risk/assurance need** separately.
4. Show default role/model/effort assignments.
5. Show default assurance profile, per-role assurance overrides and re-review policy.
6. Recommend any capability or assurance overrides.
7. User accepts/overrides either axis.
8. Persist capability and assurance configuration.
9. Commit/push initialization state if tracked artifacts changed.

## Phase 1 — Requirements

1. Planner researches current code/docs as needed.
2. Planner creates/updates `requirements.md`.
3. User reviews.
4. Pre-approval changes are logged as draft changes.
5. User explicitly approves requirements.

## Phase 2 — Design

1. Planner creates/updates `design.md` and `research.md`.
2. Planner resolves implementation-significant empirical questions during design where possible.
3. User reviews.
4. Planner revises if requested.
5. User explicitly approves design.

## Phase 3 — Tasks

1. Planner creates fully executable `tasks.md`.
2. No appendices.
3. Red/Green/Refactor/Documentation/Test-Maintenance/Verification boundaries explicit.
4. Mini-milestone checkpoint annotations included.
5. User reviews.
6. User explicitly approves task plan.

## Phase 4 — Architect review

1. Architect performs adversarial source-grounded review at the configured capability and assurance level.
2. Findings returned to Orchestrator.
3. **User disposition gate occurs before Planner revision.**
4. User accepts/rejects/changes resolution per finding.
5. Planner revises only dispositioned items.
6. Any materially changed design/tasks return to their explicit approval gates.
7. Orchestrator classifies the revision (material architecture/product, bounded design clarification, task-only translation, documentation/accounting, etc.).
8. Architect performs targeted, broad or full re-review according to repair class and assurance profile; no automatic full restart outside policies that require it.
9. Approved spec checkpoint committed/pushed.

## Phase 5 — Coding

1. Strong lead Coder owns integration.
2. Cheap helpers do bounded work.
3. Ordinary approved implementation continues without repeated user permission.
4. Mini-milestone checkpoints:
   - focused checks;
   - commit/push;
   - SHA/task-log update.
5. Genuine blockers recorded precisely.
6. Restricted live/destructive actions get narrow user gates.

## Phase 6 — Test Maintenance

1. Execute Planner-owned final test dispositions.
2. No fresh audit by Coder.
3. Produce durable regression suite.

## Phase 7 — Verification

1. Full tests/typecheck/lint/etc.
2. No edits.
3. Failure returns to owning task.

## Phase 8 — Reviewer

1. Strong Reviewer validates implementation against approved spec and branch at the configured assurance breadth.
2. Findings go through user disposition if material.
3. Coder reproduces actionable behavioral findings with failing witnesses where practical, then repairs within approved scope.
4. Orchestrator classifies each repair and selects targeted, broad or full re-review according to assurance policy.
5. Test/doc-only repairs normally receive targeted witness verification plus required regression/static checks unless `high-assurance` or new evidence requires a full fresh pass.
6. Production/spec changes receive broader/full re-review as warranted.
7. Final Reviewer acceptance is recorded only when no unresolved findings remain under the configured policy.
8. Final workflow checkpoint.

---

# 31. Suggested data to record in `task_log.json`

Potential categories:

## Workflow initialization
- feature;
- branch;
- baseline SHA;
- selected role models/efforts;
- selected capability/resource profile;
- selected assurance/rigor profile;
- per-role assurance overrides;
- re-review policy;
- user overrides;
- capability/complexity recommendation;
- assurance/risk recommendation.

## Spec lifecycle
- draft creation;
- user change request;
- Planner revision wrapper;
- artifact approval;
- Architect review;
- user finding disposition;
- revision/repair class;
- selected Architect re-review scope and rationale;
- revised artifact approval;
- final Architect acceptance.

## Coding lifecycle
- coding start;
- current lead model;
- helper model;
- task-range milestone;
- checkpoint SHA;
- blocker;
- live-operation authorization;
- live-operation result;
- model-role change.

## Final lifecycle
- Test-Maintenance complete;
- Verification results;
- Reviewer findings;
- finding reproduction status where applicable;
- repair class;
- selected Reviewer re-review scope and rationale;
- review-pass count;
- user disposition;
- implementation complete.

Do not force giant blobs into every event; preserve structured references to the artifacts/wrappers where possible.

---

# 32. Potential workflow configuration object

This is an illustrative implementation idea, not a finalized schema:

```json
{
  "workflow_config": {
    "capability": {
      "profile": "maximum",
      "planner": {
        "model": "gpt-6-astra",
        "effort": "high"
      },
      "architect": {
        "model": "gpt-6-astra",
        "effort": "max"
      },
      "coder": {
        "model": "gpt-6-astra",
        "effort": "high"
      },
      "reviewer": {
        "model": "gpt-6-astra",
        "effort": "max"
      },
      "helpers": {
        "model": "gpt-5.6-luna",
        "effort": "max"
      }
    },
    "assurance": {
      "profile": "thorough",
      "planner": "thorough",
      "architect": "thorough",
      "coder": "thorough",
      "reviewer": "high-assurance",
      "re_review_policy": {
        "material_spec_or_architecture_change": "full",
        "production_behavior_fix": "broad",
        "test_only_repair": "targeted",
        "documentation_only_repair": "targeted",
        "accounting_only_repair": "targeted"
      }
    }
  }
}
```

The example intentionally demonstrates mixed settings: a project can use maximum-capability models while choosing less-than-maximum re-review breadth, and it can give one role (for example Reviewer) stronger assurance than the rest.

The exact schema, profile names, model names and inheritance rules should be defined when the workflow project is updated.

---

# 33. Potential capability and assurance recommendation categories

The Orchestrator should make two recommendations rather than collapsing all signals into one generic "complexity" score.

## 33.1 Capability/resource recommendation factors

An eventual Orchestrator implementation could classify the reasoning/execution difficulty using factors such as:

| Factor | Lower-complexity signal | Higher-complexity signal |
|---|---|---|
| Scope | 1–2 files / one module | many modules / runtime wiring |
| Architecture | existing pattern | new boundary/abstraction |
| State | stateless | state machine / locking |
| Persistence | none | migration / durable data |
| External systems | none/mocked | live APIs / credentials |
| Security | low | secrets / auth / SSRF-like boundaries |
| Compatibility | none | backward/frozen compatibility |
| Tests | small local | broad migration |
| Ambiguity | fully specified | unresolved edge behavior |
| Runtime risk | cosmetic | startup / provider / write path |

This recommendation primarily answers: **how capable does the role/model need to be to reason correctly about the work?**

## 33.2 Assurance/rigor recommendation factors

Assurance should be recommended separately using consequence-oriented signals such as:

| Factor | Lower-assurance signal | Higher-assurance signal |
|---|---|---|
| Blast radius | private/local, few users | public/widely used/critical dependency |
| Reversibility | easy rollback/re-run | destructive or difficult recovery |
| Data durability | disposable/reconstructable | persistent user/business data |
| Security exposure | no secrets/auth boundary | credentials/auth/security-sensitive boundary |
| External side effects | mocked/local only | live writes, deployments, paid/irreversible actions |
| Safety/legal/financial consequence | none/low | safety, legal, financial, regulated impact |
| Failure visibility | obvious and easy to diagnose | silent/corrupting/difficult to observe |
| Recovery cost | minutes and low consequence | expensive/manual/high-consequence recovery |
| Compatibility surface | private implementation | public API/frozen protocol/backward-compat contract |
| User preference | ordinary confidence | explicit forensic/high-assurance request |

This recommendation answers: **how much evidence and repeated verification is justified before accepting the work?**

A technically difficult but low-blast-radius private project may therefore receive **maximum capability + standard/thorough assurance**. A conceptually simple credential rotation or destructive migration may receive **moderate capability + high assurance**.

Both recommendations should remain advisory and user-overridable.

---

# 34. What should *not* happen

The future workflow should avoid:

- silently downgrading a lead role;
- making the user choose models repeatedly mid-run for ordinary work;
- using Architect findings as automatic product decisions;
- revising tasks before the user has approved a material design change;
- putting design appendices into `tasks.md`;
- asking Coder to perform Planner-owned discovery;
- letting Coder decide final test-maintenance strategy ad hoc;
- treating `proposal.md` as the final authoritative spec;
- restarting completed explorer work after every resume;
- committing every tiny edit;
- going too long without any durable checkpoint;
- bundling authorized offline work with separately gated live operations;
- letting cheap helper conclusions become authoritative without parent verification;
- treating the strongest selected model as an implicit request for maximum assurance;
- silently raising or lowering assurance because a model or usage limit changes;
- forcing a complete fresh Architect/Reviewer audit after every bounded test/doc/accounting repair outside a policy that requires it;
- allowing repeated full-review loops to continue indefinitely on a low-risk project without either new material risk, `high-assurance` configuration, or a user gate.

---

# 35. Practical lessons from the FEC-bot run

## 35.1 Detailed planning helped, but did not eliminate the need for a strong Coder

The v2 spec became exceptionally detailed:

- 47 tasks;
- 17 Red/Green pairs;
- 65 acceptance criteria mapped;
- explicit provider contracts;
- explicit taxonomy semantics;
- formal Architect approval.

Even then, implementation encountered a real-world parser issue.

Therefore “make the plan detailed enough that the Coder needs no reasoning” is not a safe design goal for large features.

## 35.2 The Architect found valuable issues after extensive informal review

Formal adversarial review was worth the cost.

It found:

- state-transition nuance;
- path errors;
- frozen-doc nuance;
- Discord message-boundary issue;
- test ownership/provenance problem.

Therefore the workflow should keep a strong formal review role.

## 35.3 User disposition before revision would save expensive loops

Several findings were product-sensitive enough that automatic Planner revision would have been inappropriate.

This should become a first-class gate.

## 35.4 Artifact hygiene matters

The “Appendices A–H” episode showed that detailed information still needs the right home.

Artifact ownership is not cosmetic; it prevents the Coder from reading conflicting or duplicated sources of truth.

## 35.5 Checkpoints improve resilience

When the parser live run failed, having commits/task-log state made it possible to:

- inspect exactly what happened;
- switch lead model;
- preserve diagnostic evidence;
- continue from the blocker.

This should be planned rather than accidental.

## 35.6 Strong review was valuable, but maximum-rigor repeated re-review became disproportionate

The final FEC-bot code-review sequence supplied a second stress test after the original notes were compiled.

The first Astra Max Reviewer pass was clearly worthwhile:

- it found real response-cleanup and typed-reader-contract defects;
- those defects had survived extensive implementation work, informal review and a 1,525-test green suite;
- the Coder independently reproduced them with failing Red tests before repair.

However, the workflow then required repeated full fresh re-review. Across the next passes, production behavior was already correct and the new findings were primarily:

- test witnesses that did not reject plausible wrong implementations;
- documentation/JSDoc wording;
- proof that provider-free or override behavior was meaningfully protected.

Those improvements were useful, but obtaining them required several more full Astra Max review cycles, supporting-agent audits, repeated full-suite execution and multiple usage resets. For a private Discord bot affecting only a small group, the marginal confidence eventually became disproportionate to the resource cost.

The lesson is:

> **Keep the strong adversarial role, but make assurance breadth and re-review scope independently configurable from model strength.**

The final workflow should be able to preserve the exact current maximum-rigor behavior for high-consequence work while using targeted/broad follow-up review for lower-risk projects.

---

# 36. Priority order for future Orchestrator Flow improvement work

When the separate workflow project is revisited, a sensible priority could be:

## Priority 1 — Workflow control / user authority
- startup capability/resource **and assurance/rigor** gate;
- no silent lead-role model or assurance fallback;
- Architect → user disposition → Planner revision;
- repair-class-based targeted/broad/full re-review selection;
- separate renewed design/task approvals.

## Priority 2 — Durable state
- branch as first-class state;
- checkpoint commit/push rules;
- task-log checkpoint/model/blocker events;
- resume from completed evidence.

## Priority 3 — Artifact rules
- no `tasks.md` appendices;
- canonical artifact ownership;
- Revision History rule;
- stronger task specificity contract;
- final Test-Maintenance disposition rules.

## Priority 4 — Capability/assurance economics
- independent capability and assurance recommendations;
- named capability/resource profiles;
- named assurance/rigor profiles;
- role-specific overrides on both axes;
- diminishing-return/review-loop policy;
- strong lead + Luna helpers;
- parent verification of helper evidence.

## Priority 5 — Cross-harness parity
- canonical semantics;
- Codex/Copilot/Claude/Cursor adaptation matrix;
- bring older harness implementations up to current workflow rules.

---

# 37. Open implementation questions for the future workflow project

These were not fully settled and can be decided during the Orchestrator Flow improvement proposal/design:

1. Exact names of capability/resource profiles (`economy`, `standard`, `maximum`, etc.).
2. Exact names and semantics of assurance/rigor profiles (`lean`, `standard`, `thorough`, `high-assurance`, etc.).
3. Exact `task_log.json` schema for capability, assurance, per-role overrides and selected re-review scope.
4. Whether helper-model fallback is automatic or user-configurable.
5. Exact event names for pre-approval draft revisions.
6. Whether every artifact approval creates a checkpoint commit or only certain gates.
7. How Planner encodes mini-milestone boundaries without turning them into fake tasks.
8. Exact thresholds/rules for targeted vs broad vs full Architect re-review after each repair class; the principle that targeted re-review is valid is now settled.
9. Exact thresholds/rules for targeted vs broad vs full Reviewer re-review, including when test/doc-only changes may trigger escalation.
10. How user overrides of `must_fix` findings are represented in task log.
11. How the workflow detects “material design change” versus ordinary task clarification/accounting reconciliation.
12. How resume logic verifies that saved helper evidence is still valid for the current branch SHA.
13. How much of the capability and assurance recommendation rubrics are rule-based versus model judgment.
14. Whether repeated full-review loops should have a configurable user-gate/pass-count threshold below `high-assurance`.
15. How assurance inheritance works when the global profile and role-specific overrides disagree.
16. How to express the same semantic workflow across the four harnesses without forcing identical mechanics.

---

# 38. Final consolidated target

The desired Orchestrator Flow is one where:

- the feature branch and workflow state are explicit;
- the user chooses or accepts both a capability/resource plan and an assurance/rigor plan before work begins;
- the Orchestrator can recommend cheaper or stronger roles based on task difficulty;
- the Orchestrator can independently recommend leaner or stronger assurance based on blast radius, consequence, reversibility and user preference;
- strong models own synthesis and cross-cutting decisions;
- Luna-class helpers gather evidence and perform bounded work;
- Planner leaves no foreseeable architecture discovery to Coder;
- Architect reviews adversarially against real source at the configured assurance breadth;
- user dispositions review findings before revision;
- Architect re-review can be targeted, broad or full according to repair class and assurance policy;
- artifact approvals are separate and explicit;
- canonical files have clear ownership and clean Revision History rules;
- long implementations have planned stable checkpoints;
- task-log state is durable and committed;
- ordinary approved implementation does not stop unnecessarily;
- live/destructive operations have narrow explicit gates;
- completed evidence survives interruptions;
- expensive models are used at maximum information/minimum churn;
- model capability is not conflated with maximum review breadth;
- repeated review scope is risk- and repair-aware, with full fresh re-review preserved for high-assurance cases;
- final Test-Maintenance produces a durable regression suite;
- final Reviewer validates the real implementation rather than merely trusting earlier plans;
- all four supported harnesses implement the same workflow semantics in harness-native ways.

---

# End

These notes intentionally preserve both the **specific workflow changes we agreed on** and the **reasoning that led to them**, so they can later be converted into a proper Orchestrator Flow proposal, requirements/design/tasks spec, and cross-harness implementation plan without having to reconstruct the FEC-bot discussion.
