# Shared test project inputs

These completed product proposals follow the repository's [proposal template](../../../../templates/proposal-template.md). They are platform-neutral: each kit decides which inputs it uses, where it copies them, and which feature identifiers it gives them.

During setup, copy an input to `.docs/specs/{feature-name}/proposal.md`, taking the feature directory from the kit's own run matrix:
- the [Codex kit's feature sequence](../../codex/runbook.md#feature-sequence)
- the [Claude native test](../../claude/README.md)

Don't create task logs or specifications during setup.

| Input | Feature and prerequisite | Used by |
| --- | --- | --- |
| [00-line-list-project.md](00-line-list-project.md) | The initial application, built from non-application bootstrap material. In the Codex kit, Standard uses feature directory `line-list-project-v1.0.0`, and Basic and Maximum use `line-list-project`. | Codex kit |
| [01-unique-lines.md](01-unique-lines.md) | Exact uniqueness, after the accepted initial application. | Codex kit |
| [02-output-limit.md](02-output-limit.md) | An output limit, after accepted unique-lines. Its initial input accepts positive limits only. | Codex kit |
| [03-ignore-case.md](03-ignore-case.md) | Case-insensitive uniqueness, after accepted output-limit. All earlier accepted behavior is preserved. | Codex kit |
| [04-contains-filter.md](04-contains-filter.md) | A literal `--contains TEXT` filter, after the initial application. Its text includes non-ASCII characters and `<`, `>` and `&`, and it leaves one product question open for Planner to route. | Claude native test |

The four main sections of each proposal are the planning-input contract. Requirements, design, tasks, versions, approvals and implementation remain the workflow's work. Where a later decision differs from the original input, the decision supersedes it; never edit a copied proposal to hide that change. Private stimuli and expected workflow findings stay in each kit's own documents.
