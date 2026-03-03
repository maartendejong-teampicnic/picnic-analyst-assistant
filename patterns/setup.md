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

**Goal:** Configure MCP connections. Snowflake and GitHub are required for all users. Confluence and Slack are optional — configure only the tools you use.

### What are MCPs?
MCPs (Model Context Protocol servers) let Claude Code call external systems — databases,
wikis, messaging tools — directly during a session. Each server is configured in
`~/.claude/settings.json` under `mcpServers`, with a `command` (the server binary) and
`env` (credentials). GitHub is an exception: it uses the `gh` CLI, not mcpServers.

After any change to `settings.json`, Claude Code must be restarted for the change to
take effect. `/setup` is resumable — re-running it skips steps that are already complete.

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

### Mandatory: GitHub

**Goal:** Ensure `gh` CLI is installed and authenticated.

Run: `gh auth status`
- ✅ Logged in → confirm and continue
- ⚠️ Not authenticated → run `gh auth login` and follow the prompts:
  1. Select **GitHub.com**
  2. Choose **HTTPS**
  3. Authenticate via browser — sign in with your Picnic GitHub account
  4. After login, re-run `gh auth status` to confirm

Verify repo access:
```bash
gh repo view PicnicSupermarket/picnic-dbt-models --json name
```
- ✅ Returns repo info → working
- ⚠️ Access denied → "Check with your team lead to be added to the PicnicSupermarket org."

Note: `gh` credentials are stored by the CLI — no entry needed in `settings.json`.

---

### Optional tools — select what you need

Ask the user: "Which optional tools would you like to configure?
  - **Confluence** — read and write Confluence pages (useful for documentation work)
  - **Slack** — read channels and send messages from Claude

You can configure them now or skip and re-run `/setup` later to add them."

Work through each selected tool below. Skip any tool the user does not select.

---

### Optional: Confluence

**Check:** Is `CONFLUENCE_API_TOKEN` set and non-empty in `mcpServers.confluence.env`?

**If not configured — walk through these steps with the user:**
1. Install the MCP server:
   ```bash
   pip install mcp-atlassian
   ```
2. Open a browser → go to https://id.atlassian.com/manage-profile/security/api-tokens
3. Sign in with your Picnic email
4. Click your **Account settings** (top right) →  **Security** →  scroll down to **Create API token**.
5. **Copy the token immediately** — it is shown only once
6. Ask the user to paste the token here

When you have the token, update `~/.claude/settings.json`:
- Set `CONFLUENCE_USERNAME` to their email (lowercase)
- Set `CONFLUENCE_API_TOKEN` to the pasted token

If `mcpServers.confluence` does not yet exist in `settings.json`, add the following block
to the `mcpServers` object:
```json
"confluence": {
  "command": "mcp-atlassian",
  "args": [],
  "env": {
    "CONFLUENCE_URL": "https://picnic.atlassian.net/wiki",
    "CONFLUENCE_USERNAME": "<email>",
    "CONFLUENCE_API_TOKEN": "<token>"
  }
}
```

**Verification** (run after configuring, or if already configured):
Attempt to fetch a Confluence page using the MCP tool.
- ✅ Returns content → working
- ⚠️ Error → "Check that `mcp-atlassian` is installed (`pip show mcp-atlassian`) and the
  API token is correct. Restart Claude Code after any changes to `settings.json`."

---

### Optional: Slack

**Check:** Is `mcpServers.slack` present and `SLACK_MCP_XOXP_TOKEN` set and non-empty?

**If not configured — walk through these steps with the user:**
1. Check with a colleague who already has Slack set up — they can share the Picnic Claude
   app details and confirm your token scopes.
2. Go to the Picnic Claude Slack app → **OAuth & Permissions** → confirm **User Token Scopes**
   include: `chat:write`, `channels:read`, `channels:history`, `lists:read`
3. Under **OAuth Tokens for Your Workspace**, copy the **User OAuth Token** (starts with `xoxp-`)
4. Ask the user to paste the token here

When you have the token:
- Add the following block to `mcpServers` in `settings.json`:
  ```json
  "slack": {
    "command": "slack-mcp-server",
    "args": [],
    "env": {
      "SLACK_MCP_XOXP_TOKEN": "<token>"
    }
  }
  ```
- Confirm the block is saved

**Verification:**
Check that `SLACK_MCP_XOXP_TOKEN` is set and non-empty.
- ✅ Present → configured (scope cannot be verified without a test send)
- ⚠️ Not yet → "You can add it later by re-running `/setup`."

Note: Slack token needs manual renewal when it expires. When Slack calls stop working,
re-run `/setup` to update the token in `settings.json`.

---

### After any settings.json changes

If you updated `settings.json` during this phase, tell the user:
> "You need to **restart Claude Code** for MCP changes to take effect.
> After restarting, run `/setup` again — it will re-run the verification checks and pick up
> where you left off."

---

### Phase 2 summary

Report a summary table covering every tool checked in this phase:
```
MCP Status:
  Snowflake    ✅ / ⚠️
  GitHub       ✅ / ⚠️
  <Confluence> ✅ / ⚠️  (if selected)
  <Slack>      ✅ / ⚠️  (if selected)
```

If any ⚠️: tell the user they can fix these later and re-run `/setup` to re-check.
Then ask: "Continue to Phase 3?"

---

## Phase 3 — Personal Context

**Goal:** Create personal context files so agents have background on current projects, and ensure TASKS.md exists.

### Project context

Ask: "Do you have an active project you'd like to add context for?
(e.g. a new DBT model, app feature or dashboard?)
This helps kickstart agents to work with domain-specific vocabulary and status."

If yes:
1. Ask for the project name and a brief description (2–3 sentences)
2. Ask: "Any key components, terminology, or resources to document?"
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

Check if `~/Documents/Github/picnic-analytical-tools` exists:

- ✅ Exists → run `git -C ~/Documents/Github/picnic-analytical-tools pull` to update
- ⚠️ Missing → clone it now (uses the `gh` CLI set up in Phase 2):
  ```bash
  gh repo clone PicnicSupermarket/picnic-analytical-tools ~/Documents/Github/picnic-analytical-tools
  ```
  - ✅ Cloned → continue
  - ⚠️ Error → "Check that your GitHub account has access to PicnicSupermarket/picnic-analytical-tools.
    You can re-run `/setup` later to retry."

Once the repo is present and up to date, run the `sync-picnic-skills` skill.
- ✅ Success: list the installed skills
- ⚠️ Error: "Sync failed. You can re-run `/setup` later to retry."

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
     <status line per tool configured in Phase 2>

   Personal Context
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
