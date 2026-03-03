# Skill: Create Slides (.pptx)

## What this covers
Building executive slide narratives as .pptx files using the Picnic branded template.
Translates analytical findings into clear, well-structured presentations.

## When to use
When creating or updating PowerPoint presentations — A/B test results, analysis write-ups,
stakeholder decks, biweekly personal updates, weekly updates.

## How to do it

1. **Clarify** deck type and primary audience (exec, team, stakeholder)
2. **Draft outline** — `title` text only for each slide, confirm with Maarten before writing body
3. **Build content** — fill subtitle, footer, notes per slide; flag chart/image placeholders
4. **Generate JSON** — save to `~/.claude/data/Input/<deck_name>.json`
5. **Run skill** — call `slides` skill to produce the .pptx
6. **Report path** — tell Maarten the output file path for review in PowerPoint

### Execution tools
- Skill: `slides` (`~/Documents/Claude/analysistant/skills/slides/SKILL.md`)
- Template: `~/.claude/data/Input/picnic_default_ppt_theme.pptx`
- Output dir: `~/.claude/data/Output/`

### Think-cell charts
- **Named template exists**: use `thinkcell_tool.py` — provides real think-cell charts in .pptx
  - Tool: `~/Documents/Claude/analysistant/skills/slides/thinkcell_tool.py`
  - ppttc.exe: `C:\Program Files (x86)\think-cell\ppttc.exe`
  - Stages files via Windows %TEMP% to avoid WSL UNC path rejection
  - Requires a template with **named** think-cell elements
- **No named template yet**: leave `title-only` slide with `[CHART PLACEHOLDER: <description>]` in notes

| Situation | Tool | Approach |
|-----------|------|----------|
| Named template exists | `thinkcell.sh` | Provide chart data in JSON → real think-cell charts |
| No named template yet | `slides.sh` | Leave `title-only` slide, `[CHART PLACEHOLDER: ...]` in notes |
| Phone design mockup | `slides.sh` | `[IMAGE PLACEHOLDER: ...]` in notes — Maarten adds in Figma/PPT |
| Timeline / Gantt | `slides.sh` | Build from connector lines + text boxes |

---

## Reference: Conventions & Patterns

### Two-line title structure
Nearly every content slide uses the **Title Only** layout with two title lines:

| Placeholder | Role | Example |
|-------------|------|---------|
| `title` (ph[0]) | **Main conclusion or finding** | "Conversion of home page section is significantly higher for test group" |
| `subtitle` (ph[10]) | **Metric definition, scope, or secondary point** | "Conversion (%) = adding customers / viewing customers" |
| `footer` (ph[23]) | **Data scope note** — dataset, date range, sample size | "Usuals page performance of week 2026-05 in NL" |

Footer examples:
- `"Results from A/B-test in NL, out of 50K active mature customers."`
- `"Usuals page performance of week 2026-05 in NL"`
- `"Active and Mature customers with Weekly or Biweekly order frequency (239K)."`
- `"Power = 80, alpha = 5%"` (on power analysis slide)

### Layout preference
- **Content slides**: almost always `title-only` — visual content placed freely
- **Bullets layout is rarely used** — Maarten builds text visuals as free-form text boxes
- Use `bullets` only when content is genuinely a list of points with no accompanying visual

### Speaker notes
- For biweekly: just the week number ("wk36", "Wk 202604")
- For strategic and analysis decks: 3–5 sentences for cold readers
- Can be in Dutch for internal Picnic presentations

### Core conventions
- **One message per slide**: if a slide makes two claims, split it into two slides
- **Title-only layout by default**
- **Never fabricate data**: use only numbers from ANALYST output; insert `[DATA PLACEHOLDER]` if missing
- **BLUF narrative flow**: put the conclusion slide early; support it with evidence
- **Always English** in the slides themselves

### Deck types

#### Biweekly personal update
Single slide per biweekly session. All updates collected in one growing deck file.

| Field | Content |
|-------|---------|
| Layout | `title-only` |
| `title` (ph[0]) | Project context label, e.g. `"Usuals page"` |
| `subtitle` (ph[10]) | The headline — what happened / was delivered this sprint |
| Notes | Just the week: `"wk36"` or `"Wk 202604"` |

#### A/B test results
**Start → Agenda → Test setup → Results (one metric per slide) → Success metrics summary → Test planning → End**

| # | Layout | `title` | `subtitle` | `footer` |
|---|--------|---------|-----------|---------|
| 1 | `start` | Experiment name | Period · market · test ID | — |
| 2 | `agenda` | "Agenda" | — | — |
| 3 | `title-only` | "Test ran WK[X]–[Y] on [N]K [market] [audience]" | Hypothesis | — |
| 4+ | `title-only` | **Conclusion** e.g. "Conversion significantly improved +2.0pp" | Metric definition | "Data wk [X]" or "50K customers in each group" |
| N-1 | `title-only` | "All success metrics are met / [metric] slightly below target" | "Power = 80, alpha = 5%" | — |
| N | `end` | — | — | — |

#### Analysis write-up
**Start → Context/background → Findings (one per slide) → Recommendation → End**

| # | Layout | `title` | `subtitle` |
|---|--------|---------|-----------|
| 1 | `start` | Topic name | Date or scope |
| 2 | `title-only` | "Context: [problem statement]" | Supporting detail |
| 3+ | `title-only` | **Finding as conclusion** | Data definition or scope |
| N | `title-only` | "Recommendation: [clear action]" | Owner / timeline |
| N+1 | `end` | — | — |

#### Stakeholder / strategy (CEO-level)
**Start → Agenda → Sections → Proposal → End** with appendix slides after End

| # | Layout | Notes |
|---|--------|-------|
| 1 | `start` | Title + "WK[YYYY-WW]" as subtitle |
| 2 | `agenda` | Up to 4 section items |
| 3–N | `title-only` | Customer data, problem scoping, proposal |
| N+1 | `title-only` | Recommendation slide |
| N+2 | `end` | — |
| N+3+ | `title-only` | Appendix / backup slides (after End) |

#### Weekly update
**Start → Highlights → Metrics → Actions → End**

| # | Layout | `title` | `subtitle` |
|---|--------|---------|-----------|
| 1 | `start` | "Weekly update — CW[XX] [YYYY]" | Team or scope |
| 2 | `title-only` | "Three highlights this week" | Brief context |
| 3 | `title-only` | Key metric movement (conclusion first) | Metric definition |
| 4 | `title-only` | "Next week: [top 3 priorities]" | Owner or deadline |
| 5 | `end` | — | — |

### Think-cell template setup (one-time, per deck type)
In PowerPoint with think-cell installed:
1. Right-click each chart/text field → **"Name"**
2. Assign slug names (`conversion_bar`, `trend_line`, `test_period`, etc.)
3. Save as `<type>_template.pptx` in `~/.claude/data/Input/`

**Recommended named templates to create:**
- `ab_test_template.pptx` — charts: `primary_bar`, `trend_line`, `success_table`; fields: `test_name`, `test_period`, `market`, `sample_size`
- `biweekly_template.pptx` — fields: `topic`, `headline`, `week`
