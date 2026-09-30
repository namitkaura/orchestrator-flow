# Repository Guidance

## Purpose

This repository is the source of truth for the Orchestrator Flow workflow and its platform-specific agent and skill artifacts. It packages the workflow for use by other repositories; it is not itself a product repository that consumes the workflow.

Maintaining agent or skill artifacts does not by itself activate the workflow they describe. Treat their runtime role restrictions, approval gates, and task-log procedures as contracts being maintained, not as instructions to run that process for repository maintenance. Run the workflow here only when the user explicitly requests it.

The supported integrations are:

- GitHub Copilot: `.github/agents/`
- Claude Code: `.claude/agents/` and `.claude/commands/`
- Codex: `.codex/skills/orchestrator-flow/`
- Cursor: `.cursor/agents/`, `.cursor/commands/`, and `.cursor/rules/`

## Repository Layout

- `Directives/codingAgentDirectives.md` is the shared directive source of truth consumed by the platform-specific artifacts.
- `.docs/` contains repository-level incident reports, proposals, and design notes. These documents do not need to be placed under a feature directory.
- `.docs/archived/` preserves historical proposals, notes, and incident evidence. Archived recommendations may be superseded; consult them as optional background rather than additional requirements when a current proposal consolidates them.
- `.docs/specs/{feature}/` is the runtime spec convention documented for downstream repositories that adopt this workflow; it is not required for this repository's own notes.
- `templates/` contains the canonical reusable proposal and bug-report templates, with their own authoring guidance and integer template versions. Keep reusable templates distinct from completed input documents.
- `.codex/skills/orchestrator-flow/references/` contains Codex role contracts, schemas, wrapper examples, and supporting references.
- `.codex/skills/orchestrator-flow/scripts/` contains Codex artifact-validation utilities.

## Change Guidelines

- When implementing a user-selected proposal, treat its agreed changes as the target behavior and inspect current contracts to preserve unaffected behavior. Existing contracts do not veto intentional changes specified by that proposal. Raise genuine contradictions or unresolved user-visible decisions rather than silently substituting another policy. Proposed runtime behavior does not automatically govern the repository maintenance session implementing it.
- Preserve the shared workflow contract across platforms. When changing workflow behavior, inspect the corresponding Orchestrator, Planner, Architect, Coder, and Reviewer artifacts in each affected platform and update all intentionally affected copies. Keep affected commands, rules, README/setup instructions, and templates consistent with those changes while preserving platform-appropriate implementation mechanisms.
- Treat `Directives/codingAgentDirectives.md` as the shared source of truth. Preserve relative links or symlinks that consume it; do not replace portable repository references with machine-specific absolute paths.
- For Codex changes, keep `SKILL.md`, role references, JSON schemas, wrapper examples, and validation scripts consistent whenever the change affects more than one of those artifacts.
- Keep paths embedded in distributed agent instructions workspace-relative and POSIX-style unless a setup instruction explicitly requires a machine-local path.
- Keep JSON valid and preserve the contract between schemas and their example wrappers.
- Keep repository notes in `.docs/` organized by clear filenames. Use a subdirectory only when the volume or category of notes justifies it; do not move repository notes into `.docs/specs/` merely to make them look like consumer feature specs.
- Do not modify downstream projects or machine-local installation paths from this repository unless the user explicitly requests that setup work.

## Validation

There is no package build or general application test suite in this repository. Run targeted checks appropriate to the files changed:

- `git diff --check`
- `python3 .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py task-log <path-to-task_log.json>`
- `python3 .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py spec-change-wrapper <path>`
- `python3 .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py spec-review-wrapper <path>`
- `python3 .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py change-wrapper <path>`
- `python3 .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py review-wrapper <path>`

On Windows, use the equivalent `python` command when `python3` is unavailable. For JSON-only changes without a relevant workflow artifact, also verify parsing with the available JSON tooling.

The artifact-validator commands above check individual inputs; passing them alone does not demonstrate that a changed workflow behaves correctly. For validator or schema changes, exercise relevant valid and invalid examples. For workflow-semantic changes, verify affected transition, approval, interruption, and resume scenarios, including failure handling where applicable. Keep checks proportionate to the change, and update this guidance when new validation commands or test suites are introduced.

## Git Workflow

- Keep changes focused and review the complete diff before finalizing.
- Do not create commits, branches, pull requests, or push to a remote unless the user explicitly asks.
- Implementing a consumer workflow that creates branches or checkpoints does not itself authorize those Git operations in this repository's maintenance session.
- Before handing work back, report validation performed and leave unrelated existing changes untouched.
