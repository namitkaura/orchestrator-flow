# Orchestrator Flow

Orchestrator Flow takes a proposal or bug report through **Planner → Architect → Coder → Reviewer**, coordinated by **Orchestrator**. The current **2.1.0** workflow, identified by the canonical [VERSION](VERSION), is implemented for **Codex and Claude Code**. GitHub Copilot and Cursor retain their committed native implementations; their v2 updates are deferred.

This repository is the installation source. Maintaining its artifacts does not run the consumer workflow here. See [AGENTS.md](AGENTS.md) for maintenance boundaries and validation. The separate legacy BugAgents, CoordinatorVersion and TaskSync implementations are outside the v2 work.

## Integrations and ownership

| Platform | Entry point and artifacts | Current scope |
| --- | --- | --- |
| Codex | [Orchestrator Flow skill](.codex/skills/orchestrator-flow/SKILL.md) | v2; actual native subagents, with no virtual/in-place role fallback |
| Claude Code | `/orchestrator-flow`, [Orchestrator Flow skill](.claude/skills/orchestrator-flow/SKILL.md), [agents](.claude/agents/orchestrator-flow) | v2; real `flow-*` subagents started by the main conversation, with no in-place role fallback |
| GitHub Copilot | Select **Orchestrator** in the custom-agent selector; [agents](.github/agents), [prompts](.github/prompts/prompts.md) | Existing custom agents; v2 deferred |
| Cursor | `/cursor-orchestrate`, [rule](.cursor/rules/Orchestrator.mdc), [agents](.cursor/agents), [command](.cursor/commands/cursor-orchestrate.md) | Existing rule, command and agents; v2 deferred |

In v2 (Codex and Claude Code), Orchestrator owns user interaction, initialization, configuration, `task_log.json`, `known-issues.md`, log checkpoints and recovery coordination. Planner publishes requirements/design/tasks/research artifacts; Coder publishes its implementation/tests/docs and task-completion progress. Architect and Reviewer assess work read-only. Coder's helpers explore and execute tests without intentional edits or publication. Git ownership is serialized through the active producer and coherent yields; no agent performs the final squash merge.

Each v2 integration carries its own native contracts, schemas, examples and runtime scripts: Codex in [.codex/skills/orchestrator-flow](.codex/skills/orchestrator-flow) and Claude Code in [.claude/skills/orchestrator-flow](.claude/skills/orchestrator-flow). Their contracts ([Codex protocol](.codex/skills/orchestrator-flow/references/workflow-protocol.md), [Claude Code protocol](.claude/skills/orchestrator-flow/references/workflow-protocol.md), `assurance.md` and the role references) are written for each platform with the same meaning. Their shared runtime files (the JSON schemas, validator and recorder, protocol replay, document reader, checkpoint helper and `requirements.txt`) are byte-identical, which a repository test enforces, so a task log means the same thing on both. GitHub Copilot and Cursor retain their own substantive instructions and do not load either v2 implementation. The v2 runtime behavior below applies to Codex and Claude Code; project coding guidance and reusable input templates apply to all four platforms.

| Source location | Purpose |
| --- | --- |
| [.codex/skills/orchestrator-flow/](.codex/skills/orchestrator-flow) | Codex instructions, UI metadata, role references, schemas, examples, runtime scripts, dependency declaration, and version/template symlinks |
| [.claude/skills/orchestrator-flow/](.claude/skills/orchestrator-flow) | Claude Code skill: instructions, role references, schemas, examples, runtime scripts (including the Claude-only startup check and log writer), dependency declaration, and version/template symlinks |
| [.claude/agents/orchestrator-flow/](.claude/agents/orchestrator-flow) | Claude Code subagents for the four roles and the two helper types |
| [Directives/codingAgentDirectives.md](Directives/codingAgentDirectives.md) | Reusable coding guidance for projects using any of the four platforms; copy and customize per project, separately from workflow installations |
| [tests/](tests) | Repository development tests and fixtures, outside all platform-specific integration directories |
| [.docs/v2.0.0/](.docs/v2.0.0/) | Workflow and test-kit proposals, corrections, and release validation summaries |
| [.docs/v2.1.0/](.docs/v2.1.0/) | Claude Code integration proposal and handoff |
| [tests/live/](tests/live/README.md) | Reusable live test kit: bootstrap setup, twelve feature cases, prompts, evidence, and run-retention instructions |

## Codex setup: link the source checkout

Keep this checkout available and link its skill directory into the user's Codex skills directory. These examples assume the destination does not already exist and its parent directory does. Inspect existing installations before making setup changes.

POSIX:

```sh
ln -s "[ORCHESTRATOR_REPO_PATH]/.codex/skills/orchestrator-flow" ~/.codex/skills/orchestrator-flow
```

PowerShell:

```powershell
$skillSource = Join-Path '[ORCHESTRATOR_REPO_PATH]' '.codex/skills/orchestrator-flow'
$skillDestination = Join-Path $env:USERPROFILE '.codex/skills/orchestrator-flow'
New-Item -ItemType SymbolicLink -Path $skillDestination -Target $skillSource
```

The skill accesses its own `references/` and `scripts/` directly. Its two external resources are real relative symlinks inside the checkout:

| Skill entry | Relative target |
| --- | --- |
| `VERSION` | `../../../VERSION` |
| `templates` | `../../../templates` |

Git stores each symlink as mode `120000` with its relative target, so the reference survives a push/clone when the checkout supports symlinks. When staging these entries, verify their modes with `git ls-files --stage -- .codex/skills/orchestrator-flow/VERSION .codex/skills/orchestrator-flow/templates`.

Windows needs permission to create symlinks (an administrator shell, or a supported Developer Mode setup) and Git's `core.symlinks=true`. For a new checkout, use `git clone --config core.symlinks=true <REPOSITORY_URL> <CHECKOUT_PATH>`. For an existing checkout, setting `git config --local core.symlinks true` does not itself convert already flattened links. Repair them as real relative symlinks before using the skill. `Get-Item <SKILL_PATH>/VERSION,<SKILL_PATH>/templates | Format-Table Name,LinkType,Target` should show `SymbolicLink` and the targets above. A broken link or a regular file containing a relative path is a setup error; no text-pointer or copy/export fallback is supported.

### Runtime Python dependency

Python 3.10+ runs the helpers. Install the declared dependency once in the Python environment that will run them, from the checkout:

```sh
python -m pip install -r .codex/skills/orchestrator-flow/scripts/requirements.txt
```

Use `python3` where appropriate and `python` on Windows, consistently selecting the same environment for setup and helper execution. `scripts/requirements.txt` declares `jsonschema>=4.18,<5`, which supplies the JSON Schema validator. Revisit setup when its requirements change. This is workflow setup; do not add this dependency to each consuming project's dependency files. Runtime scripts remain in the skill, while development tests remain in this repository's `tests/` directory.

## Claude Code setup: link the skill and agents

The Claude Code integration is the [Orchestrator Flow skill](.claude/skills/orchestrator-flow/SKILL.md) plus six subagents in [.claude/agents/orchestrator-flow](.claude/agents/orchestrator-flow):

| Agent | Role |
| --- | --- |
| `flow-planner` | Planner: requirements, design and tasks |
| `flow-architect` | Architect: read-only specification review |
| `flow-coder` | Coder: implementation, tests, documentation and task progress |
| `flow-reviewer` | Reviewer: read-only implementation review |
| `flow-explorer` | Exploration and research helper, started by a lead |
| `flow-runner` | Test and check runner, started by a lead |

The main conversation is Orchestrator. It starts each lead as a real subagent with the feature's accepted model and effort, continues each lead across approvals and repairs by its agent ID, and records every return directly from the subagent's transcript, so large returns are never copied by hand. Leads start their own helpers. The `flow-` prefix keeps these agents from colliding with a project's own agents; you, the task log and the contracts still use the role names.

### Link the two folders

Keep this checkout available and link its two folders into your Claude Code folders. Both destinations are subfolders, so your other skills and agents keep working beside them. These commands assume the destinations do not already exist:

```sh
mkdir -p ~/.claude/skills ~/.claude/agents
ln -s "[ORCHESTRATOR_REPO_PATH]/.claude/skills/orchestrator-flow" ~/.claude/skills/orchestrator-flow
ln -s "[ORCHESTRATOR_REPO_PATH]/.claude/agents/orchestrator-flow" ~/.claude/agents/orchestrator-flow
```

The skill's `VERSION` and `templates` entries are real relative symlinks (`../../../VERSION` and `../../../templates`) stored by Git as mode `120000`, exactly as in the Codex skill. A missing, broken or flattened link is a setup error.

The previous Claude Code integration linked the whole `~/.claude/agents` directory to this checkout and linked a single `~/.claude/commands/orchestrate.md`. Before adding the two links above, check with `ls -l ~/.claude ~/.claude/commands`, then replace that installation:

```sh
rm ~/.claude/agents                      # only when it is a symlink to this checkout
mkdir ~/.claude/agents
rm ~/.claude/commands/orchestrate.md
```

The workflow never changes these paths itself. Features started under the old `/orchestrate` workflow cannot continue under v2, and their logs remain unsupported.

### Python runtime

The workflow scripts need Python 3.10+ with `jsonschema`. Create a dedicated virtual environment inside the skill, where it is ignored by Git, and install the declared requirements into it:

```sh
python3 -m venv "[ORCHESTRATOR_REPO_PATH]/.claude/skills/orchestrator-flow/.venv"
"[ORCHESTRATOR_REPO_PATH]/.claude/skills/orchestrator-flow/.venv/bin/python" -m pip install -r "[ORCHESTRATOR_REPO_PATH]/.claude/skills/orchestrator-flow/scripts/requirements.txt"
```

Every workflow script runs as `<skill-dir>/.venv/bin/python <skill-dir>/scripts/<script>.py`, in the CLI and the desktop app alike. The one exception is the startup check, which uses `python3` so that it can report a missing or broken venv, for example after a system Python upgrade, together with the commands that recreate it. Do not add this dependency to consuming projects.

### Version requirement

Orchestrator Flow requires **Claude Code 2.1.296 or newer**. Every `/orchestrator-flow` invocation, including a resume, first runs `scripts/check_claude_code.py`, which reports the version of the Claude Code actually running the session and stops the workflow with an update message when it is older. The CLI and the desktop app run separate copies of Claude Code: check the CLI with `claude --version` and update it with `claude update`; the desktop app's bundled Claude Code changes only when you update the Claude app. If the check cannot run as part of the skill, Orchestrator runs it itself, and asks you before continuing when the version stays unknown.

### Start a feature

```text
/orchestrator-flow .docs/specs/<feature>/proposal.md
```

The skill starts only when you invoke it; Claude never starts it on its own. Orchestrator recommends a complete configuration with a reason for each choice, and you accept or override any part. Repository defaults live in the consumer's `.orchestrator-flow.json`; these are the suggested starting defaults:

```json
{
  "assurance_level": "standard",
  "capability_defaults": {
    "claude-code": {
      "planner": {"model": "opus", "reasoning_effort": "xhigh"},
      "architect": {"model": "opus", "reasoning_effort": "max"},
      "coder": {"model": "opus", "reasoning_effort": "high"},
      "reviewer": {"model": "opus", "reasoning_effort": "max"},
      "exploration_helpers": {"model": "sonnet", "reasoning_effort": "medium"},
      "helpers": {"model": "haiku", "reasoning_effort": "medium"}
    }
  }
}
```

Models are Claude Code's short names `opus`, `sonnet`, `haiku` and `fable`. A short name resolves to the newest model in its family, or to the session's own model version when the session uses that family, so the log records the name chosen rather than an exact model version. Efforts are `low`, `medium`, `high`, `xhigh` and `max`, and the log always records an explicit effort. `exploration_helpers` assigns the exploration and research helpers; `helpers` assigns the test and check runners. These are defaults, not rules: Orchestrator may recommend Fable for a hard feature's Planner, Architect or Reviewer, or medium effort for a routine feature's Coder. Fable costs more than Opus, can bill usage credits and falls back to another model automatically when its safety classifiers flag a request; choosing it records that as an accepted limitation. `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` and `CLAUDE_CODE_EFFORT_LEVEL` override per-role choices; the startup check reports them and Orchestrator asks you to accept or remove them.

Leads run in the background, so you can keep talking to Orchestrator during long runs, for example to answer a question, approve a document or change a setting. `/tasks` lists the running agents. After an interruption, resume the same session (reopen it in the desktop app, or run `claude --resume` in the CLI) and run `/orchestrator-flow` again; Orchestrator continues each lead by its agent ID.

### Permissions

Auto mode, Claude Code's default starting mode, is the recommended mode for workflow sessions because it lets long runs continue while you are away. What to expect:

- The first time a role reads the skill's references outside the project, Claude Code asks once; choose to keep allowing such reads.
- Checkpoint pushes to the feature branch run without a prompt.
- The classifier can block an action, and the agent reports the block with its rule name. After three blocks in a row or twenty in total, auto mode falls back to prompts and the run waits for you.
- If the classifier flags a role's report, Orchestrator shows you the warning before acting on it.
- The classifier adds latency and, on API or Enterprise billing, token cost. Narrow allow rules for the commands below skip it.

If you prefer to approve commands yourself, use `acceptEdits` mode with allow rules like these in `~/.claude/settings.json`, replacing `<skill-dir>` with the absolute skill path that appears in the workflow's commands:

```json
{
  "permissions": {
    "allow": [
      "Read(~/.claude/skills/orchestrator-flow/**)",
      "Bash(<skill-dir>/.venv/bin/python <skill-dir>/scripts/*)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(git push *)"
    ]
  }
}
```

`Bash(git push *)` also matches force-push variants; add ask or deny rules for them if you want that guard, although no workflow role force-pushes. A background agent's permission prompts appear in the main session and name the agent. Architect, Reviewer and the helpers have no edit tools, but their Bash use stays read-only by contract rather than by enforcement. Headless `claude -p` runs are not supported, because they deny permission prompts. The workflow never changes the session's permission mode.

### Standalone roles

Each lead can be used without Orchestrator. Ask for it by name in any session, for example "use flow-reviewer to review these changes"; it runs as a subagent and returns its questions to that session. Or start a session as the role with `claude --agent flow-reviewer`, and it asks you directly. Standalone use never creates orchestration approvals.

Windows setup for Claude Code is not covered yet.

## Project coding guidance

[Directives/codingAgentDirectives.md](Directives/codingAgentDirectives.md) is an optional starting point for a project's coding conventions on **all four platforms: Codex, Claude Code, GitHub Copilot, and Cursor**. Copy it to a suitable location in the consuming repository, keep the relevant language sections, and customize its frameworks, tooling and conventions. Identify that project-owned file in the project's native instruction file or README so the chosen platform's agents can find it.

Maintain the project's copy independently of the workflow installation. Keep the reusable source in this repository's `Directives/` directory, separate from platform-specific workflow artifacts. Workflow assurance, approvals, task ownership and recovery belong in each platform's workflow contracts rather than the coding-directives document.

Codex and Claude Code v2 follow this separation. The deferred Copilot and Cursor implementations still have their existing Directives references; those remain unchanged in this phase and will need to align with the same project-owned guidance policy when updated.

## Capability and feature configuration

During first setup, establish repository defaults with the user in committed consumer-root `.orchestrator-flow.json`. Do not add these defaults to `AGENTS.md`. Model and effort are configured separately from assurance for Planner, Architect, Coder, Reviewer and helpers, with an optional separate assignment for exploration helpers.

An illustrative Codex default file is below. Replace `YOUR_AVAILABLE_MODEL` and confirm supported effort values through the user's native configuration; these are examples, not a model fallback chain or a claim of availability:

```json
{
  "assurance_level": "standard",
  "capability_defaults": {
    "codex": {
      "planner": {"model": "YOUR_AVAILABLE_MODEL", "reasoning_effort": "high"},
      "architect": {"model": "YOUR_AVAILABLE_MODEL", "reasoning_effort": "high"},
      "coder": {"model": "YOUR_AVAILABLE_MODEL", "reasoning_effort": "high"},
      "reviewer": {"model": "YOUR_AVAILABLE_MODEL", "reasoning_effort": "high"},
      "helpers": {"model": "YOUR_AVAILABLE_MODEL", "reasoning_effort": "medium"}
    }
  }
}
```

The configuration schema retains the platform identifiers `codex`, `claude-code`, `github-copilot`, and `cursor`; Codex and Claude Code implement v2, and the other identifiers do not imply v2 support in the deferred integrations. An optional `exploration_helpers` assignment gives exploration and research helpers their own model and effort, leaving `helpers` for test and check execution; when it is absent, `helpers` covers both, exactly as in 2.0.0. Claude Code uses it (see [Claude Code setup](#claude-code-setup-link-the-skill-and-agents)); Codex keeps a single `helpers` assignment in 2.1.0. For the Codex setup, configure the `codex` assignments for all five roles. Check available model/reasoning controls and native agent settings, present per-role recommendations, and record the user's accepted values. Configure a matching native agent or use an invocation override where supported; a role prompt alone does not enforce model/effort.

### Codex native assignments

For clients supporting custom-agent TOML files, create one file per delegated role under the consumer's `.codex/agents/` or `~/.codex/agents/`. For example, `.codex/agents/flow-planner.toml`:

```toml
name = "flow_planner"
description = "Planner for explicitly requested Orchestrator Flow work."
model = "YOUR_AVAILABLE_MODEL"
model_reasoning_effort = "high"
developer_instructions = """
Follow the Planner contract, common essentials, applicable assurance and
project guidance supplied by Orchestrator. Return bounded structured outputs;
Orchestrator owns user gates and the task log; Planner publishes its artifacts.
"""
```

Create corresponding Architect, Coder, Reviewer and helper definitions with the accepted assignments. A custom file's model/effort can take precedence over spawn settings; keep it consistent with the feature snapshot, including overrides. Where the native spawn interface directly exposes model/effort, use those controls without a conflicting custom profile. Confirm the effective assignment before work. See [official Codex subagent configuration](https://learn.chatgpt.com/docs/agent-configuration/subagents).

### Feature acceptance and overrides

Both v2 skills use accepted feature assignments rather than fixed model choices. Explicit `platform_default` values or `not_supported` effort require disclosure and user acceptance of the actual native limitation. Record concrete effective values when exposed. If an explicit assignment cannot be honored, or a lead/helper reaches a model limit, pause affected work and ask whether to choose another assignment or wait. Never silently fall back or change assurance with a model substitution.

At the beginning of each feature, Orchestrator reads defaults, assesses the proposal, presents recommendations for acceptance/override, and stores the **complete resolved feature configuration** in the task log before Planner runs. On resume that snapshot governs. Default changes affect future features; applying them to this feature requires a recorded `user-override`. Feature acceptance does not silently change repository defaults.

The built-in `review_disposition_policy` is `spec_user_code_auto`: user disposition of Architect findings before Planner revision, routine in-scope Reviewer-driven repairs allowed. Explicit feature alternatives are `all_user` and `within_scope_auto`. The effective policy is top-level in the task log, not a repository-default field. All alternatives preserve material artifact approvals, product decisions, must-fix exceptions, loop limits and operational authorization.

## Assurance and review

| | Basic | Standard | Maximum |
| --- | --- | --- | --- |
| Initial review | Complete relevant spec and implementation | Complete relevant spec and implementation | Complete exhaustive review |
| Follow-up | Focused, expanding when consequences/evidence warrant | Focused, affected or full according to impact | Comprehensive on each required pass |
| Remediation | Practical benefit, likelihood, consequences and total workflow cost | Stronger presumption toward robustness/repair | Existing rigorous repair and justified-deferral obligations |
| Further repair gate | Before a second repair-and-re-review cycle | Before a third | Existing rigorous loops and stalled-loop safeguards |

Classification itself reflects the agreed acceptance standard. Findings explain factual behavior, conditions and actual project consequences, distinguishing demonstrated defects, hardening opportunities and preferences. A personal project's optional improvement need not receive a consequential deployment's completion priority. Facts stay accurate; explicit must-fix exceptions require user disposition. A nonempty known-issues document does not automatically prevent acceptance. Completed nit-only reviews are accepted by default at every assurance, including Maximum; Orchestrator derives their deferral and known issues without a producer response, another approval or a polishing cycle. An explicit user request to repair a nit uses the existing findings-decision and repair path, including its allowances and follow-up review. Nits cannot excuse missing required work, checks or consequential findings. Basic weighs should-fix benefit against total follow-up cost; Standard normally repairs should-fix unless there are concrete exceptional grounds.

Basic/Standard check source/assumption changes, reuse valid completed evidence, and repeat affected or incomplete work. Maximum actively revalidates decision-critical evidence even when sources appear unchanged. Helpers separate observations, inferences, gaps and uncertainty with verifiable references. Leads own synthesis. Preserve ongoing role context across checkpoints where supported; full review obligations concern the work performed, not starting a new agent.

Basic/Standard use targeted Red/Green checks and broader integration/final checks, reusing fresh applicable evidence. Report corrections, checkbox changes and unrelated documentation do not alone invalidate results. Reviewer independently evaluates code/assertions and reruns where useful; Maximum retains comprehensive fresh checks. Coder reuses suitable exploration/test helpers, keeps tested work stable, and reports concise command/status/count/failure evidence once.

If assurance increases while a review is running, record its output against the settings it actually used. Compare that result with the current requirement; any gap requires catch-up review before dependent coding or final completion, including when this was the first review.

See the assurance rubric ([Codex](.codex/skills/orchestrator-flow/references/assurance.md), [Claude Code](.claude/skills/orchestrator-flow/references/assurance.md)) for classification, acceptance, task boundaries and proportionate test execution. Each skill's Maximum checklists, exceptional-phase and recovery references are loaded when applicable.

## Artifacts and user gates

Consumer artifacts live under `.docs/specs/{feature}/`. Requirements, design and tasks are mandatory, with separate approvals in dependency order. A material upstream decision must be approved before dependent revisions proceed. Unaffected artifacts need no artificial changes or renewed approval. Editorial corrections, faithful recording and task-progress accounting preserve a real approval basis with rationale.

Feedback received while Planner is drafting stays in the current creation or revision cycle, even when an earlier spec handoff has already completed. Record the clarification and subsequent draft updates, preserve the existing Planner context where supported, and continue the approval path. A new revision starts when feedback arrives outside active drafting; clarifications within a cycle do not consume extra repair cycles.

Required documents have independent integer content versions from the first draft and a final Revision History. Every completed content update increments its document version, including separate updates in one session. Pure approvals do not change documents. Spec documents contain no duplicated workflow/Git metadata. Read current bodies with the streaming body reader; retrieve history explicitly when needed.

Task-checkbox progress preserves the tasks version, Revision History, producing Planner reference and approval. Coder changes only actual numbered completion marks; Planner owns wording, numbering, dependencies and editorial revisions. Bounded reader chunks use normalized character offsets, so truncated output can be reread without losing the end of a line. Initial review still covers every current spec body at all assurance levels.

`task_log.json` holds append-only events, effective configuration, requests, actual outputs, approvals, findings/dispositions and recovery authority. Planner returns requirements and design drafts at their approval gates, then supplies the consolidated handoff with the final tasks draft. Unchanged tasks approval establishes spec_ready and enables Architect using that same immutable return plus approval context; no extra Planner invocation or duplicate wrapper. Coder normally returns one cumulative wrapper per completed assignment/repair; ordinary artifact checkpoints need no wrapper or acknowledgement. The coding-updated event contains coordination details only, preserving progress and blockers without claiming completion. Required returns are complete actual JSON, never file pointers. Normal operation creates no scratch role artifacts; validate directly in memory or through stdin. Optional research has no content version or separate approval gate. Orchestrator maintains current deferred findings/accepted limitations in `known-issues.md`; resolved history remains in the log and review summaries/evidence.

Exceptionally large tasks plans may propose stable implementation phases through the existing tasks approval. Basic skips intermediate reviews; Standard uses Basic, and Maximum uses Standard, with one/two repair cycles per intermediate stage. Required intermediate capability retains the full Reviewer model with effort `max → high`, `xhigh → medium`, or `high → low`, recorded in feature configuration. Basic needs no unused assignment; unmapped/unsupported settings require explicit direction. Final review always uses full feature settings and its separate allowance. The last Coder integrates and reports the entire feature and owns all final repairs. Natural Markdown checkpoint groups alone do not justify phases.

Assurance changes reuse all applicable accepted evidence: unchanged Maximum evidence remains sufficient after lowering and restoring assurance. Real content/source/assumption gaps require bounded assessment or review, scoped independently to specification, phase or final implementation. Applicability assessments grant neither higher assurance nor new acceptance; required Maximum review work remains comprehensive.

All levels preserve Scaffolding boundaries, separate Red/Green tasks sized around coherent behavioral changes, production-only Refactor, concrete Documentation, Planner-defined final Test-Maintenance and repair-free Verification. Planning supplies concrete design, targets, dependencies and requirement mappings. Diagrams are used when useful, without a compulsory diagram at any level. Coder may mark task progress, not redesign the plan. Architect approval is distinct from user authorization to begin coding. Reviewer approval is distinct from final feature acceptance.

## Checkpoints, interruptions and final merging

Initialize the explicit user branch or otherwise exactly the feature name, keeping a release version when the feature name has one (`v2.1.0-claude-code-integration`) and the bare name otherwise (`unique-lines`). Validate it with Git and record the integration target, remote and baseline. Never add a `codex/`, `claude/` or other prefix or invent a product version; conflicts need direction. Every artifact and log checkpoint is committed on and pushed to that feature branch, never the integration branch. Use the existing checkout unless a worktree was explicitly requested. Planner checkpoints substantive artifacts before handoff. Coder checkpoints approved natural task groups, meaningful partial work and completion. Orchestrator separately checkpoints every authoritative log update, approval, decision and review return. Deliberately Red work is described accurately. Checkpoints grant neither approval nor merge readiness.

Every checkpoint has feature/kind/role trailers; producer artifacts also identify invocation and applicable phase. Only log commits carry the log path and contiguous event range. Wrappers identify already-published artifact commits; no event stores its containing log checkpoint's own hash. No ordinary checkpoint or success-receipt event is added. Resume reconciles metadata and names/statuses, paginating recent commits as needed, with remote delivery and actual native/user evidence. Orchestrator delegates content inspection and recovers existing producers before replacement. Coder reconstructs cumulative work against its original baseline, distinguishing recovered verification from newly run checks.

On a failed push, preserve the local commit and failure evidence, globally pause work, and obtain direction. Before an authorized retry, commit the failure context and retry-authorization update. One push then delivers the outstanding checkpoint plus this update. Git proves successful delivery; do not create a success receipt or another commit/push. A failed retry is immediately preserved locally and requires new direction. The final checkpoint uses the same sequence, leaving no pending success receipt or extra approval.

If an attempt was recorded but its result is unknown after interruption, inspect Git first. When delivery cannot be established, a fresh explicit authorization may permit one more push. Record the original attempt and the actual observation in `uncertain_attempts`, commit the authorization, then record the new attempt before dispatch. Do not invent a failure or reuse a consumed allowance. `checkpoint_state.py inspect` supplies the uncertain-attempt context; it never authorizes or performs a push.

Other blockers pause only affected operations/dependencies while independent approved work can continue. Model unavailability requires user direction; no automatic fallback. Ordinary role failures preserve context and completed evidence, with three total attempts before further direction. Bound external-operation retries to their actual authorization.

After Reviewer acceptance, present delivery, verification and known issues for **explicit user feature acceptance**. Record `implementation-complete` with status `implementation_complete`, complete its checkpoint delivery, and then provide one conventional squash-commit message covering the total final change against the baseline. A commit-message request does not itself authorize completion. The user manually merges into `main` or the explicitly selected integration branch. No agent performs that merge or deployment.

## Proposal and bug-report templates

These reusable inputs apply to all four platforms.

- [Proposal template](templates/proposal-template.md): feature/improvement intent, rationale, settled decisions and important constraints.
- [Bug-report template](templates/bugreport-template.md): observed failure, reproduction, expected correction and relevant preservation boundaries without requiring a speculative diagnosis.

Each is self-contained with visible Markdown authoring guidance, section expectations and optional heading hierarchy. No earlier proposal/report is needed as a style reference. Copy the appropriate template into a completed document in the consuming repository, following that repository's artifact-location conventions; do not overwrite the reusable template.

Remove the template-version line, authoring guidance, examples, instructional text and placeholders. Preserve the applicable completed-document outline and scale detail to the work. Invoke `$orchestrator-flow` in Codex or `/orchestrator-flow` in Claude Code with the completed document's path. Copilot and Cursor retain their existing entry points listed above.

Each template currently has independent integer **template version 2**. These integers track authoring contracts, independently of each other, workflow semantic versions, product releases and spec content versions. Both v2 skills access the canonical files through their real `templates/` symlinks.

## Compatibility and validation

The workflow applies accepted settings to subsequent affected work while preserving the logical assignment, cumulative baseline, approvals, progress and repair allowances. Reuse the native context where supported; capability-only changes do not invalidate useful in-flight results. Assurance remains a separate gate based on actual review work. Required returns are validated before recording. Small report corrections stay in the same assignment without failure records, empty commits or automatic retesting; genuine failures retain bounded recovery.

The `record-handoff` command takes the actual native wrapper JSON once, derives the event, ID, causal requestor, UTC timestamp and state, and records it unchanged in the selected task log. Internal validation/readback checks preserve the historical prefix and captured values. It never commits or pushes; other validator commands remain read-only. Use UTF-8 stdin. In PowerShell set `$OutputEncoding = [System.Text.UTF8Encoding]::new($false)` before piping literal Unicode. See the [workflow protocol](.codex/skills/orchestrator-flow/references/workflow-protocol.md#compact-returns-and-recording) for the input format, in-memory API and recovery rules. In Claude Code, `claude_log.py record-return` reads a role's return directly from its subagent transcript and records it through the same recorder, and `claude_log.py append-entry` records Orchestrator's own entries after validating them; see the [Claude Code protocol](.claude/skills/orchestrator-flow/references/workflow-protocol.md#compact-returns-and-recording).

Version 2.1.0 applies to new work. Logs written by 2.0.0 stay valid under 2.1.0 readers, and an absent `exploration_helpers` assignment keeps its 2.0.0 meaning. Pre-2.0/missing-version logs are unsupported; stop and obtain direction rather than migrate or repair automatically. Completed historical features remain untouched. Patch/minor releases preserve older supported logs' execution and approval meaning, with actual documented defaults for compatible additions. Exact-version-only checks must not reject an older supported log under a compatible newer reader. Older readers need not understand newer logs; major changes require an explicit compatibility boundary.

Run these commands from the source checkout. Runtime commands can also use the linked skill's `scripts/` path; the unittest and Git checks are repository development checks:

```sh
python .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py task-log <TASK_LOG> --workspace <CONSUMER_ROOT>
python .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py repository-config <REPOSITORY_CONFIG>
python .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py spec-change-wrapper <WRAPPER>
python .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py spec-review-wrapper <WRAPPER>
python .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py change-wrapper <WRAPPER>
python .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py review-wrapper <WRAPPER>
python .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py resume-action <TASK_LOG> --observations <OBSERVATIONS_JSON>
python .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py record-handoff - --log <TASK_LOG> --workspace <CONSUMER_ROOT>
python .codex/skills/orchestrator-flow/scripts/read_spec_body.py <SPEC_DOCUMENT> --offset 0 --max-chars 8000
python .codex/skills/orchestrator-flow/scripts/checkpoint_state.py inspect <TASK_LOG> --repo <CONSUMER_ROOT>
python .codex/skills/orchestrator-flow/scripts/checkpoint_state.py recent <TASK_LOG> --repo <CONSUMER_ROOT> --limit 20
python3 .claude/skills/orchestrator-flow/scripts/check_claude_code.py
.claude/skills/orchestrator-flow/.venv/bin/python .claude/skills/orchestrator-flow/scripts/claude_log.py record-return --log <TASK_LOG> --agent-id <AGENT_ID> --workspace <CONSUMER_ROOT>
.claude/skills/orchestrator-flow/.venv/bin/python .claude/skills/orchestrator-flow/scripts/claude_log.py append-entry --log <TASK_LOG> --workspace <CONSUMER_ROOT> < <ENTRY_JSON>
python -B -m unittest discover -s tests -v
git diff --check
```

Primary validator input `-` reads actual JSON on stdin. For candidate updates, `task-log - --previous <AUTHORITATIVE_LOG>` verifies append-only history without creating snapshots. `--observations -` is allowed when the log is a file; stdin cannot be consumed twice. `--workspace` mechanically verifies Git provenance, publication, document versions, checkbox-only progress and task completion, returning concise diagnostics. The read-only resume command accepts delivery/liveness observations and actual unrecorded output/approval entries; it validates those entries before recommending recording. Results expose scope, phase readiness, counters and evidence gaps. Without evidence it requests reconciliation. These observations do not execute or authorize actions.

The checkpoint helper additionally provides `attempt` (optional `--authorization-event`) and `failure` (`--attempt-id`, `--exit-code`, redacted `--error-summary`) to preserve local Git-metadata evidence. It never commits, pushes, retries or records success receipts. The focused suite uses temporary repositories/local bare remotes. Schema validation checks shape; replay/scenario tests check transitions, approvals, interruptions, recovery and linked resource access. Codex must still honor its native configuration and permissions.
