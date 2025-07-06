{# More details about base table in https://cloud.google.com/bigquery/docs/information-schema-jobs -#}
jobs.admin
SELECT
field1,
field2,
field3
FROM `region-{{ dbt_bigquery_monitoring_variable_bq_region() }}`.`INFORMATION_SCHEMA`.`jobs`