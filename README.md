# Orchestrator Mode: Spec -> Code -> Review with TaskSync

This repository defines a set of **VS Code custom agents** that work together to take a feature from a rough idea through:

1. **Spec creation** (requirements, design, tasks)
2. **Implementation** (test-driven coding)
3. **Review** (structured feedback and acceptance)

All of this is powered by the **TaskSync V5 Protocol**, which keeps the session running continuously and uses Python terminal commands to drive the task loop.

## High-level design

This workflow is implemented by four main agents on top of TaskSync:

- **TaskSync** enforces a non-terminating, terminal-driven loop using Python commands for tasks and questions, and forbids concluding language.
- **Planner** turns a rough feature idea into three spec artifacts under `.docs/specs/{feature_name}/` (`requirements.md`, `design.md`, `tasks.md`) and never writes implementation code.
- **Orchestrator** is your main entry point:
  - **Mode A – Proposal-first**: takes a free-form proposal or proposal file path, calls Planner to create/update the spec, then starts implementation and review.
  - **Mode B – Existing spec**: starts from an existing spec directory or explicit spec file paths and skips Planner.
  In both modes, Orchestrator does not read spec contents; it passes file paths to subagents, drives a Coder → Reviewer loop, and maintains a per-feature `task_log.json` next to the spec to track status and history.
- **Coder** implements or updates the feature according to the spec and any review feedback, using TDD and repo-appropriate tools, and returns a structured change wrapper (what changed, which commands/tests ran, and key notes).
- **Reviewer** evaluates the implementation against the spec and best practices, may re-run tests, and returns a structured review wrapper with `accepted`, `must_fix`, `should_fix`, and `nit` feedback.

Orchestrator keeps cycling Coder and Reviewer (updating `task_log.json` after each pass) until the feature is accepted or progress appears stuck, at which point it asks you for guidance via the TaskSync terminal question command. None of the agents ever create commits, branches, or PRs; you always review and commit manually.


## Agent roster

### TaskSync (base protocol)

`agents/TaskSync.agent.md`

TaskSync defines the **V5 protocol** that all other agents inherit:

- Sessions must **never end automatically**; only explicit terminal commands like `stop`, `end`, `terminate`, or `quit` may terminate the session.
- The agent must **never** use closing language ("let me know if you need anything else", "we're done", etc.).
- After each task, the agent must immediately **request the next task via the terminal** using:
  - Task input: `python -c "task = input('')"`
  - Question input: `python -c "question = input('How can i help you? ')"`
- The agent runs in a continuous loop: **execute task → summarize → request next task via Python command**.

All other agents (Orchestrator, Coder, Reviewer; Planner in its own way) treat these rules as **primary directives**: their prompts are additive and must not weaken TaskSync behavior.

---

### Orchestrator

`agents/Orchestrator.agent.md`

Orchestrator is the **central coordinator**. It:

- Inherits all TaskSync V5 primary directives.
- Is the **only agent** allowed to call other agents via `runSubagent`.
- Coordinates a full **Spec → Code → Review loop** using Planner, Coder, and Reviewer.
- Maintains a lightweight `task_log.json` per feature alongside the spec files.
- Never reads or interprets spec contents itself; it treats spec file paths as **opaque references** and delegates interpretation to Coder and Reviewer.
- Never creates commits, branches, or PRs; it only edits workspace files and reports what changed so you can commit/PR manually.

Orchestrator supports two entry modes:

#### Mode A – Proposal-first (create/update a spec)

Use this mode when the input is a **new proposal**, such as:

- Free-form feature description text.
- A path to a proposal-only markdown file (e.g., under `docs/proposals/`).
- An explicit request like "create a spec".

Workflow in Mode A:

1. **Call Planner**
   - Orchestrator invokes Planner via `runSubagent`, passing the proposal text or file path.
   - Planner runs its full requirements → design → tasks workflow.
   - When finished (and all three docs are approved), Planner returns:
     - `feature_name`
     - `requirements_ref`
     - `design_ref`
     - `tasks_ref`

2. **Capture spec references (metadata only)**
   - Orchestrator parses Planner's final summary.
   - It stores the spec file paths but **does not open or analyze** their contents.

3. **Create or update `task_log.json`**
   - Computes `feature_dir` from `requirements_ref` and `task_log_ref = <feature_dir>/task_log.json`.
   - If `task_log.json` does not exist, it creates a minimal JSON document, for example:
     - `feature`
     - `requirements_ref`, `design_ref`, `tasks_ref`, `task_log_ref`
     - `status` (e.g., `"spec_ready"`)
     - `history` (array with an entry recording spec creation via Planner + Orchestrator).
   - If it already exists, Orchestrator updates high-level fields (e.g., `status = "spec_updated"`) and appends a new `history` event.

4. **First Coder call**
   - Orchestrator calls **Coder** via `runSubagent`, passing:
     - `feature`
     - `requirements_ref`, `design_ref`, `tasks_ref`
     - Instructions to:
       - Read and understand the spec files.
       - Use `requirements.md` for *what*, `design.md` for *how*, and `tasks.md` as the actionable implementation checklist.
       - Implement tasks end-to-end using TDD and repo-appropriate best practices (Go/JS/HTML/CSS).
       - Run tests and other checks as needed.
       - Return a **change wrapper** with:
         - `feature`
         - `requirements_ref`, `design_ref`, `tasks_ref`
         - `changed_files`, `new_files`, `deleted_files`
         - `cli_runs` (commands/tests executed)
         - `tests_passed`
         - `notes` (summary, remaining work, blockers).

5. **Update task log after coding**
   - Orchestrator inspects the change wrapper.
   - It updates `task_log.json`, e.g.:
     - `status = "coding_complete"` if tests passed.
     - `status = "blocked"` if tests failed or there are known blockers.
     - Appends a `history` event summarizing test results + file counts.

6. **Reviewer call**
   - Orchestrator calls **Reviewer** via `runSubagent`, passing:
     - `feature`
     - `requirements_ref`, `design_ref`, `tasks_ref`
     - The full Coder change wrapper.
   - Reviewer compares the implementation against the spec and returns a **review wrapper** containing:
     - `feature`
     - `accepted` (boolean)
     - `must_fix`, `should_fix`, `nit` (lists of issues)
     - Optional `tests_passed`
     - `notes` (overall assessment).

7. **Handle review result & potentially re-call Coder**

   - If `accepted: true`:
     - Orchestrator updates `task_log.json` with `status = "accepted"` and appends a history event.
     - It generates a user-facing summary: feature name, spec refs, main changes, tests run, and a reminder that you must commit/PR manually.
     - Then it immediately returns to the TaskSync "request next task" state (running the Python task command in the terminal).

   - If `accepted: false`:
     - Orchestrator updates `task_log.json` with `status = "changes_requested"` and logs counts/themes of `must_fix`/`should_fix` items.
     - It re-calls **Coder** via `runSubagent`, passing:
       - The same spec refs.
       - The full review wrapper.
       - Instructions to:
         - Fix **all** `must_fix` items.
         - Fix `should_fix` where scope is reasonable and aligned with the spec/design.
         - Fix trivial, low-risk `nit` items.
         - For nits that would significantly expand scope or add risk, leave them and explain why in `notes`.

8. **Update task log after follow-up coding**
   - Orchestrator updates `task_log.json` based on the new Coder change wrapper (status + new `history` event).

9. **Repeat until accepted or stuck**
   - Orchestrator repeats the **Coder → Reviewer → task_log** loop until the Reviewer returns `accepted: true`.
   - If it detects a "stuck" loop (e.g., repeated reviews asking for the same unresolved fixes), it uses a Python `question = input('...')` command in the terminal to ask you explicitly how to proceed, summarizing the history and blockers.

Throughout Mode A, Orchestrator owns the TaskSync loop and Python task/question commands; Planner, Coder, and Reviewer operate as **bounded subagents**.

#### Mode B – Existing spec (skip spec creation)

Use this mode when the input points to **existing spec artifacts**, such as:

- A spec directory like `.docs/specs/add-region/`.
- Explicit paths to `requirements.md`, `design.md`, and/or `tasks.md`.
- An instruction like "start from this spec".

Workflow in Mode B:

1. **Skip Planner** – Orchestrator does **not** call Planner.
2. **Resolve spec refs** – It determines `requirements_ref`, `design_ref`, and `tasks_ref` from the given directory or paths (assuming standard filenames under `.docs/specs/<feature>/`).
3. **Create/update `task_log.json`** – Same behavior as Mode A step 3, still without reading the spec contents.
4. **Call Coder, then Reviewer, then loop** – It starts with Coder as in Mode A step 4 and follows the same steps (5–9), including updates to `task_log.json`, review cycles, and eventual acceptance.

In both modes, Orchestrator **never opens the spec documents**; it only passes paths around and manages orchestration + logging.

---

### Planner

`agents/Planner.agent.md`

Planner is a **spec creation agent**. It turns a rough feature idea into three spec artifacts under:

```text
.docs/specs/{feature_name}/
  requirements.md
  design.md
  tasks.md
```

Key behaviors:

- Works in two modes:
  - **Standalone Mode** – when invoked directly by a user; guides the user through requirements → design → tasks, asking for approval at each step and then stops after the spec is complete.
  - **Orchestrator Mode** – when invoked by Orchestrator via `runSubagent`; runs the same workflow but instead of concluding the conversation, it returns a **machine-readable summary**:
    - `feature_name`
    - `requirements_ref`
    - `design_ref`
    - `tasks_ref`
- Enforces a strict, iterative workflow:
  - Requirements are written and refined (EARS-style acceptance criteria) until explicitly approved.
  - Design is created and refined (overview, architecture, components, data models, error handling, testing strategy) until approved.
  - Tasks are created as an actionable, code-focused checklist until approved.
- Uses Python `question = input('...')` commands to get explicit user approval before advancing to the next stage.
- **Never executes implementation tasks** from `tasks.md`; it only creates and updates the spec documents.

Planner is the **source of truth for spec artifacts**; Orchestrator, Coder, and Reviewer all treat these files as authoritative.

---

### Coder

`agents/Coder.agent.md`

Coder is a **staff-engineer-level implementation agent** for Go/JS/HTML/CSS and related assets. It:

- Inherits TaskSync V5 and obeys all primary directives (no auto-termination, no concluding language).
- Is normally invoked by Orchestrator with:
  - `feature`
  - `requirements_ref`, `design_ref`, `tasks_ref`
  - Optionally a `review_wrapper` from Reviewer.
- Reads and interprets the spec files:
  - Uses `requirements.md` to understand *what* must be built.
  - Uses `design.md` to understand *how* it should be structured.
  - Uses `tasks.md` as the step-by-step implementation checklist.
- Implements tasks using **TDD and small, incremental changes**.
- Runs tests and other relevant commands.
- On follow-up calls, focuses on addressing review feedback:
  - Always addresses `must_fix`.
  - Usually addresses `should_fix` if scope is reasonable.
  - Applies trivial `nit` items; may skip risky or high-scope nits but must explain why in `notes`.

Coder returns a **change wrapper** including at least:

- `feature`
- `requirements_ref`, `design_ref`, `tasks_ref`
- `changed_files`
- `new_files`
- `deleted_files`
- `cli_runs` (commands/tests executed)
- `tests_passed` (summary of outcomes)
- `notes` (tasks completed, feedback addressed, open questions/risks)

Constraints:

- Coder **must not** call `runSubagent` or other agents.
- Coder **must not** create commits, branches, or PRs.

---

### Reviewer

`agents/Reviewer.agent.md`

Reviewer is a **staff-engineer-level review agent** for Go/JS/HTML/CSS and related assets. It:

- Inherits TaskSync V5 and obeys all primary directives.
- Is normally invoked by Orchestrator with:
  - `feature`
  - `requirements_ref`, `design_ref`, `tasks_ref`
  - A Coder **change wrapper**.
- Opens and reads the spec documents and relevant code/tests.
- Optionally re-runs tests and tools.
- Evaluates the implementation for:
  - Correctness and alignment with requirements.
  - Conformance to the design.
  - Test quality and coverage.
  - Security, performance, concurrency, error handling.
  - Readability, maintainability, and (for frontends) accessibility/UX.
- Classifies findings into:
  - `must_fix` (blocking issues)
  - `should_fix` (important but non-blocking improvements)
  - `nit` (small, low-risk suggestions)

Reviewer returns a **review wrapper** including at least:

- `feature`
- `accepted` (boolean)
- `must_fix`
- `should_fix`
- `nit`
- Optional `tests_passed`
- `notes` (overall assessment and key callouts)

Constraints:

- Reviewer **must not** call `runSubagent`.
- Reviewer **must not** create commits, branches, or PRs.


## `task_log.json` state tracking

For each feature, Orchestrator maintains a `task_log.json` file in the same directory as the spec files (e.g., `.docs/specs/{feature_name}/task_log.json`). It:

- Stores pointers to the spec files: `requirements_ref`, `design_ref`, `tasks_ref`, `task_log_ref`.
- Tracks a `feature` name and high-level `status` such as:
  - `spec_ready`
  - `spec_updated`
  - `coding_complete`
  - `blocked`
  - `changes_requested`
  - `accepted`
- Maintains a `history` array with timestamped events summarizing:
  - Spec creation/updates by Planner.
  - Coder passes (including test results and change summaries).
  - Reviewer passes (including whether they were accepted or requested changes).

`task_log.json` provides a **lightweight, file-backed state machine** for each feature so the workflow can be resumed or inspected later without relying on large in-memory prompts.


## Using this workflow in VS Code

At a high level, usage looks like this:

1. **Configure custom agents**
   - Point VS Code (GitHub Copilot / custom agents) at the `agents/*.agent.md` files so `TaskSync`, `Planner`, `Orchestrator`, `Coder`, and `Reviewer` appear in the agent picker.

2. **Drive everything through TaskSync + Orchestrator**
   - Start with the **TaskSync** agent to enforce the continuous terminal-driven loop.
   - Use **Orchestrator** as your main assistant for feature work:
     - For new features, provide a proposal and let it run **Mode A** (Planner → Coder → Reviewer).
     - For existing features with specs, provide the spec directory or file paths and let it run **Mode B**.

3. **Review & commit manually**
   - Inspect the generated/updated spec files, code, tests, and `task_log.json`.
   - When satisfied, create your own commits, branches, and PRs; the agents never push or commit for you.

## Future improvements
- Add a research agent that can gather context, links, and references based on the feature proposal before calling Planner.
- Add a git commit agent that can create commits based on `task_log.json` summaries, but still requires user approval before committing.
- Add a pull/merge request generation agent that can create PRs based on `task_log.json` summaries, but still requires user approval before merging.
- Add CI integration agent that can run tests and report results back into the Orchestrator workflow.
- Add CD agent that can help with deployment steps based on the completed feature.


## Guardrails & design goals

This orchestrated setup is designed to:

- Keep **specs as the source of truth**, with Planner owning their creation and evolution.
- Use Orchestrator to manage **cross-agent coordination and feature-level state**, without reading large spec contents itself.
- Encourage **TDD and incremental implementation** via Coder.
- Enforce **structured, high-signal review** via Reviewer, with clear `must_fix` / `should_fix` / `nit` separation.
- Maintain TaskSync's guarantee of **non-terminating, terminal-driven sessions**, so you can continuously feed new work into the system.

This README is a conceptual guide; for exact operational rules, see the individual agent definitions in `agents/`.