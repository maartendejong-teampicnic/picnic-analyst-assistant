# Picnic Analyst Assistant

A Claude Code framework for analyst work at Picnic Technologies.
Covers data analysis, A/B experimentation, dbt PRs, Slack/Confluence communication, and slide decks —
orchestrated across specialised agents with approval gates before any irreversible action.

---

## Setup (new user)

### 1. Clone this repo

```bash
git clone <repo-url> ~/Documents/Claude/picnic-analyst-assistant
```

### 2. Install slash commands

```bash
cp ~/Documents/Claude/picnic-analyst-assistant/commands/* ~/.claude/commands/
```

### 3. Run `/setup` in Claude Code

```
/setup
```

The setup guide walks you through all configuration steps automatically:
configuring your identity, verifying MCP connections, creating personal context files,
and syncing shared skills. Takes about 10 minutes.

### 4. Onboard your knowledge

The `knowledge/` folder ships with one example file. Before `/perform` is useful,
add skill files for your workflow (SQL conventions, dbt, Slack templates, etc.):

```
/onboard-knowledge
```

Run once per skill area — typically 5–10 minutes each.

---

## Daily use

```
/perform    → orchestrated task (multi-agent, full workflow)
/analyst    → SQL analysis, A/B design
/engineer   → dbt PRs, CI validation
/writer     → Slack, Confluence, PR copy
/presenter  → PowerPoint slide decks
/designer   → Excalidraw diagrams
```

```
/architect          → review or change the system structure
/onboard-knowledge  → add a new skill file
/gdrive             → browse Google Drive for context
/costs              → check Claude API cost breakdown
```

---

## File layout

```
picnic-analyst-assistant/
├── CLAUDE.md              ← orchestration rules (shared)
├── README.md              ← this file (shared)
├── user-config.md.example ← copy → user-config.md and fill in
├── user-config.md         ← YOUR identity: name, prefix, email, team (gitignored)
├── TASKS.md               ← YOUR task list (gitignored)
├── agents/                ← 6 agent onboarding files (shared)
├── commands/              ← slash command wrappers (copy to ~/.claude/commands/)
├── knowledge/             ← skill files + INDEX.yaml (shared)
├── patterns/              ← architect.md, onboard-knowledge.md, setup.md (shared)
├── skills/                ← gdrive, slides, costs (shared)
├── context/
│   ├── picnic-business.md ← shared Picnic vocabulary (shared)
│   ├── communication-style.md ← YOUR style guide (gitignored)
│   └── <project>.md       ← YOUR project context (gitignored)
├── tasks/                 ← task output folders (gitignored)
└── direct/                ← direct mode output folders (gitignored)
```

**Shared** = committed to the repo, same for everyone.
**Personal / gitignored** = your private configuration, never committed.

---

## Shared vs. personal

| What | Shared | Personal |
|------|--------|----------|
| Agent logic, skill files, patterns | ✅ | |
| Picnic business vocabulary | ✅ | |
| Your identity (username, email) | | ✅ `user-config.md` |
| Your task list | | ✅ `TASKS.md` |
| Your communication style | | ✅ `context/communication-style.md` |
| Your project context | | ✅ `context/<project>.md` |
| Task and direct output folders | | ✅ `tasks/`, `direct/` |

---

## How it works

```
~/CLAUDE.md
  └── @import → picnic-analyst-assistant/CLAUDE.md   (rules + hard constraints)

~/.claude/commands/*.md                              (slash commands)
  └── thin wrappers → picnic-analyst-assistant/agents/ and patterns/

picnic-analyst-assistant/user-config.md              (read by agents at startup)
  └── username_prefix → used in task IDs and direct/ output folder names
```

---

## Onboarding a colleague

1. Share the repo URL
2. They clone it and run: `cp ~/Documents/Claude/picnic-analyst-assistant/commands/* ~/.claude/commands/`
3. They run `/setup` in Claude Code — everything else is guided
