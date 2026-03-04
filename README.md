# Picnic Analyst Assistant

A Claude Code framework to create your own **Analyst Assistant** that combines shared resources with tailored knowledge about your own domain. 

---

## How it works

The system is built around a multi-agent pipeline coordinated by an **orchestrator**.

The ORCHESTRATOR reads your task brief, decomposes the task into phases, and routes each phase to a specialist agent that produces structured output the next agent builds on. Each agent is trained on one specifc domain of your work and loads only the knowledge files relevant to that domain. As a result, each agent enters a task with focused context, producing high quality results.

The more precisely an agent knows your conventions and context, the more consistent and effective its output. If you want conclusions of Snowflake queries instead of tables, teach the ANALYST. If your dbt models always use specific joins, teach the ENGINEER. If your slide titles should state the finding instead of the topic, tell the PRESENTER. If your Slack messages should be based on your own way of writing, train the WRITER. The more you invest in this 'onboarding' process, the higher the quality of your **Analyst Assistant** will be.

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

### 3. Open VS Code from the repo and run `/setup`

```bash
cd ~/picnic-analyst-assistant && code .
```

This reopens VS Code from inside the repo — **this is the activation step**. Claude Code loads the analyst assistant automatically from `CLAUDE.md` in whatever folder VS Code is opened from. You must open from `~/picnic-analyst-assistant/` every time you want to use the assistant.

Then in the Claude Code panel, type `/setup`. The setup guide handles the rest.

---

### Going forward

> ⚠️ **Always open VS Code from `~/picnic-analyst-assistant/`** to activate the analyst assistant:
> ```bash
> cd ~/picnic-analyst-assistant && code .
> ```
> If you open VS Code from your home directory or another folder, the analyst context will not load.

---

## Onboarding your knowledge

The knowledge onboarding step is what makes the assistant useful for your specific workflow. Without it, agents have no context about your tables, your coding conventions, your Slack style, or your experiment methodology.

Run `/onboard-knowledge` once per skill area:

```
/onboard-knowledge
```

It guides you through:

1. Describing the skill area (e.g. "Snowflake SQL conventions", "dbt model patterns", "Slack communication style")
2. A structured intake — you answer questions about your conventions
3. The system drafts a `knowledge/<skill>.md` file and registers it in `INDEX.yaml`
4. You review and approve before anything is written

The `knowledge/` folder ships with example files that show the expected format. Typical first skills to onboard: SQL conventions, dbt patterns, Slack style, experiment methodology.

To review or evolve the knowledge base and overall system structure, use `/architect`.

---

## File layout

```
picnic-analyst-assistant/
│
├── CLAUDE.md                          # orchestration rules
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

Share this README. They follow the Getting started steps from the top — prerequisites, clone, bootstrap, `/setup`.
