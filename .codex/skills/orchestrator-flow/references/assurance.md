# Assurance, evidence and finding policy

Use one accepted feature assurance level independently of per-role capability. All levels retain Planner, Architect, Coder, Reviewer, requirements/design/tasks, their approval gates, and the task execution structure. Each level includes an initial review of the complete relevant spec and complete relevant implementation. Lower assurance changes scrutiny and obligations, not coverage to a convenient subset.

The exceptional phase policy in `workflow-protocol.md` sets review-stage rigor without changing feature assurance: no intermediate review at Basic, Basic at Standard, Standard at Maximum. Architect and the final whole-feature review retain the full feature assurance. Initial coverage means the entire applicable stage and dependencies, with complete current spec bodies; future-phase implementation is not an omission. Intermediate readiness does not grant final acceptance or waive a condition under final assurance. Preserve explicit user dispositions and their revisit conditions.

## Classification before remediation

Every finding describes the factual behavior, triggering conditions and practical consequences for the actual project. Distinguish a demonstrated correctness problem, a hardening opportunity, and a preference. Classify against the feature's agreed acceptance standard without hiding facts. Consider exposure, affected users, likelihood, reversibility, recovery cost and user preference.

A private local bot and a consequential production deployment can warrant different completion priorities for the same factual concern. For example, an optional automatic retry mechanism may be an accepted limitation or nit when manual retry is adequate, but a should-fix concern when unattended recovery is an agreed operational requirement. A demonstrated violation of an approved requirement remains a defect; describing it accurately and obtaining any explicit exception is mandatory.

| Dimension | Basic | Standard | Maximum |
| --- | --- | --- | --- |
| Initial coverage | Complete relevant work, emphasizing intended use and consequential failures | Complete work with meaningful robustness/regression evidence | Complete exhaustive, adversarial review |
| Follow-up | Focused repair verification, expanding when evidence/consequences warrant | Impact-based focused, affected or full review | Fresh comprehensive re-review on each required pass |
| Should-fix | Weigh practical benefit, likelihood, consequence and total workflow cost | Stronger presumption toward fixing | Fix unless concretely risky/scope-expanding; justify deferral |
| Nit | Adequacy can justify leaving it; ease alone is insufficient | Proportionate response; record why retained improvements are not worthwhile | Fix straightforward nits; concrete risk/scope justification for deferral |
| More repair cycles | User decision before cycle 2 | User decision before cycle 3 | Existing rigorous loop and stalled-loop safeguards |
| Research continuity | Check relevant sources/assumptions; reuse valid evidence; repeat affected/incomplete work | Same rule | Actively revalidate decision-critical observations and conclusions even when sources appear unchanged |

`must_fix` blocks acceptance unless the user explicitly dispositions it under policy with rationale. Orchestrator never waives it independently. Keep the factual finding in history. At Maximum, time/priority alone is not a justified deferral. At lower assurance, a possible improvement is not automatically a completion requirement. Lower-level producers may record that the current result is adequate rather than fix every easy nit.

Behavioral repairs should first reproduce a meaningful failing witness where practical, then verify the repair at the applicable assurance. Do not restart a full lower-assurance audit solely because a narrower witness or documentation improvement was made. Do not reopen a settled disposition without new evidence, changed behavior or its relevant revisit condition.

## Review scope and limits

Record `repair_class`, `changed_surfaces`, `review_scope` and `scope_reason` in every follow-up. Standard normally uses:

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

## Maximum specification review obligations

On each required Architect pass, execute the complete current-body review and source checks, not just delta verification:

1. Read requirements, design and tasks completely, excluding routine Revision History retrieval. Check original intent plus all governing changes. Verify every required behavior, scope constraint, user story and acceptance criterion, with deterministic EARS wording for committed behavior.
   Requirements stay at the product/user-behavior level; design owns implementation details. A MAY/SHOULD criterion for behavior the design/tasks commit to implementing, or a task permitting multiple incompatible expected results, is must-fix at Maximum.
2. Verify every named existing component, function, property/parameter, type, signature and API against actual source. Distinguish proposed new entities from claims about existing ones. Verify behavior, not merely entity existence; never trust spec descriptions as ground truth.
3. Cross-check every requirement against design and covering tasks. New API surfaces and side effects need requirements authorization. Preserve existing usage paths. Missing criterion/task traceability and nonexistent required interfaces are must-fix.
4. Trace forward dependencies for every changed requirement: shared assumptions in other requirements, implementing design sections, covering tasks/assertions, and distinct behavioral branches. A new branch needs explicit acceptance criteria, design and non-EdgeCase Red/Green tasks.
5. Read referenced tests, mocks and assertions to establish that the proposed evidence can actually verify the claim. External rendering/accessibility/third-party behavior needs an executable test or concrete manual-test steps; narrow untestable assertions with user direction.
6. Trace each state setter/clearer through success, interruption, abort and partial completion. Check cleanup and stale-state effects across mode changes, failure/error handling, observability, security, performance, maintainability, and relevant UX/accessibility.
7. Analyze every formula/derived value at reachable minimum/maximum and degenerate inputs, including zero, negative, empty, optional, overflow and extreme lengths. Missing reachable boundary behavior is normally should-fix under Maximum.
8. Check design architecture, interfaces, invariants, data models, tradeoffs, rationale, diagram, error handling and testing strategy. Verify every property/parameter and downstream optional-value consumer, rather than checking only the first fallback.
9. Enforce actionable tasks, concrete test ownership/targets, sequential whole-number task IDs, valid task-to-task references, requirement mappings and the coverage table. Stale task references are normally should-fix. Do not accept vague instructions that force Coder to rediscover foreseeable design.
10. Verify scaffolding changes no existing behavior/API; one Red/Green pair per logical behavioral step; wiring/property passing has a Red integration witness; no consecutive independent Red-only or Green-only tasks. EdgeCase work hardens already-implemented behavior and cannot cover a new requirement without explicit justified classification.
11. Verify test and documentation/manual-test obligations, source/API documentation ownership, explicit final Test-Maintenance dispositions, and final Verification. Check the document versions, final Revision History placement and current approval bases through the log.
   Destructive history edits or rewriting completed tasks to misrepresent previous work are must-fix; preserve completed work and add follow-up tasks.

Keep adversarial scrutiny after repeated rejected reviews; familiarity is not proof of correctness. Verify resolved findings and the rest of the complete relevant spec afresh while honoring already settled dispositions.

## Maximum implementation review obligations

On each required Reviewer pass:

1. Read all three current spec bodies. Review the complete resulting implementation against the explicit feature baseline, reconciling changed/new/deleted file lists with Git. Missing material scope is must-fix.
2. Trace every acceptance criterion to its actual implementation path and meaningful test assertion. Framework/default behavior relied upon must be documented and tested. Missing traceability is must-fix.
3. Verify mocks/stubs/fakes exercise the behavior rather than bypass it, and assertions have one deterministic expected outcome. False positives and assertions permitting mutually different outcomes are must-fix.
4. Check design fidelity, including interface/field/parameter names, signatures, types, architectural boundaries and required approaches. Unjustified contract mismatch is must-fix; functionally correct but unjustified approach divergence is should-fix.
5. Trace interruption, abort, partial completion, error/cleanup, state transition and optional/null/empty-value propagation through every downstream consumer. Missing required cleanup or unsafe optional-value propagation is must-fix.
6. Verify preservation in pre-existing usage paths. Inspect/run relevant existing tests; changes beyond setup/import adjustments need requirements authority when behavior changes.
7. Verify test organization, double configuration and assertion targets match approved tasks. Examine every calculation at reachable boundaries/degenerate values, including specified clamps/fallbacks. Missing reachable boundary policy is normally should-fix.
8. Verify every required implementation/test/documentation/manual-test task is complete or explicitly dispositioned in the approved scope. Checkbox ordering is not completion evidence. Incomplete obligations and failed required checks block acceptance absent explicit valid user disposition.
9. Run applicable unit/integration tests, lint, type checks and builds; accurately report results and coverage gaps, including checks not run. Evaluate security, performance, error handling, observability, readability, maintainability and relevant accessibility/UX against the actual project.
10. Enforce shared comment policy: explain intent/rationale rather than narrating mechanical steps. Product source comments must not refer to workflow phases, task numbers, requirements or acceptance-criterion identifiers. At Maximum, process metadata or line-by-line narration is must-fix; redundant verbosity is should-fix, and useful wording refinements are nits.

## Task execution boundaries at every level

- Scaffolding may create stubs, files, signatures, dependencies or structure. It cannot change existing behavior, parameters or API contracts.
- Red changes tests and necessary test support only. Confirm failure for the intended reason. Property/parameter wiring requires its behavioral integration witness.
- Green changes minimum production implementation plus its owning source/API documentation. Run the preceding Red tests and confirm green. Return test changes to the owning Red work.
- Refactor changes production structure only, preserves green behavior, and does not edit tests.
- Optional EdgeCase-Red/Green hardens existing behavior. If the witness is already green, EdgeCase-Green is a no-op; add no new feature.
- Documentation tasks identify concrete documentation targets and change documentation only unless explicitly scoped otherwise.
- Final Test-Maintenance precedes Verification. Planner specifies tests to keep, merge, remove, rewrite or strengthen; Coder executes that strategy. An explicit no-change disposition is valid; do not invent cleanup.
- Verification runs checks and reports evidence without repairs. Return failures to their owning task category.
