# Cursor Orchestrator

You are running the spec → spec review → code → code review workflow.

1. Treat **`.cursor/rules/Orchestrator.mdc`** as binding for state machine, `task_log.json` schema, and Task tool usage.
2. Use the **Task** tool with `subagent_type`: **`planner`**, **`architect`**, **`coder`**, or **`reviewer`** (foreground) as defined in **`.cursor/agents/`**.
3. Do **not** follow **`.claude/commands/orchestrate.md`** or read **`~/.claude/agents/`** for this run—that path is for Claude Code only.

**User input (feature proposal, spec paths, or change request):**

$ARGUMENTS

Begin the Orchestrator workflow from Step 1 of the rule unless the user is resuming an existing `task_log.json`.
