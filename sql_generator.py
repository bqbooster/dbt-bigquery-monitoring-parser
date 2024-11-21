import textwrap
from typing import List

def generate_sql_for_dataset(url: str, columns: List[dict], table_name: str, required_role_str: str):
    # Prepare a run_query statement to fetch datasets for the list of projects
    preflight_sql = f"""
    {{% set preflight_sql -%}}
    {{% if project_list()|length > 0 -%}}
    {{% for project in project_list() -%}}
    SELECT
    CONCAT('`', CATALOG_NAME, '`.`', SCHEMA_NAME, '`') AS SCHEMA_NAME
    FROM `{{{{ project | trim }}}}`.`region-{{{{ var('bq_region') }}}}`.`INFORMATION_SCHEMA`.`SCHEMATA`
    {{% if not loop.last %}}UNION ALL{{% endif %}}
    {{% endfor %}}
    {{%- else %}}
    SELECT
    CONCAT('`', CATALOG_NAME, '`.`', SCHEMA_NAME, '`') AS SCHEMA_NAME
    FROM `region-{{{{ var('bq_region') }}}}`.`INFORMATION_SCHEMA`.`SCHEMATA`
    {{%- endif %}}
    {{%- endset %}}
    {{% set results = run_query(preflight_sql) %}}
    {{% set dataset_list = results | map(attribute='SCHEMA_NAME') | list %}}
    {{%- if dataset_list | length == 0 -%}}
    {{{{ log("No datasets found in the project list", info=True) }}}}
    {{%- endif -%}}
    """

    # Prepare the column names as a comma-separated string
    column_names = [column["name"].lower() for column in columns]
    columns_str = ", ".join(column_names)

    # Generate a SQL for fallback in case of no datasets
    columns_with_empty_values_arr = [f"CAST(NULL AS {column['type']}) AS {column['name'].lower()}" for column in columns]
    columns_with_empty_values_str = ", ".join(columns_with_empty_values_arr)

    sql = f"""
    {{# More details about base table in {url} -#}}
    {required_role_str}
    {preflight_sql}
    WITH base AS (
    {{%- if dataset_list | length == 0 -%}}
      SELECT {columns_with_empty_values_str}
      LIMIT 0
    {{%- else %}}
    {{% for dataset in dataset_list -%}}
      SELECT {columns_str}
      FROM {{{{ dataset | trim }}}}.`INFORMATION_SCHEMA`.`PARTITIONS`
    {{% if not loop.last %}}UNION ALL{{% endif %}}
    {{% endfor %}}
    {{%- endif -%}}
    )
    SELECT
    {columns_str},
    FROM
    base
    """

    return sql

def generate_sql_for_table(url: str, columns: List[dict], table_name: str, required_role_str: str, has_project_id_scope: bool):
  # Prepare the column names as a comma-separated string
  column_names = [column["name"].lower() for column in columns]
  columns_str = ", ".join(column_names)

  # Build the base query
  base_query = textwrap.dedent(f"""SELECT {columns_str}
FROM `region-{{{{ var('bq_region') }}}}`.`INFORMATION_SCHEMA`.`{table_name}`""")

  # Add project-scoped query if needed
  if has_project_id_scope:
    base_query = textwrap.dedent(f"""{{% if project_list()|length > 0 -%}}
  {{% for project in project_list() -%}}
  SELECT {columns_str}
  FROM `{{{{ project | trim }}}}`.`region-{{{{ var('bq_region') }}}}`.`INFORMATION_SCHEMA`.`{table_name}`
  {{% if not loop.last %}}UNION ALL{{% endif %}}
  {{% endfor %}}
{{%- else %}}
  {base_query}
{{%- endif %}}""")

  # Combine everything into the final SQL string
  sql = textwrap.dedent(f"""{{# More details about base table in {url} -#}}
{required_role_str}
WITH base AS (
  {base_query}
)
SELECT
{columns_str},
FROM
base
""")
  return sql


def generate_sql(url: str, columns: List[dict], table_name: str, required_role_str: str, type: str, has_project_id_scope: bool):
    if type == "table":
        return generate_sql_for_table(url, columns, table_name, required_role_str, has_project_id_scope)
    elif type == "dataset":
        return generate_sql_for_dataset(url, columns, table_name, required_role_str)
    else:
        raise ValueError(f"Invalid type: {type}")
