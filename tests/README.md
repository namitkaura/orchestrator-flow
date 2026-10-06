# Focused Codex v2 validation

Install `.codex/skills/orchestrator-flow/scripts/requirements.txt` once in the Python environment used for the workflow helpers, then run from the source checkout:

```sh
python -B -m unittest discover -s tests -v
```

These development tests remain in the repository's `tests/` directory. The Codex skill runs through a directory symlink into this checkout and keeps its required runtime scripts and schemas together. Test Git operations run exclusively in temporary repositories with local bare remotes. The runtime utilities do not dispatch agents, commit, push, install integrations or alter consumer projects. Claude Code, GitHub Copilot and Cursor retain their committed native implementations; this suite does not require them to adopt Codex v2 resources.

For native agent execution, use the separate [v2.0.0 local test kit](../.docs/v2.0.0/README.md). Its master prompt delegates setup, scripted decisions, test-chat coordination, and evidence collection within fresh disposable repositories. Those live results are separate from this suite's recorded-history and helper evidence.

| Suite | Evidence |
| --- | --- |
| `test_protocol.py` | Complete histories across assurance/policy combinations; expected resume actions at each delivered happy-path boundary; versions, material/nonmaterial approvals, references, overrides, cycle gates, checks and compatibility. |
| `test_recovery_and_reviews.py` | Spec/code repair pairs, lower-level limits, Maximum stalled-loop protection, required classification context in review wrappers, settled findings, helper/role attempt limits, scoped blockers, evidence reuse, feedback within ongoing User/Architect-requested Planner revisions, assurance increases during initial Architect/Reviewer work, and uncertain-attempt schema/default semantics. |
| `test_checkpoint.py` | Commit failure; push/retry failure and interruptions; fresh authorization for uncertain attempts without invented failures; stale/mismatched/consumed authorization rejection; authorization committed before one push; no successful-delivery receipt; failed and interrupted final-checkpoint recovery; Git metadata discovery; delivery helpers operating with unrelated staged and unstaged changes. |
| `test_distribution.py` | Schemas and examples; runtime/test separation; real relative VERSION/templates links; setup failures for missing, broken or flattened VERSION links; all validator commands from a foreign working directory; resource access through a directory symlink; temporary Git push/clone preserving mode `120000`; current-body reader and actual checkbox completion. |
| `test_platform_contracts.py` | A recorded Codex initialization → interrupted drafting → coding authorization → recovered output → accepted completion walkthrough, and explicit capability overrides preserving assurance. |

The checkout's VERSION and templates link checks must pass. Tests that create additional native symlinks explicitly report a skip if the process lacks permission; report those skips with validation results. They do not authorize text-pointer fallbacks. Exercise the skipped checks from an environment with symlink privileges before claiming that the Git round trip and temporary linked-installation checks passed.

## Codex contract walkthrough

Review these instruction-level behaviors alongside the executable histories. The suite does not launch a native Codex client. Native delegation/session continuity, repository-default loading, and an agent's classification judgment require separate observation; the tests validate recorded artifacts and helper behavior. Checkpoint fixtures select files and commit/push explicitly, so they do not prove an Orchestrator selects the correct files or Git commands.

| Situation | Expected behavior |
| --- | --- |
| Start and delegate | Load the full applicable role contract and use actual subagents. |
| Capability unavailable | Pause affected work for accepted native configuration or wait; no virtual role or model fallback. |
| Requirements returned | Record incremental output; checkpoint; obtain approval of the exact version before design. |
| Feedback during a Planner revision | Apply feedback in the same drafting cycle; preserve trigger/requestor and continue native context where supported. |
| Basic/Standard repair | Apply actual project consequences and impact scope; check source/assumption changes before evidence reuse. |
| Maximum repair | Perform comprehensive current-body/source/traceability review and active revalidation; preserve useful context. |
| Assurance increased during review | Record the actual invocation basis, then require catch-up review before dependent work, including after the first review. |
| Interruption or failed push | Recover output/liveness and reconcile Git first; a failed push globally pauses workflow work. |
| Push outcome remains uncertain | Preserve attempt identity; commit a fresh one-push user authorization with uncertain context before retry. No invented failure or replenished allowance. |
| Final acceptance | Obtain explicit feature acceptance, deliver the completion checkpoint, then provide the total squash message. No success receipt or agent merge. |

A live client/account must still expose the configured native controls and permissions. Validators check records and correspondence, not whether a model's factual research is true or a provider honored an unavailable setting. Leads remain responsible for verifying those claims.
