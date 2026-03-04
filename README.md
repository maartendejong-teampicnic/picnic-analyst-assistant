# Picnic Analyst Assistant

A Claude Code framework that gives you a personal **Analyst Assistant** — a multi-agent system that knows your data, your conventions, and your communication style.

---

## What it can do

| Task | Command |
|------|---------|
| Run a one-off Snowflake query and explain the result | `/analyst` |
| Draft a Confluence page or Slack message | `/writer` |
| Build a slide deck from query results | `/perform` |
| Run a full task: query → Slack update → summary | `/perform` |
| Teach the system your SQL conventions or Slack style | `/onboard-knowledge` |
| Review the system or add new agents and skills | `/architect` |

The more you invest in teaching the assistant your conventions, the higher the quality of its output.

---

## How it works

The system is built around a multi-agent pipeline coordinated by an **orchestrator**.

The ORCHESTRATOR reads your task brief, decomposes the task into phases, and routes each phase to a specialist agent that produces structured output the next agent builds on. Each agent is trained on one specific domain of your work and loads only the knowledge files relevant to that domain. As a result, each agent enters a task with focused context, producing high quality results.

Six specialist agents are available: **ANALYST** (SQL, metrics, A/B testing), **ENGINEER** (dbt models, GitHub PRs), **WRITER** (Slack, Confluence), **PRESENTER** (PowerPoint), and **DESIGNER** (Excalidraw diagrams).

---

## Prerequisites

The following must already be installed before continuing:

- **Claude Code + VS Code** — [Claude Code installation guide](https://picnic.atlassian.net/wiki/spaces/ADP/pages/4627071060)
- **GitHub, Snowflake, and dev tooling** — [Developer security setup](https://picnic.atlassian.net/wiki/spaces/DEVSEC/pages/5599363243)

---

## Getting started

### 1. Open a VS Code terminal

From any WSL terminal, type `code .` to open VS Code connected to WSL. Then open a terminal inside VS Code: **Terminal → New Terminal**.

### 2. Clone the repo and copy the entry point

```bash
gh repo clone maartendejong-teampicnic/picnic-analyst-assistant ~/picnic-analyst-assistant
mkdir -p ~/.claude/commands/ && cp ~/picnic-analyst-assistant/commands/setup.md ~/.claude/commands/
```

### 3. Open VS Code from the repo

```bash
cd ~/picnic-analyst-assistant && code .
```

This reopens VS Code from inside the repo — **this is the activation step**. Claude Code loads `CLAUDE.md` automatically from whichever folder VS Code is opened from. You must always open from `~/picnic-analyst-assistant/` to activate the assistant.

Then in the Claude Code panel, type `/setup`. The setup guide handles Phase 0–3 automatically.

> **Going forward:** always open VS Code from `~/picnic-analyst-assistant/`:
> ```bash
> cd ~/picnic-analyst-assistant && code .
> ```
> Opening from your home directory or any other folder will not load the analyst context.

---

## After setup: your first session

Once setup is complete, the assistant is installed but not yet personalised. Follow these steps in order:

**1. Onboard your knowledge**
Run `/onboard-knowledge` once per skill area. Start with the skills most relevant to your work:
```
/onboard-knowledge Snowflake SQL conventions
/onboard-knowledge dbt model patterns
/onboard-knowledge Slack communication style
```

**2. Add your first task**
Open `TASKS.md` and add a task under `## Active`:
```markdown
## Active
- Write a query to show last week's IPD trend by market
```

**3. Run the task**
```
/perform
```

The orchestrator plans the task, shows you the steps, and asks for approval before executing.

---

## Onboarding your knowledge

This is the most important step after setup. Without knowledge files, agents produce generic output. With them, agents know your exact table names, your coding conventions, your Slack tone, and your experiment methodology.

Run `/onboard-knowledge` and describe a skill area:
```
/onboard-knowledge
```

It guides you through:
1. Describing the skill area (e.g. "Snowflake SQL conventions", "dbt model patterns", "Slack style")
2. A structured intake — you answer questions about your conventions
3. The system drafts a `knowledge/<skill>.md` file and registers it in `INDEX.yaml`
4. You review and approve before anything is written

The `knowledge/` folder ships with example files that show the expected format.

To review or evolve the system structure, use `/architect`.

---

## File layout

```
picnic-analyst-assistant/
│
├── CLAUDE.md                          # orchestration rules (loaded automatically)
├── README.md
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
│   └── <skill>.md
│
├── patterns/                          # meta-maintenance
│   ├── architect.md
│   ├── onboard-knowledge.md
│   └── setup.md
│
├── tools/                             # tool integrations (shared)
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
| Your project context | `context/<project>.md` | personal |
| Task and direct output | `tasks/`, `direct/` | personal |

---

## Onboarding a colleague

Share this README. They follow the Getting started steps from the top — prerequisites, clone, bootstrap, `/setup`, then `/onboard-knowledge` for their first skill area.
