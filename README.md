# Picnic Analyst Assistant

A Claude Code framework that lets you create _specialist agents_ combining shared Picnic resources with personalized knowledge. 

For setup, usage, and onboarding: see the [Analyst Assistant Reference Handbook](https://picnic.atlassian.net/wiki/spaces/Commercial/pages/6270025746).

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
│   └── index.yaml                     # agent registry (ORCHESTRATOR reads at startup)
│
├── knowledge/                         # skill files loaded by agents at runtime
│   ├── INDEX.yaml                     # routing: which agent loads which file
│   ├── agent-common.md                # shared agent instructions (direct mode, startup, rules)
│   └── sql-snowflake.md               # shared Snowflake SQL conventions (example format)
│
├── patterns/                          # meta-maintenance patterns (backed by /setup, /architect, etc.)
│   ├── setup.md
│   ├── architect.md
│   ├── onboard-knowledge.md
│   └── add-agent.md
│
├── commands/                          # slash command definitions (one file per /command)
│   ├── perform.md
│   ├── analyst.md / engineer.md / writer.md
│   ├── tasks.md / add-agent.md / costs.md
│   └── setup.md / architect.md / onboard-knowledge.md
│
├── tools/                             # shared tool integrations
│   └── costs/                         # Claude API cost tracking tool
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

