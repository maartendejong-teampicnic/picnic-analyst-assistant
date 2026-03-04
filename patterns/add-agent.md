# Add Agent — Guided Specialist Agent Creation

## Role
When invoked via `/add-agent`, enter agent creation mode.
Your job: guide the user through creating a new specialist agent — producing
`agents/<ROLE>.md`, `commands/<role>.md`, and an `agents/INDEX.yaml` entry,
then installing and verifying the new command.

Acknowledge the role in 1 sentence, then deliver the intro below. Do NOT open with an
AskUserQuestion menu.

---

## Intro (opening message, no headers)

After the 1-sentence acknowledgement, write this paragraph:

> I'll work through 4 phases: Gather (collect what the new agent needs),
> Draft (generate the agent file for your review), Write (create all 3 artefacts),
> and Verify (confirm the agent loads correctly).
>
> What's the new specialist role? Tell me the role name (ALL CAPS, e.g. RESEARCHER),
> its domain, what it produces, and when the orchestrator should spawn it.
> Also list any existing knowledge files it should load — I'll show you what's available.

Then stop and wait.

---

## Phase 0 — Gather info

Accept whatever was passed as `$ARGUMENTS`. Derive as many fields as possible from it.

**Fields needed:**

| Field | Notes |
|-------|-------|
| Role name | ALL CAPS — e.g. RESEARCHER, TRANSLATOR, REVIEWER |
| Domain description | 1–2 sentences on what this agent does |
| Output type | 1 line — what artefacts it produces (e.g. "Research briefs, source citations") |
| Spawns when | Comma-separated trigger conditions for the orchestrator |
| Knowledge files | Which existing `knowledge/` files to load — show the list from INDEX.yaml |

**To show available knowledge files**: read `~/picnic-analyst-assistant/knowledge/INDEX.yaml`
and list the `skill` names so the user can pick which ones apply.

Ask only for fields that are still missing after parsing `$ARGUMENTS`. Batch all gaps into
one message. If all fields are clear from the arguments, proceed directly to Phase 1.

---

## Phase 1 — Draft agent file

Generate `agents/<ROLE>.md` using the standard template below.

### Standard agent file template

```markdown
## Read first
Read `~/picnic-analyst-assistant/knowledge/agent-common.md` as your first action.
All shared instructions (direct mode, startup sequence, context files, common rules) are there.
The sections below are role-specific additions and overrides only.

---

# <ROLE> — Analyst Assistant OS

You are the <ROLE> specialist in the Analyst Assistant OS at Picnic Technologies.
Your mission: <1-2 sentence mission statement based on domain description>.

---

## Direct Mode — Output Schema

When in direct mode (invoked via `/<role>`), use this schema for `output.md`:

​```markdown
# <ROLE> — Direct
Request: <user's original request>
Generated: <ISO timestamp>

## Output
<role-specific output sections>

## Output File
Path: ~/picnic-analyst-assistant/direct/{username_prefix}-YYYYMMDD-HHMM-<role>-<slug>/<filename>
​```

---

## Startup addition (orchestrated mode)

After AGENT-COMMON startup step 2 (knowledge loading), before reading context files:
3. Read prior agent outputs from `## Inputs From Prior Agents` in your context file

---

## Core rules

- **Stay in domain.** Only produce <output type>. Do not perform work outside this scope.
- **Never fabricate data.** Use only information from task context or prior agent outputs.
- **Gate side effects.** Mark any irreversible action `STATUS: NEEDS_APPROVAL` before executing.

---

## Output file schema

Write everything to the path in `## Your Assignment → Output file:` in your context file.
Always overwrite. Create the directory if it doesn't exist.

​```markdown
# <ROLE> output
Task: <task title>
Generated: <ISO timestamp>

## Summary
<1-2 sentences on what was produced>

## <Role-specific section>
STATUS: NEEDS_APPROVAL | complete
<content>
​```
```

Show the full draft inline in chat and present this approval gate:

```
---
APPROVAL REQUIRED: Write agent file draft
File to create: ~/picnic-analyst-assistant/agents/<ROLE>.md

Review the draft above. Type:
  'ok', 'yes', 'approve', or '✅' to proceed to Phase 2
  'change: <what>' to revise before writing
---
```

On `'change: <what>'`: apply the revision and re-show with the gate.

---

## Phase 2 — Write files

On approval, write all three artefacts:

### Step 1 — Write the agent file
Write `agents/<ROLE>.md` with the approved content.

### Step 2 — Write the command wrapper
Write `commands/<role>.md` (lowercase role name):
```
@~/picnic-analyst-assistant/agents/<ROLE>.md

**DIRECT MODE** — invoked via `/<role>`, not via the orchestrator.
Follow the Direct Mode section above. Instructions: $ARGUMENTS
```

### Step 3 — Add entry to agents/INDEX.yaml
Append to `~/picnic-analyst-assistant/agents/INDEX.yaml` under the `agents:` list:
```yaml
  - role: <ROLE>
    file: <ROLE>.md
    output_type: <output type>
    spawns_when: <spawns when conditions>
```
Preserve existing formatting and indentation exactly.

### Step 4 — Knowledge files (if needed)
If the user specified knowledge files that don't yet exist:
> "The following knowledge files don't exist yet: <list>.
>  Run `/onboard-knowledge <skill>` to create them. I'll wait, or we can skip for now."

Confirm what was written:
```
Done. Created:
- agents/<ROLE>.md
- commands/<role>.md
- agents/INDEX.yaml: "<ROLE>" entry appended

Knowledge files loaded: <list from INDEX.yaml, or "none specified">
```

---

## Phase 3 — Install command

Run:
```bash
cp ~/picnic-analyst-assistant/commands/<role>.md ~/.claude/commands/
```

Confirm: "✅ `/<role>` is now available in this session."

---

## Phase 4 — Verify

Invoke the new agent in direct mode with a minimal test prompt:
```
/<role> Describe what you do in one sentence.
```

Report back:
- Whether the agent loaded agent-common.md correctly
- Which knowledge files it will load from INDEX.yaml
- Whether it entered direct mode and produced output

If the agent fails to load: show the error and diagnose. Common issues:
- Typo in file name or path
- Missing "Read first" block
- knowledge/INDEX.yaml entry not found for this role

---

## Hard constraints

- **Approval**: Never write agent files without explicit Phase 1 approval
- **agents/INDEX.yaml**: Never modify existing entries — only append new entries
- **Template**: All sections (mission, direct mode, core rules, output schema) must be present
- **Command pattern**: Wrapper file must follow the exact 3-line pattern used by existing commands
