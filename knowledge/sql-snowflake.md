# Skill: Write Snowflake SQL

## What this covers
Writing, running, and interpreting Snowflake SQL queries against Picnic's data warehouse.
Covers conventions, table joins, date math, deduplication, event analytics, and edge models.

## When to use
Any data question, metric calculation, A/B audience query, or dashboard feed query that runs
against Picnic's Snowflake (PICNIC_NL/DE/FR_PROD). Not for Calcite SQL — see `sql-calcite.md`.

## How to do it

### Step 0 — Discover tables with the catalog

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
   After approval, save `<descriptive_name>.sql` alongside the task's output.md.
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
- **Left join filter trap**: always apply `left join` filters in the `on` clause, not `where` (a `where` on the right table silently turns it into an inner join)
- **Structure**: CTEs with `with` clause — not subqueries; never `select *`
- **Deduplication**: `qualify row_number() over (partition by ... order by ...) = 1`
- **Market**: `public.f_get_market()` — not hardcoded `'nl'`/`'de'`/`'fr'`
- **Comments**: `/*` style, capitalised, placed above the code line they describe. Each CTE always get's a brief comment describing it's use. Non-trivial column or filters also get comments. 
- **No `order by` inside CTEs** — only in the final output

### Standard Filters (apply unless instructed otherwise)
```sql
-- Active real orders
and dmo.order_actual = 'yes'

-- Real customers (exclude test + deleted)
and dmc.cust_internal = 'no'
and dmc.cust_deleted = 'no'
```

### Database Structure

```
picnic_market           — per-market database (NL/DE/FR), resolved at query time
picnic_global           — cross-market database

Within each database:
  dim     — core fact + dimension tables (orders, customers, articles, dates, …)
  edge    — 200+ processed analyst models (use these before building from scratch)
  sandbox — personal experimentation
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

#### Customer + Orders
```sql
from dim.FT_ORDER as fto
inner join dim.dm_order as dmo
    on (fto.key_order = dmo.key_order)
inner join dim.dm_customer as dmc
    on (fto.key_customer = dmc.key_customer)
inner join dim.dm_date as dmd
    on (fto.key_order_date = dmd.key_date)
where
    dmo.order_actual = 'yes'
    and dmo.order_actual_delivery_rank = 1
    and dmc.cust_internal = 'no'
    and dmc.cust_deleted = 'no'
```

#### Delivery-based queries
```sql
from dim.ft_delivery as ftd
inner join dim.dm_date_delivery as dmdd
    on (ftd.key_delivery_date = dmdd.key_delivery_date)
inner join dim.dm_customer as dmc
    on (ftd.key_customer = dmc.key_customer)
where
    dmc.cust_internal = 'no'
    and dmc.cust_deleted = 'no'
```

#### Article / Product Lookup
```sql
from dim.dm_article as dma
-- Key fields: art_supply_chain_name, art_p_cat_lev_1/2/3, art_p_cat_lev_3_id
where dma.art_assortment_status = 'In'   -- active articles only
```

#### Customer Tags / Experiment Assignment
```sql
from dim.ft_customer_tag as ftct
inner join dim.dm_tag as dmt
    on (ftct.key_tag = dmt.key_tag)
where dmt.tag_type = '<experiment_type>'
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

-- Reference in query:
where ftse.key_event_date >= $key_start_date
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

### Category Hierarchy (dm_article)
```
art_p_cat_lev_1      — top level (e.g., 'Fresh', 'Dry', 'Non-food')
art_p_cat_lev_2      — mid level
art_p_cat_lev_3      — leaf category (most granular, used in most analyses)
art_p_cat_lev_3_id   — ID for joining (prefer over name for joins)
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
ft_store_events is very large — avoid scanning it multiple times:
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
public.f_get_current_local_date()    -- current local date (use instead of current_date())
public.f_get_market()                -- current market ('nl'/'de'/'fr')
public.f_get_key_dim(null)           -- returns null-dimension key (for baseline price filter)
```

### Reusable Edge Models

Always check the EDGE schema before building a query from scratch — a ready-made model may already exist:
```
skill: read-dwh-data-catalog  |  args: <topic> --schema edge
```
Edge models cover: acquisition/retention, commercial KPIs, A/B test significance, CRM performance, pricing, and more. Use the catalog to discover what's available and get exact column names.

### A/B Test Random Assignment Pattern
```sql
-- MD5-based deterministic random assignment (50/50 split)
right(regexp_replace(md5(concat(key_customer, '<test_id>' || '-ab-test')), '[^0-9]', ''), 2) < 50
    as test_group   -- true = treatment, false = control
```

### Performance Rules
- Filter on `key_*` surrogate key columns first (partition pruning)
- Apply date/week range filters as early as possible in CTE chain
- For `left join`: put filter conditions in `on` clause, NOT `where` (silently becomes inner join)
- No `order by` inside CTEs — only in the final `select`
- Prefer `inner join` for dimension lookups (all fact records should have matching dimensions)
