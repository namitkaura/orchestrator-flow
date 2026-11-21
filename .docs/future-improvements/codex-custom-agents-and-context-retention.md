# Future improvement: Codex role instructions and long-lived subagent context

**Status:** Research candidate; deferred beyond v2.2.0. Not an approved change or authorization to modify agent configuration, workflow behaviour, or the current six-area proposal.

## Motivation

Orchestrator Flow reuses the same native Planner (and other role) subagent across document approvals and revisions to retain useful decisions and avoid costly reconstruction. During the music-analyzer F01 feature, the Planner produced a structurally complete but under-specified Tasks v1, then improved the contracts in Tasks v2 but placed substantial task-specific instructions in detached, unnumbered sections. These are demonstrated planning-quality problems, **not proof of a context or compaction defect**.

A possible contributing factor is the accumulation of superseded drafts, feedback and tool results in a long-lived role context. The Orchestrator supplies the role contract and references when starting a subagent, but the contents of role Markdown subsequently read as files may be summarized or lose salience following context compaction. Whether this actually happened in F01, and whether the contract is refreshed on later continuations, remains unverified.

## Why Codex custom agents may help

Codex supports custom agents defined by `.codex/agents/*.toml` or `~/.codex/agents/*.toml`, each with `developer_instructions`. Unlike ordinary conversation text or previously read tool output, these are native developer-level instructions defining the role. Codex's current implementation includes tests for developer-instruction retention across compaction. This suggests that **short, invariant role obligations** embedded directly in custom-agent developer instructions may be more resistant to instruction drift.

For Planner, examples would include ownership of consequential design decisions, implementation-ready tasks, task-specific instructions inside numbered tasks, and escalation of unresolved requirements. Merely putting “read planner.md” in the custom agent would **not** guarantee that the full external file content remains verbatim available after compaction.

Custom agents are still real subagents and can still accumulate distracting history. Native agent configuration is therefore a possible answer to **instruction retention**, not necessarily to **context pollution**. Also verify which Codex clients and spawn interfaces actually support invoking named custom agents. Custom-agent model/effort settings can override spawn settings and must not silently defeat Orchestrator Flow's accepted per-feature capability choices.

## Later investigation (no implementation now)

1. Inspect a representative long Codex feature run for compaction, role-contract loading/reloading, and the timing of quality regressions; distinguish observed facts from conjecture.
2. Verify on the actual Codex host that named custom-agent `developer_instructions` remain effective across continuation and compaction, including how current skill/role references are reloaded.
3. Compare the same bounded planning/revision scenario with (a) existing reused native subagent, (b) custom Planner with concise invariant developer instructions, and (c) fresh Planner handed the approved artifacts and complete relevant prior wrappers. Keep model/effort and acceptance criteria comparable.
4. Assess quality, cost, continuity, and configuration friction. Consider selective context renewal or a light instruction refresh before requiring custom agents or redesigning the lifecycle.

**Decision:** Park this in `.docs/future-improvements/`. The six selected v2.2.0 planning areas already address the concrete specification-readiness and task-ownership failures. Do not absorb this hypothesis into v2.2.0 or create a seventh workstream without a future explicit decision.

## References

- [Orchestrator Flow v2.1.1 Codex orchestration contract](../../.codex/skills/orchestrator-flow/references/orchestrator.md) — reuse, role contract injection, continuity.
- [Orchestrator Flow v2.1.1 Planner contract](../../.codex/skills/orchestrator-flow/references/planner.md) — existing planning and handoff expectations.
- [Codex subagent/custom-agent configuration](https://learn.chatgpt.com/docs/agent-configuration/subagents) — TOML `developer_instructions` and model/effort precedence.
- [Codex developer-instruction compaction tests](https://github.com/openai/codex/blob/main/codex-rs/app-server/tests/suite/v2/multi_agent_v2_developer_instructions.rs) — evidence to validate against the actual host/runtime.
