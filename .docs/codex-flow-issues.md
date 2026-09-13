# Orchestrator Flow Incident Report: `task_log.json` Protocol Drift

## Context

This incident occurred while using the `orchestrator-flow` skill for the feature:

- Feature: `upcoming-and-watch-history-management`
- Spec directory: `.docs/specs/upcoming-and-watch-history-management/`
- Workflow artifact: `.docs/specs/upcoming-and-watch-history-management/task_log.json`

The feature had already gone through:

1. Planner spec creation/revision
2. Architect spec review
3. Coder implementation
4. Reviewer code review
5. Multiple Coder/Reviewer revision loops
6. Final Reviewer approval

After that, the user noticed a small cleanup issue:

- `src/utils/format.ts` exported `DISCORD_MESSAGE_LIMIT = 2000`
- `src/utils/watch-format.ts` privately defined `DISCORD_MESSAGE_LIMIT = 2_000`
- The user wanted this reflected in the spec as planned Coder work, not implemented directly by the Orchestrator.

The resulting follow-up flow exposed several failures in how the Orchestrator maintained `task_log.json`.

---

## Summary Of What Went Wrong

The Orchestrator treated `task_log.json` as a loose narrative/status diary instead of a strict workflow protocol artifact.

The main problems were:

1. Directly editing code/spec files when only Planner/Coder should have.
2. Logging events that were not part of the true workflow.
3. Recording `implementation-complete` too early.
4. Misusing `actor` and `requestor` pairs.
5. Creating duplicate/spec-noise events for same-session clarifications.
6. Failing to update stale `history id N` references after event removals/renumbering.
7. Relying on schema validation even though the schema did not catch semantic flow errors.

---

## Detailed Timeline Of The Failure

### 1. User reported duplicated constant

The user observed:

```text
watch-format.ts also defines DISCORD_MESSAGE_LIMIT just like format.ts does.
This could cause drift as this default is defined in two places.
```

Expected Orchestrator behavior:

- Treat this as a new user change request.
- Send it to Planner.
- Planner updates spec/tasks.
- Architect reviews the updated spec.
- Only after approval, Coder implements.
- Reviewer reviews.
- `task_log.json` records each role transition.

Actual Orchestrator behavior:

- The Orchestrator directly edited implementation files:
  - Added `src/utils/discord.ts`
  - Modified `src/utils/format.ts`
  - Modified `src/utils/watch-format.ts`
- This violated role ownership:
  - Planner should update specs.
  - Coder should modify implementation.
  - Orchestrator should coordinate and maintain `task_log.json`.

The user stopped the change and corrected the Orchestrator.

### 2. User clarified naming

The user pointed out:

```text
also you made discord.ts... it should probably something more like constants.ts...
```

Expected behavior:

- Add that to Planner context.
- Do not edit implementation.

Actual behavior:

- The Orchestrator acknowledged this but still had already made code changes, which then had to be undone.

### 3. User requested undo and Planner handoff

The user said:

```text
Undo what you did and send the request back to the planner.
```

Expected behavior:

- Revert only the accidental Orchestrator code edits.
- Send the cleanup request to Planner.
- Record the workflow correctly.

Actual behavior:

- The Orchestrator correctly removed `src/utils/discord.ts` and restored `format.ts`/`watch-format.ts`.
- It then spawned Planner.
- Planner returned a recommendation.
- But the recommendation was initially just reported in chat instead of being reflected as a spec update.

### 4. User clarified Planner must update the spec

The user said:

```text
The planner is supposed to update the spec so that the spec reflects the final implementation.
Even if it's only to add some tasks to the tasks.md file so that the Coder can implement
(and check it off) and this can be passed to the Reviewer to review.
```

Expected behavior:

- Append a `user-change-requested` event.
- Append `spec-revision-started`.
- Spawn Planner.
- Planner edits `tasks.md`.
- Append exactly one `spec-updated` event for that Planner revision.
- Architect reviews.

Actual problems:

- The Orchestrator directly edited `tasks.md` in one later refinement, despite the user explicitly saying Planner must do it.
- The Orchestrator also edited `task_log.json` in a way that introduced later cleanup needs.

### 5. Same-session clarification was logged as a separate revision

The user clarified:

```text
Task 51 almost certainly should remove the Red test for the constant...
this is definitely an implementation test and has no long term behavioural benefit.
```

This clarification happened during the same unapproved Planner revision session.

Expected behavior:

- Send clarification to Planner.
- Planner folds clarification into the same spec update.
- `tasks.md` Revision History entry remains a single Revision 2.
- `task_log.json` should not necessarily create a new `user-change-requested` and `spec-revision-started` pair if the prior revision had not been approved.

Actual behavior:

- The Orchestrator directly edited `tasks.md`.
- The Orchestrator appended:
  - a new `user-change-requested`
  - a new `spec-revision-started`
- Later the user removed these because they were not real separate workflow events.

### 6. Revision History entry 3 was incorrectly created

Planner added a Revision 3 in `tasks.md` for the clarification.

User said:

```text
Revision history entry 3 is not necessary since this was in the same session
(i had not yet approved the revised spec). That clarification should have been
rolled into revision history entry 2
```

Expected behavior:

- Planner should fold the clarification into Revision 2.
- Remove Revision 3.
- Keep Tasks 49-52 unchecked.
- Keep one spec update event for the unapproved revision session.

Actual behavior:

- Eventually Planner fixed it.
- But `task_log.json` already had extra events which later needed manual cleanup.

### 7. Architect review was performed, but task log was not kept current

The user said:

```text
you need to keep the task log updated
```

Expected behavior:

- After Planner and Architect subagents complete, Orchestrator must append:
  - `spec-updated`
  - `spec-review-started`
  - `spec-reviewed`
- Status should reflect current phase.

Actual behavior:

- Orchestrator initially failed to log some subagent outputs promptly.
- Then it appended the missing events, but not all semantics were correct.

### 8. `implementation-complete` was logged too early

The Orchestrator recorded:

```json
{
  "actor": "Orchestrator",
  "requestor": "User",
  "event": "implementation-complete",
  "details": "Implementation and review completed..."
}
```

This happened immediately after Reviewer approved code.

Expected behavior:

- Final Reviewer approval should set status to something like `code_approved`.
- `implementation-complete` should only be used after the user validates the feature and asks for finalization/commit.
- Code approval and implementation completion are distinct workflow stages.

Actual behavior:

- The Orchestrator treated Reviewer acceptance as implementation completion.
- The user later removed the event and renumbered the remaining history.
- This was a serious workflow-state mistake.

### 9. `actor` / `requestor` pairs were mechanically chosen

Several entries had schema-valid but semantically wrong `requestor` values.

Example category:

```json
{
  "actor": "Reviewer",
  "requestor": "Planner",
  "event": "code-review-started"
}
```

In many re-review cases, the actual requestor should have been `Coder`, because the Coder had just submitted a `change_wrapper` for review.

The user corrected several of these based on the intended workflow.

Expected convention:

- `actor` = role that performs the event.
- `requestor` = role/user whose handoff or request caused the event.
- For review after Coder completes:
  - `actor=Reviewer`
  - `requestor=Coder`
- For Coder revision after Reviewer rejects:
  - `actor=Coder`
  - `requestor=Reviewer`
- For Planner revision requested by Architect feedback:
  - `actor=Planner`
  - `requestor=Architect`
- For Planner revision requested by user:
  - `actor=Planner`
  - `requestor=User`

The Orchestrator often set `requestor=Planner` because Planner/orchestrator was coordinating, but that was semantically too broad.

### 10. `subagent-error` actor/requestor semantics were unclear

The Orchestrator flagged two `subagent-error` events as potentially odd.

The user clarified:

- For the failed Planner attempt:
  - `actor=Planner`
  - `requestor=User`
  - This is correct because the Planner attempt failed while acting on the user's request.

- For the failed Reviewer attempt:
  - `actor=Reviewer`
  - `requestor=Coder`
  - The reviewer failed while reviewing the Coder’s submitted changes.

This indicates the skill should explicitly document subagent-error semantics.

Recommended convention:

```text
For subagent-error:
- actor = role/subagent that failed
- requestor = entity whose work/request the failed subagent was serving
```

### 11. Renumbering caused stale id references

After the user removed incorrect events and renumbered, several text fields still referenced old ids:

Examples:

- `history id 44` referenced the current approved review instead of the failed review.
- `wrapper id 39` referenced a review-start event instead of the coding-complete wrapper.
- `history id 39` referenced review-start instead of coding-complete.

Expected behavior:

After any event removal or id renumbering, the Orchestrator must scan every text field in:

- `details`
- `notes`
- `spec_change_wrapper.notes`
- `spec_review_wrapper.notes`
- `change_wrapper.notes`
- `review_wrapper.notes`
- any nested wrapper text

and verify all references like:

- `history id N`
- `review id N`
- `wrapper id N`
- `wrappers from ids N, M, ...`
- `history ids N and M`

still point to the intended event type.

The Orchestrator initially did not do this until the user asked.

---

## Final Corrected State

After user cleanup and validation:

- `task_log.json` schema validation passed.
- IDs were contiguous.
- No duplicate IDs.
- No missing IDs.
- Status was `code_approved`.
- Stale id references were corrected.
- Final code review approval remained recorded.
- `implementation-complete` event was removed.

---

## Root Causes

### Root Cause 1: Skill does not distinguish schema validity from workflow semantic validity

The JSON schema allowed many incorrect things:

- `implementation_complete` status after Reviewer approval
- Duplicate same-session spec update events
- Odd but allowed actor/requestor pairs
- Stale id references in text
- `subagent-error` semantics ambiguity

Because validation passed, the Orchestrator assumed the log was correct.

### Root Cause 2: Orchestrator role boundaries were underspecified or not enforced

The Orchestrator edited code and specs directly.

The flow needs stronger language:

```text
The Orchestrator may edit only task_log.json.
The Orchestrator must not edit requirements.md, design.md, tasks.md, source files, tests, or docs.
Planner owns spec edits.
Coder owns implementation/test/doc edits.
Architect and Reviewer are read-only.
```

### Root Cause 3: `implementation-complete` semantics were ambiguous

The skill allowed or implied that implementation completion could be recorded after code review.

The user’s intended semantics:

```text
code_approved = Reviewer accepted implementation.
implementation_complete = User has validated the feature and requested finalization/commit.
```

The skill must encode this.

### Root Cause 4: Same-session Planner revisions were not clearly handled

The user clarified a spec update before approving it.

The Orchestrator logged it as a new change request/revision.

The skill needs a rule:

```text
If the user clarifies an in-progress, unapproved Planner revision, fold it into the same Planner revision/session.
Do not append another user-change-requested/spec-revision-started pair unless the prior revision was already approved, rejected, or closed.
```

### Root Cause 5: No semantic id-reference linter exists

The validator checks schema, but not text references.

The skill needs a semantic validator or at least a mandatory manual check.

---

## Recommended Skill Changes

### 1. Add a “Role Ownership” section

Add to `orchestrator-flow` skill:

```markdown
## Role Ownership Rules

The Orchestrator coordinates the workflow and maintains `task_log.json`.

The Orchestrator MUST NOT directly edit:
- `requirements.md`
- `design.md`
- `tasks.md`
- source code
- tests
- README or technical documentation

Role ownership:
- Planner edits spec artifacts only.
- Architect reviews spec artifacts only and is read-only.
- Coder edits implementation/tests/docs required by approved tasks.
- Reviewer reviews code only and is read-only.
- Orchestrator edits `task_log.json` only.

If a user asks for a spec change, the Orchestrator MUST route it to Planner.
If a user asks for implementation after spec approval, the Orchestrator MUST route it to Coder.
```

### 2. Add explicit event/status semantics

Add:

```markdown
## Status Semantics

- `spec_in_progress`: Planner is actively creating/revising specs.
- `spec_updated`: Planner has produced spec changes but they have not yet been reviewed/approved.
- `spec_in_review`: Architect review is active.
- `spec_approved`: Architect accepted the spec and implementation may begin if user/flow continues.
- `coding_in_progress`: Coder is implementing approved tasks.
- `coding_complete`: Coder returned a change_wrapper.
- `code_in_review`: Reviewer is reviewing Coder output.
- `code_changes_requested`: Reviewer rejected or requested changes.
- `code_approved`: Reviewer accepted implementation with no issues.
- `implementation_complete`: ONLY after explicit user validation/finalization/commit request. Do not set this merely because Reviewer approved code.
```

### 3. Add allowed transition rules

Add a transition table:

```markdown
## Task Log Transition Rules

Allowed normal transitions:

1. User request:
   - append `user-change-requested` if this is a new request after a completed/approved phase.
   - status -> `spec_in_progress`

2. Planner starts:
   - append `spec-creation-started` or `spec-revision-started`
   - actor=Planner
   - requestor=User/Architect as appropriate

3. Planner completes:
   - append `spec-created` or `spec-updated`
   - actor=Planner
   - requestor=same entity that requested Planner
   - status -> `spec_updated` or `spec_created`

4. Architect starts:
   - append `spec-review-started`
   - actor=Architect
   - requestor=Planner
   - status -> `spec_in_review`

5. Architect completes:
   - append `spec-reviewed`
   - actor=Architect
   - requestor=Planner
   - if accepted true: status -> `spec_approved`
   - if accepted false: status -> `spec_changes_requested`

6. Coder starts:
   - append `coding-started` or `coding-revision-started`
   - actor=Coder
   - requestor=Planner for initial coding after approved spec
   - requestor=Reviewer for code revisions after failed review
   - status -> `coding_in_progress`

7. Coder completes:
   - append `coding-complete`
   - actor=Coder
   - requestor=same role that requested coding
   - status -> `coding_complete`

8. Reviewer starts:
   - append `code-review-started`
   - actor=Reviewer
   - requestor=Coder
   - status -> `code_in_review`

9. Reviewer completes:
   - append `code-reviewed`
   - actor=Reviewer
   - requestor=Coder
   - if accepted true: status -> `code_approved`
   - if accepted false: status -> `code_changes_requested`
   - if conditional: status -> `code_conditionally_approved`

10. Final implementation completion:
   - append `implementation-complete`
   - actor=Orchestrator
   - requestor=User
   - ONLY after explicit user validation/finalization/commit request
   - status -> `implementation_complete`
```

### 4. Clarify same-session user refinements

Add:

```markdown
## Same-Session Planner Refinements

If the user clarifies or corrects a Planner revision before that revised spec has been approved or rejected:

- Do not append a new `user-change-requested` event unless the clarification changes the scope materially.
- Do not append a second `spec-revision-started` for the same continuous Planner session.
- Route the clarification to Planner.
- Planner should fold the clarification into the same `spec_change_wrapper`.
- Revision History in changed spec files should contain one entry for the session.
```

### 5. Clarify `subagent-error`

Add:

```markdown
## Subagent Error Semantics

For `subagent-error` events:

- `actor` is the role/subagent that failed or stalled.
- `requestor` is the entity whose request the failed subagent was serving.

Examples:
- Planner failed while handling a user spec request:
  - actor=Planner
  - requestor=User
- Reviewer failed while reviewing Coder output:
  - actor=Reviewer
  - requestor=Coder
- Architect failed while reviewing Planner output:
  - actor=Architect
  - requestor=Planner
```

### 6. Add a mandatory pre-append checklist

Add:

```markdown
## Pre-Append Checklist

Before appending any `task_log.json` entry, the Orchestrator MUST answer:

1. Is this a real workflow event, or just same-session clarification?
2. Which role actually performed the event?
3. Which role/user requested or caused this event?
4. Is the event allowed by the current status?
5. What should the new status be?
6. Does this event duplicate an existing in-progress event?
7. Does the event include wrapper data required by the role contract?
8. If this event references prior history IDs, are those IDs current and correct?
```

### 7. Add a mandatory post-update validation checklist

Add:

```markdown
## Post-Update Validation Checklist

After every task_log.json edit, run:

1. JSON schema validation.
2. ID contiguity check.
3. Duplicate ID check.
4. Status/event consistency check.
5. Actor/requestor semantic check.
6. Text reference scan for:
   - `history id N`
   - `review id N`
   - `wrapper id N`
   - `wrappers from ids N, M`
   - `history ids N and M`
7. Verify referenced IDs point to the intended event types.
```

---

## Recommended Validator Enhancements

The existing validator should gain a semantic mode, for example:

```bash
python validate_orchestrator_artifacts.py task-log --semantic path/to/task_log.json
```

### Semantic checks to add

#### 1. Contiguous ids

Already likely covered or easy to add:

```text
history[0].id == "1"
each next id == previous + 1
no duplicates
```

#### 2. Status must match last meaningful event

Examples:

```text
last event spec-updated => status should be spec_updated or spec_in_review if review started after
last event spec-reviewed accepted true => status should be spec_approved unless later coding started
last event coding-started => status coding_in_progress
last event coding-complete => status coding_complete unless review started
last event code-review-started => status code_in_review
last event code-reviewed accepted true => status code_approved
last event code-reviewed accepted false => status code_changes_requested
last event implementation-complete => status implementation_complete
```

#### 3. Prevent premature `implementation-complete`

Rule:

```text
implementation-complete may only appear if explicitly preceded by a user event/details indicating validation/finalization/commit request.
```

At minimum, warn if:

```text
implementation-complete immediately follows code-reviewed accepted true with no user-change/request/finalization event.
```

#### 4. Actor/requestor pair linting

Recommended default rules:

```text
spec-creation-started:
  actor=Planner
  requestor=User

spec-revision-started:
  actor=Planner
  requestor=User or Architect

spec-created/spec-updated:
  actor=Planner
  requestor=User or Architect

spec-review-started/spec-reviewed:
  actor=Architect
  requestor=Planner

coding-started:
  actor=Coder
  requestor=Planner or User depending on convention, but prefer Planner after spec approval

coding-revision-started:
  actor=Coder
  requestor=Reviewer

coding-complete:
  actor=Coder
  requestor=same as corresponding coding-started/coding-revision-started

code-review-started/code-reviewed:
  actor=Reviewer
  requestor=Coder

implementation-complete:
  actor=Orchestrator
  requestor=User

subagent-error:
  actor=failed role
  requestor=role/user whose request failed
```

#### 5. Detect duplicate same-session spec updates

Warn if:

```text
Two consecutive or near-consecutive `spec-updated` events occur without an intervening Architect review, user approval, or materially new user-change-requested event.
```

This should be a warning, not always an error, because some workflows may intentionally record incremental Planner outputs.

#### 6. Reference scanner

Parse all strings in the log and find patterns:

```regex
history id (\d+)
review history id (\d+)
review id (\d+)
wrapper id (\d+)
wrappers from ids ([0-9, and]+)
history ids ([0-9, and]+)
```

Then validate:

- referenced id exists
- if phrase says `review id`, referenced event is `code-reviewed` or `spec-reviewed`
- if phrase says `wrapper id`, referenced event contains the appropriate wrapper:
  - `change_wrapper`
  - `spec_change_wrapper`
  - `review_wrapper`
  - `spec_review_wrapper`
- if phrase says `history id`, at least exists
- optionally warn when an event references itself unless intended

#### 7. Wrapper/event compatibility

Check:

```text
spec-created/spec-updated must contain spec_change_wrapper
spec-reviewed must contain spec_review_wrapper
coding-complete must contain change_wrapper
code-reviewed must contain review_wrapper
other events should usually contain details
```

The schema may already enforce some of this, but semantic mode should produce clearer messages.

---

## Specific Skill Documentation Patch Suggestions

In `orchestrator-flow/SKILL.md`, add:

```markdown
## Critical Orchestrator Boundaries

The Orchestrator coordinates and edits only `task_log.json`.

The Orchestrator MUST NOT directly edit spec files or implementation files. All spec edits go through Planner. All implementation/test/doc edits go through Coder. Architect and Reviewer are read-only.

The Orchestrator MUST keep `task_log.json` aligned with the workflow state machine. Do not use it as a loose progress diary.
```

In `references/orchestrator.md`, add:

```markdown
## Completion Semantics

`code_approved` means Reviewer accepted the code.

`implementation_complete` is reserved for the final user-validated completion step, normally after the user has reviewed/validated the feature and requested finalization or commit. Never append `implementation-complete` immediately after a Reviewer approval unless the user explicitly requested final completion.
```

In `references/task_log_schema.json`, consider adding stricter `status` docs:

```json
"implementation_complete": "Only after explicit user validation/finalization/commit request; not equivalent to code approval."
```

In `scripts/validate_orchestrator_artifacts.py`, add semantic checks as above.

---

## Example Correct Flow For The Cleanup Case

The correct flow for the duplicated constant cleanup should look like:

```text
32 user-change-requested
   actor=Orchestrator
   requestor=User
   details=User identified duplicated DISCORD_MESSAGE_LIMIT...

33 spec-revision-started
   actor=Planner
   requestor=User

34 spec-updated
   actor=Planner
   requestor=User
   spec_change_wrapper=Planner updated tasks.md, folded same-session clarification into Revision 2

35 spec-review-started
   actor=Architect
   requestor=Planner

36 spec-reviewed
   actor=Architect
   requestor=Planner
   accepted=true

37 coding-started
   actor=Coder
   requestor=Planner

38 coding-complete
   actor=Coder
   requestor=Planner
   change_wrapper=shared constants implementation

39 code-review-started
   actor=Reviewer
   requestor=Coder
   details=Reviewing wrapper from history id 38

40 code-reviewed
   actor=Reviewer
   requestor=Coder
   accepted=false
   review_wrapper=must_fix harness ESM portability

41 coding-revision-started
   actor=Coder
   requestor=Reviewer
   details=Fixing review history id 40

42 coding-complete
   actor=Coder
   requestor=Reviewer
   change_wrapper=harness fix

43 code-review-started
   actor=Reviewer
   requestor=Coder
   details=Reviewing revision wrapper from history id 42

44 code-reviewed
   actor=Reviewer
   requestor=Coder
   accepted=true
   notes=Prior must_fix from history id 40 resolved; cumulative wrapper id 38 accounts for constants.ts
```

Top-level status after this should be:

```text
code_approved
```

Not:

```text
implementation_complete
```

The latter should wait for explicit user final validation/finalization.

---

## Lessons Learned

1. Passing JSON schema is not enough.
2. `task_log.json` is protocol state, not a narrative log.
3. Orchestrator must not directly edit specs/code.
4. Same-session clarifications should be consolidated.
5. `implementation-complete` must be reserved for the final user-approved completion gate.
6. Actor/requestor pairs need role semantics, not just schema validity.
7. Any renumbering requires a full text-reference scan.
8. The skill needs semantic validation because future chat instances will not remember this incident.

---

## Priority Fixes For The Skill

If only a few changes can be made, do these first:

1. Add explicit role ownership rule: Orchestrator edits only `task_log.json`.
2. Add `code_approved` vs `implementation_complete` distinction.
3. Add actor/requestor pair guidance.
4. Add same-session clarification rule.
5. Add semantic validator for id references and status/event consistency.

These five changes would have prevented nearly all of the mistakes in this incident.
