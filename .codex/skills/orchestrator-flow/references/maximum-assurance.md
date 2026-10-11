# Maximum assurance checklists

Read when the applicable review stage requires Maximum. Apply these complete checks on every required pass; retain role context where supported. Finding priority still follows demonstrated behavior and actual consequences under `assurance.md`. Cosmetic wording preferences do not become blockers, and nits alone never cause a repair-only cycle. Honor explicit user repair decisions through the existing path described in `assurance.md`.

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
8. Check design architecture, interfaces, invariants, data models, tradeoffs, rationale, useful diagrams where they clarify the design, error handling and testing strategy. Verify every property/parameter and downstream optional-value consumer, rather than checking only the first fallback.
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
10. Check project-owned comment guidance: comments should explain intent and rationale rather than narrate mechanical steps or introduce workflow metadata into product source. Classify actual practical consequences; do not automatically promote wording, verbosity or cosmetic process references into must-fix or should-fix.
