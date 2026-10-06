# Resume a real workflow run

The master fills this prompt after checking the prior chat and subagent liveness. Use it in the existing chat or a specifically authorized replacement local chat for the same repository. Create replacements with GPT-6.1 Sol High through the native controls specified in the runbook; preserve the same top-level setting when messaging an existing chat. The feature's role/helper assignments remain independently recorded. Do not create a second active writer.

---

Use `$orchestrator-flow` to resume feature {{FEATURE_ID}} in {{WORKING_REPO}}, using its actual task log at {{TASK_LOG_PATH}}. The installed skill and helper interpreter are {{SKILL_PATH}} and {{PYTHON_PATH}}.

This continues a disposable test under the human's recorded authorization {{HUMAN_TEST_AUTHORITY}}. The master test controller remains the authorized delegate for the same bounded decisions. No new product approval, retry, cycle allowance, or final acceptance is granted merely by resuming.

Previous runner: {{PRIOR_THREAD_AND_HOST}}
Observed native role liveness/output: {{ACTUAL_LIVENESS_EVIDENCE}}
Last observed checkpoint/delivery: {{ACTUAL_CHECKPOINT_EVIDENCE}}
Current controller context relevant to the next action: {{BOUNDED_CONTEXT}}

Validate supported workflow version and actual artifacts, replay the log, and reconcile Git and invocation outcomes before dependent work. Preserve the feature's recorded configuration even if repository defaults changed. Recover completed output and existing native handles where available before dispatching another writer. An unavailable handle is a limitation to record, not evidence that unfinished work completed.

Continue from the correct existing state and pending gate. Preserve approvals, findings, dispositions, version history, counters, and capability overrides. Do not recreate planning, automatically repeat settled lower-assurance reviews, fabricate missing records, or treat an unknown push outcome as an unused retry allowance. Report the actual next action or required decision in this chat.
