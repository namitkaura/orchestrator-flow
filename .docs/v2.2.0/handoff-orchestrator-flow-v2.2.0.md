# Handoff: Orchestrator Flow v2.2.0

Start the next release here. It is v2.2.0 unless the task-log schema changes in a non-backwards-compatible way. In that case it becomes v3.0.0, and this folder and file are renamed during planning.

These items were found or deferred while releasing v2.1.0, or carried forward from v2.0.0. The evidence behind them is in the [v2.1.0 native-test summary](../v2.1.0/native-test-summary.md). The last two sections hold lessons for running the next release and the transcript facts the recorder items rely on.

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
   - a contract option to ask in plain text when the user has delegated decisions, then a test of whether Orchestrator honours labelled delegated decisions
   - an Agent SDK host program that answers dialogs in code, if the SDK supports that, which hasn't been checked
8. **Not yet covered natively.** Each of these has deterministic tests, but no native run has shown it. The [Claude native test](../../tests/live/claude/README.md) can cover several of them in its next run:
   - the `flow-explorer` helper, which neither native feature needed
   - the plain final-message report form, because every return used SubagentHandback
   - a tool call interrupted inside a lead after a resume, the Claude Code 2.1.296 fix; in run 2 the Coder was waiting, not mid-call
   - `find-agent` choosing between two sessions' leads with the same feature and invocation; run 2 got a different invocation from run 1
   - the desktop app as the workflow host, since both native runs used the CLI
   - an Opus Orchestrator after the step-4 checklist fix; before it, Opus left out the per-choice reasons until asked

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

    Choose proportionate coverage. A full matrix isn't the default response to every kit fix (§8).

## Platforms

11. **Windows.** Claude Code setup on Windows, and a native test from PowerShell, aren't covered yet.
12. **Copilot and Cursor.** Their v2 updates remain deferred, as set out in `AGENTS.md`.

## Lessons for running the next release

- **Carry the v2 baseline forward.** The [v2.1.0 handoff](../v2.1.0/handoff-orchestrator-flow-v2.1.0.md)'s settled behaviour (§3), implementation boundaries (§4) and test-kit intent (§8) still apply. Don't reopen settled decisions. Perfection is the enemy of good.
- **Test natively early, and compare runs.** Three contract assumptions failed only on real runs:
  - the symlink allow-rule behaviour
  - helpers running asynchronously under background leads
  - a model following `SKILL.md` by hand when a slash command didn't run as one

  Comparing run 1, which passed an explicit `run_in_background: false`, with run 2, which omitted it, is what separated platform behaviour from model behaviour.
- **Verify documentation claims natively** when users will follow them. Part D confirmed the README's auto-mode `Read` rules this way.
- **Keep review separate from implementation.** A review thread that checked every diff and claim against the files and transcripts caught a confirm-first condition that would have fired on every typed run, and a misread finding.
- **Messages between threads need care.** They're delivered only when the receiving thread's turn ends, and can't be recalled once queued. Agree on the content before sending; "yes, but…" is still discussion. A hold must arrive before the work starts. In this release, a reorganization was done, undone and redone because a hold and an undo were queued behind work already under way.
- **Commit shared files in order.** When several pending changes touch the same files, commit them in order and apply later edits only after the earlier commit. Then no commit links to a file that doesn't exist yet.

## Reference: transcript structure the recorder relies on

These hold for items 4 and 5, and were verified on real transcripts during v2.1.0.

- **Where a run starts:** at a user prompt that isn't `isMeta`, or at an `isMeta` user record whose `origin.kind` is `coordinator` (a SendMessage continuation) or `peer` (a helper's hand-back). Harness nudges are `isMeta` with no `origin`.
- **How a message is recorded:** one record per content block, all sharing `message.id`. The final record carries `stop_reason: "end_turn"`, while `max_tokens` marks a cut-off.
- **Hand-backs and refusals:** a SubagentHandback's tool result is `{"success": true, …}`, and refusals set `is_error`.
- **Async helpers:** the launch's tool result carries `toolUseResult.status: "async_launched"` and the `agentId`. The hand-back arrives with `origin.from` set to that ID.
- **Large outputs:** tool results over 50,000 characters are saved to the session's `tool-results/` folder, and the model gets a 2 KB preview.
- **Background notices:** the desktop app XML-escapes their text. The CLI delivers them as `<task-notification>` entries in `queue-operation` records.
