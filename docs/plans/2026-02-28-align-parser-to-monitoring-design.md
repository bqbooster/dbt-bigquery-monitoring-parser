# Design: Align Parser Output to dbt-bigquery-monitoring

## Problem

The parser's generated output in `output/` has drifted from the canonical
`dbt-bigquery-monitoring` models. Differences fall into four categories:

1. **Comma style** — parser uses leading commas; monitoring uses trailing commas.
2. **Type corrections** — Google's documentation contains wrong types for several
   columns; monitoring has manually corrected them.
3. **Missing experimental columns** — three config entries are missing
   `principal_subject` or `reservation_group_path` experimental columns.
4. **Column selection macro** — jobs and tables models in monitoring use
   `dbt_bigquery_monitoring_get_column_selection()` instead of inline Jinja
   `{%- if %}` blocks for runtime-optional columns.

## Approach

Minimal targeted changes across three files: `config.py`,
`documentation_parser.py`, and `sql_generator.py`.

## Section 1: Comma Style (`sql_generator.py`)

Change `build_columns_str()` from leading-comma to trailing-comma style.
Last column has no trailing comma. Experimental `{%- if %}` wrapper columns
place the comma on the preceding line.

Change `build_columns_with_empty_values()` to remove the space before commas
in the empty-value SELECT.

## Section 2: Type Overrides (`config.py` + `documentation_parser.py`)

Add an optional `type_overrides: dict[str, str]` key to config entries.
Applied in `update_column_list()` after parsing column types from the docs.

Config entries requiring `type_overrides`:

| Entry | Column | Docs Type | Correct Type |
|---|---|---|---|
| `schemata_links` | `linked_schema_catalog_number` | STRING | INT64 |
| `jobs_timeline` (all 4 variants) | `period_slot_ms` | FLOAT | FLOAT64 |
| `insights` | `associated_insights`, `associated_recommendations` | STRING | ARRAY\<STRING\> |
| `recommendations`, `recommendations_by_organization` | same two columns | STRING | ARRAY\<STRING\> |
| `reservation_changes`, `reservations`, `reservations_timeline` | `autoscale` (or relevant field) | STRING | ARRAY\<STRING\> |
| `parameters` | `ordinal_position` | STRING | INT64 |

## Section 3: Missing Experimental Columns (`config.py`)

Extend `experimental_columns` lists:

- `shared_dataset_usage`: add `"principal_subject"`
- `sessions_by_user`: add `"principal_subject"`
- `reservations`, `reservation_changes`, `reservations_timeline`: add `"reservation_group_path"`

## Section 4: Column Selection Macro (`config.py` + `sql_generator.py`)

Add optional `column_selection_macro: bool` flag to config entries. When
`True`, `sql_generator.py` emits the runtime column check macro instead of
inline Jinja if-blocks for experimental columns:

```sql
{{ dbt_bigquery_monitoring_get_column_selection(
    dbt_bigquery_monitoring_variable_bq_region(),
    'TABLE_NAME',
    [
        {'name': 'col1', 'type': 'INT64'},
        {'name': 'col2', 'type': 'STRING'}
    ]
) }},
```

Config entries that get `column_selection_macro: True`:
`jobs`, `jobs_by_project`, `jobs_by_user`, `jobs_by_folder`,
`jobs_by_organization`, `tables`.

## Section 5: Testing

- Update existing expected fixture files to reflect trailing-comma style.
- Add `type_overrides` test case in `test_update_column_list()`.
- Add `column_selection_macro` test case using a new expected SQL fixture.
- Run: `uv run pytest tests/`
