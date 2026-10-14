# Assurance, evidence and finding policy

Use one accepted feature assurance level independently of per-role capability. All levels retain Planner, Architect, Coder, Reviewer, requirements/design/tasks, their approval gates, and the task execution structure. Each level includes an initial review of the complete relevant spec and complete relevant implementation. Lower assurance changes scrutiny and obligations, not coverage to a convenient subset.

The exceptional phase policy in `implementation-phases.md` sets review-stage rigor without changing feature assurance: no intermediate review at Basic, Basic at Standard, Standard at Maximum. Architect and the final whole-feature review retain the full feature assurance. Initial coverage means the entire applicable stage and dependencies, with complete current spec bodies; future-phase implementation is not an omission. Intermediate readiness does not grant final acceptance or waive a condition under final assurance. Preserve explicit user dispositions and their revisit conditions.

## Classification before remediation

Every finding describes the factual behavior, triggering conditions and practical consequences for the actual project. Distinguish a demonstrated correctness problem, a hardening opportunity, and a preference. Classify against the feature's agreed acceptance standard without hiding facts. Consider exposure, affected users, likelihood, reversibility, recovery cost and user preference.

A private local bot and a consequential production deployment can warrant different completion priorities for the same factual concern. For example, an optional automatic retry mechanism may be an accepted limitation or nit when manual retry is adequate, but a should-fix concern when unattended recovery is an agreed operational requirement. A demonstrated violation of an approved requirement remains a defect; describing it accurately and obtaining any explicit exception is mandatory.

| Dimension | Basic | Standard | Maximum |
| --- | --- | --- | --- |
| Initial coverage | Complete relevant work, emphasizing intended use and consequential failures | Complete work with meaningful robustness/regression evidence | Complete exhaustive, adversarial review |
| Follow-up | Focused repair verification, expanding when evidence/consequences warrant | Impact-based focused, affected or full review | Fresh comprehensive re-review on each required pass |
| Should-fix | Weigh practical benefit, likelihood, consequence and total workflow cost | Stronger presumption toward fixing | Fix unless concretely risky/scope-expanding; justify deferral |
| Nit | Nonblocking; derive deferral without another producer/user pass | Nonblocking; retain an adequate result | Nonblocking; fix straightforward nits alongside necessary repairs only |
| More repair cycles | User decision before cycle 2 | User decision before cycle 3 | Existing rigorous loop and stalled-loop safeguards |
| Research continuity | Check relevant sources/assumptions; reuse valid evidence; repeat affected/incomplete work | Same rule | Actively revalidate decision-critical observations and conclusions even when sources appear unchanged |

`must_fix` blocks acceptance unless the user explicitly dispositions it under policy with rationale. Orchestrator never waives it independently. Keep the factual finding in history. At Maximum, time/priority alone is not a justified deferral. At lower assurance, a possible improvement is not automatically a completion requirement. Lower-level producers may record that the current result is adequate rather than fix every easy nit.

Behavioral repairs should first reproduce a meaningful failing witness where practical, then verify the repair at the applicable assurance. Do not restart a full lower-assurance audit solely because a narrower witness or documentation improvement was made. Do not reopen a settled disposition without new evidence, changed behavior or its relevant revisit condition.

## Review scope and limits

For a repair follow-up record `repair_class`, `changed_surfaces`, `review_scope`, `scope_reason` and `meaningful_change`. Applicability-only catch-up is not a producer repair. Standard normally uses:

| Repair class | Scope |
| --- | --- |
| `editorial`, `test_documentation` | `focused`: change and relevant consistency |
| `bounded_correctness` | `affected`: repair, meaningful evidence and neighboring contracts |
| `architectural_systemic` | `full`: relevant work where architecture/conclusions/systemic evidence changed |

Basic normally starts focused and expands with practical consequences. Maximum is always comprehensive. Broaden when evidence warrants it; a new invocation is not a reason on its own. Focused review does not ignore failed required checks, approved requirements, or preservation boundaries.

Count a cycle only after a producer repair and the corresponding completed re-review. Initial reviews, interim checkpoints and invocation retries do not count. Spec and implementation have separate counts. At the limit, if more repair is needed, present remaining findings and the expected value of more work, then obtain continuation, permitted deferral, scope or assurance direction. Acceptance does not trigger an unnecessary pause. A generic continue grants one more cycle, not a reset. Preserve counts across settings/model/context changes.

Also detect the same must-fix identities across two reviews without meaningful progress, and more than three revision cycles without status improvement. Review outputs identify whether meaningful progress occurred; do not equate a new wrapper/checkpoint ID with a repair. Summarize attempts and unchanged blockers and obtain direction. Existing explicit finding decisions can be reused; do not pretend they were newly granted.

## Evidence and interruptions

Helpers provide inspected sources with enough path/revision/date/experiment context to check applicability; concrete observations; separate inferences; assumptions; coverage gaps; and uncertainty. Leads synthesize and verify decision-critical claims at the feature's assurance. Helper confidence is not evidence.

Preserve completed reports and relevant research across usage interruptions, model changes and resumed sessions. Basic and Standard check whether relevant sources and assumptions changed, reuse valid completed evidence, and repeat only affected or incomplete work. At Maximum, actively revalidate decision-critical research observations and conclusions against current sources even when they appear unchanged. Report confirmed evidence without forcing a pointless research rewrite. Planner owns substantive corrections; reviewers report them as findings.

A fresh Maximum review means doing the full required review work, not creating a fresh agent. Preserve ongoing role context and bounded handoffs where supported. Evidence reuse does not waive Maximum's comprehensive passes.

Review necessity depends on all applicable accepted evidence at the required stage, not the last override. Unchanged Maximum evidence survives Maximum → Standard → Maximum; log and checkbox-only changes do not invalidate content evidence. Compare actual assurance, reviewed scope/versions/commit, later changes, sources/assumptions and decisions. If applicability cannot be established from existing records, delegate a bounded assessment and record `review-evidence-assessed` only when it affects a gate. It cannot invent higher assurance, replace mandatory review of changed work, or grant acceptance. Stage gaps remain independent, including in-flight lower-assurance returns.

Each nonfinal phase has its own completed repair/re-review count (one at Standard, two at Maximum), separately from the final Basic one-cycle, Standard two-cycle and Maximum rigorous-loop policy. Preserve counts through replacement, interruption, override and returns to unresolved phases. Initial passes, retries and artifact checkpoints do not consume cycles. Basic needs no intermediate Reviewer assignment; higher assurance resolves the recorded stage assignment before dispatch. Only the last Coder owns final integration and all final-review repairs.

## Acceptance and useful test execution

A completed nit-only review returns `"true"` for both review roles at every assurance unless an explicit user request for follow-up remains outstanding. Orchestrator derives default nit deferral and concise known issues without a producer response, extra approval or cleanup deadline. Acceptance ends the loop; do not start a polishing cycle, rerun tests or ask for extra cycles solely for nits.

An actual user decision to fix a nit uses `review-findings-dispositioned` and the existing changes-requested, repair and follow-up review path. Preserve its recorded authority until the work is resolved or the user changes that decision; a producer's matching response does not replace it with policy authority. Explicit clarification or reconsideration also remains outstanding until addressed. The finding remains a nit, and existing repair allowances still apply. A proposed or policy-only response does not create this exception.

Unresolved must-fix needs actual user disposition. Basic weighs should-fix benefit against the entire follow-up cost; Standard normally repairs it, with concrete exceptional grounds for deferral; Maximum retains rigorous repair and risk/scope justification. A disposition without authority is a proposal. Policy cannot override a user's contrary direction. Incomplete required review/evidence, tasks or checks still block acceptance.

For Basic and Standard, use targeted Red/Green checks and broader checks at meaningful integration/final boundaries. Reuse fresh applicable results after checking relevant source/assumption changes. Checkbox accounting, reporting corrections and unrelated documentation do not alone invalidate them. Reviewer independently evaluates code and meaningful assertions and reruns checks where useful. Maximum performs comprehensive fresh review checks and active revalidation from `maximum-assurance.md`.

## Task execution boundaries at every level

- Scaffolding may create stubs, files, signatures, dependencies or structure. It cannot change existing behavior, parameters or API contracts.
- Red changes tests and necessary test support only. Confirm failure for the intended reason. Property/parameter wiring requires its behavioral integration witness.
- Green changes minimum production implementation plus its owning source/API documentation. Run the preceding Red tests and confirm green. Return test changes to the owning Red work.
- Refactor changes production structure only, preserves green behavior, and does not edit tests.
- Optional EdgeCase-Red/Green hardens existing behavior. If the witness is already green, EdgeCase-Green is a no-op; add no new feature.
- Documentation tasks identify concrete documentation targets and change documentation only unless explicitly scoped otherwise.
- Final Test-Maintenance precedes Verification. Planner specifies tests to keep, merge, remove, rewrite or strengthen; Coder executes that strategy. An explicit no-change disposition is valid; do not invent cleanup.
- Verification runs checks and reports evidence without repairs. Return failures to their owning task category.
