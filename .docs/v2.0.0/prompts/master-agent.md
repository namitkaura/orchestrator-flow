# Master agent prompt

Submit this prompt to an agent with the parent test folder filled in. The agent resolves the kit/source paths from this file and prepares all other prompts. For a fresh run it always allocates the next `testrun-N` container. To resume instead, explicitly provide the existing run container and request resumption.

---

Act as the master agent for the Orchestrator Flow v2.0.0 local test kit containing this prompt. Read `../test-runbook.md` and `../test-scenarios.md`, resolving paths relative to this file. Perform setup, drive the test runs, and collect the evidence into a final report.

Parent test folder: `<absolute test folder>`

For a fresh run, create the next numbered `testrun-N` container under that parent: `testrun-1`, then `testrun-2`, etc. Advance beyond the largest existing number, including incomplete runs, without reusing gaps or existing paths. Inside it use working folders `basic`, `standard`, and `maximum`, bare remotes `basic-repo`, `standard-repo`, and `maximum-repo`, and a private `.orchestrator-test` directory containing all controller records, prompts, fixtures, evidence, and the report. Leave earlier runs intact. Record and show the actual selected paths.

Number only the immediate runs in the parent I supplied. A different empty parent starts at `testrun-1` regardless of runs elsewhere; do not use a global counter.

I authorize you to create the three ordinary local test repositories and their bare remotes, build and verify the small baseline once, seed all three from that commit, and perform the bounded setup Git operations described in the runbook. Keep application code, setup artifacts, and evidence within this run's allocated paths. Do not change the workflow distribution, my installed skills, personal settings, or unrelated projects. Do not create worktrees, hosted repositories, PRs, force-pushes, or merges.

I explicitly authorize you to create local Codex test chats for these repositories, to create a replacement local chat when a scripted fresh-context test requires it, and to send those test chats the initial prompts and follow-up decisions described in this kit. Use the app's native project/chat tools. First prepare the repositories and then look up their saved project IDs. If I need to add the three prepared directories as Codex projects, give me one concise request listing them; continue independent preparation in the meantime. Do not use an unrelated project as a substitute.

Create every top-level test Orchestrator chat, including replacements for fresh-context tests, using GPT-6.1 Sol with High reasoning. Select `model: "gpt-6.1-sol"` and `thinking: "high"` through the native chat-creation controls; preserve those settings on follow-up messages. This is my explicit choice for the test Orchestrators. If it cannot be honored, report the limitation and ask for direction before starting the affected chat. The role/helper capabilities remain separate test choices.

I authorize the bounded setup and evidence subagents needed by this runbook. Each test chat should run the real Orchestrator Flow skill with native Planner, Architect, Coder, Reviewer, and helper delegation. Do not simulate those roles or treat the master's work as their output. Discover actual supported role model/effort controls and preserve an explicit capability choice I supply. Let each Orchestrator recommend repository defaults and feature settings through its normal gates; then decide as my delegate. Exercise both initial paths: accept valid recommended capabilities unchanged in U-B, and select at least one different supported role assignment in U-S. Record those cases separately from later overrides of already accepted settings. Keep intended test selections out of initial runner prompts unless they are actual human-supplied constraints. Use a small mix of supported capabilities across the cases; do not force identical maps across assurance runs.

The capability tests must establish that we can set model/effort assignments, that the intended agents actually use them, and that they persist through later invocations, overrides, and resumption. Use a small mix of supported assignments to expose inheritance or fallback errors. Do not benchmark models, rank their quality or speed, or add runs to find the best capability combination. Assess assurance behavior against its specified contract.

You may make the scripted workflow decisions on my behalf within this disposable test scope: configuration acceptance/overrides, document approvals, coding authorization, in-scope finding dispositions, the bounded continuation/retry decisions, and final feature acceptance. Apply the runbook's decision table. These are delegated decisions, not automatic approval of every output. Cite actual artifacts, versions, findings, or attempts and identify your delegated authority in the delivered message. Do not invent a human conversation, waive demonstrated must-fix defects or required failures, or extend the limits. Refer unexpected product scope, policy, cost, or exception decisions to me.

Operate one lane at a time by default. Reuse each test chat for its next feature; use the preceding accepted feature branch as the explicit baseline when the runbook calls for it. No agent merges into `main`. Preserve native context where supported, and check liveness before replacing an interrupted writer.

Observe real progress and gates. Read the test chats to collect outputs; they do not need to message you back. Use the separate prompt files for initial runs, decisions/stimuli, resumption, standalone exercises, and evidence collection. Expand all placeholders with observed values before sending. Keep the private scenario expectations outside the runner context.

Stop an affected scenario when it reaches an unauthorized boundary, and continue only independent permitted work. Record failures rather than starting an open-ended effort to perfect the workflow. If a native capability or rare failure condition cannot be verified, mark that coverage unverified instead of inventing evidence.

Finish with a linked report identifying actual passes, failures, unverified/not-run cases, native-setting evidence, relevant logs/diffs/commands, and remaining limitations. Leave the repositories and evidence available for inspection. Merely creating files or passing validators is not proof that the native workflow obeyed them.
