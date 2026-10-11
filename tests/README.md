# Focused Codex v2 validation

Install `.codex/skills/orchestrator-flow/scripts/requirements.txt` once in the Python environment used for the workflow helpers, then run from the source checkout:

```sh
python -B -m unittest discover -s tests -v
```

These development tests remain in the repository's `tests/` directory. The Codex skill runs through a directory symlink into this checkout and keeps its required runtime scripts and schemas together. Test Git operations run exclusively in temporary repositories with local bare remotes. Runtime utilities never dispatch agents, commit, push or install integrations. The explicit `record-handoff` command writes only the selected authoritative log from one actual native return with internal candidate/readback checks; other validator commands remain read-only. Checkpoint attempt/failure commands retain their local Git-metadata journal writes. Claude Code, GitHub Copilot and Cursor retain their committed native implementations; this suite does not require them to adopt Codex v2 resources.

For native agent execution, use the separate [live test kit](live/README.md). Its master prompt delegates non-application bootstrap setup, twelve feature runs including initial application creation, scripted decisions, feature-specific local chats, and evidence collection in fresh disposable repositories. Maintaining the kit does not launch those runs or authorize cleanup. Live results remain separate from this suite's recorded-history and helper evidence.

| Suite | Evidence |
| --- | --- |
| `test_protocol.py` | Complete histories across assurance/policy combinations; expected resume actions at each delivered happy-path boundary; completed-Coder cumulative-output recovery; versions, material/nonmaterial approvals, references, complete capability overrides preserving assurance, cycle gates, checks and compatibility. |
| `test_recovery_and_reviews.py` | Spec/code repair pairs, lower-level limits, Maximum stalled-loop protection, required classification context in review wrappers, settled findings, helper/role attempt limits, scoped blockers, evidence reuse, feedback within ongoing User/Architect-requested Planner revisions, assurance increases during initial Architect/Reviewer work, and uncertain-attempt schema/default semantics. |
| `test_checkpoint.py` | Commit failure; push/retry failure and interruptions; fresh authorization for uncertain attempts without invented failures; stale/mismatched/consumed authorization rejection; authorization committed before one push; no successful-delivery receipt; failed and interrupted final-checkpoint recovery; Git metadata discovery; delivery helpers operating with unrelated staged and unstaged changes. |
| `test_distribution.py` | Schemas and examples; the actual checkout's real relative VERSION/templates links; setup failures for missing or flattened VERSION resources; all validator commands from a foreign working directory; current-body reader and actual checkbox completion. |
| `test_implementation_phases.py` | Ordinary/final acceptance boundaries; Basic without unused intermediate capability; assurance escalation; phase plans bound to tasks revisions/approvals; repair starts bound to the active review scope; stage repair counts; earlier-phase catch-up and final-assurance treatment of phase findings with whole-feature final repairs. |

The suite also checks same-version progress and preserved approval/provenance, actual Git content comparisons, no-artifact Planner returns, typed coordination without completion, stdin candidate validation, exact bounded-body reconstruction, artifact-only delivery after a delivered log, metadata pagination, and evidence sufficiency after lowering/restoring assurance. Examples with orchestration references illustrate the declared interfaces; validate full relationships in the complete-history fixtures and scenario tests. Example commit hashes are illustrative. They are not consumer feature logs or claims of real published artifacts.

Continuation and recovery coverage checks prospective settings at approved-document boundaries, helper-only overrides, unchanged assignment/approval/attempt accounting, in-flight review assurance and bounded genuine failure recovery. Recording tests feed one actual wrapper, preserve literal Unicode through stdin/PowerShell, derive correct events and causal requestors, and detect concurrent modification or failed readback. Small correction tests keep the same assignment and published artifacts. Git tests validate logical invocation/phase provenance and allow corrected returns to reuse their earlier applicable checkpoints. No test claims to prove an agent captured the actual native response or reported every failure.

The kit's [deterministic phase inventory](live/scenarios.md#deterministic-phase-coverage) maps proposal requirements to specific tests and records missing behavioral coverage as corrections-work dependencies. A whole-suite pass does not establish absent reasoning-mapping or Maximum intermediate-limit cases. Native phased execution remains Deferred/Not run in this kit revision. Record the exact tested runtime source and results separately from the source used for the kit or installed skill.

The checkout's VERSION and templates link checks must pass. Resource tests use those existing links and do not need permission to create additional symlinks. Broken or flattened links remain setup errors; follow the repository's clone-and-symlink guidance to repair them.

## Codex contract walkthrough

Review these instruction-level behaviors alongside the executable histories. The suite does not launch a native Codex client. Native delegation/session continuity, repository-default loading, and an agent's classification judgment require separate observation; the tests validate recorded artifacts and helper behavior. Checkpoint fixtures select files and commit/push explicitly, so they do not prove an Orchestrator selects the correct files or Git commands.

| Situation | Expected behavior |
| --- | --- |
| Start and delegate | Load the full applicable role contract and use actual subagents. |
| Capability unavailable | Pause affected work for accepted native configuration or wait; no virtual role or model fallback. |
| Requirements returned | Record incremental output; checkpoint; obtain approval of the exact version before design. |
| Planner blocked before any artifact | Permit a genuine incremental questions-only return with null checkpoint; no empty commit, artifact approval or review readiness. Ordinary clarification stays draft-first. |
| Natural coding group | Coder publishes artifacts and concise progress/check evidence, continues the assignment, and returns no mandatory interim wrapper or acknowledgement. |
| Required handoff | Pass the actual JSON once to record-handoff; it derives metadata/state and validates/records unchanged values internally. Recover clipped native output before attributing a producer failure. |
| Accepted capability continuation | Apply current settings to subsequent work at a coherent boundary, preserving assignment, approvals, attempts and cumulative baseline. Helper-only changes affect subsequent helpers without restarting the lead. |
| Reporting correction or failure | Small corrections use the same assignment without failure events, empty commits or retests. Genuine unusable output/execution failure uses bounded recovery from actual invocation evidence. Recording errors are not producer failures. |
| Truncated spec read | Retry the chunk's starting character offset with a smaller bound; claim completeness only after the full current body is retrieved. |
| Final tasks draft | Record consolidated Planner context before tasks approval; unchanged approval enables Architect without another return. Changed artifacts/decisions follow the applicable approval path. |
| Nit-only review | Accept by default at every assurance and derive known issues without a repair/disposition bounce; an explicit user repair decision uses the existing repair path and retains its authority through producer responses. Missing required work/checks still block. |
| Feedback during a Planner revision | Apply feedback in the same drafting cycle; preserve trigger/requestor and continue native context where supported. |
| Basic/Standard repair | Apply actual project consequences and impact scope; check source/assumption changes before evidence reuse. |
| Maximum repair | Perform comprehensive current-body/source/traceability review and active revalidation; preserve useful context. |
| Assurance increased during review | Record the actual invocation basis, then require catch-up review before dependent work, including after the first review. |
| Maximum → Standard → Maximum | Reuse sufficient applicable accepted evidence; changed work/assumptions receive bounded applicability assessment or necessary review. |
| Phased feature | Basic skips intermediate review; Standard/Maximum use recorded lower stage settings and separate allowances; last Coder integrates and repairs the full feature. |
| Coder helpers | Exploration/test execution only, accepted capability, stable work during tests, concise actual results and failure category; Coder owns all intentional edits. |
| Resume with artifact checkpoints | Inspect Git metadata and native evidence in bounded batches; recover the owner before replacing it. Coder reconstructs its original cumulative baseline, including reversals and historical versus new checks. |
| Interruption or failed push | Recover output/liveness and reconcile Git first; a failed push globally pauses workflow work. |
| Push outcome remains uncertain | Preserve attempt identity; commit a fresh one-push user authorization with uncertain context before retry. No invented failure or replenished allowance. |
| Final acceptance | Obtain explicit feature acceptance, deliver the completion checkpoint, then provide the total squash message. No success receipt or agent merge. |

A live client/account must still expose the configured native controls and permissions. Validators check records and correspondence, not whether a model's factual research is true or a provider honored an unavailable setting. Leads remain responsible for verifying those claims.
