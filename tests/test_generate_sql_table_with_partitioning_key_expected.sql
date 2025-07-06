{{ config(materialized=dbt_bigquery_monitoring_materialization(), enabled=true, tags=["test"], partition_by={'field': 'creation_time', 'data_type': 'timestamp', 'granularity': 'hour'}, partition_expiration_days=180) }}
{# More details about base table in https://cloud.google.com/bigquery/docs/information-schema-jobs -#}
jobs.admin
SELECT
field1,
field2,
field3
FROM `region-{{ dbt_bigquery_monitoring_variable_bq_region() }}`.`INFORMATION_SCHEMA`.`jobs`