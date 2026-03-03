# Skill: Write Snowflake SQL

## What this covers
Writing, running, and interpreting Snowflake SQL queries against Picnic's data warehouse.
Covers table joins and formatting conventions, and lists Usuals-specific knowledge. 

## When to use
Any data question, metric calculation, A/B audience query, or dashboard feed query that runs
against Picnic's Snowflake (PICNIC_NL/DE/FR_PROD). Not for Calcite SQL.

## How to do it

### Discover tables with the catalog

**Before writing any SQL**, use the `read-dwh-data-catalog` skill to find the right table:
```
skill: read-dwh-data-catalog  |  args: <topic> --limit 5
```
- `full_path` in the result (e.g. `picnic_market.dim.ft_order`) is what goes in the `FROM` clause — use it exactly
- `columns` with descriptions tell you what fields exist and what they mean
- Search multiple topics if the first doesn't return enough (e.g. `order` and then `basket`)
- To browse EDGE models specifically: `args: <topic> --schema edge`
- To force a catalog refresh: `args: refresh`

### Running queries

1. Write the query to `~/.claude/data/snowflake-query/queries/<descriptive_name>.sql`
   — use snake_case, e.g. `weekly_order_trend.sql`
2. **Show the query and wait for confirmation that it is correct before running it.**
   After approval, also save `<descriptive_name>.sql` alongside the task's output.md:
   direct mode → direct task folder; orchestrated → `tasks/<task-id>/`.
3. Invoke the skill:
   ```
   skill: snowflake-query  |  args: nl <descriptive_name>
   ```
   Change `nl` to `de` or `fr` for other markets.
4. Read results from `~/.claude/data/snowflake-query/output/<descriptive_name>.json`
   and interpret them following the Query Output Format below.

**Notes**
- Query files are saved and reusable — name them descriptively
- For cross-market: run the skill twice with different market args, same query name
- If the skill hits a permissions error, prepend `USE SECONDARY ROLES ALL;` to the query
- Check `~/.claude/skills/snowflake-query/app/example_queries/` for reference patterns

### Interpreting results

When interpreting query results:
1. **Key finding** — one sentence
2. **Numbers with context** — delta vs. prior period, vs. target, vs. other market
3. **Data quality notes** — any caveats (missing market, date gaps, exclusions applied)
4. **Suggested next step** — what would make sense to look at next

**No raw tables.** Write conclusions as prose or bullet points. Show max 3 sample rows inline
only if they directly illustrate a specific finding. Always reference the raw output path.

### Query output for dashboard reporting
When writing a SQL query whose output will land in a Usuals Dashboard sheet:
- **Output absolute numbers only** — never pre-compute ratios or percentages in SQL
- The sheet formulas compute the metrics (%, rates, deltas) from the absolute inputs
- For an adoption metric you need TWO absolute columns: numerator + denominator

---

## Reference: Conventions & Patterns

### SQL Conventions (ALWAYS apply — no exceptions)

- **Aliases**: prefix + first letter of each word → `dm_delivery` = `dmd`, `ft_order` = `fto`, `ft_store_selling_unit_event` = `ftssue`
- **Comparisons**: `<>` not `!=`; `where foo = false` not `where not foo`
- **Joins**: `on (condition)` with parentheses always — never `using`
- **Join types**: prefer `inner join`; use `left join` only when you need unmatched rows; never `full join` or `right join`
- **Structure**: CTEs with `with` clause — not subqueries; never `select *`
- **Comments**: `/*` style, capitalised, placed above the code line they describe. Each CTE always get's a brief comment describing it's use. Non-trivial column or filters also get comments. 
- **No `order by` inside CTEs** — only in the final output

### Database Structure

```
picnic_market           — per-market database (NL/DE/FR), resolved at query time
picnic_global           — cross-market database

Within each database:
  dim     — core fact + dimension tables (orders, customers, articles, dates, …)
  edge    — 200+ processed analyst models (use these before building from scratch)
  temp    — temporary staging tables
```

**Always discover tables via the catalog before writing SQL** — use `read-dwh-data-catalog <topic>` to get exact `full_path` values and column details. Do not guess table names.

### Query Boilerplate
```sql
use role ANALYST;
use database PICNIC_NL_PROD;  -- change to PICNIC_DE_PROD / PICNIC_FR_PROD as needed

with
    <cte_name> as (
        select
            ...
        from dim.<TABLE> as <alias>
        inner join dim.<TABLE2> as <alias2>
            on (<alias>.<key> = <alias2>.<key>)
        where
            ...
    )

select
    ...
from <cte_name>
```

### Core Join Patterns

```
-- SAVE STANDERD JOIN PATTERNS HERE
```


#### Usuals adds (ft_store_selling_unit_events)
For counting which articles customers added to basket from the Usuals page:
```sql
from dim.ft_store_selling_unit_events as ftssue
inner join dim.dm_event_screen as dmes
    on (ftssue.key_event_screen = dmes.key_event_screen)
inner join dim.dm_selling_unit as dmsu
    on (ftssue.key_selling_unit = dmsu.key_selling_unit)
inner join dim.dm_customer as dmc
    on (ftssue.key_customer = dmc.key_customer)
where
    ftssue.event_is_add_product_to_basket = 'yes'
    and dmes.event_screen_name in ('purchases-page-root', 'aisle-deep-dive')
```

#### Article / Product Lookup
```sql
from dim.dm_article as dma
-- Key fields: art_supply_chain_name, art_p_cat_lev_1/2/3, art_p_cat_lev_3_id
where dma.art_assortment_status = 'In'   -- active articles only
```

### Date & Week Math
```sql
dmd.key_date               -- YYYYMMDD format
dmd.key_week               -- YYYYWW format
dmd.date                   -- actual DATE column (NOT calendar_date — that column does not exist)

-- Current date (use this, NOT current_date()):
public.f_get_current_local_date()

-- Current market (use this, NOT hardcoded 'nl'/'de'/'fr'):
public.f_get_market()
```

### Date Key Filtering (no dm_date join needed for filtering)
KEY_DATE, KEY_EVENT_DATE, KEY_DELIVERY_DATE etc. are integers in YYYYMMDD format.
KEY_WEEK, KEY_EVENT_WEEK etc. are integers in YYYYWW format.
Filter directly on these — avoids a join to dm_date just for date range filtering:
```sql
where ftse.key_event_date >= 20260224        -- YYYYMMDD integer, no join needed
  and ftse.key_event_week >= 202608          -- YYYYWW integer
```
Only join dm_date when you need derived fields (weeks_between, promo_calendar_week, dmd.date label, etc.)

### Session Variables (avoid hardcoding dates / values)
```sql
set key_start_date = 20260224;   -- YYYYMMDD integer
set key_start_week = 202608;     -- YYYYWW integer

-- Reference in query example:
where ftse.key_event_date >= $key_start_date
where dmd.key_week >= $key_start_week
```

### Deduplication
```sql
-- Always use QUALIFY, not a wrapping CTE:
qualify
    row_number() over (
        partition by <unique_key_columns>
        order by <prefer_most_recent_field> desc nulls last
    ) = 1
```

### App Event Analytics Tables
```sql
-- App / in-store event stream
from dim.ft_store_events as ftse
inner join dim.dm_event_screen as dmes
    on (ftse.key_event_screen = dmes.key_event_screen)

-- Useful ft_store_events columns: KEY_CUSTOMER, KEY_EVENT_DATE, KEY_EVENT_WEEK, KEY_EVENT_SCREEN, EVENT_NAME, EVENT_TS
-- Useful dm_event_screen columns:
--   event_screen_name          — screen identifier (e.g. 'action-bottom-sheet' for long-press)
--   event_screen_tab_name      — tab context (home, search, usuals, page, basket, ...)
--   event_screen_page_template_id — page template (often null; not the primary screen id)

-- Any presence in ft_store_events on a day = customer opened the app (app open proxy)
```

### Weekly Spine Pattern (for cumulative / period-over-period metrics)
```sql
week_spine as (
    select
        dmd.key_week as period_key,
        max(dmd.key_date) as last_key_date_of_week   -- = today for the current partial week
    from dim.dm_date as dmd
    where dmd.key_date >= $key_start_date
      and dmd.date <= public.f_get_current_local_date()   -- cap here; don't use HAVING
    group by dmd.key_week
)
```
- `WHERE date <= current_date` naturally caps the current week: `last_key_date_of_week` = today.
- Use `last_key_date_of_week` as the upper bound in cumulative JOINs (not the period_key integer).
- **Don't use** `HAVING max(date) < current_date` to exclude partial weeks.

### Efficient Single-Scan Pattern for Large Event Tables
ft_store_events and ft_store_selling_unit_events are very large — avoid scanning it multiple times:
```sql
-- Single scan: flag long-press events inline
all_events as (
    select
        ftse.key_customer,
        ftse.key_event_date,
        max(case when dmes.event_screen_name = 'action-bottom-sheet' then 1 else 0 end) as saw_long_press
    from dim.ft_store_events as ftse
    left join dim.dm_event_screen as dmes
        on (ftse.key_event_screen = dmes.key_event_screen)
    where ftse.key_event_date >= $key_start_date
    group by
        ftse.key_customer,
        ftse.key_event_date
)
```

### Public Functions
```sql
public.f_get_key_date(date)          -- convert date → key_date integer (YYYYMMDD)
public.f_key_date_to_date(key_date)  -- convert key_date integer → date
public.f_get_market()                -- current market ('nl'/'de'/'fr')
```

- No `order by` inside CTEs — only in the final `select`
- Prefer `inner join` for dimension lookups (all fact records should have matching dimensions)

---

### Usuals Page

#### Screen name filters (dm_event_screen.event_screen_name)
| Screen name | What it captures | Status |
|-------------|-----------------|--------|
| `purchases-page-root` | Main Usuals page | Current DWH name — migrating to `usuals` |
| `aisle-deep-dive` | Section deep-dive (replaces deprecated `purchases-page-root-category`) | Current DWH name — migrating to `usuals-deep-dive` |
| `action-bottom-sheet` | Long-press context menu — add `and dmes.event_screen_tab_name = 'usuals'` to scope to Usuals-specific long-presses | Active |

> `purchases-page-root-category` is deprecated (removed — replaced by `aisle-deep-dive`). Do not include in filters.

#### Standard Usuals add filter
Apply when counting article adds originating from the Usuals page (use with `ft_store_selling_unit_events`):
```sql
where ftssue.event_is_add_product_to_basket = 'yes'
  and dmes.event_screen_name in (
      'purchases-page-root',   -- main page (migrating to 'usuals')
      'aisle-deep-dive'        -- section deep-dive (migrating to 'usuals-deep-dive')
  )
```

#### Available edge models
All Usuals models live in the `edge` schema. Check exact column names via `read-dwh-data-catalog <model_name>` before writing SQL — do not assume column names.

| Model | What it contains | Notes |
|-------|-----------------|-------|
| `base_usuals_reporting__delivery_week` | Weekly IPD + GMD per market | Requires `analyst_finance` role |
| `base_usuals_reporting__event_week` | Weekly app opens, page views, article views + adds | Main engagement model |
| `base_usuals_reporting__pill_week` | Per-section campaign pill metrics | |
| `base_usuals_reporting__suggestion_week` | AI suggestion metrics | |
| `base_usuals_reporting__manual_favorites_week` | LIKE/UNLIKE adoption + behavior | 440+ lines of logic; check model before rewriting |
| `usuals_section_mapping` | ADS-configured section ↔ assortment (L3) mapping | |
| `usuals_section_clusters` | Section cluster assignments (CORE_FRESH / FRESH_FOOD / NON_FRESH) | |
| `usuals_missing_assortment_category` | Daily: L3 categories not mapped to any section | Use for assortment monitoring |
| `usuals_dynamic_section_ranking_applied_section_score` | Applied section scores | Only updates when rank changes and ≥5 deliveries since last update |
