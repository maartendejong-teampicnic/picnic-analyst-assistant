# SETUP — Analyst Assistant Onboarding

You are running the guided setup for the Analyst Assistant at Picnic.
Your job: walk a new user through bootstrap, identity, MCP connections, and skill installation.

Acknowledge the role in 1–2 sentences, then immediately print the welcome message below and
begin Phase 0. Do not ask for permission to start.

---

## Welcome message (print at the very start, before any action)

```
Welcome to the Picnic Analyst Assistant setup.

I'll walk you through 4 short phases:

  Phase 0 — Install        Set up commands and protect your personal files  (~30s, automatic)
  Phase 1 — Identity       Your name, email, and task prefix                (~1 min)
  Phase 2 — Connections    Snowflake, GitHub, and optional tools            (5–10 min)
  Phase 3 — Skills         Sync shared tools from the tools repo            (~1 min)

Let's go.
```

---

## Phase 0 — Install

**Fully automatic — no user input needed. Run all steps, then move to Phase 1.**

### 1. Install commands

```bash
cp ~/picnic-analyst-assistant/commands/*.md ~/.claude/commands/
```

List the installed files. Print: `✅ All commands installed.`

### 2. Git isolation

Protect personalizations in agents/, commands/, and patterns/ from being accidentally committed:

```bash
git -C ~/picnic-analyst-assistant update-index --skip-worktree \
  $(git -C ~/picnic-analyst-assistant ls-files agents/ commands/ patterns/)
```

- ✅ No output → working. `git status` will always be clean for these files.
- ⚠️ Error → note it and continue; non-critical.

### 3. TASKS.md

Check if `~/picnic-analyst-assistant/TASKS.md` exists. If not, create it silently:

```markdown
# Tasks

## Active

## Done
```

### 4. Entry point check

If `~/CLAUDE.md` exists and references this repo, tell the user:
"You have a `~/CLAUDE.md` that imports from this repo — it is no longer needed. You can delete it if you like."

Print: `✅ Phase 0 complete.` then move immediately to Phase 1.

---

## Phase 1 — Identity

**Goal:** Create `~/picnic-analyst-assistant/user-config.md` with the user's identity.

Ask in one message:
> "What's your full name and Picnic email?
> And which team are you on? (e.g. Consumer - Shopping - Usuals)
>
> Example: Maarten de Jong · maarten.dejong@teampicnic.com · Consumer - Shopping - Usuals"

From the email, derive the username prefix automatically:
- Logic: first char of first name + lastname, all lowercase, no spaces
- `maarten.dejong@teampicnic.com` → `mdejong`

In the same reply or a follow-up, show the derived prefix and confirm:
> "Username prefix: `mdejong` — looks good? Press Enter to confirm, or type a different one."

Check if `~/picnic-analyst-assistant/user-config.md` already exists. If it does, show the current
contents and ask: "Overwrite with new values?" Only proceed if they confirm.

Write the file:
```markdown
# User Config
username_prefix: <prefix>
full_name: <Full Name>
email: <email>
team: <Team Name>
```

Print: `Identity saved. → Moving to connections.` then move to Phase 2.

---

## Phase 2 — Connections

**Goal:** Configure MCP connections. Snowflake and GitHub are required. Confluence and Slack optional.

### What are MCPs?

MCPs (Model Context Protocol servers) let Claude Code call external systems — databases, wikis,
messaging tools — directly during a session. Each server lives in `~/.claude/settings.json`
under `mcpServers`. GitHub uses the `gh` CLI instead.

After any change to `settings.json`, Claude Code must be restarted for changes to take effect.
`/setup` is resumable — re-running it skips steps already complete.

### Pre-check: settings.json

Check if `~/.claude/settings.json` exists:
- ✅ Exists → read current `mcpServers` and continue
- ⚠️ Missing → create it now with this base template (Picnic fixed values pre-filled):

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

For each tool below: if already configured, run verification. If empty or missing, walk through setup first.

---

### Required: Snowflake

**Check:** Is `SNOWFLAKE_TOKEN` set and non-empty in `mcpServers.snowflake.env`?

**If not configured:**
1. Open a browser → log into your Snowflake account
2. Click your avatar (bottom left) → **Settings**
3. Go to **Authentication** → **Programmatic Access Tokens** → **Generate new token**
4. Name it `claude-code`, set expiry to maximum (1 year)
5. **Copy the token immediately** — it is shown only once
6. Paste the token here

When you have the token, update `~/.claude/settings.json`:
- Set `SNOWFLAKE_USER` to their email **in UPPERCASE** (e.g. `FIRSTNAME.LASTNAME@TEAMPICNIC.COM`)
- Set `SNOWFLAKE_TOKEN` to the pasted token

**Verification** (run after configuring, or if already configured):
Run via the `snowflake-query` skill:
```sql
SELECT
  CURRENT_USER() AS you,
  CURRENT_ROLE() AS role,
  CURRENT_WAREHOUSE() AS warehouse,
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES) AS tables_accessible
```

- ✅ Returns a row → print the wow output:
  ```
  ⚡ Snowflake connected
     You: FIRSTNAME.LASTNAME@TEAMPICNIC.COM
     Role: ANALYST · Warehouse: ANALYSIS
     Tables accessible: 1,247
  ```
  (Use actual values from the query result — substitute the real user and table count.)

- ⚠️ Error → "Token may be expired or `SNOWFLAKE_USER` is not all-caps. Regenerate the PAT
  in Snowflake UI if needed, update `settings.json`, then restart Claude Code."

Note: PAT tokens expire (max 1 year). When Snowflake queries stop working, regenerate and update `SNOWFLAKE_TOKEN`.

---

### Required: GitHub

**Goal:** Ensure `gh` CLI is installed and authenticated.

Run: `gh auth status`
- ✅ Logged in → continue
- ⚠️ Not authenticated → run `gh auth login`:
  1. Select **GitHub.com**
  2. Choose **HTTPS**
  3. Authenticate via browser — sign in with your Picnic GitHub account
  4. Re-run `gh auth status` to confirm

**Verification:**
1. Verify org access: `gh api orgs/PicnicSupermarket --jq '.login'`
2. Show their own recent PRs:
   ```bash
   gh pr list --repo PicnicSupermarket/picnic-dbt-models --author @me --state all --limit 3 --json title,state
   ```
3. Show latest open PR:
   ```bash
   gh pr list --repo PicnicSupermarket/picnic-dbt-models --state open --limit 1 --json title
   ```

Print wow output:
```
⚡ GitHub connected
   Organisation: PicnicSupermarket — access confirmed

   Your recent PRs in picnic-dbt-models:
     • <actual PR title> (<state>)
     • <actual PR title> (<state>)

   Latest open PR: "<actual PR title>"
```
(Use actual values from the commands. If no personal PRs found, skip that section gracefully.)

Note: `gh` credentials are stored by the CLI — no entry needed in `settings.json`.

---

### Optional tools

Ask once:
> "Which optional tools would you like to set up?
>   A — Confluence (read/write pages)
>   B — Slack (read channels, send messages)
>   C — Skip for now
>
> You can always re-run /setup to add them later."

Work through each selected tool. Skip anything the user does not select.

---

### Optional: Confluence

**Check:** Is `CONFLUENCE_API_TOKEN` set and non-empty in `mcpServers.confluence.env`?

**If not configured:**
1. Install the MCP server:
   ```bash
   pip install mcp-atlassian
   ```
2. Go to https://id.atlassian.com/manage-profile/security/api-tokens
3. Sign in with your Picnic email
4. Click **Create API token**, give it a name, click **Create**
5. **Copy the token immediately** — it is shown only once
6. Paste the token here

When you have the token, add to `mcpServers` in `settings.json`:
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

**Verification:** Use the Confluence MCP to search for pages they contributed to using CQL:
`contributor = currentUser() ORDER BY lastmodified DESC`
If that returns no results (new employee), fall back to searching for "analytics".

Print wow output:
```
⚡ Confluence connected
   Found: (title of the first result returned)
```
(Use the actual page title returned.)

- ⚠️ Error → "Check that `mcp-atlassian` is installed (`pip show mcp-atlassian`) and the API token is correct."

---

### Optional: Slack

**Check:** Is `SLACK_MCP_XOXP_TOKEN` set and non-empty in `mcpServers.slack.env`?

**If not configured:**
1. Check with a colleague who has Slack set up — they can share Picnic Claude app details
2. Go to the Picnic Claude Slack app → **OAuth & Permissions** → confirm scopes include:
   `chat:write`, `channels:read`, `channels:history`, `lists:read`
3. Under **OAuth Tokens for Your Workspace**, copy the **User OAuth Token** (starts with `xoxp-`)
4. Paste the token here

Add to `mcpServers` in `settings.json`:
```json
"slack": {
  "command": "slack-mcp-server",
  "args": [],
  "env": {
    "SLACK_MCP_XOXP_TOKEN": "<token>"
  }
}
```

Print: `⚡ Slack configured — token saved. You'll see it in action when you use /writer.`

---

### After any settings.json changes — restart notice

If `settings.json` was updated during this phase, print this block prominently and **stop**:

```
⚡ Restart required
   settings.json was updated. Restart Claude Code now, then reopen VS Code from
   ~/picnic-analyst-assistant/ and run /setup again — it will pick up from Phase 3.
```

Do not proceed to Phase 3. The user must restart first.

---

### Connections summary (print before moving on)

```
Connections:
  Snowflake    ✅  (ANALYST role · ANALYSIS warehouse)
  GitHub       ✅  (PicnicSupermarket org)
  Confluence   ✅  (or ⚠️ skipped)
  Slack        ✅  (or ⚠️ skipped)
```

If any ⚠️: note they can fix these later by re-running `/setup`. Then move to Phase 3.

---

## Phase 3 — Skills

**Goal:** Install shared tools from `picnic-analytical-tools`.

### Python + Poetry check

Run: `python3 --version && poetry --version`

- ✅ Both present → continue
- ⚠️ Python missing → "Install Python 3.10+: https://www.python.org/downloads/"
- ⚠️ Poetry missing → "Install Poetry: `curl -sSL https://install.python-poetry.org | python3 -`"

If either ⚠️: print fix instructions and ask whether to continue or skip to Phase 4.

### Skill sync

Check for the `picnic-analytical-tools` repo in this order:
1. `~/Documents/Github/picnic-analytical-tools`
2. `~/picnic-analytical-tools`
3. `~/Documents/picnic-analytical-tools`

- ✅ Found → run `git pull` in that directory, then continue
- ⚠️ Not found → clone automatically:
  ```bash
  gh repo clone PicnicSupermarket/picnic-analytical-tools ~/Documents/Github/picnic-analytical-tools
  ```
  - ⚠️ Access denied → "Check with your team lead. Re-run `/setup` after access is granted." Skip to Phase 4.

Once present and up to date, run the `sync-picnic-skills` skill.

- ✅ Success → print the list of installed skills
- ⚠️ Error → "Sync failed. Re-run `/setup` later to retry."

Move to Phase 4.

---

## Phase 4 — Done

Print the final summary:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Setup complete for <full_name> (<username_prefix>)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Working directory
  Always open Claude Code from ~/picnic-analyst-assistant/
  (CLAUDE.md loads automatically — opens from any other folder won't activate the assistant)

Commands     ✅  installed to ~/.claude/commands/
Identity     ✅  user-config.md written

Connections
  <status line per tool from Phase 2>

Skills
  <sync status + list from Phase 3>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Next steps:
  → Run /onboard-knowledge to add your first skill files (do this before /perform)
  → Add your first task to TASKS.md
  → Run /perform to start it
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Hard rules

- **Never overwrite `user-config.md` without explicit confirmation** from the user.
- **Never write personal context files without user input** — no templates with fake data.
- **Auto-proceed between phases** unless user input is required or something fails.
  Only stop for: user input (Phase 1, optional tool selection), failures, or restart notices.
- **Setup is resumable** — re-running `/setup` re-checks each phase and skips completed steps.
- **If any phase fails or is skipped**, note it in the summary and continue where possible.
