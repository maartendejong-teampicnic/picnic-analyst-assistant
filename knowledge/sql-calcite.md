# Skill: Write Calcite SQL (picnic-store-config)

## What this covers
Writing and validating Calcite SQL queries for the `picnic-store-config` repository.
Calcite is the SQL engine that powers live store pages (Usuals page and others) by querying
customer-scoped virtual tables at request time per customer.

## When to use
When editing `.sql` files in `picnic-store-config/pages/picnic-pages/src/pages/*/queries/`.
Not for Snowflake/DWH/DBT queries.

## How to do it

TO BE ONBOARDED

## Reference: Conventions & Patterns

### Calcite vs. Snowflake Differences

| Rule | Calcite (store-config) | Snowflake (dbt) |
|------|----------------------|-----------------|
| Parameters | `${paramName}` (e.g. `${aisleId}`, `${sellingUnitLimit}`) | Jinja `{{ }}` |
| Date arithmetic | `current_date - INTERVAL 3 MONTH` | `dm_date.weeks_between` |
| Feature flags | `EXISTS (SELECT 1 FROM calcite_user_tags WHERE id = 'flag-id')` | N/A |
| FULL OUTER JOIN | Allowed and used | Avoid |
| LATERAL VALUES | `CROSS JOIN LATERAL (VALUES ('a', x), ('b', y)) AS t (col1, col2)` | Not used |
| QUALIFY | Same syntax: `QUALIFY ROW_NUMBER() OVER (...) = 1` | Same |
| SELECT * | Avoided (use explicit columns) | Same |
| Comments | `/* block comments */` only (not `--`) | Both |
| No schema prefix | Tables are virtual — no database/schema prefix needed | Always schema-qualified |
| Deduplication | `QUALIFY ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...) = 1` | Same |

### Virtual Table Catalogue (Usuals / Aisle page)

These are customer-scoped virtual tables — they automatically scope to the requesting customer.

| Table | What it contains |
|-------|-----------------|
| `customer_sellable_attributes` | Manual favorite status per selling unit (`manual_favorite_status`, `sellable`) |
| `upcoming_deliveries_selling_units` | Selling units in the customer's upcoming delivery |
| `customer_upcoming_deliveries_selling_units_l3s_attribute` | L3-level just-delivered selling units |
| `core_catalog_selling_units` | Catalog: `id`, `sole_article_id`, `sole_article_count` |
| `customer_article_targeting_model_rank_per_group_attribute` | Article rank within L3 (`key`=article_id, `val`=rank) |
| `categories_selling_units` | Maps selling units to L3 category (`l3_category_id`) |
| `assortment_aisle_assortment_category_attributes` | Maps L3 categories to aisles (`assortment_aisle`, `assortment_category`, `mapping_l3`, `mapping_l3_unique`) |
| `customer_article_attributes` | `last_purchased_selling_unit`, `previous_usual_selling_units`, `article` |
| `user_blacklisted_articles` | Blacklisted selling units for the customer |
| `customer_assortment_category_l3_rebuy_probability_attribute` | Rebuy probability per L3 (`key`=l3_id, `val`=prob) |
| `customer_l3_targeting_model_delivery_count_l14m_attribute` | Delivery count last 14 months per L3 (`key`=l3_id, `val`=count) |
| `customer_l3_targeting_model_activity_type_attribute` | Activity type per L3 (`key`=l3_id, `val`=Active/Passive/Churned) |
| `selling_unit_alternatives` | Alternative selling units (`selling_unit_id`, `alternative_selling_unit_id`, `alternative_type`) |
| `selling_unit_stock` | Availability status per slot (`selling_unit_id`, `slot_id`, `availability_status`) |
| `user_slots` | Customer's delivery slots (`slot_id`, `selected`) |
| `customer_selling_unit_attributes` | `selling_unit`, `last_purchased_time` |
| `purchases_selling_units` | Catalog of purchasable selling units (`id`, `sole_article_id`) |
| `customer_article_recency_frequency_score_attribute` | Recency-frequency score (`key`=article_id, `val`=score) |
| `customer_liked_favorite_deliveries_not_bought_attribute` | Number of deliveries since a liked-but-unbought favorite was last bought (`key`=article_id, `val`=count) |
| `customer_l3_months_since_last_delivery_attribute` | Months since last delivery in L3 (`key`=l3_id, `val`=months) |
| `calcite_user_tags` | Feature flags enabled for the customer (`id`=flag_id) |

### Feature Flag Pattern

```sql
/* Check if a feature flag is enabled for this customer */
EXISTS (
  SELECT 1
  FROM calcite_user_tags
  WHERE id = 'flag-id-here'  /* Human-readable comment of what flag does */
)
```

Use this in WHERE clauses or CASE expressions. Example: filter for single-unit articles only
when the progressive discounts flag is active:
```sql
WHERE (
  (EXISTS (SELECT 1 FROM calcite_user_tags WHERE id = '68c91cb70317be0cea23b471')
    AND ccsu.sole_article_count = 1)
  OR
  NOT EXISTS (SELECT 1 FROM calcite_user_tags WHERE id = '68c91cb70317be0cea23b471')
)
```

### tile-grid.sql vs tile-grid-test-group.sql

These two files are **identical except for one field** in the `all_aisle_selling_units` CTE:

| File | WHERE clause in all_aisle_selling_units |
|------|-----------------------------------------|
| `tile-grid.sql` | `aaaca.mapping_l3 = 'TRUE'` |
| `tile-grid-test-group.sql` | `aaaca.mapping_l3_unique = 'TRUE'` |

- `mapping_l3 = 'TRUE'`: include all L3 categories that belong to this aisle (an L3 may appear in multiple aisles)
- `mapping_l3_unique = 'TRUE'`: include only L3 categories that belong **exclusively** to this aisle (strict, no cross-aisle L3s)

### Tile-Grid Ranking Logic (full pipeline)

The tile-grid query builds a personalized product list for a customer in an aisle section.
Pipeline in order:

1. **manual_favorite_selling_units** — get manually liked/unliked products
2. **manual_and_upcoming_articles** — combine upcoming delivery + just-delivered + manual favorites
3. **all_aisle_selling_units** — join with ranking model (`article_rank_per_group`) and L3 catalogue
4. **aisle_selling_units** — deduplicate to one SU per article (prefer: upcoming delivery → previous usual SU → last purchased → smallest count)
5. **blacklist_filtered_selling_units** — remove blacklisted, unliked, and Voedselbank (L3 `33060`)
6. **selling_units_rankers** — add rebuy_prob, del_count, rank_activity (Active=1, Passive=1, Churned=2, unknown=3)
7. **selling_units_with_replacements / expanded_selling_units / availability_selling_units** — add stock/availability per slot, expand to include alternatives
8. **all_selling_units** — pivot back to one row per original SU, with original + alternative availability
9. **valid_replacement_flag / replacement_candidates / availability_with_best** — apply replacement logic for LONG_TERM_UNAVAILABLE originals
10. **replaced_selling_unit_selection** — finalize SU and article selection (original or replacement)
11. **selection** — top `${sellingUnitLimit}` articles, ordered by delivery status → manual favorites → months_ago → article rank → rank_activity → rebuy_prob
12. **selection_ranked** — compute `global_rank` among previously bought articles
13. **Final ORDER BY** — upcoming delivery first tiles (first 3 reserved for non-upcoming), then just_delivered/newly bought, then degradation logic for unbought liked favorites

### File Locations

```
pages/picnic-pages/src/pages/aisle-shopping-root/
  components/partial-aisle/queries/
    tile-grid.sql              ← production ranking query
    tile-grid-test-group.sql   ← test group variant (mapping_l3_unique)
  queries/
    tile-grid-campaigns-query.sql   ← campaigns overlay
  components/grid/queries/
    tile-grid-campaign.sql          ← campaign tiles query
```
