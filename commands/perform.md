@~/picnic-analyst-assistant/agents/ORCHESTRATOR.md

You have been invoked via `/perform`. Argument (if any): $ARGUMENTS

## What to do now

1. If an argument was provided, treat it as the task identifier (id, title fragment, or
   task number). Otherwise, use the most recent Active task in TASKS.md.
   Multiple arguments separated by commas or "and" indicate multiple tasks to run
   sequentially in this session.

2. Read `~/picnic-analyst-assistant/user-config.md` to get `username_prefix`.

3. Read `~/picnic-analyst-assistant/TASKS.md` to identify the target task(s).

4. Resolve the `task-id` for each task (see Task ID resolution in ORCHESTRATOR.md).

5. For each task, check for an existing `tasks/<task-id>/context.md`:
   - File exists and no `summary.md` → task in flight; ask whether to resume or start fresh.
   - File exists and `summary.md` present → task already done; confirm before restarting.
   - File absent → clean slate; proceed to planning.

6. Enter ORCHESTRATOR Planning Phase (Phase 1) for the first task:
   - Load relevant pattern files and memory files
   - Decompose into subtasks with agent assignments
   - Create `tasks/<task-id>/context.md` from the template at `CONTEXT.md`
   - Present the plan with the approval prompt
   - Wait for explicit confirmation before spawning any agents

7. After the first task closes (Phase 4), proceed to the next task if one was specified
   or if the user confirms.

**Do not skip the planning phase. Do not spawn agents without user approval.**
**Do not run two tasks in parallel within one session — open a second terminal for that.**
