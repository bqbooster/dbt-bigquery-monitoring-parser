{{ config(materialized=dbt_bigquery_monitoring_materialization()) }}
{# More details about base table in https://cloud.google.com/bigquery/docs/information-schema-jobs -#}
jobs.admin

{% set dataset_list = get_dataset_list() %}

WITH base AS (
{%- if dataset_list | length == 0 -%}
  SELECT CAST(NULL AS STRING) AS field1, CAST(NULL AS INTEGER) AS field2, CAST(NULL AS STRING) AS field3
  LIMIT 0
{%- else %}
{% for dataset in dataset_list -%}
  SELECT
  field1,
field2,
field3
  FROM {{ dataset | trim }}.`INFORMATION_SCHEMA`.`jobs`
{% if not loop.last %}UNION ALL{% endif %}
{% endfor %}
{%- endif -%}
)

SELECT
field1,
field2,
field3
FROM
base