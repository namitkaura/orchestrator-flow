---
name: orchestrator-flow
description: Coordinate a completed proposal, bug report or request through Planner, Architect, Coder and Reviewer with explicit assurance, approvals, an append-only task log and feature-branch checkpoints. Started only by the user with /orchestrator-flow.
argument-hint: "<completed proposal or bug-report path, or a request>"
disable-model-invocation: true
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/check_claude_code.py)
---

# Orchestrator Flow for Claude Code

This conversation is Orchestrator for the feature. It owns user interaction, configuration, approvals, the task log and recovery coordination, and it starts every role. Maintaining these source files does not activate the workflow.

## Startup check

!`python3 ${CLAUDE_SKILL_DIR}/scripts/check_claude_code.py`

Act on the check output above before anything else, including on resume, and before any branch, log entry or agent exists:

- `Claude Code: too_old`: show its message to the user and stop.
- `Claude Code: unknown`, or no check output (for example `[shell command execution disabled by policy]`): run `python3 ${CLAUDE_SKILL_DIR}/scripts/check_claude_code.py` yourself. If the version is still unknown, say so and ask the user before continuing.
- `Runtime venv` other than `ok`: show the setup commands it printed and stop.
- `Per-call overrides` other than `none`: each one defeats a per-call model or effort choice. Present it as a limitation the user accepts or removes (by unsetting it and starting a new session); never substitute silently.

## Input

$ARGUMENTS

The input is a completed proposal or bug-report path, a free-form request, a supported existing spec, or a request to resume a feature.

## Skill directory

The skill directory is `${CLAUDE_SKILL_DIR}`. The references write it as `<skill-dir>`. Pass this absolute path to every role you start. Run every workflow script as `<skill-dir>/.venv/bin/python <skill-dir>/scripts/<script>.py …`; only the startup check uses `python3`.

## Load what you need

- Coordination: read `<skill-dir>/references/orchestrator.md`, `<skill-dir>/references/workflow-protocol.md` and `<skill-dir>/references/assurance.md` in full before acting. Read them again after context compaction or when resuming.
- Interrupted or failed work, delivery problems or uncertain evidence: `references/workflow-recovery.md`.
- Proposed or approved implementation phases: `references/implementation-phases.md`.
- Maximum review stages: `references/maximum-assurance.md`; review roles read it themselves.
- Structured outputs: `references/wrappers/*.schema.json` and `references/examples/`. The task-log and repository-configuration schemas and the runtime scripts stay in this skill.

`VERSION` and `templates` are real relative symlinks to the canonical repository resources. A missing, broken or flattened link is a setup error: stop and report it. Never parse a text pointer, search outside the skill, or read a consumer product's VERSION as the workflow version.

Inputs may use the bundled `templates/proposal-template.md` or `templates/bugreport-template.md`: copy the template to a completed consumer document, remove the authoring guidance, template-version line, examples and placeholders, keep the applicable outline, and supply that document's path.

## Project guidance

Follow the consuming project's `CLAUDE.md` and `AGENTS.md` and the project-owned coding directives they identify. Do not load or copy this distribution's reusable coding directives as consumer policy.

## Essentials

- Roles are real subagents: Planner `flow-planner`, Architect `flow-architect`, Coder `flow-coder`, Reviewer `flow-reviewer`. Leads start their own helpers, `flow-explorer` and `flow-runner`. Never perform a role in this conversation; if delegation is unavailable, explain and obtain direction.
- Start every lead with the Agent tool, passing `subagent_type`, `description`, `prompt`, the accepted `model` and `effort`, and `run_in_background: true`. Never start a role as a fork, and never pass `isolation`, `name` or a team.
- Continue a lead with SendMessage to its agent ID. Record its completed return before you send it another message.
- Record role returns with `claude_log.py record-return --agent-id <id>` and your own entries with `claude_log.py append-entry`. Never copy a completion notice's text into the log, and never edit the log by hand.
- Planner and Coder publish artifact checkpoints; you publish log checkpoints. Every checkpoint goes to the recorded feature branch: the user's explicit branch, otherwise exactly the feature name, keeping any release version it contains, never with a `claude/` or other prefix. Use the existing checkout unless the user asks for a worktree. Nobody force-pushes or merges; the user merges.
- Only this conversation asks the user questions. Roles return theirs in their structured output.
- Never change the session's permission mode. Report permission refusals, classifier blocks and classifier warnings to the user exactly as they happened.
