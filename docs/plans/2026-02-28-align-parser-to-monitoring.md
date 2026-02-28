# Align Parser Output to dbt-bigquery-monitoring Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Update the parser generator and config so that regenerating output produces files that match the canonical `dbt-bigquery-monitoring` models.

**Architecture:** Four targeted changes: (1) comma style in `sql_generator.py`, (2) a `type_overrides` dict mechanism in `config.py` + `documentation_parser.py`, (3) missing experimental columns in `config.py`, (4) a `column_selection_macro` flag in `config.py` + `sql_generator.py`.

**Tech Stack:** Python 3.11+, `uv`, `pytest`, `beautifulsoup4`, `pyyaml`

---

## Background: Identified Diffs

Running `diff -r output/ ../dbt-bigquery-monitoring/models/information_schema/` reveals:

| Category | Files affected | Details |
|---|---|---|
| Comma style | All | Parser uses `  , col_name` (leading); monitoring uses `col_name,` (trailing) |
| Wrong types in docs | schemata_links, jobs_timeline x4, insights, recommendations x2, reservations x3, parameters | Google docs has STRING/FLOAT instead of INT64/FLOAT64/ARRAY\<STRING\> |
| Missing experimental cols | shared_dataset_usage, reservations, reservation_changes, reservations_timeline | `reservation_group_path`, `job_principal_subject` not marked experimental |
| Macro vs if-block | jobs x5, tables | Monitoring uses `dbt_bigquery_monitoring_get_column_selection()` macro |

**Exact type corrections needed:**
- `schemata_links.linked_schema_catalog_number`: STRING → INT64
- `jobs_timeline*.period_shuffle_ram_usage_ratio`: FLOAT → FLOAT64 (all 4 variants)
- `insights.target_resources`, `insights.associated_recommendation_ids`: STRING → ARRAY\<STRING\>
- `recommendations.target_resources`, `recommendations.associated_insight_ids`: STRING → ARRAY\<STRING\>
- `recommendations_by_organization` (same two columns): STRING → ARRAY\<STRING\>
- `reservations.reservation_group_path`, `reservation_changes.reservation_group_path`, `reservations_timeline.reservation_group_path`: STRING → ARRAY\<STRING\>
- `parameters.ordinal_position`: STRING → INT64

---

## Task 1: Fix comma style in `sql_generator.py`

**Files:**
- Modify: `sql_generator.py` — `build_columns_str()` and `build_columns_with_empty_values()`
- Modify: `tests/test_generate_sql_table_expected.sql` and all other `tests/test_generate_sql_*_expected.sql` files
- Modify: `tests/test_documentation_parser.py` — update any inline expected strings

**Context:** Currently `build_columns_str()` uses leading-comma style. The monitoring repo uses trailing-comma.

**Rule for trailing commas:**
- Every column gets a trailing comma EXCEPT the last in the list
- Experimental columns (wrapped in `{%- if %}`) always get a trailing comma inside the block
- Constraint: experimental columns must never be the last item in the list (monitoring enforces this by placement)
- `build_columns_with_empty_values()`: remove space before commas (`AS col , CAST` → `AS col, CAST`)

**Step 1: Update `build_columns_str()` in `sql_generator.py`**

Replace the current function:

```python
def build_columns_str(columns: List[dict]) -> str:
    # Find last non-experimental column index for trailing-comma logic
    last_regular_idx = max(
        (i for i, col in enumerate(columns) if not col.get("experimental")),
        default=len(columns) - 1,
    )

    parts = []
    for i, column in enumerate(columns):
        col_name = column["name"].lower()
        jinja_var_name = column.get("jinja_var", col_name)
        jinja_var = f"dbt_bigquery_monitoring_variable_enable_{jinja_var_name}()"
        is_last = i == last_regular_idx and not column.get("experimental")

        if column.get("experimental"):
            parts.append(f"{{%- if {jinja_var} %}}")
            parts.append(f"{col_name},")
            parts.append("{%- endif %}")
        else:
            parts.append(col_name if is_last else f"{col_name},")
    return "\n".join(parts)
```

Note the new `jinja_var_name = column.get("jinja_var", col_name)` — this supports Task 4 (variable overrides). For now it defaults to `col_name`.

**Step 2: Update `build_columns_with_empty_values()` in `sql_generator.py`**

Remove the space before commas in the `prefix` variable:

```python
def build_columns_with_empty_values(columns: List[dict]) -> str:
    parts = []
    for i, column in enumerate(columns):
        col_name = column["name"].lower()
        data_type = column["data_type"]
        val = f"CAST(NULL AS {data_type}) AS {col_name}"
        if column.get("experimental"):
            jinja_var_name = column.get("jinja_var", col_name)
            jinja_var = f"dbt_bigquery_monitoring_variable_enable_{jinja_var_name}()"
            prefix = "" if i == 0 else ", "
            parts.append(f"{{%- if {jinja_var} %}}{prefix}{val}{{%- endif %}}")
        else:
            prefix = "" if i == 0 else ", "
            parts.append(f"{prefix}{val}")
    return " ".join(parts)
```

**Step 3: Update all expected SQL fixture files in `tests/`**

For each `tests/test_generate_sql_*_expected.sql` file, update the column list from leading to trailing comma style. Example for `test_generate_sql_table_expected.sql`:

```sql
{{ config(materialized=dbt_bigquery_monitoring_materialization()) }}
{# More details about base table in https://cloud.google.com/bigquery/docs/information-schema-jobs -#}
jobs.admin
SELECT
field1,
field2,
field3
FROM `region-{{ dbt_bigquery_monitoring_variable_bq_region() }}`.`INFORMATION_SCHEMA`.`jobs`
```

Files to update:
- `tests/test_generate_sql_table_expected.sql`
- `tests/test_generate_sql_table_no_project_id_expected.sql`
- `tests/test_generate_sql_dataset_expected.sql`
- `tests/test_generate_sql_table_with_partitioning_key_expected.sql`
- `tests/test_generate_sql_table_with_custom_materialization_expected.sql`
- `tests/test_generate_sql_table_with_custom_materialization_and_project_scope_expected.sql`
- `tests/test_generate_sql_table_with_custom_materialization_and_partitioning_expected.sql`

**Step 4: Run tests to verify**

```bash
uv run pytest tests/test_documentation_parser.py -v -k "generate_sql"
```

Expected: All `generate_sql` tests PASS.

**Step 5: Run full test suite**

```bash
uv run pytest tests/ -v
```

Expected: All tests PASS.

**Step 6: Commit**

```bash
git add sql_generator.py tests/
git commit -m "feat: switch to trailing-comma style in SQL generator"
```

---

## Task 2: Add `type_overrides` mechanism

**Files:**
- Modify: `documentation_parser.py` — `update_column_list()` and `generate_files()`
- Test: `tests/test_documentation_parser.py` — add test case to `test_update_column_list()`

**Context:** Google's documentation occasionally lists the wrong BigQuery type for a column. A `type_overrides` dict in a config entry maps `column_name → correct_type`. This is applied in `update_column_list()`.

**Step 1: Write the failing test in `tests/test_documentation_parser.py`**

Add this test case inside `test_update_column_list()` (after the existing cases):

```python
# Test case: type_overrides corrects wrong types from docs
columns_for_override = [
    {"name": "col_a", "type": "STRING", "description": "Column A"},
    {"name": "col_b", "type": "FLOAT", "description": "Column B"},
    {"name": "col_c", "type": "STRING", "description": "Column C"},
]
result = update_column_list(
    columns_for_override,
    exclude_columns=[],
    type_overrides={"col_b": "FLOAT64", "col_c": "ARRAY<STRING>"},
)
assert result[0]["type"] == "STRING"   # unchanged
assert result[1]["type"] == "FLOAT64"  # overridden
assert result[2]["type"] == "ARRAY<STRING>"  # overridden
```

**Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_documentation_parser.py::test_update_column_list -v
```

Expected: FAIL — `update_column_list()` does not accept `type_overrides` parameter.

**Step 3: Update `update_column_list()` in `documentation_parser.py`**

Add `type_overrides: dict = None` parameter and apply it after all column processing:

```python
def update_column_list(
    input_columns: List[dict],
    exclude_columns: List[str],
    experimental_columns: List[str] = None,
    field_mappings: dict = None,
    type_overrides: dict = None,
):
    # ... existing logic unchanged ...

    # Apply type overrides (fixes wrong types in Google's documentation)
    if type_overrides:
        for column in columns:
            if column["name"].lower() in {k.lower() for k in type_overrides}:
                for override_name, override_type in type_overrides.items():
                    if column["name"].lower() == override_name.lower():
                        column["type"] = override_type

    return columns
```

Also update `generate_files()` signature to accept and pass `type_overrides`:

```python
def generate_files(
    filename: str,
    dir: str,
    url: str,
    exclude_columns: List[str],
    experimental_columns: List[str],
    override_table_name: str,
    type: str,
    materialization: str = None,
    enabled: bool = None,
    tags: List[str] = None,
    field_mappings: dict = None,
    type_overrides: dict = None,
):
    # ... existing code ...
    columns = update_column_list(
        columns, exclude_columns, experimental_columns, field_mappings, type_overrides
    )
```

And update `generate_all()` and `generate_for_key()` to pass `target.get("type_overrides")`.

**Step 4: Run tests**

```bash
uv run pytest tests/test_documentation_parser.py::test_update_column_list -v
```

Expected: PASS.

**Step 5: Run full test suite**

```bash
uv run pytest tests/ -v
```

Expected: All tests PASS.

**Step 6: Commit**

```bash
git add documentation_parser.py tests/test_documentation_parser.py
git commit -m "feat: add type_overrides support to update_column_list()"
```

---

## Task 3: Add `experimental_variable_overrides` mechanism

**Files:**
- Modify: `documentation_parser.py` — `update_column_list()`
- Test: `tests/test_documentation_parser.py`

**Context:** Some experimental columns use a different Jinja variable name than the column name. For example, `shared_dataset_usage.job_principal_subject` is controlled by `enable_principal_subject()`. A new `experimental_variable_overrides: dict[str, str]` config key maps `column_name → variable_name`.

**Step 1: Write the failing test**

Add to `test_update_column_list()`:

```python
# Test case: experimental_variable_overrides sets custom jinja_var
columns_var_override = [
    {"name": "job_principal_subject", "type": "STRING", "description": "Job principal"},
]
result = update_column_list(
    columns_var_override,
    exclude_columns=[],
    experimental_columns=["job_principal_subject"],
    experimental_variable_overrides={"job_principal_subject": "principal_subject"},
)
assert result[0]["experimental"] is True
assert result[0].get("jinja_var") == "principal_subject"
```

**Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_documentation_parser.py::test_update_column_list -v
```

**Step 3: Update `update_column_list()` in `documentation_parser.py`**

Add `experimental_variable_overrides: dict = None` parameter. After marking columns as experimental, set `jinja_var` if override exists:

```python
def update_column_list(
    input_columns: List[dict],
    exclude_columns: List[str],
    experimental_columns: List[str] = None,
    field_mappings: dict = None,
    type_overrides: dict = None,
    experimental_variable_overrides: dict = None,
):
    # ... existing logic for experimental marking ...

    # Apply experimental variable overrides (for columns whose Jinja variable name
    # differs from the column name, e.g. job_principal_subject → principal_subject)
    if experimental_variable_overrides:
        for column in columns:
            override_key = column["name"].lower()
            if override_key in {k.lower() for k in experimental_variable_overrides}:
                for col_name, var_name in experimental_variable_overrides.items():
                    if override_key == col_name.lower():
                        column["jinja_var"] = var_name

    # Apply type overrides ...
    return columns
```

Also thread `experimental_variable_overrides` through `generate_files()`, `generate_all()`, and `generate_for_key()`.

**Step 4: Run tests**

```bash
uv run pytest tests/ -v
```

Expected: All PASS.

**Step 5: Commit**

```bash
git add documentation_parser.py tests/test_documentation_parser.py
git commit -m "feat: add experimental_variable_overrides support"
```

---

## Task 4: Apply type_overrides and experimental_columns fixes in `config.py`

**Files:**
- Modify: `config.py`

**Context:** Apply the two new mechanisms (`type_overrides`, `experimental_variable_overrides`) to config entries that need them, and add missing experimental columns.

**Step 1: Add type_overrides to affected entries in `config.py`**

```python
# schemata_links
"schemata_links": {
    "dir": "datasets",
    "url": "...",
    "type_overrides": {
        "linked_schema_catalog_number": "INT64",
    },
},

# jobs_timeline (all 4 variants: jobs_timeline, jobs_timeline_by_user,
# jobs_timeline_by_folder, jobs_timeline_by_organization)
"jobs_timeline": {
    "dir": "jobs_timeline",
    "url": "...",
    "type_overrides": {
        "period_shuffle_ram_usage_ratio": "FLOAT64",
    },
    # ... rest unchanged
},

# insights
"insights": {
    "dir": "recommendations_and_insights",
    "url": "...",
    "type_overrides": {
        "target_resources": "ARRAY<STRING>",
        "associated_recommendation_ids": "ARRAY<STRING>",
    },
},

# recommendations
"recommendations": {
    "dir": "recommendations_and_insights",
    "url": "...",
    "type_overrides": {
        "target_resources": "ARRAY<STRING>",
        "associated_insight_ids": "ARRAY<STRING>",
    },
},

# recommendations_by_organization (same overrides as recommendations)
"recommendations_by_organization": {
    ...
    "type_overrides": {
        "target_resources": "ARRAY<STRING>",
        "associated_insight_ids": "ARRAY<STRING>",
    },
},

# reservations, reservation_changes, reservations_timeline
"reservations": {
    ...
    "experimental_columns": ["reservation_group_path"],
    "type_overrides": {
        "reservation_group_path": "ARRAY<STRING>",
    },
},
"reservation_changes": {
    ...
    "experimental_columns": ["reservation_group_path"],
    "type_overrides": {
        "reservation_group_path": "ARRAY<STRING>",
    },
},
"reservations_timeline": {
    ...
    "experimental_columns": ["reservation_group_path"],
    "type_overrides": {
        "reservation_group_path": "ARRAY<STRING>",
    },
},

# parameters
"parameters": {
    "dir": "routines",
    "url": "...",
    "type_overrides": {
        "ordinal_position": "INT64",
    },
},
```

**Step 2: Add `job_principal_subject` as experimental with variable override in `shared_dataset_usage`**

```python
"shared_dataset_usage": {
    "dir": "datasets",
    "url": "...",
    "experimental_columns": ["job_principal_subject"],
    "experimental_variable_overrides": {
        "job_principal_subject": "principal_subject",
    },
},
```

**Step 3: Verify the changes look correct by running ruff**

```bash
uv run ruff check config.py && uv run ruff format config.py
```

**Step 4: Run full test suite**

```bash
uv run pytest tests/ -v
```

Expected: All PASS (no test exercises actual config entries directly).

**Step 5: Commit**

```bash
git add config.py
git commit -m "fix: add type_overrides and experimental column fixes to config"
```

---

## Task 5: Add `column_selection_macro` support to `sql_generator.py`

**Files:**
- Modify: `sql_generator.py` — `generate_sql_for_table()` and `generate_sql_for_dataset()`
- Test: `tests/test_documentation_parser.py` — add test case
- Create: `tests/test_generate_sql_table_with_column_selection_macro_expected.sql`

**Context:** When `column_selection_macro=True`, experimental columns are emitted as a single `{{ dbt_bigquery_monitoring_get_column_selection(...) }}` macro call instead of individual `{%- if %}` blocks. The macro accepts `(region, table_name, columns_list)`.

The macro call always has a trailing comma and is placed where the experimental columns would normally appear in the list. Non-experimental columns before and after render normally.

**Step 1: Create the expected SQL fixture file**

Create `tests/test_generate_sql_table_with_column_selection_macro_expected.sql`:

```sql
{{ config(materialized=dbt_bigquery_monitoring_materialization()) }}
{# More details about base table in https://cloud.google.com/bigquery/docs/information-schema-jobs -#}
jobs.admin
SELECT
field1,
{{ dbt_bigquery_monitoring_get_column_selection(
    dbt_bigquery_monitoring_variable_bq_region(),
    'jobs',
    [
        {'name': 'field2', 'type': 'INTEGER'},
        {'name': 'field3', 'type': 'STRING'}
    ]
) }},
field4
FROM `region-{{ dbt_bigquery_monitoring_variable_bq_region() }}`.`INFORMATION_SCHEMA`.`jobs`
```

(Use columns: `field1` regular, `field2` + `field3` experimental, `field4` regular after)

**Step 2: Write the failing test**

Add to `tests/test_documentation_parser.py`:

```python
def test_generate_sql_table_with_column_selection_macro():
    columns = [
        {"name": "field1", "data_type": "STRING", "description": "Field 1", "experimental": False},
        {"name": "field2", "data_type": "INTEGER", "description": "Field 2", "experimental": True},
        {"name": "field3", "data_type": "STRING", "description": "Field 3", "experimental": True},
        {"name": "field4", "data_type": "STRING", "description": "Field 4", "experimental": False},
    ]
    result = generate_sql(
        "https://cloud.google.com/bigquery/docs/information-schema-jobs",
        columns,
        "jobs",
        "jobs.admin",
        "table",
        has_project_id_scope=True,
        column_selection_macro=True,
    )
    with open(TESTS_DIR / "test_generate_sql_table_with_column_selection_macro_expected.sql") as f:
        expected = f.read()
    assert result == expected
```

**Step 3: Run test to verify it fails**

```bash
uv run pytest tests/test_documentation_parser.py::test_generate_sql_table_with_column_selection_macro -v
```

**Step 4: Add `build_column_selection_macro_str()` helper to `sql_generator.py`**

```python
def build_column_selection_macro_str(table_name: str, experimental_columns: List[dict]) -> str:
    """Emit the dbt_bigquery_monitoring_get_column_selection macro call for experimental columns."""
    col_entries = "\n".join(
        f"        {{'name': '{col['name'].lower()}', 'type': '{col['data_type']}'}}"
        for col in experimental_columns
    )
    return (
        f"{{{{ dbt_bigquery_monitoring_get_column_selection(\n"
        f"    dbt_bigquery_monitoring_variable_bq_region(),\n"
        f"    '{table_name}',\n"
        f"    [\n"
        f"{col_entries}\n"
        f"    ]\n"
        f") }}}}"
    )
```

**Step 5: Update `build_columns_str()` to accept `column_selection_macro` and `table_name`**

```python
def build_columns_str(
    columns: List[dict],
    column_selection_macro: bool = False,
    table_name: str = None,
) -> str:
    if column_selection_macro:
        regular = [c for c in columns if not c.get("experimental")]
        experimental = [c for c in columns if c.get("experimental")]
        parts = []
        # Split regular columns into those before and after experimental
        # For simplicity: emit all regular first, then macro, then no more regular
        # (Ordering comes from the column list order - find insertion point)
        exp_start = next((i for i, c in enumerate(columns) if c.get("experimental")), len(columns))
        before_exp = [c for c in columns[:exp_start] if not c.get("experimental")]
        after_exp = [c for c in columns[exp_start:] if not c.get("experimental")]
        
        for col in before_exp:
            parts.append(f"{col['name'].lower()},")
        if experimental:
            parts.append(build_column_selection_macro_str(table_name, experimental) + ",")
        for i, col in enumerate(after_exp):
            is_last = (i == len(after_exp) - 1)
            parts.append(col["name"].lower() if is_last else f"{col['name'].lower()},")
        return "\n".join(parts)
    
    # ... existing trailing-comma logic unchanged ...
```

Update `generate_sql_for_table()` and `generate_sql_for_dataset()` to accept and pass `column_selection_macro` + `table_name` to `build_columns_str()`.

Update `generate_sql()` to accept and pass `column_selection_macro=False`.

**Step 6: Run tests**

```bash
uv run pytest tests/test_documentation_parser.py::test_generate_sql_table_with_column_selection_macro -v
```

Expected: PASS.

**Step 7: Run full test suite**

```bash
uv run pytest tests/ -v
```

Expected: All PASS.

**Step 8: Commit**

```bash
git add sql_generator.py tests/
git commit -m "feat: add column_selection_macro support to SQL generator"
```

---

## Task 6: Apply `column_selection_macro` flag to config entries

**Files:**
- Modify: `config.py`
- Modify: `documentation_parser.py` — thread `column_selection_macro` through `generate_files()`

**Context:** Jobs (all 5 variants) and `tables` use the `get_column_selection` macro in the monitoring repo.

**Step 1: Thread `column_selection_macro` through `generate_files()`**

Add `column_selection_macro: bool = False` parameter to `generate_files()`. Pass it to `generate_sql()`. Also update `generate_all()` and `generate_for_key()` to pass `target.get("column_selection_macro", False)`.

**Step 2: Add `column_selection_macro: True` to config entries**

```python
"jobs": {
    ...
    "column_selection_macro": True,
    "experimental_columns": [
        "total_services_sku_slot_ms",
        "principal_subject",
    ],
},
# Same for: jobs_by_project, jobs_by_user, jobs_by_folder, jobs_by_organization
"tables": {
    ...
    "column_selection_macro": True,
    "experimental_columns": ["managed_table_type"],
    # managed_table_type is currently in exclude_columns — move it to experimental
},
```

Note for `tables`: `managed_table_type` is currently in `exclude_columns`. Remove it from there and add it to `experimental_columns` to make it macro-controlled.

**Step 3: Run full test suite**

```bash
uv run pytest tests/ -v
```

Expected: All PASS.

**Step 4: Run ruff**

```bash
uv run ruff check config.py documentation_parser.py sql_generator.py
```

**Step 5: Commit**

```bash
git add config.py documentation_parser.py
git commit -m "feat: apply column_selection_macro to jobs and tables config entries"
```

---

## Task 7: Verify end-to-end output

**Context:** After all code changes, regenerate a few key files and diff against the monitoring repo to confirm alignment.

**Step 1: Regenerate a few key files**

```bash
uv run python documentation_parser.py reservations
uv run python documentation_parser.py jobs
uv run python documentation_parser.py insights
```

**Step 2: Diff against monitoring repo**

```bash
diff output/reservations/information_schema_reservations.sql \
  ../dbt-bigquery-monitoring/models/information_schema/reservations/information_schema_reservations.sql

diff output/jobs/information_schema_jobs.sql \
  ../dbt-bigquery-monitoring/models/information_schema/jobs/information_schema_jobs.sql
```

Expected: Only differences should be in content that was manually added to monitoring (e.g., `materialized_view_statistics` column in jobs which doesn't come from docs).

**Step 3: Final full test run**

```bash
uv run pytest tests/ -v
```

**Step 4: Commit summary**

```bash
git commit --allow-empty -m "chore: verify parser output aligns with dbt-bigquery-monitoring"
```

---

## Out of Scope

- `sessions_by_user.yml` `principal_subject` entry: monitoring added this manually to YML only (not in docs, not in SQL). Requires a new `extra_yml_columns` mechanism — deferred.
- `jobs.sql` `materialized_view_statistics` column: manually added in monitoring, not from docs. Not generated by parser.
- `jobs.yml` description differences: monitoring has curated descriptions for `total_services_sku_slot_ms` and `principal_subject` — parser uses raw doc text.
