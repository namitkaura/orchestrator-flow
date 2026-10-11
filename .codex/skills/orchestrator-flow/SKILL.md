---
name: orchestrator-flow
description: Coordinate feature or bug delivery through Planner, Architect, Coder and Reviewer with explicit assurance, approvals, append-only history and feature-branch checkpoints. Use when the user requests the Orchestrator Flow workflow.
---

# Orchestrator Flow for Codex

Use this skill when the user invokes the workflow. Maintaining these source artifacts does not activate it. Read the skill's own VERSION and the selected role contract, plus applicable assurance guidance. Paths here are relative to this skill directory, including through a home-directory installation link.

## Load what the role needs

- End-to-end coordination: `references/orchestrator.md` and the normal `references/workflow-protocol.md`.
- Delegated or standalone work: the selected `references/planner.md`, `architect.md`, `coder.md` or `reviewer.md`; consult relevant protocol sections for approvals, recording and publication.
- All roles: `references/assurance.md`. Maximum review stages additionally read `references/maximum-assurance.md`.
- Interrupted/failed work or uncertain evidence: `references/workflow-recovery.md`.
- Proposed/approved exceptional phases: `references/implementation-phases.md`.
- Structured outputs: the selected `references/wrappers/*.schema.json` and examples. Task-log/configuration schemas and runtime helpers remain in this skill.

VERSION and templates are real relative symlinks to canonical repository resources. Missing, broken or flattened links are setup errors: stop and report them, do not parse text pointers or search outside the skill. Never read a consumer product VERSION as the workflow version. The other platforms retain their native implementations; their v2 updates are deferred.

Follow the consuming project's AGENTS.md/README and project-owned coding directives they identify. Do not automatically load/copy this distribution's reusable coding directives as consumer policy. Inputs may use bundled `templates/proposal-template.md` or `templates/bugreport-template.md`: copy to a completed consumer input, remove authoring/version/example placeholders, preserve the applicable outline, and supply its path.

## Native execution and ownership

Orchestrated Planner, Architect, Coder and Reviewer work requires actual native subagent delegation. Never perform delegated roles virtually or in place. If delegation is unavailable, explain and obtain direction. Standalone use is separate.

Use accepted model/effort through native controls or matching configured agent settings. Check availability and effective overrides; prompt text alone cannot enforce inference settings. Where custom agents expose model and model_reasoning_effort, verify those settings against the accepted feature assignment. Never create a competing profile silently or fall back to a different model. Obtain direction for unavailable controls or usage limits, including helpers.

Capabilities apply prospectively. Continue the same native context at coherent boundaries where supported; a necessary replacement preserves assignment, cumulative baseline, approvals, repair allowances and completed evidence. A checkpoint or setting change does not require a new agent. Keep the actual starting assurance for review evidence even if capability changes in flight.

Orchestrator owns user interaction, configuration, gates, log, known issues and recovery coordination. It uses metadata and structured returns, never product patches or spec/code/test bodies. Planner/Coder own their artifacts and publish natural checkpoints; Orchestrator publishes log decisions. Review roles are read-only. Helpers explore and execute checks, never intentionally edit or publish. Route questions through Orchestrator's native user-input mechanism; preserve context and bound handoffs.

Ordinary Coder checkpoints require no wrapper or acknowledgement. Completion/repair returns are cumulative from the original assignment. Planner returns at draft/approval boundaries; its final tasks draft includes consolidation before tasks approval. Nits never independently block acceptance or require a producer response.

## Validation and delivery essentials

Install `scripts/requirements.txt` once in the Python environment running the helpers; do not add it to consumer dependencies. Use python3 or python on Windows. Validate actual native JSON directly through stdin/in-memory functions. Orchestrator records one actual wrapper with `scripts/validate_orchestrator_artifacts.py record-handoff - --log <task_log> [--workspace <root>]`; event/state metadata and readback checks are internal. Small reporting corrections stay in the same assignment; genuine failures use bounded recovery.

UTF-8 input is required. Set `$OutputEncoding = [System.Text.UTF8Encoding]::new($false)` before PowerShell pipelines carrying literal Unicode. No routine wrapper files, previous-log snapshots, scratch archive or transport-proof handoff. Temporary copies need concrete tool/recovery necessity and leave no durable debris.

Current-body reads use `scripts/read_spec_body.py <path> --offset 0 --max-chars 8000`, continuing until eof; retry truncated chunks from the same offset with a smaller bound. Recovery uses read-only resume-action and checkpoint inspect/recent. The protocol defines validation commands, artifact/log trailers and approval/checkpoint gates.

Record local push-attempt identity before each publishing push. Failed/uncertain delivery globally pauses workflow work and follows the recovery reference. Successful delivery requires no receipt. Do not force-push, merge, create a worktree without explicit instruction, or treat a commit-message request as final acceptance. Explicit feature acceptance, delivered final checkpoint and manual user merge remain separate.
