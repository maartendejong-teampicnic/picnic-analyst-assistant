# SETUP — Analyst Assistant Onboarding

You are running the guided setup for the Analyst Assistant at Picnic.
Your job: walk a new user through identity configuration, MCP verification,
personal context creation, and shared skill installation.

Acknowledge the role in 1–2 sentences (e.g. "I'm the setup guide — I'll walk you through
configuring the Analyst Assistant so it's ready to use."), then begin Phase 0.

Work through all phases sequentially. At the end of each phase, confirm completion
before moving to the next.

---

## Phase 0 — Entry Point

**Goal:** Ensure `~/CLAUDE.md` is in place so Claude Code loads this system at every session start.

Check if `~/CLAUDE.md` exists and contains exactly:
```
@picnic-analyst-assistant/CLAUDE.md
```

- ✅ Correct → confirm and continue
- ⚠️ Wrong or missing → write the correct content to `~/CLAUDE.md` and confirm:
  "Created `~/CLAUDE.md` — Claude Code will now load the Analyst Assistant automatically."

Note: this file is your personal entry point and is **not** in the repo.

### Git isolation

Run to tell git to ignore your local modifications to agents, commands, and patterns.
These files are committed as shared starting points, but your personalizations should
never be pushed back.

```bash
git -C ~/picnic-analyst-assistant update-index --skip-worktree \
  $(git -C ~/picnic-analyst-assistant ls-files agents/ commands/ patterns/)
```

- ✅ No output → working. `git status` will now always be clean for these files.
- ⚠️ Error → note it and continue; non-critical. User can run manually later.

---

## Phase 1 — Identity

**Goal:** Create `~/picnic-analyst-assistant/user-config.md` with the user's identity.

1. Ask the user for:
   - **Full name** (e.g. Maarten de Jong)
   - **Email** (e.g. maarten.dejong@teampicnic.com)
   - **Team** (e.g. Shopping / Usuals)
   - **Username prefix** — suggest: first initial + last name, all lowercase, no spaces
     (e.g. `mdejong`). This prefix appears in task IDs and output folder names.
     Ask them to confirm or change the suggestion.

2. Check if `~/picnic-analyst-assistant/user-config.md` already exists.
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

## Phase 2 — MCP Setup & Verification

**Goal:** Configure MCP connections for Snowflake, Confluence, and Slack, then verify each is working.

### Pre-check: settings.json

Check if `~/.claude/settings.json` exists:
- ✅ Exists → read the current `mcpServers` section and proceed to each tool below
- ⚠️ Missing → create it now with this base template (Picnic-specific fixed values pre-filled):

```json
{
  "env": {},
  "permissions": {
    "defaultMode": "default"
  },
  "mcpServers": {
    "snowflake": {
      "command": "mcp_snowflake_server",
      "args": [],
      "env": {
        "SNOWFLAKE_ACCOUNT": "BF99047-UJ82639",
        "SNOWFLAKE_USER": "",
        "SNOWFLAKE_AUTHENTICATOR": "PROGRAMMATIC_ACCESS_TOKEN",
        "SNOWFLAKE_TOKEN": "",
        "SNOWFLAKE_WAREHOUSE": "ANALYSIS",
        "SNOWFLAKE_DATABASE": "PICNIC_NL_PROD",
        "SNOWFLAKE_SCHEMA": "DIM",
        "SNOWFLAKE_ROLE": "ANALYST"
      }
    },
    "confluence": {
      "command": "mcp-atlassian",
      "args": [],
      "env": {
        "CONFLUENCE_URL": "https://picnic.atlassian.net/wiki",
        "CONFLUENCE_USERNAME": "",
        "CONFLUENCE_API_TOKEN": ""
      }
    },
    "slack": {
      "command": "slack-mcp-server",
      "args": [],
      "env": {
        "SLACK_MCP_XOXP_TOKEN": ""
      }
    }
  }
}
```

For each tool below: check if the relevant fields are already filled in. If yes, run the
verification check. If empty or missing, walk through the setup steps first.

---

### Snowflake

**Check:** Is `SNOWFLAKE_TOKEN` set and non-empty in `mcpServers.snowflake.env`?

**If not configured — walk through these steps with the user:**
1. Open a browser → log into your Snowflake account (the way you normally access it, e.g. via app.snowflake.com or your bookmark)
2. Click your avatar (bottom left) → **Settings**
4. Go to **Authentication** → **Programmatic Access Tokens** → click **Generate new token**
5. Name it `claude-code`, set expiry to maximum (1 year)
6. **Copy the token immediately** — it is shown only once
7. Ask the user to paste the token here

When you have the token, update `~/.claude/settings.json`:
- Set `SNOWFLAKE_USER` to their email **in UPPERCASE** (e.g. `FIRSTNAME.LASTNAME@TEAMPICNIC.COM`)
- Set `SNOWFLAKE_TOKEN` to the pasted token

**Verification** (run after configuring, or if already configured):
Run via the `snowflake-query` skill:
```sql
SELECT CURRENT_USER() AS user, CURRENT_ROLE() AS role, CURRENT_WAREHOUSE() AS warehouse
```
- ✅ Returns a row → working. Report the user/role/warehouse values.
- ⚠️ Error → "Token may be expired or `SNOWFLAKE_USER` is not all-caps. Regenerate the PAT
  in Snowflake UI if needed, update `settings.json`, then restart Claude Code."

Note: remind the user that PAT tokens expire (max 1 year). When Snowflake queries stop working,
regenerate the token and replace `SNOWFLAKE_TOKEN` in `settings.json`.

---

### Confluence

**Check:** Is `CONFLUENCE_API_TOKEN` set and non-empty in `mcpServers.confluence.env`?

**If not configured — walk through these steps with the user:**
1. Install the MCP server:
   ```bash
   pip install mcp-atlassian
   ```
2. Open a browser → go to https://id.atlassian.com/manage-profile/security/api-tokens
3. Sign in with your Picnic email
4. Click **Create API token** → name it `claude-code`
5. **Copy the token immediately** — it is shown only once
6. Ask the user to paste the token here

When you have the token, update `~/.claude/settings.json`:
- Set `CONFLUENCE_USERNAME` to their email (lowercase)
- Set `CONFLUENCE_API_TOKEN` to the pasted token

**Verification** (run after configuring, or if already configured):
Attempt to fetch a Confluence page using the MCP tool.
- ✅ Returns content → working
- ⚠️ Error → "Check that `mcp-atlassian` is installed (`pip show mcp-atlassian`) and the
  API token is correct. Restart Claude Code after any changes to `settings.json`."

---

### Slack

**Check:** Is `SLACK_MCP_XOXP_TOKEN` set and non-empty in `mcpServers.slack.env`?

**If not configured — walk through these steps with the user:**
1. Ask if they have access to the Picnic Slack MCP app. If unsure, they should check with a
   colleague who already has the assistant set up.
2. To get a user token:
   - Go to https://api.slack.com/apps → open the shared Picnic Claude assistant app
   - Go to **OAuth & Permissions** → confirm **User Token Scopes** include:
     `chat:write`, `channels:read`, `channels:history`, `lists:read`
   - Under **OAuth Tokens for Your Workspace**, copy the **User OAuth Token** (starts with `xoxp-`)
3. Ask the user to paste the token here

When you have the token, update `~/.claude/settings.json`:
- Set `SLACK_MCP_XOXP_TOKEN` to the pasted token

**Verification:**
Check if `SLACK_MCP_XOXP_TOKEN` is set and non-empty.
- ✅ Present and non-empty → configured (scope cannot be verified without a test send)
- ⚠️ Missing or placeholder → "Slack is not yet configured. It's optional — you can skip
  it now and configure it later."

Note: Slack is the least critical of the three. If the user can't access the Picnic Slack app
yet, skip it and continue.

---

### After any settings.json changes

If you updated `settings.json` during this phase, tell the user:
> "You need to **restart Claude Code** for MCP changes to take effect.
> After restarting, run `/setup` again — it will re-run the verification checks and pick up
> where you left off."

---

### Phase 2 summary

Report a summary table:
```
MCP Status:
  Snowflake   ✅ / ⚠️
  Confluence  ✅ / ⚠️
  Slack       ✅ / ⚠️ (token configured — scope unverified)
```

If any ⚠️: tell the user they can fix these later and re-run `/setup` to re-check.
Then ask: "Continue to Phase 3?"

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

Write `~/picnic-analyst-assistant/context/communication-style.md`:
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
3. Write `~/picnic-analyst-assistant/context/<project-slug>.md` with the provided content,
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

Check if `~/picnic-analyst-assistant/TASKS.md` exists.
If not, create it:
```markdown
# Tasks

## Active

## Done
```
Confirm: "TASKS.md created."

---

## Phase 4 — Shared Skills

**Goal:** Check Python + Poetry are available, then install shared skills from `picnic-analytical-tools`.

### Python + Poetry check

Run: `python3 --version && poetry --version`

- ✅ Both present → continue
- ⚠️ Python missing → "Install Python 3.10+: https://www.python.org/downloads/"
- ⚠️ Poetry missing → "Install Poetry: `curl -sSL https://install.python-poetry.org | python3 -`"

If either ⚠️: print the fix instructions and ask whether to continue or skip to Phase 5.
Local skills (gdrive, slides, costs) require Poetry to run.

### Skill sync

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

   Entry Point
     <~/CLAUDE.md status>

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

   Local Tools
     <Python status>
     <Poetry status>

   Shared Skills
     <sync status>

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Next steps:
   - Run /onboard-knowledge to add your first skill files (do this before /perform)
   - Add your first task to TASKS.md
   - Run /perform to start it
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
