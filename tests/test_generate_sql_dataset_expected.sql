
    {# More details about base table in https://cloud.google.com/bigquery/docs/information-schema-jobs -#}
    jobs.admin
    
    {% set preflight_sql -%}
    {% if project_list()|length > 0 -%}
    {% for project in project_list() -%}
    SELECT
    CONCAT('`', CATALOG_NAME, '`.`', SCHEMA_NAME, '`') AS SCHEMA_NAME
    FROM `{{ project | trim }}`.`region-{{ var('bq_region') }}`.`INFORMATION_SCHEMA`.`SCHEMATA`
    {% if not loop.last %}UNION ALL{% endif %}
    {% endfor %}
    {%- else %}
    SELECT
    CONCAT('`', CATALOG_NAME, '`.`', SCHEMA_NAME, '`') AS SCHEMA_NAME
    FROM `region-{{ var('bq_region') }}`.`INFORMATION_SCHEMA`.`SCHEMATA`
    {%- endif %}
    {%- endset %}
    {% set results = run_query(preflight_sql) %}
    {% set dataset_list = results | map(attribute='SCHEMA_NAME') | list %}
    {%- if dataset_list | length == 0 -%}
    {{ log("No datasets found in the project list", info=True) }}
    {%- endif -%}
    
    WITH base AS (
    {%- if dataset_list | length == 0 -%}
      SELECT CAST(NULL AS STRING) AS field1, CAST(NULL AS INTEGER) AS field2, CAST(NULL AS STRING) AS field3
      LIMIT 0
    {%- else %}
    {% for dataset in dataset_list -%}
      SELECT field1, field2, field3
      FROM {{ dataset | trim }}.`INFORMATION_SCHEMA`.`PARTITIONS`
    {% if not loop.last %}UNION ALL{% endif %}
    {% endfor %}
    {%- endif -%}
    )
    SELECT
    field1, field2, field3,
    FROM
    base
    