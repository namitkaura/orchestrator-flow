# Repository Guidance

## Purpose

This repository is the source of truth for the Orchestrator Flow workflow and its platform-specific agent and skill artifacts. Integrations run from this checkout through symbolic links; it is not itself a product repository that consumes the workflow.

Maintaining agent or skill artifacts does not by itself activate the workflow they describe. Treat their runtime role restrictions, approval gates, and task-log procedures as contracts being maintained, not as instructions to run that process for repository maintenance. Run the workflow here only when the user explicitly requests it.

The repository contains these native integrations:

- GitHub Copilot: `.github/agents/`
- Claude Code: `.claude/agents/` and `.claude/commands/`
- Codex: `.codex/skills/orchestrator-flow/`
- Cursor: `.cursor/agents/`, `.cursor/commands/`, and `.cursor/rules/`

The current v2 implementation phase is Codex only. Preserve `.claude/`, `.github/`, and `.cursor/` at their committed versions; their v2 updates are deferred. Each platform retains its substantive native instructions and does not load the Codex implementation through adapters.

## Repository Layout

- `Directives/codingAgentDirectives.md` is reusable coding guidance for projects using any of the four platforms: Codex, Claude Code, GitHub Copilot, and Cursor. Users copy and customize it per consuming project. Keep this source document in `Directives/`, outside all platform-specific integration directories. The deferred integrations' existing Directives references remain unchanged until their updates.
- `.docs/` contains repository-level incident reports, proposals, and design notes. These documents do not need to be placed under a feature directory.
- `.docs/v2.0.0/` contains the v2 proposal and local test kit. Its runbook, proposals, and prompts are inputs for a separate user-invoked test run; maintaining them does not authorize launching chats, initializing downstream repositories, or running the consumer workflow here.
- `.docs/v2.0.0/` contains the v2 proposal and local test kit. Its runbook, proposals, and prompts are inputs for a separate user-invoked test run; maintaining them does not authorize launching chats, initializing downstream repositories, or running the consumer workflow here.
- `.docs/archived/` preserves historical proposals, notes, and incident evidence. Archived recommendations may be superseded; consult them as optional background rather than additional requirements when a current proposal consolidates them.
- `.docs/specs/{feature}/` is the runtime spec convention documented for downstream repositories that adopt this workflow; it is not required for this repository's own notes.
- `templates/` contains the canonical reusable proposal and bug-report templates for all four platforms, with their own authoring guidance and integer template versions. Keep reusable templates distinct from completed input documents.
- `.codex/skills/orchestrator-flow/references/` contains the role contracts, schemas, wrapper examples, and supporting references required by the Codex skill.
- `.codex/skills/orchestrator-flow/scripts/` contains the required runtime validation, replay, spec-reader, and checkpoint utilities, with their declared dependencies. These are part of the installed skill, not development test scripts.
- `tests/` contains repository development tests and fixtures, outside all platform-specific integration directories.
- `.codex/skills/orchestrator-flow/` keeps its instructions, UI metadata, references, and runtime scripts together. Its `VERSION` and `templates` entries are real relative symlinks to the canonical root resources. Installation links the entire skill directory into the user's Codex skills directory; the checkout remains the source. There is no copy/export installation or separate shared runtime.

## Change Guidelines

- When implementing a user-selected proposal, treat its agreed changes as the target behavior and inspect current contracts to preserve unaffected behavior. Existing contracts do not veto intentional changes specified by that proposal. Raise genuine contradictions or unresolved user-visible decisions rather than silently substituting another policy. Proposed runtime behavior does not automatically govern the repository maintenance session implementing it.
- Keep this phase's changes within Codex and the related repository documentation/tests. Do not modify the deferred platform directories to satisfy stale tests or synchronize them with Codex v2. Future platform changes require their own plan using their native mechanisms and substantive role instructions.
- For all four platforms, coding directives are project-owned guidance, separate from the workflow installation. Each integration follows the consuming project's own instructions and any project-owned coding directives they identify. Keep the reusable `Directives/codingAgentDirectives.md` focused on general and language-specific coding guidance; do not add Orchestrator Flow policy or bundle the reusable source as mandatory runtime guidance. Workflow policy belongs in each platform's workflow contracts. Preserve the deferred integrations' existing references during this Codex-only phase; align them with this common policy when their updates are undertaken.
- For Codex changes, keep `SKILL.md`, role references, JSON schemas, wrapper examples, and validation scripts consistent whenever the change affects more than one of those artifacts.
- Keep paths embedded in distributed agent instructions workspace-relative and POSIX-style unless a setup instruction explicitly requires a machine-local path.
- For every platform, keep workflow resource access inside that integration's own directory. Expose required canonical VERSION and template resources through real relative symlinks recorded by Git as mode `120000`; do not parse text placeholders, search outside the integration, or add copy/export fallbacks. This common installation policy does not authorize changing the deferred integrations in this phase or sharing Codex runtime files with them. A checkout with broken or flattened links needs its setup repaired. Consumer project files remain the workflow's normal inputs.
- Keep JSON valid and preserve the contract between schemas and their example wrappers.
- Keep repository notes in `.docs/` organized by clear filenames. Use a subdirectory only when the volume or category of notes justifies it; do not move repository notes into `.docs/specs/` merely to make them look like consumer feature specs.
- Do not modify downstream projects or machine-local installation paths from this repository unless the user explicitly requests that setup work.

## Validation

There is no package build or general application test suite in this repository. Codex v2 has a focused Python protocol, schema, document-reader, checkpoint, and linked-resource test suite. Retain `scripts/requirements.txt`: install its declared dependencies once in the Python environment used for the workflow helpers with `python -m pip install -r .codex/skills/orchestrator-flow/scripts/requirements.txt`, revisiting setup when those requirements change. This does not add dependencies to each consuming project. Run targeted checks appropriate to the files changed:

- `git diff --check`
- `python3 .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py task-log <path-to-task_log.json>`
- `python3 .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py spec-change-wrapper <path>`
- `python3 .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py spec-review-wrapper <path>`
- `python3 .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py change-wrapper <path>`
- `python3 .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py review-wrapper <path>`
- `python3 .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py repository-config <path>`
- `python3 .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py resume-action <path-to-task_log.json> [--observations <path>]`
- `python3 -B -m unittest discover -s tests -v`

Use `task-log --previous <previous-log>` to check append-only updates and `--workspace <consumer-root>` to verify current document metadata and consolidated task completion. `resume-action` and `checkpoint_state.py inspect` are read-only. The checkpoint helper's `attempt` and `failure` operations only record local Git-metadata evidence and never commit, push, or retry. Exercise Git recovery tests only in their temporary repositories/local bare remotes; these tests do not authorize Git workflow operations in this maintenance checkout.

Resource tests verify the Codex skill's real relative links, local version/schema access from a foreign working directory, and preservation of link entries through a temporary Git push/clone. Tests that create symlinks report a skip when the test process lacks permission; the actual checkout's resource-link checks must still pass. Report such skips as validation limitations, never as support for text pointers. Check resource entries with `git ls-files --stage` when staging them; each must have mode `120000`. Windows clones require symlink privileges and `git clone --config core.symlinks=true`.

On Windows, use the equivalent `python` command when `python3` is unavailable. For JSON-only changes without a relevant workflow artifact, also verify parsing with the available JSON tooling.

The artifact-validator commands above check individual inputs; passing them alone does not demonstrate that a changed workflow behaves correctly. For validator or schema changes, exercise relevant valid and invalid examples. For workflow-semantic changes, verify affected transition, approval, interruption, and resume scenarios, including failure handling where applicable. Keep checks proportionate to the change, and update this guidance when new validation commands or test suites are introduced.

## Git Workflow

- Keep changes focused and review the complete diff before finalizing.
- Do not create commits, branches, pull requests, or push to a remote unless the user explicitly asks.
- Implementing a consumer workflow that creates branches or checkpoints does not itself authorize those Git operations in this repository's maintenance session.
- Before handing work back, report validation performed and leave unrelated existing changes untouched.
