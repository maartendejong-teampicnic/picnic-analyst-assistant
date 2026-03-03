---
name: slides
description: Create PowerPoint .pptx files from a JSON deck definition. Use when building a new presentation or adding slides for Maarten. Supports both python-pptx layout slides and real think-cell charts via ppttc.exe.
allowed-tools:
  - Bash
  - Read
  - Write
---

# Slides Tool

CLI tool for creating PowerPoint .pptx files from structured JSON input.
Uses the Picnic branded template by default.

## Tool Path

```bash
~/Documents/Claude/analysistant/skills/slides/slides.sh <deck.json>
```

## Input format

The tool accepts a JSON file with this structure:

```json
{
  "title": "My Deck",
  "template": "/home/picnic/.claude/data/Input/picnic_default_ppt_theme.pptx",
  "output": "/home/picnic/.claude/data/Output/my_deck.pptx",
  "slides": [
    {
      "layout": "start",
      "title": "Usuals – Personalized section ranking",
      "subtitle": "WK2026-07",
      "notes": "Opening slide."
    },
    {
      "layout": "title-only",
      "title": "Conversion of home page section is significantly higher for test group",
      "subtitle": "Conversion (%) = adding customers / viewing customers",
      "footer": "Data wk 7 · NL · 50K customers per group",
      "notes": "[CHART PLACEHOLDER: bar chart test vs control conversion, annotate +2.0pp]"
    },
    {
      "layout": "title-only",
      "title": "Recommendation: roll out to 100% of NL customers",
      "subtitle": "All success metrics met — proceed with full roll-out in CW10",
      "notes": "Decision slide. Summarise the key evidence."
    }
  ]
}
```

## Layouts (Picnic template)

| Key | Template name | Use for |
|-----|--------------|---------|
| `start` | Start | Title / opening slide |
| `agenda` | Agenda | Numbered list of up to 6 agenda items |
| `title-only` | Title Only | **Default content slide** — conclusion + subtitle + optional footer |
| `bullets` | Bullets | Text-only slide with a bullet list (rarely used) |
| `charts` | Charts | Chart slide with 3 right-side annotation text boxes |
| `blank` | Blank | Full-canvas custom content |
| `end` | End | Closing slide |

## Slide fields

| Field | Layouts | Placeholder | Description |
|-------|---------|-------------|-------------|
| `layout` | all | — | Layout key above (default: `title-only`) |
| `title` | all except blank/end | ph[0] in content layouts; ph[10] in start | Main conclusion / finding. Ph[0] is the thin colored top strip — it holds the primary message. |
| `subtitle` | start, title-only, bullets, charts | ph[10] or ph[11] | Metric definition, scope, or secondary point |
| `footer` | title-only, bullets, charts, blank | ph[23] | Data scope note: dataset, market, week, sample size |
| `body` | bullets | ph[24] | Array of strings. Use `{"text": "...", "level": 1}` for sub-bullets |
| `items` | agenda | ph[26,33,35…] | Array of up to 6 agenda item strings (auto-numbered) |
| `sidebar` | charts | ph[24,25,26] | Array of up to 3 annotation strings for chart callouts |
| `notes` | all | notes slide | Speaker notes. Use `"[CHART PLACEHOLDER: ...]"` or `"[IMAGE PLACEHOLDER: ...]"` for visual slots |

## Default paths

- Template: `~/.claude/data/Input/picnic_default_ppt_theme.pptx`
- Output: `~/.claude/data/Output/<deck_name>.pptx`
- JSON input: `~/.claude/data/Input/<deck_name>.json`

## Workflow

1. Confirm deck type and audience with Maarten
2. Draft outline (titles only) and confirm before filling content
3. Build the full JSON deck definition
4. Save JSON to `~/.claude/data/Input/<deck_name>.json`
5. Run: `~/Documents/Claude/analysistant/skills/slides/slides.sh ~/.claude/data/Input/<deck_name>.json`
6. Output .pptx is saved to `~/.claude/data/Output/`
7. Report the file path to Maarten for review in PowerPoint

## Examples

```bash
# Build layout/text deck from JSON file
~/Documents/Claude/analysistant/skills/slides/slides.sh ~/.claude/data/Input/my_deck.json

# Build with inline JSON (simple decks)
~/Documents/Claude/analysistant/skills/slides/slides.sh --json '{"output": "~/out.pptx", "slides": [...]}'
```

---

## Think-cell chart automation

For slides with real think-cell charts, use the **thinkcell tool** instead:

```bash
~/Documents/Claude/analysistant/skills/slides/thinkcell.sh <deck.json>
```

### How it works

1. You provide a `.pptx` template that already contains named think-cell elements
2. The tool generates a `.ppttc` data file and calls `ppttc.exe` (installed at `C:\Program Files (x86)\think-cell\`)
3. Output is a `.pptx` with all charts and text fields filled with your data

### How to name think-cell elements (one-time setup per template)

In PowerPoint with think-cell installed:
1. Right-click a think-cell chart or text field
2. Select **"Name"** (or "Add Name" in older versions)
3. Enter a short slug, e.g. `conversion_bar`, `trend_line`, `test_period`
4. Repeat for every element you want to fill programmatically
5. Save as `<name>_template.pptx` in `~/.claude/data/Input/`

### Input format

```json
{
  "template": "/home/picnic/.claude/data/Input/ab_test_template.pptx",
  "output":   "/home/picnic/.claude/data/Output/ab_test_wk05-08.pptx",
  "charts": [
    {
      "name": "conversion_bar",
      "categories": ["Control", "Test"],
      "series": [
        {"name": "Conversion (%)", "values": [81.1, 83.1]}
      ]
    },
    {
      "name": "trend_line",
      "categories": ["WK05", "WK06", "WK07", "WK08"],
      "series": [
        {"name": "Test",    "values": [80.5, 81.2, 82.0, 83.1]},
        {"name": "Control", "values": [80.3, 80.7, 80.9, 81.1]}
      ]
    }
  ],
  "textfields": [
    {"name": "test_period",  "value": "CW05–08 2026"},
    {"name": "sample_size",  "value": "50K customers per group"},
    {"name": "market",       "value": "NL"}
  ]
}
```

### Chart table format (ppttc spec)

| Row | Content |
|-----|---------|
| Row 0 | `[null, category_1, category_2, ...]` |
| Row 1+ | `[series_name, value_1, value_2, ...]` |

Values can be numbers, strings, or ISO 8601 dates.

### Recommended templates to build

| Template file | Charts to name | Text fields to name |
|---------------|---------------|---------------------|
| `ab_test_template.pptx` | `primary_bar`, `secondary_bar`, `trend_line`, `success_table` | `test_name`, `test_period`, `market`, `sample_size`, `hypothesis` |
| `biweekly_template.pptx` | `metric_chart` (optional) | `topic`, `headline`, `week` |
