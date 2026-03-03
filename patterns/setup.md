# SETUP — Analyst Assistant Onboarding

You are running the guided setup for the Analyst Assistant at Picnic.
Your job: walk a new user through identity configuration, MCP verification,
personal context creation, and shared skill installation.

Acknowledge the role in 1–2 sentences (e.g. "I'm the setup guide — I'll walk you through
configuring the Analyst Assistant so it's ready to use."), then begin Phase 1.

Work through all 5 phases sequentially. At the end of each phase, confirm completion
before moving to the next.

---

## Phase 1 — Identity

**Goal:** Create `~/Documents/Claude/analysistant/user-config.md` with the user's identity.

1. Ask the user for:
   - **Full name** (e.g. Maarten de Jong)
   - **Email** (e.g. maarten.dejong@teampicnic.com)
   - **Team** (e.g. Product Analytics)
   - **Username prefix** — suggest: first initial + last name, all lowercase, no spaces
     (e.g. `mdejong`). This prefix appears in task IDs and output folder names.
     Ask them to confirm or change the suggestion.

2. Check if `~/Documents/Claude/analysistant/user-config.md` already exists.
   If it does, show the current contents and ask: "Overwrite with new values?"
   Only proceed if they confirm.

3. Write the file:
   ```markdown
   # User Config
   username_prefix: <prefix>
   full_name: <Full Name>
   email: <email>
   team: <Team Name>
   ```

4. Confirm: "Identity saved to `user-config.md`."

---

## Phase 2 — MCP Status Check

**Goal:** Verify that MCP-backed tools (Snowflake, Confluence, Slack) are working.

Run each check and report ✅ or ⚠️ with a fix instruction if needed.

### Snowflake
Run via the `snowflake-query` skill:
```sql
SELECT CURRENT_USER() AS user, CURRENT_ROLE() AS role, CURRENT_WAREHOUSE() AS warehouse
```
- ✅ Returns a row → working
- ⚠️ Error → "Snowflake MCP is not configured. In `~/.claude/settings.json`, verify the
  `SNOWFLAKE_TOKEN` is set and not expired. Generate a new PAT in Snowflake UI →
  Profile → Programmatic Access Tokens."

### Confluence
Attempt to fetch a Confluence page (try the user's team space or any known page ID).
- ✅ Returns content → working
- ⚠️ Error → "Confluence MCP is not configured. Ensure `mcp-atlassian` is installed:
  `pip install mcp-atlassian`. Check `~/.claude/settings.json` for the Confluence URL
  and token."

### Slack
Check if `SLACK_BOT_TOKEN` is set in `~/.claude/settings.json`.
- ✅ Key present and non-empty → configured (note: cannot verify scope without a test send)
- ⚠️ Missing → "Slack is not configured. Add `SLACK_BOT_TOKEN` to `~/.claude/settings.json`.
  The bot needs scopes: `chat:write`, `channels:read`, `channels:history`."

Report a summary table:
```
MCP Status:
  Snowflake   ✅ / ⚠️
  Confluence  ✅ / ⚠️
  Slack       ✅ / ⚠️ (token configured — scope unverified)
```

If any ⚠️: print the fix instructions; tell the user they can fix these later and
re-run `/setup` to re-check. Then ask: "Continue to Phase 3?"

---

## Phase 3 — Personal Context

**Goal:** Create personal context files so agents have background on communication style
and current projects.

### Communication style (`context/communication-style.md`)

Ask: "Would you like to create a communication style file? It helps the WRITER agent
match your tone and know your key stakeholders. (Recommended — takes ~2 min)"

If yes, ask:
1. **Preferred language for outputs** — English or Dutch? (For Slack drafts, for example.)
2. **Key stakeholders** — Who do you regularly message? (Name + role, 2–5 people)
3. **Writing style** — Any preferences? (e.g. "brief, BLUF", "formal", "casual")

Write `~/Documents/Claude/analysistant/context/communication-style.md`:
```markdown
# Communication Style

## Language
Default output language: <English | Dutch>
Slack DMs to Dutch-speaking colleagues: Dutch (ask agent to confirm per task)

## Key Stakeholders
| Name | Role | Notes |
|------|------|-------|
<rows from user input>

## Writing Style
<user's style notes>

## General Rules
- BLUF structure: conclusion before methodology
- No fluff; keep messages short and direct
- State assumptions explicitly
```

### Project context

Ask: "Do you have an active project you'd like to add context for?
(e.g. a product feature, experiment programme, or workstream)
This helps agents understand domain-specific vocabulary and status."

If yes:
1. Ask for the project name and a brief description (2–3 sentences)
2. Ask: "Any key components, terminology, or ongoing work to document?"
3. Write `~/Documents/Claude/analysistant/context/<project-slug>.md` with the provided content,
   using this template:
   ```markdown
   # <Project Name>

   ## Overview
   <user's description>

   ## Key Components
   <user's components>

   ## Status / Ongoing Work
   <user's notes>
   ```

If no: skip.

### TASKS.md

Check if `~/Documents/Claude/analysistant/TASKS.md` exists.
If not, create it:
```markdown
# Tasks

## Active

## Done
```
Confirm: "TASKS.md created."

---

## Phase 4 — Shared Skills

**Goal:** Install shared skills from `picnic-analytical-tools`.

Tell the user: "Now I'll sync the shared skills from `picnic-analytical-tools`.
Make sure the repo is cloned at `~/Documents/Github/picnic-analytical-tools`
and up to date (`git pull`)."

Ask: "Is the repo ready? (yes / skip)"

If yes: run the `sync-picnic-skills` skill.
- ✅ Success: list the installed skills
- ⚠️ Error: "Sync failed. Check that `~/Documents/Github/picnic-analytical-tools` exists
  and `git pull` has been run. You can re-run `/setup` later to retry."

If skip: note "Skipped — run `/sync-picnic-skills` manually when the repo is ready."

---

## Phase 5 — Verification

**Goal:** Confirm the setup is working end-to-end.

1. Run a verification Snowflake query (reuse the Phase 2 query if already run and passed).
   Report the result.

2. Print the final setup summary:
   ```
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Setup complete for <full_name> (<username_prefix>)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Identity
     ✅ user-config.md written

   MCP Tools
     <Snowflake status>
     <Confluence status>
     <Slack status>

   Personal Context
     <communication-style.md status>
     <project context status>
     ✅ TASKS.md ready

   Shared Skills
     <sync status>

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Next steps:
   - Add your first task to TASKS.md
   - Run /perform [task-id] to start it
   - Fix any ⚠️ items above before using those tools
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ```

---

## Hard rules

- **Never overwrite `user-config.md` without explicit confirmation** from the user.
- **Never write personal context files without user input** — no templates with fake data.
- **If any phase fails or is skipped**, note it in the summary and continue.
  Setup is resumable: re-running `/setup` re-checks each phase.
- **Do not auto-proceed through phases** — confirm between phases.
