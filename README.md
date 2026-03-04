# Picnic Analyst Assistant

A Claude Code framework to create your own **Analyst Assistant** that combines shared resources with tailored knowledge about your own domain. 

---

## How it works

The system is built around a multi-agent pipeline coordinated by an **orchestrator**.

The ORCHESTRATOR reads your task brief, decomposes the task into phases, and routes each phase to a specialist agent that produces structured output the next agent builds on. Each agent is trained on one specifc domain of your work and loads only the knowledge files relevant to that domain. As a result, each agent enters a task with focused context, producing high quality results.

The more precisely an agent knows your conventions and context, the more consistent and effective its output. If you want conclusions of Snowflake queries instead of tables, teach the ANALYST. If your dbt models always use specific joins, teach the ENGINEER. If your slide titles should state the finding instead of the topic, tell the PRESENTER. If your Slack messages should be based on your own way of writing, train the WRITER. The more you invest in this 'onboarding' process, the higher the quality of your **Analyst Assistant** will be.

---

## Setup

### 1. Clone and install

The repo must live at a fixed path — `~/CLAUDE.md` imports the orchestration rules from there.

```bash
git clone <repo-url> ~/picnic-analyst-assistant
mkdir -p ~/.claude/commands/
cp ~/picnic-analyst-assistant/commands/* ~/.claude/commands/
```

### 2. Run `/setup` in Claude Code

```
/setup
```

The setup guide walks you through everything: configuring your identity, verifying MCP connections (Snowflake, GitHub, Confluence, Slack), creating personal context files, and syncing shared skills. About 10 minutes total.

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

1. Share the repo URL
2. They clone to `~/picnic-analyst-assistant` and copy the commands (step 1 above)
3. They run `/setup` in Claude Code — everything else is guided
