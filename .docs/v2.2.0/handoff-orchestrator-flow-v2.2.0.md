# Handoff: Orchestrator Flow v2.2.0

Start planning the next release here, provisionally as v2.2.0. The original six improvement areas, the **seventh Autonomy candidate added November 21, 2026**, the **new prospective task-reordering candidate added November 23**, and the **released v2.1.3 baseline** are described in the dated updates below. If the chosen authoritative schema or workflow semantics are incompatible, consider v3.0.0 during proposal design. A major version is not justified solely by the number or size of changes.

This file preserves why v2 exists, the settled workflow baseline, Claude Code integration, implementation boundaries, and the v2.1.0 candidate findings. The dated updates carry the context through v2.1.1, v2.1.2 and v2.1.3 and record subsequent user decisions; the older candidate/test-kit/platform sections remain useful historical reference, not automatically selected scope. The [v2.1.0 native-test summary](../v2.1.0/native-test-summary.md) contains historical native-test evidence.

## Start here

- **State:** Latest released baseline **v2.1.3** on `main`, annotated tag `v2.1.3`, squash commit [`038f5eb`](https://github.com/namitkaura/orchestrator-flow/commit/038f5ebfea56cc4ce7ac3a6b13ba16b4d455a022). `v2.2.0-workflow-clarity-and-flexibility` is the planning/integration branch; continue from the latest released baseline. Branch/release naming is provisional pending design.

- **Reading:** this file is the only required reading to seed a new v2.2.0 planning thread; read the complete handoff first and open linked files only as needed. [AGENTS.md](../../AGENTS.md), which holds the maintenance rules, loads automatically in Codex and Claude Code sessions in this checkout. Everything else is for when a topic needs it: the source map at the end points to the contracts, scripts and history. The proposals, the v2.1.0 handoff and the native-test summary hold rationale, history and evidence; what they settled is summarized here.
- **Status of the items:** The original six areas remain numbered for planning history, but **item 3's general external Git-commit reconciliation shipped in v2.1.3** and must not be implemented again. The distinct, still-needed user-originated **workflow re-entry** belongs under item 2. Items 1, 2, 4, 5 and 6 remain for focused proposals, not authorized implementation. **Autonomy (item 7)** remains a candidate whose v2.2.0 versus separate-release placement is undecided. **Prospective task reordering (item 8, added November 23)** is a newly recorded future candidate, also not yet assigned to a release. Preserve unaffected v2 through **v2.1.3** behavior. This handoff is the context seed; proposals become authoritative once written.

## Planning observation — November 24, 2026: Standard assurance with autonomous, targeted correction

**Status:** User-reported operational observation from ongoing `music-analyzer` **F01 Stage A3**, not a new numbered improvement, an independently measured comparison, a change to the released v2.1.3 approval contracts, or authorization to edit/interfere with the active consumer project. It supports assessing existing **Autonomy (7)** and **implementation readiness / Planner–Coder ownership (5–6)** during proposal design.

**Configuration and delegation:** The user expressly allowed this F01 Orchestrator run to advance autonomously through Planner specification work, intermediate approvals and Architect reviews while using **Standard Assurance**. Planner and Architect used **Astra Max**, Coder **Sol High**. This was a user-authorized workflow-specific arrangement, **not** evidence that the proposed Guided/Delegated/Proactive approval semantics have shipped generally; any future generalization must represent approval/delegation provenance truthfully, not fabricate direct user approvals.

**What the user observed:** During actual implementation, Coder identified genuine specification omissions, including a consequential **data-model issue concerning multiple treatments of the same historical audio fixture**. Instead of making an unauthorized design choice or stopping for another user answer, Orchestrator coordinated **targeted Planner corrections → independent Architect re-reviews → Coder continuation**, preserving completed work. Implementation exposed concrete data/interface constraints that had not been fully resolved by upfront planning/review. This example is evidence that autonomous feedback and targeted revisions can work; it does not establish that the original omissions were harmless or that review could be skipped.

**Working hypothesis, not established outcome:** Upfront Maximum reviews and repeated user gates can incur meaningful token cost and hours of idle time without guaranteeing discovery of every implementation-facing omission. Some issues may only become clear when real code and data interact. A bounded Standard-Assurance process with strong role ownership, specific corrections and independent re-review **may** achieve better end-to-end efficiency than exhaustive upfront cycles. The user also suspects distinct model families might reduce correlated blind spots, **but this case cannot establish that**. Actual token savings, elapsed time, defect rates and cross-model benefit were **not measured**, so avoid numerical or causal claims.

**Design implication:** Preserve substantive upfront Planner contracts and Architect scrutiny proportional to Assurance, but do **not** pursue flawless specifications through open-ended polishing before Coder can begin. Treat implementation as an additional source of evidence: when a material gap emerges, return the consequential decision to Planner, review its affected changes independently through Architect, preserve valid completed work, then let Coder resume without repeated user intervention *where authority permits*. Neither Coder nor Orchestrator should silently invent product/scientific semantics; human-reserved decisions, new budgets/access, explicit restrictions and essential scientific validity remain boundaries. Reduce unnecessary **process** checks and broad re-review loops, **not** sound scientific validation, actual-code review, essential tests or genuine approval provenance.

**Principle:** *Perfection is the enemy of good when pursuing it creates expensive review cycles that may miss issues anyway.* The target is a **reliable autonomous feedback loop** that discovers and corrects consequential defects while minimizing avoidable reviews, tokens, rework and human attention. Use this as qualitative evidence when designing Autonomy and readiness/ownership proposals, **not as a request for extra review gates or to weaken Assurance**.

**Follow-up: why this needs to be codified (November 24):** The user clarified that this F01 behavior was achieved by **explicitly prompting the existing Orchestrator to proceed without the usual user approval gates**. It was a deliberate one-off delegation, **not a native Autonomy feature**. Needing such an intervention is itself a product-design gap: the desired bounded autonomous Planner → Architect → Coder → Planner/Architect correction → Coder feedback loop should be available as an intentional workflow policy, rather than an improvised exception that must be explained each time.

**Updated working direction for improvement 7 (November 24):** Make approval delegation and in-scope corrective specification revisions a **first-class, honestly recorded** consequence of Autonomy, without pretending the user personally approved artifacts they did not inspect. **The user agrees that Delegated (the proposed default) should ordinarily permit targeted Planner correction and independent Architect re-review of consequential specification omissions discovered *after coding authorization*, followed by Coder resumption, without reopening the consolidated user specification gate** when the correction remains within the user's accepted objective, scope, constraints and delegated decision authority. Proactive should permit this too. A change to agreed product objectives, a genuinely reserved scientific/method decision, explicit recovery prohibition, additional budget/access, evidence-integrity issue or other nondelegated authority still requires actual user direction; a material approved-contract change must not be relabeled a minor repair just to avoid a gate. Implement truthful transitions for both feature-start Autonomy and an *explicit, limited mid-feature delegation*, not a silent default change for active features. Retain independent Architect/Reviewer scrutiny according to Assurance, proportionate re-review of affected work, valid completed evidence and original resource limits. Exact schema, authority boundaries and compatibility remain proposal-design questions. Prefer ordinary roles/transitions over an ad hoc bypass command, another settings axis or added approval bureaucracy.

**Actual F01 delegation prompt, supplied November 24 as historical evidence:** The user provided the instruction they had given the existing Orchestrator while already on branch `f01-trustworthy-temporal-measurements`. It independently authorized **three exact external commits**—A3 research report `8690e5c7bfb3b94e797226f6e9a74e8e24cf1545`, research-link correction `7dc2d96d1ec8ff453713752aceded8b9eda59eb4`, and A3 follow-up proposal `185c07233d06d76c9057f8e8646931086939d7ab`—and identified `music-analysis-research/.docs/specs/f01-trustworthy-temporal-measurements/proposal-f01-trustworthy-temporal-measurements-followup-2.md` as the **authoritative scope-change input**. External Git reconciliation here is separate from granting any specification or coding approval; it was already shipped in v2.1.3.

The operative gate language was **“I explicitly preapprove all intermediate specification approval gates, provided the documents faithfully implement the proposal”** and **“Once the specifications have passed independent Architect review, stop at the coding authorization gate and present the final approved plan for my review.”** The request explicitly covered Requirements, Design, Tasks, Manual Test Plan and genuine independent Architect review, including autonomous Planner repair and necessary repeat Architect review. It explicitly **forbade coding or experiments until further user authorization**, and permitted early interruption only for a real blocker or consequential decision beyond proposal scope. Thus this was **conditional delegation of intermediate *planning* approvals, not unconditional approval of whatever Planner wrote, not an Architect-review bypass, and not authorization to implement**. In particular, the text itself did **not** grant unlimited post-coding specification changes or retries; those need valid feature authority separately.

**Design/acceptance-test distinction:** This real prompt demonstrates why a native **Delegated planning mode** should require no hand-crafted "preapprove every intermediate gate" instructions: conduct Planner work and independent Architect review, then pause for the user's **single consolidated specification/coding authorization**, before any implementation. A separately authorized mid-feature override can be bounded to planning or other phases, and should retain its exact scope. Distinguish (1) the user's grant of permission to proceed, (2) actual Planner artifact/version decisions, (3) independent Architect acceptance, and (4) the user's later coding authorization, without fictionally attributing each unseen intermediate draft approval to the user. Once coding *is* authorized, the working Delegated rule above supplies the normal targeted repair loop for in-scope omissions, not a fresh approval requirement for every correction. Testing should verify these boundaries and interruption/resumption honestly, without reusing the historical F01 prompt as new consumer authorization.

## Planning update — November 23, 2026: task ordering during specification revisions

**Status:** New future improvement candidate, numbered **8** for planning continuity after the six original areas and Autonomy (7). Its inclusion in v2.2.0 versus a subsequent release is **not decided**. This records a desired workflow behavior, **not** implementation authorization or a request to modify or interrupt the running `music-analyzer` F01 feature. Earlier dated seven-candidate inventories remain historical snapshots, not a limit on new candidates.

**Governing rule: Completed work is immutable; unfinished work can be reorganized to accommodate changed requirements.** When Planner revises `tasks.md` after a specification change, it must preserve **every completed task exactly as completed**, including its task ID, definition, checkbox/completion state and attributable history. **New and unfinished tasks** are still a prospective execution plan: insert, reorder and renumber them as necessary into the correct dependency and stage order instead of blindly appending new work after unrelated unfinished tasks. A task being assigned or partially attempted does not make it completed; nevertheless its actual partial work and evidence must be preserved and reconciled.

**F01 motivating example:** Tasks **1–68** were completed and should remain unchanged. Existing **69–74** were unfinished Stage B tasks. A revised specification introduced **Stage A3**, which must execute *before* Stage B. The Planner placed A3 at **75–119** after the unfinished Stage B tasks. The desired sequence instead keeps **1–68** intact, places the 45 A3 tasks at **69–113**, and renumbers the six prospective Stage B tasks to **114–119**. These numbers illustrate the intended planning behavior; they are **not** instructions to renumber the active F01 files now.

**Required consistent revision:** Planner updates every affected **prospective** task dependency, forward cross-reference, requirement/acceptance-criterion coverage mapping, stage ordering, task grouping, and relevant current design/documentation and manual-test procedures. Preserve clear authoritative ownership of design contracts, task-local instructions and manual procedures (items 5 and 6). Do not alter completed task definitions merely to make their old references cosmetically current. Maintain specification content versions, genuine revision history and required affected approvals; do not manufacture new completion evidence.

**Historical evidence must remain true:** Do not rewrite prior `task_log.json` events, historical task IDs, completed-task references, checkpoints, published artifacts or valid results. Prior references to *then-unfinished* task numbers must remain interpretable in the context of the specification version under which they were recorded. If numbering is reused across revisions, the workflow needs a minimal, reliable way to relate the previous and current **unfinished-task identities** during recovery and review, without pretending historic evidence referred to different work or introducing a speculative task-identity database.

**When implementation is underway:** Orchestrator and Coder must recognize the revised approved plan and associate any **partially performed unfinished work**, tests, findings and native Coder handoffs with the correct current tasks. Do not silently discard work, repeat valid completed work, duplicate completion, overwrite artifacts or make an out-of-date assignment appear current. Route substantive specification changes through the earliest affected Planner/Architect approvals; mechanical renumbering should not itself create gratuitous user interruptions or new approval ceremonies. Where an in-flight task's meaning or state cannot safely be reconciled, surface the real ambiguity before continuing dependent work.

**Design and verification follow-up:** During proposal design, inspect the actual v2.1.3 Planner/Orchestrator/Coder instructions, task reader, validator, reducer, handoff and resume assumptions before selecting the smallest consistent change. Test insert/reorder/renumber both before coding and amid partial coding, preserve completed task content and historical log validity, and verify correct dependencies/coverage/manual references, honest handoff/recovery and Codex/Claude behavior. Avoid a new ledger, redundant approval system or full Markdown semantic parser unless a concrete failure shows one is needed. This improvement complements **item 2** (truthful re-entry) and **items 5–6** (executable task plans and Planner ownership) but is a distinct task-order/state-continuity requirement.

## Latest released baseline and planning direction — November 21, 2026 (v2.1.3)

This update supersedes older statements describing v2.1.2 as the latest release or item 3 as unsolved. Preserve older dated discussions below as history, not new implementation tasks.

- **Released:** The `v2.1.3-authorized-external-commit-reconciliation` branch was squash-merged into `main` as [`038f5ebfea56cc4ce7ac3a6b13ba16b4d455a022`](https://github.com/namitkaura/orchestrator-flow/commit/038f5ebfea56cc4ce7ac3a6b13ba16b4d455a022), whose parent is released v2.1.2 `79af96c`. The annotated `v2.1.3` tag resolves to that commit. The release tree matches the original development head; canonical `VERSION` is `2.1.3`. See the completed [v2.1.3 proposal](../v2.1.3/proposal-v2.1.3-authorized-external-commit-reconciliation.md).
- **F01 origin:** A ChatGPT planning conversation reached its length limit. The user authorized a second continuity handoff, committed externally at [`6f82e6b7a3d9db5b8ebdd63f9357aba1ef43adb4`](https://github.com/namitkaura/music-analyzer/commit/6f82e6b7a3d9db5b8ebdd63f9357aba1ef43adb4), adding `.docs/handoffs/music-analyzer-continuity-002.md` in the **repository-wide** handoff directory, not the nested F01 specification folder. Its sole parent was the published event-94 workflow checkpoint. v2.1.2 allowed only added feature-local proposal/bug-report documents, so a legitimate user authorization passed event-schema checks but was still rejected by workspace/checkpoint validation. The Music Analyzer Orchestrator correctly paused instead of bypassing integrity checks.
- **What v2.1.3 actually ships:** The general `accept-external-commit` operation uses existing `user-authorization-recorded` events with an exact, user-approved full Git SHA, unchanged stage and original Git history. It checks first-parent ancestry, a single parent and the entire changed-file inventory; supports ordinary regular-file additions, edits, deletions, renames as Git changes, mode changes, mixed documents/code/tests and binaries. Git object identity fixes the actual contents; **do not perform forensic blob inspection unless a real authorization ambiguity warrants it**. Existing log paths, genuine checkpoint identification, published acknowledgment-before-dependent-producer ordering and remote delivery/recovery rules are retained. The narrower `accept-spec-input-commit` retains its v2.1.2 meaning; neither grant is specification approval, a fictional agent return or scientific/budget authority. The shared Codex and Claude runtime copies remain identical.
- **Live verification:** The F01 Orchestrator reports **event 95** records the exact user grant. Git verifies that the normal published acknowledgment checkpoint [`d7f54d2feb5e779fa0aab6efbfebfec0c7c97b0c`](https://github.com/namitkaura/music-analyzer/commit/d7f54d2feb5e779fa0aab6efbfebfec0c7c97b0c) directly follows the original external continuity commit and changes only F01's authoritative `task_log.json`. The user reports that subsequent workspace validation passed and the continuity commit was preserved. **The separate F01 scientific/budget blocker remains separate**; commit acknowledgment never authorized extra experimental work.
- **Test evidence:** the release commit reports 18 focused reconciliation tests passed and a Windows 192-test run with 189 passing methods; seven failure reports were attributable to three previously known Claude POSIX-executable startup-fixture methods. Do not represent this as an unconditional clean full suite. The skill has no CI pipeline; adding one isn't required. The actual F01 recovery is the specific end-to-end acceptance evidence.
- **v2.2.0 impact:** General Git reconciliation is now **done**. Do not add another document-type exception, redo the generalized authorization system, or build speculative content provenance/stale-review checks. The remaining user-originated code/test or bug-finding case concerns **truthful workflow-stage re-entry** into native Planner/Coder/Reviewer and belongs with item 2.

**Overriding design principle, clarified after F01:** **Verify and validate the actual work, not procedural compliance for its own sake.** The workflow itself must not become the bottleneck. The event log has **exactly two fundamental purposes**: (1) provide sufficient reliable state to **resume correctly after context loss/interruption** (completed work, genuine approvals, remaining tasks, resources, blockers, next action), and (2) give the user a **meaningful, human-readable audit log** of what happened and why. Full native agent outputs help those two aims; they are not a third independent administrative goal. **Simplify or remove any event/checkpoint/process validation without material benefit to resumption or audit.** Resolve safe bookkeeping discrepancies autonomously. Stop for real work failures, essential user-reserved science/scope/resource choices or genuinely unrecoverable uncertainty, not mechanical ceremony. This does **not** weaken rigorous actual Planner/Architect/Coder/Reviewer work, tests or scientific evidence. Treat simplification as a cross-cutting design criterion, not an eighth mandatory subsystem.

**How future planning works:** This handoff is a **self-contained continuity/context document**, not a permanently maintained release tracker. Develop focused proposals directly under `.docs/v2.2.0/` (no `proposals/` subfolder), and let completed proposals become authoritative. Earlier consideration of roughly five groupings for six improvements must be revisited now that item 3 shipped. Readiness (5) and Planner/Coder ownership (6) can share a proposal while preserving both concerns. Autonomy remains a separate release-scope decision. Orchestrator Flow itself is developed using direct Codex/Claude implementation and ChatGPT review, **not by running Orchestrator Flow on itself**. Direct GitHub connector edits suffice for ordinary documents; don't needlessly delegate to an expensive model. Use `v2.2.0-workflow-clarity-and-flexibility` as the integration branch, optional focused development branches, squash merges to integration and eventually to `main` with a tag. Keep useful old branch history; rebase integration after independent patches on `main`. No implementation or final merge is authorized by this handoff.

## New planning rationale — stronger frontier models and scarce user attention (November 21, 2026)

This records additional discussion **after the v2.1.3 release and the earlier Autonomy design**. A replacement planning thread should treat it as the user's **overriding optimization goal**, not as a newly authorized implementation, a new eighth improvement, or a claim about behavior already shipped in v2.1.3.

### Models and initial workflow assumptions have changed

Orchestrator Flow was first designed roughly a year before this conversation, using much older models. At that time, relatively unreliable planning, uncertain recovery, missed implementation details and weak judgment made many explicit approval steps, rigid transitions and mechanical safety checks seem worthwhile. **The user now has substantially greater trust in current frontier-model results than even six months ago**, let alone at the workflow's inception. This is a user observation and change in working assumptions, **not a claim that any model is infallible**.

Modern agents can better plan from rich proposals, reason through consequential choices, investigate ambiguous evidence, fix routine bugs, seek independent review and reconstruct the current state from a readable, meaningful history. **An old control designed to compensate for weak models can now actively prevent stronger models from using their capabilities.** When considering each legacy event, validation or user gate, ask: *Would we design this constraint today, for the user's actual projects and current model capabilities?* Do not preserve it solely because it existed in older versions.

This does **not** invalidate the user's emphasis on substantive reviews. They may assign **Coder a weaker model than Planner or Architect**, so excellent task specification, complete design contracts and independent review of **actual implementation against the actual specification** remain vital. Never infer that code is correct just because the plan is detailed or the Coder claims compliance. Model improvements support **more autonomy in how rigorous review gets done**, not abandonment of quality, evidence or scientific validity.

### The priority is meaningful work per unit of user attention

**The central objective is to keep the user from becoming the throughput bottleneck** and enable substantially more useful work to be accomplished autonomously. The user often does not watch the Orchestrator continuously; a routine clarification or five-minute engineering fix may leave a feature idle for hours. A bit more agent execution time spent investigating, comparing options, repairing, testing or consulting another agent is usually a better tradeoff than requiring the user's immediate involvement. **Optimize for meaningful, correctly implemented and independently verified work per unit of user attention**, not minimum model runtime or maximum procedural controls.

User involvement should be **exceptional and high-value**. Ideally the user supplies a sufficiently bounded objective, works on something else, then returns to substantial completed and independently reviewed work, a clear record of what happened and only genuinely necessary decisions. An agent encountering uncertainty does **not automatically require the user to resolve it**. First investigate, obtain relevant evidence, use an appropriate helper or lead role, compare alternatives, make a justified decision **within the delegated objective and limits**, verify it, and continue.

Escalate when the user's own judgment or new authority is truly needed: substantive goals or scope outside the proposal, closely contested alternatives under **Delegated** rather than **Proactive**, explicitly reserved scientific/method-selection decisions, new external/private access, higher budgets or human effort, consequential irreversible actions, or state too uncertain to resume safely. Routine debugging, safe in-scope recovery and ordinary design choices should not become approval ceremonies. An explicit prohibition or scientific integrity constraint cannot be ignored under the banner of autonomy.

This reinforces the separately documented **Guided / Delegated (default) / Proactive** candidate in item 7: Guided for deliberate user participation; Delegated to consolidate most planning into an Architect-reviewed specification gate and final acceptance; Proactive to complete planning, implementation, independent review, verification and safe recovery with **final user acceptance as its only routine gate**, while still honoring reserved choices. These levels are **proposed**, not implemented v2.1.3 behavior, and release inclusion remains undecided.

### Verify the work; minimize workflow ceremony

The event log has **exactly two legitimate underlying purposes**: **reliable resumption after interruption/context loss** and **useful human-readable audit**. It must retain enough genuine information to know what happened, what was completed, actual approvals and constraints, unresolved issues, active ownership and next action. Original role output matters because it serves those purposes; it is not a separate justification for infinite bookkeeping.

**Rigorous verification applies to the actual work**—concrete requirements, implementation, tests, independent Architect/Reviewer evaluation and trustworthy scientific findings. **Workflow mechanics need only as much rigor as materially serves resumption and human audit**. Reconcile safely repairable bookkeeping issues rather than halting for process purity. An administrative check that consumes hours of user attention while protecting no real work, recovery or audit requirement is a design defect. Conversely, an actual failing check, unknown scientific state or user-reserved consequential decision can appropriately block dependent work.

Evaluate each proposed or existing control using three questions:

1. What **concrete, consequential risk to the actual work, safe resumption or meaningful audit** does this prevent?
2. Must it stop or involve the user, or can the agent **investigate, reconcile, repair and continue independently**?
3. Does its practical benefit justify the **complexity, time and user attention** consumed, given the risk level of these mostly personal projects and stronger models?

If not, remove or simplify the safeguard. Avoid turning this principle into an eighth subsystem, another durable checklist or an extra approval gate. Version 2.1.3 demonstrates the desired pattern: generalize an actually failing case with a small existing-mechanism extension, retain real identity and authority, and do not add speculative content-forensics, review-staleness detectors or a new provenance database.

### Specific handoff / branch continuity for a new planning thread

The handoff is intended to let the user open **a fresh ChatGPT conversation without losing the planning decisions and their rationale**. Its earlier sections already cover the seven numbered areas, v2.1.3's release and F01 proof, technical contracts, native integration boundaries and deferred work. **The next step is planning**, not more Git reconciliation or automatic implementation.

Version `v2.1.3` has been squash-merged into `main` at `038f5ebfea56cc4ce7ac3a6b13ba16b4d455a022`. The `v2.2.0-workflow-clarity-and-flexibility` integration branch was rebased onto that release; Codex's last verification confirmed all **eight development patches preserved in order** by `git range-diff`, the exact original handoff/deferred-note bytes preserved, and clean local and remote branches both at `06538a7e81220272100d1d8bcb2eb89d40e8af2c` with **0 ahead / 0 behind**. The old remote branch tip is not a second branch. A later documentation-only update advances the remote tip and needs only ordinary local synchronization—**not another rebase**.

Keep the direct-planning workflow: release proposals are placed directly under `.docs/v2.2.0/` with no extra `proposals/` subdirectory; each approved proposal, once written, becomes the authoritative plan for its area, while this handoff is only a self-contained seed. The original rough proposal grouping must be reassessed because **former item 3 shipped with v2.1.3**. The still-open topics are items **1, 2, 4, 5 and 6**, possibly combining related readiness/role-ownership work, plus **Autonomy (7)** only after a separate release-scope decision. Defer unselected Codex agent/compaction research in its existing `.docs/future-improvements/` note. Orchestrator Flow's own maintenance uses direct Codex/Claude implementation and ChatGPT/GitHub review; the workflow is **not run on its own development**. No v2.2.0 implementation, release or merge is authorized by this handoff.

## Released baseline update — November 18, 2026 (v2.1.2)

This historical update superseded v2.1.1 assumptions at the time. **The November 21 v2.1.3 update above supersedes its current-baseline and remaining-Git-work statements.** It does not authorize implementation.

- **Release:** v2.1.2 was developed from released v2.1.1 on `v2.1.2-authorized-spec-input-commits`, squash-merged into `main` and tagged `v2.1.2` at `79af96cf42cc41c67f5d11cff73a34d6456dc765`. Its completed standalone [proposal](../v2.1.2/proposal-v2.1.2-authorized-spec-input-commits.md) records the narrow design and motivation. The v2.2.0 development branch now uses v2.1.2 as its baseline.
- **Origin:** a legitimate user-authored F01 follow-up proposal was already pushed in the consumer `music-analyzer` feature branch at `49b0ea61fe07a710acb91bd081e5dcba02312abb`. Its normal, trailerless commit prevented Orchestrator Flow v2.1.1 checkpoint validation even though the Planner could identify Requirements as the correct first artifact for the revised Stage A → A2 → generated Stage B scope. The earlier `fec-bot` v2.0.1 input-documents case exposed the same class of blocker.
- **Exact patch boundary:** v2.1.2 accepts an **explicitly user-authorized, single-parent, add-only commit of regular UTF-8 `proposal-*.md` or `bugreport-*.md` files** in the active feature's effective historical spec directory. It validates the entire commit, changed modes/paths/blobs, Git ancestry, and the exact full commit ID. The grant uses the **existing** `user-authorization-recorded` event (`kind: external_operation`, `operation: accept-spec-input-commit`) with no new event, role, stage, task-log schema or wrapper. A valid input commit is acknowledged but **never masquerades as a Flow checkpoint or grants spec approval**. Its Orchestrator log acknowledgment must reach the remote before dependent Planner/Coder publication; failed/uncertain push recovery, historical relocation and existing 2.1.1 logs remain supported.
- **Evidence and limits:** the release added 15 focused regression tests and ran the Windows 189-test suite, with seven POSIX startup-fixture failures also reproduced on the pre-patch baseline; do **not** claim an unconditional clean full-suite pass. The user tried the patch against the **actual blocked F01 feature** and confirmed the workflow got past the original external-proposal-commit blocker. This confirms that specific problem was resolved; do not infer that the entire F01 revision or every possible downstream workflow action was completed.
- **Historical remaining-scope description:** code/test handoffs, user-originated Coder/Reviewer re-entry and general Git reconciliation were missing then. **v2.1.3 has since delivered Git reconciliation**. The distinct native re-entry requirement remains with item 2, while items 1, 4, 5 and 6 remain for planning.

Future planning should inspect **current released v2.1.3 source**, not reimplement the historical v2.1.1 blanket rejection or v2.1.2 narrow-only grant.

## Planning update — November 14, 2026 (released v2.1.1 baseline)

This section captures decisions and new evidence developed **after the original handoff**. It supersedes older baseline/status assumptions where they conflict; the earlier sections below remain historical context. **It is not an implementation request, an approved final schema, a license to change consumer repositories, or authorization to expand scope.**

### Released v2.1.1: nested placement and path-only relocation

- **Release:** `v2.1.1` was committed directly to `main`, tagged and pushed. Commit `589c77072235875593c0825687f80b2acec6557c`; subject `fix(orchestrator-flow): support nested feature placement and authorized relocation`; tag annotation “Orchestrator Flow v2.1.1”. The patch changed 22 files across Codex, Claude Code, docs, VERSION and tests. Copilot/Cursor remain deferred.
- **Origin and acceptance:** an “Initial extractor test” conversation in the consuming `music-analyzer` project needed its specification at `music-extractor/.docs/specs/initial-extractor-test/`. The user selected “Fix workflow support, then relocate”. Implementation/review happened in that consumer chat; changes to the Orchestrator Flow source checkout were left uncommitted until separate authority was granted. The user accepts the patch, subsequently authorized validation, commit, tag and push, and does not request reversal. No dedicated v2.1.1 development chat existed.
- **Placement:** respect an explicitly chosen feature directory; infer nested `.docs/specs/` from an unambiguous input proposal; default to repository-root `.docs/specs/{feature}/` otherwise. Resolve ambiguity before initialization, keep paths repository-root-relative, and keep `.orchestrator-flow.json` at repository root.
- **Relocation event:** `feature-relocated` records an expressly authorized *path-only* move without restarting. Preserve actual document bytes/versions, historical wrappers, approvals/producing references, effective configuration, logical assignments, state, published checkpoint identities and trailers. Separately authorized input/proposal files may move too. Orchestrator can perform the mechanical move; substantive spec contents remain Planner-owned.
- **Validation and recovery:** derive current effective paths from the relocation history but resolve historical task logs, artifacts and checkpoint trailers at their original published paths. Verify relocated file bytes against Git; reject unauthorized changes, path traversal, overlapping/historical locations, duplicates and overwritten targets. Content-preserving moves retain approvals/review evidence. Planner may acknowledge corrected paths without an invented new draft, content version, approval or checkpoint.
- **Reader fact:** a log with `feature-relocated` needs runtime v2.1.1 or newer even when top-level `workflow_version` remains 2.1.0. The user always runs the latest installed workflow; supporting old readers for this case is not a practical requirement. Relocation itself does *not* recognize externally authored code or authorize a new workflow stage.

**Validation (report accurately):** 174 tests ran on Windows with seven failure reports across three Claude startup-fixture test methods. Their POSIX shell executable fixtures produce `WinError 193` on Windows; the same failures reproduced with the previously committed, unchanged startup-test code. There were no errors/skips, and no evidence of relocation regressions. Seven relocation tests, the Claude relocation writer test, five parity/resource tests and 38 foreign-working-directory CLI cases passed. Changed Python/JSON parsing, 33 local documentation links, whitespace and four actual symlinks (`VERSION`/`templates`, Git mode `120000`) were checked. **Not an unconditional full-suite pass.** No new consumer live run was performed as part of this release; the originating extractor run separately reported successful relocation. Portability testing is not automatically added to next-release scope.

### Improvement candidates — six original areas plus Autonomy (November 21, 2026)

Keep the original numbered topics for planning history, but **item 3's core Git work shipped in v2.1.3**, with remaining native re-entry belonging to item 2. Keep items 5 and 6 distinct even if they share one proposal. Autonomy is a seventh candidate with release placement undecided. These are planning constraints, not implementation authorization.

| # | Improvement | Core requirement |
| --- | --- | --- |
| 1 | Task-log readability | Clear fields, locally meaningful content, minimal reference chasing or duplication |
| 2 | Workflow flexibility | User-provided findings or already-applied work can enter the appropriate normal stage |
| 3 | External Git reconciliation — **shipped v2.1.3** | Exact user-authorized external commits now reconcile; native workflow-stage re-entry for their contents remains item 2 |
| 4 | Orchestrator helpers | A separate economical read-only helper capability for exceptional preparation and inspection |
| 5 | Implementation readiness | Approved requirements, design, tasks and manual procedures are executable and sufficiently complete |
| 6 | Planner–Coder role boundary | Consequential planning belongs to Planner; Architect independently enforces; Coder escalates gaps |
| 7 | **Autonomy (release undecided)** | Planner judgment, ordinary engineering/recovery initiative and delegated approval gates, with Guided/Delegated/Proactive levels and Delegated default |

#### 1. Human-first `task_log.json` readability

The authoritative task log has **two fundamental purposes: reliable recovery/resumption** and **human understanding/audit**. Its contents must establish what happened, why, what's complete, what's outstanding, authorized decisions and the next action. Original meaningful native Planner/Architect/Coder/Reviewer returns support those two goals; preserving them is not a third bureaucratic purpose. This is not a provenance/transaction database. Extra event and checkpoint checks should exist only where they materially improve resumption or human audit.

The user wants **clear, self-identifying field names and information locality**, not literal restoration of pre-v2 field names. `checks`, `test_results`, `cli_runs`, `implementation_details`, `notes` and a possible `verification_results` are naming candidates, *not settled mandatory names*. Choose one authoritative home for each kind of information. Avoid storing identical test results in multiple fields or repeating the same implementation explanation across `summary`, `notes` and generic `evidence`.

- Reading **one event** in VS Code should explain its substantive action, outcome, implementation/findings, important changed files, meaningful verification and required next step without forcing the human to resolve normalized references in separate events/sections. Preserve `event_id` and historical source references for exact context, approvals, prior reviews and recovery; these links should supplement the explanation, not replace it. Do not duplicate full prior reviews in every subsequent wrapper either.
- Prefer a predictable visible structure: actual `must_fix`, `should_fix` and `nit` (singular) categories, even if empty, and clear `changed_files`/`new_files`/`deleted_files` inventories. Whether they are schema-required or agent-required remains a design decision.
- Preserve useful v2 metadata: native invocation/context, artifact versions and reference identity, actual evidence/review dispositions, task progress, cumulative Coder work, checkpoint provenance and recovery. Keep full original agent returns, not status-only placeholders or Orchestrator summaries.
- Current v2.1.3 schema (unchanged here from v2.1.1) permits `issue_details: {}` and optional changed/new/deleted inventories. Its Coder wrapper requires `summary`, `task_progress` and `checks`. Current instructions/tests deliberately omit empty optional fields. A mandatory change to old optional fields or replacing an authoritative field could therefore be a real breaking contract change.
- Do **not** create a redundant `task_log_summary.md`, duplicate archival files, helper reports or a separate machine-normalized database. Evaluate the proposed shape against actual v2.1.1 examples, not just schema validity. Pre-v2 is a *readability reference*, not a demand to return wholesale to its fields.

#### 2. Legitimate user-directed handoffs and stage re-entry

Current v2.1.3 `user-change-requested` still routes to Planner/spec revision. `coding-revision-started` expects unresolved formal Reviewer findings and `code-review-started` expects a recognized Coder handoff, so user-originated post-review activity cannot always enter the sensible stage.

- **User reports a bug after review:** a truthful user-originated findings/review-like wrapper should permit the *normal Coder* to implement a bounded correction when there is no missing/new specification decision; then the normal Reviewer assesses the actual Coder `change_wrapper`. If product requirements or architecture are changed, resume at the earliest affected Planner artifact and observe necessary approvals.
- **User/another ChatGPT already committed code:** a truthful user-originated `change_wrapper` should enter the *normal Reviewer* path, without fabricating a Coder invocation or using a disconnected standalone Reviewer. The `fec-bot` v2.0.1 two-line test correction (`ce8747fb32b8e519d8b25dd3f2a994eeb42f89c4`) instead resulted in a standalone review and pointer-only audit workaround; that is the demonstrated failure.
- **User-authored proposal or bug report:** v2.1.2's narrow spec-input grant and v2.1.3's general grant now accept authorized Git history. Neither performs Planner's substantive work or approves its contents. External changes or findings still need truthful native handoffs/reviews, not fictional Planner/Coder output.
- **Authority and continuity:** proposed user-originated events may use `actor: "User"` and `requestor: "User"`. The existing `user-change-requested` currently records `actor: "Orchestrator"` / `requestor: "User"`; don't retroactively rewrite it. Preserve actual past review wrappers, dispositions, approvals and previous Coder outputs. Follow-up Reviewer gets the actual earlier `review_wrapper` and newest `change_wrapper`, not a rewritten synopsis. Helpers may prepare truthful wrapper content but are not the substantive role.
- **Runtime impact:** new event/handoff shapes (names not decided), state transitions and recovery actions must be handled by `task_log_schema.json`, `workflow_protocol.py`, native recorders and both platforms. Codex `record-handoff` and Claude `record-return` assume a lead-owned active invocation; Claude `append-entry` currently accepts Orchestrator-created `details` events, not an embedded user-supplied wrapper. Extend narrowly, preserving normal validation, actual-agent attribution and existing approval gates.

#### 3. Authorized external Git commits — **shipped in v2.1.3**

**General external-commit reconciliation is no longer an unimplemented v2.2.0 improvement.** The exact user-authorized `accept-external-commit` operation now recognizes ordinary code, test, binary and documentation Git changes across repository paths; the legacy feature-local `accept-spec-input-commit` remains restricted. The existing workflow log/checkpoint machinery makes authorization durable, without attributing changes to a fictional agent or bypassing approval of the work. See the current release summary above and the [v2.1.3 proposal](../v2.1.3/proposal-v2.1.3-authorized-external-commit-reconciliation.md).

**Original motivating examples retained for audit:** `fec-bot` v2.0.1 included an externally authored two-line test correction (`ce8747fb32b8e519d8b25dd3f2a994eeb42f89c4`) after review and a user-authored proposal+bugreport commit (`10384738c998356d23a7345cc321d4cf34ffec41`); both needed manual reconciliation. v2.1.2 fixed only proposals and bug reports. The later F01 continuity file under repository-wide `.docs/handoffs/` exposed the narrow exception's failure and was successfully acknowledged as event 95 through v2.1.3.

**Remaining work belongs in item 2:** a user-authored code correction may still need genuine Reviewer handling; a user-reported finding may need genuine Coder repair; specification changes need Planner. **Recognizing the external Git SHA is already solved** and should not trigger another commit-provenance subsystem, file-type exception or blanket content-validation gate.

#### 4. Independently configured Orchestrator helpers

v2.1.0 introduced Claude `flow-explorer` (optional `exploration_helpers`) and `flow-runner` (`helpers`), both lead-owned; Codex still commonly uses one `helpers` setting for lead helper work. **Do not reuse those assignments** for Orchestrator's own occasional read-only preparation.

Add a separate configurable capability (working name `orchestrator_helpers`) using the same `model`/`reasoning_effort` shape, with an appropriate small Claude `flow-orchestrator-helper` and native Codex delegation. Use inexpensive user-selected models/effort (e.g. a suitable Codex Luna or Claude Haiku/Sonnet), independent of the main lead helpers. Orchestrator itself remains metadata/wrapper focused; the helper may inspect code/specs/Git and prepare a factual user handoff or reconcile external commits.

No substantive Planner/Architect/Coder/Reviewer work, no agent-generated approval, no editing/publishing, no separate wrapper file, no helper-specific persistent log event, no separate configuration for each preparation task and no elaborate per-invocation provenance machinery. Dispatch only when bounded inspection adds value, not for trivial user instructions. Resolve how missing settings behave without silently appropriating an unrelated `helpers` profile.

#### 5. Implementation readiness of approved work

A specification can have complete requirement coverage, a large task list, named file targets and Red/Green pairs yet still be **unexecutable without Coder design choices**. Planner should assess **every task and its dependencies** and all consequential manual/empirical procedures from the point of view of the *actual assigned Coder*. Resolve missing technical/data/evidence/verification/documentation policies in their correct requirements or design artifact before implementation. A detailed task referencing an incomplete design is still incomplete.

Scope-proportionate obligations include: exact externally exchanged data fields/validation/state semantics (with representative valid/invalid records when useful); deterministic fixture formulas/independent numerical expectations when scientifically consequential; stage budget accounting across commands and interruptions; CLI artifact ownership/paths and no-overwrite behavior; public/private evidence allowlists; prescriptive documentation/report structures and acceptance tests; manual annotation and human observation handoffs; and an actual final Test-Maintenance strategy, including a justified no-change outcome.

Plan maintenance **before formal acceptance testing or expensive empirical/manual evidence collection when it affects the reliability of that evidence**; exploratory tests may precede it. Final Verification remains last. Do not impose F01's scientific rigor, exhaustive report templates or file-by-file matrices on trivial features merely because a large study needed them.

**F01 example:** the `music-analyzer` feature's Tasks v1 had 37 numbered tasks, 12 Red/Green pairs, a complete requirement-coverage table, named source/tests and Manual Test Plan v1 against Requirements v2 and Design v2. A user-requested independent task-by-task review found strong core temporal, digital level, onset, chroma and scoring tasks but missing consequential choices elsewhere:

| Tasks | Unresolved Planner decision |
| --- | --- |
| 1; 2–5 | Public stubs needed for meaningful Red failures; manifest/local binding/ownership/error record structures |
| 8–9 | Discrete waveform envelopes/noise decay/normalization, deterministic sampling and independent expected references |
| 16–19; 22–25 | Serialized scoring/annotation/run/evidence records, validity/completion states, sanitized public fields, CLI input/output paths |
| 20–21; 24–25; 28–29; 33 | Cumulative stage budgets across separate processes and interruptions, frozen stage order, exhaustion and authority-reference handling |
| 26; 30; 35 | Exact README operating guide and Stage A/final empirical report structure and interpretation boundaries |
| 31–34 and manual M0–M6 | Human annotation/listening entry formats, independence, authorizations and scoring/report handoffs |
| 36; 27; 37 | Test-preservation/refactoring policy and dependency-aware ordering before formal experiments; final verification |

The corrective request was **targeted Tasks v2 and Manual Test Plan v2**, with only narrow Design v2 revisions if necessary. It was **not** a condemnation of all tasks, and Architect had not yet reviewed them; do not claim it failed to catch defects. Planner's test-maintenance strategy should name what must be preserved/revised/consolidated and why, without speculative refactoring. Coder supplies actual executed commands/results, not the plan.

**F01 follow-up — decisions resolved but placed outside their owning tasks (Tasks v2):** After the user's implementation-readiness feedback, the revised `Tasks v2` and `Manual Test Plan v2` reportedly improved the substantive contracts. However, the user's independent review found substantial **unnumbered standalone sections interspersed under `## Task List`**, making `tasks.md` a hybrid of numbered tasks, design specifications and procedures. The user requested structural cleanup **before approving tasks**, without removing the useful detail:

| Unnumbered section reported in F01 Tasks v2 | Appropriate ownership |
| --- | --- |
| Public boundary and scaffold readiness | Task 1, with precise references to the governing design |
| Contract-to-implementation map | Relevant numbered Red/Green tasks and exact design references |
| Cold-primary and reproducibility acceptance contract | Authoritative Design v6, with executable requirements referenced by owning tasks |
| Required README structure for Task 26 | Within Task 26 |
| Preservation matrix for Task 27 | Within Task 27 (Test-Maintenance) |
| Mandatory Stage A report template for Task 31 | Within Task 31, with detailed operator steps in the Manual Test Plan |
| Final report extension for Task 36 | Within Task 36 |

**Ownership and location rule:** keep `## Task List` focused on numbered, independently actionable tasks with brief natural `###`/`####` grouping headings. Instructions, acceptance expectations, documentation outlines, and preservation/disposition requirements for a task belong **inside that numbered task**, not in separate unnumbered prose with no task ID or completion accountability. Place substantial scientific algorithms, formulas, external data schemas and reproducibility policies in authoritative `design.md`; cite exact design contracts from the tasks instead of duplicating them. Put detailed manual/operator procedures in `manual-test-plan.md`; the relevant task states its prerequisites, outputs, completion evidence and precise M0–M6 references. A Coder should neither invent policy nor have to reconcile multiple competing copies.

This is **not** permission to under-specify. The user's correction preserved 37 tasks, twelve Red/Green pairs, Test-Maintenance at Task 27 before formal acceptance/experiments, all 59 acceptance-criterion mappings, the approved Requirements v3 / Design v6 scope, and the overall scientific methodology. The user specifically corrected a Task 36 enum mismatch: Design v6 family dispositions are `supported | promising_unvalidated | unsuitable | not_evaluated`. `uncertain` is a human-validation status, **not** a family disposition. This illustrates how duplicating authoritative contracts in task prose can introduce contradictions. The user requested revised `tasks.md` for approval and changes to `manual-test-plan.md` **only** if an actual reference or instruction changed; no requirements/design reopening or implementation was authorized.

**Existing validation is not semantic layout validation.** The Planner reportedly acknowledged the issue and noted that the workflow's document helper checks versions/history but not prose ownership. Source inspection of v2.1.1 `read_spec_body.py` (unchanged for this purpose in v2.1.2) confirms it checks document version/history and extracts numbered checkboxes, without verifying that substantive obligations under `## Task List` are attached to an owning task. A detached instruction can therefore escape the numbered task completion model. This should primarily be addressed through **Planner's pre-approval structural/ownership check and Architect's independent review at all assurance levels**, rather than a full prose parser, a new durable checklist, or additional unnumbered validation sections. A narrowly mechanical, low-false-positive check may be considered only if it demonstrably helps.

**Two separate F01 failure modes now inform improvements 5 and 6:** *(a) missing consequential decisions* and *(b) resolved decisions that are misplaced, orphaned or duplicated across tasks/design/manual procedures*. Readiness requires both **decision completeness and clear authoritative placement/ownership**.

**Minor F01 follow-up — references between living specification documents:** After the task-layout cleanup, the unchanged Manual Test Plan v2 still referred to “Tasks v2” even though the current task plan was Tasks v3. The user considers that **an immaterial editorial nit**, because task IDs, procedures and cross-references remained applicable; it does not justify another revision cycle or changing the F01 files solely to update a label.

For ordinary dependencies between *current* documents, Planner should use stable filenames or relative links (e.g. `requirements.md`, `design.md`, `tasks.md`, `manual-test-plan.md`) **without embedding their current content version**. This avoids unnecessary maintenance and misleading stale references after unrelated revisions. Each document still retains its own required `Content version: N` and Revision History; the task log still records exact versioned approvals and review bases. Explicit versions remain appropriate for genuinely historical comparisons, past decisions or a deliberately frozen/immutable baseline—not routine links to living specifications. Architect should distinguish a harmless stale label from a reference that actually changes meaning or points to the wrong governing artifact; do not turn incidental version-label drift into mandatory editorial repairs.

Treat this editorial-reference nit as a small **Planner/Architect instruction refinement within improvements 5 and 6**. No new schema field, cross-reference validator, approval gate or separate workstream **for that editorial nit** is needed.



#### 6. Planner–Coder ownership: prevent hidden decision delegation

**Rule:** *Coder chooses how to implement the approved design, not what that design means.*

- **Planner** owns consequential user/product, architecture, data semantics, algorithm and verification criteria, external interfaces and evidence/publication policy, documentation scope and test-maintenance decisions. Place each in requirements, design or tasks as appropriate. Ordinary private loops, helper naming, simple refactoring and equivalent local technique remain Coder discretion.
- **Architect** performs an independent **Coder-readiness/decision-completeness review at Basic, Standard and Maximum**. Don't accept a plan merely because all acceptance criteria have mapped tasks, named filenames or tests. Ask whether two competent Coders could comply while selecting materially different behavior, data contracts or verification outcomes; if so, report the missing consequential decision, impact, and earliest artifact needing revision. Also assess **artifact locality and task accountability**: design contracts belong in design, task-specific instructions inside their numbered tasks, and detailed manual procedures in the manual plan. Flag orphaned unnumbered obligations, unclear cross-references, duplicate/conflicting contracts, and important work with no owning task. These are specification defects, not optional Maximum hardening items.
- **Coder** implements approved decisions and escalates real missing consequential ones through Orchestrator for Planner resolution and necessary artifact reapproval/review. Neither high capability nor strong assumptions grant Coder authority to invent requirements, data meanings, scientific methods, publication standards or test-preservation policy.
- **No new routine subsystem:** Planner self-audits as part of its existing task preparation; Architect enforces within its ordinary review; Coder uses normal blocker/clarification routing. Do not add a standalone readiness report, additional mandatory role, extra gate, persisted checklist or schema field.

Current Codex/Claude Planner instructions already require concrete tasks and test-maintenance planning; Coder's boundary is largely clear. Architect's requirement to check “sufficient concrete tasks/tests/documentation” is too easy to satisfy superficially, and the sharpest “do not force Coder to rediscover foreseeable design” obligation appears in the **Maximum** checklist. Strengthen Planner, Architect and common assurance instructions at **all** levels; clarify Coder escalation only as needed. Item 5 asks whether work is executable; item 6 assigns responsibility for decisions and escalation, without duplicating checks.


#### 7. Autonomy — delegated judgment, gate control and engineering recovery (November 21, 2026; release undecided)

**Status:** This is the **seventh improvement candidate** specifically requested for preservation in this v2.2.0 handoff. The user **has not decided** whether it belongs in v2.2.0, a separate later minor release, or a major version if gate/approval-state changes break compatibility. Preserve its full background and decisions for later proposal design. This addition is not implementation authorization, a finalized configuration or an automatic extension of the original six-area release scope.

**Core definition:** *Autonomy determines how independently Orchestrator Flow may make decisions, solve problems, recover and advance through the workflow within authority delegated by the user.* It is a third **independent** axis, alongside:

| Setting | Governs | Question answered |
| --- | --- | --- |
| **Capability** | Per-role models and reasoning effort | How capable are the agents? |
| **Assurance** | Verification, independent review, evidence and rigor | How thoroughly must correctness be established? |
| **Autonomy** | Planning judgment, engineering/recovery initiative, escalation and approval-gate delegation | How independently should the workflow proceed? |

**Maximum Assurance + Proactive** must still conduct real, rigorous Architect and Reviewer reviews and meaningful testing; it should simply require fewer interruptions. **Basic Assurance + Guided** is also valid. Higher Autonomy must not lower Assurance, collapse role separation, allow Coder to invent missing consequential scientific/product requirements or let Orchestrator replace independent review.

##### Background: F01 and the cost of unnecessary stops

This emerged from repeated stops during \`music-analyzer\` F01. After a narrow code-identity correction, an independent source review found **no numerical method change**, and **all 216 tests across 18 modules passed**. Nine existing M0 diagnostic profiles kept their original code identities; the nine new score records correctly identified their producing code. No fixtures were regenerated and no profiles were repeated.

Then **Task 62's single authorized diagnostic job** returned \`INVALID_RECORD\` before writing its final \`diagnosis_result\`. A read-only isolated check demonstrated a likely NumPy \`float64\` versus native Python \`float\` validator defect, **but it had not established that this was the precise field that stopped the live job**, because the worker discarded the field pointer. The failed operation, partial diagnostic CSV files and earlier valid data were preserved. At the recorded stop A2 had **836,352 ms charged and 8,163,648 ms remaining**. Development had not begun; the method recommendation and actual scientific selection were still reserved for **Task 66**. The Orchestrator asked for authorization merely to diagnose and repair the serialization problem, and said the consumed diagnostic job could not be retried automatically.

The user responded with **“Standing Instruction: Implementation Defects, Recovery, and Unnecessary Pauses”**, applying to that F01 run and future Music Analyzer work and subsequently recorded as a user authorization in that consuming feature's task log. **That project's standing authorization does not automatically apply to other consumer repositories.** But the incident exposed a general Orchestrator Flow issue: the workflow was treating ordinary engineering repair and recovery as fresh user authorization decisions. The user may not be monitoring it, so a small bug can halt progress **for hours**. Such pauses cost execution time, require needless human intervention, reduce autonomy, disrupt momentum, add bureaucratic bookkeeping and incentivize procedural compliance over useful outcomes.

**The governing principle:** The workflow exists to deliver trustworthy, meaningful results—not to become a supervised sequence of small commands. A pause is justified by a **real consequential user decision, unacceptable uncertainty or work beyond granted authority**, not merely by a programming error or an overall code-hash change. Rigor and autonomy should reinforce each other.

**Important distinction:** Existing Orchestrator Flow role contracts already make *ordinary in-scope code repair* part of the Coder's job, including defects found during Verification. By contrast, **F01's approved Design and Manual Test Plan explicitly contained an unconditional one-attempt/no-recovery scientific fail-stop rule**. That restriction was intended to protect scientific integrity but accidentally conflated failed **software execution** with unfavorable but scientifically valid **measurements**. A higher Autonomy selection **cannot silently override an explicit approved project no-retry rule**. Instead, Planner should specify recovery policy carefully from the outset, Architect should independently challenge unnecessarily restrictive contracts, and any necessary policy change should follow the appropriate authority/spec revision process. The user's F01 standing instruction authorized a narrow recovery policy there; it did not authorize unlimited retries.

**Scientific repetition is different from engineering recovery.** Never repeat a valid, unfavorable observation to improve the metrics, tune thresholds after seeing holdout results, change references to fit an outcome, selectively keep favorable trials, regenerate completed fixtures or inflate budget. But an operation that fails to serialize a valid result, crashes, misclassifies report completion or maps a field incorrectly is **not automatically a completed scientific observation**. A verified repair may allow a distinct retry **when the governing recovery contract permits it**. Previous evidence retains its original source/build identity; an overall code-hash change alone does not demonstrate numerical incompatibility. Assess scientific applicability through real source review and focused regressions, without elaborate compatibility frameworks or new provenance ledgers.

The user gave a concrete eight-step normal engineering recovery expectation:

1. **Diagnose** actual failure, saved state and relevant evidence, distinguishing demonstrated cause from conjecture.
2. **Reproduce** with a deterministic isolated fixture through the **actual final validation/serialization boundary**, rather than rerunning costly science simply to debug.
3. **Correct narrowly** without altering calculations, algorithms, thresholds, frozen inputs, schema strictness, independent references or scientific methods unless separately justified.
4. **Verify rigorously** with positive and negative regressions, affected integration tests, fresh automated acceptance and genuine review of actual implementation/spec/preservation.
5. **Assess existing evidence** for applicability. Preserve prior valid results and actual code producer identities; code-hash changes alone do not invalidate them.
6. **Recover safely** if known execution state, approved recovery rules and remaining resource bounds permit it: record a separate recognizable attempt, preserve the failed one and its partial artifacts, and charge all real consumption.
7. **Continue previously authorized tasks** without asking for permission again between diagnosis, repair, verification and safe recovery.
8. **Report meaningful outcomes** and genuine remaining scientific limitations, rather than asking users to decide routine debugging details.

Never overwrite or relabel failed/completed evidence, reset cumulative resource use, create a replacement study to hide failed attempts, invent unknown costs/state, repeat successful profiles/scores unnecessarily or assume a fresh process is safe when the previous operation is left active/corrupt. Escalate when state is genuinely uncertain, evidence integrity cannot be established, tests fail, the repair changes scientific meaning, new work exceeds method/fixture/input scope, a resource cap would rise, protected private files or services need access, or the project forbids the planned retry. For **the immediate F01 case**, the user expected verification of the suspected \`diagnosis_result\` type defect, preservation of **21 generated mixes, nine original M0 profiles, nine scores, original failed diagnostic and partial CSVs**, maintenance of the **836,352 ms spent and 8,163,648 ms remaining** accounting, a new owned diagnostic attempt only if safe, and continuation through **Tasks 63–65** under the existing study scope. The next *planned* user decision remained **Task 66** for actual method choice, not another bug-fix approval.

##### Three levels: combine original recovery meaning with later gate delegation

**Both concepts must be preserved:** the initial Autonomy definitions concerned agent initiative, investigation, replanning and operational recovery. Later discussion added *user approval-gate delegation*. The latter must not replace the former. This is the current **conceptual working model**, not an approved schema.

| Level | Planner decisions | Engineering/operational initiative | Planned user gates |
| --- | --- | --- | --- |
| **Guided** | Ask about meaningful design/product alternatives with a recommendation, as the existing interactive Planner does. | Independently handle ordinary implementation and debugging. Ask before nontrivial operational recovery or new consequential decisions not clearly authorized. | **Requirements → Design → Tasks → Coding → Final Acceptance**, each requiring user approval. |
| **Delegated — DEFAULT** | Choose autonomously when the proposal/evidence makes one option reasonably clearly best; when **material options are close to similarly good**, ask with a recommendation. | Diagnose failures, repair, test, review and recover interrupted work independently **where approved recovery policy permits**; escalate actual consequential choices. | **One consolidated specification approval after Architect**, then **Final Acceptance**. |
| **Proactive** | Choose and justify the best defensible approach **even when several options are similarly good**. Resolve ordinary ambiguity and in-scope replanning through Planner/Architect; escalate decisions beyond the proposal without a justified clear path or reserved authority. | **Maximize autonomy** in diagnosis, testing, debugging, safe recovery and continuation within the delegated objectives and limits; do not default to user questions merely because several approaches work. | **Final Acceptance only**, after actual Reviewer acceptance. Intermediate requirements/design/tasks/coding user gates are delegated. |

**Guided** is *not* permission to ask before every routine programming correction or private implementation choice. It preserves the traditional early design decisions and document approvals, not micromanagement. **Delegated** permits Planner to produce **Requirements → Design → Tasks** without separate user interruptions and resolve ordinary Architect findings. Architect independently reviews the **complete specification** before the user reviews it. The user then retains a real opportunity to reject, reshape or correct the consolidated spec **before coding**; if feedback changes Requirements, revise downstream Design/Tasks and obtain appropriate renewed Architect review. Do not reopen unaffected decisions or run approval loops just for bookkeeping. The single consolidated spec gate is intentionally **after Architect**, not before.

**Proactive** means: *“Give the agents the proposal, let them plan, independently review, implement, debug and verify it, then bring me the reviewed implementation to accept.”* It can make meaningful **Planner** design decisions within delegated objectives even when there is no unique best choice. Independent Architect review must challenge them; when correction is required, Planner may revise, Architect re-review, and the workflow proceed without another routine user pause. Coder still owns implementation and ordinary defects; Planner owns consequential specifications. **Actual requirements/design/tasks, approvals/authority provenance and Reviewer acceptance still exist.** They must not be skipped merely because there is no *user* checkpoint. The sole planned user approval is the final gate before \`implementation-complete\`.

An especially important Proactive possibility: if Coder discovers a project-specific spec restriction that blocks a safe, otherwise in-scope engineering recovery, Orchestrator could route a **narrow revision through Planner and Architect** and then continue under an accurately recorded delegated decision, **only if the initial delegation actually covers changing that restriction**. Express prohibitions or a consequential new scientific decision explicitly reserved to the user may not be waived simply because Autonomy is high. Proactive is *not* “never ask.”

**Planner example:** If a proposal needs a small results store and JSON is clearly sufficient compared with SQLite or Parquet, Delegated and Proactive should select JSON without presenting a menu merely because alternatives exist. If JSON and SQLite are **materially close choices**, **Guided** asks and recommends, **Delegated** asks with a recommendation, and **Proactive** selects and documents a justified approach. There need not be a mathematically unique winner. However, missing/ambiguous *product objectives* or new scientific claims/budgets/access beyond the proposal are not minor design options: ask where the user must actually decide. Preserve Planner choices, rejected alternatives and rationale in ordinary \`design.md\`, not a new ledger.

At every level, a user-specified reserved decision (e.g., F01 **Task 66**), materially changed product objectives, new scientific methods/reference choices, unauthorized recordings or services, increased time/memory/output/human-effort budget, irreversibly uncertain state, acceptance of unresolved must-fix defects or new high-consequence external actions remain out of automatic delegated scope unless explicitly authorized. Higher Autonomy cannot turn failed experiments into favorable ones or bypass rigorous review.

##### Why Delegated is the default: actual experience and better proposals

The current five gates were originally introduced **for a sound reason**: a sparse/ambiguous user-written proposal might send Planner down the wrong path at Requirements, and the user wanted to correct that before investing in downstream Design and Tasks. But after real experience, the user observes **much fewer serious wrong-path specifications than expected**, while repeated spec approval loops and pauses create substantial overhead. **Delegated preserves a consolidated Architect-reviewed specification gate before any coding**, so the user can still demand significant specification changes without having to approve each intermediate document.

The quality of inputs has also changed. Earlier proposals were often **shorter and handwritten**; now the user frequently discusses an idea extensively with ChatGPT before supplying a **more thoroughly specified proposal**, with objectives, constraints, examples, edge cases, choices and rationale already worked out. The user wants either style of input with appropriate Autonomy: **Guided** for interactive shaping of a sparse proposal; **Delegated** for a carefully developed proposal whose complete design the user still wants to inspect; **Proactive** for a goal and bounded authority the user is comfortable delegating end-to-end. These are **natural pairings, not restrictions**. A sparse proposal can use Proactive if goals/limits are clear enough; a rich proposal can use Guided when particular design choices matter. **Never infer Autonomy from proposal length, who authored it, Capability or Assurance.**

**Explicit user choice: Delegated is the default when the user doesn't specify an Autonomy setting on a NEW feature.** Show the effective level alongside Capability and Assurance without adding a special confirmation gate for the default. **Existing in-progress features must keep their recorded approvals and authorization policy**, not silently transition because software now defaults differently; changes require specific user direction and compatible runtime transition logic.

##### One setting, truthful approvals, implementation boundaries and open decisions

The user asked whether **approval gates should be a separate setting** from problem-solving autonomy. These are conceptually different dimensions of autonomy, and combinations like Guided approval gates with Proactive debugging are legitimate possibilities. The current **working preference** is nevertheless **one three-level Autonomy setting**, coupling Planner discretion, operational initiative and gate delegation as sensible presets. Avoid proliferating independent knobs or a large gate-permutation matrix until actual experience justifies it. Preserve the possibility of narrowly reserved user decisions/gates, e.g., F01's Task 66. Do not declare a separate override mechanism already approved; it is a later design question.

**Truthful approval provenance is essential.** v2.1.2's schema/reducer currently assigns some approvals and coding authorization to the **User**. Under Delegated/Proactive, the task log must **not pretend the user personally approved documents they never saw**. Record real initial user delegation and distinguish Orchestrator advancement under that delegated authority from direct user decisions. Record exact artifact versions and review bases, genuine Planner/Architect/Coder/Reviewer outputs, actual findings/dispositions and final user acceptance. Removing a *user prompt* does not remove the stage's documents or independent reviews. This may require nontrivial changes to repository configuration, event/schema/reducer, both platform recorders and role contracts, resume/recovery and tests. The impact could be **breaking** and justify moving Autonomy to a later release or v3.0.0; do not force v2.2.0 compatibility merely to fit the version number.

**No new bureaucracy in the name of autonomy.** Reuse current roles and artifacts; do not add approval ledgers, a generalized retry manager or compatibility database, duplicate evidence documents, new routine authorization questions or an “improvement process for the process.” Even with high Autonomy, external permission, failed/uncertain Git checkpoint delivery, changed scientific methodology or material exception authority must still respect real safety/approval boundaries.

**Questions for the later proposal:** (1) Is Autonomy included in v2.2.0, a separate minor, or major? (2) How do delegated spec/coding approvals honestly appear in task-log schema, stage transitions, resume and older active logs? (3) Precisely which in-scope recoveries and spec corrections are covered without new questions, and how are project-specific no-retry contracts honored? (4) Do three presets suffice with individually reserved decisions, or is gate control truly independent after real usage? (5) How should focused, realistic Codex/Claude tests demonstrate both Planner judgment on clear versus near-tied alternatives and authentic Architect/Reviewer independence, final acceptance, repair/retry and authority boundaries, not merely passing schemas?

**Governing philosophy:** *Assurance determines how confidently the workflow establishes correctness; Autonomy determines how independently it works toward that result.* **Delegated** is the user's preferred normal balance of hands-off work and retained final-spec control. **Proactive** is maximum initiative within the proposal, preserving genuine user-reserved decisions, independent reviews, scientific integrity and final acceptance.

**Added rationale (November 21):** Greater trust in newer frontier models makes *user attention*, rather than agent execution time, the scarce resource. The goal is far more autonomously completed, genuinely verified work per unit of user involvement. Do not let older weaker-model safeguards prevent today's models from exercising responsible judgment; preserve strong actual-work review, not needless approval ceremonies. See the new planning-rationale section above. This supports the proposed Autonomy design but does not settle its release inclusion.

### Compatibility, release name and upgrade practice

**Working choice: v2.2.0 for planning, not yet a final compatibility finding.** SemVer major changes are justified by breaking published schemas or workflow semantics, not by the count of improvements. **Autonomy may change user-only approval-event semantics**, requiring its own compatibility and version assessment; do not assume it must be in v2.2.0. Additive user event types and optional helper assignments may be minor-compatible; **general external-commit recognition already shipped in v2.1.3**; replacing required `checks` or changing previously optional field requirements may be breaking. The user is not attached to pre-v2 literal names, so **first design the most understandable authoritative wrappers** and then classify the real delta. If it is incompatible, discuss v3.0.0 and rename this release folder/branch during planning rather than maintain bad fields just to retain 2.2.0.

The user is the only current consumer and always uses the latest linked installation. Workflow upgrades are normally made **between completed features**; a mid-feature patch is unusual and usually fixes a blocker (the v2.1.1 relocation fix and deliberate v2.1.2 spec-input fix are examples). Completed features' logs are retained for **human audit**, and will not be read by the workflow again in normal practice. **Active** logs require accurate state/approval/return/recovery interpretation; patch upgrades must correctly resume them. Minor upgrades are normally feature-to-feature and should retain compatible meaning as appropriate to a minor release, but no elaborate hypothetical migration system is warranted. A new major version may break active old-format compatibility; finish ongoing work first and address any rare exception explicitly. Do not rewrite completed historical logs or build a dual-format execution engine only for them. The special older-reader caveat for v2.1.1 relocation is irrelevant to the user's latest-runtime practice.

### Architecture, review and testing touchpoints

- **Shared runtime/schema (identical Codex and Claude copies):** `references/common.schema.json`, `task_log_schema.json`, four `wrappers/*.schema.json`, `scripts/workflow_protocol.py`, `workflow_artifacts.py`, `validate_orchestrator_artifacts.py` and `checkpoint_state.py`. State/replay/next-action, references and publication must agree. Keep `tests/test_runtime_parity.py` parity; no cross-platform import adapter.
- **Native contracts:** both platform-specific Planner, Architect, Coder, Orchestrator, assurance and helper instructions. The Codex handoff recorder and Claude `claude_log.py` (`record-return`, `append-entry`, actual transcript handling) need appropriate user-event support; Claude may add one read-only `flow-orchestrator-helper` agent. Do not modify deferred Copilot/Cursor integrations.
- **Focused behavior tests:** user reported post-review bug → real Coder → real Reviewer; user-supplied already-applied correction → real Reviewer; external spec document commits → Planner; unknown external commit rejected; committed historical outputs and approval continuity; interrupted/new-context resume after user events; checkpoint validation and publish after reconciled commits, including **relocation across paths** and preservation of the **v2.1.2 spec-input acceptance path**; failure/uncertain push safeguards; human readability inspection of real log events; Architect catches incomplete external data/docs/Test-Maintenance decisions **and misplaced or duplicated task/design/manual-plan instructions** at lower assurance while allowing legitimate Coder implementation discretion. Planner and Architect should accept simple grouping headings and precise references without demanding repeated contracts, new sidecar reports or a semantic Markdown validator. Add selective native Codex/Claude runs; do not treat deterministic unit tests as proof of native role behavior.
- **Not automatic scope:** old handoff candidates about Orchestrator log-entry examples, acceptEdits prompts, Claude helper transcript edge cases, Git journal optimization, native live-kit expansion, Windows fixture portability/setup, Maximum/phase coverage and future Copilot/Cursor support remain separate choices. Adopt a small related fix only by deliberate scope decision. The 2.1.1 Windows fixture failures are not a mandate to fix them here.

**Repository ownership preference:** Orchestrator Flow source maintenance should originate only from conversations in the user's **Orchestrator Flow project**, not consuming-project chats. The user explicitly opted to enforce this personally; **do not encode it in `AGENTS.md`, skills, an extra permission gate, ledger or schema** without a separate request. The v2.1.1 patch remains accepted.

**Next work, when asked:** inspect **released v2.1.3** role/log output and reduce unnecessary workflow validations using the **two log purposes**. Plan the still-open improvements: log readability, user-originated stage re-entry, optional Orchestrator helpers and Planner/Architect readiness and role ownership. **Do not reimplement general Git reconciliation.** Evaluate genuine compatibility and whether Autonomy belongs in v2.2.0 or separately. Write focused proposals; do not implement or automatically adopt deferred backlog.


## Why v2 exists

The motivating example was the user's FEC bot: a private repository, running from the user's laptop, serving roughly a dozen active users on one private Discord server. An API-provider migration worked very well, but the workflow spent approximately two and a half usage allocations hardening it. Repeated Architect and Reviewer passes kept reopening the whole specification or implementation and discovering increasingly minor improvements.

That outcome was too expensive for the project's consequences. Small, recoverable bugs would have been acceptable. The purpose of v2 was to match the cost of planning, implementation, and assurance to the work, while preserving deliberate engineering and useful recovery.

The governing instruction is **“perfection is the enemy of good.”** It applies to this workflow and its maintenance just as much as to the projects it produces. **November 21 refinement:** the event log exists for resumption and human audit, while the *actual work* deserves substantive verification. Workflow bookkeeping should be the minimum needed for those two objectives, never an end in itself.

- Optimize the ordinary successful path. Resumption is important but exceptional; extra bounded reconstruction during recovery can be preferable to permanent bookkeeping on every successful operation.
- Preserve enough information for the next agent and a future resume. A perfect process audit is not a deliverable.
- **Historical assumption:** the user may be available for unusual decisions but may also be **absent for hours** while agents wait. Do not rely on immediate user attention for routine work or build a transaction framework, watchdog, permission ledger, migration system or elaborate recovery protocol to eliminate every hypothetical question. Favor autonomous diagnosis/repair; stop for genuine decisions or unsafe state.
- Classify findings by actual project consequences and agreed assurance. Technical complexity alone does not make a private project mission-critical.
- Maximum preserves meaningful rigorous review. It does not justify useless diagrams, duplicate reports, polishing loops for nits, or administrative ceremony.
- Simpler process does not mean vague planning. The user has seen weaker Coders produce incoherent work when too much design is left implicit. Concrete requirements, design, task targets, dependencies, and test expectations remain valuable.

The user prioritizes Codex and Claude Code. GitHub Copilot and Cursor should eventually remain usable and behaviorally consistent, but their updates need their own proposal.

## Settled v2 workflow behavior

This carries forward section 3 of the v2.1.0 handoff, updated for v2.1.0. The runtime contracts and schemas remain the exact field and event definitions; do not create a second competing schema from this summary.

### Roles, ownership, and user gates

The pipeline remains **Planner → Architect → Coder → Reviewer**, coordinated by Orchestrator. Lower assurance does not bypass a lead role or a required document. Direct standalone role use remains supported with its own supplied context; it must not invent orchestrated approvals.

| Role | Responsibility |
| --- | --- |
| Orchestrator | User interaction; configuration; branch initialization; approvals and decisions; `task_log.json`; current `known-issues.md`; log checkpoints; recovery coordination. |
| Planner | Requirements, design, tasks, optional research, their artifact checkpoints, and incremental/consolidated specification handoffs. |
| Architect | Read-only specification review at the applicable assurance. |
| Coder | Intentional implementation, test, documentation, and task-checkbox edits; artifact checkpoints; cumulative implementation handoff. |
| Reviewer | Read-only implementation review at the applicable assurance. |
| Helpers | Bounded exploration/research and execution of specified checks; concise evidence returned to their owning lead. They do not intentionally edit project files or publish checkpoints. |

Orchestrator preserves its context by using structured outputs, metadata, file names/statuses, and concise mechanical diagnostics. It does not inspect specification/research bodies, product source, tests, or patches. Delegate content questions. Since v2.1.0, open questions in the input are evidence for Orchestrator's difficulty assessment, not questions for it to ask: Orchestrator never asks the user product or requirements questions itself, and Planner returns them for routing. These are consumer runtime boundaries, not restrictions on an agent maintaining this workflow repository.

Requirements must be approved before dependent design, design before dependent tasks, and tasks before Architect review. Material upstream changes require the affected approvals in that order. Unaffected documents do not need artificial revisions or repeated approvals. Architect acceptance is separate from the user's initial coding authorization; Reviewer acceptance is separate from final feature acceptance.

Questions from delegated roles pass through Orchestrator. Use real native role delegation; do not quietly simulate the roles in the Orchestrator's own context. A platform limitation needs an explicit design/user decision, not an invisible loss of separation.

### Capability and assurance are different settings

**Capability** selects model and reasoning/effort for each of Planner, Architect, Coder, Reviewer, and helpers. Since v2.1.0, the shared schema accepts an optional `exploration_helpers` assignment for exploration and research helpers, leaving `helpers` for test and check execution; Claude Code uses it, and Codex keeps one `helpers` assignment for now. Different role assignments are intentional: a stronger reviewer than producer is valid. **Assurance** selects the feature's process/review standard and is shared across the lead roles, apart from the explicitly defined intermediate phase reviews.

Consumer-root `.orchestrator-flow.json` contains `assurance_level` and `capability_defaults`, with maps for configured platforms. It does not belong in `AGENTS.md`, because those project instructions may also be used without Orchestrator Flow.

At first setup, the user and Orchestrator establish repository defaults. For each new feature, Orchestrator recommends a complete configuration and the user accepts or overrides it. The effective feature settings are recorded in `task_log.json`; later repository-default edits do not silently change an existing feature. Accepting a feature recommendation does not silently rewrite repository defaults.

Current task-log configuration fields include `workflow_version`, `assurance_level`, `capability`, and `review_disposition_policy`. Capability records the platform, resolved role assignments, and acknowledged limitations. The current schema already recognizes `codex`, `claude-code`, `github-copilot`, and `cursor`; each assignment uses `model` and `reasoning_effort`. Native inheritance and unavailable effort controls must be represented honestly using the contract's supported conventions, with user acceptance where required.

Accepted capability changes apply **prospectively** at a coherent boundary. Preserve approved work, logical assignment, cumulative reporting baseline, context where usable, and repair allowances. A model/effort change does not invalidate useful completed or in-flight work. A helper-only change affects subsequent helpers without requiring the lead to restart.

Do not restore the rejected dispatch-provenance design: no `role-dispatch-started`, execution-segment lineage, per-dispatch configuration matching, helper capability ledger, or retrospective proof of which model produced every portion of an artifact. Use real native controls and verify supported settings when selecting/using them; prompt text claiming a model is not a native model selection. Unavailable requested settings require user direction, not automatic substitution.

The user prefers cheaper suitable helpers, such as Luna in Codex, rather than routinely using Sol for them. This is a cost preference, not a fixed cross-platform model mapping. Some live tests intentionally used different assignments to verify that accepted choices stuck. Do not copy their test settings as universal runtime defaults.

### Assurance, findings, and when to stop

Initial Architect and Reviewer coverage includes the entire relevant specification/implementation at **every** assurance. Assurance changes depth, classification, evidence expectations, and follow-up scope; it does not permit conveniently omitting a file or document.

| Behavior | Basic | Standard | Maximum |
| --- | --- | --- | --- |
| Scrutiny | Intended behavior, meaningful preservation, and obvious consequential failures; recoverable limitations can be acceptable. | Stronger robustness and regression expectations, proportionate to consequences. | Comprehensive adversarial review and active revalidation of decision-critical evidence. |
| Follow-up review | Normally focused on the repair; expand when consequences/evidence warrant. | Focused, affected, or full according to repair impact. | Comprehensive on each required pass. |
| Should-fix findings | Weigh benefit, likelihood, impact, and the entire cost of another repair/review cycle. | Normally fix; defer with concrete grounds, such as disproportionate rework or risk. | Preserve rigorous repair and justified-deferral standards. |
| Nits | Normally defer and record concise known issues. | Nonblocking; do not create polishing cycles. | Still nonblocking; address straightforward nits alongside necessary repairs only. |
| Ordinary repair allowance | One completed repair/re-review cycle before further direction. | Two completed cycles before further direction. | Existing rigorous loop and stall safeguards. |

**Completed nit-only reviews accept at every assurance, including Maximum.** The factual issue may receive a different severity at different assurance levels; what remains a nit at Maximum is still nonblocking. An explicit user request to repair or reconsider one remains binding through the ordinary decision/repair path. Nits never excuse missing required work or failed required checks.

Must-fix exceptions require actual user disposition. Do not silently weaken a requirement. Preserve findings, authority, and rationale without reopening a settled decision absent new evidence or its agreed revisit condition. Initial reviews, checkpoints, and small reporting corrections are not repair cycles.

The built-in `review_disposition_policy` is `spec_user_code_auto`: user disposition before Planner repairs, ordinary in-scope Coder repairs allowed. Alternatives are `all_user` and `within_scope_auto`. This policy is an explicit feature field, not a repository-default field. All policies preserve material document approvals, user product decisions, operational authority, loop limits, and explicit final acceptance.

An assurance increase may require additional review work before the affected gate, including when a lower-assurance initial review was already running. Capability changes alone do not create that gap. Reuse sufficient applicable evidence: unchanged Maximum work remains applicable after Maximum → Standard → Maximum. Do not infer insufficiency solely from the last override or add a new full review merely because the agent context changed.

### Deliberate planning and Red/Green remain mandatory

The user explicitly rejected combining implementation and tests into loosely defined work to save planning cost. Preserve separate Red and Green stages at every assurance. Scale the depth of tests and review instead: Basic can cover intended use and obvious edge cases without exhaustively defending every remote possibility.

Requirements describe user/product behavior with deterministic acceptance criteria. Design names concrete interfaces, ownership, data flow, invariants, and relevant decisions. Tasks identify targets, dependencies, useful verification, and requirement mappings so a lower-capability Coder does not have to rediscover the design. The existing requirement-to-task coverage structure remains; do not treat the removal of pointless diagrams as permission to omit useful traceability.

Preserve the current task categories and their boundaries: behavior-free Scaffolding where needed; test-only Red; minimum production Green with source/API documentation; production-only Refactor; optional EdgeCase pairs for hardening existing behavior; concrete Documentation; explicit final Test-Maintenance; repair-free final Verification. Planner supplies the test-maintenance strategy; a justified no-change result is acceptable.

Size Red/Green pairs around coherent behavioral changes, not one pair per assertion and not one enormous pair for the whole feature. Planner uses Markdown headings for natural groups that become Coder checkpoint boundaries. A group is not an extra state, approval, phase review, or mandatory return to Orchestrator.

Coder delegates execution of applicable tests, lint/type checks, builds, and planned manual checks to helpers. It retains intentional edits, interpretation, and repairs. Exploration helpers answer bounded source questions; reuse suitable helper contexts across related work instead of spawning one per task. Keep tested work stable and return concise commands, actual outcomes, useful counts, and exact relevant failures rather than filling Coder's context with successful tool output. Basic/Standard can reuse fresh applicable results after checking relevant changes; reporting corrections and checkbox updates alone do not require retesting. Maximum preserves its comprehensive fresh-check obligations.

Diagrams are useful only when they clarify something. They are not mandatory even at Maximum.

### Documents, versions, and handoffs

Consumer feature artifacts normally live together under `.docs/specs/{feature}/`. The user's intended use places the completed proposal/bug-report input beside its task log and specifications. Repository-maintenance documents such as proposals and this handoff belong in repository-level `.docs/` folders, not artificial consumer spec folders.

- `requirements.md`, `design.md`, and `tasks.md` are required. Each has its own integer `Content version: N` from the first draft and a final top-level `## Revision History` with useful changes and rationale.
- Do not put workflow state, approval metadata, branch names, or Git hashes into those specification documents. The task log and Git already own that information.
- **Checking off tasks does not increment the tasks content version or add revision history.** Coder changes actual completion marks only, preserving task wording, Planner provenance, and the existing approval basis. Planner owns substantive task changes.
- Routine readers exclude the final Revision History before loading content. Read all required current bodies, and recover truncated chunks without skipping content. Do not create a separate read-audit artifact.
- `research.md` is optional when useful, organized into purpose/scope, investigations/findings, open questions, and sources/references. It is a current-state research document, not a scratch dump. It has no content version, Revision History, or independent approval gate; substantive changes are reported through Planner and the log.
- `known-issues.md` captures current deferred findings/accepted limitations with enough rationale and scope to be useful. It is not a second append-only history or a requirement to fix every recorded item.

Planner returns incremental complete structured outputs at approval boundaries. Its **final tasks draft already includes the consolidated Planner handoff**: current final state, requirements/design/tasks context, material decisions and reasons, constraints, and dispositions. After unchanged tasks approval, Orchestrator can send that same return plus approval context to Architect. Do not call Planner again merely to obtain a duplicate consolidation. The handoff describes the final agreed behavior, not the conversation's back-and-forth.

Coder normally returns one cumulative completion/repair wrapper for its assignment, covering work before and after interruptions against the original baseline. Ordinary artifact checkpoints need no interim completion wrapper or Orchestrator acknowledgement. Genuine progress/blocker coordination is distinct from claiming completion.

Record actual complete native JSON, not a pointer/status object or a rewritten summary. Give each fact one place rather than duplicating inventories and test results across fields. Minor report-only omissions are corrected in the same assignment without a formal failure, new repair cycle, empty checkpoint, or automatic retest. Genuine execution failure or repeatedly unusable output still uses bounded recovery.

Normal operation creates **no temporary wrapper files or snapshots**. A concrete tool/recovery need can justify a temporary file, removed after safe recording/recovery; it must not become committed spec-folder debris. Each platform's recorder accepts the actual return once, derives metadata, and validates and reads back internally. Codex uses the shared validator's `record-handoff` command; Claude Code uses `claude_log.py record-return`, which reads the return from the subagent's transcript. The Codex recorder fixed a demonstrated Windows Unicode corruption problem without making the agent prove every transport step. Preserve explicit UTF-8 handling when adapting this behavior.

### Git ownership, checkpoints, and final acceptance

The user supplies a feature name, which may contain a version or just a description. An explicit branch selection wins; otherwise use the feature name, usually matching the spec directory. Never add a `claude/`, `codex/` or other prefix, or an invented product version. Validate the name and obtain direction for a conflict. Record the integration branch, remote, and baseline.

Use the existing local checkout. A request for a separate/fresh chat does not authorize a worktree. No agent force-pushes or performs the final merge.

| Completed update | Publisher and checkpoint boundary |
| --- | --- |
| Specification/research draft or substantive revision | Planner publishes its owned artifacts before the handoff/approval boundary. |
| Natural coding group, meaningful partial work, or completion | Coder publishes implementation, tests, docs, and actual task progress. A deliberately Red checkpoint is described honestly. |
| Authoritative task-log update, user approval/request/override, review return, disposition, or final acceptance | Orchestrator publishes the log and its related owned artifacts. Related records from one logical update may share a checkpoint. |

Each checkpoint is committed and pushed. Do not batch away distinct completed drafts or approval gates; do not commit after every file write or command. Serialize Git ownership and use coherent yields when Orchestrator needs to record an asynchronous decision during producer work. Preserve unrelated staged, unstaged, and untracked changes.

Artifact checkpoints and log checkpoints intentionally differ. A legitimate Planner/Coder commit may contain no `task_log.json`. Commit metadata identifies the feature, publisher, kind, and relevant assignment; log checkpoints identify the event range. Do not create routine checkpoint events, success receipts, or recursive commits to record successful pushes.

On a failed/uncertain push, preserve local work and actual attempt evidence and follow the existing bounded, user-directed recovery. Commit the recovery authorization before its one permitted push; successful remote ancestry proves delivery without another receipt. Other blockers pause only dependent work. Since v2.1.0, a checkpoint attempt journal counts only records on the run's own branch and remote whose commits are in the current checkpoint's ancestry, so an earlier run of the same feature can't block a rerun.

On resume, Orchestrator examines the log, native ownership/output, branch/baseline, and recent Git metadata plus changed-file names/statuses, paging further if necessary. It still does not read product/spec diffs. Coder can inspect its own checkpoints, diffs, code, tests, and task progress to reconstruct cumulative work and distinguish historical checks from newly executed checks. Do not infer old test success from a checkbox or duplicate an active writer.

After Reviewer acceptance, obtain the user's explicit final feature acceptance, record/deliver completion, and generate one meaningful conventional squash-commit message describing the complete change against the integration baseline. A request for a commit message is not acceptance. **The user manually merges; neither Orchestrator nor any other agent does it.** Maintenance commits/branches/pushes in this source repository require separate user authorization.

### Exceptional implementation phases

Phases were accepted only for unusually large features whose Coder context genuinely needs to be split. Task count or multiple checkpoint groups is not sufficient justification; no fixed threshold was agreed. Even the substantial FEC bot migration was thought unlikely to need them.

An approved phase has stable task membership and a cumulative phase return. Subsequent phases use fresh Coders; repair/recovery preserves useful context. Basic has no intermediate reviews; Standard uses Basic intermediate reviews; Maximum uses Standard. Final review always uses full feature settings.

Intermediate Reviewer capability retains the full Reviewer model and uses the agreed effort mapping `max → high`, `xhigh → medium`, `high → low`; unsupported/unmapped settings require a decision. Standard and Maximum intermediate stages have one and two repair cycles respectively, separate from final-review allowances. The final Coder owns whole-feature integration, final Test-Maintenance/Verification, the consolidated whole-feature return, and all final-review repairs, including earlier-phase code.

Claude Code's per-call efforts can express this mapping; native phase execution remains untested on both platforms. Do not silently substitute a guessed equivalent, and do not make phase infrastructure part of every ordinary feature.

### Versions and compatibility

Workflow semantic versioning is separate from integer template versions, per-document content versions, and a consumer product's version. Both reusable input templates currently have template version 2; completed proposals remove the template-version line and authoring guidance.

The initial v2.0.0 deliberately does not migrate pre-v2 or missing-version logs. Old completed features stay untouched; an unusual request to use an incompatible log stops for explicit user-directed handling. The discarded prerelease shapes from disposable tests also did not justify a migration framework.

**Future patch/minor readers must keep supported older logs valid and usable.** A v2.0.0 or v2.1.0 log should keep working under v2.2.0 without inventing prior user decisions. Compatible additions need documented reasonable defaults when absent. Old readers need not understand new logs. Incompatible structural/semantic changes require a major-version decision and an explicit migration-or-breaking-change discussion.

v2.1.0 added Claude Code without breaking 2.0.0 logs (see "Settled in v2.1.0"); v2.1.1 added nested placement and authorized relocation, and v2.1.2 added narrowly authorized external specification-input commits while preserving existing log formats. The next release is v2.2.0 unless it changes the log schema incompatibly; then it becomes v3.0.0 and needs that discussion. A canonical VERSION bump reaches both integrations through their symlinks, so compatibility matters even when a change is platform-specific.

## Settled in v2.1.0: the Claude Code integration

The [v2.1.0 proposal](../v2.1.0/proposal-orchestrator-flow-v2.1.0.md) records the reasoning; these are its decisions as implemented. Like the v2 behavior above, they aren't reopened without a concrete reason.

- **Installation:** two user-level links, `~/.claude/skills/orchestrator-flow` and `~/.claude/agents/orchestrator-flow`, as subfolders beside the user's other skills and agents. A venv inside the skill runs every workflow script; only the startup check uses `python3`.
- **Start:** the user types `/orchestrator-flow`, because the skill sets `disable-model-invocation`. A request in other words that Claude follows by hand asks once, before the run starts, then runs as if invoked.
- **Startup check:** every invocation, including a resume, checks:
  - the running Claude Code version, read from `$CLAUDE_CODE_EXECPATH`, against a minimum of 2.1.296
  - the venv
  - environment overrides that defeat per-call model or effort
- **Roles:** the main conversation is Orchestrator, on the session's own model. Planner, Architect, Coder and Reviewer are real `flow-*` subagents with Claude-native contracts. Each starts in the background, never as a fork, with the accepted model and effort passed on every call. Models are short names such as `opus`, `sonnet`, `haiku` or `fable`. Start prompts open with `Orchestrator-Feature` and `Orchestrator-Invocation` lines.
- **Capability:** separate from assurance, as in Codex. Orchestrator recommends settings per feature, with a reason for each, and the user accepts or overrides them. The starting repository defaults are:
  - Planner: opus/xhigh
  - Architect: opus/max
  - Coder: opus/high
  - Reviewer: opus/max
  - `exploration_helpers`: sonnet/medium
  - `helpers`: haiku/medium
- **Helpers:** `flow-explorer` and `flow-runner`, started by their lead. Explorers use `exploration_helpers` when it's set and `helpers` otherwise; runners use `helpers`. Under a background lead, helpers run asynchronously: the lead ends its turn while it waits, and the hand-back wakes it.
- **Recording:** the Claude-only `claude_log.py`:
  - records role returns straight from subagent transcripts (`record-return`), and runs before every message to a lead
  - validates Orchestrator's own entries (`append-entry`)
  - finds a lead's agent ID from its start-prompt lines (`find-agent`)

  Notice text is never copied into the log.
- **Continuation and resume:** leads are continued by agent ID with SendMessage, across approvals and repairs, while their model and effort still match. After an interruption, the user resumes the same session and runs `/orchestrator-flow` again. A lead whose helper was lost with the session is continued by message and reruns that work with a fresh helper.
- **Runtime:** Claude keeps its own copy of the shared runtime, byte-identical to Codex's and enforced by a parity test. Contracts and the Claude-only scripts stay platform-specific.
- **Permissions:**
  - Auto mode is recommended; acceptEdits with the README's allow rules is the alternative.
  - Headless `-p` runs aren't supported.
  - The workflow never changes the session's mode.
- **Versioning:** 2.1.0 is additive. 2.0.0 logs stay valid, an absent `exploration_helpers` keeps its 2.0.0 meaning, and Claude logs record `platform: "claude-code"`.
- **Rules tightened by the native tests:** the initial task log and repository defaults are created with the Write tool, never a shell redirect or heredoc. The two changes that apply to both platforms, no product or requirements questions from Orchestrator and run-scoped checkpoint journals, are in the v2 behavior above.
- **Not in scope:**
  - no Copilot or Cursor changes
  - no runtime shared by reference
  - no headless operation
  - no migration of pre-v2 Claude logs
  - Windows not yet covered (item 11)

## Implementation boundaries

The first v2 implementation attempted to make other platforms load shared files from the Codex integration and gutted much of their substantive native guidance. The user rejected this. Those platform folders were restored, and v2.0.0 was intentionally completed for Codex only. v2.1.0 then added Claude Code with its own native contracts and runtime copy.

The implementation also built export/copy/materialization machinery and treated links as text pointers. That was based on the wrong installation model. The user clones this repository and symlinks the integration into the relevant tool's configuration. There is no exported product package to build or deploy.

Preserve these boundaries:

- Each integration owns its substantive native instructions and runtime resources. No integration loads another's files, and there is no generic shared orchestration runtime: the shared runtime files are byte-identical copies in each v2 integration, checked by `tests/test_runtime_parity.py`.
- Required canonical `VERSION` and template resources are exposed through real relative symlinks within the integration, stored by Git as mode `120000`. No flattened-pointer parser, parent-directory search, consumer-product VERSION fallback, or export fallback. Each platform's layout and installation follow its verified native support.
- Required runtime utilities belong with the integration that executes them. The validation/replay, document-reader, handoff-recorder and checkpoint helpers, and Claude Code's startup check and log writer, are functional runtime support, not an installation framework. Do not remove useful helpers merely because the exported-package approach was rejected.
- Development tests belong under repository-level `tests/`, not in a symlinked skill directory. The live test kits belong under `tests/live/`, not release proposal folders.
- `Directives/codingAgentDirectives.md` remains reusable, project-owned coding guidance outside the integrations. Users copy/customize it as appropriate. Workflow policy must not be added to that general document or imposed through an automatically loaded distribution copy.
- README explains what the repository provides and how to use it. Do not narrate “part-2 corrections,” plans, revision tracking, or implementation minutiae in operational guidance. Do not add release-folder READMEs or validation-report documents merely for ceremony.
- Retain meaningful behavioral, schema, and actual linked-resource tests. Export/materialization tests, extra symlink-creation/clone exercises requiring special privileges, broad distribution infrastructure, and wording-only tests were rejected or removed. Tests that validate literal instructions do not establish native agent compliance.

## Before the next release

1. **Watch the next real Codex run.** v2.1.0 changed two parts of the shared runtime:
   - the optional `exploration_helpers` assignment
   - checkpoint journals scoped to the current run (`run_attempts` in `checkpoint_state.py`)

   Only the development suite exercised these on Codex. The decision was not to run a separate Codex test before release, because the next release will be validated anyway. If either change misbehaves in a real Codex run first, ship a v2.1.1 fix.

   v2.1.0 also moved the Codex live kit to `tests/live/codex/`, with its inputs shared in `tests/live/common/proposals/`. Its master now finds the source checkout three levels above the kit, and the next Codex run of the kit will be the first real use of that discovery. If it fails, fix it in v2.1.1 too.

## Workflow and contracts

2. **Shapes of Orchestrator's own log entries.** In the first native run, Orchestrator couldn't find an example of what to pass to `claude_log.py append-entry` for its own events.
   - It read the references with `cat` and ran 11 inline Python scripts against `common.schema.json` and `task_log_schema.json` to learn each event's `details`.
   - One entry was refused ("Final acceptance must disclose current known issues") before a corrected retry.
   - `references/examples/` holds only role returns and repository configuration.

   Give Orchestrator a reference or examples for every event it records. If the clearest fix changes the schema itself, the release becomes v3.0.0.

   The checkpoint helper has a related gap. Neither recovery contract names `checkpoint_state.py attempt --authorization-event <event-id>`, which an authorized push retry needs. Without it, the helper refuses with "Previous delivery failed/is uncertain; obtain recovery direction", which could send Orchestrator back to the user for an authorization it already has. `failure`'s required flags are likewise documented only by `--help`. Until the v2.1.0 README cleanup, the README held the only list of these flags.
3. **Prompts in acceptEdits mode.** The same `cat` reads and inline scripts match none of the documented allow rules, so in acceptEdits mode each one would prompt; auto mode was unaffected. Item 2 should remove most of them. The contracts could also steer Orchestrator to the Read tool, which the README's `Read` rules already cover.

## Claude transcript recorder (`claude_log.py`)

4. **Helpers that finish without a peer hand-back.** `pending_helpers` treats a helper as finished only when its hand-back arrives as a peer message. If a helper finished some other way *and* its lead's report were malformed, the recorder would read the lead as still waiting. Orchestrator would then wait instead of asking for a correction. All 11 helpers that finished in the native runs handed back as peer messages. Consider also checking the helper's own transcript for a finished run.
5. **The coordinator-message reset.** A coordinator message clears the pending-helper list, because helpers lost with an interrupted session never hand back. If Orchestrator messages a lead while it waits, and the lead replies in plain text before its helper hands back, `record-return` reports `report_not_json`, and a stray correction request can follow. It's recoverable, since the lead just says it's still waiting. A precise fix needs a way to tell a resume from an ordinary message, or to see whether a helper is still alive.

## Shared runtime

6. **Cost of the journal filter.** `run_attempts` runs one `git merge-base --is-ancestor` for each journal record on the run's own branch. That's fine at today's journal sizes; batch it if journals grow large.

## Testing

7. **A Claude version of the live test kit.** The short [Claude native test](../../tests/live/claude/README.md) is the starting point. Codex's design, where a master session holds the user's delegated authority and answers each Orchestrator's dialogs, doesn't carry over. A probe on 2026-10-16 found:
   - another session's message can't answer an open AskUserQuestion dialog; it queues behind it
   - the tool for stopping a session's turn refuses while that session waits for the user
   - a slash command runs only when it's the CLI's opening prompt, not when it's a desktop session's opening prompt or a message

   The options:
   - the user answers the dialogs, with features possibly launched in CLI tabs by a master session
   - a contract option to ask in plain text when the user has delegated decisions, then a test of whether Orchestrator honors labeled delegated decisions
   - an Agent SDK host program that answers dialogs in code, if the SDK supports that, which hasn't been checked
8. **Not yet covered natively.** No native run has shown these yet, though most have deterministic tests. The [Claude native test](../../tests/live/claude/README.md) can cover several of them in its next run:
   - the `flow-explorer` helper, which neither native feature needed
   - the plain final-message report form, because every return used SubagentHandback
   - a tool call interrupted inside a lead after a resume, the Claude Code 2.1.296 fix; in run 2 the Coder was waiting, not mid-call
   - `find-agent` choosing between two sessions' leads with the same feature and invocation; run 2 got a different invocation from run 1
   - the desktop app as the workflow host, since both native runs used the CLI
   - an Opus Orchestrator after the step-4 checklist fix; before it, Opus left out the per-choice reasons until asked
   - a confirmed start through context compaction: whether a `SKILL.md` that Claude followed by hand holds up as well as an invoked skill, and whether the confirmation is still never asked twice

9. **Codex live-kit issues deferred from v2.0.0.** The [v2.1.0 handoff](../v2.1.0/handoff-orchestrator-flow-v2.1.0.md) (§7) kept these from v2.0.0's third run for the next significant workflow change. v2.1.0 only moved the kit.
   - Fix the deliberate push-rejection hook so it accepts the workflow's paragraph-separated checkpoint trailers, and preflight it against a real checkpoint commit. This is a harness defect.
   - State that a successor's eligibility follows actual acceptance and delivery, not a historical protocol Fail.
   - Set out the local push destinations and their standing scope in the setup the user authorizes, so delegated pushes don't ask repeatedly.
   - Keep these as observations:
     - Git exit codes invented after a tool refusal
     - the Maximum Architect's disagreement between its startup and status signals
     - the missed in-flight Reviewer override, which stays Unverified
10. **Codex coverage still open from v2.0.0** (v2.1.0 handoff §6.2):
    - The full Maximum feature sequence wasn't validated.
    - Native exceptional-phase execution remains deferred.
    - The deterministic inventory has gaps around some intermediate effort mappings and the Maximum two-cycle intermediate boundary.

    Choose proportionate coverage. A full matrix isn't the default response to every kit fix (see "Test-kit intent").

## Platforms

11. **Windows.** Claude Code setup on Windows, and a native test from PowerShell, aren't covered yet.
12. **Copilot and Cursor.** Their v2 updates remain deferred, as set out in `AGENTS.md`.

## Test-kit intent

The live kits exercise real native agents on a small Python line-list CLI. They are compliance and behavior observation kits, **not benchmarks of which model or assurance is fastest or best**. They test acceptance of recommendations, deliberate supported overrides, and whether the selected settings govern subsequent work. They don't manufacture product bugs to make every row green.

The next paragraphs describe the managed Codex kit in [tests/live/codex](../../tests/live/codex/README.md): an overview, runbook, scenario catalogue and six prompt files. Its four product proposals live in [tests/live/common/proposals](../../tests/live/common/proposals/README.md), beside the Claude native test's proposal. The kits were intentionally moved out of release `.docs/` folders.

The user supplies one parent test folder. Allocate the next unused `testrun-N` there, with all working repositories, local bare remotes, and evidence inside that run. A fresh empty parent starts at `testrun-1`; occupied/incomplete entries are not overwritten. Working repositories are named `basic`, `standard`, and `maximum`, with corresponding `basic-repo`, `standard-repo`, and `maximum-repo` local bare remotes. A working Git repository and initial commit must exist before its first push; cloning the prepared local bare repository is also a valid setup approach.

Setup provides ordinary project guidance, ignore rules, and proposal inputs only. **The initial application itself must be built through Flow in all three projects**, followed by unique lines, output limit, and ignore case: four proposals times three assurance cases. Each proposal is copied into its own `.docs/specs/{feature}/proposal.md` beside that feature's later log/specs. Private controller stimuli and expected results stay outside the product proposals and runner context.

Use one new chat per feature. A planned fresh-context replacement continues the same feature; it is not a new feature or permission to reuse a completed feature's chat. This is the user's practice and a test-kit requirement, **not a requested runtime prohibition on ever reusing a chat**.

Successors start from the accepted/delivered predecessor branch tip as their explicit integration baseline. `main` remains at bootstrap; the kit does not merge features. Independent projects may continue when another predecessor chain is blocked.

The human-submitted master prompt delegates setup, native chat creation/messaging, normal scripted workflow decisions, and evidence collection within the disposable scope. The master selects supported capability choices after actual Orchestrator recommendations; exercise both accepting a recommendation unchanged and overriding it. Master and top-level Orchestrators used GPT-6.1 Sol High to control cost; lead/helper assignments vary deliberately. These are Codex test choices, not Claude model defaults.

Keep controller evidence under run-level `.orchestrator-test/`, outside consumer repositories. Controller helpers do not count as workflow-role helpers. Unrelated staged/unstaged/untracked fixtures belong only to their assigned scenario and must be identified as intentional; the three projects do not all need identical injected disturbances. Do not record controller-only actions as invented feature events.

Reports distinguish accepted product delivery, protocol observations, actual native role returns, deterministic tests, and inference. Use Pass/Fail/Unverified/Not run honestly. A later success does not erase a historical failure, but a historical failure does not automatically prevent an accepted product from being used. Close out when no authorized work can advance, identifying pending human choices separately from technical blockers; do not leave the master idle indefinitely or repeatedly poll unchanged state.

Do not require another full matrix as the default response to every small kit fix. Native phases remain deferred unless specifically selected for future testing. Claude Code has its own short [native test](../../tests/live/claude/README.md) rather than a reproduction of Codex's chat and project orchestration; item 7 covers a fuller Claude kit.

## Lessons for running the next release

- **Carry the baseline forward.** "Why v2 exists", the settled v2 behavior, "Settled in v2.1.0", the implementation boundaries and the test-kit intent all still apply. Don't reopen settled decisions. Perfection is the enemy of good.
- **Test natively early, and compare runs.** Three contract assumptions failed only on real runs:
  - the symlink allow-rule behavior
  - helpers running asynchronously under background leads
  - a model following `SKILL.md` by hand when a slash command didn't run as one

  Comparing run 1, which passed an explicit `run_in_background: false`, with run 2, which omitted it, is what separated platform behavior from model behavior.
- **Verify documentation claims natively** when users will follow them. Part D confirmed the README's auto-mode `Read` rules this way.
- **Keep review separate from implementation.** A review thread that checked every diff and claim against the files and transcripts caught a confirm-first condition that would have fired on every typed run, and a misread finding.
- **Messages between threads need care.** They're delivered only when the receiving thread's turn ends, and can't be recalled once queued. Agree on the content before sending; "yes, but…" is still discussion. A hold must arrive before the work starts. In this release, a reorganization was done, undone and redone because a hold and an undo were queued behind work already under way.
- **Commit shared files in order.** When several pending changes touch the same files, commit them in order and apply later edits only after the earlier commit. Then no commit links to a file that doesn't exist yet.

## Reference: Claude Code platform facts

These were verified natively during v2.1.0, on CLI 2.1.300 to 2.1.304 and the desktop app's 2.1.299.

### Transcript structure the recorder relies on

Items 4 and 5 rely on these, which were checked on real transcripts.

- **Where a run starts:** at a user prompt that isn't `isMeta`, or at an `isMeta` user record whose `origin.kind` is `coordinator` (a SendMessage continuation) or `peer` (a helper's hand-back). Harness nudges are `isMeta` with no `origin`.
- **How a message is recorded:** one record per content block, all sharing `message.id`. The final record carries `stop_reason: "end_turn"`, while `max_tokens` marks a cut-off.
- **Hand-backs and refusals:** a SubagentHandback's tool result is `{"success": true, …}`, and refusals set `is_error`.
- **Async helpers:** the launch's tool result carries `toolUseResult.status: "async_launched"` and the `agentId`. The hand-back arrives with `origin.from` set to that ID.
- **Large outputs:** tool results over 50,000 characters are saved to the session's `tool-results/` folder, and the model gets a 2 KB preview.
- **Background notices:** the desktop app XML-escapes their text. The CLI delivers them as `<task-notification>` entries in `queue-operation` records.

### Skills, permissions and resume

- **Skills:**
  - `${CLAUDE_SKILL_DIR}` expands to the link path, `~/.claude/skills/orchestrator-flow`, not the checkout.
  - An inline `` !`…` `` command that matches `allowed-tools` runs pre-approved.
  - `disable-model-invocation` hides a skill from the model, but not its files.
- **Permissions:**
  - A read through a symlink is allowed only when both the link path and the resolved path match allow rules. Separate rules may match each one.
  - Narrow `Read` rules suppress the out-of-project read prompt in both acceptEdits and auto mode. That prompt's "keep allowing" and "block … from now on" options are both permanent, and both apply to every read outside the project.
  - Bash allow rules match the command text as written.
- **Resume:** `claude --resume` keeps the session ID. Background agents cut off when a session ends aren't restarted, so a lead's lost helpers never hand back.
- **Commit attribution:** Claude Code's `attribution` setting controls the Co-Authored-By trailer. `false` hides all attribution on 2.1.281 or later; earlier versions reject it and skip the settings file that holds it. The object form, with empty `commit` and `pr` strings and `sessionUrl: false`, also works on older versions.

## Source map

| Read when needed | Source |
| --- | --- |
| Maintenance boundaries, layout and validation | [AGENTS.md](../../AGENTS.md) |
| User-facing setup and behavior | [README.md](../../README.md) |
| Proposal format | [Proposal template](../../templates/proposal-template.md) |
| Released v2.1.3 reconciliation | [General external-commit proposal](../v2.1.3/proposal-v2.1.3-authorized-external-commit-reconciliation.md), [checkpoint runtime](../../.codex/skills/orchestrator-flow/scripts/checkpoint_state.py), [tests](../../tests/test_spec_input_commits.py), and retained [v2.1.2 narrow grant](../v2.1.2/proposal-v2.1.2-authorized-spec-input-commits.md) |
| Codex entry and contracts | [SKILL.md](../../.codex/skills/orchestrator-flow/SKILL.md), [references](../../.codex/skills/orchestrator-flow/references/) |
| Claude Code entry, contracts and agents | [SKILL.md](../../.claude/skills/orchestrator-flow/SKILL.md), [references](../../.claude/skills/orchestrator-flow/references/), [agents](../../.claude/agents/orchestrator-flow/) |
| Shared runtime, byte-identical in both skills | Each skill's `scripts/` and schemas, enforced by `tests/test_runtime_parity.py` |
| Claude-only runtime | `check_claude_code.py` and `claude_log.py` in the Claude skill's [scripts](../../.claude/skills/orchestrator-flow/scripts/) |
| Development tests and their limits | [tests/README.md](../../tests/README.md) |
| Live test kits | [tests/live](../../tests/live/README.md): `codex/`, `claude/`, `common/` |
| History and rationale | [.docs/v2.0.0](../v2.0.0/) (v2 proposals/corrections), [.docs/v2.1.0](../v2.1.0/) (Claude handoff/native tests), and [deferred custom-agent research](../future-improvements/codex-custom-agents-and-context-retention.md) (not selected) |
