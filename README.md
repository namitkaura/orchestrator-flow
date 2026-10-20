# Orchestrator Flow

Orchestrator Flow takes a proposal or bug report through **Planner → Architect → Coder → Reviewer**, coordinated by **Orchestrator**, with your approval at each gate, an append-only task log and checkpoints pushed to a feature branch. The current workflow, **2.1.0** ([VERSION](VERSION)), is implemented for Codex and Claude Code. This repository is the installation source: integrations run from this checkout through links, and maintaining the checkout doesn't run the workflow in it.

| Platform | Entry point and files | Status |
| --- | --- | --- |
| Codex | `$orchestrator-flow`: [skill](.codex/skills/orchestrator-flow/SKILL.md) | v2, using real subagents with no in-place role fallback |
| Claude Code | `/orchestrator-flow`: [skill](.claude/skills/orchestrator-flow/SKILL.md), [agents](.claude/agents/orchestrator-flow) | v2, using real `flow-*` subagents with no in-place role fallback |
| GitHub Copilot | **Orchestrator** in the custom-agent selector: [agents](.github/agents), [prompts](.github/prompts/prompts.md) | Existing custom agents; v2 deferred. `.github/agents/` also holds the separate BugAgents, CoordinatorVersion and TaskSync agent sets, outside the v2 work. |
| Cursor | `/cursor-orchestrate`: [rule](.cursor/rules/Orchestrator.mdc), [agents](.cursor/agents), [command](.cursor/commands/cursor-orchestrate.md) | Existing rule, command and agents; v2 deferred |

## How it works

In v2 (Codex and Claude Code):

- **Roles.** Orchestrator talks to you and owns configuration, approvals, the task log, known issues, log checkpoints and recovery. Planner writes the requirements, design and tasks. Coder implements the tasks with separate Red and Green steps. Architect and Reviewer review read-only. Helpers started by a lead explore or run checks without editing.
- **Gates.** You approve the requirements, design and tasks in turn, then authorize coding after Architect's review. After Reviewer accepts the implementation, you give explicit feature acceptance.
- **Artifacts.** A feature's documents, `task_log.json` and `known-issues.md` live in the consuming repository under `.docs/specs/{feature}/`.
- **Branches and checkpoints.** Work stays in your existing checkout, unless you ask for a worktree, on one feature branch: the branch you name, otherwise exactly the feature name, keeping any release version it has (for example `v2.1.0-claude-code-integration` or `unique-lines`), never with a `codex/`, `claude/` or other prefix. Every artifact and log checkpoint is committed and pushed to that branch, never to the integration branch. A failed push pauses the workflow until you decide.
- **Interruptions.** Invoke the workflow again for the feature, and it continues from the task log and Git.
- **Merging.** After acceptance, Orchestrator gives one conventional squash-commit message and you merge. No agent merges, force-pushes or deploys.
- **Versions.** 2.1.0 applies to new work, logs written by 2.0.0 stay valid, and a resumed feature keeps its recorded version. Pre-2.0 logs aren't supported: Orchestrator stops for your direction instead of migrating them.

Both integrations implement the same protocol and task log through their own contracts, which hold the full rules: the protocol ([Codex](.codex/skills/orchestrator-flow/references/workflow-protocol.md), [Claude Code](.claude/skills/orchestrator-flow/references/workflow-protocol.md)), with `assurance.md`, `workflow-recovery.md`, `implementation-phases.md` and the role contracts beside it.

## Setup

### Codex setup: link the skill

Keep this checkout available and link its skill folder into your Codex skills folder. These commands assume the destination doesn't exist yet and its parent does; inspect any existing installation before changing it.

```sh
ln -s "[ORCHESTRATOR_REPO_PATH]/.codex/skills/orchestrator-flow" ~/.codex/skills/orchestrator-flow
```

In PowerShell:

```powershell
$skillSource = Join-Path '[ORCHESTRATOR_REPO_PATH]' '.codex/skills/orchestrator-flow'
$skillDestination = Join-Path $env:USERPROFILE '.codex/skills/orchestrator-flow'
New-Item -ItemType SymbolicLink -Path $skillDestination -Target $skillSource
```

The helper scripts need Python 3.10+ and the declared dependency, `jsonschema>=4.18,<5`. Install it once from the checkout into the environment that will run them, and use the same interpreter (`python3`, or `python` on Windows) for setup and for the helpers. Revisit this when `scripts/requirements.txt` changes. It's workflow setup: don't add the dependency to consuming projects.

```sh
python -m pip install -r .codex/skills/orchestrator-flow/scripts/requirements.txt
```

The skill's `VERSION` and `templates` entries are real relative symlinks to `../../../VERSION` and `../../../templates`. On Windows, Git needs permission to create symlinks (an administrator shell or a supported Developer Mode setup) and `core.symlinks=true`:

- For a new checkout, use `git clone --config core.symlinks=true <REPOSITORY_URL> <CHECKOUT_PATH>`.
- In an existing checkout, `git config --local core.symlinks true` doesn't convert links already flattened into files. Repair them as real relative symlinks before using the skill.
- `Get-Item <SKILL_PATH>/VERSION,<SKILL_PATH>/templates | Format-Table Name,LinkType,Target` should show `SymbolicLink` and the targets above.

A broken link, or a regular file holding a relative path, is a setup error; there is no text-pointer or copy fallback.

### Claude Code setup: link the skill and agents

The integration is the [Orchestrator Flow skill](.claude/skills/orchestrator-flow/SKILL.md) plus six subagents in [.claude/agents/orchestrator-flow](.claude/agents/orchestrator-flow):

| Agent | Role |
| --- | --- |
| `flow-planner` | Planner: requirements, design and tasks |
| `flow-architect` | Architect: read-only specification review |
| `flow-coder` | Coder: implementation, tests, documentation and task progress |
| `flow-reviewer` | Reviewer: read-only implementation review |
| `flow-explorer` | Exploration and research helper, started by a lead |
| `flow-runner` | Test and check runner, started by a lead |

The main conversation is Orchestrator. It starts each lead as a background subagent with the feature's accepted model and effort, continues it across approvals and repairs by its agent ID, and records every return straight from the subagent's transcript, so large returns are never copied by hand. Leads start their own helpers, which Claude Code runs asynchronously; a lead waiting for a helper's report is still working. The `flow-` prefix keeps these agents from colliding with a project's own; you, the task log and the contracts still use the role names.

If you used the pre-v2 Claude Code integration, [migrate it](#upgrading-from-the-pre-v2-claude-integration) first. Then link the two folders. Both links are subfolders of your Claude Code folders, so your other skills and agents keep working beside them. These commands assume the links don't exist yet and `~/.claude/agents` is a real directory:

```sh
mkdir -p ~/.claude/skills ~/.claude/agents
ln -s "[ORCHESTRATOR_REPO_PATH]/.claude/skills/orchestrator-flow" ~/.claude/skills/orchestrator-flow
ln -s "[ORCHESTRATOR_REPO_PATH]/.claude/agents/orchestrator-flow" ~/.claude/agents/orchestrator-flow
```

Keep the checkout and link paths free of spaces, because the skill's inline startup check runs its script by an unquoted path. As in the Codex skill, `VERSION` and `templates` are real relative symlinks, and a missing, broken or flattened one is a setup error. The workflow never changes these paths itself.

**Python.** The workflow scripts need Python 3.10+ with `jsonschema`. Create a virtual environment inside the skill, where Git ignores it, and install the requirements into it:

```sh
python3 -m venv "[ORCHESTRATOR_REPO_PATH]/.claude/skills/orchestrator-flow/.venv"
"[ORCHESTRATOR_REPO_PATH]/.claude/skills/orchestrator-flow/.venv/bin/python" -m pip install -r "[ORCHESTRATOR_REPO_PATH]/.claude/skills/orchestrator-flow/scripts/requirements.txt"
```

Every workflow script runs as `<skill-dir>/.venv/bin/python <skill-dir>/scripts/<script>.py`, in the CLI and the desktop app alike. Only the startup check uses `python3`, so that it can report a missing or broken venv, for example after a system Python upgrade, with the commands that recreate it. Don't add this dependency to consuming projects.

**Version.** Orchestrator Flow requires **Claude Code 2.1.296 or newer**. Every `/orchestrator-flow` invocation, including a resume, first runs `scripts/check_claude_code.py`, which reports the version of the Claude Code actually running the session and stops the workflow with an update message when it's older. The CLI and the desktop app run separate copies of Claude Code: check the CLI with `claude --version` and update it with `claude update`; the desktop app's copy changes only when you update the Claude app. If the check can't run as part of the skill, Orchestrator runs it itself, and asks you before continuing when the version stays unknown.

Windows setup for Claude Code isn't covered yet.

#### Permissions

Auto mode, Claude Code's default starting mode, is recommended for workflow sessions, because long runs continue while you're away. Switch modes with Shift+Tab in the CLI or the mode selector in the desktop app, or set `defaultMode` in your settings. What to expect:

- When a role reads the skill's references outside the project, Claude Code may show its out-of-project read prompt. Its "keep allowing" option is saved permanently and covers every read outside a project, in all sessions, not just this skill's. Instead, add the two `Read` rules from the allow list below, even in auto mode: rules are checked before the mode decides, so the skill's reads go through without the prompt and nothing broad is saved.
- Checkpoint pushes to the feature branch run without a prompt.
- The classifier can block an action, and the agent reports the block with its rule name. After three blocks in a row or twenty in total, auto mode falls back to prompts and the run waits for you.
- If the classifier flags a role's report, Orchestrator shows you the warning before acting on it.
- The classifier adds latency and, on API or Enterprise billing, token cost. Narrow allow rules for the commands below skip it.

To approve commands yourself, use `acceptEdits` mode with allow rules like these in `~/.claude/settings.json`. The workflow's commands use the skill's absolute link path, and Bash rules match command text as written, so spell that path out, replacing `/Users/you` with your home directory. Claude Code allows a read through a symlink only when both the link and the file it resolves to are allowed, so the second `Read` rule covers the checkout. In `Read` rules a leading `//` marks an absolute path, hence the extra slash before `[ORCHESTRATOR_REPO_PATH]`:

```json
{
  "permissions": {
    "allow": [
      "Read(~/.claude/skills/orchestrator-flow/**)",
      "Read(/[ORCHESTRATOR_REPO_PATH]/.claude/skills/orchestrator-flow/**)",
      "Bash(/Users/you/.claude/skills/orchestrator-flow/.venv/bin/python /Users/you/.claude/skills/orchestrator-flow/scripts/*)",
      "Bash(python3 /Users/you/.claude/skills/orchestrator-flow/scripts/check_claude_code.py)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(git push *)"
    ]
  }
}
```

A typed `/orchestrator-flow` pre-approves its own startup check; the `python3` rule covers a run you confirmed after asking in other words. `Bash(git push *)` also matches force-push variants; add ask or deny rules for them if you want that guard, although no workflow role force-pushes. A background agent's permission prompts appear in the main session and name the agent. Architect, Reviewer and the helpers have no edit tools, but their Bash use stays read-only by contract rather than by enforcement. Headless `claude -p` runs aren't supported, because they deny permission prompts. The workflow never changes the session's permission mode.

### GitHub Copilot and Cursor

These keep their committed integrations and the entry points in the table above: select **Orchestrator** in Copilot's custom-agent selector, or run `/cursor-orchestrate` in Cursor. Neither loads a v2 implementation.

## Using it

### Write a proposal or bug report

These reusable templates apply to all four platforms:

- [Proposal template](templates/proposal-template.md): feature or improvement intent, rationale, settled decisions and important constraints.
- [Bug-report template](templates/bugreport-template.md): observed failure, reproduction, expected correction and relevant preservation boundaries, without requiring a speculative diagnosis.

Each is self-contained, with visible authoring guidance and section expectations, so no earlier document is needed as a style reference. Copy the appropriate template into a completed document in the consuming repository, following its conventions for where artifacts go; don't overwrite the template itself. Remove the template-version line, authoring guidance, examples, instructional text and placeholders, keep the applicable outline, and scale the detail to the work. Each template's integer template version, now 2, advances only when its authoring contract changes, independently of the other template, the workflow version, product releases and spec content versions.

### Start a feature

Invoke the workflow with the completed document's path: `$orchestrator-flow` in Codex, or in Claude Code:

```text
/orchestrator-flow .docs/specs/<feature>/proposal.md
```

Copilot and Cursor keep their own entry points.

In Claude Code the skill starts only when you invoke it; Claude never starts it on its own. If you ask for it in other words and Claude follows the skill without the command, it asks you to confirm first, then runs as if you had typed the command. Typing the command is still the better start for long runs: a skill Claude follows by hand is only a file it read, which may hold up less well through context compaction than an invoked skill.

Claude Code leads run in the background, so you can keep talking to Orchestrator during long runs, for example to answer a question, approve a document or change a setting. `/tasks` lists the running agents. After an interruption, resume the same session (reopen it in the desktop app, or run `claude --resume` in the CLI) and run `/orchestrator-flow` again; Orchestrator continues each lead by its agent ID.

### Configuration

On first setup, Orchestrator establishes repository defaults with you in the consuming repository's committed `.orchestrator-flow.json`; don't put them in `AGENTS.md`. The defaults set an assurance level and, separately, a model and effort for Planner, Architect, Coder, Reviewer and helpers, with an optional separate assignment for exploration helpers.

At the start of each feature, Orchestrator reads the defaults, assesses the proposal and recommends a complete configuration with a reason for each choice. You accept it or override any part. The accepted configuration is recorded in the task log before Planner runs, and it governs on resume. Changing the defaults affects later features; changing a running feature's settings takes a recorded override, and accepting a feature's settings never changes the defaults.

Suggested Claude Code defaults:

```json
{
  "assurance_level": "standard",
  "capability_defaults": {
    "claude-code": {
      "planner": {"model": "opus", "reasoning_effort": "xhigh"},
      "architect": {"model": "opus", "reasoning_effort": "max"},
      "coder": {"model": "opus", "reasoning_effort": "high"},
      "reviewer": {"model": "opus", "reasoning_effort": "max"},
      "exploration_helpers": {"model": "sonnet", "reasoning_effort": "medium"},
      "helpers": {"model": "haiku", "reasoning_effort": "medium"}
    }
  }
}
```

Claude Code's models are the short names `opus`, `sonnet`, `haiku` and `fable`. A short name resolves to the newest model in its family, or to the session's own model version when the session uses that family, so the log records the name chosen rather than an exact model version. Efforts are `low`, `medium`, `high`, `xhigh` and `max`, and the log always records an explicit effort. `exploration_helpers` assigns the exploration and research helpers, and `helpers` the test and check runners; without `exploration_helpers`, `helpers` covers both. These are defaults, not rules: Orchestrator may recommend Fable for a hard feature's Planner, Architect or Reviewer, or medium effort for a routine feature's Coder. Fable costs more than Opus, can bill usage credits and falls back to another model automatically when its safety classifiers flag a request; choosing it records that as an accepted limitation. `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` and `CLAUDE_CODE_EFFORT_LEVEL` override per-role choices; the startup check reports them and Orchestrator asks you to accept or remove them.

An illustrative Codex default file follows. Replace `YOUR_AVAILABLE_MODEL` and confirm the supported effort values in your Codex configuration; these are examples, not a model fallback chain or a claim of availability. Codex keeps a single `helpers` assignment, so configure all five roles:

```json
{
  "assurance_level": "standard",
  "capability_defaults": {
    "codex": {
      "planner": {"model": "YOUR_AVAILABLE_MODEL", "reasoning_effort": "high"},
      "architect": {"model": "YOUR_AVAILABLE_MODEL", "reasoning_effort": "high"},
      "coder": {"model": "YOUR_AVAILABLE_MODEL", "reasoning_effort": "high"},
      "reviewer": {"model": "YOUR_AVAILABLE_MODEL", "reasoning_effort": "high"},
      "helpers": {"model": "YOUR_AVAILABLE_MODEL", "reasoning_effort": "medium"}
    }
  }
}
```

A role prompt alone doesn't enforce a model or effort. For Codex clients supporting custom-agent TOML files, create one file per delegated role under the consumer's `.codex/agents/` or `~/.codex/agents/`. For example, `.codex/agents/flow-planner.toml`:

```toml
name = "flow_planner"
description = "Planner for explicitly requested Orchestrator Flow work."
model = "YOUR_AVAILABLE_MODEL"
model_reasoning_effort = "high"
developer_instructions = """
Follow the Planner contract, common essentials, applicable assurance and
project guidance supplied by Orchestrator. Return bounded structured outputs;
Orchestrator owns user gates and the task log; Planner publishes its artifacts.
"""
```

Create corresponding Architect, Coder, Reviewer and helper definitions with the accepted assignments. A custom file's model and effort can take precedence over spawn settings, so keep it consistent with the feature's configuration, including overrides. Where the native spawn interface exposes model and effort directly, use those controls without a conflicting custom profile. Confirm the effective assignment before work. See [official Codex subagent configuration](https://learn.chatgpt.com/docs/agent-configuration/subagents).

If an assignment can't be honored, or a lead or helper reaches a model limit, Orchestrator pauses the affected work and asks whether to choose another assignment or wait. It never silently falls back or changes assurance with a model substitution. An explicit `platform_default` value or a `not_supported` effort is a native limitation that Orchestrator discloses for you to accept. The configuration schema also accepts `github-copilot` and `cursor` keys, which don't imply v2 support in those integrations.

The review-disposition policy is chosen per feature and recorded in the task log, not in the defaults. The built-in `spec_user_code_auto` has you decide on Architect's findings before Planner revises, while routine in-scope repairs after Reviewer's findings go ahead; `all_user` and `within_scope_auto` are the alternatives. Every policy keeps material document approvals, product decisions, must-fix exceptions, loop limits and operational authorization with you.

### Assurance

| | Basic | Standard | Maximum |
| --- | --- | --- | --- |
| Initial review | Complete relevant spec and implementation | Complete relevant spec and implementation | Complete exhaustive review |
| Follow-up | Focused, expanding when consequences/evidence warrant | Focused, affected or full according to impact | Comprehensive on each required pass |
| Remediation | Practical benefit, likelihood, consequences and total workflow cost | Stronger presumption toward robustness/repair | Rigorous repair; any deferral needs justification |
| Further repair gate | Before a second repair-and-re-review cycle | Before a third | Rigorous loops with stalled-loop safeguards |

Each feature has one assurance level, set separately from the roles' models and efforts. It follows the feature's consequences, such as exposure and reversibility, and your preference, not its technical difficulty. Every level reviews the complete relevant work; higher levels add scrutiny, not coverage. Findings describe actual behavior and its consequences for your project. A must-fix finding blocks acceptance unless you decide otherwise, while nit-only reviews are accepted at every level, with the nits recorded as known issues. The assurance rubric ([Codex](.codex/skills/orchestrator-flow/references/assurance.md), [Claude Code](.claude/skills/orchestrator-flow/references/assurance.md)) sets out classification, acceptance, task boundaries and proportionate test execution.

### Standalone roles

In Claude Code, each lead can be used without Orchestrator. Ask for it by name in any session, for example "use flow-reviewer to review these changes"; it runs as a subagent and returns its questions to that session. Or start a session as the role with `claude --agent flow-reviewer`, and it asks you directly. Standalone use never creates orchestration approvals.

## Upgrading from the pre-v2 Claude integration

The previous Claude Code integration linked the whole `~/.claude/agents` directory to this checkout and linked a single `~/.claude/commands/orchestrate.md`. Migrate that installation before adding the new links: while `~/.claude/agents` is itself a symlink to this checkout, `mkdir -p` succeeds silently and the agents link would be created inside the checkout instead. Check with `ls -ld ~/.claude/agents ~/.claude/commands/orchestrate.md`, then:

```sh
rm ~/.claude/agents                      # only when it is a symlink to this checkout
mkdir ~/.claude/agents
rm ~/.claude/commands/orchestrate.md
```

Then follow the [Claude Code setup](#claude-code-setup-link-the-skill-and-agents). Features started under the old `/orchestrate` workflow can't continue under v2, and their logs remain unsupported.

## Project coding guidance

[Directives/codingAgentDirectives.md](Directives/codingAgentDirectives.md) is an optional starting point for a project's coding conventions on all four platforms. Copy it to a suitable place in the consuming repository, keep the relevant language sections, and customize its frameworks, tooling and conventions. Name that project-owned file in the project's native instruction file or README so the chosen platform's agents can find it, and maintain it independently of the workflow installation. Workflow policy, such as assurance, approvals, task ownership and recovery, belongs in the workflow contracts, not in the coding directives. Codex and Claude Code follow this separation; the Copilot and Cursor integrations still have their existing Directives references.

## More

- **Contracts:** each skill's `SKILL.md` and `references/` folder ([Codex](.codex/skills/orchestrator-flow/references), [Claude Code](.claude/skills/orchestrator-flow/references)) hold the full rules for the protocol, assurance, recovery, implementation phases and each role.
- **[AGENTS.md](AGENTS.md):** maintaining this repository, its layout and its validation commands.
- **[tests/README.md](tests/README.md):** the focused test suite.
- **[tests/live/](tests/live/README.md):** the [Codex live kit](tests/live/codex/README.md), the [Claude native test](tests/live/claude/README.md) and the [material they share](tests/live/common/README.md).
- **[.docs/](.docs):** the [v2.0.0](.docs/v2.0.0) and [v2.1.0](.docs/v2.1.0) proposals, the [v2.1.0 native-test summary](.docs/v2.1.0/native-test-summary.md) and the [v2.2.0 handoff](.docs/v2.2.0/handoff-orchestrator-flow-v2.2.0.md).
