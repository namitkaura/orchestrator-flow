# Handoff: Orchestrator Flow v2.2.0

Start planning the next release here, provisionally as v2.2.0. The six selected improvement areas and the **released v2.1.2 baseline** are described in the dated updates below. If the chosen authoritative schema or workflow semantics are incompatible, consider v3.0.0 during proposal design. A major version is not justified solely by the number or size of changes.

This file preserves why v2 exists, the settled workflow baseline, Claude Code integration, implementation boundaries, and the v2.1.0 candidate findings. The dated updates carry the context through v2.1.1 and v2.1.2 and record subsequent user decisions; the older candidate/test-kit/platform sections remain useful historical reference, not automatically selected scope. The [v2.1.0 native-test summary](../v2.1.0/native-test-summary.md) contains historical native-test evidence.

## Start here

- **State:** Released baseline is **v2.1.2** on `main`, tagged `v2.1.2`, squash commit [`79af96c`](https://github.com/namitkaura/orchestrator-flow/commit/79af96cf42cc41c67f5d11cff73a34d6456dc765). The `v2.2.0-workflow-clarity-and-flexibility` planning branch was rebased onto that release, preserving its five development changes before this handoff update. Branch/release naming is provisional pending schema design.
- **Reading:** this file is the only required reading. [AGENTS.md](../../AGENTS.md), which holds the maintenance rules, loads automatically in Codex and Claude Code sessions in this checkout. Everything else is for when a topic needs it: the source map at the end points to the contracts, scripts and history. The proposals, the v2.1.0 handoff and the native-test summary hold rationale, history and evidence; what they settled is summarized here.
- **Status of the items:** six improvement areas remain selected for proposal *development*, not yet specified or authorized for implementation. Earlier deferred candidates remain optional. Preserve unaffected v2/v2.1.0/v2.1.1/**v2.1.2** behavior unless a selected design explicitly replaces it. This handoff supplies context for future proposals; those proposals, once authored, become the decision/specification record.

## Released baseline update — November 18, 2026 (v2.1.2)

This update **supersedes the older v2.1.1-as-latest assumptions**, while preserving the November 14 planning analysis below as historical evidence. It does not create a seventh v2.2.0 improvement area or authorize implementation.

- **Release:** v2.1.2 was developed from released v2.1.1 on `v2.1.2-authorized-spec-input-commits`, squash-merged into `main` and tagged `v2.1.2` at `79af96cf42cc41c67f5d11cff73a34d6456dc765`. Its completed standalone [proposal](../v2.1.2/proposal-v2.1.2-authorized-spec-input-commits.md) records the narrow design and motivation. The v2.2.0 development branch now uses v2.1.2 as its baseline.
- **Origin:** a legitimate user-authored F01 follow-up proposal was already pushed in the consumer `music-analyzer` feature branch at `49b0ea61fe07a710acb91bd081e5dcba02312abb`. Its normal, trailerless commit prevented Orchestrator Flow v2.1.1 checkpoint validation even though the Planner could identify Requirements as the correct first artifact for the revised Stage A → A2 → generated Stage B scope. The earlier `fec-bot` v2.0.1 input-documents case exposed the same class of blocker.
- **Exact patch boundary:** v2.1.2 accepts an **explicitly user-authorized, single-parent, add-only commit of regular UTF-8 `proposal-*.md` or `bugreport-*.md` files** in the active feature's effective historical spec directory. It validates the entire commit, changed modes/paths/blobs, Git ancestry, and the exact full commit ID. The grant uses the **existing** `user-authorization-recorded` event (`kind: external_operation`, `operation: accept-spec-input-commit`) with no new event, role, stage, task-log schema or wrapper. A valid input commit is acknowledged but **never masquerades as a Flow checkpoint or grants spec approval**. Its Orchestrator log acknowledgment must reach the remote before dependent Planner/Coder publication; failed/uncertain push recovery, historical relocation and existing 2.1.1 logs remain supported.
- **Evidence and limits:** the release added 15 focused regression tests and ran the Windows 189-test suite, with seven POSIX startup-fixture failures also reproduced on the pre-patch baseline; do **not** claim an unconditional clean full-suite pass. The user tried the patch against the **actual blocked F01 feature** and confirmed the workflow got past the original external-proposal-commit blocker. This confirms that specific problem was resolved; do not infer that the entire F01 revision or every possible downstream workflow action was completed.
- **Still in v2.2.0 scope:** externally authored **code/test corrections**, user-originated finding or change wrappers, their native Coder/Reviewer re-entry, and more general authorized external-commit reconciliation remain unsolved. Improvement 3 must **extend or intentionally supersede** the now-shipped restricted specification-input path without duplicating it, weakening its explicit Git/authorization protections or forcing another ledger. Improvements 1, 2, 4, 5 and 6 remain as separately selected.

The v2.1.2 release is not a new v2.2.0 proposal, and the next planning work should inspect the **current v2.1.2 source** rather than redesign or describe the v2.1.1 blanket-rejection behavior as still current.

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

### The six selected next-release improvement areas

Keep items 5 and 6 explicit even though role-contract changes may overlap. These are **problem statements and constraints for a proposal**, not already-decided implementations.

| # | Improvement | Core requirement |
| --- | --- | --- |
| 1 | Task-log readability | Clear fields, locally meaningful content, minimal reference chasing or duplication |
| 2 | Workflow flexibility | User-provided findings or already-applied work can enter the appropriate normal stage |
| 3 | External commit reconciliation | Extend v2.1.2's spec-input exception to other legitimate user-originated work with bounded verification |
| 4 | Orchestrator helpers | A separate economical read-only helper capability for exceptional preparation and inspection |
| 5 | Implementation readiness | Approved requirements, design, tasks and manual procedures are executable and sufficiently complete |
| 6 | Planner–Coder role boundary | Consequential planning belongs to Planner; Architect independently enforces; Coder escalates gaps |

#### 1. Human-first `task_log.json` readability

The authoritative task log has three primary functions: **human understanding** (what happened, findings, files, results, next steps); **recovery** (state, approvals, decisions, interruptions/new sessions); and **complete meaningful native role handoffs** (original Planner/Architect/Coder/Reviewer wrapper content preserved for subsequent agents). It is not an elaborate provenance/transaction database.

The user wants **clear, self-identifying field names and information locality**, not literal restoration of pre-v2 field names. `checks`, `test_results`, `cli_runs`, `implementation_details`, `notes` and a possible `verification_results` are naming candidates, *not settled mandatory names*. Choose one authoritative home for each kind of information. Avoid storing identical test results in multiple fields or repeating the same implementation explanation across `summary`, `notes` and generic `evidence`.

- Reading **one event** in VS Code should explain its substantive action, outcome, implementation/findings, important changed files, meaningful verification and required next step without forcing the human to resolve normalized references in separate events/sections. Preserve `event_id` and historical source references for exact context, approvals, prior reviews and recovery; these links should supplement the explanation, not replace it. Do not duplicate full prior reviews in every subsequent wrapper either.
- Prefer a predictable visible structure: actual `must_fix`, `should_fix` and `nit` (singular) categories, even if empty, and clear `changed_files`/`new_files`/`deleted_files` inventories. Whether they are schema-required or agent-required remains a design decision.
- Preserve useful v2 metadata: native invocation/context, artifact versions and reference identity, actual evidence/review dispositions, task progress, cumulative Coder work, checkpoint provenance and recovery. Keep full original agent returns, not status-only placeholders or Orchestrator summaries.
- Current v2.1.2 schema (unchanged here from v2.1.1) permits `issue_details: {}` and optional changed/new/deleted inventories. Its Coder wrapper requires `summary`, `task_progress` and `checks`. Current instructions/tests deliberately omit empty optional fields. A mandatory change to old optional fields or replacing an authoritative field could therefore be a real breaking contract change.
- Do **not** create a redundant `task_log_summary.md`, duplicate archival files, helper reports or a separate machine-normalized database. Evaluate the proposed shape against actual v2.1.1 examples, not just schema validity. Pre-v2 is a *readability reference*, not a demand to return wholesale to its fields.

#### 2. Legitimate user-directed handoffs and stage re-entry

Current v2.1.2 `user-change-requested` still routes to Planner/spec revision. `coding-revision-started` expects unresolved formal Reviewer findings and `code-review-started` expects a recognized Coder handoff, so user-originated post-review activity cannot always enter the sensible stage.

- **User reports a bug after review:** a truthful user-originated findings/review-like wrapper should permit the *normal Coder* to implement a bounded correction when there is no missing/new specification decision; then the normal Reviewer assesses the actual Coder `change_wrapper`. If product requirements or architecture are changed, resume at the earliest affected Planner artifact and observe necessary approvals.
- **User/another ChatGPT already committed code:** a truthful user-originated `change_wrapper` should enter the *normal Reviewer* path, without fabricating a Coder invocation or using a disconnected standalone Reviewer. The `fec-bot` v2.0.1 two-line test correction (`ce8747fb32b8e519d8b25dd3f2a994eeb42f89c4`) instead resulted in a standalone review and pointer-only audit workaround; that is the demonstrated failure.
- **User-authored proposal or bug report:** v2.1.2 now supports an exact, explicitly authorized **add-only input commit** through the normal Planner revision path; retain that functioning mechanism. Already-made specification edits or other external changes still need an appropriate factual handoff, not a fabricated Planner completion or skipped approval.
- **Authority and continuity:** proposed user-originated events may use `actor: "User"` and `requestor: "User"`. The existing `user-change-requested` currently records `actor: "Orchestrator"` / `requestor: "User"`; don't retroactively rewrite it. Preserve actual past review wrappers, dispositions, approvals and previous Coder outputs. Follow-up Reviewer gets the actual earlier `review_wrapper` and newest `change_wrapper`, not a rewritten synopsis. Helpers may prepare truthful wrapper content but are not the substantive role.
- **Runtime impact:** new event/handoff shapes (names not decided), state transitions and recovery actions must be handled by `task_log_schema.json`, `workflow_protocol.py`, native recorders and both platforms. Codex `record-handoff` and Claude `record-return` assume a lead-owned active invocation; Claude `append-entry` currently accepts Orchestrator-created `details` events, not an embedded user-supplied wrapper. Extend narrowly, preserving normal validation, actual-agent attribution and existing approval gates.

#### 3. Authorized external Git commits

**Historical problem (v2.1.1):** `checkpoint_state.py` rejected every post-baseline commit without recognized Flow checkpoint trailers, blocking user-authored inputs and externally made changes. **Current v2.1.2 baseline:** a deliberately narrow `accept-spec-input-commit` exception now accounts for expressly authorized, add-only proposal/bug-report Markdown commits after strict whole-commit and historical-path validation. `validate_workspace()`, checkpoint/push inspection and remote acknowledgment enforcement support that path. All other unrecognized external commits, including external code/test edits, are still rejected. Do **not** reimplement or describe the fixed input case as pending work.

Concrete `fec-bot` v2.0.1 examples:
- `ce8747fb32b8e519d8b25dd3f2a994eeb42f89c4` — externally authored test correction after accepted review.
- `10384738c998356d23a7345cc321d4cf34ffec41` — externally authored **one commit adding two input documents**, `bugreport-unicode-admin-title-matching.md` and `proposal-update-text-only-and-rejected-search-recovery.md`, which required a **Planner spec revision**, not a code-review source.
- The user authorized a narrowly scoped **manual checkpoint reconciliation workaround** to finish and release `fec-bot` v2.0.1. This was not a permanent product fix.

**Remaining v2.2.0 proposal:** extend the verified user-directed reconciliation model beyond v2.1.2's spec-input-only case. Inspect actual SHA/ancestry, changed-file inventory and substantive content when needed via bounded read-only delegation; obtain user acceptance of precisely identified external code/test/specification work; record suitable scope/authority in the **existing log** and consistently recognize it in subsequent checkpoint, workspace, recovery and push validation. Preserve original commits and attribution; never forge trailers, silently trust unknown/unrelated work, invent a publisher identity or add a second audit ledger. Reuse the established restricted path for ordinary new proposal/bug-report inputs. The purpose of other external work determines its workflow re-entry stage; reconciliation and user-stage re-entry are related but distinct.

Preserve serialized Git ownership, safe fast-forward checks, unrelated-work protections, verified delivery and failed/uncertain push recovery. Retain v2.1.2's existing exact-input acknowledgment, acknowledgment-before-producer publication rule, and compatibility with historical checkpoint paths from v2.1.1 relocation; broader external commits and `feature-relocated` should compose, not be conflated.

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

Treat this as a small **Planner/Architect instruction refinement within improvements 5 and 6**. No new schema field, cross-reference validator, approval gate or seventh workstream is needed.



#### 6. Planner–Coder ownership: prevent hidden decision delegation

**Rule:** *Coder chooses how to implement the approved design, not what that design means.*

- **Planner** owns consequential user/product, architecture, data semantics, algorithm and verification criteria, external interfaces and evidence/publication policy, documentation scope and test-maintenance decisions. Place each in requirements, design or tasks as appropriate. Ordinary private loops, helper naming, simple refactoring and equivalent local technique remain Coder discretion.
- **Architect** performs an independent **Coder-readiness/decision-completeness review at Basic, Standard and Maximum**. Don't accept a plan merely because all acceptance criteria have mapped tasks, named filenames or tests. Ask whether two competent Coders could comply while selecting materially different behavior, data contracts or verification outcomes; if so, report the missing consequential decision, impact, and earliest artifact needing revision. Also assess **artifact locality and task accountability**: design contracts belong in design, task-specific instructions inside their numbered tasks, and detailed manual procedures in the manual plan. Flag orphaned unnumbered obligations, unclear cross-references, duplicate/conflicting contracts, and important work with no owning task. These are specification defects, not optional Maximum hardening items.
- **Coder** implements approved decisions and escalates real missing consequential ones through Orchestrator for Planner resolution and necessary artifact reapproval/review. Neither high capability nor strong assumptions grant Coder authority to invent requirements, data meanings, scientific methods, publication standards or test-preservation policy.
- **No new routine subsystem:** Planner self-audits as part of its existing task preparation; Architect enforces within its ordinary review; Coder uses normal blocker/clarification routing. Do not add a standalone readiness report, additional mandatory role, extra gate, persisted checklist or schema field.

Current Codex/Claude Planner instructions already require concrete tasks and test-maintenance planning; Coder's boundary is largely clear. Architect's requirement to check “sufficient concrete tasks/tests/documentation” is too easy to satisfy superficially, and the sharpest “do not force Coder to rediscover foreseeable design” obligation appears in the **Maximum** checklist. Strengthen Planner, Architect and common assurance instructions at **all** levels; clarify Coder escalation only as needed. Item 5 asks whether work is executable; item 6 assigns responsibility for decisions and escalation, without duplicating checks.

### Compatibility, release name and upgrade practice

**Working choice: v2.2.0 for planning, not yet a final compatibility finding.** SemVer major changes are justified by breaking published schemas or workflow semantics, not six substantial enhancements. Additive user event types, broader external-commit recognition and optional helper assignments may be minor-compatible; replacing required `checks` or changing previously optional field requirements may be breaking. The user is not attached to pre-v2 literal names, so **first design the most understandable authoritative wrappers** and then classify the real delta. If it is incompatible, discuss v3.0.0 and rename this release folder/branch during planning rather than maintain bad fields just to retain 2.2.0.

The user is the only current consumer and always uses the latest linked installation. Workflow upgrades are normally made **between completed features**; a mid-feature patch is unusual and usually fixes a blocker (the v2.1.1 relocation fix and deliberate v2.1.2 spec-input fix are examples). Completed features' logs are retained for **human audit**, and will not be read by the workflow again in normal practice. **Active** logs require accurate state/approval/return/recovery interpretation; patch upgrades must correctly resume them. Minor upgrades are normally feature-to-feature and should retain compatible meaning as appropriate to a minor release, but no elaborate hypothetical migration system is warranted. A new major version may break active old-format compatibility; finish ongoing work first and address any rare exception explicitly. Do not rewrite completed historical logs or build a dual-format execution engine only for them. The special older-reader caveat for v2.1.1 relocation is irrelevant to the user's latest-runtime practice.

### Architecture, review and testing touchpoints

- **Shared runtime/schema (identical Codex and Claude copies):** `references/common.schema.json`, `task_log_schema.json`, four `wrappers/*.schema.json`, `scripts/workflow_protocol.py`, `workflow_artifacts.py`, `validate_orchestrator_artifacts.py` and `checkpoint_state.py`. State/replay/next-action, references and publication must agree. Keep `tests/test_runtime_parity.py` parity; no cross-platform import adapter.
- **Native contracts:** both platform-specific Planner, Architect, Coder, Orchestrator, assurance and helper instructions. The Codex handoff recorder and Claude `claude_log.py` (`record-return`, `append-entry`, actual transcript handling) need appropriate user-event support; Claude may add one read-only `flow-orchestrator-helper` agent. Do not modify deferred Copilot/Cursor integrations.
- **Focused behavior tests:** user reported post-review bug → real Coder → real Reviewer; user-supplied already-applied correction → real Reviewer; external spec document commits → Planner; unknown external commit rejected; committed historical outputs and approval continuity; interrupted/new-context resume after user events; checkpoint validation and publish after reconciled commits, including **relocation across paths** and preservation of the **v2.1.2 spec-input acceptance path**; failure/uncertain push safeguards; human readability inspection of real log events; Architect catches incomplete external data/docs/Test-Maintenance decisions **and misplaced or duplicated task/design/manual-plan instructions** at lower assurance while allowing legitimate Coder implementation discretion. Planner and Architect should accept simple grouping headings and precise references without demanding repeated contracts, new sidecar reports or a semantic Markdown validator. Add selective native Codex/Claude runs; do not treat deterministic unit tests as proof of native role behavior.
- **Not automatic scope:** old handoff candidates about Orchestrator log-entry examples, acceptEdits prompts, Claude helper transcript edge cases, Git journal optimization, native live-kit expansion, Windows fixture portability/setup, Maximum/phase coverage and future Copilot/Cursor support remain separate choices. Adopt a small related fix only by deliberate scope decision. The 2.1.1 Windows fixture failures are not a mandate to fix them here.

**Repository ownership preference:** Orchestrator Flow source maintenance should originate only from conversations in the user's **Orchestrator Flow project**, not consuming-project chats. The user explicitly opted to enforce this personally; **do not encode it in `AGENTS.md`, skills, an extra permission gate, ledger or schema** without a separate request. The v2.1.1 patch remains accepted.

**Next work, when asked:** inspect actual v2.1.2 events/wrappers against human locality, recovery and full-handoff goals; choose coherent authoritative schemas, user re-entry and external commit semantics; evaluate breaking versus additive changes; then draft the proposal and select 2.2.0 or 3.0.0. Do not start implementation or automatically absorb the older handoff's unselected backlog.


## Why v2 exists

The motivating example was the user's FEC bot: a private repository, running from the user's laptop, serving roughly a dozen active users on one private Discord server. An API-provider migration worked very well, but the workflow spent approximately two and a half usage allocations hardening it. Repeated Architect and Reviewer passes kept reopening the whole specification or implementation and discovering increasingly minor improvements.

That outcome was too expensive for the project's consequences. Small, recoverable bugs would have been acceptable. The purpose of v2 was to match the cost of planning, implementation, and assurance to the work, while preserving deliberate engineering and useful recovery.

The governing instruction is **“perfection is the enemy of good.”** It applies to this workflow and its maintenance just as much as to the projects it produces.

- Optimize the ordinary successful path. Resumption is important but exceptional; extra bounded reconstruction during recovery can be preferable to permanent bookkeeping on every successful operation.
- Preserve enough information for the next agent and a future resume. A perfect process audit is not a deliverable.
- The user is often available to resolve an unusual situation. Do not build a transaction framework, watchdog, permission ledger, migration system, or elaborate recovery protocol merely to remove every possible question.
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
| Released v2.1.2 patch | [Authorized spec-input commit proposal](../v2.1.2/proposal-v2.1.2-authorized-spec-input-commits.md), [implementation](../../.codex/skills/orchestrator-flow/scripts/checkpoint_state.py), [regression tests](../../tests/test_spec_input_commits.py) |
| Codex entry and contracts | [SKILL.md](../../.codex/skills/orchestrator-flow/SKILL.md), [references](../../.codex/skills/orchestrator-flow/references/) |
| Claude Code entry, contracts and agents | [SKILL.md](../../.claude/skills/orchestrator-flow/SKILL.md), [references](../../.claude/skills/orchestrator-flow/references/), [agents](../../.claude/agents/orchestrator-flow/) |
| Shared runtime, byte-identical in both skills | Each skill's `scripts/` and schemas, enforced by `tests/test_runtime_parity.py` |
| Claude-only runtime | `check_claude_code.py` and `claude_log.py` in the Claude skill's [scripts](../../.claude/skills/orchestrator-flow/scripts/) |
| Development tests and their limits | [tests/README.md](../../tests/README.md) |
| Live test kits | [tests/live](../../tests/live/README.md): `codex/`, `claude/`, `common/` |
| History and rationale | [.docs/v2.0.0](../v2.0.0/) (v2 proposals, corrections, test kit) and [.docs/v2.1.0](../v2.1.0/) (Claude proposal, the v2.1.0 handoff with v2.0.0's test history, native-test summary) |
