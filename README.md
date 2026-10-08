# Orchestrator Flow

Orchestrator Flow takes a proposal or bug report through **Planner → Architect → Coder → Reviewer**, coordinated by **Orchestrator**. The current **2.0.0 implementation is Codex only**, identified by the canonical [VERSION](VERSION). Claude Code, GitHub Copilot, and Cursor retain their committed native implementations; their v2 updates are deferred.

This repository is the installation source. Maintaining its artifacts does not run the consumer workflow here. See [AGENTS.md](AGENTS.md) for maintenance boundaries and validation. The separate legacy BugAgents, CoordinatorVersion and TaskSync implementations are outside this Codex v2 work.

## Integrations and ownership

| Platform | Entry point and artifacts | Current scope |
| --- | --- | --- |
| Codex | [Orchestrator Flow skill](.codex/skills/orchestrator-flow/SKILL.md) | v2; actual native subagents, with no virtual/in-place role fallback |
| Claude Code | `/orchestrate`, [agents](.claude/agents), [command](.claude/commands/orchestrate.md) | Existing native instructions; v2 deferred |
| GitHub Copilot | Select **Orchestrator** in the custom-agent selector; [agents](.github/agents), [prompts](.github/prompts/prompts.md) | Existing custom agents; v2 deferred |
| Cursor | `/cursor-orchestrate`, [rule](.cursor/rules/Orchestrator.mdc), [agents](.cursor/agents), [command](.cursor/commands/cursor-orchestrate.md) | Existing rule, command and agents; v2 deferred |

In Codex v2, Orchestrator owns user interaction, initialization, configuration, `task_log.json`, `known-issues.md`, log checkpoints and recovery coordination. Planner publishes requirements/design/tasks/research artifacts; Coder publishes its implementation/tests/docs and task-completion progress. Architect and Reviewer assess work read-only. Coder's helpers explore and execute tests without intentional edits or publication. Git ownership is serialized through the active producer and coherent yields; no agent performs the final squash merge.

The Codex contracts are [workflow-protocol.md](.codex/skills/orchestrator-flow/references/workflow-protocol.md), [assurance.md](.codex/skills/orchestrator-flow/references/assurance.md), the five role references and the [schemas/examples](.codex/skills/orchestrator-flow/references). They live within the skill alongside its required runtime scripts. Other platforms retain their own substantive instructions and do not load this Codex implementation. The v2 runtime behavior and Codex setup instructions below apply to Codex; project coding guidance and reusable input templates apply to all four platforms.

| Source location | Purpose |
| --- | --- |
| [.codex/skills/orchestrator-flow/](.codex/skills/orchestrator-flow) | Codex instructions, UI metadata, role references, schemas, examples, runtime scripts, dependency declaration, and version/template symlinks |
| [Directives/codingAgentDirectives.md](Directives/codingAgentDirectives.md) | Reusable coding guidance for projects using any of the four platforms; copy and customize per project, separately from workflow installations |
| [tests/](tests) | Repository development tests and fixtures, outside all platform-specific integration directories |
| [.docs/v2.0.0/](.docs/v2.0.0/) | Workflow and test-kit proposals, corrections, and release validation summaries |
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

## Project coding guidance

[Directives/codingAgentDirectives.md](Directives/codingAgentDirectives.md) is an optional starting point for a project's coding conventions on **all four platforms: Codex, Claude Code, GitHub Copilot, and Cursor**. Copy it to a suitable location in the consuming repository, keep the relevant language sections, and customize its frameworks, tooling and conventions. Identify that project-owned file in the project's native instruction file or README so the chosen platform's agents can find it.

Maintain the project's copy independently of the workflow installation. Keep the reusable source in this repository's `Directives/` directory, separate from platform-specific workflow artifacts. Workflow assurance, approvals, task ownership and recovery belong in each platform's workflow contracts rather than the coding-directives document.

Codex v2 follows this separation. The deferred Claude, Copilot, and Cursor implementations still have their existing Directives references; those remain unchanged in this phase and will need to align with the same project-owned guidance policy when updated.

## Capability and feature configuration

During first setup, establish repository defaults with the user in committed consumer-root `.orchestrator-flow.json`. Do not add these defaults to `AGENTS.md`. Model and effort are configured separately from assurance for Planner, Architect, Coder, Reviewer and helpers.

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

The configuration schema retains the platform identifiers `codex`, `claude-code`, `github-copilot`, and `cursor`; this does not imply v2 support in the deferred integrations. For this Codex setup, configure the `codex` assignments for all five roles. Check available model/reasoning controls and native agent settings, present per-role recommendations, and record the user's accepted values. Configure a matching native agent or use an invocation override where supported; a role prompt alone does not enforce model/effort.

### Codex native assignments

For clients supporting custom-agent TOML files, create one file per delegated role under the consumer's `.codex/agents/` or `~/.codex/agents/`. For example, `.codex/agents/flow-planner.toml`:

```toml
name = "flow_planner"
description = "Planner for explicitly requested Orchestrator Flow work."
model = "YOUR_AVAILABLE_MODEL"
model_reasoning_effort = "high"
developer_instructions = """
Follow the complete Planner, workflow-protocol, assurance and engineering
contracts supplied by Orchestrator. Return bounded structured outputs;
Orchestrator owns user gates and the task log; Planner publishes its artifacts.
"""
```

Create corresponding Architect, Coder, Reviewer and helper definitions with the accepted assignments. A custom file's model/effort can take precedence over spawn settings; keep it consistent with the feature snapshot, including overrides. Where the native spawn interface directly exposes model/effort, use those controls without a conflicting custom profile. Confirm the effective assignment before work. See [official Codex subagent configuration](https://learn.chatgpt.com/docs/agent-configuration/subagents).

### Feature acceptance and overrides

The Codex skill uses accepted feature assignments rather than fixed model choices. Explicit `platform_default` values or `not_supported` effort require disclosure and user acceptance of the actual native limitation. Record concrete effective values when exposed. If an explicit assignment cannot be honored, or a lead/helper reaches a model limit, pause affected work and ask whether to choose another assignment or wait. Never silently fall back or change assurance with a model substitution.

At the beginning of each feature, Orchestrator reads defaults, assesses the proposal, presents recommendations for acceptance/override, and stores the **complete resolved feature configuration** in the task log before Planner runs. On resume that snapshot governs. Default changes affect future features; applying them to this feature requires a recorded `user-override`. Feature acceptance does not silently change repository defaults.

The built-in `review_disposition_policy` is `spec_user_code_auto`: user disposition of Architect findings before Planner revision, routine in-scope Reviewer-driven repairs allowed. Explicit feature alternatives are `all_user` and `within_scope_auto`. The effective policy is top-level in the task log, not a repository-default field. All alternatives preserve material artifact approvals, product decisions, must-fix exceptions, loop limits and operational authorization.

## Assurance and review

| | Basic | Standard | Maximum |
| --- | --- | --- | --- |
| Initial review | Complete relevant spec and implementation | Complete relevant spec and implementation | Complete exhaustive review |
| Follow-up | Focused, expanding when consequences/evidence warrant | Focused, affected or full according to impact | Comprehensive on each required pass |
| Remediation | Practical benefit, likelihood, consequences and total workflow cost | Stronger presumption toward robustness/repair | Existing rigorous repair and justified-deferral obligations |
| Further repair gate | Before a second repair-and-re-review cycle | Before a third | Existing rigorous loops and stalled-loop safeguards |

Classification itself reflects the agreed acceptance standard. Findings explain factual behavior, conditions and actual project consequences, distinguishing demonstrated defects, hardening opportunities and preferences. A personal project's optional improvement need not receive a consequential deployment's completion priority. Facts stay accurate; explicit must-fix exceptions require user disposition. A nonempty known-issues document does not automatically prevent acceptance.

Basic/Standard check source/assumption changes, reuse valid completed evidence, and repeat affected or incomplete work. Maximum actively revalidates decision-critical evidence even when sources appear unchanged. Helpers separate observations, inferences, gaps and uncertainty with verifiable references. Leads own synthesis. Preserve ongoing role context across checkpoints where supported; full review obligations concern the work performed, not starting a new agent.

If assurance increases while a review is running, record its output against the settings it actually used. Compare that result with the current requirement; any gap requires catch-up review before dependent coding or final completion, including when this was the first review.

See [the full assurance rubric and Maximum checklists](.codex/skills/orchestrator-flow/references/assurance.md) for exact review/remediation and task-category rules.

## Artifacts and user gates

Consumer artifacts live under `.docs/specs/{feature}/`. Requirements, design and tasks are mandatory, with separate approvals in dependency order. A material upstream decision must be approved before dependent revisions proceed. Unaffected artifacts need no artificial changes or renewed approval. Editorial corrections, faithful recording and task-progress accounting preserve a real approval basis with rationale.

Feedback received while Planner is drafting stays in the current creation or revision cycle, even when an earlier spec handoff has already completed. Record the clarification and subsequent draft updates, preserve the existing Planner context where supported, and continue the approval path. A new revision starts when feedback arrives outside active drafting; clarifications within a cycle do not consume extra repair cycles.

Required documents have independent integer content versions from the first draft and a final Revision History. Every completed content update increments its document version, including separate updates in one session. Pure approvals do not change documents. Spec documents contain no duplicated workflow/Git metadata. Read current bodies with the streaming body reader; retrieve history explicitly when needed.

Task-checkbox progress preserves the tasks version, Revision History, producing Planner reference and approval. Coder changes only actual numbered completion marks; Planner owns wording, numbering, dependencies and editorial revisions. Bounded reader chunks use normalized character offsets, so truncated output can be reread without losing the end of a line. Initial review still covers every current spec body at all assurance levels.

`task_log.json` holds append-only events, effective configuration, requests, actual outputs, approvals, findings/dispositions and recovery authority. Planner returns drafts and a consolidated handoff. Coder normally returns one cumulative wrapper per completed assignment/repair; ordinary artifact checkpoints need no wrapper or acknowledgement. Typed coordination reports preserve blockers without claiming completion. Required returns are complete actual JSON, never file pointers. Normal operation creates no scratch role artifacts; validate directly in memory or through stdin. Optional research has no content version or separate approval gate. Orchestrator maintains current deferred findings/accepted limitations in `known-issues.md`; resolved history remains in the log and review notes/evidence.

Exceptionally large tasks plans may propose stable implementation phases through the existing tasks approval. Basic skips intermediate reviews; Standard uses Basic, and Maximum uses Standard, with one/two repair cycles per intermediate stage. Required intermediate capability retains the full Reviewer model with effort `max → high`, `xhigh → medium`, or `high → low`, recorded in feature configuration. Basic needs no unused assignment; unmapped/unsupported settings require explicit direction. Final review always uses full feature settings and its separate allowance. The last Coder integrates and reports the entire feature and owns all final repairs. Natural Markdown checkpoint groups alone do not justify phases.

Assurance changes reuse all applicable accepted evidence: unchanged Maximum evidence remains sufficient after lowering and restoring assurance. Real content/source/assumption gaps require bounded assessment or review, scoped independently to specification, phase or final implementation. Applicability assessments grant neither higher assurance nor new acceptance; required Maximum review work remains comprehensive.

All levels preserve Scaffolding boundaries, Red/Green separation, production-only Refactor, concrete Documentation, Planner-defined final Test-Maintenance and repair-free Verification. Coder may mark task progress, not redesign the plan. Architect approval is distinct from user authorization to begin coding. Reviewer approval is distinct from final feature acceptance.

## Checkpoints, interruptions and final merging

Initialize the explicit user branch or otherwise the feature name, validating it with Git and recording integration target, remote and baseline. No automatic prefix or product version; conflicts need direction. Use the existing checkout unless a worktree was explicitly requested. Planner checkpoints substantive artifacts before handoff. Coder checkpoints approved natural task groups, meaningful partial work and completion. Orchestrator separately checkpoints every authoritative log update, approval, decision and review return. Deliberately Red work is described accurately. Checkpoints grant neither approval nor merge readiness.

Every checkpoint has feature/kind/role trailers; producer artifacts also identify invocation and applicable phase. Only log commits carry the log path and contiguous event range. Wrappers identify already-published artifact commits; no event stores its containing log checkpoint's own hash. No ordinary checkpoint or success-receipt event is added. Resume reconciles metadata and names/statuses, paginating recent commits as needed, with remote delivery and actual native/user evidence. Orchestrator delegates content inspection and recovers existing producers before replacement. Coder reconstructs cumulative work against its original baseline, distinguishing recovered verification from newly run checks.

On a failed push, preserve the local commit and failure evidence, globally pause work, and obtain direction. Before an authorized retry, commit the failure context and retry-authorization update. One push then delivers the outstanding checkpoint plus this update. Git proves successful delivery; do not create a success receipt or another commit/push. A failed retry is immediately preserved locally and requires new direction. The final checkpoint uses the same sequence, leaving no pending success receipt or extra approval.

If an attempt was recorded but its result is unknown after interruption, inspect Git first. When delivery cannot be established, a fresh explicit authorization may permit one more push. Record the original attempt and the actual observation in `uncertain_attempts`, commit the authorization, then record the new attempt before dispatch. Do not invent a failure or reuse a consumed allowance. `checkpoint_state.py inspect` supplies the uncertain-attempt context; it never authorizes or performs a push.

Other blockers pause only affected operations/dependencies while independent approved work can continue. Model unavailability requires user direction; no automatic fallback. Ordinary role failures preserve context and completed evidence, with three total attempts before further direction. Bound external-operation retries to their actual authorization.

After Reviewer acceptance, present delivery, verification and known issues for **explicit user feature acceptance**. Record `implementation_complete`, complete its checkpoint delivery, and then provide one conventional squash-commit message covering the total final change against the baseline. A commit-message request does not itself authorize completion. The user manually merges into `main` or the explicitly selected integration branch. No agent performs that merge or deployment.

## Proposal and bug-report templates

These reusable inputs apply to all four platforms.

- [Proposal template](templates/proposal-template.md): feature/improvement intent, rationale, settled decisions and important constraints.
- [Bug-report template](templates/bugreport-template.md): observed failure, reproduction, expected correction and relevant preservation boundaries without requiring a speculative diagnosis.

Each is self-contained with visible Markdown authoring guidance, section expectations and optional heading hierarchy. No earlier proposal/report is needed as a style reference. Copy the appropriate template into a completed document in the consuming repository, following that repository's artifact-location conventions; do not overwrite the reusable template.

Remove the template-version line, authoring guidance, examples, instructional text and placeholders. Preserve the applicable completed-document outline and scale detail to the work. Invoke `$orchestrator-flow` with the completed document's path in Codex. The deferred platforms retain their existing entry points listed above.

Each template currently has independent integer **template version 2**. These integers track authoring contracts, independently of each other, workflow semantic versions, product releases and spec content versions. The Codex skill accesses the canonical files through its real `templates/` symlink.

## Compatibility and validation

Version 2.0.0 applies to new work. Pre-2.0/missing-version logs are unsupported; stop and obtain direction rather than migrate or repair automatically. Completed historical features remain untouched. Patch/minor releases preserve older supported logs' execution and approval meaning, with actual documented defaults for compatible additions. Exact-version-only checks must not reject an older supported log under a compatible newer reader. Older readers need not understand newer logs; major changes require an explicit compatibility boundary.

Run these commands from the source checkout. Runtime commands can also use the linked skill's `scripts/` path; the unittest and Git checks are repository development checks:

```sh
python .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py task-log <TASK_LOG> --workspace <CONSUMER_ROOT>
python .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py repository-config <REPOSITORY_CONFIG>
python .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py spec-change-wrapper <WRAPPER>
python .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py spec-review-wrapper <WRAPPER>
python .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py change-wrapper <WRAPPER>
python .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py review-wrapper <WRAPPER>
python .codex/skills/orchestrator-flow/scripts/validate_orchestrator_artifacts.py resume-action <TASK_LOG> --observations <OBSERVATIONS_JSON>
python .codex/skills/orchestrator-flow/scripts/read_spec_body.py <SPEC_DOCUMENT> --offset 0 --max-chars 8000
python .codex/skills/orchestrator-flow/scripts/checkpoint_state.py inspect <TASK_LOG> --repo <CONSUMER_ROOT>
python .codex/skills/orchestrator-flow/scripts/checkpoint_state.py recent <TASK_LOG> --repo <CONSUMER_ROOT> --limit 20
python -B -m unittest discover -s tests -v
git diff --check
```

Primary validator input `-` reads actual JSON on stdin. For candidate updates, `task-log - --previous <AUTHORITATIVE_LOG>` verifies append-only history without creating snapshots. `--observations -` is allowed when the log is a file; stdin cannot be consumed twice. `--workspace` mechanically verifies Git provenance, publication, document versions, checkbox-only progress and task completion, returning concise diagnostics. The read-only resume command accepts delivery/liveness observations and actual unrecorded output/approval entries; it validates those entries before recommending recording. Results expose scope, phase readiness, counters and evidence gaps. Without evidence it requests reconciliation. These observations do not execute or authorize actions.

The checkpoint helper additionally provides `attempt` (optional `--authorization-event`) and `failure` (`--attempt-id`, `--exit-code`, redacted `--error-summary`) to preserve local Git-metadata evidence. It never commits, pushes, retries or records success receipts. The focused suite uses temporary repositories/local bare remotes. Schema validation checks shape; replay/scenario tests check transitions, approvals, interruptions, recovery and linked resource access. Codex must still honor its native configuration and permissions.
