@~/picnic-analyst-assistant/agents/ORCHESTRATOR.md

You have been invoked via `/perform`. Argument (if any): $ARGUMENTS

## What to do now

1. Read `~/picnic-analyst-assistant/TASKS.md`.

2. If an argument was provided, treat it as the task identifier (id, title fragment, or
   task number) and skip to step 3.

   If no argument was provided, present the Active tasks as a numbered list and ask the
   user to pick one:

   ```
   Active tasks:
     1. <task title> [<status>]
     2. <task title> [<status>]
     ...

   Type a number to select a task, or /tasks to add a new one.
   ```

   Wait for the user to respond before continuing.
   Multiple selections separated by commas or "and" indicate tasks to run sequentially.

3. Identify the target task(s) from TASKS.md.

4. Resolve the `task-id` for each task (see Task ID resolution in ORCHESTRATOR.md).

5. For each task, check for an existing `tasks-output/<task-id>/context.md`:
   - File exists and no `summary.md` → task in flight; ask whether to resume or start fresh.
   - File exists and `summary.md` present → task already done; confirm before restarting.
   - File absent → clean slate; proceed to planning.

6. Enter ORCHESTRATOR Planning Phase (Phase 1) for the first task:
   - Load relevant pattern files and memory files
   - Decompose into subtasks with agent assignments
   - Create `tasks-output/<task-id>/context.md` from the template at `CONTEXT.md`
   - Present the plan with the approval prompt
   - Wait for explicit confirmation before spawning any agents

7. After the first task closes (Phase 4), proceed to the next task if one was specified
   or if the user confirms.

**Do not skip the planning phase. Do not spawn agents without user approval.**
**Do not run two tasks in parallel within one session — open a second terminal for that.**
