# Picnic Analyst Assistant

A Claude Code framework to create your own **Analyst Assistant** that combines shared resources with tailored knowledge about your own domain. 

---

## How it works

The system is built around a multi-agent pipeline coordinated by an **orchestrator**.

The ORCHESTRATOR reads your task brief, decomposes the task into phases, and routes each phase to a specialist agent that produces structured output the next agent builds on. Each agent is trained on one specifc domain of your work and loads only the knowledge files relevant to that domain. Agents build on each other's work. For example, the ANALYST writes a Snowflake query for a new metric. The ENGINEER creates a turns the query into a DBT model, creates ticket and PR using the debrief of the ANALYST. The WRITER sends a Slack message to a colleague asking to review the PR. Once merged, the ANALYST edits the dashboard sheet to add the new metric in the correct format. As a result, each agent enters a task with focused context, producing high quality results.

The more precisely an agent knows your conventions and context, the more consistent and effective its output. <CLAUDE WRITE: stress the importance of the onboarding flow. State that it starts of knowing nothing, and it is up to you to learn it to work using your conventions. However, shared resources let it automatically read e.g. the datawarehouse catalog or repository conventions. Hence, it is capable, but needs to be steered based on your specific conventions. 

<CLAUDE REPHRASE but keep the structure the same. Name a enticing example skill for each agent>. If you want to have the ANALYST state it's findings in a specific way, tell it so. If your edge-models are from the same context, learn it the ENGINEER. If you want the title of your slides to be the conclusion, tell the PRESENTER. If you write your slack messages in a certain way, learn it to the WRITER. The more time you spent onboarding your **Analyst Assitant** the better results it will give (perhaps more funny phrasing as if it were a real person onboarding). 

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
├── skills/                            # tool integrations
│   ├── gdrive/
│   ├── slides/
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
