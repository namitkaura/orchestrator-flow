# Orchestrator workflow: Spec → Architecture Review → Code → Code Review

This repository documents a set of **VS Code custom agents** (stored under `.github/agents/`) that work together to take a feature from a rough idea through:

1. **Spec creation / revision** (requirements, design, tasks)
2. **Architecture review of the spec** (structured feedback)
3. **Implementation** (test-driven coding)
4. **Code review** (structured feedback and acceptance)

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