# Standalone native role exercise

Use only for a named coverage gap from [the scenario catalogue](../scenarios.md#standalone-corpus-and-evidence-gaps). Invoke an actual native role with a recorded supported capability; do not convert its output into a live workflow result. Fixtures and controller metadata stay under the control directory.

Substitution checklist: populate `ROLE`, `ROLE_CONTRACT_PATH`, `ASSURANCE`, `NATIVE_ASSIGNMENT_AND_EVIDENCE`, `FIXTURE_PATH_AND_PERMISSIONS`, `BASELINE_AND_PROVENANCE`, `DOCUMENTS`, `TASK`, `PRIOR_RESULT_AND_DECISIONS`, `EVIDENCE`, and `HUMAN_TEST_AUTHORITY`. Verify coherent fixture versions/history, provenance, and applicable schema/semantic validation before invocation. Record intentional defects and expected observations in private controller metadata, ensuring unrelated metadata errors cannot determine the result. Do not include that answer key in the role's prompt. Use `None` for absent previous decisions; never invent them. Expand all placeholders and send only text below the divider.

---

Use the Orchestrator Flow {{ROLE}} contract at `{{ROLE_CONTRACT_PATH}}` in standalone mode for the supplied fixture. Read the applicable current assurance, role, and evidence contracts and perform the actual bounded work.

Assurance: {{ASSURANCE}}
Accepted native assignment and observable dispatch evidence: {{NATIVE_ASSIGNMENT_AND_EVIDENCE}}
Fixture directory and permitted writable/read-only scope: {{FIXTURE_PATH_AND_PERMISSIONS}}
Actual source/spec baseline and provenance: {{BASELINE_AND_PROVENANCE}}
Current documents and content versions: {{DOCUMENTS}}
Authorized bounded task: {{TASK}}
Previous standalone output and actually communicated decisions: {{PRIOR_RESULT_AND_DECISIONS}}
Supplied evidence and its source context: {{EVIDENCE}}
Human's delegated test authority: {{HUMAN_TEST_AUTHORITY}}

Use standalone context truthfully. Do not invent workflow history, approvals, event IDs, invocations, or Git delivery. Return the role's complete structured standalone JSON result with `context: null`. A saved wrapper or pointer does not replace the native return. This output will not be inserted into a live task log as an orchestrated invocation.

Architect/Reviewer work is read-only. Planner/Coder may edit only the explicitly authorized fixture artifacts under their ownership and task boundaries. Keep live consumers and workflow source unchanged. Missing decisions, unavailable settings, or unverifiable evidence remain reported limitations.

Perform the scope required by the selected assurance. Classify concerns using factual behavior and project consequences. State actual evidence, gaps, and dispositions; the assurance label itself proves no coverage. Preserve actual prior decisions rather than treating facts embedded in a fixture as newly granted user authority.
