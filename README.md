# Picnic Analyst Assistant

A Claude Code framework that lets you create _specialist agents_ combining shared Picnic resources with personalized knowledge. 

For setup, usage, and onboarding: see the [Analyst Assistant Reference Handbook](https://picnic.atlassian.net/wiki/spaces/Commercial/pages/6270025746).

---

## File layout

```
picnic-analyst-assistant/
│
├── CLAUDE.md                          # loaded automatically; sets Claude's behaviour for this project
├── CONTEXT.md                         # blank template the orchestrator copies per task
├── TASKS.md                           # your personal task list (gitignored)
│
├── agents/                            # one file per specialist agent; customise to your workflow
│   ├── ORCHESTRATOR.md                # decomposes tasks, routes to specialists, gates actions
│   ├── ANALYST.md                     # writes SQL, analyses data, designs experiments
│   ├── ENGINEER.md                    # builds dbt models, creates GitHub PRs
│   ├── WRITER.md                      # drafts Slack messages and Confluence pages
│   └── index.yaml                     # agent registry: tells ORCHESTRATOR what agents exist
│
├── knowledge/                         # skill files; agents load these at startup via INDEX.yaml
│   ├── INDEX.yaml                     # routing table: which agent loads which file
│   ├── agent-common.md                # shared rules and startup sequence for every agent
│   └── sql-snowflake.md               # example skill file: Snowflake SQL conventions
│
├── patterns/                          # guided flows; each one backs a slash command
│   ├── setup.md                       # backs /setup    — onboard a new user
│   ├── architect.md                   # backs /architect — review or change the system
│   ├── onboard-knowledge.md           # backs /onboard-knowledge — teach the system a new skill
│   └── add-agent.md                   # backs /add-agent — add a new specialist agent
│
├── commands/                          # slash command entry points; one file per /command
│   ├── perform.md / tasks.md          # task orchestration
│   ├── analyst.md / engineer.md / writer.md   # direct agent access
│   ├── setup.md / architect.md / onboard-knowledge.md / add-agent.md   # guided flows
│   └── costs.md                       # Claude API cost tracking
│
├── tools/costs/                       # cost tracking tool (Python)
│
├── tasks-output/                      # one folder per /perform task (gitignored)
│   └── <task-id>/
│       ├── context.md                 # coordination file: plan, assignments, status
│       ├── <role>.md                  # each agent writes its output here
│       └── summary.md                 # synthesis; presence marks the task complete
│
├── direct-output/                     # output from direct agent commands (gitignored)
│   └── <username>-YYYYMMDD-HHMM-<role>-<slug>/
│       └── output.md
│
├── user-config.md.example             # copy this to user-config.md and fill in your details
└── user-config.md                     # your identity: name, email, username prefix, team (gitignored)
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

