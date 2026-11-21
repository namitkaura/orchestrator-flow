# Proposal: Orchestrator Flow v2.1.3 — Authorized External Commit Reconciliation

## Problem Statement

### Legitimate work outside the workflow still blocks all checkpoints

Orchestrator Flow uses Git checkpoints to preserve role ownership, approved artifacts, an append-only task log, and publish/recovery history. Those guarantees are useful. In the released 2.1.2 implementation, however, `checkpoint_state.py` still rejects ordinary commits after the recorded feature baseline unless they are either a recognized Orchestrator Flow checkpoint or an **explicitly authorized, add-only proposal/bug-report commit inside the active feature specification directory**.

The 2.1.2 exception was created to unblock a user-authored F01 follow-up proposal. It worked for that case: the workflow could record `user-authorization-recorded`, recognize the exact proposal commit, checkpoint the acknowledgment and resume the Planner without rewriting Git history. But the restriction to `proposal-*.md` and `bugreport-*.md` files in `.docs/specs/{feature}/` was narrower than the underlying problem.

A subsequent, independently confirmed F01 incident demonstrates the gap. While the user was working with an external ChatGPT planning thread, that thread reached its conversation limit. The user created a second continuity document and committed **one new file**, `.docs/handoffs/music-analyzer-continuity-002.md`, on the existing `f01-trustworthy-temporal-measurements` feature branch of `namitkaura/music-analyzer`. The commit was made after Codex had paused and yielded Git ownership. Its sole parent was the latest published F01 workflow checkpoint (event 94). It changed no executable code, specifications, experiments, configuration, existing results or task log. The file is a repository-wide continuity handoff to another discussion, **not a specification input**.

The user's exact-commit authorization was clear. The proposed `user-authorization-recorded` event passed task-log schema validation. Yet checkpoint/workspace validation still rejected the commit as unaccounted-for, because its legitimate path and purpose failed the narrow 2.1.2 filename/directory filter. The existing workflow history therefore could not publish the authorization, and further work was blocked. This is a **durability failure**, not a missing instruction to the Planner: a user decision in a conversation is insufficient if the runtime refuses to record and subsequently recognize it.

The same class of issue has arisen previously in FEC-bot v2.0.1 with externally supplied test corrections, and in F01 with a proposal commit. The user's normal development style involves ChatGPT planning threads, Codex/Claude Code, GitHub commits, and continuity files. External commits are therefore not necessarily anomalies. A patch that adds another special operation just for `*-continuity-NNN.md` would repeat the pattern: each new legitimate file type would require another exception and potentially another release.

### Reconciliation is not approval of the changed content

Two responsibilities must remain distinct:

1. **Git-history reconciliation:** Verify an actual, precisely authorized external commit and account for it durably, so strict checkpoint validation no longer treats that particular commit as unrelated history.
2. **Workflow interpretation:** Determine whether its content is a passive handoff, a new Planner input, a user-authored code/test change, a specification edit requiring proper artifact ownership, or a finding needing a native Coder/Reviewer stage.

The first does **not** imply the second. An accepted continuity handoff requires no task-state transition. A new proposal normally goes to Planner. Externally edited code must not magically become a Coder-authored `change_wrapper` or an already Reviewer-approved implementation. The broader user-originated role handoffs, flexible re-entry and improvements to stage ownership remain part of the separately planned v2.2.0 work.

The immediate objective is consequently **general, tightly authorized Git reconciliation without a wholesale rewrite of workflow states or agent return contracts**. The exception should be narrow in **authority and verified commit identity**, not in arbitrary document names.

## Proposed Solution

Extend the existing v2.1.2 acknowledgment machinery to account for **individually identified, user-authorized external Git commits** regardless of whether their ordinary repository files are proposals, continuity documents, or source/test changes. Preserve the entire genuine Git history, the existing task-log authorization event, strict workflow-checkpoint validation, and all separate content/approval safeguards. No external change becomes an Orchestrator-produced checkpoint by being acknowledged.

### 1. One explicit, durable user decision per external commit

Use the existing `user-authorization-recorded` event (`actor: User`, `requestor: User`, `kind: external_operation`) with a distinct, clearly named operation such as **`accept-external-commit`** (working name) and a `scope` containing the **full resolved Git commit object ID**. The user statement must genuinely approve the identified commit, *including its entire inspected changed-file inventory*, not merely authorize a vague class of changes. Preserve actual relevant history references. Use the existing required `limits` with null values when inapplicable, and empty failed/uncertain-attempt arrays. The event maintains the current workflow stage.

The existing task-log event schema already supports operation and scope strings, and both native integrations can record ordinary user-authored events. Prefer reusing it without introducing a new event, new role output, new persisted state field, sidecar audit ledger or migration format. A user instruction that unambiguously authorizes the exact existing commit and its contents should suffice; do **not** demand another user confirmation purely to manufacture procedural authority. If actual files or identity differ from the authorized description, do not infer permission from similarity.

Each external commit needs its own exact grant. There is no blanket approval for a branch, all documents in a folder, all commits from ChatGPT, a future range of SHAs or any later change by the same author. A denied/deferred decision is not a grant. Subsequent explicit withdrawals or changed decisions must retain the current checkpoint-boundary and forward-effect rules; stale grants must not override a newer applicable decision.

**Backward compatibility:** Keep the shipped `accept-spec-input-commit` operation functioning with its **original strict add-only proposal/bug-report validation**. Do not reinterpret an old grant for that operation as general acceptance of code, continuity files or mixed changes. A new `accept-external-commit` grant must be explicit and distinguishable. When both operations refer to one SHA, reconcile decisions unambiguously rather than exploiting an older or weaker grant to evade a later restriction.

### 2. Verify the full Git change without an arbitrary file-type whitelist

Only account for a commit when it is an ordinary **single-parent commit reachable through the active feature branch's first-parent history after its recorded baseline**, with its exact object ID and parent established from Git. Preserve existing branch/remote and Git-ownership checks. Do not accept a merge commit, a substituted hash, an unrelated branch, a rewritten cherry-pick, a history rewrite or a commit that masquerades as a Flow checkpoint by supplying partial/fictitious trailers.

Inspect the **entire parent-to-commit diff**, not just a user-mentioned file. Verify file paths, statuses, modes and object identities from Git (using robust handling of non-ASCII/path separators). The exception should be **independent of directory and document naming**: ordinary contained repository files may be added, modified or removed, including documents in `.docs/handoffs/` and user-authored source/tests. A rename must be completely accounted for as its actual tree change rather than silently ignored. No changes outside the explicitly accepted commit may piggyback on its authorization. A full SHA already commits to the tree and blob content; avoid duplicating every blob hash or retaining a separate changed-file ledger.

**Safety boundary:** An external commit must not be permitted to substitute for an Orchestrator log checkpoint or silently rewrite the authoritative `task_log.json`, history or workflow authorization. Existing role-owned document/version/provenance checks, repository path containment, and rejection of unsupported Git object types remain in force. Symlinks, gitlinks/submodules or other unusual modes must not be automatically accepted by treating them like ordinary files; they require deliberate supported verification or remain out of scope for this patch. The inspection must be substantive and proportionate to the changed content, not a superficial match on filenames. Orchestrator may examine full SHA, parents and changed-file metadata under its existing metadata-only role; use an appropriate read-only delegate when interpreting code, documents, binary assets or other content is necessary to establish what the user actually authorized. An uninspectable or materially ambiguous change must not be silently trusted.

A mixed commit (e.g. a documentation file and a test correction) is **not intrinsically forbidden just because it mixes types**, provided the user knowingly authorizes **all** its changed files, each change can be verified, and subsequent content-specific workflow obligations are handled. Conversely, discovering extra files absent from the user's authorization remains grounds to stop and ask, not to broaden the grant. Avoid an endless succession of hard-coded `proposal-`, `bugreport-`, `continuity-` or source-file exceptions.

The checkpoint validator's job is to establish **Git accountability**, not that every kind of externally authored content has been accepted scientifically, architecturally or functionally.

### 3. Separate Git acknowledgment from workflow-stage authority

Recognizing a commit means **only** that this exact Git history has an authorized explanation. The commit must **not** appear in the collection of authentic Planner/Coder/Orchestrator artifact or log checkpoints, invent `Orchestrator-Invocation` trailers, supply role reports, change an artifact's approved version, or grant implementation/experiment permission.

| External change | Git acknowledgment | Content/workflow treatment |
| --- | --- | --- |
| Continuity handoff under `.docs/handoffs/` | Accept exact authorized commit; preserve document and history | **No automatic specification change, task transition or new scientific authority** |
| New proposal or bug report in a feature | Preserve current 2.1.2 path and allow a separately explicit general grant where appropriate | Route substantive changes through the ordinary Planner revision and approval gates |
| User-authored code/test correction | Account for Git identity and complete inventory | Must still undergo applicable implementation review/verification and honest author attribution; **not** fabricated as Coder output |
| Changed approved `requirements.md`, `design.md`, `tasks.md`, or experimental evidence | Do not conceal the actual change | Retain normal artifact ownership, content-version, evidence-integrity and approval constraints; require legitimate reconciliation/specification work before dependent continuation |

When the existing workflow has no supported path for directly admitting an externally authored code/spec change at its current stage, **acknowledging its Git commit must not be interpreted as permission to bypass the missing native stage**. Continue only work for which the current approved state and genuine evidence suffice; otherwise report that separate stage/review blocker. Full user-originated `change_wrapper`/`review_wrapper` handoffs, post-review re-entry, and stage-state extensions remain v2.2.0 candidates. This boundary is fundamental to keeping v2.1.3 a legitimate patch rather than implementing half the next release.

For the concrete F01 handoff, Git acknowledgment should restore the ability to append/publish normal workflow decisions while **leaving the unrelated A2 budget/scientific method-selection blocker and the current feature state untouched**. Reconciliation of a handoff commit is not approval to exceed A2 resources, perform new held-out evaluations, or change the scientific specification.

### 4. Preserve ordering, delivery, withdrawal and resumption invariants

Use the tested 2.1.2 acknowledgment sequence as the base:

1. Reconcile known workflow checkpoints and failed/uncertain pushes; verify current Git ownership/yield and exact external SHA, parent, full diff and user authority.
2. Append the user decision through existing authoritative log recording. The **candidate** acknowledgment must be able to validate before its own checkpoint is published, without creating a circular requirement for pre-existing durable authority.
3. Commit the decision as a genuine **Orchestrator log checkpoint after the external commit**, preserving existing log event IDs, history prefix, checkpoint ranges and earlier role outputs. A pre-existing intermediate log checkpoint must be reconciled, not rewritten or fabricated.
4. Publish and verify acknowledgment delivery on the actual remote feature branch **before dependent Planner or Coder publication**. An external commit already on the remote need not be pushed a second time.
5. Treat the acknowledged commit as accounted for on **all subsequent workspace, checkpoint, push-attempt, delivery and interruption/resume validations**, while continuing to reject unrelated external commits. Outgoing pushes that bundle later producer work cannot silently jump over an undelivered acknowledgment. Retain the existing rules for effective/withdrawn grants at committed boundaries, including failed/uncertain delivery recovery.

A bare external commit as HEAD is still **not a valid workflow checkpoint to push using the workflow's checkpoint attempt helper**. The valid outgoing tip is the subsequently created Flow log or role artifact checkpoint. Do not modify, amend, rebase, cherry-pick, recreate or force-push an existing user commit merely to attach Flow trailers. Do not convert a truthful later user decision into a retroactively fictional Coder/Planner act.

The repaired reader must resume **existing 2.1.1 and 2.1.2 logs**, including logs already using the exact-spec-input exception and historical `feature-relocated` paths, without rewriting their recorded `workflow_version`, completed work, previous grants, approvals or Git checkpoint identities. The user's original F01 continuity case is especially important: a documented, single-parent, add-only handoff commit immediately after a published blocked-state log checkpoint should be acknowledged via the normal existing user-decision event, then permit resumption **only of otherwise authorized work**.

### 5. Implement as a bounded extension and verify it on both platforms

The expected core changes are concentrated in **shared `scripts/checkpoint_state.py`**, extending the existing external-commit classification, exact-grant processing, whole-diff inspection and acknowledgment delivery logic. Update the relevant Codex and Claude Code Orchestrator/protocol guidance so the legitimate user acknowledgment can be recorded without guesswork. Reuse the current shared event schema, `workflow_protocol.py` reducer, Codex `record-handoff` and Claude `claude_log.py append-entry` unless a demonstrated failing case requires a specific extension. Keep the shared code and schemas **byte-identical** across the two supported integrations. Increment canonical `VERSION` to 2.1.3 when actually implementing/releasing, not when merely writing this proposal.

**Required regression evidence should include:**

| Case | Required outcome |
| --- | --- |
| F01-style add-only continuity Markdown commit outside the feature spec folder, single parent after a published checkpoint | Correct full-SHA grant validates, produces a durable log acknowledgment and permits subsequent normal checkpoint/resume validation |
| Existing 2.1.2 `accept-spec-input-commit` histories, including 2.1.1-origin logs | Preserve the original strict path and historical approvals with no rewrite |
| Legitimate user-authorized add/modify/delete of ordinary repository files | Correct Git accountability for each actual change type, without a filename whitelist or implicit content approval |
| Entirely identified mixed docs + code/tests commit | Git reconciliation may succeed with exact whole-commit authority; any required semantic review remains separate |
| User-supplied code changes that cannot enter the current native Reviewer/Coder stage | Commit may be accounted for, but unperformed review/approval is not invented and dependent completion cannot be falsely claimed |
| Nested consumer roots and previously authorized feature relocation | Correct ancestry and effective/historical paths; unmodified original checkpoint identity |
| Multiple external commits, existing log checkpoint between input and acknowledgment, and Codex/Claude recording | Each SHA needs individual authority; no duplicate event or fictitious role return |
| Already delivered input, committed acknowledgment, later producer checkpoint, failed/uncertain push | Correct remote-ancestry ordering and standard recovery without rewriting or re-pushing the input |

| Rejection case | Required outcome |
| --- | --- |
| Missing grant, partial/wrong SHA, branch mismatch, unaccounted additional commit or incomplete user-approved inventory | Reject; never accept a folder/author/range by implication |
| Denied/deferred/withdrawn scope, or a historical grant before the wrong commit | Reject reliance that lacks effective authority; preserve already established history |
| Merge, unverified symlink/submodule, malformed/pretended Flow trailers or uninspectable/ambiguous changes | Do not treat as an ordinary authorized commit |
| Attempted external edit to `task_log.json` or bypass of role-owned artifact validation | Reject; preserve real log and approval provenance |
| Acknowledgment after unauthorized dependent producer publication, or unacknowledged commit as a push tip | Reject; no retroactive or implied role authorization |
| A valid but unfavorable experiment or a new budget/method authorization hidden in a continuity file | No scientific or operational permission is conferred by Git acknowledgment |

Preserve existing positive and negative tests from `tests/test_spec_input_commits.py`, checkpoint/delivery/recovery and relocation tests, Codex/Claude shared-runtime parity, and relevant native-recording tests. Add targeted tests rather than a new test orchestration subsystem. Run the full available suite and report environment limitations accurately (in particular, the previously observed Windows POSIX startup-fixture failures must not be counted as clean passes).

### 6. Non-goals and patch boundary

**Do not implement** the broader v2.2.0 features merely to recognize external Git history: user-authored `change_wrapper` or `review_wrapper` events, new Reviewer/Coder re-entry paths, changed stage transitions, generalized assessment agents, dedicated Orchestrator helper capability, new Autonomy levels, redesigned task-log readability, or a separate approval/audit database. These remain independent future design choices.

This proposal is **not authority to modify the consuming music-analyzer project**, change its scientific budgets or methods, edit its task log, rewrite the continuity commit, or start its stopped experimental work. It also does not authorize modifying shared Orchestrator Flow runtime code before the patch is separately selected for implementation. GitHub Copilot and Cursor remain deferred.

The goal is a durable answer to the recurring *external Git commitment* defect while retaining every substantive workflow safeguard. If implementing safe generalized recognition proves to require major changes to native stage and approval semantics, disclose that dependency and reconsider patch scope instead of silently weakening controls or implementing the remainder of v2.2.0.

## Questions

The user has selected the **direction** of this proposal: generalize exact, explicitly authorized external Git commit reconciliation instead of adding a third special filename/path exception, while keeping workflow-stage re-entry outside this patch. The proposed new operation name `accept-external-commit` is a working choice consistent with the existing event schema; verify that it composes unambiguously with the released `accept-spec-input-commit` and its withdrawal semantics.

The technical design still needs to settle how far ordinary regular-file changes (including deletions, renames represented as tree changes, and nontext blobs) can be inspected and accepted safely without expanding the state machine, and how to make **unreviewed content changes incapable of falsely satisfying existing approval/completion gates**. Preserve these as real design obligations for the implementing Planner/Architect or code review rather than hand-waving them away. If those boundaries cannot be met with a small extension, report the concrete blocker and request direction before implementation.

No user decision about new scientific execution, resource increases or the other v2.2.0 improvements is implied by this proposal.

## References

- `AGENTS.md` — native integration boundaries, shared-runtime byte parity, symlink installation and change/testing rules.
- `templates/proposal-template.md` — canonical standalone proposal format, including removal of authoring instructions from completed inputs.
- `.docs/v2.1.2/proposal-v2.1.2-authorized-spec-input-commits.md` — released narrow exception, its original rationale, invariants and explicit non-goals; v2.1.3 must preserve old grants.
- `.codex/skills/orchestrator-flow/references/workflow-protocol.md` and `.claude/skills/orchestrator-flow/references/workflow-protocol.md` — true user decisions, feature scope, existing spec-input acknowledgments and checkpoint delivery.
- `.codex/skills/orchestrator-flow/references/orchestrator.md`, `.codex/skills/orchestrator-flow/references/workflow-recovery.md`, and their Claude Code counterparts — orchestration boundaries, native role accountability, failure/recovery and permission limits.
- `.codex/skills/orchestrator-flow/references/task_log_schema.json` — existing `user-authorization-recorded` with `external_operation`, user statement, scope and null-capable limits.
- `.codex/skills/orchestrator-flow/scripts/checkpoint_state.py` — exact external commit verification, authentic Flow checkpoint classification, acknowledgment chronology and publication checks.
- `.codex/skills/orchestrator-flow/scripts/workflow_protocol.py`, `.codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py` and `.claude/skills/orchestrator-flow/scripts/claude_log.py` — current event replay, candidate validation, workspace checks, and native log writers.
- `tests/test_spec_input_commits.py`, `tests/test_checkpoint.py`, `tests/test_relocation.py`, `tests/test_claude_runtime.py`, `tests/test_runtime_parity.py` — acceptance/rejection, delivery, provenance, recovery and both-platform parity coverage.
- [Music Analyzer F01 continuity handoff](https://github.com/namitkaura/music-analyzer/blob/f01-trustworthy-temporal-measurements/.docs/handoffs/music-analyzer-continuity-002.md) — concrete repository-wide documentation input whose verified ordinary Git commit triggered the 2.1.2 limitation.
