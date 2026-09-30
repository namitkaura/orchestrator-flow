# Bug: [Short descriptive title of the bug]

Template version: 2

## Authoring Guidance — Remove from the Completed Bug Report

This template defines a standalone bug report for Orchestrator Flow planning. A useful report establishes the failure, expected correction, and relevant preservation boundaries; it does not require a root-cause diagnosis or proposed fix.

- Write for someone who has repository access but has not seen the conversation. Preserve the title prefix and the five document sections below; add subsections only when they improve clarity.
- Use `##` for the main document sections, descriptive `###` subheadings for distinct cases, environments, symptoms, or preservation requirements, and `####` for meaningful subdivisions within a topic. Do not skip heading levels; prefer paragraphs or bullets when another heading adds little value, and prefer restructuring over nesting deeper than `####`. Prefer unnumbered subheadings so reproduction-step numbers remain easy to follow. A short report may need no subheadings, and no particular nesting depth is required.
- Keep the report proportional to the bug. A concise report with exact inputs and observable results is preferable to speculative analysis or unrelated requirements.
- Separate reported or directly observed behavior from suspected causes, hypotheses, and proposed fixes. Do not claim that reproduction or validation was performed unless it was.
- Preserve significant input exactly, including emoji, Unicode characters, whitespace, punctuation, casing, and encoding. Use fenced blocks where formatting matters; identify code points or escaped forms if visual appearance alone is ambiguous and the information is known.
- Include a nearby successful case when it helps isolate the failure. Do not require one when none is known.
- State relevant behavior the fix must preserve. Do not turn a bounded correction into an unrequested redesign or general hardening project.
- Include environment, affected versions, frequency, logs, or screenshots when relevant and available. They are not mandatory sections. Use safe excerpts and references rather than dumping entire logs or exposing secrets and unrelated personal data.
- Do not add workflow status, approval metadata, or Git checkpoint metadata to the completed report. An affected build or commit may be cited as evidence when it helps identify the failure. The template's integer version identifies its authoring contract, advances independently of the proposal template, and is separate from the workflow's semantic version.
- Remove the Template version line and this Authoring Guidance section; replace all bracketed prompts and instructional text with finished content. Retain only relevant references. No previous bug report or conversation should be needed to interpret the result.

## Summary

[In a short paragraph, identify the affected operation, triggering condition, incorrect result, and practical impact. Mention a successful comparison or frequency when it materially clarifies the problem. Avoid unsupported severity claims or an unverified diagnosis.]

Style example: "Searching history for an emoji returns no match even when the entry contains that emoji. Searching for a word from the same entry succeeds."

## Observed Behaviour

[Describe what actually happens, using the smallest representative data and exact action or input. Show the returned result, error, or incorrect state. Include a relevant successful comparison where useful.]

Include as applicable:

- The exact record, request, command, or sequence involved.
- Actual output or a precise description of the observed result.
- Conditions, configuration, environment, or affected version that distinguish the failure.
- Relevant evidence and whether it was reported by the user or independently reproduced.

[Do not generalize a demonstrated failure to untested inputs as though they were observed. Keep hypotheses explicitly labelled.]

## Reproduction Steps

[Give numbered steps in execution order. Include prerequisites, representative setup data, exact actions, and the result to observe. State whether reproduction is reliable, intermittent, or not yet confirmed.]

[When there are genuinely different known reproduction scenarios, separate them with descriptive `###` subheadings, such as "Case A: Single emoji query" and "Case B: Mixed text and emoji query", and give each its own numbered steps. Keep individual actions as steps rather than headings. Do not invent additional scenarios to fill out the structure.]

1. [Establish the required state or configuration.]
2. [Perform a successful comparison, if useful and known; otherwise omit this step.]
3. [Perform the action that triggers the bug, with the exact input.]
4. [Observe the specific incorrect result.]

[Adapt the steps to the actual bug rather than retaining this sequence mechanically. If no reproduction is known, say so and describe the known incident conditions and missing evidence instead of inventing steps.]

## Expected Behaviour

[Describe the correct observable result for the failing example. Explain the basis for that expectation: an existing requirement, documented behavior, a known regression baseline, or the user's explicit intended behavior.]

Also identify, where relevant:

- Existing successful cases and nearby behavior that must continue to work.
- Display, data, interface, compatibility, and side-effect boundaries the correction must preserve.
- Any broader expected behavior beyond the demonstrated case. Distinguish that requested scope from inputs actually tested, and flag unresolved intent for confirmation during planning.

[For example, an emoji matching fix may need to preserve ordinary normalized word search and existing result formatting. Describe the actual preservation boundaries for this bug without prescribing a speculative implementation.]

## Additional Context and Resources

[Include useful context not already covered: a workaround, relevant recent changes, investigation findings, suspected cause or candidate fix, and genuine open questions. Label hypotheses and do not require a diagnosis or solution when none is established.]

[List the actual references needed for planning. Use repository-relative, POSIX-style paths for repository files and direct URLs for external sources. Briefly explain their relevance. Verify references where access is available; label anything unverified.]

Include as applicable:

- Project overview, such as `README.md`, if present.
- Applicable repository instructions, such as `AGENTS.md`, and relevant documents they actually reference.
- Authoritative definitions of the expected behavior and preservation boundaries.
- Relevant source/tests, safe evidence excerpts, screenshots, or incident records.

[Do not assume a particular documentation structure or refer vaguely to a previous release's behavior. Summarize the relevant behavior here and point to its definition when available. Raise unresolved intent or material changes in scope with the user during planning.]
