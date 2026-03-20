# Orchestrator workflow: Spec → Architecture Review → Code → Code Review

This repository documents an orchestrator workflow that supports **GitHub Copilot, Claude Code, Codex, and Cursor**.

The repository contains platform-specific agent and skill artifacts, while preserving one shared workflow contract across all supported platforms:

| Platform | Repository-internal artifact location | Notes | Status |
|---|---|---|---|
| GitHub Copilot | `.github/agents` | VS Code custom agent contracts (`*.agent.md`) | Works the best and is the most consistent and stable |
| Claude Code | `.claude/agents` | Claude agent contracts | Works fairly well though not quite as consistent or as robust as the GitHub Copilot version |
| Codex | `.codex/skills/orchestrator-flow/references` | Codex orchestrator skill reference contracts - Works but doesn't use sub-agents and is inconsistent  | All work is run as a skill in the main agent which switches roles - work in progress |
| Cursor | `.cursor/agents` (`planner`, `architect`, `coder`, `reviewer`) + `.cursor/rules/Orchestrator.mdc` | Orchestrator uses the **Task** tool; rule applies under `.docs/specs/**` or via **`/cursor-orchestrate`** (not Claude `/orchestrate`) | `task_log.json` schema matches GitHub; models set per agent YAML |

These platform-specific paths represent implementation-location differences only; they do not change the base workflow contract.

This repository documents platform-specific artifacts that work together to take a feature from a rough idea through:

1. **Spec creation / revision** (requirements, design, tasks)
2. **Architecture review of the spec** (structured feedback)
3. **Implementation** (test-driven coding)
4. **Code review** (structured feedback and acceptance)

In this opening section, `.github/agents` contract paths are shown as the **GitHub Copilot-specific** implementation detail for loading the shared workflow roles in VS Code.

If you are using **Claude Code**, **Codex**, or **Cursor**, use the later sections in this README—**Setup options for other projects**, **Setup commands**, and **Usage by platform**—for harness-specific artifact locations, setup options, and usage commands.

This README is intentionally scoped to the five agent contracts that define that workflow:

- `.github/agents/Orchestrator.agent.md`
- `.github/agents/Planner.agent.md`
- `.github/agents/Architect.agent.md`
- `.github/agents/Coder.agent.md`
- `.github/agents/Reviewer.agent.md`

## High-level design

The workflow is coordinated by **Orchestrator**, which delegates bounded work to the other four agents via `runSubagent`:

- **Planner** creates or revises spec artifacts under `.docs/specs/{feature}/`:
  - `requirements.md`
  - `design.md`
  - `tasks.md`
- **Architect** reviews the spec (requirements/design/tasks) and returns structured review feedback.
- **Coder** implements the feature using the spec as the source of truth (with TDD), and returns a structured change summary.
- **Reviewer** reviews the implementation against the spec, re-runs checks as needed, and returns structured feedback.

Orchestrator records workflow state in a per-feature `task_log.json` file next to the spec artifacts and uses it to support resuming work across sessions.

## Agent roster (the five workflow contracts)

### Orchestrator

File: `.github/agents/Orchestrator.agent.md`

Orchestrator is the **central coordinator**. It:

- Is the **only** agent allowed to call other agents via `runSubagent`.
- **Does not read or interpret** spec contents; it treats spec paths as opaque references and delegates interpretation to Architect/Coder/Reviewer.
- Owns the feature’s `task_log.json` and is the **only** agent allowed to create/update it.
- Never creates commits, branches, or PRs; you review and commit manually.

Orchestrator accepts two input forms:

1. **Proposal-first**: you provide free-form feature text or a proposal file path.
2. **Start from an existing spec**: you provide a spec directory or explicit file paths to `requirements.md`, `design.md`, and `tasks.md` (plus an optional change request).

In both cases, Orchestrator:

1. Creates/updates `<feature_dir>/task_log.json` next to the spec artifacts (typically `.docs/specs/{feature}/task_log.json`).
2. Runs the **Spec loop** until the spec is accepted:
   - Planner → Architect → (Planner → Architect …)
3. Runs the **Implementation loop** until the implementation is accepted:
   - Coder → Reviewer → (Coder → Reviewer …)

Both loops support a “deferred with justifications” path that requires explicit user confirmation before proceeding.

### Planner

File: `.github/agents/Planner.agent.md`

Planner is the **spec authoring** agent. In Orchestrator-invoked runs it returns a JSON `spec_change_wrapper` that includes:

- `feature` (kebab-case)
- `feature_dir` (relative path, typically `.docs/specs/{feature}`)
- `requirements_ref`, `design_ref`, `tasks_ref`
- `notes`
- `user_request`

Planner is **forbidden** from editing `task_log.json`.

### Architect

File: `.github/agents/Architect.agent.md`

Architect is the **spec review** agent. It reads the spec artifacts and returns a JSON `spec_review_wrapper` containing:

- `accepted`: one of `"true" | "false" | "conditional"`
- `issue_details`: `must_fix`, `should_fix`, `nit`
- `notes`

Architect is **forbidden** from editing `task_log.json`.

### Coder

File: `.github/agents/Coder.agent.md`

Coder is the **implementation** agent. It reads `requirements.md`, `design.md`, and `tasks.md`, implements tasks incrementally (with tests), and returns a JSON `change_wrapper` containing:

- `changed_files`, `new_files`, `deleted_files`
- `cli_runs`
- `test_results`
- `implementation_details`
- `notes`

Coder is **forbidden** from editing `task_log.json`.

### Reviewer

File: `.github/agents/Reviewer.agent.md`

Reviewer is the **code review** agent. It reviews the implementation against the spec and returns a JSON `review_wrapper` containing:

- `accepted`: one of `"true" | "false" | "conditional"`
- `issue_details`: `must_fix`, `should_fix`, `nit`
- `test_results`
- `notes`

Reviewer is **forbidden** from editing `task_log.json`.

## `task_log.json` state tracking

For each feature, Orchestrator maintains:

`.docs/specs/{feature}/task_log.json`

At a high level it:

- Stores pointers to spec artifacts (`requirements_ref`, `design_ref`, `tasks_ref`).
- Tracks a workflow `status` and an append-only `history` of timestamped events.
- Provides enough information to resume work after restarts without relying on in-memory chat history.

The exact schema, allowed `status` values, and allowed `event` values are defined in `.github/agents/Orchestrator.agent.md`.

## Using this workflow in VS Code

1. Configure VS Code custom agents to load the five agent contracts under `.github/agents/`.
2. Start with **Orchestrator** and provide either:
   - A proposal (text or proposal file path), or
   - A spec directory / explicit spec file paths (and optionally a change request).
3. Review the generated/updated spec files, code changes, and `task_log.json` as the workflow proceeds.
4. Create commits/PRs manually when you’re satisfied.

## Setup options for other projects

You can adopt this workflow in another repository using one of these setup approaches:

- **project-local copy**: copy the relevant platform artifacts into each destination project.
- **home-directory copy**: copy platform assets into a machine-level location in your home directory.
- **home-directory symlink**: keep this repository as a source of truth and link home-directory entries to it.

For machine-local setup, treat home-directory paths as **external setup paths** (`~/.claude/agents`, `~/.codex/skills/orchestrator-flow`, and similar). These paths are machine-local configuration, are not repository-committed artifacts, and are not repository path-existence checks.

### Placeholder definitions

- `[ORCHESTRATOR_REPO_PATH]`: full absolute path to this repository root on your machine.
- `[TARGET_PROJECT_PATH]`: full absolute path to a destination project where you want to consume orchestrator assets.

### Platform-specific setup guidance

- **GitHub Copilot**: configure VS Code `chat.agentFilesLocations` with the full path to `[ORCHESTRATOR_REPO_PATH]/.github/agents`.
- **Claude Code**: use the machine-local path `~/.claude/agents` and point it to this repository's `.claude/agents` artifacts.
- **Codex**: use the machine-local path `~/.codex/skills/orchestrator-flow` and point it to this repository's `.codex/skills/orchestrator-flow` artifacts.
- **Cursor (copy mode)**: copy this repository's `.cursor` directory into each destination project's `.cursor` directory.
- **Cursor (copy mode Directives contract)**: copy this repository's `Directives` directory into the destination project root (sibling of `.cursor`) so `.cursor/agents/Directives -> ../../Directives` resolves correctly.
- **Cursor (symlink alternative)**: create a per-project symlink from the destination project's `.cursor/agents` to `[ORCHESTRATOR_REPO_PATH]/.cursor/agents`.

### Symlink strategy and caveats

This repository supports an optional hub-and-spoke symlink pattern where `Directives/codingAgentDirectives.md` is the shared source of truth and platform folders consume it through relative `Directives` links.
Use relative symlink targets (avoid absolute paths); relative links are required for portability across machines and clones.

Some tools or sandboxed environments may not follow symlinks. If that happens, use a fallback by copying or syncing the `Directives` content directly into the destination project layout.

## Setup commands

These are **POSIX** shell command snippets. On **Windows**, use equivalent **PowerShell** or Command Prompt commands, or run the POSIX commands through **WSL** or **Git Bash**.

### Repository-committed commands

Use these in this repository to create in-repo `Directives` symlinks for each platform directory:
Always keep these link targets relative so the repository setup remains portable across machines and clones.

```sh
ln -s ../../Directives .claude/agents/Directives
ln -s ../../../../Directives .codex/skills/orchestrator-flow/references/Directives
ln -s ../../Directives .cursor/agents/Directives
ln -s ../../Directives .github/agents/Directives
```

### Machine-local commands

Use these for machine-local setup paths that are not committed:

```sh
ln -s "[ORCHESTRATOR_REPO_PATH]/.claude/agents" ~/.claude/agents
ln -s "[ORCHESTRATOR_REPO_PATH]/.codex/skills/orchestrator-flow" ~/.codex/skills/orchestrator-flow
ln -s "[ORCHESTRATOR_REPO_PATH]/.cursor/agents" "[TARGET_PROJECT_PATH]/.cursor/agents"
```

## Usage by platform

Use the same workflow contract across platforms, with platform-specific invocation entry points:

- **GitHub Copilot**: select the appropriate custom agent mode in the **Copilot Chat agent selector**, then provide your prompt.
- **Claude Code**: run `/orchestrate` followed by your prompt.
- **Codex**: select the `Orchestrator Flow` skill, then provide your prompt.
- **Cursor**: run `/orchestrate` followed by your prompt.

## Guardrails & design goals

- Specs are the source of truth: Planner writes them; Architect reviews them; Coder/Reviewer implement and validate against them.
- Orchestrator coordinates and logs state in `task_log.json` but does not interpret spec contents.
- No agent creates commits/branches/PRs.

## Future improvements
- Add a research agent that can gather context, links, and references based on the feature proposal before calling Planner.
- Add a git commit agent that can create commits based on `task_log.json` summaries, but still requires user approval before committing.
- Add a pull/merge request generation agent that can create PRs based on `task_log.json` summaries, but still requires user approval before merging.
- Add CI integration agent that can run tests and report results back into the Orchestrator workflow.
- Add CD agent that can help with deployment steps based on the completed feature.
- Refine the semantics of how deferred `should_fix` and `nit` items are determined by the Orchestrator in its Steps 6 and 12.