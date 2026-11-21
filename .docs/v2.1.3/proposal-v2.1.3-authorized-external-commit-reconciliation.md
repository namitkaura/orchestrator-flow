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

The immediate objective is consequently **general, tightly authorized Git reconciliation without a wholesale rewrite of workflow states or agent return contracts**. The exception should be narrow in **authority and verified commit identity**, not in arbitrary document names. The workflow mostly serves the user's personal projects, so **simplicity and forward progress take priority over exhaustive preventive checks**. Introduce validation only when it addresses a concrete risk of materially breaking the workflow.

## Proposed Solution

Extend the existing v2.1.2 acknowledgment machinery to account for **individually identified, user-authorized external Git commits** regardless of whether their ordinary repository files are proposals, continuity documents, source/test changes or binaries. Preserve genuine Git history, existing user authorization, and meaningful checkpoint/log integrity. **Do not add new artifact-provenance checks, stale-review detection, generalized content analysis, or approval machinery.** A Git acknowledgment does not grant workflow-stage approval.

### 1. One explicit, durable user decision per external commit

Use the existing `user-authorization-recorded` event (`actor: User`, `requestor: User`, `kind: external_operation`) with a distinct, clearly named operation such as **`accept-external-commit`** (working name) and a `scope` containing the **full resolved Git commit object ID**. The user statement must genuinely authorize the identified existing commit and its full Git changed-file inventory, rather than a vague class of future changes. Preserve actual relevant history references. Use the existing required `limits` with null values when inapplicable, and empty failed/uncertain-attempt arrays. The event maintains the current workflow stage.

The existing task-log event schema already supports operation and scope strings, and both native integrations can record ordinary user-authored events. Prefer reusing it without introducing a new event, new role output, new persisted state field, sidecar audit ledger or migration format. A user instruction unambiguously authorizing the exact existing commit suffices; do **not** require new approvals or substantive inspection of each file merely to establish permission. If the SHA or inventory contradicts the user's description materially, ask rather than guessing.

Each external commit needs its own exact grant. There is no blanket approval for a branch, all documents in a folder, all commits from ChatGPT, a future range of SHAs or any later change by the same author. A denied/deferred decision is not a grant. Subsequent explicit withdrawals or changed decisions must retain the current checkpoint-boundary and forward-effect rules; stale grants must not override a newer applicable decision.

**Backward compatibility:** Keep the shipped `accept-spec-input-commit` operation functioning with its **original strict add-only proposal/bug-report validation**. Do not reinterpret an old grant for that operation as general acceptance of code, continuity files or mixed changes. A new `accept-external-commit` grant must be explicit and distinguishable. When both operations refer to one SHA, reconcile decisions unambiguously rather than exploiting an older or weaker grant to evade a later restriction.

### 2. Verify actual Git history without an arbitrary file-type whitelist

Reuse the v2.1.2 Git commit reader and checkpoint logic. Require an **existing full SHA**, its actual **single parent**, and ancestry on the active feature branch's first-parent history after its recorded baseline. Read the **complete parent-to-commit Git inventory** (changed paths, statuses, modes and Git objects) rather than only a user-mentioned filename. The SHA identifies immutable tree content; check the relevant changed-file list against the user's authorization. Reuse existing branch, ownership, genuine-checkpoint and Git-delivery safeguards.

For `accept-external-commit`, accept ordinary contained regular files **regardless of path, extension or whether their contents are text or binary**. Additions, modifications, deletions, executable-bit changes, and mixed documents/source/tests are in scope. Account for a rename through its actual before/after Git change; do not build special filename exceptions. Git object identity is sufficient to establish which bytes belong to the commit. **Do not require forensic binary inspection, semantic reading of every blob, or a new binary-analysis capability.** An existing read-only tool/role may inspect content if necessary to resolve an actual ambiguity about what was authorized; absent such ambiguity, avoid another gate. If the SHA or complete inventory materially differs from what the user authorized, stop for clarification.

Retain only the existing protections that prevent **material workflow breakage**: an external change cannot masquerade as an authentic Flow checkpoint or edit the authoritative `task_log.json` (including its recorded historical location) outside the normal log-checkpoint process. Keep unsupported Git modes such as symlinks/gitlinks out of this patch rather than designing special handling. **Do not add new provenance scans or mandatory content inspection** for otherwise authorized ordinary files.

Continue to support the shipped `accept-spec-input-commit` operation with its original strict add-only UTF-8 proposal/bug-report and historical directory checks. A legacy grant remains narrow; only the new operation authorizes general Git reconciliation.

### 3. Acknowledge Git history without changing workflow authority

Reconciliation establishes **only that the exact external commit is accounted for**. It does not create a Planner/Coder handoff, approval, test result, reviewed implementation, completed task or authorization for new experiments. Do not invent role outputs, source authorship, task-log history or checkpoint trailers.

- An **F01 continuity handoff** requires no automatic stage change. The independent A2 scientific/budget blocker remains in effect.
- A **user-authored proposal or bug report** still follows existing Planner decisions and specification approvals when its contents are to be acted upon.
- **Code, tests, specifications and evidence** do not become Planner/Coder-authored or Reviewer-approved merely because their Git commits are recognized. Normal role and approval responsibilities remain unchanged.

**Do not introduce new automatic artifact byte-provenance comparisons, stale-review/evidence detectors, broad change-impact analysis, or additional approval gates for v2.1.3.** Existing workflow processes should handle substantive decisions when they arise. If an external change requires a role transition not currently supported, identify that separate issue for v2.2.0 instead of turning reconciliation into an approval-enforcement redesign. Git acknowledgment itself gives no new scientific permission.

### 4. Preserve ordering, delivery, withdrawal and resumption invariants

Use the tested 2.1.2 acknowledgment sequence as the base:

1. Reconcile known workflow checkpoints and failed/uncertain pushes; verify current Git ownership/yield and exact external SHA, parent, full diff and user authority.
2. Append the user decision through existing authoritative log recording. The **candidate** acknowledgment must be able to validate before its own checkpoint is published, without creating a circular requirement for pre-existing durable authority.
3. Commit the decision as a genuine **Orchestrator log checkpoint after the external commit**, preserving existing log event IDs, history prefix, checkpoint ranges and earlier role outputs. A pre-existing intermediate log checkpoint must be reconciled, not rewritten or fabricated.
4. Publish and verify acknowledgment delivery on the actual remote feature branch **before dependent Planner or Coder publication**. An external commit already on the remote need not be pushed a second time.
5. Treat the acknowledged commit as accounted for on **all subsequent workspace, checkpoint, push-attempt, delivery and interruption/resume validations**, while continuing to reject unrelated external commits. Outgoing pushes that bundle later producer work cannot silently jump over an undelivered acknowledgment. Retain the existing rules for effective/withdrawn grants at committed boundaries, including failed/uncertain delivery recovery.

A bare external commit as HEAD is still **not a valid workflow checkpoint to push using the workflow's checkpoint attempt helper**. The valid outgoing tip is the subsequently created Flow log or role artifact checkpoint. Do not modify, amend, rebase, cherry-pick, recreate or force-push an existing user commit merely to attach Flow trailers. Do not convert a truthful later user decision into a retroactively fictional Coder/Planner act.

The repaired reader must resume **existing 2.1.1 and 2.1.2 logs**, including logs already using the exact-spec-input exception and historical `feature-relocated` paths, without rewriting their recorded `workflow_version`, completed work, previous grants, approvals or Git checkpoint identities. The user's original F01 continuity case is especially important: a documented, single-parent, add-only handoff commit immediately after a published blocked-state log checkpoint should be acknowledged via the normal existing user-decision event, then permit resumption **only of otherwise authorized work**.

### 5. Small extension and focused verification

Concentrate changes in shared `scripts/checkpoint_state.py`. Recognize the new exact-SHA authorization alongside the existing narrow spec-input operation; reuse its historical-grant precedence, pending candidate, delivery ordering and failed/uncertain push recovery. Update relevant Codex/Claude Orchestrator and protocol guidance. Reuse existing event schema, reducer and native recorders unless a concrete functional failure proves a change necessary. Keep shared runtime copies byte-identical. Update canonical `VERSION` to 2.1.3 during implementation/release.

**Required focused scenarios:**

| Scenario | Expected result |
| --- | --- |
| **F01 regression:** a published single-file `.docs/handoffs/` continuity commit after a blocked-state Flow checkpoint | Exact general authorization validates, is durably logged in the next authentic Orchestrator checkpoint, is published and survives resume; original F01 state/scientific limits remain |
| Missing, partial or wrong SHA; denied grant; otherwise unaccounted-for commit | Rejected |
| Ordinary authorized files, including a binary and a mixed documentation/test commit | Accepted without a filename whitelist, forensic inspection or invented content approval |
| Existing v2.1.2 narrow input grants and v2.1.1/2.1.2-origin logs | Original meaning, prior approvals and working feature history preserved |
| Normal checkpoint and delivery handling | External SHA is not an authentic Flow checkpoint; task-log tampering remains rejected; dependent publication respects acknowledgment delivery |
| Both supported integrations | Codex/Claude recording and shared-runtime parity remain functional |

Reuse the current spec-input, checkpoint, relocation and delivery tests. Add **only focused tests demonstrating the new operation and material failure cases**, not an exhaustive combinatorial matrix or speculative evidence-integrity subsystem. Run existing Python tests and parity/resource checks and inspect the actual diff; report real pass/failure/skip counts and baseline Windows-fixture failures accurately.

### 6. Non-goals and patch boundary

Do not implement v2.2.0's user-originated `change_wrapper`/`review_wrapper` paths, Reviewer/Coder stage re-entry, generalized artifact-provenance checks, stale-review detection, semantic code-impact analysis, helper agents, Autonomy settings, task-log redesign or a new reconciliation ledger. Do not create an approval process around every authorized Git change. These are predominantly personal projects; **the workflow should enable progress, not police hypothetical inconsistencies**.

This proposal does **not** authorize changing `music-analyzer`, its F01 budget or scientific scope, task log, experimental work or original continuity commit, and does not authorize implementing the patch before the user directs it. Deferred Copilot/Cursor integrations remain out of scope.

**Only add a new validation for a demonstrated risk that could materially break the workflow or corrupt its history.** If a genuine blocker cannot be addressed without significant stage/schema changes, identify the exact case and seek direction rather than quietly expanding v2.1.3.

## Questions

The user has decided to keep v2.1.3 **minimal and pragmatic**. Use `accept-external-commit` for the exact authorized SHA; preserve `accept-spec-input-commit` unchanged for old grants. Ordinary binary content is permitted without a new forensic inspection requirement; use existing read-only inspection only for a concrete ambiguity.

The implementation should settle only the necessary integration of the new decision with existing commit classification, grant precedence, checkpoint acknowledgment and delivery. **Preventing every hypothetical stale review or content inconsistency is not a v2.1.3 requirement.** If an essential workflow integrity safeguard demonstrably needs additional machinery, identify the exact failure before proposing it.

This proposal does not approve new scientific execution, resource increases or separate v2.2.0 improvements.

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
