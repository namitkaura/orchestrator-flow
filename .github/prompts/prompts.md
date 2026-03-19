# ORCHESTRATOR START FROM FEATURE REQUEST:

You must follow all directives and workflow precisely as defined in your custom agent file `.github/agents/Orchestrator.agent.md` and are not allowed to ignore any of the directives and instructions within.

I want to add a new feature spec.  Do not read any files listed after this point. This is the prompt you will send to the Planner:

## Planner Prompt
Read and follow all instructions and workflows from your custom agent file: `.github/agents/Planner.agent.md` You **MUST** follow these instruction precisely and cannot ignore or skip any of them.

Read `README.md` and `AGENTS.md` (if they exist) first to get project context.  Then follow your workflow to spec out a new feature:

[DEFINE_REQUIREMENTS]

Read `.github/agents/Directives/codingAgentDirectives.md` to understand the coding principles and guidelines.  You **MUST** follow these principles for the spec design you create.


---


# ORCHESTRATOR REPORT SPEC ISSUE:

You must follow all directives and workflow precisely as defined in your custom agent file `.github/agents/Orchestrator.agent.md` and are not allowed to ignore any of the directives and instructions within.

I want to revise the spec based on issues noticed or clarified after implementation.  Do not read any files listed after this point. This is the prompt you will send to the Planner:

## Planner Prompt
Read and follow all instructions and workflows from your custom agent file: `.github/agents/Planner.agent.md` You **MUST** follow these instruction precisely and cannot ignore or skip any of them.

Read `README.md` and `AGENTS.md` (if they exist) first to get project context.  Then follow your workflow to revise the spec starting from the requirements phase.  You must update the `requirements.md` file then follow your workflow prompting for acceptance before moving on to updating the `design.md` file.  Then follow protocols to ask for acceptance before updating `tasks.md`. Then follow your workflow to get acceptance on the tasks before finalizing the updates to the spec. This is the same workflow as when creating a new spec but now applied to revising an existing spec.


[DEFINE_UPDATES_TO_SPEC]


---


# ORCHESTRATOR REPORT IMPLEMENTATION ISSUE:

You must follow all directives and workflow precisely as defined in your custom agent file `.github/agents/Orchestrator.agent.md` and are not allowed to ignore any of the directives and instructions within.

I found an issue with the implementation.  Do not read any files listed after this point. This is the prompt you will send to the Coder:

## Coder Prompt
Read and follow all instructions and workflows from your custom agent file: `.github/agents/Coder.agent.md` You **MUST** follow these instruction precisely and cannot ignore or skip any of them.

Read `README.md` and `AGENTS.md` (if they exist) first to get project context.  Then follow your workflow to address the reported issues.  You must read the `requirements.md`,`design.md`, and `tasks.md` files to understand the original requirements. Then follow your workflow completely to implement the necessary changes to fix the reported issues.  


[DEFINE_ISSUE(S)_WITH_IMPLEMENTATION]


---


# ORCHESTRATOR BUG REPORT:

You must follow all directives and workflow precisely as defined in your custom agent file `.github/agents/BugOrchestrator.agent.md` and are not allowed to ignore any of the directives and instructions within.

I found a bug.  Do not read any files listed after this point. This is the prompt to send to BugPlanner (in addition to any other information or instructions that you normally include):

# BugPlanner Prompt
Follow your complete workflow as defined in `.github/agents/BugPlanner.agent.md` (which you MUST read first) Then read `README.md` and `AGENTS.md` (if they exist) to understand the context of this project. Then you need to follow your workflow and do a deep analysis of this problem. Think very hard about this and ultra think to do a deep analysis of the problem.  Imagine that solving this problem is life or death for you and if you can't come up with a solution you will be replaced by a different AI agent.

### Bug Description
[DEFINE_BUG]


---


# ORCHESTRATOR COMMIT MESSAGE:

Create a commit message using conventional commit format adhering to the following:

- Determine all the changes to files or new files to understand the changes made:
- Be thorough and precise in your commit message, ensuring it accurately reflects all changes made during the implementation of the plan.
- The commit message should reflect the current state of the code after implementing the plan and not a log of all the fixes and changes made during the implementation.
- All tests and documentation changes should be included in the commit.
- If the specs directory is archived or moved still include any changes to it in the commit message.
- Present the commit message in a copyable code block.


---


# REVIEWER STANDALONE REVIEW (GitLab Issue and Merge Request):

Whenever accessing Gitlab resources, you must use the Gitlab MCP tools only and not try to use the fetch or web access tools (they won't work).  

Given this Gitlab issue [`issue`] and associated merge request [`merge_request`] you must do a complete review of the merge request changes in relation to the issue. 

Perform a through review being a skeptical and critical reviewer and follow your workflow. 

Also whenever you need to search, read through the code, run tests, or do any other things that would add to your context windows, you must use the `searchSubagent` or `runSubagent` tools to do so using a subagent prompt that is clear and specific about what you need to do and what information you need to gather.  You must also specify specifically what you want the subagent to return to you as only that should be added to your context window.  You should not try to do any of these things yourself and must use the tools to do so through subagents and avoid filling your context window with unnecessary information.  Always use the GPT-5.3-Codex (copilot) model (it has the highest context window and is best for this type of work) for your subagents when doing reviews.

When the review is completed, instead of the normal reviewer_wrapper, create a detailed review report in markdown format in a copyable code block using four backticks.
