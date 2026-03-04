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
│   ├── WRITER.md
│   ├── PRESENTER.md
│   └── DESIGNER.md
│
├── knowledge/                         # skill files loaded by agents at runtime
│   ├── INDEX.yaml                     # routing: which agent loads which file
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
├── context/                           # reference context loaded by agents
│   ├── picnic-business.md             # Picnic vocabulary (shared)
│   └── <project>.md                   # your project context (gitignored)
│
├── tasks/                             # task outputs, one folder per task (gitignored)
│   └── <task-id>/
│       ├── context.md
│       ├── summary.md
│       └── <role>.md
│
├── direct/                            # direct-mode outputs (gitignored)
│   └── <username>-YYYYMMDD-HHMM-<role>-<slug>/
│       └── output.md
│
├── user-config.md.example             # identity configuration template
└── user-config.md                     # your identity: name, prefix, email, team (gitignored)
```

**Shared** — committed to the repo, the same for every team member.
**Gitignored** — your private configuration and outputs, never committed.

---

## Shared vs. personal

| What | Where | Shared |
|------|-------|--------|
| Agent logic, skill files, patterns | `agents/`, `knowledge/`, `patterns/` | ✅ |
| Picnic business vocabulary | `context/picnic-business.md` | ✅ |
| Your identity (name, prefix, email) | `user-config.md` | personal |
| Your task list | `TASKS.md` | personal |
| Your knowledge files | `knowledge/<skill>.md` (except `sql-snowflake.md`) | personal |
| Your project context | `context/<project>.md` | personal |
| Task and direct output | `tasks/`, `direct/` | personal |

---

## Onboarding a colleague

Share the [Analyst Assistant Reference Handbook](https://picnic.atlassian.net/wiki/spaces/Commercial/pages/6270025746) — everything they need is there.
