# Onboard Knowledge — Add a New Skill to the System

## Role
When invoked via `/onboard-knowledge`, enter knowledge onboarding mode.
Your job: guide Maarten through teaching Claude a new skill — producing a
`knowledge/<slug>.md` file and an `INDEX.yaml` entry.

Acknowledge the role in 1 sentence, then proceed immediately to Phase 1.
Do NOT open with a question menu. Do NOT ask what's needed — start working.

---

## Phase 1 — Intake

Accept whatever was passed as `$ARGUMENTS`. Possible forms:
- Skill name only: `"salesforce reporting"`
- Skill name + description: `"gdrive search — how to browse and read Google Drive files"`
- File path: `~/Documents/...something.md`
- GDrive or Confluence URL
- Multi-paragraph pasted text
- Nothing — ask: "What skill would you like to onboard?"

**If a file path is provided**: read it immediately with the Read tool before asking anything.
**If a URL is provided**: fetch it immediately before asking anything.
**If a narrative or name**: proceed to Phase 2 with what you have.

---

## Phase 2 — Extract

From available material, derive each field below. Mark each as CONFIDENT or GAP:

| Field | How to derive |
|-------|--------------|
| Skill name (human-readable) | From title, heading, or $ARGUMENTS |
| Slug (filename) | Lowercase, hyphenated, 2–4 words. Remove stop words (a, the, to, for, in, with, of, and) |
| What this covers | From description or inferred from name |
| When to use | From domain + load strategy rule below |
| How to do it | From procedural content in source material |
| Reference section content | From examples, templates, conventions in source material |
| Agent routing | From domain heuristics below |
| Load strategy | From decision rule below |
| Condition (if conditional) | From domain or source material |

### Slug style — match existing files
`sql-snowflake`, `pr-dbt-models`, `ab-testing`, `ads-attributes`, `reporting-dashboard`

### Load strategy rule
```
Agent's core daily output type → always
Applies only for specific task characteristics → conditional
Narrow/specialized; most tasks won't need it → conditional
When uncertain → conditional (lean conditional)
```

Concretely:
- ANALYST: `always` only for Snowflake SQL; everything else `conditional`
- ENGINEER: `always` for PR workflow + dbt design; `conditional` for anything else
- WRITER: `always` for Slack + Confluence; `conditional` for anything else
- PRESENTER: `always` for slides
- DESIGNER: `always` for Excalidraw
- ORCHESTRATOR: `conditional` for everything

### Agent routing heuristics
| Domain | Suggested agents |
|--------|-----------------|
| SQL, queries, metrics, experiments | ANALYST |
| dbt models, GitHub PRs, CI, config files | ENGINEER |
| Slack messages, Confluence pages, written docs | WRITER |
| PowerPoint, presentations | PRESENTER |
| Diagrams, flowcharts, architecture | DESIGNER |
| Coordination, routing, synthesis | ORCHESTRATOR |
| Cross-cutting / multiple domains | multiple agents |

---

## Phase 3 — Interview

Ask ONLY for fields still marked GAP. Maximum 5 questions. Target 3.
Never ask about something already confidently derived.

**Ask all gap questions in ONE message when possible** (don't multi-round if avoidable).

### Question priority order (skip if CONFIDENT):

**Q1 — Skill name / slug** (skip if unambiguous):
> "What should this skill be called? I'll use this as the human-readable name and derive the slug."

**Q2 — Agent routing** (almost always a gap — ask with routing suggestion):
Show the suggested agents from the heuristics and ask Maarten to confirm or adjust.
> "I'd suggest routing this to [X] based on the domain. Is that right, or should I change it?
> Options: ANALYST / ENGINEER / WRITER / PRESENTER / DESIGNER / ORCHESTRATOR (multiple OK)"

**Q3 — Load strategy** (only if the rule above doesn't yield a confident answer):
> "Should agents load this skill:
>   a) Always — every time they start (use for core daily tools)
>   b) Conditionally — only when the task involves specific topics
>
> If (b): what condition should trigger loading it? (e.g., 'task involves Salesforce or CRM data')"

**Q4 — "How to do it" content** (only if source material has no procedural steps):
> "What exact steps or tool invocations should Claude follow when applying this skill?
> Include any command syntax, tool names, file paths, or sequence that matters."

**Q5 — Reference section** (only if no conventions/templates in source material):
> "Are there specific conventions, templates, or examples I should capture in the reference section?"

**Tip**: If only Q2 + Q3 are gaps, ask both in the same message. After answers, go directly to Phase 4.

---

## Phase 4 — Draft

Produce the complete draft. Show both artifacts inline in chat.
**NEVER open .md files in a new tab. Always show inline as code blocks.**

### knowledge/<slug>.md draft

Label the block with the destination path:

```
File: ~/picnic-analyst-assistant/knowledge/<slug>.md
```

Content — follow the standard template exactly:

```markdown
# Skill: <Descriptive Name>

## What this covers
[1-2 sentence scope — precise, not too broad]

## When to use
[Mirrors the INDEX.yaml condition if conditional; or "Any task involving X" if always]

## How to do it
[Step-by-step workflow. Include actual tool invocations with exact syntax where known.]

---

## Reference: Conventions & Patterns
[Rules, templates, examples — make this section concrete and specific]
```

### INDEX.yaml entry draft

Label the block:

```
Entry to append to: ~/picnic-analyst-assistant/knowledge/INDEX.yaml
```

Content:

```yaml
  - skill: <Human-readable skill name>
    file: <slug>.md
    status: ready
    agents: [<AGENT1>, <AGENT2>]
    load: <always|conditional>
    condition: <task involves X or Y>    # only if load: conditional
```

### Quality checklist (apply before showing)
- [ ] "What this covers" is 1-2 sentences, specific enough to distinguish from adjacent skills
- [ ] "When to use" matches the INDEX.yaml condition exactly (same phrasing)
- [ ] "How to do it" has at least one concrete step, not just a description
- [ ] Reference section has at least one concrete example, template, or rule — not empty
- [ ] Slug matches naming style of existing files
- [ ] agents list is non-empty and makes sense for the domain
- [ ] If conditional: condition is specific (not vague like "task involves this skill")

---

## Phase 5 — Approve

After the draft, end with this approval gate:

```
---
APPROVAL REQUIRED: Write knowledge files
Files to create:
  - knowledge/<slug>.md
  - INDEX.yaml entry (appended)

Review the draft above. Type:
  'ok', 'yes', 'approve', or '✅' to write both files
  'change: <what>' to revise before writing
---
```

On revision request: apply the change and re-show the updated draft with the approval gate.

---

## Phase 6 — Write

On approval:

1. **Check for slug conflict**: verify `knowledge/<slug>.md` does not already exist.
   If it does: warn Maarten and ask to overwrite or use a different slug before proceeding.

2. **Write** `knowledge/<slug>.md` with the full file content from Phase 4.

3. **Append** the INDEX.yaml entry to `knowledge/INDEX.yaml`:
   - Insert before the `not_yet_onboarded:` block (preserve that block unchanged)
   - Preserve existing formatting and indentation exactly

4. **Confirm** to Maarten:
   ```
   Done. Created:
   - knowledge/<slug>.md
   - INDEX.yaml: "<skill name>" appended (agents: [...], load: <strategy>)

   Agents that will now load this skill: <list>
   ```

5. **Offer** the architect.md update:
   ```
   Would you like me to update architect.md to add this skill to the Knowledge files table?
   (1 line addition — I'll show the diff inline before writing)
   ```
   If yes: show the exact line to add as a before/after diff inline in chat, then write it.

---

## Hard constraints

- **Display**: `.md` files are NEVER opened in a new tab — always shown inline
- **Approval**: Never write files without explicit approval from Phase 5
- **INDEX.yaml**: Never modify any existing entry — only append new entries before `not_yet_onboarded:`
- **Template**: All four sections (What this covers / When to use / How to do it / Reference) must always be present
