# Architect — System Review & Maintenance

## Role
When invoked via `/architect`, enter system maintenance mode. Your job is to help
the user review, onboard, or change the fundamental structure and knowledge of the
Analyst Assistant system. This is the meta-layer: not doing Picnic work, but shaping
how the system works.

Acknowledge the role briefly (1–2 sentences), then ask what's needed.

---

## System Map

### File tiers

| Tier | What's in it | Git behaviour |
|------|-------------|---------------|
| **Framework** | `CLAUDE.md`, `CONTEXT.md`, `README.md`, `user-config.md.example`, `.gitignore`, `patterns/` | Committed and tracked — do not edit |
| **Working files** | `agents/`, `commands/`, `agents/index.yaml`, `knowledge/INDEX.yaml`, `knowledge/agent-common.md`, `knowledge/sql-snowflake.md`, `tools/costs/` | Committed as starting points; skip-worktree'd by `/setup` — edit freely |
| **Personal** | `user-config.md`, `TASKS.md`, `tasks-output/`, `direct-output/`, `context/`, `knowledge/<skill>.md` (personal) | Gitignored — never committed |

User identity lives in `user-config.md` (gitignored). Agents read it at startup for
user context (full_name, email, team) — used for authorship in Slack messages, PRs, etc.

---

### Entry points (loaded automatically at startup)
| File | Purpose |
|------|---------|
| `~/Documents/Claude/picnic-analyst-assistant/CLAUDE.md` | Orchestration rules and hard rules — loaded automatically when Claude Code is opened from `~/Documents/Claude/picnic-analyst-assistant/`. Opening from any other folder gives a plain Claude session. |
| `~/.claude/projects/-home-picnic/memory/MEMORY.md` | Auto-memory index (always loaded) |

### Commands (`~/.claude/commands/`)
One `.md` file per command — each is a thin wrapper pointing at an agent or pattern file.
See `commands/` for the current list. Framework commands (setup, architect, onboard-knowledge)
are backed by `patterns/`. Agent commands (perform, analyst, engineer, writer, …) are backed
by `agents/`.

Adding a command: create `commands/<name>.md` with `@~/picnic-analyst-assistant/agents/<ROLE>.md`
and `$ARGUMENTS`. Re-run `cp ./commands/*.md ~/.claude/commands/` to install it.

### Agents (`picnic-analyst-assistant/agents/`)
See `agents/` for the current list. Each agent file defines one specialist role.
All agents share a common preamble: they read `knowledge/agent-common.md` first (via
the "Read first" block at the top of every agent file), then load role-specific knowledge
via `knowledge/INDEX.yaml`.

`agents/index.yaml` is the agent registry — ORCHESTRATOR reads it at startup to discover
available agents and their capabilities. Adding a new agent = adding an entry here.

Adding an agent: see "Add a new specialist agent" runbook below.

### Knowledge files (`picnic-analyst-assistant/knowledge/`) — self-contained skill files, loaded by agents
Routing (which agents load which files) is declared in `INDEX.yaml`. See that file for the full routing map.

**Shared starting points** (committed; skip-worktree'd after `/setup` so edits stay local):

| File | Domain |
|------|--------|
| `INDEX.yaml` | Knowledge routing authority (`agents` + `load` per skill) |
| `agent-common.md` | Shared agent instructions (direct mode, startup, common rules) |
| `sql-snowflake.md` | Snowflake SQL conventions + table patterns |

**Personal** (gitignored — specific to each user's setup, added via `/onboard-knowledge`):

| File | Domain |
|------|--------|
| `sql-calcite.md` | Calcite SQL dialect + virtual table catalogue |
| `pr-dbt-models.md` | PR workflow: dbt-models + store-config |
| `dbt-model-design.md` | dbt model SQL/YAML/MD craft |
| `ab-testing.md` | Experiment methodology, past tests |
| `slack-messages.md` | Slack templates + approval workflow |
| `confluence-pages.md` | Confluence page structure + templates |
| `ads-attributes.md` | ADS procedures + data model |
| `slides-pptx.md` | Slide conventions + tool API |
| `diagrams-excalidraw.md` | Excalidraw agent instructions |
| `reporting-dashboard.md` | Usuals dashboard structure + formulas |

### Context files (`picnic-analyst-assistant/context/`)
All files in `context/` are personal and gitignored — agents skip gracefully if absent.

| File | Domain | Read by |
|------|--------|---------|
| `communication-style.md` | Slack/Confluence style, stakeholder map | WRITER |
| `<project>.md` | Active project context (e.g. usuals-project.md) | ANALYST, WRITER |

### Pattern files (`picnic-analyst-assistant/patterns/`) — architect only
| File | Used by |
|------|---------|
| `setup.md` | `/setup` command — guided new-user onboarding |
| `architect.md` | `/architect` command |
| `onboard-knowledge.md` | `/onboard-knowledge` command |
| `add-agent.md` | `/add-agent` command — guided new specialist agent creation |

### Skills
| Skill | Type | Location |
|-------|------|----------|
| `snowflake-query` | Shared (picnic-analytical-tools) | `~/.claude/skills/` |
| `gsheet` | Shared | `~/.claude/skills/` |
| `send-slack-message` | Shared | `~/.claude/skills/` |
| `read-slack-channel` | Shared | `~/.claude/skills/` |
| `check-teamcity-build` | Shared | `~/.claude/skills/` |
| `sync-picnic-skills` | Shared | `~/.claude/skills/` |
| `ads` | Shared | `~/.claude/skills/` |
| `s3` | Shared | `~/.claude/skills/` |
| `salesforce-query` | Shared | `~/.claude/skills/` |
| `costs` | Shared (picnic-analyst-assistant) | `picnic-analyst-assistant/tools/costs/` |
| `gdrive` | Personal (not in shared repo) | `picnic-analyst-assistant/tools/gdrive/` |
| `slides` | Personal (not in shared repo) | `picnic-analyst-assistant/tools/slides/` |
| `thinkcell` | Personal (not in shared repo) | `picnic-analyst-assistant/tools/slides/` |

### Task & output folders
```
picnic-analyst-assistant/
├── TASKS.md                           ← task list (Active / Done)
├── CONTEXT.md                         ← blank context template
├── tasks-output/<task-id>/                   ← permanent record per task
│   ├── context.md                     ← coordination file (active if no summary.md)
│   ├── analyst.md / engineer.md / …   ← agent outputs (written directly during execution)
│   └── summary.md                     ← synthesis (marks task complete)
└── direct-output/YYYYMMDD-HHMM-<role>-<slug>/
    └── output.md                      ← direct mode output

~/.claude/data/Output/                 ← (legacy; no longer used for agent output)
~/.claude/data/snowflake-query/        ← query files and JSON results
```

---

## System Review Checklist

When asked to "review the system" or "check for issues", work through these:

1. **Commands vs. files** — for each file in `~/.claude/commands/`, verify the target file exists
2. **Routing authority** — check `knowledge/INDEX.yaml` has an entry for every file in `knowledge/`, with `agents` and `load` filled in for all `status: ready` entries
3. **Agent startup sequences** — check each agent reads files that actually exist
4. **Knowledge index** — check `knowledge/INDEX.yaml` has an entry for every file in `knowledge/`
5. **MEMORY.md** — check it accurately references file paths and is not stale
6. **MEMORY.md commands list** — check it matches the actual command files in `~/.claude/commands/`
7. **Stale references** — look for mentions of removed commands, old file paths, old role names

---

## Maintenance Runbooks

### Onboard a new colleague

1. Share the repo URL with the colleague
2. They clone it: `git clone <url> ~/picnic-analyst-assistant/`
3. They copy the setup command: `mkdir -p ~/.claude/commands/ && cp ~/picnic-analyst-assistant/commands/setup.md ~/.claude/commands/`
4. They open Claude Code from `~/Documents/Claude/picnic-analyst-assistant/` and run `/setup` — walks through all phases automatically:
   - Bootstrap → installs all commands, git isolation, TASKS.md
   - Identity → writes `user-config.md`
   - MCP check → Snowflake, GitHub, Confluence (optional), Slack (optional)
   - Shared skills → sync from picnic-analytical-tools
   - Verification → end-to-end test
5. Done. They can run `/perform` immediately.

Note: the analyst context loads via project-level CLAUDE.md — no `~/CLAUDE.md` needed (it must NOT exist).
They must open Claude Code from `~/Documents/Claude/picnic-analyst-assistant/` for analyst work.
Opening from any other folder gives a plain Claude session without analyst context — that's intentional.

Note: personal files (`user-config.md`, `TASKS.md`, `tasks-output/`, `direct-output/`, personal context)
are gitignored and never committed — their data stays private.

---

### Add a new knowledge skill
Use the guided command:
```
/onboard-knowledge <skill name or description>
```
The command walks through intake → extraction → interview → draft → approval → write.

Manual fallback (if needed):
1. Create `knowledge/<skill-name>.md` using the standard template:
   ```markdown
   # Skill: <Descriptive Name>
   ## What this covers
   ## When to use
   ## How to do it
   ## Reference: Conventions & Patterns
   ```
2. Add an entry to `knowledge/INDEX.yaml` with `skill`, `file`, `status: ready`, `agents`, `load`,
   and `condition` (if `load: conditional`) — that's it. No other files need changing.

### Add a new context file
Create `context/<name>.md` — agents read all files in `context/` that exist; nothing else to update.

### Add a new specialist agent
Three steps — nothing else:

1. Create `agents/<ROLE>.md` — copy an existing agent as template.
   Keep the "Read first" block at the top (it loads `knowledge/agent-common.md`).
   Add role-specific direct mode, startup sequence, core rules, and output schema.

2. Create `commands/<role>.md` — copy an existing command wrapper as template.
   Install: `cp commands/<role>.md ~/.claude/commands/`

3. Add one entry to `agents/index.yaml` with `role`, `file`, `output_type`, `spawns_when`.

No other files need updating. ORCHESTRATOR and CONTEXT.md discover agents dynamically.
If the new agent needs knowledge files: follow "Add a new knowledge skill" above,
using the new agent's role name in the `agents` field of `knowledge/INDEX.yaml`.

Tip: use `/add-agent` for a fully guided version of these steps.

### Add a new local tool (Python tool)
1. Create `picnic-analyst-assistant/tools/<name>/` with: `pyproject.toml`, `<name>_tool.py`, `<name>.sh`, `SKILL.md`
2. Run `poetry install` in that directory
3. Optionally create `~/.claude/commands/<name>.md` pointing to the SKILL.md
4. Update MEMORY.md under "Local Skills"
5. Update this file: add to Skills table above

### Sync shared skills (after picnic-analytical-tools update)
```bash
cd ~/Documents/Github/picnic-analytical-tools && git pull
```
Then run `/sync-picnic-skills` to refresh symlinks in `~/.claude/skills/`.

### Renew Snowflake PAT token
1. Snowflake UI → Profile → Programmatic Access Tokens → generate new
2. `~/.claude/settings.json` → replace `SNOWFLAKE_TOKEN`
3. Restart Claude Code; update MEMORY.md MCP status if needed

