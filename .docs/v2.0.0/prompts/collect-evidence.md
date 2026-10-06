# Evidence collection prompt

The master can perform this work directly or delegate it to an authorized read-only evidence agent. Substitute the actual control directory; its manifest contains the resolved repository/chat IDs. This prompt grants no authority to send messages to test chats or repair their work.

---

Collect and assess the evidence for the Orchestrator Flow test run recorded in {{CONTROL_ROOT}}. Read its manifest, delivered decision records, and the kit's overview/scenario expectations. Inspect the actual test chats where available and the corresponding consumer files, task logs, Git history, local bare remotes, and native invocation records. Keep inspection read-only except for writing this run's controller report and evidence summaries under {{CONTROL_ROOT}}.

For each scenario/variant and relevant role, report the accepted settings, stimulus actually delivered, expected behavior, observed actions, evidence references, result (Pass/Fail/Unverified/Not run), and limitations. Requested native settings and observed effective settings must be separate. Do not rely only on the Orchestrator's narrative, a model's self-identification, or a valid wrapper.

For capability cases, connect the Orchestrator's actual recommendation, the master's delegated selection, persisted feature settings, and actual native invocation, including the next affected invocation after an override or resumption. Distinguish accepted recommendations from changed selections, and repository defaults from feature-specific decisions. Report whether the intended role/helper used the accepted settings and whether unrelated assignments remained unchanged. A saved setting without observable native use is incomplete evidence. Do not rank models or reasoning levels by quality, speed, token use, or cost; this report assesses enforcement and persistence.

Give C1-A (recommended capabilities accepted unchanged), C1-B (different capabilities selected before initialization), and the C2 later-override variants separate results. Check persistence and actual native use after resumption for both initial-choice paths. Passing one path does not cover another, and a changed initial selection is not a later override event. If an invalid recommendation had to be corrected, do not count that as unchanged acceptance.

Validate available actual logs and wrappers with the configured helper interpreter. Use recorded previous snapshots for append-only comparisons and real filesystem/Git observations for completed boundaries. Do not invent missing snapshots, repeat failed product operations, rerun a push, or alter runtime logs to make validation succeed. Capture failed checks and skipped checks accurately.

Distinguish complete native workflow runs, standalone role exercises, deterministic fixture tests, and interpretation-only checks. A correct next-action explanation is not proof that a gate was enforced. A complete implementation is not proof that native model assignments or role ownership were honored. A case that never occurred is not a pass.

Assess judgment-dependent classifications against factual behavior, accepted requirements, exposure, and assurance. Do not require identical prose or finding counts. Report unnecessary complete rereads, duplicated output, discarded context, repeated approval questions, and unproductive repair cycles as workflow observations against the applicable contract. Do not turn those observations into model-performance comparisons or guessed savings.

Write {{CONTROL_ROOT}}/report.md with a concise finding-first assessment, a coverage table, supporting evidence links, the source fingerprint/client environment, and concrete remaining gaps. Preserve raw captured evidence separately where available. Do not modify the workflow, repair product code, merge branches, delete test directories, or claim these tests prove every future run correct.
