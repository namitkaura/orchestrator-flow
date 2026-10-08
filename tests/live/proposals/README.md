# Test project inputs

These are completed product proposals following the repository's [proposal template](../../../templates/proposal-template.md). Each is delivered as a real Flow feature in every assurance project. Copy the inputs during bootstrap setup to `.docs/specs/{feature-name}/proposal.md`, using the [run matrix](../runbook.md#feature-sequence) to resolve the feature directory. Do not create task logs or specifications during setup.

| Input | Feature and prerequisite |
| --- | --- |
| [00-line-list-project.md](00-line-list-project.md) | Initial application in all three projects, starting from non-application bootstrap material. Standard uses feature directory `line-list-project-v1.0.0`; Basic and Maximum use `line-list-project`. |
| [01-unique-lines.md](01-unique-lines.md) | Exact uniqueness after the accepted initial application in that project. |
| [02-output-limit.md](02-output-limit.md) | Output limit after accepted unique-lines. Its initial input accepts positive limits only. |
| [03-ignore-case.md](03-ignore-case.md) | Case-insensitive uniqueness after accepted output-limit; preserve all earlier accepted behavior. |

The four main sections in each proposal are the planning-input contract. Requirements/design/tasks, versions, approvals, and implementation remain the workflow's work. Later communicated decisions supersede an original input where they differ; do not edit a copied proposal to conceal that progression. Private stimuli and expected workflow findings stay in the controller's scenario documents.
