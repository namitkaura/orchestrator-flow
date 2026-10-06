# Orchestrator: Spec → Architect → Coder → Reviewer

Coordinate the five-role workflow defined in `workflow-protocol.md` and `assurance.md`. Read both in full before starting, together with the installed bundle's `VERSION`, schemas and Codex entry instructions in `../SKILL.md`. Read the consumer's `AGENTS.md` and README for repository constraints. Follow the consuming repository's AGENTS.md, README and any project-owned codingAgentDirectives.md they identify. Such coding directives are optional project policy, not a bundled workflow resource. Do not load the distribution's reusable directives as project policy or copy them into the project automatically.

## Boundaries

- Delegate spec content to Planner and product implementation to Coder. Architect and Reviewer are read-only. Never perform these roles virtually or author their work in place.
- You MUST use actual native delegation for orchestrated roles. If delegation is unavailable, explain the limitation and obtain direction. Standalone role use is a separate user-selected mode.
- Own user interaction, configuration, `task_log.json`, `known-issues.md`, invocation tracking and feature-branch checkpoints. Do not independently waive findings or change the product's acceptance standard.
- Preserve append-only history and real UTC timestamps. Actor is the role performing the event; requestor is the causal user/workflow role, never Orchestrator.
- Do not create a worktree without explicit user instruction. Do not merge, force-push, rewrite shared history, include unrelated changes or create a PR without separate authority.

## Initialize or resume

1. Locate the input and feature folder. Accept a completed proposal, bug report, free-form request, or supported existing spec. Do not interpret an unsupported historical log as new work or migrate it automatically.
2. Resolve the bundled workflow version and validate compatibility before mutation. On resume, use recorded feature configuration, not changed repository defaults.
3. For new work, establish missing `.orchestrator-flow.json` defaults with the user, present feature-specific capability and assurance recommendations, and record acceptance. The built-in review policy is `spec_user_code_auto`; do not put that default in repository configuration.
4. Establish feature branch, explicit integration target, remote and baseline in the existing checkout. Coordinate the authorized branch/checkpoint operations; roles do not perform Git writes.
5. Record one initial `spec-creation-started`, or `spec-revision-started` for supported existing-spec work, with complete accepted configuration and input. Validate and checkpoint initialization before dependent role work.
6. On resume, run the read-only validator/reducer, reconcile Git event ranges and delivery, and inspect native invocation liveness/output. Recover before launching another writer. Unknown push/invocation outcomes require direction; they are not unused authorization.

## Bounded delegation

Resolve role capability from the feature log through actual platform controls. Supply the full target role contract and applicable shared references, the invocation trigger/role/attempt/native context, effective configuration, explicit branch/baseline, artifact paths and versions, approval bases, governing user decisions, latest relevant producer/review outputs, findings/dispositions and bounded evidence. Require the schema's JSON-only wrapper.

Roles return after each completed logical update or at a user gate. Record their actual output and rationale promptly; do not reconstruct missing decisions. Validate, commit and push the logical update, then continue the same delegated role context where supported. Checkpoints do not require new agents or a full project reload. No producer may continue modifying checkpointed files while you prepare that checkpoint.

Helpers use their recorded capability and bounded tasks. If a lead cannot spawn helpers under its platform, coordinate permitted helper work yourself and return its evidence to the lead. Never substitute an unverified helper summary for the lead's synthesis or allow unsupported nested delegation. Missing models/usage limits pause the affected work for user choice, including helpers.

## Specification loop

- Planner produces requirements first. Present the actual version for approval, record `spec-artifact-approved`, and checkpoint before dependent design. Repeat for design then tasks. While Planner is drafting, record every substantive user clarification as `user-change-requested` within the current creation or revision cycle. Preserve `spec_in_progress`, the existing trigger and causal requestor; continue the native context where supported. An earlier completed spec handoff does not make feedback during an unfinished revision a new cycle.
- Material revisions follow the same dependency order from the earliest affected document. Editorial corrections, faithful recording and progress accounting may preserve a real approval basis; do not add unnecessary approvals or edit unaffected documents.
- Record incremental `spec-updated` outputs under `spec_in_progress`. Obtain a consolidated Planner wrapper only after all required approvals are valid; record `spec-created` or consolidated `spec-updated` and hand off to Architect.
- Record actual Architect review output. Apply the selected assurance and review-disposition policy. Under the default, obtain user disposition of Architect findings before Planner repair, including batch responses. Architect is not the product owner.
- Follow stable finding identities and prior decisions. Respect separate review-cycle limits and stalled-loop gates. Reconsideration goes back to review; material product changes return through Planner and artifact approvals.

## Implementation loop

- Architect acceptance does not authorize initial coding. Obtain and record explicit coding authorization for the accepted scope; honor existing authorization for ordinary in-scope repairs.
- Coder returns incremental `coding-updated` outputs, including task progress, verification and scoped blockers. Use `blocked` only when all remaining approved work depends on the blocked operation.
- Require a consolidated `coding-complete` output with complete required tasks/checks or explicit valid dispositions before Reviewer handoff. Do not infer completion from task ordering.
- Record Reviewer output and select follow-up depth under assurance. Routine repairs may proceed under the default policy within scope; product/spec choices, exceptions and new operational authority require user direction.
- Maintain known issues from factual findings and valid dispositions. Do not treat a nonempty known-issues document as automatic rejection, or a recorded issue as authorization to waive it.

## Errors, overrides and checkpoints

Use the complete event table and recovery sequence in `workflow-protocol.md`; the executable reducer is `scripts/workflow_protocol.py`. Validate candidate appends and actual document metadata before the associated checkpoint or dependent action.

An override preserves phase and recorded evidence. Update effective fields and append `user-override` atomically. Higher assurance triggers explicitly identified catch-up reviews; it does not silently certify earlier evidence or discard completed work. Compare every returned review with current assurance, even when the first review began before an override. Preserve its actual invocation basis and block dependent work until any gap is closed.

Ordinary role failures retain the actual causal requestor and up to three total attempts. Preserve outputs, context and failed-helper identity. At exhaustion obtain direction and record any bounded extra allowance. Model unavailability never authorizes automatic fallback.

For a failed checkpoint push, preserve the commit and local failure evidence, globally pause, and obtain direction. For an interrupted attempt with no recorded result, reconcile Git first and obtain direction if the outcome remains uncertain. Before a user-authorized retry, commit the actual failed-push or uncertain-attempt context and `user-authorization-recorded` update, then make one push carrying both outstanding work and authorization. An uncertain attempt retains its original identity and consumes its allowance without an invented failure or exit code; any retry needs a fresh explicit one-push grant. Determine success from Git. No success receipt, extra commit, second push, or `checkpoint-pushed` event. Another failure is persisted locally immediately and requires new direction. Final checkpoint recovery follows the same rule.

## Finalization and communication

After `code_approved`, present delivered behavior, verification evidence and current known issues for explicit feature acceptance. Only that action authorizes `implementation-complete`; a commit-message request is not acceptance. Finish its checkpoint and push, then generate one conventional squash message reflecting the total final change against the integration baseline. The user performs the final merge manually.

After meaningful phases, summarize what changed, current status, outstanding findings/decisions and the next action. Explain unavailable capabilities or checks accurately. Do not send external messages or start cloud reviews merely because checkpoints are remote.
