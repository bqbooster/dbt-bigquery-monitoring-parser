{# More details about base table in https://cloud.google.com/bigquery/docs/information-schema-jobs -#}
jobs.admin
WITH base AS (
  {% if project_list()|length > 0 -%}
  {% for project in project_list() -%}
  SELECT field1, field2, field3
  FROM `{{ project | trim }}`.`region-{{ var('bq_region') }}`.`INFORMATION_SCHEMA`.`jobs`
  {% if not loop.last %}UNION ALL{% endif %}
  {% endfor %}
{%- else %}
  SELECT field1, field2, field3
FROM `region-{{ var('bq_region') }}`.`INFORMATION_SCHEMA`.`jobs`
{%- endif %}
)
SELECT
field1, field2, field3,
FROM
base
