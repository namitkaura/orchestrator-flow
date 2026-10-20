# Orchestrator Flow v2.1.0 follow-ups

These items were found or deferred while releasing v2.1.0. They are inputs for the next release: v2.2.0, or v3.0.0 if the task-log schema changes in a non-backwards-compatible way. The evidence behind them is in the [native-test summary](native-test-summary.md).

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

## Platforms

9. **Windows.** Claude Code setup on Windows, and a native test from PowerShell, aren't covered yet.
10. **Copilot and Cursor.** Their v2 updates remain deferred, as set out in `AGENTS.md`.
