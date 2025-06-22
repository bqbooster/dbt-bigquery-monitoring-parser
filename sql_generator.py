import textwrap
from typing import List

def generate_sql_for_dataset(url: str, columns: List[dict], table_name: str, required_role_str: str):
    # Prepare a run_query statement to fetch datasets for the list of projects
    preflight_sql = textwrap.dedent(f"""
{{% set preflight_sql -%}}
SELECT
CONCAT('`', CATALOG_NAME, '`.`', SCHEMA_NAME, '`') AS SCHEMA_NAME
FROM `region-{{{{ var('bq_region') }}}}`.`INFORMATION_SCHEMA`.`SCHEMATA`
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
    columns_with_empty_values_arr = [f"CAST(NULL AS {column['type']}) AS {column['name'].lower()}" for column in columns]
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
  FROM {{{{ dataset | trim }}}}.`INFORMATION_SCHEMA`.`PARTITIONS`
{{% if not loop.last %}}UNION ALL{{% endif %}}
{{% endfor %}}
{{%- endif -%}}
)
SELECT
{columns_str},
FROM
base""")

    return sql

def generate_sql_for_table(url: str, columns: List[dict], table_name: str, required_role_str: str, has_project_id_scope: bool, partitioning_key: str, materialization: str = None):
    # Prepare the column names as a comma-separated string
    column_names = [column["name"].lower() for column in columns]
    columns_str = ",\n".join(column_names)

    # Build the base query
    query = textwrap.dedent(f"""{{# More details about base table in {url} -#}}
{required_role_str}
SELECT
{columns_str}
FROM `region-{{{{ var('bq_region') }}}}`.`INFORMATION_SCHEMA`.`{table_name}`""")
    
    # Add config block if we have project scoping or custom materialization
    if has_project_id_scope or materialization:
        # Use custom materialization if provided, otherwise use default for project-scoped tables
        if materialization:
            config_block = f"{{{{ config(materialized='{materialization}'"
        else:
            config_block = "{{ config(materialized=dbt_bigquery_monitoring_materialization()"
        
        if partitioning_key:
            config_block += f", partition_by={{'field': '{partitioning_key}', 'data_type': 'timestamp', 'granularity': 'hour'}}, partition_expiration_days=180"
        config_block += ") }}"
        query = textwrap.dedent(f"""{config_block}
{query}
  """)

    return query

def generate_sql(url: str, columns: List[dict], table_name: str, required_role_str: str, type: str, has_project_id_scope: bool, partitioning_key: str = None, materialization: str = None):
    if type == "table":
        return generate_sql_for_table(url, columns, table_name, required_role_str, has_project_id_scope, partitioning_key, materialization)
    elif type == "dataset":
        return generate_sql_for_dataset(url, columns, table_name, required_role_str)
    else:
        raise ValueError(f"Invalid type: {type}")
