Read `~/picnic-analyst-assistant/TASKS.md` silently. Do not display it yet.

Present this menu — nothing else:

```
What would you like to do?

  1. Add a new task
  2. Start a task from my list
```

Wait for the user to reply (1 / 2 / "add" / "start" / "pick" / task title or number).

---

## Option 1 — Add a new task

If the user picks 1 or types `add` / `new`, run the intake below.
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

Then say: "Task added." and immediately offer the menu again:

```
What would you like to do next?

  1. Add another task
  2. Start a task from my list
```

---

## Option 2 — Start a task from the list

If the user picks 2 or types `start` / `pick` / `perform`, display the Active tasks as a
numbered list (from TASKS.md). If there are no Active tasks, say so and offer Option 1.

Example format:
```
Active tasks:

  1. [ANALYSIS] Query Usuals page users of yesterday and post to Slack
  2. [ENGINEERING] Add long-press metric to dashboard

Pick a number to start.
```

When the user picks a number, confirm the selection and execute the task by following
the full ORCHESTRATOR instructions in `~/picnic-analyst-assistant/agents/ORCHESTRATOR.md`
(read it now if not already loaded). Treat the selected task as if `/perform` was run for it.

$ARGUMENTS
