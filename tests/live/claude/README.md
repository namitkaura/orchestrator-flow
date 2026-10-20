# Claude Code native test

A short, hands-on test of the Claude Code integration that you run yourself, over a few sessions. It is separate from the [managed Codex kit](../codex/README.md), which runs twelve features through a master session. A master session can't answer Claude Code's dialogs, so here you answer them yourself. A fuller Claude kit is [follow-up 7](../../../.docs/v2.1.0/follow-ups.md). The [v2.1.0 native-test summary](../../../.docs/v2.1.0/native-test-summary.md) records what this test found the first time it ran.

## What it covers

| Part | Mode | Checks |
| --- | --- | --- |
| A | acceptEdits | The README's allow rules. Reads through the skill link and the workflow's exact commands run without prompts, while an uncovered outside read still prompts. |
| C | auto | A plain-words request without the slash command gets the confirmation question first, and declining leaves nothing behind. |
| B | auto | A Basic feature on an explicit branch. Setup asks no product question, Planner routes the open question, and checkpoints push. A quit after the Coder's first checkpoint resumes the same Coder. |
| D | auto | The narrow `Read` rules suppress the out-of-project read prompt. |

Run them in the order A, C, B, D. Doing C before B keeps the repository clean for it, and puts B's session first in the resume list.

## Before you start

- Install the integration as the README's [Claude Code setup](../../../README.md#claude-code-setup-link-the-skill-and-agents) describes, including the skill's `.venv`.
- Run `claude --version`. The CLI and the desktop app each run their own Claude Code, and the CLI updates itself between sessions, so note the version each session reports.
- Choose the Orchestrator's model deliberately, with `/model`, before you start. The CLI's default may not be what you want: the first native run used Fable only because it was the default. The workflow doesn't record the Orchestrator's own model.
- Run every session from the scratch repository, never from the orchestrator-flow checkout. The checkout's own `.claude/` folder loads the skill even when your user-level links are broken, so a run there wouldn't test them.
- To have Claude read your terminal while you test, run the sessions in the Claude desktop app's terminal panel, beside a conversation with Claude. Say "check the terminal" at each moment marked below, and keep the app open until you finish.
- Check that nothing already pre-approves the reads under test. This should print nothing:

  ```bash
  grep -n -E 'Read|skills|python|defaultMode|additionalDirectories' ~/.claude/settings.json
  ```

## Set up the scratch project

Choose a folder outside the checkout, with no spaces in its path:

```bash
CHECKOUT=/path/to/orchestrator-flow
SCRATCH=~/scratch/of-native-test
mkdir -p "$SCRATCH"
git init -q --bare -b main "$SCRATCH/line-list.git"
cp -R "$CHECKOUT/tests/live/claude/seed" "$SCRATCH/line-list"
cd "$SCRATCH/line-list"
git init -q -b main
git remote add origin "$SCRATCH/line-list.git"
mkdir -p .docs/specs/v0.2.0-line-filter
cp "$CHECKOUT/tests/live/common/proposals/04-contains-filter.md" .docs/specs/v0.2.0-line-filter/proposal.md
python3 -m unittest discover -s tests
git add -A
git commit -q -m "chore: bootstrap the line list project"
git push -q -u origin main
```

The [seed](seed/) contains:
- a tiny standard-library line-list utility with seven tests
- an `AGENTS.md`, and no `CLAUDE.md`, so roles must read it themselves
- a `.gitignore` that also ignores `.claude/settings.local.json`
- a product `VERSION` of `0.1.0`, which the workflow must not mistake for its own version

Leave `.orchestrator-flow.json` absent, so that the workflow sets up repository defaults with you.

For parts A and D, save the allow-rule block from the README's [Permissions](../../../README.md#permissions) section as `$SCRATCH/allow-rules.json`, with your home directory and checkout path filled in. `--settings` loads it for one session only, so your own settings stay unchanged.

## Part A: allow rules in acceptEdits mode

```bash
cd "$SCRATCH/line-list" && claude --permission-mode acceptEdits --settings "$SCRATCH/allow-rules.json"
```

Send these one at a time, exactly as written, with `/Users/you` replaced by your home directory:

1. `Use the Read tool to read the first 20 lines of /Users/you/.claude/skills/orchestrator-flow/references/orchestrator.md.` No prompt expected.
2. `Run exactly: python3 /Users/you/.claude/skills/orchestrator-flow/scripts/check_claude_code.py` No prompt expected.
3. `Run exactly: /Users/you/.claude/skills/orchestrator-flow/.venv/bin/python /Users/you/.claude/skills/orchestrator-flow/scripts/read_spec_body.py .docs/specs/v0.2.0-line-filter/proposal.md --offset 0 --max-chars 2000` No prompt expected.
4. Control: ask Claude to use the Read tool on a file in your orchestrator-flow checkout outside the skill, such as its `README.md`. A prompt is expected.

**Decline every prompt.** Approving one could add a session rule that pre-approves a later request. Before declining, note the exact path or command the prompt shows, and say "check the terminal" if Claude is watching.

Bash rules match the command text as written. If Claude rewrites a command, for example with `~` or through the checkout path, the prompt that follows says nothing about the rule.

If read 1 prompts while read 4 also prompts, the two `Read` rules aren't combining. Try a fresh session with them replaced by the single pattern `Read(~/**/skills/orchestrator-flow/**)`.

Finish with `/exit`.

## Part C: plain-words start (optional)

```bash
cd "$SCRATCH/line-list" && claude --permission-mode auto
```

Without the slash command, ask: `Use Orchestrator Flow on .docs/specs/v0.2.0-line-filter/proposal.md.`

If Claude follows the skill, its first action is a question asking whether you meant to start Orchestrator Flow. Say "check the terminal" before answering. Being told to type the command passes too.

Decline, then `/exit`. Confirm that nothing was created: `git status --short` shows nothing new, and `git branch` lists only `main`.

## Part B: workflow run with a quit and resume

```bash
cd "$SCRATCH/line-list" && claude --permission-mode auto
```

```text
/orchestrator-flow .docs/specs/v0.2.0-line-filter/proposal.md (feature v0.2.0-line-filter, branch native-test/v0.2.0-line-filter)
```

1. **Start.** The startup check reports a supported version from the Claude Code CLI and a healthy venv, and no confirmation question appears.
2. **Setup.** It asks only for repository defaults and the feature configuration, and never asks the proposal's letter-case question. Before asking you to accept, the recommendation shows:
   - a reason for each choice
   - the review policy
   - how short model names resolve

   Say "check the terminal" before answering. Accept Basic.
3. **Planning.** The letter-case question arrives only after Planner returns it. Answer either way; exact case keeps the run shortest. Approve the documents, handle any Architect findings, and authorize coding.
4. **Quit after the Coder's first checkpoint reaches the remote.** This command, run in a second terminal, waits for it:

   ```bash
   until git -C "$SCRATCH/line-list.git" log --oneline --grep='Orchestrator-Role: Coder' native-test/v0.2.0-line-filter | grep -q .; do sleep 10; done; echo 'Coder checkpoint pushed'
   ```

   Watch the bare remote rather than your working copy, so you quit between checkpoints. Quitting between a commit and its push tests checkpoint recovery instead. Also quit while the Coder is running a command, not merely between checkpoints. Otherwise the Claude Code 2.1.296 fix for interrupted tool calls stays unexercised, as in the second native run, where the Coder happened to be waiting on a helper. On `/exit`, the CLI prints `claude --resume <session-id>`; note the ID.
5. **Resume.**

   ```bash
   cd "$SCRATCH/line-list" && claude --resume <session-id> --permission-mode auto
   ```

   ```text
   /orchestrator-flow resume v0.2.0-line-filter
   ```

   Say "check the terminal" once it continues the Coder. Expect:
   - the same session ID
   - the same Coder, continued by its agent ID, found directly or through `find-agent`
   - no claim that an interrupted step was "user rejected"
   - pushes that still go through
6. **Stop** once the resumed Coder makes its next checkpoint or its final report is recorded. You don't need to finish the feature.

## Part D: Read rules in auto mode

```bash
cd "$SCRATCH/line-list" && claude --permission-mode auto --settings "$SCRATCH/allow-rules.json"
```

Repeat Part A's reads 1 and 4.
- Read 1 should run without a prompt.
- Read 4 should show the out-of-project read prompt. Decline it with "No, and ask again next time". Its "Yes, and keep allowing…" and "No, and block … from now on" choices are both saved permanently, and both apply to every read outside a project.

## Inspect afterwards

Inspect read-only and structure first. Record what the records show, not their bodies.

- **Transcripts.** These are `~/.claude/projects/<project>/<session>.jsonl`, plus `<session>/subagents/` for agents.
  - Prompts: a tool call whose result arrives in the same second had no prompt, while a long gap means a prompt waited.
  - The startup-check lines in the skill invocation, and the session ID on every record across the resume.
  - Lead starts: `subagent_type`, `model`, `effort`, `run_in_background: true`, and both marker lines.
  - Helpers: launches with `toolUseResult.status: "async_launched"`, each paired with a hand-back (`origin.kind: "peer"`).
  - Continuations, as `origin.kind: "coordinator"` messages, and the report form, either SubagentHandback or final text.
- **Git:** the exact branch, every checkpoint on the remote with its trailers, and `main` untouched.
- **Task log:**
  - `task-log --workspace` reports VALID.
  - Returns sent after a continuation carry `context_id`.
  - The log records the workflow version, not the product's `VERSION`.
- **Checkpoint journal** in `.git/orchestrator-flow/<feature>/`: only this run's records, on its branch.
- **Settings:** `~/.claude/settings.json` is unchanged, and the scratch repo has no `.claude/` folder.

## Pitfalls

- **Async helpers:** a background lead's helpers run asynchronously, whatever `run_in_background` says. The lead ends its turn while it waits, and continues when the hand-back arrives as a message.
- **Two Read rules:** a read through the skill link must match both the link path and the checkout path, hence the two `Read` rules.
- **Only you can answer dialogs:** a message from another session queues behind them. A master session can start a CLI session with the slash command as its opening prompt, but it can't drive the run.
- **Exact Bash text:** Bash allow rules match the command text exactly.
- **Two Claude Code versions:** the CLI and the desktop app each run their own.

## Verdicts

Record each check as Pass, Fail, Unverified or Not run, as defined in [common/README.md](../common/README.md#verdicts).
