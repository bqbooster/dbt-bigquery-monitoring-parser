import textwrap
from typing import List


def build_columns_str(columns: List[dict]) -> str:
    column_names = []
    regular_column_indexes = [
        index for index, column in enumerate(columns) if not column.get("experimental")
    ]
    if not regular_column_indexes:
        column_names.append("{%- set has_columns = namespace(value=false) %}")
        for column in columns:
            column_name = column["name"].lower()
            jinja_var_name = column.get("jinja_var") or column_name
            jinja_var = f"dbt_bigquery_monitoring_variable_enable_{jinja_var_name}()"
            column_names.append(
                f"{{%- if {jinja_var} %}}"
                "{%- if has_columns.value %},{%- endif %}"
                f"{column_name}"
                "{%- set has_columns.value = true %}{%- endif %}"
            )
        return "\n".join(column_names)

    last_regular_column_index = (
        regular_column_indexes[-1] if regular_column_indexes else len(columns) - 1
    )

    for index, column in enumerate(columns):
        column_name = column["name"].lower()
        if column.get("experimental"):
            jinja_var_name = column.get("jinja_var") or column_name
            jinja_var = (
                f"dbt_bigquery_monitoring_variable_enable_{jinja_var_name}()"
            )
            has_regular_column_after = any(
                not next_column.get("experimental")
                for next_column in columns[index + 1 :]
            )
            if has_regular_column_after:
                column_names.append(
                    f"{{%- if {jinja_var} %}}{column_name},{{%- endif %}}"
                )
            else:
                column_names.append(
                    f"{{%- if {jinja_var} %}},{column_name}{{%- endif %}}"
                )
        else:
            suffix = "," if index != last_regular_column_index else ""
            column_names.append(f"{column_name}{suffix}")
    return "\n".join(column_names)


def build_columns_with_empty_values(columns: List[dict]) -> str:
    empty_columns = []
    regular_column_indexes = [
        index for index, column in enumerate(columns) if not column.get("experimental")
    ]
    if not regular_column_indexes:
        empty_columns.append("{%- set has_columns = namespace(value=false) %}")
        for column in columns:
            empty_column = (
                f"CAST(NULL AS {column['data_type']}) AS {column['name'].lower()}"
            )
            jinja_var_name = column.get("jinja_var") or column["name"].lower()
            jinja_var = f"dbt_bigquery_monitoring_variable_enable_{jinja_var_name}()"
            empty_columns.append(
                f"{{%- if {jinja_var} %}}"
                "{%- if has_columns.value %}, {%- endif %}"
                f"{empty_column}"
                "{%- set has_columns.value = true %}{%- endif %}"
            )
        return " ".join(empty_columns)

    last_regular_column_index = (
        regular_column_indexes[-1] if regular_column_indexes else len(columns) - 1
    )

    for index, column in enumerate(columns):
        empty_column = f"CAST(NULL AS {column['data_type']}) AS {column['name'].lower()}"
        if column.get("experimental"):
            jinja_var_name = column.get("jinja_var") or column["name"].lower()
            jinja_var = (
                f"dbt_bigquery_monitoring_variable_enable_{jinja_var_name}()"
            )
            has_regular_column_after = any(
                not next_column.get("experimental")
                for next_column in columns[index + 1 :]
            )
            if has_regular_column_after:
                empty_columns.append(
                    f"{{%- if {jinja_var} %}}{empty_column}, {{%- endif %}}"
                )
            else:
                empty_columns.append(
                    f"{{%- if {jinja_var} %}}, {empty_column}{{%- endif %}}"
                )
        else:
            suffix = "," if index != last_regular_column_index else ""
            empty_columns.append(f"{empty_column}{suffix}")
    return " ".join(empty_columns)


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
    preflight_sql = "{% set dataset_list = get_dataset_list() %}"

    # Prepare the column names as a comma-separated string
    columns_str = build_columns_str(columns)

    # Generate a SQL for fallback in case of no datasets
    columns_with_empty_values_str = build_columns_with_empty_values(columns)

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
    columns_str = build_columns_str(columns)

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
