# Skill: Design dbt Models (picnic-dbt-models)

## What this covers
Writing dbt SQL, YAML config, and MD documentation for edge models in `picnic-dbt-models`.
Covers Jinja patterns, YML conventions, dbt-score requirements, and the full model file structure.

## When to use
When creating new edge models or modifying existing model SQL, config, or docs.
For the PR workflow that wraps this, see `pr-dbt-models.md`.

## How to do it

1. Read `~/Documents/Github/picnic-dbt-models/CLAUDE.md` for repo-specific rules first.
2. Create or modify files in `edge-models/models/edge/<domain>/<model_name>/`.
3. Each model folder contains three files: `.sql`, `.yml`, `.md`.
4. Validate via docker exec (see `pr-dbt-models.md` for container commands).
5. Target: `guide fix lint` at 0 warnings. This also includes `dbt-score`, which should be at 10/10.

---

## Reference: Conventions & Patterns

### Model File Structure

Each model lives in its own folder under `edge-models/models/edge/<domain>/<model_name>/`:
```
<model_name>/
  <model_name>.sql    — Jinja SQL logic
  <model_name>.yml    — config, columns, tests
  <model_name>.md     — {% docs %} documentation block
```

### Domains Maarten Works In
- `usuals/` — Usuals page (main active area)
  - Models owned: `usuals_dynamic_section_ranking_*`, `usuals_section_clusters`, etc.
  - Team: "Commercial Store Usuals"

### SQL Model Pattern (Jinja)
```sql
with
    /* Jinja variables at the top for config values */
    {% set some_param = 42 %}

    /* CTEs for all logic — no subqueries */
    my_cte as (
        select
            col_a,
            col_b
        from {{ ref("other_model") }}
        inner join {{ ref("dwh", "dm_delivery") }} dm_del on (dm_del.key_delivery = mc.key_delivery)
        where ...
    ),

    /* Incremental pattern */
    state as (
        {% if is_incremental() %}
            select key_customer, max(delivery_actual_rank) as max_rank
            from {{ this }}
            group by key_customer
        {% else %}select null as key_customer, null as max_rank where false
        {% endif %}
    )

select ...
from my_cte
```

Key Jinja patterns:
- `{{ ref("model_name") }}` — reference another edge model
- `{{ ref("dwh", "table_name") }}` — reference DWH/dim table
- `{{ env_var('PEE_MARKET') }}` — market variable
- `{{ this }}` — self-reference in incremental models
- `{% if is_incremental() %}` — incremental logic blocks

### YML Config Pattern

#### Single-column PK (most common) — scores 10/10
```yaml
---
models:
  - name: model_name
    description: "{{ doc('model_name') }}"
    config:
      enabled: "{{ env_var('PEE_MARKET') in ['nl', 'de', 'fr'] }}"
      materialized: incremental
      unique_key:
        - key_col
      incremental_strategy: merge
      grants:
        select: ["analyst"]
    meta:
      owner: "Maarten de Jong"
      team: "Commercial Store Usuals"
      alert_slack_users:
        - "U08Q96CDB25"
    columns:
      - name: key_col
        data_type: varchar
        description: "..."
        constraints:
          - type: primary_key        # ← PK at column level for single-col PK
        data_tests:
          - not_null
          - unique                   # ← uniqueness at column level
      - name: some_metric
        data_type: integer
        description: "..."
```
**No model-level `constraints:` block. No model-level `data_tests:` block.**

#### Composite PK (multi-column unique key)
```yaml
    constraints:                     # ← PK at model level for composite PK
      - type: primary_key
        columns: ["key_col_1", "key_col_2"]
    columns:
      - name: key_col_1
        ...  # no constraints: here
    data_tests:
      - dbt_utils.unique_combination_of_columns:
          arguments:
            combination_of_columns:
              - key_col_1
              - key_col_2
```

Key config values:
- `data_type`: `varchar`, `integer`, `float`, `boolean`, `date`, `timestamp`
- `materialized`: `incremental`, `table`, `view`
- Maarten's Slack user ID for alerts: `U08Q96CDB25`
- Market gate: `"{{ env_var('PEE_MARKET') in ['nl', 'de', 'fr'] }}"`

### Column Naming Conventions
- Weekly period key: always `key_week` (integer, YYYYWW format)
- Daily period key: always `key_date` (integer, YYYYMMDD format)
- Customer key: `key_customer` (varchar)

### MD Documentation Pattern

Follow the phrasing established by other Usuals reporting models:

1. **Opening line**: `"Query to generate weekly _[topic]_ data used in the Usuals reporting dashboard."`
   - Add `"This dbt model is used to export the output to the dashboard Google sheets."` if it has a `google_sheets:` config.
2. **Body**: numbered list or prose describing what the model computes.
3. **Example preamble** (required): one sentence explaining what the example demonstrates
4. **Example query**: always includes a non-trivial WHERE clause.

```markdown
{% docs model_name %}

Query to generate weekly _[topic]_ data used in the Usuals reporting dashboard.
This dbt model is used to export the output to the dashboard Google sheets.

[Body: numbered list or prose describing what the model computes]

The following query example selects [what] for [filter condition].

\`\`\`sql
select col_a, col_b
from edge.model_name
where key_week = '202601';
\`\`\`

{% enddocs %}
```

### dbt-score Rules — Key Learnings

#### Single-column PK rules (score 10 requires ALL of these):
- PK constraint must be at **column level** (`constraints: - type: primary_key` under the column)
- Uniqueness test must be at **column level** (`data_tests: - unique` under the column)
- Do NOT add model-level `constraints:` block or `dbt_utils.unique_combination_of_columns` for single-col PKs

#### Path structure rule (`path_to_model_is_allowed`):
Allowed patterns (regex-based):
1. `models/edge/{model}/{model}.sql` — simple top-level model
2. `models/edge/{topic}/{model}/{model}.sql` — model within topic folder
3. `models/edge/{model}/base/base_{model}__{suffix}/base_{model}__{suffix}.sql` — base model, no topic
4. `models/edge/{topic}/{model}/base/base_{model}__{suffix}/base_{model}__{suffix}.sql` — base model with topic

**Rules:**
- `base_` and `__` must both be present OR both absent in the path (XOR = violation)
- A model in `usuals/usuals_reporting/base/` MUST be named `base_usuals_reporting__{something}`
- An intermediate/staging model that doesn't fit the `base_` naming convention → use a regular name and place it in `models/edge/{topic}/{model_name}/`

#### Parent base model naming rule (`parent_base_model_name_is_valid`):
- If model `foo` references parent `base_bar`, then `bar` must equal `foo__{something}`
- **Practical implication**: if an intermediate model is referenced by a `base_` reporting model, do NOT give the intermediate model a `base_` prefix
