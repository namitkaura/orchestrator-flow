# Proposal: Orchestrator Flow v2.1.2 — Authorized Specification Input Commits

## Problem Statement

### User-authored proposal commits block legitimate specification revisions

Orchestrator Flow 2.1.1 requires every commit after a feature's recorded Git baseline to carry recognized Orchestrator checkpoint trailers. The shared `scripts/checkpoint_state.py` `workflow_checkpoints()` rejects an ordinary commit as unaccounted-for, even when the user deliberately published a new proposal or bug report on the active feature branch as input to a normal Planner-led specification change. The same check is used by workspace validation and checkpoint/push inspection. The task log can be semantically valid while checkpoint delivery remains blocked; merely adding a subsequent Orchestrator checkpoint does not account for the earlier ordinary commit.

This has occurred on more than one consumer feature. During the FEC-bot v2.0.1 work, a user-authored commit introduced a proposal and bug-report document, and a manual, explicitly authorized workaround was needed. In the later music-analyzer F01 feature, the user published a follow-up proposal at `music-analysis-research/.docs/specs/f01-trustworthy-temporal-measurements/proposal-f01-trustworthy-temporal-measurements-followup.md`. The Planner's read-only assessment correctly identified Requirements as the first artifact to revise, but the ordinary proposal commit prevented checkpoint validation and therefore blocked the formal revision. The proposal is a specification *input*, not Planner-authored requirements or a code checkpoint.

The user wants to resume the existing F01 flow without rewriting its Git history, losing its earlier approvals/completed Stage A work, or allowing an unrelated commit onto a checkpoint push. The broader v2.2.0 plan already addresses general external Git reconciliation and user-originated workflow re-entry. Implementing that full system just to accept an added proposal document would be inappropriate for a 2.1.2 patch.

### The existing authorization event provides a smaller route

The 2.1.1 task log already has `user-authorization-recorded` with `kind: external_operation`, `decision`, `operation`, `scope`, `user_statement`, `references` and bounded limits. The reducer preserves the current workflow stage for this event. The schema allows an operation name and scope string, and both Codex and Claude Code can append user decisions through their existing mechanisms. This enables a narrowly scoped acknowledgment without inventing a new stage, event, wrapper, or migration format.

## Proposed Solution

**Accept only an explicitly user-authorized, add-only Git commit containing specification input Markdown documents for the active feature.** Record the user decision in the existing authoritative task log, validate the exact Git commit and changed files, and exempt that verified input commit from the *checkpoint-trailer requirement only*. All ordinary Flow checkpoints, approvals, role handoffs, Git delivery rules and unrelated-commit rejection remain intact.

### 1. Record one bounded user authorization using an existing event

Use the existing `user-authorization-recorded` event with `actor: User`, `requestor: User`, `kind: external_operation`, `operation: accept-spec-input-commit`, `decision: granted`, and `scope` equal to the **full, resolved Git commit object ID**, not an abbreviated hash, branch name, path, free-form list, or range. Preserve the actual user statement authorizing this exact input; include existing event references when appropriate. The pre-existing required `limits` fields remain present with null values when inapplicable, and push-failure arrays remain empty. No task-log schema alteration or new event type is proposed.

The grant is a bounded acknowledgment of the specified commit's **input provenance**, not authorization of an arbitrary external operation. A later explicit denied/deferred decision for the same operation and commit must not be overridden by an older grant. Missing, malformed, ambiguous, conflicting or unrelated authority must fail closed. The same user instruction may supply the authority if it unambiguously identifies the actual commit and intended documents; do not demand another ritual approval solely because the user used an external authoring thread. The Orchestrator must inspect and identify the actual Git commit and changed-file inventory, not infer authority from a commit message.

Keep the normal `user-change-requested` record and ordinary Planner revision path for the substantive spec change. If the change request is already recorded, append only the needed acknowledgment; do not duplicate the change request, reset the Planner assignment, or rewrite earlier log entries. If it is not yet recorded, preserve the user's request through the normal existing event sequence. This acknowledgment never acts as spec approval, coding authorization or a replacement for a Planner/Architect return.

### 2. Verify the exact, narrowly allowed Git content

The shared checkpoint reader should distinguish a recognized Flow checkpoint from a *specification input commit* only when an effective grant matching its full object ID exists in the current validated append-only task log. For that exception, enforce all of the following:

- The commit is present on the current feature branch after the recorded baseline, reachable through its ordinary first-parent history, and is a normal **single-parent** commit; no merge, rebase, cherry-pick rewriting, history graft, or unrelated branch acceptance.
- Its **entire changed-file inventory** consists exclusively of newly added regular Markdown proposal/bug-report documents (for example filenames beginning `proposal-` or `bugreport-` and ending `.md`). Require an ordinary regular-file Git mode; reject symlinks, submodules, binary files, deletions, modifications, renames and extra changes to code, tests, generated evidence, log files, approved specifications or configuration.
- Each added document is located **inside the active feature's recorded `.docs/specs/{feature}/` directory**, including an allowed nested project root. Resolve the effective historical feature directory when authorized `feature-relocated` events are already present; do not assume the feature lives at repository root.
- The exact commit and all of its files must be in the user's accepted scope. The Orchestrator can inspect SHA, parents, modes, changed paths and statuses as metadata; delegate substantive document-content inspection to Planner or an appropriate read-only role, respecting the existing metadata-only Orchestrator boundary.
- An unrecognized commit, nonmatching path or content type, absent/revoked grant, extra file, wrong feature/branch, or ambiguous historical order remains **unaccounted-for** and blocks normal validation and publication. There is no automatic acceptance of everything under a spec folder.

The full commit object ID already binds the Git tree and document contents; do not store duplicate hashes, invented Planner publication trailers, an external-commit inventory ledger or a second audit file. A commit can add more than one qualifying proposal/bug-report input, provided *every* changed file satisfies the same checks and the user's authorization covers the complete commit. Updating or moving a previously committed input document through an ordinary external commit is **not** included in this patch.

### 3. Preserve checkpoint ordering and successful recovery

An authorized input commit is **not** an Orchestrator artifact/log checkpoint and must not appear in the workflow-checkpoint results used to validate producer handoffs, event ranges, publishing role, completion or delivery. It only ceases to be an unexplained commit in the baseline-to-HEAD traversal. Existing checkpoint trailer and historical task-log correspondence checks apply unchanged to every real Flow checkpoint.

The user decision must be added to the authoritative log, validated and delivered as a **normal Orchestrator log checkpoint before further dependent Planner/Coder publication**. For a candidate log whose input-acknowledgment event has not yet been checkpointed, allow workspace validation to use that candidate authorization so the normal log checkpoint can be created; do not create a circular demand for a pre-existing acknowledgment checkpoint. Once committed, verify the acknowledgment is on the proper ancestry *after* the input commit, not an attempt to pre-authorize a future unknown SHA or retroactively excuse unrelated producer work. If a prior failed validation left a log checkpoint locally committed after the input, reconcile its actual state and recorded events rather than rewriting it or fabricating a producer return.

`validate_workspace()`, `checkpoint_state.py inspect`, `attempt`, delivery/recovery checks and later resumption must all agree about the accepted input commit. Normal pushes still require HEAD to be an actual validated Flow checkpoint, and the existing attempt journal, remote-ancestry verification, one-push authorization and failed/uncertain delivery safeguards remain in force. No duplicate push is needed when the user already published the input; publish the subsequent log and Planner checkpoints normally.

The repaired runtime must resume **existing 2.1.1 feature logs without changing their recorded `workflow_version`, approved artifact versions, prior completed tasks, wrappers, historical checkpoint SHAs or feature identity**. It must also retain v2.1.1 path-relocation behavior. If the specific run has an unknown/unpublished checkpoint state, use the established recovery procedure first; the exception never grants permission to skip that reconciliation.

### 4. Keep the change small and verify both native integrations

The expected functional change is concentrated in the shared `scripts/checkpoint_state.py` checkpoint classification/verification and the small amount of shared or platform-specific guidance necessary to record this existing authorization operation. Use the existing replay/schema contract and the existing Codex log validator and Claude `claude_log.py append-entry` writer; **do not add a new recorder, event kind, persisted registry or migration subsystem merely for this scenario**. Revise those components only if a concrete test proves a necessary gap. Bump the canonical `VERSION` to 2.1.2 when the patch is implemented and keep both supported integrations' shared runtime files byte-identical, as required by `tests/test_runtime_parity.py`.

The implementation's tests should cover at least:

| Positive scenario | Required outcome |
| --- | --- |
| Existing feature, one user-published added proposal, explicit matching grant | Log candidate validates; normal log checkpoint and push/resume can follow |
| Existing feature, one commit adding a proposal **and** a bug report, both authorized | Both inputs accepted without treating either as Flow checkpoints |
| Existing 2.1.1 log containing a prior `user-change-requested` and blocked checkpoint state | Append acknowledgment without rewriting or duplicating history; continue correct Planner stage |
| Nested feature path and a feature with authorized relocation history | Correct current/historical scope without weakening relocation validation |
| Codex and Claude recording paths | Same effective authorization and validation, with no new native-agent return format |
| Already published input commit followed by a normal log checkpoint | Delivery and later resumption work through existing remote-ancestry checks |

| Negative scenario | Required outcome |
| --- | --- |
| No grant; wrong or abbreviated SHA; denied/deferred/revoked grant | Still rejected as unaccounted-for |
| Mixed proposal plus code/test/config/log/spec edit; modified/deleted/renamed input | Rejected, even if user authorizes the commit generally |
| Input outside the permitted feature directory; wrong branch; symlink/submodule; merge commit | Rejected |
| Attempted direct push with input commit as HEAD and no Flow checkpoint | Rejected |
| Historical grant appearing only after unrelated producer publication | Does not retrospectively legitimize that publication |
| User authorization recorded but proposal's contents unapproved | Normal requirements/design/tasks and Architect approvals remain mandatory |
| Failed/uncertain checkpoint push after accepted input | Existing pause, recovery authorization and retry bounds remain unchanged |

Exercise both the focused existing checkpoint/recovery/relocation and Claude-recorder tests and the repository's broader suite where the environment permits. Retain the repository's known Windows fixture limitations as separate evidence; do not claim a clean full run merely because relevant targeted tests pass. Update the Codex/Claude Orchestrator and workflow protocol guidance sufficiently that an agent can perform the accepted operation without improvising the event, bypassing validation or starting work before checkpoint delivery.

### Non-goals

This patch does **not** accept externally authored product code, tests or corrections; invent `change_wrapper` / `review_wrapper` returns for the User; introduce Reviewer→Coder or user→Reviewer re-entry; change the five-role workflow, task-log readability or wrapper schemas; add the prospective Orchestrator helper capability; or generalize reconciliation to arbitrary external commits. Those belong to the separately planned v2.2.0 improvements.

It does not authorize changes in the music-analyzer repository, rewrite its proposal commit, edit preserved Stage A evidence, modify approved F01 scientific scope, create extra historical log files, or perform the patch implementation before the user chooses to proceed. Deferred Copilot and Cursor integrations remain untouched.

## Questions

No additional product-level decision is required to **propose** this narrow patch: the immediate need is to recognize explicitly user-authorized, add-only specification inputs while preserving the existing stage and checkpoint rules. During planning or implementation, verify that the affected consumer input actually meets the constrained Git/file rules and that the candidate authorization can be recorded with the existing writers. If it does not, report the specific mismatch and obtain direction; do not silently expand the exception into general external-commit reconciliation. Any technical complication that substantially broadens state or schema changes should trigger reconsideration of whether a 2.1.2 patch is still appropriate.

## References

- `AGENTS.md` — repository change boundaries, source installation, shared runtime parity, testing rules and deferred integrations.
- `templates/proposal-template.md` — canonical standalone proposal structure and authoring requirements.
- `.codex/skills/orchestrator-flow/SKILL.md` and `.claude/skills/orchestrator-flow/SKILL.md` — native skill entry points and role boundaries.
- `.codex/skills/orchestrator-flow/references/orchestrator.md`, `.claude/skills/orchestrator-flow/references/orchestrator.md` — metadata-only orchestration, existing log decisions and native handoffs.
- `.codex/skills/orchestrator-flow/references/workflow-protocol.md`, `.claude/skills/orchestrator-flow/references/workflow-protocol.md` — spec revision, event ownership, checkpoint delivery, reconciliation and authorized feature relocation.
- `.codex/skills/orchestrator-flow/references/workflow-recovery.md`, `.claude/skills/orchestrator-flow/references/workflow-recovery.md` — existing commit/delivery inspection and bounded recovery.
- `.codex/skills/orchestrator-flow/references/task_log_schema.json` — existing `user-authorization-recorded` and `external_operation` fields (shared with Claude).
- `.codex/skills/orchestrator-flow/scripts/workflow_protocol.py` — event replay, append-only history, feature directory and state transitions (shared).
- `.codex/skills/orchestrator-flow/scripts/checkpoint_state.py` and `.codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py` — strict commit traversal, workspace/handoff checks and delivery validation (shared).
- `.claude/skills/orchestrator-flow/scripts/claude_log.py` — existing Claude Code `append-entry` writer for user decisions.
- `tests/test_checkpoint.py`, `tests/test_relocation.py`, `tests/test_protocol.py`, `tests/test_recovery_and_reviews.py`, `tests/test_claude_runtime.py`, `tests/test_runtime_parity.py` — relevant regression and native-parity coverage.
- `.docs/v2.0.0/proposal-orchestrator-flow-v2.0.0-corrections.md` — established correctness/preservation and proportionate recovery principles.
