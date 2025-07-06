import textwrap
from typing import List


def generate_sql_for_dataset(
    url: str,
    columns: List[dict],
    table_name: str,
    required_role_str: str,
    has_project_id_scope: bool,
    partitioning_key: str = None,
    materialization: str = None,
    enabled: bool = None,
    tags: List[str] = None,
):
    # Prepare a run_query statement to fetch datasets for the list of projects
    preflight_sql = textwrap.dedent(f"""
{{% set preflight_sql -%}}
SELECT
CONCAT('`', CATALOG_NAME, '`.`', SCHEMA_NAME, '`') AS SCHEMA_NAME
FROM `region-{{{{ dbt_bigquery_monitoring_variable_bq_region() }}}}`.`INFORMATION_SCHEMA`.`SCHEMATA`
{{%- endset %}}
{{% set results = run_query(preflight_sql) %}}
{{% set dataset_list = results | map(attribute='SCHEMA_NAME') | list %}}
{{%- if dataset_list | length == 0 -%}}
{{{{ log("No datasets found in the project list", info=False) }}}}
{{%- endif -%}}
""")

    # Prepare the column names as a comma-separated string
    column_names = [column["name"].lower() for column in columns]
    columns_str = ",\n".join(column_names)

    # Generate a SQL for fallback in case of no datasets
    columns_with_empty_values_arr = [
        f"CAST(NULL AS {column['data_type']}) AS {column['name'].lower()}"
        for column in columns
    ]
    columns_with_empty_values_str = ", ".join(columns_with_empty_values_arr)

    sql = textwrap.dedent(f"""{{# More details about base table in {url} -#}}
{required_role_str}
{preflight_sql}
WITH base AS (
{{%- if dataset_list | length == 0 -%}}
  SELECT {columns_with_empty_values_str}
  LIMIT 0
{{%- else %}}
{{% for dataset in dataset_list -%}}
  SELECT
  {columns_str}
  FROM {{{{ dataset | trim }}}}.`INFORMATION_SCHEMA`.`{table_name}`
{{% if not loop.last %}}UNION ALL{{% endif %}}
{{% endfor %}}
{{%- endif -%}}
)
SELECT
{columns_str}
FROM
base""")

    # Add config block if we have project scoping, custom materialization, enabled, or tags
    if has_project_id_scope or materialization or enabled is not None or tags:
        # Use custom materialization if provided, otherwise use default for project-scoped tables
        if materialization:
            config_block = f"{{{{ config(materialized='{materialization}'"
        else:
            config_block = (
                "{{ config(materialized=dbt_bigquery_monitoring_materialization()"
            )

        # Add enabled parameter
        if enabled is not None:
            config_block += f", enabled={'true' if enabled else 'false'}"

        # Add tags parameter
        if tags:
            tags_str = '["' + '", "'.join(tags) + '"]'
            config_block += f", tags={tags_str}"

        # Add partitioning configuration
        if partitioning_key:
            config_block += f", partition_by={{'field': '{partitioning_key}', 'data_type': 'timestamp', 'granularity': 'hour'}}, partition_expiration_days=180"
        config_block += ") }}"

        sql = f"""{config_block}
{sql}"""

    return sql


def generate_sql_for_table(
    url: str,
    columns: List[dict],
    table_name: str,
    required_role_str: str,
    has_project_id_scope: bool,
    partitioning_key: str,
    materialization: str = None,
    enabled: bool = None,
    tags: List[str] = None,
):
    # Prepare the column names as a comma-separated string
    column_names = [column["name"].lower() for column in columns]
    columns_str = ",\n".join(column_names)

    # Build the base query
    query = textwrap.dedent(f"""{{# More details about base table in {url} -#}}
{required_role_str}
SELECT
{columns_str}
FROM `region-{{{{ dbt_bigquery_monitoring_variable_bq_region() }}}}`.`INFORMATION_SCHEMA`.`{table_name}`""")

    # Add config block if we have project scoping, custom materialization, enabled, or tags
    if has_project_id_scope or materialization or enabled is not None or tags:
        # Use custom materialization if provided, otherwise use default for project-scoped tables
        if materialization:
            config_block = f"{{{{ config(materialized='{materialization}'"
        else:
            config_block = (
                "{{ config(materialized=dbt_bigquery_monitoring_materialization()"
            )

        # Add enabled parameter
        if enabled is not None:
            config_block += f", enabled={'true' if enabled else 'false'}"

        # Add tags parameter
        if tags:
            tags_str = '["' + '", "'.join(tags) + '"]'
            config_block += f", tags={tags_str}"

        # Add partitioning configuration
        if partitioning_key:
            config_block += f", partition_by={{'field': '{partitioning_key}', 'data_type': 'timestamp', 'granularity': 'hour'}}, partition_expiration_days=180"
        config_block += ") }}"

        query = f"""{config_block}
{query}"""

    return query


def generate_sql(
    url: str,
    columns: List[dict],
    table_name: str,
    required_role_str: str,
    type: str,
    has_project_id_scope: bool,
    partitioning_key: str = None,
    materialization: str = None,
    enabled: bool = None,
    tags: List[str] = None,
):
    if type == "table":
        return generate_sql_for_table(
            url,
            columns,
            table_name,
            required_role_str,
            has_project_id_scope,
            partitioning_key,
            materialization,
            enabled,
            tags,
        )
    elif type == "dataset":
        return generate_sql_for_dataset(
            url,
            columns,
            table_name,
            required_role_str,
            has_project_id_scope,
            partitioning_key,
            materialization,
            enabled,
            tags,
        )
    else:
        raise ValueError(f"Invalid type: {type}")
