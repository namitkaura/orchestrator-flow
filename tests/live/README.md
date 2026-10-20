# Live test kits

Native tests run real agents. They are separate from the deterministic suite described in [tests/README.md](../README.md).

| Folder | Contents |
| --- | --- |
| [codex/](codex/README.md) | The managed Codex kit. A master session runs twelve features across three assurance projects and answers each Orchestrator's dialogs as your delegate. |
| [claude/](claude/README.md) | A short Claude Code native test that you run and answer yourself. |
| [common/](common/README.md) | Material both use: the product proposals and the verdict definitions. |

Maintaining these files doesn't authorize running either kit. Launching sessions, initializing scratch repositories and cleaning up runs each need the user's request.
