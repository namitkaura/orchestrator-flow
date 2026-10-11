# Recovery and exceptional evidence assessment

Read when work is interrupted, delivery fails, a role fails, or evidence applicability cannot be established. Normal execution and ownership remain in `workflow-protocol.md`.

On failed push, preserve the commit, record failure immediately, report it, globally pause workflow work, and obtain direction. An interrupted attempt with no recorded result also pauses work until Git establishes delivery or the user gives direction. `inspect` returns an `uncertain_attempt` suitable for recording with that decision when delivery cannot be established; it does not fabricate a failure or grant a retry. On an authorized retry:

1. Append `user-authorization-recorded` with the actual latest failed-push or uncertain-attempt context, target operation, and `max_attempts: 1`. Use `failed_attempts` for a recorded failure or `uncertain_attempts` for the interrupted started record and current observation. A later recovery decision supersedes an earlier one.
2. Validate and commit that update locally before retrying. Recovery bookkeeping is allowed during the pause; product/spec work is not.
3. Persist the attempt identity before invoking one push that delivers the outstanding work and authorization together.
4. Determine successful delivery from Git remote ancestry and commit trailers. Create no success event, success receipt, extra commit, or second push.
5. If it fails, persist the new failure locally and pause again. If it is interrupted without a known result, retain its started record and reconcile Git. The next user-directed recovery update carries the new failure or uncertainty into the task log before another attempt; citing an older attempt cannot authorize this retry.

The final checkpoint follows exactly this sequence. Once Git proves delivery of acceptance and any recovery authorization, produce the squash message with no pending receipt or extra approval. If interrupted before dispatch or after sending a push, inspect Git before repeating it. If the outcome cannot be established, ask for direction; a fresh explicit one-push authorization can permit another attempt without pretending the earlier one failed. An uncertain attempt consumes its recorded authorization and never replenishes it. Commit failures block dependent work. Push failures globally pause work even when offline tasks would otherwise be independent.

Recover running role work or completed output before dispatching a duplicate writer. Use trigger/role/attempt and native context IDs. Retain producer context across artifact checkpoints and coherent yields for log updates. New invocations receive the full role contract, effective configuration, current artifact/approval context, relevant prior output and bounded durable evidence, not the entire history by default.

On resume inspect recorded branch/baseline, current HEAD, staged/unstaged/untracked names/statuses, native liveness/output/user messages and concise validators. `checkpoint_state.py recent <log> --repo <root> --limit 20` returns commit metadata, changed names/statuses and `next_cursor`; pass `--cursor` to continue when relevant history remains unaccounted for. HEAD changes invalidate the cursor. No patches/bodies are returned. A commit message cannot establish approval, completion or a wrapper. Delegate content questions and request bounded findings, preserving context where available.

Recover an actual unrecorded return or user approval once, validating its original scope/version before recording and checkpointing. A recorded document awaiting approval is presented without regenerating it. Delivered artifact work awaiting a required handoff needs the owner's actual return. Active Coder work with checkpoints and no interim wrapper is normal: continue/recover the assignment, not a completion report or duplicate writer. Completed Coder work requires its cumulative return against the original assignment baseline; the owner reconstructs checkpoints/diffs, tasks, actual code and decisions, distinguishing historical checks from new runs. Read-only reconciliation itself creates no event/checkpoint.

## Local attempt evidence and inspection

Use `checkpoint_state.py inspect` and `recent` read-only. The append-only attempt journal is located through `git rev-parse --git-path orchestrator-flow/{feature}/checkpoint-attempts.jsonl`; never assume .git is a directory. Records preserve checkpoint kind, publishing role, invocation/phase, exact commit/event range, target, timestamp and authorization. Only artifact-only commits allow empty event IDs. Keep credentials out. This is operational evidence, not a pending-action field.

Validate log correspondence separately from artifact checkpoints. Legitimate artifacts may follow the latest delivered log and must be delivered too. Reject a push silently including unrelated unaccounted commits. Reconcile remote ancestry and previous attempts before another attempt; completed delivery requires neither another push nor a receipt. Recover uncommitted work without treating file presence or commit prose as user authority.

## Role failure and reporting correction

Use the original trigger, role, attempt and available native handle to recover running work or actual output before replacing a writer. Accepted capability changes apply prospectively at a coherent boundary. A replacement preserves assignment baseline, approvals, scope, repair counts and evidence. No execution-segment events or helper dispatch ledger.

A small missing path, unclear summary or similar report defect is corrected by the owner in the same assignment before the dependent gate. No failure record, attempt increment, empty artifact commit, repair cycle or automatic retest. Do not count corrections.

Actual execution failure, unusable output or repeated inability to supply a usable result uses subagent-error and the existing maximum of three total ordinary attempts while authorized. Record the actual invocation/requestor and evidence, then checkpoint before retry. At exhaustion obtain bounded direction. Model/usage unavailability requires immediate choice rather than substitution. A failed helper report identifies the actual helper, accepted model/effort and owning role; a helper-only change need not restart the lead.

A clipped native capture is not necessarily a producer failure: first recover the native output. `invalid_native_output` from the recorder prevents recording, but does not decide whether a small correction or genuine bounded failure applies. `recording_error` (concurrent log change, write/readback failure, wrong destination) belongs to Orchestrator. Correct from actual evidence without charging the producer. The helper does not claim crash-atomic storage. Reconcile interrupted unpublished writes with Git/native evidence. Published history stays append-only; truthful subsequent records may be used only where the existing contract supports them. Published corruption or uncertain prior authority stops for user-directed recovery; do not build a generic historical-repair process.

## Exact authority and scoped blockers

user-authorization-recorded defines kind (coding, repair_cycle, external_operation, checkpoint_recovery), operation, scope, decision, references, limits and actual user statement. Coding cites the current accepted spec review. Repair allowance cites the stage review (generic continue grants one additional cycle, never resets history). external_operation can explicitly authorize accept-check-result with check name as scope, accept-task-result with task ID, or bounded continue-role with original trigger as scope. Extra role attempts are bounded from failures already recorded at the decision.

For non-delivery blockers, pause only the affected operation/dependencies and continue approved independent work. Record task/operation IDs, reason, evidence, attempts, dependencies, remaining independent tasks and needed authority. Honor concrete request/retry/credential/deadline bounds where relevant, without imposing unrelated operational checklists. Failed checkpoint delivery is the global-pause exception.

## Evidence applicability

Derive stage sufficiency from all applicable accepted reviews: actual starting assurance, source handoff and published artifact commit, approved versions/scope, later changes, findings/dispositions and sources/assumptions. Do not consider only the latest review or last override. Maximum → Standard → Maximum on unchanged applicable work adds no gap. Log-only commits and checkbox accounting do not invalidate content evidence. Missing assurance still blocks; lower-assurance in-flight output cannot enable a higher gate. A gap in one stage does not create another.

Changed relevant content or assumptions require assessment or the necessary review. Earlier accepted evidence never bypasses a mandatory review of later changed work. If existing records establish unchanged applicability, do not add an event. Otherwise delegate a bounded content assessment to Architect/Reviewer and record review-evidence-assessed only when it affects a gate: referenced review, assessed current output/artifacts/commit/scope, conclusion applicable/inapplicable/uncertain, verifiable evidence and actual role context. It grants neither higher assurance nor acceptance and consumes no repair cycle. Unknown/insufficient applicability cannot enable work.

A catch-up review can temporarily enter an existing review state from interrupted work; restore that assignment on success, route findings through its own stage on failure. Get Coder's coherent yield before taking over review/Git coordination. Existing role context can perform the work; fresh Maximum review means comprehensive work, not a fresh agent.
