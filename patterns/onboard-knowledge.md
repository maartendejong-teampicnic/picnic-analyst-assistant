# Onboard Knowledge — Add a New Skill to the System

## Role
When invoked via `/onboard-knowledge`, enter knowledge onboarding mode.
Your job: guide the user through teaching Claude a new skill — producing a
`knowledge/<slug>.md` file and an `INDEX.yaml` entry, verified through a live practice test.

Acknowledge the role in 1 sentence, then deliver the intro below. Do NOT open with a menu.

---

## Intro (opening message, no headers)

After the 1-sentence role acknowledgement, write this paragraph:

> I'll work through 5 phases: Intake (gather your material), Extract (derive the skill structure and gap questions), Practice (I'll actually execute the skill using a draft — you evaluate real output), Feedback Loop (we iterate until the output is right), and Implement (write the files). The key difference from a normal review: rather than just approving text, I'll actually use the skill and you can tell me what's wrong with the output.
>
> What skill should I onboard? Share anything you have — example resources are useful but not required. Useful sources include: documentation pages, code files (SQL, dbt models), example outputs (Slack messages, past PRs, analysis write-ups), tool guides, or just a description in your own words.

Then stop and wait.

---

## Phase 1 — Intake

Accept whatever was passed as `$ARGUMENTS`. Possible forms:
- Skill name only: `"salesforce reporting"`
- Skill name + description: `"gdrive search — how to browse and read Google Drive files"`
- File path: `~/Documents/...something.md`
- GDrive or Confluence URL
- Multi-paragraph pasted text
- Nothing — the Intro already asked; proceed with whatever description was given

**If a file path is provided**: read it immediately with the Read tool before asking anything.
**If a URL is provided**: fetch it immediately before asking anything.
**If a narrative or name**: proceed to Phase 2 with what you have.

After reading all provided material, ask once whether additional example resources exist:
- If material is already rich: "Anything else to add?"
- If material is thin (name/description only): "Do you have example outputs or past work I could reference? Not required — I can work from what you've shared."

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
| **Test task** | From test task design table below |

### Slug style examples
`sql-snowflake`, `sql-calcite`, `pr-dbt-models`, `pr-store-config`, `ads-attributes`, `reporting-dashboard`

### Load strategy rule
```
Agent's core daily output type → always
Applies only for specific task characteristics → conditional
Narrow/specialized; most tasks won't need it → conditional
When uncertain → conditional (lean conditional)
```

Concretely:
- ANALYST: `always` only for Snowflake SQL + dashboards; everything else `conditional`
- ENGINEER: `always` for PR workflow + dbt or edge models; `conditional` for anything else
- WRITER: `always` for Slack + Confluence; `conditional` for anything else
- ORCHESTRATOR: `conditional` for everything

### Agent routing heuristics
| Domain | Suggested agents |
|--------|-----------------|
| SQL, Snowflake queries, metrics, experiments, analyses | ANALYST |
| dbt models, GitHub PRs | ENGINEER |
| Slack messages, Confluence pages, written docs | WRITER |
| Coordination, routing, synthesis | ORCHESTRATOR |
| Cross-cutting / multiple domains | multiple agents |

### Test task design table
| Domain | Test type | What to do |
|--------|-----------|------------|
| SQL / Snowflake | Run a real query | Write small query on most relevant table; run via `snowflake-query` |
| dbt model design | Design a model skeleton | Draft `.sql` + `.yml` stub for a realistic model; show it (don't run) |
| PR workflow | Walk steps | Narrate exact steps for a hypothetical PR with a real branch/ticket name. If user names a real PR, use it |
| Slack messages | Draft a message | Draft a realistic example for the most common message type in the skill |
| Confluence pages | Draft a section | Draft TL;DR + first body section for a realistic page type |
| Reporting / dashboards | Show formula or structure | Produce sample formula or table structure matching the skill's patterns |
| ADS attributes | Read a real attribute | Run `/ads` for a relevant attribute; show output |
| Hard to execute | Dry-run narration | Narrate step-by-step what you would do; name tools you'd call; show any output artifacts |

---

## Phase 2b — Interview

Ask ONLY for fields still marked GAP. Maximum 5 questions. Target 3.
Never ask about something already confidently derived.

**Ask all gap questions in ONE message when possible** (don't multi-round if avoidable).

### Question priority order (skip if CONFIDENT):

**Q1 — Skill name / slug** (skip if unambiguous):
> "What should this skill be called? I'll use this as the human-readable name and derive the slug."

**Q2 — Agent routing** (almost always a gap — ask with routing suggestion):
Show the suggested agents from the heuristics and ask the user to confirm or adjust.
> "I'd suggest routing this to [X] based on the domain. Is that right, or should I change it?
> Options: any agent in agents/ — common ones: ANALYST / ENGINEER / WRITER / ORCHESTRATOR (multiple OK)"

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

**Q_test — Test object** (only if the practice test needs a specific real object the user must supply):
> "For the practice test, I'll [describe test]. Is there a specific [object] I should use, or should I invent a placeholder?"

**Tip**: If only Q2 + Q3 are gaps, ask both in the same message. After answers, go directly to Phase 3.

---

## Phase 3 — Practice

1. **Build the draft knowledge file internally** using the standard template (see Phase 5 for template). Apply the quality checklist. Do NOT show the full draft to the user yet.

2. **Announce the test** with a visible block:
   ```
   ---
   PRACTICE TEST
   Skill: <name>
   Test: <one sentence describing what you're about to do>
   ---
   ```

3. **Execute** using real tools. Show output inline — no paraphrasing, no summarising.

4. End with: "Does this look right? What should I adjust?"

### Fallback — dry-run narration (when the skill cannot be directly executed)
- Announce with `PRACTICE TEST (narration)` and a one-sentence scenario
- Narrate exactly what you'd do: name each tool, show draft artifacts (SQL, messages, model stubs), describe decision branches
- End with: "Does this capture the right approach? What should I adjust?"

---

## Phase 4 — Feedback Loop

On each piece of feedback:

### Step 1 — Map feedback to draft section
| Feedback type | Draft section to update |
|---------------|------------------------|
| Wrong output format | Reference section |
| Missing step | How to do it |
| Wrong tool invocation | How to do it |
| Wrong scope | What this covers / When to use |
| Missing convention | Reference section |

### Step 2 — Show a diff, not the full file
```
DRAFT UPDATE — <section name>
Before: [old lines]
After:  [new lines]
```
If an addition: `Adding: [new content]`

Apply all feedback from a single message in one update block, then run one test.

### Step 3 — Re-execute
Announce with `PRACTICE TEST (iteration N)`. Show output inline. End with: "Better? Anything else?"

Repeat until satisfied. Use the same test by default; only change the test if the feedback changes what the skill produces.

### Satisfaction signals
"ok" / "looks good" / "approve" / "✅" / "ship it" / "that's right" / no further feedback offered

### Stall rule
After 5 iterations without satisfaction: ask whether to continue or proceed to Phase 5 and edit the file directly after writing it.

### Efficiency rules
- Never show the full draft during the loop — only diffs + test output
- After satisfaction is signalled, move directly to Phase 5

---

## Phase 5 — Implement

### 1. Show the full final draft

Both artifacts:

**knowledge/\<slug\>.md** — label the block:
```
File: ~/picnic-analyst-assistant/knowledge/<slug>.md
```

Content — standard template:
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

**INDEX.yaml entry** — label the block:
```
Entry to append to: ~/picnic-analyst-assistant/knowledge/INDEX.yaml
```

```yaml
  - skill: <Human-readable skill name>
    file: <slug>.md
    status: ready
    agents: [<AGENT1>, <AGENT2>]
    load: <always|conditional>
    condition: <task involves X or Y>    # only if load: conditional
```

### 2. Quality checklist (apply before showing)
- [ ] "What this covers" is 1-2 sentences, specific enough to distinguish from adjacent skills
- [ ] "When to use" matches the INDEX.yaml condition exactly (same phrasing)
- [ ] "How to do it" has at least one concrete step, not just a description
- [ ] Reference section has at least one concrete example, template, or rule — not empty
- [ ] Slug matches naming style of existing files
- [ ] agents list is non-empty and makes sense for the domain
- [ ] If conditional: condition is specific (not vague like "task involves this skill")

### 3. Approval gate

End with this block:
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

On `'change: <what>'`: apply the revision and re-show the updated draft with the approval gate.
No need to re-run the practice test unless the scope of the skill changes.

### 4. Write (on approval)

1. **Check for slug conflict**: verify `knowledge/<slug>.md` does not already exist.
   If it does: warn the user and ask to overwrite or use a different slug before proceeding.

2. **Write** `knowledge/<slug>.md` with the full file content.

3. **Append** the INDEX.yaml entry to `knowledge/INDEX.yaml`:
   - Add as the last item under the `skills:` list
   - Preserve existing formatting and indentation exactly

4. **Confirm** to the user:
   ```
   Done. Created:
   - knowledge/<slug>.md
   - INDEX.yaml: "<skill name>" appended (agents: [...], load: <strategy>)

   Agents that will now load this skill: <list>
   ```

---

## Hard constraints

- **Approval**: Never write files without explicit Phase 5 approval
- **INDEX.yaml**: Never modify any existing entry — only append new entries at the end of the `skills:` list
- **Template**: All four sections (What this covers / When to use / How to do it / Reference) must always be present
- **Practice**: Never skip to Phase 5 without running at least one practice test or dry-run narration
