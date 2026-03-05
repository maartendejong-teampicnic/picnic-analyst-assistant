# SETUP — Analyst Assistant Onboarding

You are running the guided setup for the Analyst Assistant at Picnic.
Your job: walk a new user through bootstrap, identity, MCP connections, and skill installation.

Acknowledge the role in 1–2 sentences, then immediately run resume detection below.
Do not ask for permission to start.

---

## Resume detection (run before anything else, before the welcome message)

Check state silently before deciding where to start:

1. Does `./user-config.md` exist? (path relative to the picnic-analyst-assistant folder)
2. Read `~/.claude/settings.json` — is `SNOWFLAKE_TOKEN` set and non-empty?

**Choose a path based on what's found:**

**A — Fresh install** (user-config.md does NOT exist):
Print the welcome message below, then show the pre-flight block, then run Phase 0 → 4 in full.

**B — Resuming mid-setup** (user-config.md exists and SNOWFLAKE_TOKEN is non-empty):
Do NOT print the welcome message or pre-flight block. Print instead:
```
Resuming setup — Phases 0–1 already complete. Picking up from Phase 2 (Connections).
```
Skip Phases 0 and 1. Go directly to Phase 2 and process **every tool in sequence**:
- For each tool already configured: run its verification, show the ✅ wow output, then ask
  "Ready to continue to [next tool]?" before moving on.
- For each tool NOT yet configured: walk through its setup steps as normal.
This ensures you never skip a tool that was missed in a previous session.

**C — Partial setup** (user-config.md exists but SNOWFLAKE_TOKEN is empty or settings.json is missing):
Do NOT print the welcome message. Show the pre-flight block, then print:
```
Resuming setup — Phase 1 already complete. Picking up from Phase 2 (Connections).
```
Run Phase 0 silently (it is idempotent — no user input, no repeated output). Skip Phase 1.
Go to Phase 2 and process every tool in sequence as described in Path B above.

---

## Welcome message (print only on fresh install — path A above)

```
Welcome to the Picnic Analyst Assistant setup.

I'll walk you through 4 short phases:

  Phase 0 — Install        Set up commands and protect your personal files  (~10s, automatic)
  Phase 1 — Identity       Your name, email, and task prefix                (~1 min)
  Phase 2 — Connections    Snowflake, Atlassian, GitHub, and optional tools  (5–10 min)
  Phase 3 — Skills         Sync shared tools from the tools repo            (~1 min)

Let's go.
```

---

## Pre-flight block (print on path A and C — NOT on path B)

Print this block after the welcome message (path A) or resume message (path C), before running Phase 0:

```
─────────────────────────────────────────
For a smoother experience, I can pre-approve all tools
needed for setup so you won't be prompted for each action.

  → Enable auto-approve for setup tools? (y/n)
    Yes = adds specific tool approvals to settings.json
          (takes effect after the restart in Phase 2)
    No  = keeps default mode (you'll be prompted per action)

Type your choice (y/n), then press Enter to start.
─────────────────────────────────────────
```

Wait for the user to respond before continuing.

If the user answered **y**: immediately write (or update) `~/.claude/settings.json` to set:
```json
"permissions": {
  "defaultMode": "acceptEdits",
  "allowedTools": [
    "Bash", "Read", "Write", "Edit", "Glob", "Grep",
    "WebFetch", "WebSearch",
    "mcp__snowflake__read_query",
    "mcp__snowflake__list_databases",
    "mcp__snowflake__list_schemas",
    "mcp__snowflake__list_tables",
    "mcp__confluence__confluence_search",
    "mcp__confluence__confluence_get_page",
    "mcp__confluence__confluence_create_page",
    "mcp__confluence__confluence_update_page",
    "mcp__confluence__jira_get_issue",
    "mcp__confluence__jira_search_issues",
    "mcp__confluence__jira_create_issue",
    "mcp__confluence__jira_update_issue"
  ]
}
```
If the file does not yet exist, create it with just this block for now — Phase 2 will add `mcpServers`.
If it already exists, merge these values into the existing `permissions` block.
Confirm: `✅ Tool approvals saved — these take effect after the restart in Phase 2.`

If the user answered **n** (or anything else): proceed without changing permissions.

---

## Phase 0 — Install

**Fully automatic — no user input needed. Run all steps, then move to Phase 1.**

### 1. Install commands

```bash
cp ./commands/*.md ~/.claude/commands/
```

List the installed files. Print: `✅ All commands installed.`

### 2. TASKS.md

Check if `./TASKS.md` exists in the current directory. If not, create it silently:

```markdown
# Tasks

## Active

## Done
```

### 4. Entry point check

Verify that `./CLAUDE.md` exists in the current directory (the picnic-analyst-assistant folder).
- ✅ Exists → nothing to do.
- ⚠️ Missing → create it with the following content:

```markdown
# Analyst Assistant @ Picnic

You are an analyst assistant at Picnic Technologies (grocery delivery service).
You help with the full range of analytical work: data analysis, SQL queries, experiments,
communication (Slack, slides) and documentation (Confluence, slides).

**User identity** is stored in `~/picnic-analyst-assistant/user-config.md`. Agents read it at startup to parameterize task IDs and output paths.
New users: copy `user-config.md.example` → `user-config.md` and fill in your details,
or run `/setup` for guided onboarding.
```

Do NOT touch `~/CLAUDE.md`. If the user has one, it contains their own personal instructions for other Claude sessions and must be left as-is.

Print: `✅ Phase 0 complete.` then ask: "Ready to set up your identity? (Phase 1)"
Wait for any confirmation before continuing.

---

## Phase 1 — Identity

**Goal:** Create `~/picnic-analyst-assistant/user-config.md` with the user's identity.

Ask in one message:
> "What's your full name and Picnic email?
> And which team are you on? (e.g. Consumer - Shopping - Usuals)
>
> Example: Maarten de Jong · maarten.dejong@teampicnic.com · Consumer - Shopping - Usuals"

From the email, derive the username prefix automatically:
- Logic: first char of first name + lastname, all lowercase, no spaces or dots
- `maarten.dejong@teampicnic.com` → `mdejong`

In the same reply or a follow-up, show the derived prefix and confirm:
> "Username prefix: `mdejong` — looks good? Type 'y' to confirm, or type a different one."

Check if `./user-config.md` already exists. If it does, show the current
contents and ask: "Overwrite with new values?" Only proceed if they confirm.
(Note: this prompt is only reached on a fresh install — resume paths skip Phase 1 entirely.)

Write the file:
```markdown
# User Config
username_prefix: <prefix>
full_name: <Full Name>
email: <email>
team: <Team Name>
```

Print: `✅ Identity saved.` then ask: "Ready to set up connections? (Phase 2)"
Wait for any confirmation before continuing.

---

## Phase 2 — Connections

**Goal:** Configure MCP connections. Snowflake and, Atlassian and Github are required. Slack is optional.

### What are MCPs?

MCPs (Model Context Protocol servers) let Claude Code call external systems — databases, wikis,
messaging tools — directly during a session. Each server lives in `~/.claude/settings.json`
under `mcpServers`. GitHub uses the `gh` CLI instead.

After any change to `settings.json`, Claude Code must be restarted for changes to take effect.
`/setup` is resumable — re-running it skips steps already complete.

### Pre-check: settings.json

Note: if the user answered **y** to auto-approve in the pre-flight block, permissions were already
written to `settings.json` before Phase 0. No need to set them again here.

Check if `~/.claude/settings.json` exists:
- ✅ Exists → read current `mcpServers` and continue.
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

For each tool below: if already configured, run the personalized **verification** of the connection. If a connection for a REQUIRED tool has not been made or is missing, walk through setting up the connection.

---

### Required: Snowflake

**Check:** Is `SNOWFLAKE_TOKEN` set and non-empty in `mcpServers.snowflake.env`?

**If not configured:**
1. Open a browser → log into your Snowflake account
2. Click your avatar (bottom left) → **Settings**
3. Go to **Authentication** → **Programmatic Access Tokens** → **Generate new token**
4. Name it `claude-code`, set expiry to maximum (1 year) and **grant access to all your roles**
5. **Copy the token immediately** — it is shown only once
6. Paste the token here

When you have the token, update `~/.claude/settings.json`:
- Set `SNOWFLAKE_USER` to their email from Phase 1, converted to **UPPERCASE**
  (e.g. `firstname.lastname@teampicnic.com` → `FIRSTNAME.LASTNAME@TEAMPICNIC.COM`)
- Set `SNOWFLAKE_TOKEN` to the pasted token

**Verification** (run after configuring, or if already configured):
Run via the `snowflake-query` skill:
```sql
SELECT
  CURRENT_USER() AS you,
  CURRENT_ROLE() AS role,
  CURRENT_WAREHOUSE() AS warehouse,
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES) AS tables_accessible,
  (SELECT COUNT(*) FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY_BY_USER(
    USER_NAME => CURRENT_USER(),
    END_TIME_RANGE_START => DATEADD(week, -1, CURRENT_TIMESTAMP())
  ))) AS queries_past_week
```

- ✅ Returns a row → print the wow output.

  Extract the user's first name from `user-config.md` `full_name` field (Phase 1 has already
  written this file, so it is always available here).

  ```
  ⚡ Snowflake connected
     Welcome back, <First Name>!
     Role: ANALYST · Warehouse: ANALYSIS
     Tables accessible: 1,471
     Queries run this week: 42
  ```

  (Use actual values from the query result, formatted with thousands separators.)

- ⚠️ Error → "Token may be expired or `SNOWFLAKE_USER` is not all-caps. Regenerate the PAT
  in Snowflake UI if needed, update `settings.json`, then restart Claude Code."

Note: PAT tokens expire (max 1 year). When Snowflake queries stop working, regenerate and update `SNOWFLAKE_TOKEN`.

Ask: "Ready to continue to Atlassian?" and wait for confirmation before proceeding.

---

### Required: Atlassian

> **Important:** Use the `mcp-atlassian` Python package configured in `settings.json` — do NOT
> use `claude mcp add` for Atlassian. The `claude mcp add` approach only supports reading Confluence
> and Jira; it does not support creating Jira tickets.

**Check:** Are `CONFLUENCE_API_TOKEN` and `JIRA_API_TOKEN` both set and non-empty in
`mcpServers.confluence.env` in `settings.json`?

**If not configured:**

First, silently install the package (no user input needed):
```bash
pip install mcp-atlassian
```

Then ask the user for their API token:
> "Open a browser → https://id.atlassian.com/manage-profile/security
> Go to **API tokens** → **Create API token** → name it `claude-code` → copy immediately.
> Paste the token here when you have it."

`CONFLUENCE_USERNAME` and `JIRA_USERNAME` are the Picnic email from Phase 1 — no need to ask again.

Add to `mcpServers` in `settings.json` (the same API token works for both Confluence and Jira):
```json
"confluence": {
  "command": "mcp-atlassian",
  "args": [],
  "env": {
    "CONFLUENCE_URL": "https://picnic.atlassian.net/wiki",
    "CONFLUENCE_USERNAME": "<email from Phase 1>",
    "CONFLUENCE_API_TOKEN": "<pasted token>",
    "JIRA_URL": "https://picnic.atlassian.net",
    "JIRA_USERNAME": "<email from Phase 1>",
    "JIRA_API_TOKEN": "<pasted token>"
  }
}
```

**Verification** (run after configuring, or if already configured):

> **Important:** Only run verification if the `confluence` MCP server is already loaded in
> this session. It loads at startup — if `settings.json` was just updated, a restart is needed
> first (handled by the restart block below). Do NOT attempt bash diagnostics to probe the
> MCP process; this leads to a dead end.

Step 1 — Confluence: use the `confluence` MCP to search for pages the user contributed to:
```
CQL: contributor = currentUser() ORDER BY lastmodified DESC LIMIT 5
```
If no results (new employee), fall back to: `space = "ANALYTICS" ORDER BY lastmodified DESC LIMIT 5`

Step 2 — Jira: create a test ticket using the `confluence` MCP:
- Find a Jira project the user has access to (search recent issues assigned to them, or list
  available projects and pick a team backlog or personal project).
- Create an issue with:
  - Summary: `Claude Code setup test — <Full Name>`
  - Description: `This ticket was automatically created during Claude Code setup to verify the Jira MCP connection. Safe to close.`
  - Issue type: `Task` (fall back to whatever types are available if Task does not exist)

Print wow output:
```
⚡ Atlassian connected (Confluence + Jira)
   Your recent contributions:
     • <page title 1>
     • <page title 2>
     • <page title 3>

   Test Jira ticket created: <PROJECT-123>
   https://picnic.atlassian.net/browse/<PROJECT-123>
   (Safe to close — just proves the connection works)
```
(Use actual page titles and the real ticket key + URL from the create response.)

- ⚠️ MCP not loaded ("server not found" error) → The `confluence` MCP is configured but not
  active in this session. This means settings.json was updated but Claude wasn't restarted yet.
  Print: "Atlassian is configured — restart Claude Code and run /setup to complete verification."
  Do NOT attempt bash diagnostics. Move on.
- ⚠️ API error (auth failed, token wrong) → Check that `mcp-atlassian` is installed
  (`pip install mcp-atlassian`) and that both Confluence and Jira env vars in `settings.json`
  are correct. Do NOT use `claude mcp add atlassian` — that approach does not support Jira
  ticket creation.

Ask: "Ready to continue to GitHub?" and wait for confirmation before proceeding.

---

### Required: GitHub

**Goal:** Ensure `gh` CLI is installed and authenticated.

Run: `gh auth status`
- ✅ Logged in → skip to verification below
- ⚠️ Not authenticated → run this command automatically (no user action needed before the browser):
  ```bash
  gh auth login --hostname github.com --git-protocol https --web
  ```
  This opens a browser tab. Tell the user:
  > "A browser tab just opened — sign in with your Picnic GitHub account and authorise the app.
  > Come back here when the browser says you're done."
  Wait for the user to confirm they completed the browser step, then continue automatically.

**Verification** (run automatically after auth, or if already logged in):
Run both commands in sequence — no user action needed:
```bash
gh api orgs/PicnicSupermarket --jq '.login'
gh pr list --repo PicnicSupermarket/picnic-dbt-models --author @me --state all --limit 3 --json title,state
```

Print wow output:
```
⚡ GitHub connected
   Organisation: PicnicSupermarket — access confirmed

   Your recent PRs in picnic-dbt-models:
     • <actual PR title> (<state>)
     • <actual PR title> (<state>)

```
(Use actual values from the commands. If no personal PRs found, skip that section gracefully.)

Note: `gh` credentials are stored by the CLI — no entry needed in `settings.json`.

---

### Optional tools

Ask once:
> "Which optional tools would you like to set up?
>   A — Slack (read channels, send messages)
>   B — Skip for now
>
> You can always re-run /setup to add them later."

Work through each selected tool. Skip anything the user does not select.

---

### Optional: Slack

**Check:** Is `SLACK_MCP_XOXP_TOKEN` set and non-empty in `mcpServers.slack.env`?

**If not configured:**

Walk the user through creating their own Slack app step by step. Print the following instructions and ask them to follow along, pausing where indicated:

```
Here's how to create your Slack app — follow each step, then come back here.

1. Open: https://api.slack.com/apps/
   Click "Create New App" → choose "From scratch"

2. Give it a name (e.g. "Claude Code - <Your Name>") and select the
   Picnic workspace from the dropdown → click "Create App"

3. In the left navigation bar, scroll down and click "OAuth & Permissions"

4. Scroll down to "Scopes" → under "User Token Scopes", click "Add an OAuth Scope"
   and add each of the following one by one:
     • channels:history
     • channels:read
     • chat:write
     • lists:read

5. Scroll back up to the top of the page and click "Request to Workspace Install"
   → follow the prompts and submit the request

6. ⚠️  A Picnic workspace admin needs to approve your app before you can get a token.
   Ping someone in the #analytics-engineering or #it-support channel to approve it.
   Come back here once it's approved.

7. After approval: return to your app at https://api.slack.com/apps/,
   go to "OAuth & Permissions", and copy the "User OAuth Token" (starts with xoxp-)

Paste the token here when you have it.
```

Wait for the user to paste the token, then add to `mcpServers` in `settings.json`:
```json
"slack": {
  "command": "slack-mcp-server",
  "args": [],
  "env": {
    "SLACK_MCP_XOXP_TOKEN": "<pasted token>"
  }
}
```

Print: `⚡ Slack configured — token saved. You'll see it in action when you use /writer.`

---

### After all MCP configs are written — one restart

**Do not restart after each individual MCP.** Instead: configure every MCP that needs setup (Snowflake, Atlassian, GitHub, optional Slack) in sequence, writing all entries to `settings.json`. Only after ALL configurations are written, print this block prominently and **stop**:

```
⚡ Restart required — one time
   All MCP configurations have been written to settings.json.
   MCP servers only load at startup, so one restart is needed
   before any of the newly configured connections will work.

   Steps:
     1. Open a new terminal and start Claude Code from the
        picnic-analyst-assistant folder
     2. Run /setup — it will verify all connections and continue
        to Phase 3

   (If you already completed some of these steps before and
   are returning to verify, the connections phase runs fast.)
```

Do not proceed to the connection verifications or Phase 3. The user must restart first.

**How to detect whether to restart or verify:**
- If any MCP was added or updated to `settings.json` in this session → show restart block and stop.
- If all MCPs were already in `settings.json` when Phase 2 started AND the MCP server responds to tool calls → run verifications directly (no restart needed).

---

### Connections summary (print before moving on)

```
Connections:
  Snowflake    ✅
  Atlassian    ✅
  GitHub       ✅
  Slack        ✅  (or ⚠️ skipped)
```

If any ⚠️: note they can fix these later by re-running `/setup`.

Ask: "Ready to sync skills? (Phase 3)" and wait for confirmation before proceeding.

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

Once present and up to date, sync the skills:

Read `<repo-path>/claude-code/skills/sync-picnic-skills/SKILL.md`
(where `<repo-path>` is the picnic-analytical-tools location found above)
and follow the instructions in that file. This installs all shared skills by
creating symlinks from the repo into `~/.claude/skills/`.

- ✅ Success → print the list of installed skills
- ⚠️ Error → "Sync failed. Re-run `/setup` later to retry."

Move to Phase 4.

---

## Phase 4 — Done

### Git cleanup (automatic — no user input)

Untrack all repo files except README and the setup command so users can freely edit,
add, or delete any file without git ever flagging it. The files stay on disk — only
git's tracking changes. This is purely local and never pushed.

Run silently:
```bash
# Untrack everything except README + setup files
git rm --cached -r --quiet .

# Re-track only the bootstrapping files
git add README.md commands/setup.md patterns/setup.md .gitignore

# Overwrite .gitignore locally so untracked files are properly ignored
cat > .gitignore << 'EOF'
# Only README and the setup command are tracked.
# Everything else is yours to add, edit, or delete freely.
*
!.gitignore
!README.md
!commands/
!commands/setup.md
!patterns/
!patterns/setup.md
EOF

git add .gitignore

# Commit locally (never pushed — keeps git status permanently clean)
git commit -m "Local: untrack all personal files (setup complete)"
```

- ✅ Success → `git status` is now permanently clean. Any file can be edited, added, or deleted freely.
- ⚠️ Error → note it and continue; non-critical. Users can still work normally.

Print the final summary:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Setup complete for <full_name> (<username_prefix>)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Working directory
  Always open Claude Code from the picnic-analyst-assistant folder
  CLAUDE.md loads automatically — opening from any other folder enters a
  regular Claude session, without the **Analyst Assistant** context.)

Commands     ✅  installed to ~/.claude/commands/
Identity     ✅  user-config.md written

Connections
  <status line per tool from Phase 2>

Skills
  <sync status + list from Phase 3>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Next steps:
  → Run /onboard-knowledge to add your first personalized knowledge files
  → Run /tasks to add your first task to the TASKS.md file
  → Run /analyst and try out your Snowflake MCP connection
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Hard rules

- **Never overwrite `user-config.md` without explicit confirmation** from the user.
- **Never write personal context files without user input** — no templates with fake data.
- **Always confirm before starting the next phase or the next tool within Phase 2.**
  Any response (including "yes", "ok", Enter) counts as confirmation. Never auto-advance.
- **Setup is resumable** — re-running `/setup` re-checks each phase and skips completed steps.
- **If any phase fails or is skipped**, note it in the summary and continue where possible.
