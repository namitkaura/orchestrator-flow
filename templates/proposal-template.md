# Proposal: [Name of the feature or improvement]

Template version: 2

## Authoring Guidance — Remove from the Completed Proposal

This template defines a standalone input to Orchestrator Flow planning. Use it without requiring a previous proposal as a style guide.

- Write for someone who can inspect the repository but has not seen the conversation. Explain the current problem, intended outcome, established decisions, and important rationale.
- Preserve the title prefix and the four document sections below. Descriptive `###` subheadings are allowed and encouraged within any section when they improve readability or separate distinct topics. Use numbered subsections under Proposed Solution for substantial proposals.
- Use `##` for the main document sections, `###` for distinct topics, and `####` for meaningful subdivisions within a topic. Keep related details under their owning topic and do not skip heading levels. Prefer paragraphs or bullets when a separate subsection adds little value, and prefer restructuring over nesting deeper than `####`. If headings are numbered, keep numbering consistent with the hierarchy, such as `### 4. Implement the provider adapter` followed by `#### 4.1 Preserve catalogue breadth`. No particular nesting depth is required.
- Scale detail to the change. A small improvement can be a few paragraphs; a substantial change may need several subsections. Do not invent scope, hardening requirements, abstractions, or unanswered questions to fill the template.
- Present the final intent and decisions rather than the discussion or abandoned drafts that led to them. Distinguish confirmed facts, user decisions, recommendations, and unresolved choices. Do not claim approval that was not given.
- Include technical constraints already established by the user or repository. Leave genuinely open implementation choices to requirements and design; this document is not a substitute for the spec or task plan.
- Use concrete inputs, outputs, examples, and boundaries where they remove ambiguity. Explain consequential decisions in the section they affect.
- Use tables for mappings, alternatives, or configuration behavior; use diagrams only when they clarify relationships or flow. Use fenced blocks for exact commands, inputs, and outputs.
- The guidance below lists considerations, not mandatory extra headings. Include what matters and omit inapplicable material. Summarize substantial evidence and reference its source rather than pasting entire investigations.
- Do not add workflow status, approval metadata, or Git hashes to the completed proposal. A product or release version may be part of the title when relevant. The template's integer version identifies its authoring contract, advances independently of the bug-report template, and is separate from the workflow's semantic version.
- Remove the Template version line and this Authoring Guidance section; replace all bracketed prompts and instructional text with finished content. Retain only references that exist and are relevant. The final document must be understandable without a previous proposal or chat transcript.

## Problem Statement

[Explain what currently happens, what is inadequate or missing, and why the change matters. Identify who is affected and the practical consequences. Give enough context for a reader unfamiliar with the feature to understand the problem.]

Consider, where relevant:

- A concrete example of current behavior and its limitation.
- Relevant evidence, incidents, or measured constraints; distinguish observations from suspected causes and hypothetical future concerns.
- Project context that affects the appropriate solution: intended users, deployment, exposure, reversibility, and recovery cost.
- Existing behavior that is valuable and should be preserved.
- Why the current approach or a previous bounded fix is insufficient for the proposed outcome.

[Use descriptive `###` subheadings to separate distinct problems, relevant background, or consequences when that makes the Problem Statement easier to read. Prefer headings that express the point, such as "Draft decisions are lost between sessions" or "Full reviews cost too much for small repairs", rather than generic labels. These subsections do not need numbering. A short, single-topic problem statement can remain one or two paragraphs. Avoid a chronological troubleshooting account or repeating the solution here.]

## Proposed Solution

[Briefly explain the overall approach and intended outcome. Make the proposal actionable enough for Planner to derive requirements, design, and tasks, while identifying technical choices that remain open.]

**Authoring considerations — remove from the completed proposal:** Use descriptive `###` subsections for the concrete changes in substantial proposals, following the adaptable structure below. A small proposal may need only a paragraph. Address the following within the relevant change subsections; these are coverage prompts, not a mandatory set of headings:

- **Behavior and scope:** Describe what users or consuming systems will be able to do, including important inputs, outputs, state changes, and representative examples.
- **Decisions and rationale:** State settled choices and explain why consequential constraints or tradeoffs apply. Mark a recommendation as a recommendation if the user has not decided it.
- **Preservation boundaries:** Identify existing behavior, interfaces, data, compatibility guarantees, or historical areas that must remain unchanged.
- **Configuration:** Specify already-decided names, allowed values, defaults, and behavior for missing or invalid values. Use a table when several cases need comparison; flag unresolved policy rather than inventing it.
- **Failure and recovery:** Explain meaningful failure outcomes and recovery expectations. Identify operations needing explicit authorization where relevant, without treating the proposal itself as authorization to perform them.
- **Technical constraints:** Include established architecture, ownership, integration, or data constraints. Do not prescribe speculative modules or implementation mechanics merely to make the proposal look detailed.
- **Documentation:** Identify the durable guidance users or maintainers will need and known documentation locations that must change.
- **Verification expectations:** Describe the outcomes and regressions that need evidence, plus established repository checks where known. Leave the detailed test plan and task sequence to planning; keep expectations proportional to the change and agreed assurance.
- **Non-goals:** Explicitly exclude plausible adjacent work that could otherwise expand the scope. For larger proposals, finish the solution with a dedicated non-goals subsection.

Specificity example, for style only:

> Vague: "Handle provider errors gracefully."
>
> Concrete: "If the provider times out, preserve the current selection and offer manual retry. Automatic retries are outside this change because manual recovery is sufficient for the intended deployment."

[Use the same degree of specificity for the actual feature; do not copy the example's product decisions into it.]

### 1. [First concrete change or capability]

[Describe the intended behavior, important decisions, and their rationale. Include relevant configuration, failure handling, technical constraints, and preservation boundaries together with the change they affect. Use a descriptive heading that names the actual change.]

### 2. [Next concrete change or capability, if needed]

[Add, remove, or rename numbered change subsections to fit the proposal. Do not retain an empty subsection or spread one change's related details across generic categories solely to fill the template.]

### Documentation and Verification

[Describe relevant documentation updates and verification expectations. Split these into separate subsections if substantial; omit this section if the expectations are already covered alongside the changes or are not applicable. For a fully numbered solution, continue the subsection numbering consistently.]

### Non-goals

[Identify plausible adjacent work that is explicitly outside scope. For larger proposals, retain this as the final solution subsection, continuing the numbering if used. For a small proposal, state relevant exclusions alongside the solution instead if clearer.]

## Questions

[List genuine unresolved choices or assumptions that require confirmation. Explain what each affects and include useful alternatives when known. Clearly distinguish these from decisions already settled above.]

[If no proposal-level questions remain, state that the recorded decisions form the planning baseline. Direct Planner to raise newly discovered contradictions or material policy choices at the appropriate requirements, design, or task-planning phase rather than silently changing the agreed behavior. Do not manufacture questions or claim that unapproved recommendations are settled.]

## References

[List the actual sources needed to understand the project and plan the change. Use repository-relative, POSIX-style paths for repository files and direct URLs for external sources. Briefly explain what each contributes. Verify references where access is available; label anything unverified.]

Include as applicable:

- Project overview, such as `README.md`, if present.
- Applicable repository instructions, such as `AGENTS.md`, and relevant documents they actually reference.
- Current requirements, architecture, behavior, configuration, testing, or documentation-maintenance references.
- Research, incident evidence, or source locations supporting the proposal.
- Relevant external specifications or documentation.

[Do not assume every repository has a design system or a particular documentation structure. A previous proposal may be a factual reference when relevant, but must not be required to understand this document's outline, intended behavior, or writing style.]
