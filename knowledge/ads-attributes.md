# Skill: Create & Manage ADS Attributes

## What this covers
Reading and writing data in Picnic's Attribute Data Store (ADS) — checking values,
creating new attributes, upserting/replacing values, and understanding the data model.

## When to use
When reading ADS configuration (section clusters, assortment mappings), creating new
attributes for testing, or upserting values (e.g. assortment-section mapping uploads).

## How to do it

### Read attribute values
```
/ads nl usuals_section_clusters(assortment_aisle) --env prod --limit 20
/ads nl mapping_l3(assortment_aisle,assortment_category) --env prod --limit 10
```

### Create an attribute
```
/ads nl my_new_attr customer --create STRING --description "My description"
```
→ **Always create in dev first**, then verify before using prod.

### Write values
```
/ads nl maarten_de_jong_test(customer) 306-090-0528 --upsert "value"   # PATCH — adds/updates
/ads nl mapping_l3(assortment_aisle,assortment_category) BABY,22447 --replace true --env prod  # PUT
```
- **Upsert (PATCH)**: adds/updates without touching other entities — use for mapping uploads
- **Replace (PUT)**: wipes ALL existing values for the attribute — use with caution

For mapping uploads: always UPSERT not REPLACE (REPLACE wipes all existing mappings).

### Output location
Results saved to: `~/.claude/skills/ads/app/output/<attribute>.json`
(Not in `~/.claude/data/` — different from snowflake-query)

---

## Reference: Conventions & Patterns

### What It Is
Picnic's internal key-value store for customer and assortment configuration.
Used by the Usuals page (and other features) to store per-entity config values.

Access via: `/ads` skill or the `ads` Skill tool directly.
UI: Store Studio — `store-studio-prod.{market}.picnicinternational.com/data-editor/`

### Data Model

#### Dimensions
Attributes are indexed by one or more **dimensions** (the "entity type").
Common dimensions:
- `customer` — entity is a customer ID (e.g., `306-090-0528`)
- `id` — entity is a UUID (e.g., for aisle config)
- `assortment_aisle` — entity is an aisle code (e.g., `FRUIT`, `BABY`)
- Multi-dim example: `mapping_l3(assortment_aisle,assortment_category)` — two entities per value

#### Value types
`STRING`, `LABEL`, `CLASS`, `JSON`, `FLOAT`, `INTEGER`, `LONG`, `TIMESTAMP`
JSON values are stored as strings — parse with `parse_json()` / `get_path()` in Snowflake.

#### Attribute ID format
- Full ID includes dimensions: `attribute_name(dim1,dim2)`
- Example: `mapping_l3(assortment_aisle,assortment_category)`
- Bare name used for create/describe: `mapping_l3`

### Important Notes
- Default env is `dev` — always specify `--env prod` for production reads/writes
- Auth: browser-based Keycloak login (opens browser on first use per session)
- DWH mirror: `ft_attribute_data_store_values` — JSON values, use `get_path()` / `parse_json()`
- For mapping uploads: always UPSERT not REPLACE

### Maarten's Customer ID
`306-090-0528` — useful for testing customer-dimension attributes

### Attributes Explored (NL, dev unless noted)

#### `assortment_aisle_configuration(id)`
- Entity: UUID (not the aisle code)
- Value: JSON string with fields:
  - `is_fallback`: bool
  - `display_name`: human-readable (e.g., "Fruit")
  - `assortment_aisle`: aisle code (e.g., "FRUIT")
  - `primary_color` / `secondary_color`: hex
  - `default_priority`: integer ranking (lower = higher priority)
- Known aisles: FRUIT (1), MEAT_FISH_VEGA (4), DRINKS (9), SNACKS (10), FROZEN (13)

#### `usuals_section_clusters(assortment_aisle)`
- Entity: aisle code (e.g., `DAIRY`, `FRUIT`, `BABY`)
- Value: cluster string — `CORE_FRESH`, `FRESH_FOOD`, `NON_FRESH`, `NON_FOOD`
- Cluster ranking (section display order): CORE_FRESH → FRESH_FOOD → NON_FRESH → NON_FOOD
- Full aisle→cluster map (NL dev, 2026-02-21):

  | Aisle | Cluster |
  |-------|---------|
  | DAIRY | CORE_FRESH |
  | FRUIT | CORE_FRESH |
  | BAKERY | FRESH_FOOD |
  | DELI | FRESH_FOOD |
  | MEALS | FRESH_FOOD |
  | DRINKS | NON_FRESH |
  | FROZEN | NON_FRESH |
  | GRAINS_SWEETSPREADS | NON_FRESH |
  | BABY | NON_FOOD |
  | DRUGSTORE | NON_FOOD |

#### `mapping_l3(assortment_aisle,assortment_category)`
- Two-dimensional: `[aisle_code, l3_category_id]`
- Value: `true` (boolean) — presence = this L3 belongs to this aisle
- Used for assortment-section mapping workflow (CSV upload, UPSERT not REPLACE)
- Sample entries: BABY → [22447, 22816, 22817, 22818, 22819]

### Test Attributes Created (dev)

#### `maarten_de_jong_test(customer)`
- Created by Maarten to test write flow
- Type: STRING, dimension: customer
- Entity `306-090-0528` = Maarten's own customer ID → value "Maarten de Jong"
- Created: 2026-02-27

#### `claude_test_attribute(customer)`
- Created during same session — empty (no values written)
