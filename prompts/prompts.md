# ORCHESTRATOR START FROM FEATURE REQUEST:

You must follow all directives and workflow precisely as defined in your custom agent file #file:Orchestrator.agent.md and are not allowed to ignore any of the directives and instructions within.

I want to add a new feature spec.  Do not read any files listed after this point. This is the prompt you will send to the Planner:

## Planner Prompt
Read and follow all instructions and workflows from your custom agent file: `.github/agents/Planner.agent.md` You **MUST** follow these instruction precisely and cannot ignore or skip any of them.

Read `README.md` and `.docs/ai-context.md` first to get project context.  Then follow your workflow to spec out a new feature:

[DEFINE_REQUIREMENTS]]

Read `.github\prompts\codingAgentDirectives.md` to understand the coding principles and guidelines.  You **MUST** follow these principles for the spec design you create.
-----


# ORCHESTRATOR REPORT SPEC ISSUE:

You must follow all directives and workflow precisely as defined in your custom agent file #file:Orchestrator.agent.md and are not allowed to ignore any of the directives and instructions within.

I want to revise the spec based on issues noticed or clarified after implementation.  Do not read any files listed after this point. This is the prompt you will send to the Planner:

## Planner Prompt
Read and follow all instructions and workflows from your custom agent file: `.github/agents/Planner.agent.md` You **MUST** follow these instruction precisely and cannot ignore or skip any of them.

Read `README.md` and `.docs/ai-context.md` first to get project context.  Then follow your workflow to revise the spec starting from the requirements phase.  You must update the `requirements.md` file then follow your workflow prompting for accptance before moving on to updating the `design.md` file.  Then follow protocols to ask for acceptance before updating `tasks.md`. Then follow your workflow to get acceptance on the tasks before finalizing the updates to the spec. This is the same workflow as when creating a new spec but now applied to revising an existing spec.

When updating the requirements, design, and tasks files, you should not change any of the existing requirements, designs, or tasks unless necessary to accommodate the new revisions. 

Additionaly you must add a new Revision History section to the end of each of the three spec files to document the precise changes made during the revision process.  The Revision History section should include the date of the revision, a summary of the changes made, and the reason for the changes. If this is a second or subsequent revision, you will add it as a new entry in the Revision History section (i.e. `Revision 1`, `Revision 2`, etc).

The template for the Revision History section is as follows:

```
---

## Revision History

### Revision 1: <REVISION TITLE>

**Date:** 2025-11-24

**Reason for Revision:** Explanation of why the revision was necessary (e.g., to fix an error in the original spec, to clarify requirements, to add missing details, etc.)


<FOR `requirements.md` ONLY>
**Changes Made to Requirements:**

1. Requirement 1 changed: <Description of change>
    - Purpose: <Explanation of why this change was made>
    - Details: <Specific details about what was changed>
2. Requirement 2 added: <Description of added requirement>
    - Purpose: <Explanation of why this was added>
    - Details: <Specific details about what was added> 
... (add more changes as needed)

**Root Cause of Plan Error:**
Explanation of what caused the need for the revision (e.g., misinterpretation of requirements, oversight in design, etc.)

**Clarified Requirements / Expected Behavior:**
- Bullet point list of any requirements or expected behaviors that were clarified during the revision process

**Impact / Notes:**
- Bullet point list of any impacts this revision has on the overall feature, implementation, or testing
<end FOR `requirements.md` ONLY>

<FOR `design.md` ONLY>
**Changes Made to Design:**

1. **<What changed>**
    - <Description of change>
2. **<What changed>:**
    - <Description of change>
... (add more changes as needed)

**Root Cause of Plan Error:**
<Explanation of what caused the need for the revision e.g., misinterpretation of requirements, oversight in design, etc.>

**Design Decisions for New Requirements:**

1. **<First design decision>:**
    - <Detailed explanation of the design decision>
    - <addition details as needed>
    - Implementation: <How this should be implemented>
    - Rationale: <Why this design decision was made>
2. **<Second design decision>:**
    - <Detailed explanation of the design decision>
    - <addition details as needed>
    - Implementation: <How this should be implemented>
    - Rationale: <Why this design decision was made>
... (add more design decisions as needed)
<end FOR `design.md` ONLY>


<FOR `tasks.md` ONLY>
**Changes Made to Tasks:**

 <if applicable>
1. **Original Tasks X-Y:** Status preserved as completed (unchanged)

 <if applicable>
2. **Task X Updated:**
    - <Description and details of the update>
... (add more updated tasks as needed)

 <if applicable>
2. **New Tasks Added (Revision Tasks):**
    - **Task X:**  <Description of new task>
        - Scope: <Scope of the task, such as what files/components are affected, etc.>
        - Requirements covered: <which requirements are covered e.g. 3.2, 5.4, etc>
    - **Task Y:** 
        - <Description of new task>
        - Scope: <Scope of the task, such as what files/components are affected, etc.>
        - Requirements covered: <which requirements are covered e.g. 3.2, 5.4, etc> 
    ... (add more new tasks as needed)

 <if applicable>
3. **Requirements Coverage Tables Updated:**
   - Added Requirement X table (<Description of requirement>)
   - Updated Requirement Y table (<Description of requirement>)
   ... (add more updated tables as needed)

**Root Cause of Plan Error:**
<Explanation of what caused the need for the revision e.g., misinterpretation of requirements, oversight in design, etc.>

**Impact / Notes:**
- <Bullet point list of any impacts this revision has on the overall feature, implementation, or testing>

<end FOR `tasks.md` ONLY>


<for subsequent revisions, increment the revision number accordingly>
### Revision 2: <REVISION TITLE>
```

For the `requirements.md` file, you can update any existing requirements or acceptance criteria as needed to update them for the requested revisions. You can also add new requirements and acceptance criteria as needed to cover the requested revisions.  But you must not remove any existing requirements or acceptance criteria unless they are completely obsolete due to the requested revisions.

For the `design.md` file, ideally create a new revisions section to describe the changes for the requested revisions.  You can also update any existing design sections as needed to update them for the requested revisions but notes that they are updates for the requested revision.

For any completed tasks in `tasks.md`, do not change them or their completion state, but add a note to the task to indicate that there will be follow up tasks to fix any issues discovered during implementation.  Then add the follow up tasks at the end of the task list.  


[DEFINE_UPDATES_TO_SPEC]


-----


# ORCHESTRATOR REPORT IMPLEMENTATION ISSUE:

You must follow all directives and workflow precisely as defined in your custom agent file #file:Orchestrator.agent.md and are not allowed to ignore any of the directives and instructions within.

I found an issue with the implementation.  Do not read any files listed after this point. This is the prompt you will send to the Coder:

## Coder Prompt
Read and follow all instructions and workflows from your custom agent file: `.github/agents/Coder.agent.md` You **MUST** follow these instruction precisely and cannot ignore or skip any of them.

Read `README.md` and `.docs/ai-context.md` first to get project context.  Then follow your workflow to address the reported issues.  You must read the `requirements.md`,`design.md`, and `tasks.md` files to understand the updated requirements. Then follow your workflow completely to implement the necessary changes to fix the reported issues.  Then mark the tasks as resolved in `tasks.md`.


[DEFINE_ISSUE(S)_WITH_IMPLEMENTATION]


-----


# ORCHESTRATOR BUG REPORT:

You must follow all directives and workflow precisely as defined in your custom agent file #file:BugOrchestrator.agent.md and are not allowed to ignore any of the directives and instructions within.

I found a bug.  Do not read any files listed after this point. This is the prompt to send to BugPlanner (in addition to any other information or instructions that you normally include):

# BugPlanner Prompt
Follow your complete workflow as defined in `.github/agents/BugPlanner.agent.md` (which you MUST read first) Then read `README.md` and `.docs/ai-context.md` to understand the context of this project. Then you need to follow your workflow and do a deep analysis of this problem. Think very hard about this and ultra think to do a deep analysis of the problem.  Imagine that solving this problem is life or death for you and if you can't come up with a solution you will be replaced by a different AI agent.

### Bug Description
[DEFINE_BUG]


-----


# ORCHESTRATOR COMMIT MESSAGE:

Create a commit message using conventional commit format adhering to the following:

- Determine the all changes to files or new files to understand the changes made:
- Be thorough and precise in your commit message, ensuring it accurately reflects all changes made during the implementation of the plan.
- The commit message should reflect the current state of the code after implementing the plan and not a log of all the fixes and changes made during the implementation.
- All tests and documentation changes should be included in the commit.
- If the specs directory is archived or moved still include any changes to it in the commit message.
- Present the commit message in a copyable code block.


-----

