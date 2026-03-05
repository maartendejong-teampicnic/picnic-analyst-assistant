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
- No task-id, no tasks-output/ folder, no TASKS.md updates
- Do not write to `~/.claude/data/agents/` — that's for orchestrated runs only

**Output folder:** create explicitly using Bash:
```bash
mkdir -p ~/picnic-analyst-assistant/direct-output/{username_prefix}-YYYYMMDD-HHMM-{role}-{slug}/
```
where `{role}` is your agent name (analyst, writer, engineer, ...) and
`{slug}` is 2-3 words describing the specific request, lowercased and hyphenated.

Use the **Write tool** to create `output.md` inside that folder.
Also present key findings inline in chat — the file is the record, chat is the view.

**Session continuity:** Once a direct task folder is created, reuse it for all follow-up requests
in the same session — do not create a new timestamped folder. If unsure which folder is active,
check `~/picnic-analyst-assistant/direct-output/` for the most recently created `*-{role}-*` folder.

**Additional files:** All files produced during the session (SQL queries, CSV exports, .pptx,
.excalidraw, or any other output) also go into the same direct task folder, next to `output.md`.
Never save them to `~/.claude/data/Output/` or any other path in direct mode.

**Approval gate (direct mode):** show the draft or query inline in chat with the standard
APPROVAL REQUIRED block; wait for approval keywords before executing any irreversible action.

See your role file for the role-specific output.md schema.

---

## 3. Startup sequence (orchestrated mode)

1. Read the context file at the path given in your spawn prompt — find `## Your Assignment`
   (The file is at `~/picnic-analyst-assistant/tasks-output/<task-id>/context.md`)
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

Read any files in `~/picnic-analyst-assistant/context/` that exist and are relevant to
the task (project context, communication style, setup notes). Skip gracefully if absent —
all context files are personal and gitignored; they may not be present for all users.

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

## 6. Shared tools

These skills are installed via `picnic-analytical-tools` and available in `~/.claude/skills/`.
Invoke them using the Skill tool. Only use tools relevant to your role.

| Skill | Use when | Roles |
|-------|----------|-------|
| `picnic-query-snowflake` | Run SQL against Snowflake | ANALYST, ORCHESTRATOR |
| `picnic-read-dwh-data-catalog` | Find tables before writing SQL | ANALYST, ORCHESTRATOR |
| `picnic-gsheet` | Read/write Google Sheets | ANALYST, WRITER |
| `picnic-send-slack-message` | Send or post Slack messages | WRITER |
| `picnic-read-slack-channel` | Read Slack channel history | WRITER, ORCHESTRATOR |
| `picnic-ads` | Read/write Picnic's Attribute Data Store | ANALYST, ENGINEER |
| `picnic-check-teamcity-build` | Monitor CI build status | ENGINEER |
| `picnic-s3` | Read/write S3 files | ANALYST, ENGINEER |
| `picnic-query-salesforce` | Query Salesforce objects | ANALYST |

If a skill is missing from `~/.claude/skills/`, tell the user to run `picnic-sync-tools`.

---

## 7. Output file header

Every `output.md` begins with:

```markdown
# {ROLE} output
Task: <task title>
Generated: <ISO timestamp>

## Summary
<1-3 sentence BLUF>
```

Replace `{ROLE}` with your role name in ALL CAPS (e.g. `ANALYST`, `WRITER`, `ENGINEER`).
