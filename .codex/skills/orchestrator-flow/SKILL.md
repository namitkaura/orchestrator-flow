---
name: orchestrator-flow
description: Coordinate feature or bug delivery through Planner, Architect, Coder and Reviewer with explicit assurance, approvals, append-only history and feature-branch checkpoints. Use when the user requests the Orchestrator Flow workflow.
---

# Orchestrator Flow

This skill implements Orchestrator Flow v2 for Codex. Its role contracts, schemas, examples, and runtime helpers live in this skill's `references/` and `scripts/` directories. Maintaining these source files does not activate the consumer workflow.

## Load the contract

Read this skill's bundled `VERSION`, `references/workflow-protocol.md`, `references/assurance.md`, and the selected role contract in full. All paths below are relative to this skill directory, including when it is reached through a home-directory symlink. `VERSION` and `templates` must be real relative symlinks to the canonical repository resources, resolving to a readable version file and template directory. If either link is missing, broken, or flattened into a text file, report the setup error and stop; do not interpret text as a resource pointer or search outside the skill. Use the skill's workflow version, never a consuming repository's product version.

Follow the consuming repository's AGENTS.md, README and any project-owned codingAgentDirectives.md they identify. Such coding directives are optional project policy, not a bundled workflow resource. Do not load the distribution's reusable directives as project policy or copy them into the project automatically.

- End-to-end coordination: `references/orchestrator.md`.
- Standalone or delegated roles: `references/planner.md`, `references/architect.md`, `references/coder.md`, `references/reviewer.md`.
- Schemas: `references/task_log_schema.json`, `references/repository_config.schema.json`, `references/common.schema.json`, and the four `references/wrappers/*.schema.json` files.
- Inputs: bundled `templates/proposal-template.md` and `templates/bugreport-template.md`. Copy into a completed consumer input; remove template guidance/version/placeholders, preserve the outline, and supply its path.

## Codex delegation and capability

During orchestrated execution, you MUST use actual native subagent delegation for Planner, Architect, Coder and Reviewer. Never execute those contracts in place or label your own work a virtual subagent result. If delegation is unavailable, explain the limitation and obtain direction. Standalone role use remains supported as a separate user invocation.

Load recorded feature capability and use the native invocation's supported model/reasoning controls or matching configured agent settings. Check actual availability; do not let inherited settings silently defeat explicit assignments. If model/effort cannot be selected or a limit is reached, pause affected work and obtain the user's alternative or wait decision. Helpers use their own recorded assignment; no automatic fallback.

For clients exposing custom agents, the consuming `.codex/agents/*.toml` or personal `~/.codex/agents/*.toml` defines `model` and `model_reasoning_effort` alongside `name`, `description`, and `developer_instructions`. Check those effective settings against the feature log: a custom definition can override spawn defaults. Otherwise use the available native spawn model/effort controls. Do not create a competing profile silently or assume prompt text changes inference settings.

Pass the full role contract and bounded authoritative context. Retain native agent handles and continue the same delegated role context across checkpoints when supported. If a capability change requires another agent, preserve prior completed output and evidence. A new checkpoint does not require a fresh agent or full rediscovery.

Orchestrator handles all user questions through the available native question mechanism. Do not depend on hidden role conversations or terminal input for approvals. It owns initialization, log/configuration, known issues and recovery coordination. Planner and Coder publish their own artifact checkpoints; Orchestrator publishes authoritative log updates. Review roles are read-only, and helpers neither intentionally edit project files nor publish. Serialize Git ownership through the active producer and coherent yields, as defined in `references/workflow-protocol.md`.

Ordinary Coder checkpoints require no wrapper or acknowledgement. Coder returns the cumulative result at assignment/repair completion; exceptional approved phases use the scoped handoffs in the protocol. Required handoffs contain the actual complete JSON return, not a saved-file pointer. Normal work creates no temporary role artifacts; a concrete tool/recovery necessity is the only exception. Keep unavoidable copies outside durable project content and remove them only after validated durable recording.

## Validate and resume

Install declared dependencies once using `python -m pip install -r <skill>/scripts/requirements.txt` in the Python environment that runs these helpers, where `<skill>` is this skill directory. Revisit setup when requirements change; do not add this workflow dependency to each consuming project. Use `python3` where appropriate, `python` on Windows. Preserve the five artifact-validator commands, plus `repository-config` and read-only `resume-action`. Use `--previous` for append-only validation and `--workspace` for actual document metadata. Read current spec bodies with `scripts/read_spec_body.py`; obtain checkpoint delivery observations with `scripts/checkpoint_state.py inspect` before dependent work. The linked skill contains every required runtime script and schema; development tests remain in the source checkout's `tests/` directory.

Primary JSON inputs accept `-` for stdin, including candidate logs with `--previous <authoritative-log>`. Validate the actual native return in memory or through stdin before recording it; do not save wrappers or log snapshots just to reread them. Observations may use stdin when the log is a file. Use `read_spec_body.py <path> --offset 0 --max-chars 8000` for bounded current-body reads, and `checkpoint_state.py recent` for metadata-only recovery inspection. See the protocol for continuation cursors, provenance checks and scoped resume results.

Unsupported historical logs stop before mutation. Explicit user acceptance, successful final checkpoint delivery and manual user merging remain separate. Do not merge, force-push, create worktrees without explicit instruction, or interpret a commit-message request as completion authority.
