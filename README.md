# Picnic Analyst Assistant

A Claude Code framework that gives you a personal **Analyst Assistant** — a multi-agent system that knows your data, your conventions, and your communication style.

For setup and usage documentation, see the [Analyst Assistant Reference Handbook](https://picnic.atlassian.net/wiki/spaces/Commercial/pages/6270025746).

---

## What it can do

| Task | Command |
|------|---------|
| Run a one-off Snowflake query and explain the result | `/analyst` |
| Draft a Confluence page or Slack message | `/writer` |
| Run a full task: query → Slack update → summary | `/perform` |
| Teach the system your SQL conventions or Slack style | `/onboard-knowledge` |
| Review the system or add new agents and skills | `/architect` |

The more you invest in teaching the assistant your conventions, the higher the quality of its output.

---

## Prerequisites

- **Claude Code + VS Code** — [Claude Code installation guide](https://picnic.atlassian.net/wiki/spaces/ADP/pages/4627071060)
- **GitHub, Snowflake, and dev tooling** — [Developer security setup](https://picnic.atlassian.net/wiki/spaces/DEVSEC/pages/5599363243)

---

## Installation

```bash
gh repo clone maartendejong-teampicnic/picnic-analyst-assistant ~/picnic-analyst-assistant
mkdir -p ~/.claude/commands/ && cp ~/picnic-analyst-assistant/commands/setup.md ~/.claude/commands/
cd ~/picnic-analyst-assistant && code .
```

Then in the Claude Code panel: `/setup`

> Always open VS Code from `~/picnic-analyst-assistant/` — Claude Code loads the analyst context automatically from that folder's `CLAUDE.md`.

---

## File layout

```
picnic-analyst-assistant/
│
├── CLAUDE.md                          # orchestration rules (loaded automatically)
├── CONTEXT.md                         # blank task context template (used by orchestrator)
├── TASKS.md                           # your task list (gitignored)
│
├── agents/                            # agent onboarding files
│   ├── ORCHESTRATOR.md
│   ├── ANALYST.md
│   ├── ENGINEER.md
│   └── WRITER.md
│
├── knowledge/                         # skill files loaded by agents at runtime
│   ├── INDEX.yaml                     # routing: which agent loads which file
│   ├── agent-common.md                # shared agent instructions (direct mode, startup, rules)
│   └── sql-snowflake.md               # shared Snowflake SQL conventions (example format)
│
├── patterns/                          # meta-maintenance
│   ├── architect.md
│   ├── onboard-knowledge.md
│   └── setup.md
│
├── tools/                             # shared tool integrations
│   └── costs/
│
├── commands/                          # slash command definitions
│
├── context/                           # personal project context (gitignored)
│   └── <project>.md                   # your context files (style, usuals, etc.)
│
├── tasks-output/                             # task outputs, one folder per task (gitignored)
│   └── <task-id>/
│       ├── context.md
│       ├── summary.md
│       └── <role>.md
│
├── direct-output/                            # direct-mode outputs (gitignored)
│   └── <username>-YYYYMMDD-HHMM-<role>-<slug>/
│       └── output.md
│
├── user-config.md.example             # identity configuration template
└── user-config.md                     # your identity: name, prefix, email, team (gitignored)
```

---

## File tiers

The repo uses a three-tier model — know which tier a file is in before editing it.

### Framework — do not edit
These files define how the system works. Edits here affect everyone who clones the repo.

| File / folder | Purpose |
|---------------|---------|
| `CLAUDE.md` | Orchestration rules, loaded automatically by Claude Code |
| `README.md` | This file |
| `CONTEXT.md` | Blank task context template used by the orchestrator |
| `user-config.md.example` | Identity template for new users |
| `.gitignore` | Allowlist that controls what is committed |
| `patterns/` | Setup, architect, and onboard-knowledge patterns |

### Working files — yours to customise
These are committed as starting points so you get them on `git clone`. After `/setup` runs,
they are marked skip-worktree — any edits you make stay local and will never be committed.

| File / folder | Purpose |
|---------------|---------|
| `agents/` | Agent onboarding files — adapt prompts and rules to your workflow |
| `commands/` | Slash command definitions — add, rename, or remove commands |
| `knowledge/` | Skill files — extend INDEX.yaml and add your own via `/onboard-knowledge` |
| `tools/costs/` | Claude API cost tracking tool |

### Private — never committed
Created locally; gitignored.

| File / folder | Purpose |
|---------------|---------|
| `user-config.md` | Your identity (name, email, username prefix, team) |
| `TASKS.md` | Your task list |
| `tasks-output/` | Per-task output folders |
| `direct-output/` | Direct-mode output folders |
| `context/` | Personal project context files (communication style, project notes, etc.) |

---

## Onboarding a colleague

Share the [Analyst Assistant Reference Handbook](https://picnic.atlassian.net/wiki/spaces/Commercial/pages/6270025746) — everything they need is there.
