# Skill: Dashboard Reporting (Usuals)

## What this covers
Adding metrics to and maintaining the automated Usuals Business Performance Dashboard.
Covers the Google Sheets structure, SUMIFS formula pattern, formatting rules,
and the workflow for adding new sections or metrics.

## When to use
When adding a new metric, updating existing data, or building a new raw data tab for the
Usuals automated reporting dashboard (NL/DE/FR markets).

## Onboarding status
**Usuals automated reporting dashboard** — fully onboarded (2026-02-28). Rules below apply.
For any other report type not covered here, ask Maarten about format and workflow before proceeding.

## How to do it

### Pulling data
```
skill: snowflake-query  |  args: nl <query_name>
```
Results land in `~/.claude/data/snowflake-query/output/<query_name>.json`.

### Writing to Google Sheets
```
skill: gsheet
```
Run `info <sheet_id>` first to see available tabs.

### Draft-first workflow for dashboard edits
Never edit a live dashboard directly. Always:
1. **Duplicate the sheet** (Google Sheets → File → Make a copy, or duplicate via the gsheet skill) to create a draft version
2. **Apply all changes to the draft** — new tabs, new sections, formulas, formatting
3. **Show Maarten the draft** and wait for approval
4. **Only then apply the same changes to the real dashboard**

This applies to any structural edit: new sections, new raw data tabs, formula changes, formatting.
Read-only inspection of live sheets is always fine.

### Adding a new metric — mandatory workflow
**Always** follow this order:
1. **Create a new raw data tab** in the sheet (e.g. `NL base_usuals_reporting__<metric_name>`) to hold the absolute output of the SQL query.
   - Format: **metadata sidebar in columns A–C, data starting from column D** (same as all existing `base_usuals_reporting__*` tabs).
   - Columns A = metadata label, B = metadata value, C = empty, D = `period_key`, E onwards = absolute value columns.
2. **Write the SQL results** into that raw data tab (data from column D onwards, one row per week).
3. **Add SUMIFS rows** in the Dashboard's hidden absolute-numbers block, pulling from the new tab by `period_key` (keyed on row 8 week numbers).
4. **Add the visible metric row(s)** that compute the final metric (%, rate, etc.) from those absolute SUMIFS rows via cell formulas.

Never write static values or pre-computed ratios directly into the Dashboard data cells.

### Confirmation checkpoint before writing
After reading the sheet, state:
- Current last data row number
- Which row the new section header will go in
- Which raw data tab the SUMIFS will pull from
- Which columns in that raw tab hold the needed absolute values
- Column mapping for the new metric (B = name, F = unit, week-cols = formula structure)

Wait for go-ahead before writing anything.

---

## Reference: Conventions & Patterns

### Dashboard Sheet IDs
| Market | Sheet ID |
|--------|----------|
| NL | `1fAtVRL4k-Bk7ygWruN6jsg5DqLjGirW745ATJ60na0s` |
| DE | `1QXskY1ZQZEXi1tHOjcBF2fADN3nMKOLOkwlyrHvBkRQ` |
| FR | `17BqDhkAyQiT_uV7CwnBi61VulG-XTgDmEDUeglrtp4A` |

### Correct tab for new metrics
Always write new metrics to the `NL/DE/FR Usuals Dashboard` tab — **not** the raw data tabs
(`base_usuals_reporting__*`). Raw data tabs are source data only.

### Column layout (columns shift right every week)
An Apps Script runs weekly and inserts a new week column to the right of the current last week.
**Always determine current positions by reading row 8 with `--show-formulas` before writing.**

| Position | Role | Notes |
|----------|------|-------|
| A | Section title (header rows only) | Fixed |
| B | Metric name | Fixed |
| C | Sub-metric | Fixed |
| D–E | empty | Fixed |
| F | Unit (`#` or `%`) | Fixed |
| G → last-week-col | Weekly values (one column per week, expanding right) | Shifts every week |
| gap-col | Empty gap (1 column) | Shifts every week |
| delta-abs-col | Absolute delta vs. last week (`Abs.` in row 8) | Shifts every week |
| delta-rel-col | Relative delta vs. last week (`Rel.` in row 8) | Shifts every week |
| trailing-col | One trailing empty column (last column in sheet) | Shifts every week |

Look for in row 8:
- First week column: first column after F with a numeric week value (always G)
- Last week column: last column with a numeric or formula week value before the empty gap
- Gap column: the empty column immediately before "Abs."

### Section structure
```
[empty row]          ← separator before new section  (exactly ONE — never two)
[section header]     ← A = section title, bold + grey background, all other cols empty
[white rule]         ← empty row above abs block — stays visible when group is collapsed
[abs data rows]      ← B = metric name, F = "#", week cols = SUMIFS
[white rule]         ← included in group — hidden when collapsed
[metric row(s)]      ← B = metric name, F = "%" or "#", week cols = formulas, delta cols = delta formulas
[empty row]          ← one trailing empty row
```

### Formatting rules (apply to EVERY new row)

#### 1. Font size = 8 everywhere
All text in the dashboard uses **font size 8**. Always copy row format from a reference row.

#### 2. Section header rows
- **Column A**: bold, fontSize=8, bg=(0.95, 0.95, 0.95) — the light grey fill
- **All other columns (B → trailing-col)**: bg=(0.95, 0.95, 0.95) — grey fill

#### 3. F column and gap-col borders
Column F (unit) and the gap-col carry a thin border on every single row — separators, headers, data rows — without exception.

#### 4. Always use full-row `copyPaste` (PASTE_FORMAT) from reference rows of the SAME market
```python
# Header row → copy from row 9 (section header) of the SAME market
# All other new rows → copy from the last existing metric row of the SAME market
# Use: pasteType="PASTE_FORMAT", full column range (cols 0 → ws.col_count - 1)
```

**Section header rows (confirmed, NL):** 9, 14, 30, 41, 54, 87 (Long-press interaction)
**Last existing metric rows:** NL=85, DE=87, FR=87 (as of 2026-02-28; shifts as rows are added)

#### 5. Remove DASHED border from Manual Favorites rows
The Manual Favorites section (NL rows ~55–85) has a `left: DASHED` border on the gap-col.
After `copyPaste PASTE_FORMAT` from row 85:
- **Always remove** the `left: DASHED` from the gap-col on all non-header rows of the new section using `repeatCell` with `fields: "userEnteredFormat.borders.left"` and `style: "NONE"`.
- This does NOT apply to DE/FR — their reference rows don't carry this border.

### SUMIF data formula pattern
```
=SUMIFS('<tab>!$<col>:$<col>', '<tab>'!$D:$D, G$8)
```
- Tab name: `NL/DE/FR base_usuals_reporting__<model_name>`
- Key column: `D` = `period_key` (YYYYWW integer matching row 8 week numbers)
- Value column: whichever column holds the absolute count needed

### Delta formula pattern
Copy the delta formula from an existing row — do not hardcode column letters.
The abs delta is `=IFERROR(<last_week_col>{row}-<prev_week_col>{row},"")` and the rel delta is
`=IFERROR((<last>-<prev>)/ABS(<prev>),"")`.
