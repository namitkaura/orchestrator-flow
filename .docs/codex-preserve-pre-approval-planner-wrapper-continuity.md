# Proposal: Preserve Pre-Approval Planner Wrapper Continuity

## Problem

During initial spec creation, the Planner may run multiple pre-approval draft passes before the user approves `requirements.md`, `design.md`, and `tasks.md`.

The current workflow says not to update `task_log.json` during these pre-approval loops, but it does not clearly require the Orchestrator to pass the previous draft `spec_change_wrapper` back to Planner. It also does not clearly require the next Planner wrapper to build on the previous wrapper.

This can cause the final approved `spec-created` wrapper to omit important pre-approval draft context.

## Proposed Update

During pre-approval draft loops, Orchestrator should preserve the latest Planner `spec_change_wrapper` in conversation state and pass it back to Planner on every pre-approval re-request. Planner must return a new wrapper that builds on the prior wrapper and summarizes cumulative draft changes.

Planner must also be explicitly prohibited from adding Revision History entries during pre-approval draft loops.

## Changes to `references/orchestrator.md`

### Add to Step 3: Initial Spec Creation Approval Gate

```markdown
Pre-approval Planner wrapper continuity:

- When Planner returns a draft `spec_change_wrapper` before user approval, the Orchestrator MUST keep it as the latest draft wrapper in conversation state.
- If the user requests pre-approval draft changes, the Orchestrator MUST send the latest draft `spec_change_wrapper` back to Planner along with the user feedback.
- The Orchestrator MUST instruct Planner that the next returned `spec_change_wrapper` must build on the prior wrapper and summarize cumulative pre-approval draft changes, not only the latest small edit.
- The Orchestrator MUST NOT append these pre-approval wrapper outputs to `task_log.json`.
- Only after explicit user approval may the Orchestrator record the final approved `spec_change_wrapper` in the single `spec-created` task-log event.
- If the latest Planner wrapper does not clearly summarize all material pre-approval draft updates, the Orchestrator MUST request a final JSON-only Planner wrapper before recording `spec-created`.
```

### Update Planner invocation template for pre-approval draft feedback

```markdown
For pre-approval draft feedback loops, include:

- latest_draft_spec_change_wrapper
- user_feedback
- explicit instruction:
  - This is still initial spec creation, not a post-approval revision.
  - Do not add Revision History sections or entries.
  - Update the draft spec artifacts as needed.
  - Return a JSON-only `spec_change_wrapper` that builds on the prior wrapper and summarizes the cumulative approved-draft state, including all material pre-approval changes incorporated so far.
```

## Changes to `references/planner.md`

### Add under Orchestrator Mode

```markdown
Pre-approval draft feedback loops:

- If invoked during initial spec creation with a prior draft `spec_change_wrapper`, you MUST treat that wrapper as the continuity baseline for the next draft.
- You MUST update the draft spec artifacts according to the new feedback.
- You MUST return a new JSON-only `spec_change_wrapper` that builds on the prior wrapper.
- The new wrapper's `notes` MUST summarize the cumulative current draft state and all material pre-approval changes incorporated so far, not only the latest edit.
- The new wrapper's `user_request.additional_context` SHOULD mention the prior draft wrapper and the new feedback that was incorporated.
- You MUST NOT modify `task_log.json`.
- You MUST NOT add Revision History sections or entries during pre-approval draft loops, because the spec has not yet been approved and this is not a revision pass.
```

### Add under Revision History Tracking

```markdown
Pre-approval exception:

- Revision History entries are strictly prohibited before initial user approval of all three spec artifacts.
- User feedback before initial approval is part of initial spec creation, not a revision.
- Even if multiple Planner passes occur before approval, do not add Revision History sections or entries.
```

## Acceptance Criteria

1. WHEN Planner returns a pre-approval draft wrapper THEN Orchestrator SHALL retain it as latest draft wrapper without updating `task_log.json`.
2. WHEN user provides pre-approval draft feedback THEN Orchestrator SHALL pass the latest draft wrapper and feedback back to Planner.
3. WHEN Planner handles pre-approval draft feedback with a prior wrapper THEN Planner SHALL return a new wrapper that builds on the prior wrapper and summarizes cumulative pre-approval changes.
4. WHEN pre-approval draft loops occur THEN Planner SHALL NOT add Revision History sections or entries to any spec artifact.
5. WHEN user approves the spec artifacts THEN Orchestrator SHALL append exactly one `spec-created` event using the latest cumulative approved Planner wrapper.
6. IF the latest Planner wrapper does not summarize all material pre-approval changes THEN Orchestrator SHALL request a final cumulative JSON-only wrapper before appending `spec-created`.
