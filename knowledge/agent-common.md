# AGENT-COMMON — Shared Instructions

Read this file as your **first action** before reading your role-specific agent file.
All instructions here apply unless your role file explicitly overrides them.

---

## 1. Mode detection

Determine which mode you are in before proceeding:

- **Direct mode**: invoked via a slash command (e.g. `/analyst`) by the user directly.
  Your spawn prompt contains a user request, not a context file path.
- **Orchestrated mode**: spawned by the ORCHESTRATOR via the Agent tool.
  Your spawn prompt references a `context.md` file path and gives you a specific assignment.

---

## 2. Direct mode

**Setup:**
- Read `~/picnic-analyst-assistant/user-config.md` to get `username_prefix`
- Instructions come from the user's messages — no context file to read
- No task-id, no tasks/ folder, no TASKS.md updates
- Do not write to `~/.claude/data/agents/` — that's for orchestrated runs only

**Output folder:** create explicitly using Bash:
```bash
mkdir -p ~/picnic-analyst-assistant/direct/{username_prefix}-YYYYMMDD-HHMM-{role}-{slug}/
```
where `{role}` is your agent name (analyst, writer, engineer, ...) and
`{slug}` is 2-3 words describing the specific request, lowercased and hyphenated.

Use the **Write tool** to create `output.md` inside that folder.
Also present key findings inline in chat — the file is the record, chat is the view.

**Approval gate (direct mode):** show the draft or query inline in chat with the standard
APPROVAL REQUIRED block; wait for approval keywords before executing any irreversible action.

See your role file for the role-specific output.md schema.

---

## 3. Startup sequence (orchestrated mode)

1. Read the context file at the path given in your spawn prompt — find `## Your Assignment`
   (The file is at `~/picnic-analyst-assistant/tasks/<task-id>/context.md`)
2. **Knowledge loading:** Read `~/picnic-analyst-assistant/knowledge/INDEX.yaml`.
   Find all entries where `agents` includes your role name and `status` is `ready`.
   - `load: always` → read that file now.
   - `load: conditional` → read only if the task context matches the `condition` value.
     When in doubt, read it — over-reading is safe; under-reading risks missing conventions.
3. Read context files (see Section 4 below)
4. Execute your assignment; write all output to the path in `## Your Assignment → Output file:`
   (It will be `~/.claude/data/agents/<task-id>/<role>/output.md` — create dir if needed)

---

## 4. Context files

Always read (shared, always present):
- `~/picnic-analyst-assistant/context/picnic-business.md`

Also read any other files in `~/picnic-analyst-assistant/context/` that exist and are
relevant to the task (project context, communication style, setup notes). Skip gracefully
if absent — personal context files are gitignored and may not be present for all users.

---

## 5. Common rules

- **Never fabricate data.** Use `[DATA PLACEHOLDER]` for missing values — never estimate.
- **Approval gate keywords:** `ok`, `yes`, `go`, `send`, `approve`, `✅`, `proceed`
- **Revision keywords:** `change:`, `revise:`, `update:`, `edit:`
- **All irreversible actions** (queries, pushes, Slack sends, Sheet writes) require
  `STATUS: NEEDS_APPROVAL` before execution.
- **When knowledge is missing:** recognise the gap from the task context, not from a checklist.
  Tell the user what's missing and suggest:
  ```
  /onboard-knowledge <skill description>
  ```
  Do not improvise domain conventions you haven't been given.

---

## 6. Output file header

Every `output.md` begins with:

```markdown
# {ROLE} output
Task: <task title>
Generated: <ISO timestamp>

## Summary
<1-3 sentence BLUF>
```

Replace `{ROLE}` with your role name in ALL CAPS (e.g. `ANALYST`, `WRITER`, `ENGINEER`).
