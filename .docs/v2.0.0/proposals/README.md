# Test project inputs

These are completed proposal documents following the repository's [proposal template](../../../templates/proposal-template.md). The setup agent copies them to `.docs/inputs/` in the consumer baseline. They contain product scope, not test answer keys or approvals.

| Input | Use |
| --- | --- |
| [00-line-list-project.md](00-line-list-project.md) | Build and verify the sample baseline once during setup. No workflow task log for this setup step. |
| [01-unique-lines.md](01-unique-lines.md) | First real Orchestrator Flow feature in all three lanes, starting from the identical baseline. |
| [02-output-limit.md](02-output-limit.md) | Basic follow-up, starting from its accepted unique-lines branch. A scripted later user decision extends its initial positive-only limit to include zero. |
| [03-ignore-case.md](03-ignore-case.md) | Standard follow-up, starting from its accepted unique-lines branch. |

The four main sections in each proposal are the planning input contract. Requirements/design/tasks, their versions, approvals, and actual implementation remain the workflow's work. Later communicated decisions supersede the original input where they differ; do not edit a proposal to conceal that progression.
