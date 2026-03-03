# Architect — System Review & Maintenance

## Role
When invoked via `/architect`, enter system maintenance mode. Your job is to help
the user review, onboard, or change the fundamental structure and knowledge of the
Analyst Assistant system. This is the meta-layer: not doing Picnic work, but shaping
how the system works.

Acknowledge the role briefly (1–2 sentences), then ask what's needed.

---

## System Map

### Shared vs. personal layers

| Layer | What's in it | Git status |
|-------|-------------|------------|
| **Shared** | `CLAUDE.md`, `agents/`, `knowledge/`, `patterns/`, `skills/`, `commands/`, `context/picnic-business.md`, `README.md`, `user-config.md.example`, `.gitignore` | Committed — same for all users |
| **Personal** | `user-config.md`, `TASKS.md`, `CONTEXT.md`, `tasks/`, `direct/`, `context/communication-style.md`, `context/setup-notes.md`, `context/<project>.md` | Gitignored — per-user only |

User identity lives in `user-config.md` (gitignored). Agents read it at startup to
get `username_prefix` for task IDs and `direct/` output folder names.

---

### Entry points (loaded automatically at startup)
| File | Purpose |
|------|---------|
| `~/CLAUDE.md` | Single @import redirect → picnic-analyst-assistant/CLAUDE.md |
| `~/picnic-analyst-assistant/CLAUDE.md` | Orchestration rules and hard rules |
| `~/.claude/projects/-home-picnic/memory/MEMORY.md` | Auto-memory index (always loaded) |

### Commands (`~/.claude/commands/`)
| Command | Backed by | Purpose |
|---------|-----------|---------|
| `/perform` | agents/ORCHESTRATOR.md | Multi-agent task orchestration |
| `/tasks` | reads TASKS.md | Display task list |
| `/analyst` | agents/ANALYST.md | Direct analyst mode |
| `/engineer` | agents/ENGINEER.md | Direct engineer mode |
| `/writer` | agents/WRITER.md | Direct writer mode |
| `/presenter` | agents/PRESENTER.md | Direct presenter mode |
| `/designer` | agents/DESIGNER.md | Direct designer mode |
| `/gdrive` | skills/gdrive/SKILL.md | Google Drive browse/read |
| `/costs` | skills/costs/SKILL.md | Claude API cost breakdown |
| `/excalidraw` | ~/.claude/skills/excalidraw.md | Excalidraw diagram generation |
| `/setup` | patterns/setup.md | Guided onboarding for new users |
| `/architect` | patterns/architect.md | This mode |
| `/onboard-knowledge` | patterns/onboard-knowledge.md | Guided skill onboarding (knowledge/ + INDEX.yaml) |

### Agents (`picnic-analyst-assistant/agents/`)
| Agent | Domain | Reads on startup |
|-------|--------|-----------------|
| ORCHESTRATOR | Coordination, routing | INDEX.yaml (always + conditional for ORCHESTRATOR role) + context files |
| ANALYST | SQL, A/B testing, metrics | INDEX.yaml (always + conditional for ANALYST role) + context/picnic-business.md |
| ENGINEER | dbt, GitHub PRs, Calcite SQL | INDEX.yaml (always + conditional for ENGINEER role) + context/usuals-project.md |
| WRITER | Slack, Confluence, PR copy | INDEX.yaml (always + conditional for WRITER role) + context/communication-style.md |
| PRESENTER | PowerPoint .pptx | INDEX.yaml (always + conditional for PRESENTER role) + context/setup-notes.md |
| DESIGNER | Excalidraw diagrams | INDEX.yaml (always + conditional for DESIGNER role) + ~/.claude/skills/excalidraw.md (hardcoded) |

### Knowledge files (`picnic-analyst-assistant/knowledge/`) — self-contained skill files, loaded by agents
Routing (which agents load which files) is declared in `INDEX.yaml`. See that file for the full routing map.

| File | Domain |
|------|--------|
| `sql-snowflake.md` | Snowflake SQL conventions + table patterns |
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
| `INDEX.yaml` | Knowledge routing authority (`agents` + `load` per skill) |

### Context files (`picnic-analyst-assistant/context/`)
| File | Domain | Read by | Type |
|------|--------|---------|------|
| `picnic-business.md` | Picnic vocabulary, markets, KPIs | ANALYST, ORCHESTRATOR | Shared (committed) |
| `communication-style.md` | Slack/Confluence style, stakeholder map | WRITER | Personal (gitignored) |
| `<project>.md` | Active project context (e.g. usuals-project.md) | ANALYST, WRITER, PRESENTER, DESIGNER | Personal (gitignored) |
| `setup-notes.md` | Setup log, MCP status, tool notes | PRESENTER | Personal (gitignored) |

### Pattern files (`picnic-analyst-assistant/patterns/`) — architect only
| File | Used by |
|------|---------|
| `setup.md` | `/setup` command — guided new-user onboarding |
| `architect.md` | `/architect` command |
| `onboard-knowledge.md` | `/onboard-knowledge` command |

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
| `gdrive` | Local (personal) | `picnic-analyst-assistant/skills/gdrive/` |
| `slides` | Local | `picnic-analyst-assistant/skills/slides/` |
| `thinkcell` | Local | `picnic-analyst-assistant/skills/slides/` |

### Task & output folders
```
picnic-analyst-assistant/
├── TASKS.md                           ← task list (Active / Done)
├── CONTEXT.md                         ← blank context template
├── tasks/<task-id>/                   ← permanent record per task
│   ├── context.md                     ← coordination file (active if no summary.md)
│   ├── analyst.md / engineer.md / …   ← agent outputs (copied at close)
│   └── summary.md                     ← synthesis (marks task complete)
└── direct/{username_prefix}-YYYYMMDD-HHMM-<role>-<slug>/
    └── output.md                      ← direct mode output

~/.claude/data/agents/<task-id>/       ← transient working files (deleted at close)
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
5. **Context files** — check `context/` files are symlinked in `~/.claude/projects/-home-picnic/memory/`
6. **MEMORY.md** — check it accurately references `context/` paths (not old `memory/` paths)
7. **MEMORY.md commands list** — check it matches the actual command files in `~/.claude/commands/`
8. **Stale references** — look for mentions of removed commands, old file paths (`patterns/`, `memory/`), old role names

---

## Maintenance Runbooks

### Onboard a new colleague

1. Share the repo URL with the colleague
2. They clone it: `git clone <url> ~/picnic-analyst-assistant/`
3. They set up `~/CLAUDE.md`: single line `@picnic-analyst-assistant/CLAUDE.md`
4. They create the commands directory and copy wrappers: `mkdir -p ~/.claude/commands/ && cp ~/picnic-analyst-assistant/commands/* ~/.claude/commands/`
5. They run `/setup` in Claude Code — walks through all 5 phases automatically:
   - Identity → writes `user-config.md`
   - MCP check → Snowflake, Confluence, Slack
   - Personal context → communication style, project files, TASKS.md
   - Shared skills → sync from picnic-analytical-tools
   - Verification → end-to-end test
6. Done. They can run `/perform` immediately.

Note: personal files (`user-config.md`, `TASKS.md`, `tasks/`, `direct/`, personal context)
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
1. Create `context/<name>.md` — project/domain reference (not a procedure)
2. Create symlink in `~/.claude/projects/-home-picnic/memory/` pointing to it
3. Add to MEMORY.md under "Domain Memory Files"
4. Add to relevant agents' "Knowledge & context files to read" section
5. Update this file: add to Context files table above

### Add a new specialist agent
1. Create `agents/<ROLE>.md` — use an existing agent as template:
   - Direct Mode section, startup sequence, core rules, workflow, output schema, knowledge/context files
2. Add to ORCHESTRATOR.md: specialist agents table + routing table
3. Create `~/.claude/commands/<role>.md`:
   ```
   @~/picnic-analyst-assistant/agents/<ROLE>.md
   $ARGUMENTS
   ```
4. Update MEMORY.md: add to "Slash Commands" and note in agent list
5. Update this file: add to Commands table and Agents table above

### Add a new local skill (Python tool)
1. Create `picnic-analyst-assistant/skills/<name>/` with: `pyproject.toml`, `<name>_tool.py`, `<name>.sh`, `SKILL.md`
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

### Update Slack Bot token
1. `~/.claude/settings.json` → replace `SLACK_BOT_TOKEN`
2. Ensure scopes include: `chat:write`, `channels:read`, `channels:history`, `lists:read`
3. Restart Claude Code; update MEMORY.md Slack status
