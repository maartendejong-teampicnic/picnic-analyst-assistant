# CONTEXT TEMPLATE
# The orchestrator copies this to tasks-output/<task-id>/context.md at task start.
# Never use this file directly.
# ─────────────────────────────────────────────────────────────────────────────

# CONTEXT — [task-id]
Generated: —
Task: —
Task ID: —
Status: —

## Task Brief
[Full task description, constraints, desired outcome]

## Relevant Files
[List of files the specialist should read before executing]

## Your Assignment (active agent reads this)
Role: —
Instructions: —
Output file: ~/.claude/data/agents/[task-id]/[role]/output.md
Approval required: —

## Inputs From Prior Agents
<!-- Orchestrator adds a section per spawned agent as the task progresses.
     Format per section:
     ### <ROLE> output
     STATUS: pending | not-needed | complete
     [Key findings summary for downstream agents]  -->

## Subtask Tracker
- [ ] Orchestrator: plan written
- [ ] Agents: executing
- [ ] Side effects: executed

## Pending User Inputs
[None]

## Side Effects Log
[None]
