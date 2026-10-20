# Orchestrator Flow v2.1.0: native test summary

This summary covers native testing of the Claude Code integration on macOS, from 2026-10-16 to 2026-10-19. The raw evidence (transcripts, scratch repositories and review notes) stays local. Remaining work is listed in [follow-ups.md](follow-ups.md). To repeat the test, follow the [Claude native-test runbook](../../tests/live/claude/README.md).

## Setup

- **Claude Code:**
  - Run 1 used the CLI at 2.1.300 to 2.1.301.
  - Run 2 used the CLI at 2.1.302 to 2.1.304, started from the desktop app's terminal panel.
  - The desktop app's bundled 2.1.299 passed the startup check, but no workflow run used the desktop app as its host.
- **Orchestrator model:** Fable 5.1 in run 1 and Opus 5.5 in run 2, each the session's own choice.
- **Permission modes:** auto for both workflow runs, acceptEdits for the allow-rule check (part A), and auto for the Read-rule check (part D).
- **Installation:** the README's two user-level links and the skill's `.venv`.
- **Project:** a small standard-library Python utility in a disposable repository with a local bare remote.
  - The feature was a Basic, literal `--contains TEXT` line filter.
  - Its proposal contained non-ASCII text (`café`, `Straße`, `日本語`), `<`, `>` and `&`, and one open product question: whether matching ignores letter case.

## What ran

| Run | Date | Scope |
| --- | --- | --- |
| Master-session probe | 2026-10-16 | Whether one session can start, answer or stop another session's Orchestrator. |
| Run 1 | 2026-10-16 to 2026-10-19 | One complete Basic feature, from setup to explicit acceptance, on the default branch. |
| Run 2, part A | 2026-10-19 | The README's acceptEdits allow rules, loaded from a session-only settings file. |
| Run 2, part C | 2026-10-19 | A plain-words request without the slash command, then declining the confirmation. |
| Run 2, part B | 2026-10-19 | The same feature on an explicit branch: a quit after the Coder's first checkpoint, a resume, then a stop at the code-review start. |
| Run 2, part D | 2026-10-19 | The narrow `Read` rules in auto mode. |

## Results

| Area | Result | Evidence |
| --- | --- | --- |
| Startup check | Pass | Reported the running version and source, venv health and overrides. The inline check ran pre-approved, and after a resume it ran again on the updated CLI. |
| Confirm-first start | Pass | A typed start never asked. A plain-words request ran only read-only lookups, then asked whether the user meant to start Orchestrator Flow. Declining left nothing behind. |
| Configuration | Pass after fixes | Repository defaults were written with the Write tool. The recommendation gave explicit short names and efforts. Run 1 asked the proposal's product question itself, and run 2 left out the per-choice reasons until asked. Both are fixed, but the step-4 checklist hasn't been re-run natively. |
| Lead starts | Pass | Every lead started in the background with both marker lines and the accepted model and effort. None used a fork, isolation or a team. |
| Helpers | Pass | Haiku runners worked under the Coder and the Reviewer. They run asynchronously (see the platform facts). No explorer was needed. |
| Continuation | Pass | Planner continued across approvals under one agent ID. Returns sent after a continuation message carry that ID as `context_id`. |
| Recording | Pass | Every lead return was recorded from its transcript, and Orchestrator's own entries went through `append-entry`. The recorder caught a stale Planner report, and the entry writer caught an acceptance entry that didn't disclose known issues; both were corrected. Duplicate checks answered `already_recorded` as designed. Non-ASCII text and `<`, `>`, `&` arrived intact. |
| Git and journal | Pass after fix | The branch was the exact feature name, or the explicit branch. Every checkpoint was pushed with trailers, and `main` stayed untouched. Preparing run 2 showed that an earlier run's checkpoint journal would block a rerun's first push. After the fix, all 14 of run 2's pushes went through. |
| Resume | Pass | `claude --resume` kept the session ID. The interrupted Coder was continued by agent ID, and a `find-agent` cross-check agreed. Its cumulative report separated checks made before the interruption from fresh ones. A tool call interrupted inside a lead (the 2.1.296 fix) wasn't exercised, because the Coder was waiting on a helper, not mid-call. |
| Permissions | Pass | acceptEdits honored the README's allow rules. The `Read` rules also suppressed auto mode's out-of-project prompt. Auto mode raised no classifier blocks or warnings. |
| Report forms | Partial | Every return used SubagentHandback. Only fixtures cover the plain final-message form. |
| Workflow version | Pass | The task log recorded 2.1.0, not the product's own `VERSION`. |

## Findings and fixes

| Finding | Fix |
| --- | --- |
| When a slash command isn't run as a command, a model may follow `SKILL.md` by hand (master-session probe). | `e716306`: a confirm-first start that asks once, before the run starts. |
| Run 1's Orchestrator asked the proposal's open product question itself. | `3cea60c`: open questions count as difficulty evidence, and only Planner raises them. Applied to both integrations. |
| Run 1 created the repository defaults and the initial log with shell heredocs. | `3cea60c`: always the Write tool, never a redirect or heredoc. |
| The README's allow-rule example needed the path form the commands actually use. | `3cea60c`: link-path rules, plus a second `Read` rule for the checkout, because a read through a symlink must match both paths. |
| The checkpoint journal is keyed by feature, so an earlier run could block a rerun's first push. | `2eaaac8`: only records on the run's own branch and remote, with commits in the current checkpoint's ancestry, count. Applied to both integrations. |
| A background lead's helpers run asynchronously, so a lead waiting on one looked finished to the recorder. | `a607306`: the recorder reports a waiting lead as `no_completed_report`, and the contracts, README and proposal describe the wait. |
| Run 2's Orchestrator left out the recommendation's reasons and short-name sentence until asked. | `a607306`: an explicit list of what the recommendation must show before acceptance, mirrored for Codex. |
| The out-of-project read prompt's "keep allowing" option is permanent and broad. | `a607306`: the README recommends the narrow `Read` rules in auto mode too. Part D confirmed they suppress the prompt. |

## Known limitations

- **Orchestrator's own entries:** Orchestrator learns the shapes of its own log entries by probing the schemas with `cat` and inline scripts. Those would prompt in acceptEdits mode. Deferred; see follow-ups 2 and 3.
- **The coordinator-message reset:** a coordinator message clears the recorder's pending-helper list. If Orchestrator messages a waiting lead that then replies in plain text, a stray correction request can follow. See follow-up 5.
- **Hand-backs:** the recorder counts a helper as finished only when its hand-back arrives as a peer message. See follow-up 4.

## Claude Code platform facts

These held on CLI 2.1.300 to 2.1.304, plus the desktop app's 2.1.299 for the probe. They matter beyond this workflow.

- **Helpers of a background lead run asynchronously,** even with an explicit `run_in_background: false`. That held for 4 of 4 helper calls in run 1 and 8 of 8 in run 2.
  - The launch's tool result carries `toolUseResult.status: "async_launched"` and the helper's agent ID.
  - The lead ends its turn while it waits.
  - Each hand-back arrives as an `isMeta` user message with `origin.kind: "peer"`, which wakes the lead.
- **Continuation and resume:**
  - SendMessage continuations arrive as `isMeta` user messages with `origin.kind: "coordinator"`.
  - `claude --resume` keeps the session ID.
  - Background agents cut off when a session ends aren't restarted. A lead's lost helpers never hand back.
- **Large tool results:** a tool result over 50,000 characters is saved to the session's `tool-results/` folder, and the model gets a 2 KB preview. Orchestrator read the saved file in chunks.
- **Background notices:** the CLI delivers them as `<task-notification>` entries in `queue-operation` records, with `task-id`, `tool-use-id`, `status`, `summary`, `result`, `usage`, `note` and `output-file`.
- **Skills:**
  - `${CLAUDE_SKILL_DIR}` expands to the link path, `~/.claude/skills/orchestrator-flow`, not the checkout.
  - An inline `` !`…` `` command that matches `allowed-tools` runs pre-approved.
  - `disable-model-invocation` hides a skill from the model, but not its files.
- **Permissions:**
  - A read through a symlink is allowed only when both the link path and the resolved path match allow rules. Separate rules may match each one.
  - Narrow `Read` rules suppress the out-of-project read prompt in both acceptEdits and auto mode.
  - That prompt's "keep allowing" and "block … from now on" options are both permanent, and both apply to every read outside the project.
  - Bash allow rules match the command text as written.
- **Between sessions:**
  - A message from another session can't answer or stop a pending AskUserQuestion dialog; it queues instead.
  - A slash command runs only as the CLI's opening prompt. It doesn't run as a desktop session's opening prompt or as a cross-session message.
- **Commit attribution:** Claude Code's `attribution` setting controls the Co-Authored-By trailer. There are two documented ways to hide it:
  - `false` hides all attribution on 2.1.281 or later. Earlier versions reject it and skip the settings file that holds it.
  - The object form, with empty `commit` and `pr` strings and `sessionUrl: false`, also works on older versions.

  With one of these in user settings, none of run 2's 14 checkpoint commits had the trailer, against 15 of 15 in run 1.

## Coverage gaps and next steps

[follow-ups.md](follow-ups.md) lists them:
- watching the next real Codex run, with a v2.1.1 fix if needed
- Orchestrator's entry shapes
- the recorder's remaining edge cases
- a Claude version of the live test kit
- native coverage gaps
- Windows
- Copilot and Cursor
