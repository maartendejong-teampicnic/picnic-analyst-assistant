Read `~/picnic-analyst-assistant/TASKS.md` and display the full contents.

Then say: "Run `/perform` to start a task. Type `add` to create a new one."

---

## Add-task mode

If the user types `add`, `new`, or asks to add a task, run the intake below.
Ask **one question at a time**. Do not list all questions upfront.

### Q1 — Goal
"What do you want to achieve? Describe it in one sentence — what should be done or produced?"

### Q2 — Deliverable
"What's the main output?
- Data / metric / SQL query
- dbt model or GitHub PR
- Slack message or Confluence page
- PowerPoint slide deck
- Excalidraw diagram
- Something else?"

### Q3 — Context *(only ask if the goal implies specific scope or dependencies)*
"Any context to include? For example:
- Relevant table or project names
- Market scope (NL / DE / FR / all)
- Links to Confluence pages, Jira tickets, or Slack threads
*(Press Enter to skip)*"

---

## Compose the task entry

From the answers, determine:

| Field | How to fill |
|---|---|
| `[TAG]` | ANALYSIS / ENGINEERING / COMMUNICATION / PRESENTATION / DESIGN / SETUP |
| Title | Short imperative sentence (≤ 10 words) — what to do |
| `brief:` | 1–2 sentences: goal + deliverable, in plain language |
| `context:` | Files, URLs, or notes from Q3 — omit the line if none given |
| `status:` | Always `Draft` for new tasks |

Format the entry as:
```
- [ ] [TAG] Title
  status: Draft
  brief: <goal and deliverable in 1–2 sentences>
  context: <if provided, else omit this line>
```

Show the composed entry to the user and ask:
"Add this to TASKS.md? Reply `yes` to confirm or describe a change."

On confirmation: append the entry under `## Active` in `~/picnic-analyst-assistant/TASKS.md`.

Then say: "Task added. Run `/perform` to start it."

$ARGUMENTS
