# SETUP — Analyst Assistant Onboarding

You are running the guided setup for the Analyst Assistant at Picnic.
Your job: walk a new user through bootstrap, identity, MCP connections, skill installation, and verification.

Acknowledge the role in 1–2 sentences, then immediately run resume detection below.
Do not ask for permission to start.

---

## Resume detection (run before anything else, before the welcome message)

Check each step in order. Start executing from the first step that is not yet complete.

| Step | Done if… |
|------|----------|
| 0a — Commands installed | `~/.claude/commands/perform.md` exists |
| 0b — TASKS.md created | `./TASKS.md` exists |
| 0c — CLAUDE.md exists | `./CLAUDE.md` exists |
| 1 — Identity set | `./user-config.md` exists |
| 2a — Snowflake configured | `SNOWFLAKE_TOKEN` is non-empty in `~/.claude/settings.json` |
| 2b — Atlassian configured | `CONFLUENCE_API_TOKEN` is non-empty in `~/.claude/settings.json` |
| 2c — GitHub configured | `gh auth status` returns logged-in |
| 2d — Slack configured | `SLACK_MCP_XOXP_TOKEN` is set in `~/.claude/settings.json` OR `user-config.md` contains `slack_setup: skipped` |
| 3 — Skills synced | `~/.claude/skills/picnic-query-snowflake` symlink exists |
| 4 — Connections verified | Always run if step 3 is done (verification is read-only and quick) |

After checking all steps:
- If all steps are complete → jump straight to Phase 4 (re-verify).
- If any step is complete (i.e. you are not starting from 0a) → print one line:
  `Resuming setup — picking up from step <X>...` then proceed from there.
- If no step is complete → print the welcome message, then the pre-flight block, then start from Phase 0.

**Welcome message and pre-flight block are skipped if any step beyond Phase 0 is already complete.**

---

## Welcome message (print only on fresh install — all steps incomplete)

```
Welcome to the Picnic Analyst Assistant setup.

I'll walk you through 5 short phases:

  Phase 0 — Install        Set up commands                               (~10s, automatic)
  Phase 1 — Identity       Your name, email, and prefix                  (~1 min)
  Phase 2 — Connections    Add tokens for Snowflake, Atlassian, GitHub   (~5 min)
  Phase 3 — Skills         Sync shared Picnic tools                      (~1 min)
  Phase 4 — Verify         Test all connections in one shot              (~2 min)

Let's go.
```

---

## Pre-flight block (print on fresh install only — before Phase 0)

```
─────────────────────────────────────────
For a smoother experience, I can pre-approve all tools
needed for setup so you won't be prompted for each action.

  → Enable auto-approve for setup tools? (y/n)
    Yes = adds specific tool approvals to settings.json
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
If the file does not yet exist, create it with just this block — Phase 2 will add `mcpServers`.
If it already exists, merge these values into the existing `permissions` block.

Print:
```
✅ Permissions saved. They take effect after restarting Claude Code.
   You can restart now for a fully seamless experience, or continue in this
   session (you'll see tool approval prompts until the next restart).
```

Do NOT stop here — let the user continue. Phase 0 and 1 only write files, so approval prompts are minor.

If the user answered **n** (or anything else): proceed without changing permissions.

---

## Phase 0 — Install

**Fully automatic — no user input needed. Run all steps, then move to Phase 1.**

### Step 0a — Install commands

```bash
cp ./commands/*.md ~/.claude/commands/
```

List the installed files. Print: `✅ All commands installed.`

### Step 0b — TASKS.md

Check if `./TASKS.md` exists. If not, create it silently:

```markdown
# Tasks

## Active

## Done
```

### Step 0c — CLAUDE.md

Check if `./CLAUDE.md` exists in the current directory (the picnic-analyst-assistant folder).
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

Do **NOT** touch `~/CLAUDE.md`. If the user has one, it contains their own personal instructions for other Claude sessions and must be left as-is.

Print: `✅ Phase 0 complete.` then ask: "Ready to set up your identity? (Phase 1)"
Wait for any confirmation before continuing.

---

## Phase 1 — Identity

**Goal:** Create `./user-config.md` with the user's identity.

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

Check if `./user-config.md` already exists. If it does, show the current contents and ask:
"Overwrite with new values?" Only proceed if they confirm.
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

**Goal:** Configure all MCP connections. Collect tokens and write `settings.json` only — no verification here.
Verification happens in Phase 4, after the restart and skills sync.

### What are MCPs?

MCPs (Model Context Protocol servers) let Claude Code call external systems — databases, wikis,
messaging tools — directly during a session. Each server lives in `~/.claude/settings.json`
under `mcpServers`. GitHub uses the `gh` CLI instead.

After any change to `settings.json`, Claude Code must be restarted for changes to take effect.
`/setup` is resumable — re-running it skips steps already complete.

### Pre-check: settings.json

Note: if the user answered **y** to auto-approve in the pre-flight block, permissions were already
written to `settings.json`. No need to set them again here.

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

---

### Step 2a — Snowflake (configure only)

**Check:** Is `SNOWFLAKE_TOKEN` set and non-empty in `mcpServers.snowflake.env`?
- ✅ Already configured → skip to the "Ready to continue" prompt below.
- ⚠️ Not configured → follow steps below.

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

Print: `✅ Snowflake token saved.`

Note: PAT tokens expire (max 1 year). When Snowflake queries stop working, regenerate and update `SNOWFLAKE_TOKEN`.

Ask: "Ready to continue to Atlassian?" and wait for confirmation before proceeding.

---

### Step 2b — Atlassian (configure only)

> **Important:** Use the `mcp-atlassian` Python package configured in `settings.json` — do NOT
> use `claude mcp add` for Atlassian. The `claude mcp add` approach only supports reading Confluence
> and Jira; it does not support creating Jira tickets.

**Check:** Is `CONFLUENCE_API_TOKEN` set and non-empty in `mcpServers.confluence.env` in `settings.json`?
- ✅ Already configured → skip to the "Ready to continue" prompt below.
- ⚠️ Not configured → follow steps below.

**If not configured:**

**Step 1 — Install and locate the binary (fully automatic, no user input):**

Run in sequence, stopping at the first success:

```bash
# Attempt 1: standard pip
pip install mcp-atlassian 2>&1
which mcp-atlassian 2>/dev/null
```

If `which mcp-atlassian` returns a path → note it as `<mcp_atlassian_cmd>` and continue.

If not found after attempt 1:
```bash
# Attempt 2: pip3
pip3 install mcp-atlassian 2>&1
which mcp-atlassian 2>/dev/null
```

If still not found after attempt 2:
```bash
# Attempt 3: pip --user (installs to ~/.local/bin)
pip install --user mcp-atlassian 2>&1 || pip3 install --user mcp-atlassian 2>&1
find ~/.local/bin /home/*/.local/bin ~/.pyenv -name "mcp-atlassian" -type f 2>/dev/null | head -3
```

Use the first path returned as `<mcp_atlassian_cmd>`.

If no binary is found after all three attempts:
- Print: `⚠️ Could not install mcp-atlassian — skipping for now. Re-run /setup later to set it up.`
- Skip Atlassian setup entirely and continue to GitHub.

**Step 2 — Ask the user for their API token:**

> "Open a browser → https://id.atlassian.com/manage-profile/security
> Go to **API tokens** → **Create API token** → name it `claude-code` → copy immediately.
> Paste the token here when you have it."

`CONFLUENCE_USERNAME` and `JIRA_USERNAME` are the Picnic email from Phase 1 — no need to ask again.

**Step 3 — Write `settings.json`:**

Use `<mcp_atlassian_cmd>` (the full path if `which` returned one, otherwise `"mcp-atlassian"`)
as the `command` value. Add to `mcpServers` in `settings.json`:

```json
"confluence": {
  "command": "<mcp_atlassian_cmd>",
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

Print: `✅ Atlassian token saved.`

Ask: "Ready to continue to GitHub?" and wait for confirmation before proceeding.

---

### Step 2c — GitHub (configure only)

**Goal:** Ensure `gh` CLI is installed and authenticated.

Run: `gh auth status`
- ✅ Logged in → print `✅ GitHub already authenticated.` and continue.
- ⚠️ Not authenticated → run this command automatically (no user action needed before the browser):
  ```bash
  gh auth login --hostname github.com --git-protocol https --web
  ```
  This opens a browser tab. Tell the user:
  > "A browser tab just opened — sign in with your Picnic GitHub account and authorise the app.
  > Come back here when the browser says you're done."
  Wait for the user to confirm they completed the browser step, then run `gh auth status` to confirm
  success and print: `✅ GitHub authenticated.`

Note: `gh` credentials are stored by the CLI — no entry needed in `settings.json`.

---

### Step 2d — Slack (optional)

Ask once:
> "Would you like to set up Slack? (read channels, send messages)
>   A — Yes, set up Slack now
>   B — Skip for now
>
> You can always re-run /setup to add it later."

If user chooses **B — Skip**: add `slack_setup: skipped` to `./user-config.md` and continue.

**If setting up Slack:**

**Check:** Is `SLACK_MCP_XOXP_TOKEN` set and non-empty in `mcpServers.slack.env`?
- ✅ Already configured → print `✅ Slack already configured.` and continue.
- ⚠️ Not configured → walk the user through creating their own Slack app:

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

Print: `✅ Slack token saved.`

---

### Connections summary + restart

Print the connections summary showing what was configured:

```
Connections configured:
  Snowflake    ✅  (or ⚠️ skipped)
  Atlassian    ✅  (or ⚠️ skipped)
  GitHub       ✅  (or ⚠️ skipped)
  Slack        ✅  (or — skipped by choice)
```

**One restart required.** After writing all configurations to `settings.json`, print this block
prominently and **stop**:

```
⚡ Restart required — one time
   All MCP configurations have been written to settings.json.
   MCP servers only load at startup, so one restart is needed
   before Phase 3 (skills) and Phase 4 (verification) can run.

   Steps:
     1. Open a new terminal and start Claude Code from the
        picnic-analyst-assistant folder
     2. Run /setup — it will sync skills, verify all connections,
        and finish setup

   (Skills and verification run automatically after restart.)
```

Do not proceed to Phase 3 or 4. The user must restart first.

**Exception — skip restart if:**
All MCPs were already in `settings.json` when Phase 2 started (nothing was written in this session)
AND `gh auth status` confirms GitHub is logged in. In that case, continue directly to Phase 3
without printing the restart block.

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

Read `<repo-path>/claude-code/skills/picnic-sync-tools/SKILL.md`
(where `<repo-path>` is the picnic-analytical-tools location found above)
and follow the instructions in that file. This installs all shared skills by
creating symlinks from the repo into `~/.claude/skills/`.

- ✅ Success → print the list of installed skills
- ⚠️ Error → "Sync failed. Re-run `/setup` later to retry."

Move directly to Phase 4 (no confirmation prompt).

---

## Phase 4 — Verify connections

**Goal:** Test all connections in one shot. Run each verification in sequence.

---

### Snowflake verification

Run query 1 (scalar stats) via the `picnic-query-snowflake` skill:
```sql
SELECT
  CURRENT_USER() AS you,
  CURRENT_ROLE() AS role,
  CURRENT_WAREHOUSE() AS warehouse,
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES) AS tables_accessible
```

Run query 2 (recent activity) separately:
```sql
SELECT COUNT(*) AS query_count
FROM TABLE(SNOWFLAKE.INFORMATION_SCHEMA.QUERY_HISTORY(
    END_TIME_RANGE_START => DATEADD(day, -1, CURRENT_TIMESTAMP())))
WHERE QUERY_TYPE = 'SELECT'
```

Combine results. Extract the user's first name from `user-config.md` `full_name` field.

- ✅ Both queries succeed → print wow output:
  ```
  ⚡ Snowflake connected
     Welcome back, <First Name>!
     Role: ANALYST · Warehouse: ANALYSIS
     Tables accessible: 1,471
     SELECT queries yesterday: 42
  ```
  (Use actual values, formatted with thousands separators.)

- ⚠️ Error → "Token may be expired or `SNOWFLAKE_USER` is not all-caps. Regenerate the PAT
  in Snowflake UI if needed, update `settings.json`, then restart Claude Code."

---

### Atlassian verification

> **Important:** Only run if the `confluence` MCP server is loaded in this session.
> It loads at startup — if `settings.json` was updated and Claude was restarted, it should be active.
> Do NOT attempt bash diagnostics to probe the MCP process; this leads to a dead end.

**If Atlassian was skipped in Phase 2** (not in `settings.json`) → skip this section.

**Step 1 — Confluence:** search for pages the user contributed to:
```
CQL: contributor = currentUser() ORDER BY lastmodified DESC LIMIT 5
```
If no results (new employee), fall back to: `space = "ANALYTICS" ORDER BY lastmodified DESC LIMIT 5`

**Step 2 — Jira:** create a test ticket using the `confluence` MCP:
- Find a Jira project the user has access to (search recent issues assigned to them, or list
  available projects and pick a team backlog or personal project).
- Create an issue with:
  - Summary: `Claude Code setup test — <Full Name>`
  - Description: `This ticket was automatically created during Claude Code setup to verify the Jira MCP connection. Safe to close.`
  - Issue type: `Task` (fall back to whatever types are available if Task does not exist)

- ✅ Both succeed → print wow output:
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

- ⚠️ MCP not loaded ("server not found" / "unknown tool" error) → The `confluence` MCP is
  configured but not active in this session. Print:
  "Atlassian is configured — restart Claude Code and run /setup to complete verification."
  Do NOT attempt bash diagnostics. Mark as ⚠️ in the summary and continue.

- ⚠️ API error (401 / auth failed) → Automatically attempt to self-heal:
  1. Re-read `settings.json` and verify `CONFLUENCE_API_TOKEN` is set and non-empty.
  2. Run: `which mcp-atlassian` — if empty, re-run the 3-attempt install from Phase 2 and update
     the `command` field in `settings.json` with the located binary path.
  3. Print the corrected config values (mask the token: show first 8 chars + `...`) and inform:
     "The token or binary path was updated — restarting is needed to pick up the change."
  4. If the error persists, ask the user to re-paste the token:
     "The token may be incorrect. Paste your Atlassian API token again — or skip for now."
     On receipt, update `CONFLUENCE_API_TOKEN` and `JIRA_API_TOKEN` in `settings.json`.
     If the user skips, note Atlassian as ⚠️ in the summary and continue.
  Do NOT use `claude mcp add atlassian` — that approach does not support Jira ticket creation.

---

### GitHub verification

Run both commands in sequence:
```bash
gh api orgs/PicnicSupermarket --jq '.login'
gh pr list --repo PicnicSupermarket/picnic-dbt-models --author @me --state all --limit 3 --json title,state
```

- ✅ Succeeds → print wow output:
  ```
  ⚡ GitHub connected
     Organisation: PicnicSupermarket — access confirmed

     Your recent PRs in picnic-dbt-models:
       • <actual PR title> (<state>)
       • <actual PR title> (<state>)
  ```
  (If no personal PRs found, skip that section gracefully.)

- ⚠️ Error → "Check GitHub auth with `gh auth status` and re-run `/setup`."

---

### Connections verification summary

Print:
```
Connections verified:
  Snowflake    ✅  (or ⚠️ with note)
  Atlassian    ✅  (or ⚠️ with note)
  GitHub       ✅  (or ⚠️ with note)
  Slack        —   (configured — verified in use)
```

If any ⚠️: note they can fix these later by re-running `/setup`.

Move directly to Phase 5.

---

## Phase 5 — Done

### Git cleanup (automatic — no user input)

Untrack all repo files except README and the setup command so users can freely edit,
add, or delete any file without git ever flagging it. The files stay on disk — only
git's tracking changes. This is purely local and never pushed.

> **IMPORTANT:** Run the entire block below as ONE bash command via the Bash tool.
> Do NOT split into separate tool calls. Do NOT use the Write tool for `.gitignore`.
> The heredoc must execute as part of the same shell invocation.

```bash
git rm --cached -r --quiet . && git add README.md commands/setup.md patterns/setup.md .gitignore && cat > .gitignore << 'EOF'
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
git add .gitignore && git commit -m "Local: untrack all personal files (setup complete)"
```

After the commit, run `git status --short` and verify the output is empty (clean).

If `git status` shows untracked files after the commit, the `.gitignore` write failed:
- Run manually via bash:
  ```bash
  printf '*\n!.gitignore\n!README.md\n!commands/\n!commands/setup.md\n!patterns/\n!patterns/setup.md\n' > .gitignore && git add .gitignore && git commit -m "Local: fix .gitignore (setup complete)"
  ```

- ✅ Clean status → `git status` is now permanently clean. Any file can be edited, added, or deleted freely.
- ⚠️ Error → note it and continue; non-critical. Users can still work normally.

---

### Final summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Setup complete for <full_name> (<username_prefix>)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Working directory
  Always open Claude Code from the picnic-analyst-assistant folder.
  CLAUDE.md loads automatically — opening from any other folder enters a
  regular Claude session, without the Analyst Assistant context.

Commands     ✅  installed to ~/.claude/commands/
Identity     ✅  user-config.md written

Connections
  <status line per tool from Phase 4>

Skills
  <sync status + list from Phase 3>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Next steps:
  → Run /onboard-knowledge to add your first personalised knowledge files
  → Run /analyst and try out your Snowflake MCP connection
  → Add tasks to TASKS.md and run /perform to start working
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Hard rules

- **Never overwrite `user-config.md` without explicit confirmation** from the user.
- **Never write personal context files without user input** — no templates with fake data.
- **Always confirm before starting the next phase or the next tool within Phase 2.**
  Any response (including "yes", "ok", Enter) counts as confirmation. Never auto-advance.
  Exception: Phase 3 → Phase 4 transition is automatic (no prompt).
- **Setup is resumable** — re-running `/setup` re-checks each step and skips completed ones.
- **If any phase fails or is skipped**, note it in the summary and continue where possible.
- **Do NOT touch `~/CLAUDE.md`** — it belongs to the user and must never be created, modified, or deleted.
