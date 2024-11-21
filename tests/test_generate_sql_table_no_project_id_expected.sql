{# More details about base table in https://cloud.google.com/bigquery/docs/information-schema-jobs -#}
jobs.admin
WITH base AS (
  SELECT field1, field2, field3
FROM `region-{{ var('bq_region') }}`.`INFORMATION_SCHEMA`.`jobs`
)
SELECT
field1, field2, field3,
FROM
base