# Proposal: Orchestrator Flow v2.1.0 for Claude Code

## Problem Statement

Orchestrator Flow takes a completed proposal or bug report through **Planner → Architect → Coder → Reviewer**, coordinated by **Orchestrator**. Version 2.0.0 reworked the workflow so its cost matches the work. It added:

- separate assurance and capability settings
- independently versioned and approved specification documents
- an append-only, resumable `task_log.json`
- feature-branch checkpoints
- proportionate review rules
- explicit final acceptance

That version was implemented and released for Codex only. Claude Code, the maintainer's other priority platform, still runs the pre-v2 workflow.

### Claude Code still runs the pre-v2 workflow

The Claude integration is a `/orchestrate` command plus five instruction files in `.claude/agents/`:

- The command tells the main conversation to read `~/.claude/agents/orchestrator.md` and act as Orchestrator. For each role, the main conversation reads `~/.claude/agents/<role>.md` and passes that text to a `general-purpose` subagent. Models are hard-coded: `opus` for Planner, Architect and Reviewer, and `sonnet` for Coder.
- The five files have no frontmatter, so Claude Code does not register them as subagents.
- The files embed the older task-log schema and wrappers and forbid role Git writes. They apply older review and nit expectations, let Coder delegate implementation tasks, and load the distribution's coding directives through a `.claude/agents/Directives` symlink.

A feature run in Claude Code therefore gets none of v2.0.0's behavior, and the v2 tools cannot validate or resume its log.

v2.0.0 exists because the old process cost too much for its consequences. On the maintainer's private FEC bot, an API-provider migration worked well, but repeated full re-reviews spent about two and a half usage allocations on increasingly minor hardening. The rule that governs v2 also governs this change: perfection is the enemy of good.

### The installation takes over Claude Code's shared folders

The current installation symlinks the entire `~/.claude/agents` directory to this repository and links `/orchestrate` as a single command file. That has two consequences:

- A user cannot keep their own agents, or another tool's agents, in `~/.claude/agents` alongside the workflow.
- A single command file cannot carry the schemas, scripts and references a v2 integration needs.

### Current Claude Code provides what v2 needs

The findings below come from three sources, all dated 2026-10-14: Claude Code's documentation, its changelog up to 2.1.299, and probes run with the CLI (2.1.300) and the desktop app's bundled Claude Code (2.1.295). Version numbers give the release in which a capability arrived.

- **Real role delegation.** Custom subagents are Markdown files with YAML frontmatter.
  - They live in `~/.claude/agents/` or a project's `.claude/agents/`, and both are scanned recursively.
  - Frontmatter sets `name`, `description`, `tools` or `disallowedTools`, `model` and `effort`. The body becomes the subagent's system prompt.
  - Files without a `name` are ignored, which is why the current files never registered.
  - In a probe, agents inside a symlinked subfolder of a project's `.claude/agents/` loaded.
- **Helpers owned by each lead (2.1.219).** A subagent can start its own subagents, by default up to three levels below the main conversation. `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` changes the limit. A nested start worked in a probe.
- **Per-role capability (per-call effort since 2.1.292).** Each Agent tool call can pass `model` and `effort`, and both override the agent file.
  - `model` takes the short names `opus`, `sonnet`, `haiku` and `fable`.
  - `effort` takes `low`, `medium`, `high`, `xhigh` or `max`.
  - Two environment variables override per-call values: `CLAUDE_CODE_EFFORT_LEVEL` and `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`.
  - The `availableModels` and `fallbackModel` settings can substitute models.
- **Keeping a lead's context (2.1.77).** `SendMessage` to an agent ID resumes a finished or interrupted subagent with its full history. Since 2.1.296, a subagent resumed after a session shutdown is no longer told that the user rejected its interrupted tool call.
- **Questions go through the main conversation.** Claude Code removes `AskUserQuestion` from every subagent, so only the main conversation can ask the user.
- **Background work (2.1.186).** Subagents run in the background by default. Their permission prompts appear in the main session and name the subagent. Headless `-p` runs deny prompts.
- **Skill resources (2.1.69).** Skills live in `~/.claude/skills/<name>/`, and symlinked skill folders are supported.
  - `${CLAUDE_SKILL_DIR}` is substituted in skill content and in `allowed-tools` rules.
  - `disable-model-invocation: true` limits a skill to explicit invocation.
  - Inline `!` commands run when the skill is invoked, unless the `disableSkillShellExecution` setting turns them off.
- **Project guidance (2.1.277).** Subagents load the project's `CLAUDE.md`, or its `AGENTS.md` when no `CLAUDE.md` exists.
- **Models.**

  | Model | Price per million tokens (input / output) |
  | --- | --- |
  | Fable 5.1 | $10 / $50 |
  | Opus 5.5 | $4 / $20 |
  | Sonnet 5.5 | $2 / $10 |
  | Haiku 5.5 (2.1.293) | $0.10 / $0.50, for prompts up to 100K tokens |

  - All five effort levels work on these models.
  - Claude Code's default effort for the 5.5 models is `medium`.
  - Depending on the plan, Fable can bill paid usage credits.
  - Claude Code switches away from Fable automatically when Fable's safety classifiers flag a request.

### Large role returns do not reach the Orchestrator's context

In Codex, Orchestrator records a role's return by passing the JSON it received to `record-handoff -` on stdin. In Claude Code that cannot be the only method:

- **CLI 2.1.300.** Returns of 14 KB and 42 KB reached the main conversation byte-identical, inside a fixed hand-back header and a footer giving the subagent's `agentId`. An 82 KB return did not arrive. Claude Code saves any tool result over 50,000 characters to the session's `tool-results/` folder and gives the caller only a 2 KB preview and the file path. Both the saved file and the subagent's transcript held the exact return.
- **Desktop 2.1.295.** A 43 KB return arrived with every line indented two spaces. The indentation did not change the JSON value.
- **Transcripts.** Each subagent's exact final message is stored in its transcript at `~/.claude/projects/<project>/<session-id>/subagents/agent-<agent-id>.jsonl`. The CLI and the desktop app use the same layout, but Claude Code does not document it.
- **Real return sizes.** Typical returns are well under the limit. The largest single role return in the existing local task logs was 67 KB, which would exceed it.
- **Copying.** In one trial, Opus copied a 43 KB return into the recorder's input exactly. Copying still spends output tokens on every return, and the recorder can check a copy's shape but not its faithfulness.

### Other constraints found while investigating

- **Resuming a nested helper is unreliable.** In the desktop app (2.1.295, auto mode), a finished lead resumed its finished helper by ID, and the helper still had its context. Its reply, however, went to the main conversation instead of the lead, and auto mode blocked its attempt to message the lead as possible data exfiltration.
- **The CLI and the desktop app run separate copies of Claude Code.**
  - The desktop app bundles a specific version and changes it only through app updates. On 2026-10-14, the latest app (2.37337.1) ran Claude Code 2.1.295.
  - `claude update` updates only the CLI.
  - Sessions started inside the desktop app set `DISABLE_AUTOUPDATER=1`, and child processes inherit it.
  - Both kinds of session expose the running binary in `CLAUDE_CODE_EXECPATH`, which is not documented.

### Behavior to preserve

Every settled v2.0.0 behavior carries over. The current Codex contracts and schemas define it, and this change does not reopen it:

- Role ownership, read-only review roles, and explicit approvals in dependency order.
- Assurance levels, independent of capability, with proportionate follow-up review. Nit-only reviews are accepted at every assurance level.
- The `review_disposition_policy` options and repair allowances.
- Separate Red and Green tasks and the other task categories.
- Content versions and Revision History. Checking off a task does not change the tasks content version.
- Optional research, and a current `known-issues.md`.
- The consolidated Planner handoff on the final tasks draft, and the cumulative Coder return.
- Artifact checkpoints owned by Planner and Coder, and log checkpoints owned by Orchestrator.
- Bounded, user-authorized push recovery, explicit final acceptance, and manual merging.
- Exceptional implementation phases.
- The compatibility rules for logs.

The new integration also keeps the explicit slash-command entry Claude Code users already have.

## Proposed Solution

Implement v2 for Claude Code as a native counterpart of the Codex skill, released as workflow v2.1.0. It uses the same protocol, task-log format, wrappers and policies, but runs through Claude Code's own mechanisms: a skill, role subagents, per-call capability controls, and session transcripts.

Codex keeps its behavior. It receives only the optional schema addition in section 5, through runtime files kept identical across integrations (section 9), and the new canonical VERSION.

Choices below were decided with the maintainer unless marked **Recommendation**. Platform statements are the documented or observed facts above.

### 1. Install as two linked subfolders

The integration lives in two folders in this repository. The names shown are indicative; design may refine them.

```text
.claude/
  skills/orchestrator-flow/
    SKILL.md
    references/        Claude-native contracts, schemas, wrappers and examples
    scripts/           runtime helpers and requirements.txt
    VERSION   -> ../../../VERSION
    templates -> ../../../templates
  agents/orchestrator-flow/
    flow-planner.md  flow-architect.md  flow-coder.md  flow-reviewer.md
    flow-explorer.md  flow-runner.md
```

Installation is two directory links, each placed as a subfolder inside the user's ordinary Claude Code folders:

```sh
ln -s "[ORCHESTRATOR_REPO_PATH]/.claude/skills/orchestrator-flow" ~/.claude/skills/orchestrator-flow
ln -s "[ORCHESTRATOR_REPO_PATH]/.claude/agents/orchestrator-flow" ~/.claude/agents/orchestrator-flow
```

- **Coexistence.** `~/.claude/skills` and `~/.claude/agents` stay real directories, so the user's own skills and agents, and other tools', coexist with the workflow. The checkout remains the source, and there is no copy, export or plugin installation.
- **Shared resources.** `VERSION` and `templates` are real relative symlinks stored by Git as mode `120000`, as in Codex. A missing or flattened link is a setup error, with no text-pointer or copy fallback.
- **Legacy files.** Remove the old integration: `.claude/commands/orchestrate.md`, the five legacy files in `.claude/agents/`, and the `.claude/agents/Directives` link. No feature started under the old workflow needs to continue, and old logs remain unsupported, as in Codex v2.0.0.
- **Migrating an existing installation.** Setup documentation explains it, and the user performs it:
  - Replace a whole-directory `~/.claude/agents` link with a real directory.
  - Remove the `~/.claude/commands/orchestrate.md` link.
  - Add the two links above.

  The workflow never changes installation paths itself.
- **Maintenance sessions.** This repository's own `.claude/` folder also configures Claude Code sessions run in this checkout. Explicit-only invocation (section 2) and restrictive agent descriptions (section 3) keep maintenance sessions from starting the workflow.
- **Windows.** Windows setup and behavior are deferred. The maintainer uses PowerShell there and will test it later.

### 2. Start explicitly; the main conversation is Orchestrator

- **Explicit start.** The user starts the workflow with `/orchestrator-flow <completed proposal or bug-report path, or a request>`. The skill sets `disable-model-invocation: true`, so Claude never starts it on its own. This differs deliberately from Codex, which also allows implicit invocation.
- **A start without the slash command is confirmed first.** When `/orchestrator-flow` is not run as a command, a model can still find `SKILL.md` and follow it by hand. A native probe saw this when the command was another session's opening prompt for a desktop session; a request in other words can lead to the same thing.
  - `SKILL.md` detects the case when no copy of its skill-directory line in the conversation shows an absolute path, only the unexpanded placeholder. A placeholder alone isn't enough: a real run also reads `SKILL.md` as a file, and that copy shows the placeholder too.
  - Before the run starts, Orchestrator asks the user whether they meant to start Orchestrator Flow, naming the request it understood. If they decline, it stops. It asks only once: a run already in progress, or one the user already confirmed, never asks again, even if compaction later leaves only the file copy.
  - If they confirm, it continues exactly as an invoked run. The skill directory is the folder containing `SKILL.md`, the request comes from the user's message, and the startup check runs through its fallback (section 8).
  - Only the skill's `allowed-tools` pre-approval cannot apply, so setup documentation adds an allow rule for the startup check.
  - Reading or maintaining the skill's files never starts the workflow, and the typed command remains the normal start. Whether a `SKILL.md` read by hand persists through compaction as an invoked skill does has not been verified.
- **The main conversation is Orchestrator.** Only the main conversation can ask the user questions and start every role. Its model and effort are whatever the user picks for the session. They are not recorded and may change partway through a feature.
- **Loading guide.** `SKILL.md` is a loading guide like the Codex one. Coordination loads the Orchestrator contract, the protocol and assurance. Recovery, phases and Maximum checklists load only when they apply. `SKILL.md` resolves every path through `${CLAUDE_SKILL_DIR}` and passes the skill directory to each role it starts.
- **Version check first.** The check in section 8 runs before anything else.
- **Questions route through Orchestrator.** Roles cannot ask the user directly. They return questions in their structured output: Planner's incremental return, or Coder's coordination report for blockers. Orchestrator asks the user, records the answer as today, and continues the role with it through `SendMessage`.

### 3. Real role subagents with Claude-native contracts

Each role and helper becomes a real subagent file with frontmatter:

- **Names.** Agent names carry a `flow-` prefix, such as `flow-planner` and `flow-reviewer`. Claude Code agent names share one namespace, and a consuming project's own `reviewer` agent would otherwise take precedence over the workflow's. The prefix is internal to how roles are started. Users, contracts, the task log and wrappers keep the role names Planner, Architect, Coder and Reviewer, plus the exploration helper and the test runner. Orchestrator maps each role to its agent, so a request such as "switch the Reviewer to Fable" means exactly what it says.
- **Description.** States that the agent is used only when Orchestrator Flow delegates to it or the user explicitly asks for it. Claude chooses agents automatically from their descriptions, so this keeps a request such as "review this" in another project from picking up `flow-reviewer`. Helpers are described as internal.
- **Tool restrictions.** Claude Code enforces these natively:
  - Architect, Reviewer and both helper types get no `Edit`, `Write` or `NotebookEdit`.
  - Helpers also get no `Agent`, so they cannot start further agents.
  - `Bash` remains available for Git, tests and the workflow scripts. Read-only behavior beyond these restrictions stays a contract obligation, as in Codex.
- **No fixed model or effort.** Orchestrator supplies both on every start (section 4), so an agent file can never contradict the recorded feature configuration.
- **Body.** A short role identity, the role's non-negotiable boundaries, and an instruction to load the full contract from the skill directory. In orchestrated use, Orchestrator passes that directory. In standalone use, the role finds it at the installed location.

The full contracts live in the skill's `references/`. They are Claude-native rewrites of the v2.0.0 contracts with the same meaning, not summaries of the Codex files and not adapters that read them. They state these Claude-specific rules:

- **No forks.** Never start a role as a fork, because forks inherit the Orchestrator's conversation and model.
- **No worktrees.** Never use `isolation: worktree`. The existing checkout is used unless the user asks for a worktree.
- **No agent memory.** Never use agent `memory`, because workflow state lives in the task log and Git.
- **Project guidance.** Follow the consuming project's `CLAUDE.md` or `AGENTS.md`, plus any project-owned coding directives they identify. Do not load this repository's `Directives/codingAgentDirectives.md` as policy.
- **Git ownership.** Planner and Coder publish artifact checkpoints with Git through `Bash`, and Orchestrator publishes log checkpoints. Trailers, push-attempt evidence and failed-push recovery work exactly as in Codex. No agent force-pushes or merges.

**Standalone use.** The four lead roles can be used directly, without orchestration:

- Asked for by name from any session, a role runs as a subagent and returns its questions to the caller.
- Run as `claude --agent flow-reviewer`, the role becomes the whole session and can ask the user directly.

Standalone use never creates orchestration approvals.

### 4. Capability selection separate from assurance

Capability works as in Codex. Assurance is a separate decision.

- **Defaults and per-feature recommendation.** Repository defaults live in `.orchestrator-flow.json` under `capability_defaults["claude-code"]`. At each feature start, Orchestrator uses judgment to recommend a complete configuration, with a reason for each choice.
  - Capability follows difficulty: ambiguity, unfamiliar interfaces, integration and state, and conflicting evidence.
  - Assurance follows consequences.
- **User control.** The user accepts or overrides any part. The accepted configuration is recorded in that feature's task log, and repository defaults change only when the user asks. Mid-feature overrides apply to later work at a coherent boundary, under the existing rules.

These are the repository defaults, not fixed rules:

| Role | Model | Effort |
| --- | --- | --- |
| Planner | `opus` | `xhigh` |
| Architect | `opus` | `max` |
| Coder | `opus` | `high` |
| Reviewer | `opus` | `max` |
| Exploration helper | `sonnet` | `medium` |
| Test and check helper | `haiku` | `medium` |

The Codex tiers map roughly as Astra to Fable, Sol to Opus, and Luna to Sonnet or Haiku. The defaults use Opus rather than Fable because Fable costs 2.5 times as much, may bill usage credits, and falls back automatically. Orchestrator may recommend Fable for the Planner, Architect or Reviewer on a hard feature, or medium effort for the Coder on a routine one. Those are examples of judgment, not rules.

- **Native controls.** Every role and helper start passes the accepted `model` and `effort` on the Agent tool call. Prompt text never stands in for a native setting.
- **Recording.** The log records the short model name actually passed, and always an explicit effort, because Claude Code's default differs by model. A short name resolves to the newest model in its family, or to the session's own model version when the session uses that family. Setup documentation and Orchestrator's recommendation state this once; it is not added to every feature's acknowledged limitations, because an always-present entry would make the validator's check for an unmapped intermediate effort always pass.
- **Overrides that defeat per-call choices.** At feature start, Orchestrator checks for `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` and `CLAUDE_CODE_EFFORT_LEVEL`. It discloses any `availableModels` or `fallbackModel` substitution that Claude Code reports. Each is presented as a limitation for the user to accept or remove. Nothing is substituted silently.
- **Fable.** When the user selects Fable, its automatic fallback is recorded as an acknowledged limitation, and its usage-credit consent prompt may pause a background role until answered.
- **Unavailable models.** An unavailable model or a usage limit pauses the affected work for the user's choice, as today.
- **Intermediate phase reviews.** These keep the Reviewer's model and map effort `max → high`, `xhigh → medium`, `high → low`. Claude Code supports every level involved.

### 5. Two helper types started by their lead

- **Two kinds of helper.** Helpers split into exploration and research helpers and test and check runners.
  - Exploration helpers answer bounded questions about code, interfaces, dependencies and external sources.
  - Runners execute specified tests, lint, type checks, builds and planned manual checks.
  - Neither kind intentionally edits project files or publishes, and both return concise evidence to their lead.
  - The split lets tests run on Haiku while exploration uses a stronger model. In Codex, a single helper setting worked because Luna at maximum effort was sufficient for exploration.
- **How leads use helpers.**
  - A lead starts helpers itself with the Agent tool, passing the accepted helper model and effort.
  - It asks for a foreground start with `run_in_background: false`. Under a background lead, Claude Code runs the helper asynchronously regardless, as the native tests showed: the lead ends its turn while it waits, and the helper's hand-back arrives as a message that wakes it. A lead never returns its report while a helper is pending.
  - It groups related checks into one helper call. This replaces Codex's guidance to reuse helper contexts, which in Claude Code would depend on resuming helpers.
- **After an interruption,** leads start new helpers and rerun interrupted checks. Helpers are never resumed.
- **Report size.** Concise reports stay far below 50,000 characters. If a helper's report nonetheless arrives as a saved-file preview, the lead reads the saved file instead of rerunning the helper.
- **Fallback.** If a user setting disables nesting, the existing contract fallback applies: Orchestrator coordinates permitted helper work and returns the evidence to the lead.

#### Optional exploration-helper assignment

Add an optional exploration-helper assignment to the shared `roles` definition, used by both feature capability and repository defaults. `exploration_helpers` is the suggested name; design settles it.

- When absent, `helpers` covers exploration and execution, exactly as in 2.0.0.
- When present, exploration and research helpers use it, and `helpers` covers test and check execution.

Replay and validation support it as a complete-role override target and in examples. Helper failure records identify which helper assignment applied.

Because the shared runtime files must stay identical (section 9), this addition also lands in Codex's copy. Codex's instructions keep using the single `helpers` assignment in v2.1.0. Adopting the split there is a separate, later decision.

### 6. Record role returns from Claude Code's transcripts

Orchestrator records each role's return by agent ID rather than by copying it:

- **The recorder reads the return directly.** A Claude-only recorder input reads the role's final message from its transcript.
  - It finds the session from `CLAUDE_CODE_SESSION_ID`, and uses the agent ID Orchestrator received when it started the role.
  - It parses the JSON and records it through the shared recorder (its `prepare_handoff` API or the `record-handoff` command), with the same validation and readback as today.
  - This one method works at every size. It is exact by construction, saves the Orchestrator from re-typing large returns, needs no shell transport, and creates no temporary files.
- **A summary for Orchestrator.** After recording, the recorder prints a short summary of what Orchestrator must act on:
  - the event recorded and the resulting status
  - the review's acceptance value
  - open questions
  - findings that need a user decision, with ID, severity and title
  - blockers

  Orchestrator works from this summary and from any return that arrived inline, and never needs to load a large return into its own context.
- **Fallbacks.**
  - If the transcript is not in the current session's folder, the recorder searches this project's other session folders for the agent ID, or takes an explicit transcript path.
  - Record an inline return on stdin only when its text is unaltered. Background completion notices escape the report text and can neutralize parts of it, so their text is never copied.
  - A saved tool-result file lives in the same session folder as the transcript, so it adds no separate fallback.
  - If none of these works, stop and ask the user.
  - Never record a summary, a pointer or a reconstruction.
- **Orchestrator's own entries.** A Claude-only entry writer records approvals, overrides, dispositions and other Orchestrator entries. It derives the ID, timestamp, status and effective configuration through the shared replay and validates the candidate before writing, so Orchestrator never edits or loads a large log by hand.
- **Role obligations.** A role's final message is the JSON wrapper alone, with no code fences or prose, and the role validates its wrapper before returning, as today. Wrapper schemas do not change.

The transcript reader is a Claude-only script, kept outside the files shared with Codex. It depends on an undocumented layout, so it fails with a specific error when the layout changes, and fixture tests built from real transcripts guard it.

### 7. Continuation, interruption and resume

- **Agent IDs.** Orchestrator records each lead's agent ID as the invocation's existing optional `context_id`.
- **Continuing leads.** Orchestrator continues a lead across gates with `SendMessage` to that ID: Planner after each approval, Coder for repairs, and Architect or Reviewer for follow-up reviews. The lead keeps its context, as the v2 contracts already prefer.
- **Background leads.** **Recommendation:** start leads in the background so the user can keep talking to Orchestrator during long runs, for example to override a setting or answer a question. Orchestrator acts when the completion notice arrives. When a decision needs Git ownership, Orchestrator messages the producing lead to yield at a coherent boundary, which maps the existing coherent-yield rule onto `SendMessage`.
- **After an interruption,** the user resumes the same Claude Code session: reopen it in the desktop app, or run `claude --resume` in the CLI. Orchestrator then messages the lead by ID. This relies on the 2.1.296 fix described above.
- **Replacement recovery.** If the session cannot be resumed or the ID no longer resolves, the existing recovery applies. A new lead receives the full contract and reconstructs the original cumulative baseline from Git, the task log and task progress. There is still no dispatch ledger.

### 8. Minimum Claude Code version and a startup check

The minimum is **Claude Code 2.1.296**, the release that provides everything this proposal uses. Older versions are not supported. The relevant releases are:

| Release | Provides |
| --- | --- |
| 2.1.186 | Background permission prompts in the main session |
| 2.1.219 | Nested helpers by default |
| 2.1.292 | Per-call effort |
| 2.1.293 | Haiku 5.5 behind `haiku` |
| 2.1.296 | Correct resume after a shutdown |

The Claude integration states the minimum in exactly one place. If native testing shows that a later fix is required, the minimum rises.

The check runs at every `/orchestrator-flow` invocation, including resume, before any branch, log entry or agent exists:

- **How it runs.** `SKILL.md` runs a check script as an inline command, pre-approved through the skill's `allowed-tools`. The script runs `"$CLAUDE_CODE_EXECPATH" --version`, which reports the binary actually running in either the CLI or the desktop app. `claude` on `PATH` may be a different copy.
- **Too old.** Orchestrator shows the message and stops. The message names the actual running version and its source:

  ```text
  Orchestrator Flow requires Claude Code 2.1.296 or newer. This session is running Claude Code 2.1.295 (Claude desktop app). Update Claude Code, then start a new session: in a terminal run `claude update`; for the desktop app, update the Claude app.
  ```

- **Unknown version.** If the version cannot be determined, Orchestrator runs the script itself. That covers a missing variable, inline commands turned off by `disableSkillShellExecution`, and a run the user confirmed without the slash command (section 2). If the version is still unknown, Orchestrator says so and asks the user before continuing.
- **Standalone roles** run the same check first.

### 9. A Claude-owned runtime kept identical to Codex's

- **Claude's own copy.** The Claude skill carries its own copies of the shared runtime files:
  - the common, task-log, repository-configuration and wrapper JSON schemas
  - the validator and recorder, protocol replay, artifact, spec-reader and checkpoint scripts
  - `requirements.txt`

  There is no shared runtime directory, and no Claude adapter that reaches into `.codex/`.
- **Identical shared files.** These shared files must be byte-identical in every integration that implements v2, so they are written platform-neutrally. For example, `workflow_artifacts.py` currently describes itself as Codex validation, and that wording changes.
- **Claude-only files.** The transcript reader and the version check live in separate files.
- **Examples.** Example files may carry platform-specific values, and each integration's examples validate against its own schemas.
- **Parity test.** One development test lists the integrations that implement v2 and the shared file set, and fails by naming any file that differs. Codex and Claude Code are listed now; Copilot and Cursor join when they move to v2.
- **Maintenance rule.** AGENTS.md states that any change to the shared files, and any workflow VERSION bump, updates every v2 integration in the same change.

### 10. Versioning and compatibility

- **Canonical VERSION.** It moves from `2.0.0` to `2.1.0` and reaches Codex through its existing link. The release is additive: the Claude integration and the optional exploration-helper assignment.
- **Codex compatibility.** Codex already reads logs from 2.0.0 up to its own version. Existing 2.0.0 logs and repository configurations stay valid, and a missing exploration-helper assignment keeps the 2.0.0 meaning.
- **Claude logs.** Claude Code features use the same log schema with `platform: "claude-code"`.
- **Pre-v2 logs.** Pre-v2 Claude Code logs remain unsupported, with no migration. Encountering one stops for user direction.
- **Unchanged.** The integer template versions do not change, and switching an in-progress feature between platforms is not a requirement.

### 11. Permissions

- **How roles run commands.** Roles run Git and the workflow scripts through `Bash`. A background subagent's permission prompt appears in the main session and names the subagent.
- **Auto mode.** Auto mode's classifier can refuse actions; a probe saw it block one agent-to-agent message. A refusal is reported as it happened, with no invented exit codes. Any retry goes through the existing bounded, user-directed recovery.
- **Documentation.** Setup documentation offers optional allow rules that consuming projects may adopt for `git add`, `git commit`, `git push` and the workflow's scripts. It also recommends a permission mode for workflow sessions (see Questions). Adopting either is the user's choice.
- **Headless runs.** Headless `-p` runs are not supported, because Claude Code denies permission prompts there.

### 12. Documentation and verification

**README.md** gains a Claude Code section and drops Claude's "v2 deferred" status. Copilot and Cursor stay deferred. The section covers:

- what the integration provides
- the two install links and migration from the old installation
- the Python dependency, installed in a git-ignored virtual environment inside the skill that every workflow script call names
- the minimum version, and how to check and update the CLI and the desktop app
- invocation
- a `capability_defaults["claude-code"]` example using the defaults above
- permission guidance
- standalone role use

**AGENTS.md** updates:

- the phase scope: Codex and Claude Code implement v2, and Copilot and Cursor remain deferred and protected
- the layout entries
- Claude validation commands
- the parity and VERSION rules
- a note that this repository's `.claude/` folder loads in maintenance sessions

**tests/README.md** describes the new coverage. No release-folder README or validation report is added. A brief summary of the native test outcome may be kept in `.docs/v2.1.0/` if useful.

**Repository tests**, under `tests/` and proportionate to the change:

- **Parity:** the shared-file parity test.
- **Claude links:** real relative `VERSION` and `templates` symlinks with Git mode `120000`, readable from a foreign working directory.
- **Schema and replay** for the optional exploration-helper assignment: absent, present, as an override target, and in helper failure attribution.
- **Transcript reader**, using sanitized fixtures taken from real Claude Code transcripts:
  - inline returns
  - large returns
  - indented hand-back text
  - Unicode
  - a missing transcript
  - a final message that is not JSON
- **Version check:** older, equal and newer versions, a missing variable, and unparsable output.
- **Existing checks:** the existing suite, `git diff --check`, and JSON parsing.

**A short native test on macOS** uses the CLI, because the desktop app's bundled Claude Code is below the minimum at the time of writing. It runs one small Basic feature in a disposable repository with a local bare remote and observes:

- the version check
- the configuration recommendation and the recorded short names, explicit efforts and limitations
- roles running with the accepted model and effort, as shown by `/tasks`
- Planner continuing across approvals
- one question routed through Orchestrator
- Coder using a Haiku runner and a Sonnet explorer
- artifact and log checkpoints pushed to the remote
- returns recorded from transcripts, including one with non-ASCII text
- one restart-and-resume of the Coder by ID
- the user-level links loading
- push behavior under the recommended permission mode

**Native-test finding: helpers run asynchronously.** On CLI 2.1.301 to 2.1.304, every helper started by a background lead ran asynchronously. That held whether the lead passed `run_in_background: false`, as run 1's Coder and Reviewer did, or omitted it, as run 2's Coder did.
- The lead ends its turn while it waits, and the hand-back arrives as a peer message that wakes it.
- A waiting lead's transcript therefore ends on plain text. The recorder reports it as `no_completed_report`, so Orchestrator sends no false correction request.
- The contracts describe the wait. After a resume, a lead whose helper was lost with the session is continued by message, and it reruns that helper's work with a fresh helper.

**Native-test finding: checkpoint journals.** Preparing the second run showed that the checkpoint journal, keyed by feature only, would let an earlier run of the same feature block a rerun's first push. `2eaaac8` counts only the current run's records, in both integrations.

The [native-test summary](native-test-summary.md) records both runs, their results, the findings and fixes, and the platform facts learned. Remaining work is listed in the [v2.2.0 handoff](../v2.2.0/handoff-orchestrator-flow-v2.2.0.md).

The Codex twelve-case matrix, its master-controller harness, Windows testing, and a native exceptional-phase run are not required.

### 13. Non-goals

- v2 updates for GitHub Copilot and Cursor, and changes to the separate legacy BugAgents, CoordinatorVersion and TaskSync work.
- Changing Codex behavior, beyond the shared runtime parity and VERSION. Codex adopting the helper split is also out of scope.
- A shared cross-platform runtime, export or copy installation machinery, or any Claude adapter into Codex files.
- Packaging as a marketplace plugin or a skills-directory plugin, Claude Code agent teams, and hook-based enforcement.
- Headless or `-p` orchestration, support for Claude Code versions below the minimum, and Windows verification in this release.
- Resuming helper contexts, and a dispatch-provenance or helper ledger.
- Migrating pre-v2 logs, and switching an in-progress feature between platforms.
- Porting the Codex live test kit, rerunning the twelve-case matrix, and native exceptional-phase testing.

## Questions

Both questions were settled with the maintainer during implementation planning.

1. **Recommended permission mode for workflow sessions.**
   - **Decided:** auto mode is the single recommended mode. It is Claude Code's default starting mode and lets long runs continue while the user is away. `acceptEdits` with the documented allow rules is described as the alternative for users who prefer to approve commands themselves.
   - The mode is the user's session choice: the workflow neither detects nor changes it, and the contracts behave the same in either mode. Classifier blocks and report warnings are reported to the user as they happened.
   - The native test runs in auto mode.
2. **Background or foreground leads.**
   - **Decided:** background, as described in section 7. The user can interact with Orchestrator during long runs, and it matches Claude Code's default.
   - Leads ask for foreground helpers, but under a background lead Claude Code runs them asynchronously, and each hand-back reaches the lead as a message (section 5 and the native-test findings in section 12).

Otherwise, the decisions above form the planning baseline. Planner should raise newly discovered contradictions or material policy choices at the appropriate requirements, design or task-planning phase rather than silently changing the agreed behavior.

## References

- [README.md](../../README.md): repository purpose, the current integrations, Codex setup and v2 behavior.
- [AGENTS.md](../../AGENTS.md): maintenance boundaries, the current Codex-only phase scope this change revises, and validation commands.
- [Handoff for v2.1.0](handoff-orchestrator-flow-v2.1.0.md): settled v2 decisions, implementation lessons, and the investigation topics this proposal answers.
- [v2.0.0 proposal](../v2.0.0/proposal-orchestrator-flow-v2.0.0.md): the original rationale, including per-role capability defaults with per-feature overrides instead of named bundles.
- [v2.0.0 corrections, part 2](../v2.0.0/proposal-orchestrator-flow-v2.0.0-corrections-part2.md): the final simplification intent behind the current contracts.
- [Archived improvement notes](../archived/orchestrator-flow-consolidated-improvement-notes-2026-09-19-v2.md): the earlier Codex capability assignments (Astra and Luna) and why a Luna Coder was unreliable.
- [Codex skill entry](../../.codex/skills/orchestrator-flow/SKILL.md) and its [references](../../.codex/skills/orchestrator-flow/references/): the behavioral source for the Claude-native contracts. This covers the workflow protocol, the Orchestrator, Planner, Architect, Coder and Reviewer contracts, assurance, recovery, implementation phases and Maximum assurance.
- [Common schema](../../.codex/skills/orchestrator-flow/references/common.schema.json), [task-log schema](../../.codex/skills/orchestrator-flow/references/task_log_schema.json), [repository configuration schema](../../.codex/skills/orchestrator-flow/references/repository_config.schema.json) and [wrappers](../../.codex/skills/orchestrator-flow/references/wrappers/): the `roles`, `capability` and invocation `context_id` definitions, and the return shapes.
- [Codex runtime scripts](../../.codex/skills/orchestrator-flow/scripts/): the recorder (`record-handoff` and `prepare_handoff`), replay, spec reader and checkpoint helpers to be copied.
- Legacy Claude agents (`.claude/agents/*.md`) and the `/orchestrate` command (`.claude/commands/orchestrate.md`): the integration being replaced, removed by this change; see them in Git history at tag `v2.0.0`.
- [tests/README.md](../../tests/README.md) and [tests/test_distribution.py](../../tests/test_distribution.py): existing coverage, including the linked-resource tests to mirror for Claude.
- [Proposal and bug-report templates](../../templates/): the canonical inputs exposed through the skill's `templates` link.
- [Coding directives](../../Directives/codingAgentDirectives.md): reusable project-owned guidance that the workflow does not load as policy.
- Claude Code documentation, consulted on 2026-10-14:
  - [subagents](https://code.claude.com/docs/en/sub-agents)
  - [skills](https://code.claude.com/docs/en/skills)
  - [model configuration](https://code.claude.com/docs/en/model-config)
  - [environment variables](https://code.claude.com/docs/en/env-vars)
  - [plugin loading](https://code.claude.com/docs/en/plugins/loading), on why marketplace plugins are copied
  - [errors](https://code.claude.com/docs/en/errors), on update guidance for the CLI and the desktop app
- [Claude Code changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md): release-level evidence for the versions cited, consulted up to 2.1.299.
- Anthropic [models overview](https://platform.claude.com/docs/en/about-claude/models/overview) and [pricing](https://platform.claude.com/docs/en/about-claude/pricing): the model lineup and prices used for the capability defaults.
