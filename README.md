# Analyst Assistant @ Picnic

A framework for building a personal *Picnic Analyst Assistant* in Claude Code.
The repository provides the agent architecture, orchestration logic, and onboarding
tooling. Domain knowledge — SQL conventions, dbt workflow, Slack templates, and so on —
is not included and must be added by each analyst using `/onboard-knowledge`
before the system is operational.

---

## Prerequisites

- [Claude Code](https://docs.anthropic.com/claude-code) installed and working
- Python + [Poetry](https://python-poetry.org/) (for local skills)
- `picnic-analytical-tools` repo cloned at `~/Documents/Github/picnic-analytical-tools`
  (provides shared skills: Snowflake, Google Sheets, Slack, etc.)

---

## Setup (new user)

### 1. Clone this repo

```bash
git clone <repo-url> ~/Documents/Claude/analysistant
```

### 2. Configure `~/CLAUDE.md`

Create or edit `~/CLAUDE.md` so it contains exactly:

```
@Documents/Claude/analysistant/CLAUDE.md
```

This single line is your entry point — Claude reads it at every session start.

### 3. Copy command wrappers

```bash
cp ~/Documents/Claude/analysistant/commands/* ~/.claude/commands/
```

This installs all slash commands (`/perform`, `/analyst`, `/engineer`, etc.).

### 4. Run `/setup`

Start a Claude Code session and run:

```
/setup
```

The setup guide walks you through:
- **Phase 1** — Identity: creates `user-config.md` with your name and username prefix
- **Phase 2** — MCP check: verifies Snowflake, Confluence, and Slack connections
- **Phase 3** — Personal context: creates communication style + project context files
- **Phase 4** — Shared skills: syncs tools from `picnic-analytical-tools`
- **Phase 5** — Verification: confirms everything is working

### 5. Onboard your knowledge

The `knowledge/` folder ships with one example file (`sql-snowflake.md`).
Before `/perform` is useful, add skill files for your actual workflow:

```
/onboard-knowledge
```

Run it once per skill area (SQL conventions, dbt PR workflow, Slack templates, etc.).
Each run walks you through intake → draft → write — typically 5–10 minutes per skill.

### 6. Add your first task

Edit `~/Documents/Claude/analysistant/TASKS.md` (created by `/setup`):

```markdown
## Active
- [ ] [SQL] Adoption analysis for my feature — Q1 2026
```

Then run `/perform` to start it.

---

## Daily use

### Start a task
```
/perform
```
The orchestrator reads `TASKS.md`, generates a task ID using your username prefix,
plans the work, and routes it to the right specialists.

### Direct mode (skip the orchestrator)
```
/analyst   → SQL analysis, A/B design
/engineer  → dbt PRs, CI validation
/writer    → Slack, Confluence, PR copy
/presenter → PowerPoint slide decks
/designer  → Excalidraw diagrams
```

### Other commands
```
/architect         → review or change the system structure
/onboard-knowledge → add a new skill file to knowledge/
/gdrive            → browse Google Drive for context
/costs             → check Claude API cost breakdown
```

---

## File layout

```
analysistant/
├── CLAUDE.md              ← orchestration rules (shared)
├── README.md              ← this file (shared)
├── user-config.md.example ← copy → user-config.md (personal, gitignored)
├── user-config.md         ← YOUR identity: name, prefix, email, team (gitignored)
├── TASKS.md               ← YOUR task list (gitignored)
├── agents/                ← 6 agent onboarding files (shared)
├── commands/              ← slash command wrappers to copy to ~/.claude/commands/ (shared)
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
**Personal / gitignored** = your private configuration; never committed.

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
  └── @import → analysistant/CLAUDE.md   (rules + hard constraints)

~/.claude/commands/*.md                  (slash commands)
  └── thin wrappers → analysistant/agents/ and analysistant/patterns/

analysistant/user-config.md              (read by agents at startup)
  └── username_prefix → used in task IDs and direct/ output folder names
```

---

## Onboarding a colleague

1. Share the repo URL
2. They clone it to `~/Documents/Claude/analysistant/`
3. They set up `~/CLAUDE.md` (single @import line)
4. They copy `commands/*` to `~/.claude/commands/`
5. They run `/setup` — everything else is guided

No manual file editing required.
