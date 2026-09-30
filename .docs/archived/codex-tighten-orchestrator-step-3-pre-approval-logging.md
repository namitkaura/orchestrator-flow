# Proposal: Tighten Orchestrator Step 3 Pre-Approval Logging

## Problem

The orchestrator workflow currently allows ambiguity around Planner outputs during initial spec creation. Step 3 says `spec-created` should only be recorded after spec artifacts are approved, but an orchestrator may mistakenly log an early Planner draft as `spec-created` before user approval, then log another `spec-created` after approval.

This creates duplicate `spec-created` events and breaks the intended meaning of the task log.

## Proposed Update

Clarify that during initial spec creation, Planner draft iterations before explicit user approval are not workflow state transitions and must not update `task_log.json`.

## Changes to `references/orchestrator.md`

### Update Step 2 / Step 3 wording

Add this clarification under Step 3:

```markdown
Initial spec creation approval gate:

- During initial spec creation, Planner may return one or more draft `spec_change_wrapper` outputs before the user approves all three spec artifacts.
- These pre-approval Planner outputs are transient handoff data only.
- The Orchestrator MUST NOT append `spec-created`, `spec-updated`, `user-change-requested`, or `spec-revision-started` entries for pre-approval draft feedback loops.
- The Orchestrator MUST send user draft feedback back to Planner without changing `task_log.json`.
- The Planner MUST NOT add Revision History entries during these pre-approval draft loops.
- Only after the user explicitly approves `requirements.md`, `design.md`, and `tasks.md` may the Orchestrator append the single `spec-created` event for initial spec creation.
- That `spec-created` event MUST contain a `spec_change_wrapper` that accurately represents the final approved artifacts and all pre-approval Planner changes included in them.
- If multiple pre-approval Planner wrappers were returned, the Orchestrator must either:
  - use the final Planner wrapper if it fully summarizes the approved artifacts and pre-approval feedback, or
  - request a final JSON-only Planner wrapper that summarizes the approved artifacts before recording `spec-created`.
- The Orchestrator MUST NOT synthesize a vague or materially incomplete `spec_change_wrapper` for the approved spec-created event.
