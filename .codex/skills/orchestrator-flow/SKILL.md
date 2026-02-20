---
name: orchestrator-flow
description: Coordinate feature delivery through a Spec -> Spec Review -> Coding -> Code Review workflow with Planner, Architect, Coder, and Reviewer role contracts and append-only task_log.json tracking. Use when the user wants a GitHub/Claude-style orchestration loop in Codex.
---

# Orchestrator Flow

## Overview

Run a five-role workflow that takes a feature from proposal to reviewed implementation:
1. Planner creates or updates `requirements.md`, `design.md`, and `tasks.md`.
2. Architect reviews the spec and classifies feedback (`must_fix`, `should_fix`, `nit`).
3. Coder implements tasks with tests and returns a structured change summary.
4. Reviewer validates implementation quality and spec alignment.
5. Orchestrator coordinates loops and maintains `task_log.json` as append-only history.

## Workflow Selection

- Use `references/orchestrator.md` for end-to-end coordination.
- Use role files directly for focused work:
  - `references/planner.md`
  - `references/architect.md`
  - `references/coder.md`
  - `references/reviewer.md`

## Artifacts and Contracts

- Spec location: `.docs/specs/{feature}/`
- Required spec docs:
  - `.docs/specs/{feature}/requirements.md`
  - `.docs/specs/{feature}/design.md`
  - `.docs/specs/{feature}/tasks.md`
- Workflow log:
  - `.docs/specs/{feature}/task_log.json`

Use these machine-readable references:
- `references/task_log_schema.json`
- `references/wrappers/spec_change_wrapper.json`
- `references/wrappers/spec_review_wrapper.json`
- `references/wrappers/change_wrapper.json`
- `references/wrappers/review_wrapper.json`

## Delegation Model

Prefer runtime sub-agent handoff when available. If the runtime does not support handoff, run the role contract in-place and treat the result as a virtual sub-agent output while preserving wrapper format and `task_log.json` actor/requestor semantics.

## Guardrails

- Keep all paths workspace-relative and POSIX-style.
- Keep `task_log.json` history append-only.
- Never fabricate timestamps; use UTC.
- Keep wrappers JSON-only when a wrapper is requested.
